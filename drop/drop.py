#!/usr/bin/env python3
#fork from https://github.com/exking/udi-mqtt-pg3
from typing import Dict, List

import udi_interface
import os
import sys
import logging
import paho.mqtt.client as mqtt
import json
import yaml
import time
import version

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

dropCtrlAddress='dropctrl'
dropCtrlName='Drop'
dropTopic = 'drop_connect'
mapFile = './dmap.json'

class DeviceAddressMap:

    def __init__(self):
        self.map:Dict[str,str]={}
        self.load()

    def load(self)->bool():
        if not os.path.exists(mapFile):
            return False
        try:
            with open(mapFile, 'r') as json_file:
                self.map = json.load(json_file)
            return True
        except Exception as ex:
            LOGGER.error("failed loading the dev map file {}".format (ex))
            return False

    def save(self)->bool():
        try:
            with open(mapFile, 'w') as json_file:
                json.dump(self.map, json_file)
        except Exception as ex:
            LOGGER.error("failed saving the dev map file {}".format (ex))
            return False

    @staticmethod
    def getPG3Address(addr:str)->str:
        if addr == None:
            return None
        return addr.replace("-","").replace("_","").lower()


    #convert device address to address recognized by PG3 and store in the dect
    def addHub(self, pg3_addr:str, dev_addr:str)->bool:
        if pg3_addr == None or dev_addr == None:
            return False
        if pg3_addr not in self.map:
            self.map[pg3_addr]=dev_addr
        self.save()
        return True 

    def addDevice(self, pg3_addr:str, pg3_hub_addr:str, dev_addr:str):
        if pg3_addr == None or pg3_hub_addr == None or dev_addr == None:
            return False
        if pg3_addr not in self.map:
            self.map[pg3_addr]=pg3_hub_addr+"_"+dev_addr
        self.save()
        return True

    #returns the hub and end device addresses in an array
    #0 = hub
    #1 = device
    def getHubAndEndDevice(self, pg3_addr:str):
        m:str = self.getDevice(pg3_addr)
        if m == None:
            return None
        try:
            return m.split("_")
        except Exception as ex:
            return None

    #returns the actual device address
    def getDevice(self, addr)->str:
        if addr == None:
            return None
        return self.map[addr]

deviceAddressMap=DeviceAddressMap()
        
