"""
Manages devices and their profiles in the system. It uses IoXWrapper to interact with the underlying hardware
and periodically updates device profiles based on the latest data from the iox controller
"""


import asyncio
import os
from typing import Any
from nucore import Node
from nucore import Profile
from iox import IoXWrapper
from udi_interface import LOGGER
import xml.etree.ElementTree as ET
from opt_config.ven_settings import VENSettings
from .thermostat_optimizer import ThermostatOptimizer
from .dimmer_optimizer import DimmerOptimizer
from .switch_optimizer import SwitchOptimizer
from history.device_history import DeviceHistory
from .base_optimizer import BaseOptimizer
import threading

class DeviceManager:
    def __init__(self, poly ):
        self.poly = poly
        self.iox = IoXWrapper(json_output=True, poly=self.poly)
        self.profile = Profile(timestamp="", families=[])
        self.thermostats={}
        self.dimmers={}
        self.switches={}
        self.ven=None
        self.is_subscribed=False
        self.is_profiles_updated=False
        self.disable_optimization=False

    def update_settings(self, settings: VENSettings): 
        """
        Updates the VEN settings for all optimizers
        """
        self.ven_settings = settings
        for optimizer in self.thermostats.values():
            optimizer.update_settings(settings)
        for optimizer in self.dimmers.values():
            optimizer.update_settings(settings)
        for optimizer in self.switches.values():
            optimizer.update_settings(settings)

    def update_ven_setting(self, control:str, value: Any): 
        """
        Updates the VEN settings for all optimizers
        """
        if not self.ven_settings.is_changed(control, value):
            return
        self.update_settings(self.ven_settings)
    
    async def optimize(self, grid_state):
        if self.disable_optimization:
            return
        for optimizer in self.thermostats.values():
            await optimizer.optimize(grid_state)
        for optimizer in self.dimmers.values():
            await optimizer.optimize(grid_state)
        for optimizer in self.switches.values():
            await optimizer.optimize(grid_state) 

    def should_subscribe(self):
        """
        Determines whether the device manager should subscribe to events based on the current state of profiles and subscription
        """
        return not self.is_profiles_updated or not self.is_subscribed
    
    def subscribe_events(self):
        if not self.should_subscribe():
            return
        try:
            threading.Thread(target=asyncio.run, args=(self.iox.subscribe_events(
                on_message_callback=self.__on_message__,
                on_connect_callback=self.__on_connect__,
                on_disconnect_callback=self.__on_disconnect__),)).start()
        except Exception as ex:
            LOGGER.error(f"Failed to subscribe to events: {str(ex)}")   

    def disable_opt(self, disable: bool):
        """
        Enables or disables optimization for all devices
        """
        self.disable_optimization = disable

    def update_profiles(self):
        """
        Updates the device profiles by fetching the latest data from the iox controller
        """
        try:
            if not self.profile.load_from_json(self.iox.get_profiles()):
                LOGGER.error("Failed to load profiles from JSON data")
                return False
            
            response = self.iox.get_nodes()
            if response is None:
               LOGGER.error("Failed to fetch nodes from URL") 
               return False 
            root = Node.load_from_xml(response)
            if not self.profile.map_nodes(root):
                LOGGER.error("Failed to map nodes from XML data")
                return False
            self.__process_devices__()
            self.is_profiles_updated = True
            return True
        except Exception as ex:
            LOGGER.error(f"Failed to update profiles: {str(ex)}")
            return False

    def __process_devices__(self):
        """
        Processes devices and categorizes them into thermostats, dimmers, and switches
        """
        for node in self.profile.nodes.values():
            if (not node.enabled) or node.address in self.thermostats.keys() or node.address in self.dimmers.keys() or node.address in self.switches.keys():
                continue
            if self.ven is None and node.address.endswith("oadr3ven"):
                self.ven=node
                continue
            node_def = self.__get_node_definitions__(node)
            if not node_def:
                continue
            for prop in node_def.properties:
                if prop.id == "CLISPC" or prop.id == "CLISPH":
                    self.thermostats[node.address] = ThermostatOptimizer(self.ven_settings, node, self.iox)
                    break
                elif prop.id == "OL" or prop.id == "RR":
                    self.dimmers[node.address] = DimmerOptimizer(self.ven_settings, node,  self.iox)
                    break 
                else:
                    for cmd in node_def.cmds.accepts:
                        if cmd.id == "DON" or cmd.id == "DFON":
                            #make sure we don't also have OL and RR
                            for cmd in node_def.cmds.accepts:
                                if cmd.id == "OL" or cmd.id == "RR":
                                    self.dimmers[node.address] = DimmerOptimizer(self.ven_settings, node,  self.iox)
                                    break
                            if node.address not in self.dimmers.keys():    
                                self.switches[node.address] = SwitchOptimizer(self.ven_settings, node,  self.iox)
                                break

    def __get_node_definitions__(self, node):           
        """ returns a node definition in this format 
            NodeDef(
                id=ndict.get("id"),
                properties=props,
                cmds=cmds,
                nls=ndict.get("nls"),
                icon=ndict.get("icon"),
                links=node_links,
            )
        """
        if not node:
            LOGGER.error("Node is None, cannot get node definitions")
            return None
        try:
            key= f"{node.node_def_id}.{node.family}.{node.instance}"
            return self.profile.lookup[key]
        except Exception as ex:
            LOGGER.warning(f"Failed to get node definitions for {node.address}: {str(ex)}")
            return None

    async def __process_ven__(self, message):
        """
        Processes VEN-specific messages
        @param message: The incoming message from the event stream in JSON
        """
        if not 'control' in message:
            LOGGER.warning(f"Received VEN message without control: {message}")
            return
        control = message['control']
        value = message.get('action', None)['value']

        if control == "CGS":  # Current Grid Status update
            grid_state = value 
            #create a thread to optimize all devices based on new grid status
            await self.optimize(grid_state)
        elif control == "ST" or control == "GHG":
            #ignore
            pass
        else:
            #one of the settings changed
            self.update_ven_setting(control, value)

    async def __process_node_update__(self, node_address, message):
        """
        Processes node update messages
        @param node_address: The address of the node being updated
        @param message: The incoming message from the event stream in JSON. 
        Action values:
        #define DEVINTIX_NODE_REMOVED_ACTION               "NR"
        #define DEVINTIX_NODE_ADDED_ACTION                 "ND"
        #define DEVINTIX_NODE_ENABLED_ACTION               "EN"
        """
        try:
            action = message.get('action', {}).get('value', None)
            eventInfo = message.get('eventInfo', None)
            if action is None:
                LOGGER.warning(f"No action found in node update message for {node_address}")
                return
            if action == "NR":
                #remove it from thermostats, dimmers, switches
                if node_address in self.thermostats:
                    del self.thermostats[node_address]
                elif node_address in self.dimmers:
                    del self.dimmers[node_address]
                elif node_address in self.switches:
                    del self.switches[node_address]
            elif action == "ND" :
                #reprocess devices
                self.update_profiles(False)
            elif action == "EN":
                eventInfo = message.get('eventInfo', None)
                if eventInfo is None:
                    LOGGER.warning(f"No eventInfo found in node update message for {node_address}, {message}")
                    return
                eventInfo=ET.fromstring(eventInfo)
                enabled = eventInfo.find('enabled')
                if enabled is not None and enabled.text == "false":
                    #remove it from thermostats, dimmers, switches
                    if node_address in self.thermostats:
                        del self.thermostats[node_address]
                    elif node_address in self.dimmers:
                        del self.dimmers[node_address]
                    elif node_address in self.switches:
                        del self.switches[node_address]
                else:
                    #reprocess devices
                    self.update_profiles(False) 



        except Exception as ex:
            LOGGER.error(f"Error processing node update for {node_address}: {str(ex)}")
    
    async def __process_busy__(self, message):
        """
        Processes system busy 
        #define DEVINTIX_SYSTEM_IS_NOT_BUSY_ACTION "0"
        #define DEVINTIX_SYSTEM_IS_BUSY_ACTION "1"
        #define DEVINTIX_SYSTEM_IS_IDLE_ACTION "2"
        #define DEVINTIX_SYSTEM_IN_SAFE_MODE_ACTION "3"
        """
        LOGGER.debug(f"Received busy message: {message}")
        return

    async def __process_progress__(self, message):
        """
        Processes progress for long running operations. The action value indicates the progress status. 
        Can be ignored for now 
        """
        LOGGER.debug(f"Received progress message: {message}")
        return
    
            
    async def __on_message__(self, message):
        """
        Callback function to handle incoming messages from subscribed events
        @param message: The incoming message from the event stream in JSON
        """
        if message is None or 'node' not in message or 'control' not in message:
            LOGGER.warning(f"Received invalid message format {message}")
            return
        

        node_address = message.get('node', None)
        control = message.get('control', None)
        if control == "_3": #node updated event
            await self.__process_node_update__(node_address, message)
        elif control == "_5": #system busy event
            await self.__process_busy__(message)
        elif control == "_7": #system busy event
            await self.__process_progress__(message)
        elif control.startswith("_"): #ven message
            pass #ignore other control events
        elif node_address in self.thermostats.keys():
            await self.thermostats[node_address].update_internal_state(message)
        elif node_address in self.dimmers.keys():
            await self.dimmers[node_address].update_internal_state(message)
        elif node_address in self.switches.keys():
            await self.switches[node_address].update_internal_state(message)
        elif self.ven and node_address == self.ven.address:
            await self.__process_ven__(message)
        else:
            # not important
            pass
    
    async def __on_connect__(self):
        """
        Callback function to handle connection established event
        """
        self.is_subscribed = True
        print("Connected to event stream") 
    
    async def __on_disconnect__(self):
        """
        Callback function to handle disconnection event
        """
        self.is_subscribed = False
        print("Disconnected from event stream")