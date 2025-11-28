"""
Manages devices and their profiles in the system. It uses IoXWrapper to interact with the underlying hardware
and periodically updates device profiles based on the latest data from the iox controller
"""


from nucore import Node
from nucore import Profile
from iox import IoXWrapper
from udi_interface import LOGGER

class DeviceManager:
    def __init__(self, poly):
        self.poly = poly
        self.isy = IoXWrapper(poly=self.poly)
        self.profile = Profile("", [])
        self.thermostats={}
        self.dimmers={}
        self.switches={}

    def update_profiles(self):
        """
        Updates the device profiles by fetching the latest data from the iox controller
        """
        try:
            if not self.profile.load_from_json(self.isy.get_profiles()):
                LOGGER.error("Failed to load profiles from JSON data")
                return False
            response = self.isy.get_nodes()
            if response is None:
                LOGGER.error("Failed to fetch nodes from URL.")
                return False
            root = Node.load_from_xml(response)
            if not self.profile.map_nodes(root):
                LOGGER.error("Failed to map nodes from XML data")
                return False
            return self.__process_devices__()
        except Exception as ex:
            LOGGER.error(f"Failed to update profiles: {str(ex)}")
            return False
        
    def __process_devices__(self):
        """
        Processes devices and categorizes them into thermostats, dimmers, and switches
        """
        for node in self.profile.nodes.values():
            if node.address in self.thermostats.keys() or node.address in self.dimmers.keys() or node.address in self.switches.keys():
                continue
            node_def = self.__get_node_definitions__(node)
            if not node_def:
                continue
            for prop in node_def.properties:
                if prop.id == "CLISPC" or prop.id == "CLISPH":
                    self.thermostats[node.address] = node
                    break
                elif prop.id == "OL" or prop.id == "RR":
                    self.dimmers[node.address] = node
                    break 
                else:
                    for cmd in node_def.cmds.accepts:
                        if cmd.id == "DON" or cmd.id == "DFON":
                            #make sure we don't also have OL and RR
                            for cmd in node_def.cmds.accepts:
                                if cmd.id == "OL" or cmd.id == "RR":
                                    self.dimmers[node.address] = node 
                                    break
                            if node.address not in self.dimmers.keys():    
                                self.switches[node.address] = node
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
            key= f"{node.nodeDefId}.{node.family}.{node.instance}"
            return self.profile.lookup[key]
        except Exception as ex:
            LOGGER.warning(f"Failed to get node definitions for {node.address}: {str(ex)}")
            return None