class Controller(udi_interface.Node):
    global dropCtrlAddress
    global dropCtrlName
    global dropTopic
    global polyglot 

    id='DROPCTRL'
    def __init__(self, polyglot):
        super().__init__(polyglot, dropCtrlAddress, dropCtrlAddress, dropCtrlName)
        self.Parameters = Custom(polyglot, 'customparams')
        #self.name = "MQTT Controller"
        self.name = dropCtrlName 
        self.address = dropCtrlAddress 
        self.primary = self.address
        self.mqtt_server = "localhost"
        self.mqtt_port = 1884
        self.mqtt_user = None
        self.mqtt_password = None
        self.devlist = None
        # example: [ {'id': 'sonoff1', 'type': 'switch', 'status_topic': 'stat/sonoff1/power', 'cmd_topic': 'cmnd/sonoff1/power'} ]
        self.status_topics = [dropTopic+'/#']
        # Maps to device IDs
        self.status_topics_to_devices: Dict[str, str] = {}
        self.mqttc = None
        self.valid_configuration = False

        self.poly.subscribe(polyglot.START, self.start, dropCtrlAddress)
        self.poly.subscribe(polyglot.CUSTOMPARAMS, self.parameter_handler)
        # self.poly.subscribe(polyglot.POLL, self.poll)
        self.poly.subscribe(polyglot.STOP, self.stop)

        self.poly.addNode(self)
        self.poly.ready()

    def addAllNodes(self): 
        config = self.poly.getConfig()
        if config == None or config['nodes'] == None:
            self.valid_configuration=True
            return

        for node in config['nodes']:
            nodeDef = node['nodeDefId']
            if nodeDef == "DROPCTRL":
                continue
            address = node['address']
            primary = node['primaryNode']
            name = node['name']
            if nodeDef == "DROPHUB":
                self.addHub(address, name)
            else:
                self.addDevice(nodeDef, address, name)
        LOGGER.info("Done adding nodes, ...")
        self.valid_configuration=True

    def addHub(self, address, name)->udi_interface.Node:
        self.poly.addNode(DropHub(self.poly,address,name))
        return self.poly.getNode(address)

    def addDevice(self, nodeDef:str, endDeviceAddress:str, devName:str):
        if nodeDef == None:
            return
        devNode = None
        if nodeDef == "DROPSOFT":
            devNode=DropSoftener(self.poly, self, endDeviceAddress, devName)
        elif nodeDef == "DROPFILT":
            devNode=DropSoftener(self.poly, self, endDeviceAddress, devName)
        elif nodeDef == "DROPSALT":
            devNode=DropSalt(self.poly, self, endDeviceAddress, devName)
        elif nodeDef == "DROPPV":
            devNode=DropPV(self.poly, self, endDeviceAddress, devName)
        elif nodeDef == "DROPPC":
            devNode=DropPC(self.poly, self, endDeviceAddress, devName)
        elif nodeDef == "DROPLEAK":
            devNode=DropLeakDetector(self.poly, self, endDeviceAddress, devName)
        elif nodeDef == "DROPRO":
            devNode=DropRO(self.poly, self, endDeviceAddress, devName)

        if devNode == None:
            LOGGER.error("invalid nodedef id {}".format(nodeDef))
            return
        self.poly.addNode(devNode)
        #address map should already have them

    def parameter_handler(self, params):
        self.poly.Notices.clear()
        self.Parameters.load(params)
        LOGGER.info("Started MQTT controller")
        self.mqtt_server = self.Parameters["mqtt_server"] or 'localhost'
        self.mqtt_port = int(self.Parameters["mqtt_port"] or 1884)

        return True

    def start(self):
        self.addAllNodes()
        polyglot.updateProfile()
        self.poly.setCustomParamsDoc()

        self.mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.mqttc.on_connect = self._on_connect
        self.mqttc.on_disconnect = self._on_disconnect
        self.mqttc.on_message = self._on_message
        self.mqttc.is_connected = False

        #self.mqttc.username_pw_set(self.mqtt_user, self.mqtt_password)
        try:
            self.mqttc.connect(self.mqtt_server, self.mqtt_port, 10)
            self.mqttc.loop_start()
        except Exception as ex:
            LOGGER.error("Error connecting to Poly MQTT broker {}".format(ex))
            return False

        LOGGER.info("Start")

    def _add_status_topics(self, dev, status_topics: List[str]):
        for status_topic in status_topics:
            self.status_topics.append(status_topic)
            self.status_topics_to_devices[status_topic] = Controller._get_device_address(dev)

    def _on_connect(self, mqttc, userdata, flags, rc):
        if rc == 0:
            LOGGER.info("Poly MQTT Connected, subscribing...")
            self.mqttc.is_connected = True
            results = []
            for stopic in self.status_topics:
                results.append((stopic, tuple(self.mqttc.subscribe(stopic))))
            for (topic, (result, mid)) in results:
                if result == 0:
                    LOGGER.info(
                        "Subscribed to {} MID: {}, res: {}".format(topic, mid, result)
                    )
                else:
                    LOGGER.error(
                        "Failed to subscribe {} MID: {}, res: {}".format(
                            topic, mid, result
                        )
                    )
            for node in self.poly.getNodes():
                if node != self.address:
                    self.poly.getNode(node).query()
        else:
            LOGGER.error("Poly MQTT Connect failed")

    def _on_disconnect(self, mqttc, userdata, rc):
        self.mqttc.is_connected = False
        if rc != 0:
            LOGGER.warning("Poly MQTT disconnected, trying to re-connect")
            try:
                self.mqttc.reconnect()
            except Exception as ex:
                LOGGER.error("Error connecting to Poly MQTT broker {}".format(ex))
                return False
        else:
            LOGGER.info("Poly MQTT graceful disconnection")

    #adds a hub node if necessary
    def _getHubNode(self, hubAddr:str, name:str=None):
        hubId = DeviceAddressMap.getPG3Address(hubAddr)
        hubNode = self.poly.getNode(hubId)
        if hubNode == None:
            LOGGER.debug("creating a hub node for {}".format(hubId))
            try:
                if name == None:
                    name=hubId
                hubNode = self.addHub(hubId, hubAddr)
                if hubNode == None:
                    LOGGER.error("failed creating a hubnode for {}".format(hubId))
                    return None
                deviceAddressMap.addHub(hubId, hubAddr)
            except Exception as ex:
                LOGGER.error("Failed making hub node for {}, exception = {}".format(hubId, ex))
                return None
        return hubNode

    def _getPG3Node(self, hubAddr:str):
        hubId = DeviceAddressMap.getPG3Address(hubAddr)
        return self.poly.getNode(hubId)

    def _processDiscovery(self, hubAddr:str, devAddr:str, payload:str):
        if payload == None or hubAddr == None:
            return
        devName:str = None
        devType:str = None
        try:
            data = json.loads(payload)
            if 'name' in data:
                devName = data['name']
            if 'devType' in data:
                devType = data['devType']
        except Exception as ex:
            LOGGER.error("Failed to parse discovery payload as Json: {} {}".format(ex, payload))
            return 

        if devType == None:
            return 

        hubNode = self._getHubNode(hubAddr,devName)
        devNode = None
        if devType == "hub":
            return 
        devNode = hubNode.addEndNode(devType, devAddr, devName)
        if devNode == None:
            return
        deviceAddressMap.addDevice(devNode.address, hubNode.address, devAddr)
        

    def _processHubData(self,hubAddr:str, payload:str):
        hubNode = self._getPG3Node(hubAddr)
        if hubNode == None:
            return
        hubNode.updateInfo(payload, None)


    def _processDeviceData(self,hubAddr:str, devId:str, payload:str):
        hubNode = self._getPG3Node(hubAddr)
        if hubNode == None:
            return
        devAddress=hubNode.address+devId
        devNode = self.poly.getNode(devAddress)
        if devNode == None:
            LOGGER.debug("couldn't find the node for {}".format(hubAddr))
            return

        devNode.updateInfo(payload, None)

    def _on_message(self, mqttc, userdata, message):
        if not self.valid_configuration:
            return
        payload = message.payload.decode("utf-8")
        LOGGER.info("Received {} from {}".format(payload, message.topic))
        topic_list = message.topic.split("/")
        try:
            if topic_list[1] == "discovery":
                self._processDiscovery(topic_list[2],topic_list[3], payload)
            else:
                devId = topic_list[3]
                if devId == "255":
                    self._processHubData(topic_list[1], payload)
                else:
                    self._processDeviceData(topic_list[1], devId, payload)

        except Exception as ex:
            LOGGER.error("Failed to process message {}".format(ex))

    def _dev_by_topic(self, topic):
        return self.status_topics_to_devices.get(topic, None)

    @staticmethod
    def _get_device_address(dev) -> str:
        return dev["id"].lower().replace("_", "").replace("-", "_")[:14]

    def mqtt_pub(self, topic, message):
        self.mqttc.publish(topic, message, retain=False)

    def stop(self):
        if self.mqttc is None:
            return
        self.mqttc.loop_stop()
        self.mqttc.disconnect()
        LOGGER.info("MQTT is stopping")

    def query(self, command=None):
        for node in self.poly.getNodes().values():
            node.reportDrivers()

    def discover(self, command=None):
        pass

    commands = {"DISCOVER": discover}
    drivers = [{"driver": "ST", "value": 1, "uom": 2}]


class DropHub(udi_interface.Node):
    id="DROPHUB"

    drivers = [
        #leak detectd
        {"driver": "ST", "value": 0, "uom": 25},
        #current water flow
        {"driver": "WATERF", "value": 0, "uom": 143},
        #peak water flow
        {"driver": "GV2", "value": 0, "uom": 143},
        #water used today 
        {"driver": "WVOL", "value": 0, "uom": 69},
        #average water used in the last 30 days
        {"driver": "GV3", "value": 0, "uom": 69},
        #current system pressure
        {"driver": "WATERP", "value": 0, "uom": 138},
        #low system pressure today
        {"driver": "GV4", "value": 0, "uom": 138},
        #high system pressure today
        {"driver": "GV5", "value": 0, "uom": 138},
        #water on/off
        {"driver": "GV6", "value": 0, "uom": 78},
        #bypass on/off
        {"driver": "GV7", "value": 0, "uom": 78},
        #pMode
        {"driver": "GV8", "value": 0, "uom": 25},
        #bat level
        {"driver": "BATLVL", "value": 0, "uom": 51},
        #notification
        {"driver": "GV9", "value": 0, "uom": 25},
    ]

    def __init__(self, poly, address, name):
        super().__init__(poly, dropCtrlAddress, address, name)
        self.controller = self.poly.getNode(self.primary)
        #self.cmd_topic = device["cmd_topic"]

    def updateInfo(self, payload, topic: str):
        try:
            data = json.loads(payload)
        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False

        try:
            if "leak" in data:
                self.setDriver("ST", data["leak"], 25)
            if "curFlow" in data:
                self.setDriver("WATERF", data["curFlow"], 143)
            if "peakFlow" in data:
                self.setDriver("GV2", data["peakFlow"], 143)
            if "usedToday" in data:
                self.setDriver("WVOL", data["usedToday"], 69)
            if "avgUsed" in data:
                self.setDriver("GV3", data["avgUsed"], 69)
            if "psi" in data:
                self.setDriver("WATERP", data["psi"], 138)
            if "psiLow" in data:
                self.setDriver("GV4", data["psiLow"], 138)
            if "psiHigh" in data:
                self.setDriver("GV5", data["psiHigh"], 138)
            if "water" in data:
                if data["water"] == 1:
                    self.setDriver("GV6", 100, 78)
                else:
                    self.setDriver("GV6", data["water"], 78)
            if "bypass" in data:
                if data["bypass"] == 1:
                    self.setDriver("GV7", 100, 78)
                else:
                    self.setDriver("GV7", data["bypass"], 78)
            if "pMode" in data:
                val = data["pMode"]
                index = 0
                if val == "away":
                    index = 1
                elif val == "schedule":
                    index = 2
                self.setDriver("GV8", index, 25)
            if "battery" in data:
                self.setDriver("BATLVL", data["battery"], 51)
            if "notif" in data:
                self.setDriver("GV9", data["notif"], 25)

        except Exception as ex:
            LOGGER.error("Failed to update hub info{}".format(ex))


    

    def addEndNode(self, devType:str, devAddr:str, devName:str):
        if devType == None:
            return None
        try:
            endDeviceAddress=self.address+devAddr
            devNode = self.poly.getNode(endDeviceAddress)
            if devNode != None:
                return devNode

            if devType == "soft":
                devNode=DropSoftener(self.poly, self.controller, endDeviceAddress, devName)
            elif devType == "filter":
                devNode=DropSoftener(self.poly, self.controller, endDeviceAddress, devName)
            elif devType == "salt":
                devNode=DropSalt(self.poly, self.controller, endDeviceAddress, devName)
            elif devType == "pv":
                devNode=DropPV(self.poly, self.controller, endDeviceAddress, devName)
            elif devType == "pc":
                devNode=DropPC(self.poly, self.controller, endDeviceAddress, devName)
            elif devType == "leak":
                devNode=DropLeakDetector(self.poly, self.controller, endDeviceAddress, devName)
            elif devType == "ro":
                devNode=DropRO(self.poly, self.controller, endDeviceAddress, devName)
            elif devType == "alrt":
                devNode=DropAlert(self.poly, self.controller, endDeviceAddress, devName)

            if devNode == None:
                LOGGER.error("failed adding node since devType {} is unknown".format(devType))
                return
            self.poly.addNode(devNode)
            return devNode
        except Exception as ex:
            LOGGER.error("failed creating {} node".format(devType))

    def water(self, command):
        try:
            query = str(command['query']).replace("'","\"")
            jparam=json.loads(query)
            val=int(jparam['WCTRL.uom78'])/100
            address=command['address']
            devAddress=deviceAddressMap.getDevice(address)
            if devAddress == None:
                LOGGER.debug("couldn't find device for address {}".format(address))
                return
            LOGGER.debug("setting water to {} for {}".format(val, devAddress))
            topic="drop_connect/{}/cmd/255".format(devAddress)
            msg=json.dumps(({"water":int(val)}))
            self.controller.mqtt_pub(topic, msg) 
            #self.controller.mqtt_pub(self.cmd_topic, json.dumps({"state": "ON"}))
        except Exception as ex:
            LOGGER.error("failed setting water {}".format(ex))


    def bypass(self, command):
        try:
            query = str(command['query']).replace("'","\"")
            jparam=json.loads(query)
            val=int(jparam['BPCTRL.uom78'])/100
            address=command['address']
            devAddress=deviceAddressMap.getDevice(address)
            if devAddress == None:
                LOGGER.debug("couldn't find device for address {}".format(address))
                return
            LOGGER.debug("setting bypass to {} for {}".format(val, devAddress))
            topic="drop_connect/{}/cmd/255".format(devAddress)
            msg=json.dumps(({"bypass":int(val)}))
            self.controller.mqtt_pub(topic, msg) 
        except Exception as ex:
            LOGGER.error("failed setting bypass {}".format(ex))


    def pMode(self, command):
        try:
            query = str(command['query']).replace("'","\"")
            jparam=json.loads(query)
            val=int(jparam['PMCTRL.uom25'])
            address=command['address']
            devAddress=deviceAddressMap.getDevice(address)
            if devAddress == None:
                LOGGER.debug("couldn't find device for address {}".format(address))
                return
            param = "home"
            if val == 1:
                param = "away"
            elif val == 2:
                param = "schedule"
            LOGGER.debug("setting pmode to {} for {}".format(val, devAddress))
            topic="drop_connect/{}/cmd/255".format(devAddress)
            msg=json.dumps(({"pMode":param}))
            self.controller.mqtt_pub(topic, msg) 
        except Exception as ex:
            LOGGER.error("failed setting bypass {}".format(ex))


    def _check_limit(self, value):
        if value > 255:
            return 255
        elif value < 0:
            return 0
        else:
            return value

    def query(self, command=None):
        self.reportDrivers()

    commands = {"QUERY": query, "WATER": water, "BYPASS": bypass, "PMODE": pMode}

class DropSoftener(udi_interface.Node):
    id="DROPSOFT"

    drivers = [
        #current water flow
        {"driver": "ST", "value": 0, "uom": 143},
        #bypass on/off
        {"driver": "GV7", "value": 0, "uom": 78},
        #bat level
        {"driver": "BATLVL", "value": 0, "uom": 51},
        #capacity 
        {"driver": "WVOL", "value": 0, "uom": 69},
        #current system pressure
        {"driver": "WATERP", "value": 0, "uom": 138},
        #reserve capacity in use on/off
        {"driver": "GV2", "value": 0, "uom": 78},
    ]

    #controller = mqtt
    #primary = hub
    def __init__(self, poly, controller, address, name):
        super().__init__(poly, dropCtrlAddress, address, name)
        self.controller = controller 

    def updateInfo(self, payload, topic: str):
        try:
            data = json.loads(payload)
        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False

        try:
            if "curFlow" in data:
                self.setDriver("ST", data["curFlow"], 143)
            if "bypass" in data:
                if data["bypass"] == 1:
                    self.setDriver("GV7", 100, 78)
                else:
                    self.setDriver("GV7", data["bypass"], 78)
            if "battery" in data:
                self.setDriver("BATLVL", data["battery"], 51)
            if "capacity" in data:
                self.setDriver("WVOL", data["capacity"], 69)
            if "psi" in data:
                self.setDriver("WATERP", data["psi"], 138)
            if "resInUse" in data:
                if data["resInUse"] == 1:
                    self.setDriver("GV2", 100, 78)
                else:
                    self.setDriver("GV2", data["resInUse"], 78)
        except Exception as ex:
            LOGGER.error("Failed to update softener info{}".format(ex))

    def bypass(self, command):
        try:
            query = str(command['query']).replace("'","\"")
            jparam=json.loads(query)
            val=int(jparam['BPCTRL.uom78'])/100
            address=command['address']
            if address == None:
                LOGGER.debug("address not available ...")
                return
            parts=deviceAddressMap.getHubAndEndDevice(address)
            if parts == None:
                LOGGER.debug("couldn't find device for address {}".format(address))
                return
            hub=parts[0]
            devAddress=parts[1]
            hubAddress = deviceAddressMap.getDevice(hub)
            if hubAddress == None or devAddress == None:
                LOGGER.debug("couldn't find hub for address {}".format(address))
                return
            LOGGER.debug("setting bypass to {} for {}:{}".format(val, hubAddress,devAddress))
            topic="drop_connect/{}/cmd/{}".format(hubAddress,devAddress)
            msg=json.dumps(({"bypass":int(val)}))
            self.controller.mqtt_pub(topic, msg) 
        except Exception as ex:
            LOGGER.error("failed setting bypass {}".format(ex))


    def query(self, command=None):
        self.reportDrivers()

    commands = {"QUERY": query, "BYPASS": bypass}

class DropFilter(udi_interface.Node):
    id="DROPFILT"

    drivers = [
        #current water flow
        {"driver": "ST", "value": 0, "uom": 143},
        #bypass on/off
        {"driver": "GV7", "value": 0, "uom": 78},
        #bat level
        {"driver": "BATLVL", "value": 0, "uom": 51},
        #current system pressure
        {"driver": "WATERP", "value": 0, "uom": 138},
    ]

    #controller = mqtt
    #primary = hub
    def __init__(self, poly, controller, dropCtrlAddress, address, name):
        super().__init__(poly, primary, address, name)
        self.controller = controller 

    def updateInfo(self, payload, topic: str):
        try:
            data = json.loads(payload)
        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False

        try:
            if "curFlow" in data:
                self.setDriver("ST", data["curFlow"], 143)
            if "bypass" in data:
                if data["bypass"] == 1:
                    self.setDriver("GV7", 100, 78)
                else:
                    self.setDriver("GV7", data["bypass"], 78)
            if "battery" in data:
                self.setDriver("BATLVL", data["battery"], 51)
            if "psi" in data:
                self.setDriver("WATERP", data["psi"], 138)
        except Exception as ex:
            LOGGER.error("Failed to update softener info{}".format(ex))

    def bypass(self, command):
        try:
            query = str(command['query']).replace("'","\"")
            jparam=json.loads(query)
            val=int(jparam['BPCTRL.uom78'])/100
            address=command['address']
            if address == None:
                LOGGER.debug("address not available ...")
                return
            parts=deviceAddressMap.getHubAndEndDevice(address)
            if parts == None:
                LOGGER.debug("couldn't find device for address {}".format(address))
                return
            hub=parts[0]
            devAddress=parts[1]
            hubAddress = deviceAddressMap.getDevice(hub)
            if hubAddress == None or devAddress == None:
                LOGGER.debug("couldn't find hub for address {}".format(address))
                return
            LOGGER.debug("setting bypass to {} for {}:{}".format(val, hubAddress,devAddress))
            topic="drop_connect/{}/cmd/{}".format(hubAddress,devAddress)
            msg=json.dumps(({"bypass":int(val)}))
            self.controller.mqtt_pub(topic, msg) 
        except Exception as ex:
            LOGGER.error("failed setting bypass {}".format(ex))

    def query(self, command=None):
        self.reportDrivers()

    commands = {"QUERY": query, "BYPASS": bypass}

class DropSalt(udi_interface.Node):
    id="DROPSALT"

    drivers = [
        #salt level 1=low, 0=normal
        {"driver": "ST", "value": 0, "uom": 25},
    ]

    #controller = mqtt
    #primary = hub
    def __init__(self, poly, controller, address, name):
        super().__init__(poly, dropCtrlAddress, address, name)
        self.controller = controller 

    def updateInfo(self, payload, topic: str):
        try:
            data = json.loads(payload)
        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False

        try:
            if "salt" in data:
                self.setDriver("ST", data["curFlow"], 25)
        except Exception as ex:
            LOGGER.error("Failed to update softener info{}".format(ex))

    def query(self, command=None):
        self.reportDrivers()

    commands = {"QUERY": query}

class DropPV(udi_interface.Node):
    id="DROPPV"

    drivers = [
        #leak detectd
        {"driver": "ST", "value": 0, "uom": 25},
        #current water flow
        {"driver": "WATERF", "value": 0, "uom": 143},
        #water on/off
        {"driver": "GV6", "value": 0, "uom": 78},
        #bat level
        {"driver": "BATLVL", "value": 0, "uom": 51},
        #current system pressure
        {"driver": "WATERP", "value": 0, "uom": 138},
        #temperature
        {"driver": "WATERT", "value": 0, "uom": 17},
    ]

    #controller = mqtt
    #primary = hub
    def __init__(self, poly, controller, address, name):
        super().__init__(poly, dropCtrlAddress, address, name)
        self.controller = controller 

    def updateInfo(self, payload, topic: str):
        try:
            data = json.loads(payload)
        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False

        try:
            if "leak" in data:
                self.setDriver("ST", data["leak"], 25)
            if "curFlow" in data:
                self.setDriver("WATERF", data["curFlow"], 143)
            if "water" in data:
                if data["water"] == 1:
                    self.setDriver("GV6", 100, 78)
                else:
                    self.setDriver("GV6", data["water"], 78)
            if "battery" in data:
                self.setDriver("BATLVL", data["battery"], 51)
            if "psi" in data:
                self.setDriver("WATERP", data["psi"], 138)
            if "temp" in data:
                self.setDriver("WATERT", data["temp"], 17)

        except Exception as ex:
            LOGGER.error("Failed to update pv info{}".format(ex))
    
    def water(self, command):
        try:
            query = str(command['query']).replace("'","\"")
            jparam=json.loads(query)
            val=int(jparam['WCTRL.uom78'])/100
            address=command['address']
            if address == None:
                LOGGER.debug("address not available ...")
                return
            parts=deviceAddressMap.getHubAndEndDevice(address)
            if parts == None:
                LOGGER.debug("couldn't find device for address {}".format(address))
                return
            hub=parts[0]
            devAddress=parts[1]
            hubAddress = deviceAddressMap.getDevice(hub)
            if hubAddress == None or devAddress == None:
                LOGGER.debug("couldn't find hub for address {}".format(address))
                return
            LOGGER.debug("setting water to {} for {}:{}".format(val, hubAddress,devAddress))
            topic="drop_connect/{}/cmd/{}".format(hubAddress,devAddress)
            msg=json.dumps(({"water":int(val)}))
            self.controller.mqtt_pub(topic, msg) 
        except Exception as ex:
            LOGGER.error("failed setting bypass {}".format(ex))


    def query(self, command=None):
        self.reportDrivers()

    commands = {"QUERY": query, "WATER": water}

class DropPC(udi_interface.Node):
    id="DROPPC"

    drivers = [
        #leak detectd
        {"driver": "ST", "value": 0, "uom": 25},
        #current water flow
        {"driver": "WATERF", "value": 0, "uom": 143},
        #current system pressure
        {"driver": "WATERP", "value": 0, "uom": 138},
        #pump status on/off 1= running, 0 = off
        {"driver": "GV2", "value": 0, "uom": 78},
        #temperature
        {"driver": "WATERT", "value": 0, "uom": 17},
    ]

    #controller = mqtt
    #primary = hub
    def __init__(self, poly, controller, address, name):
        super().__init__(poly, dropCtrlAddress, address, name)
        self.controller = controller 

    def updateInfo(self, payload, topic: str):
        try:
            data = json.loads(payload)
        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False

        try:
            if "leak" in data:
                self.setDriver("ST", data["leak"], 25)
            if "curFlow" in data:
                self.setDriver("WATERF", data["curFlow"], 143)
            if "pump" in data:
                if data["pump"] == 1:
                    self.setDriver("GV6", 100, 78)
                else:
                    self.setDriver("GV6", data["pump"], 78)
            if "psi" in data:
                self.setDriver("WATERP", data["psi"], 138)
            if "temp" in data:
                self.setDriver("WATERT", data["temp"], 17)

        except Exception as ex:
            LOGGER.error("Failed to update pump controller info{}".format(ex))
    

    def query(self, command=None):
        self.reportDrivers()

    commands = {"QUERY": query}

class DropLeakDetector(udi_interface.Node):
    id="DROPLEAK"

    drivers = [
        #leak detectd
        {"driver": "ST", "value": 0, "uom": 25},
        #bat level
        {"driver": "BATLVL", "value": 0, "uom": 51},
        #current water flow
        #temperature
        {"driver": "WATERT", "value": 0, "uom": 17},
    ]

    #controller = mqtt
    #primary = hub
    def __init__(self, poly, controller, address, name):
        super().__init__(poly, dropCtrlAddress, address, name)
        self.controller = controller 

    def updateInfo(self, payload, topic: str):
        try:
            data = json.loads(payload)
        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False

        try:
            if "leak" in data:
                self.setDriver("ST", data["leak"], 25)
            if "battery" in data:
                self.setDriver("BATLVL", data["battery"], 51)
            if "temp" in data:
                self.setDriver("WATERT", data["temp"], 17)

        except Exception as ex:
            LOGGER.error("Failed to update leak detector info {}".format(ex))
    

    def query(self, command=None):
        self.reportDrivers()

    commands = {"QUERY": query}

class DropRO(udi_interface.Node):
    id="DROPRO"

    drivers = [
        #leak detectd
        {"driver": "ST", "value": 0, "uom": 25},
        #Inlet water TDS in PPM  (part/million)
        {"driver": "GV1", "value": 0, "uom": 54},
        #Outlet water TDS in PPM  (part/million)
        {"driver": "GV2", "value": 0, "uom": 54},
        #Cartdige #1 life remaining in %
        {"driver": "GV3", "value": 0, "uom": 51},
        #Cartdige #2 life remaining in %
        {"driver": "GV4", "value": 0, "uom": 51},
        #Cartdige #3 life remaining in %
        {"driver": "GV5", "value": 0, "uom": 51},
    ]

    #controller = mqtt
    #primary = hub
    def __init__(self, poly, controller, address, name):
        super().__init__(poly, dropCtrlAddress, address, name)
        self.controller = controller 

    def updateInfo(self, payload, topic: str):
        try:
            data = json.loads(payload)
        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False

        try:
            if "leak" in data:
                self.setDriver("ST", data["leak"], 25)
            if "tdsIn" in data:
                self.setDriver("GV1", data["tdsIn"], 54)
            if "tdsOut" in data:
                self.setDriver("GV2", data["tdsOut"], 54)
            if "cart1" in data:
                self.setDriver("GV3", data["cart1"], 51)
            if "cart2" in data:
                self.setDriver("GV4", data["cart2"], 51)
            if "cart3" in data:
                self.setDriver("GV5", data["cart3"], 51)

        except Exception as ex:
            LOGGER.error("Failed to update RO info {}".format(ex))
    

    def query(self, command=None):
        self.reportDrivers()

    commands = {"QUERY": query}

class DropAlert(udi_interface.Node):
    id="DROPALRT"
    drivers = [
        #Input State
        {"driver": "ST", "value": 0, "uom": 25},
        #bat level
        {"driver": "BATLVL", "value": 0, "uom": 51},
        #temperature
        {"driver": "GV1", "value": 0, "uom": 17},
        #Power Lost
        {"driver": "GV2", "value": 0, "uom": 25},
    ]

    #controller = mqtt
    #primary = hub
    def __init__(self, poly, controller, address, name):
        super().__init__(poly, dropCtrlAddress, address, name)
        self.controller = controller 

    def updateInfo(self, payload, topic: str):
        try:
            data = json.loads(payload)
        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False

        try:
            if "sens" in data:
                self.setDriver("ST", data["sens"], 25)
            if "battery" in data:
                self.setDriver("BATLVL", data["battery"], 51)
            if "temp" in data:
                self.setDriver("GV1", data["temp"], 17)
            if "pwrOff" in data:
                self.setDriver("GV2", data["temp"], 25)


        except Exception as ex:
            LOGGER.error("Failed to update Alert info {}".format(ex))
    
    def query(self, command=None):
        self.reportDrivers()

    commands = {"QUERY": query}

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start(version.ud_plugin_version)
        Controller(polyglot)
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
