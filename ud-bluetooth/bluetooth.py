#!/usr/bin/env python3
"""
Polyglot v3 plugin for managing bluetooth service/devices
Copyright (C) 2024  Universal Devices
"""

import os
import udi_interface
import sys
import time
import json
import threading
import paho.mqtt.client as mqtt
import ssl
import version

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

btCtrlAddress='btsvcctrl'
btCtrlName='Bluetooth Service'

def find_files_with_extension(directory:str, extension:str):
    if directory == None or extension == None:
        return None
    file_paths = []

    for root, _, files in os.walk('./'):
        for file in files:
            if file.endswith(extension):
                # Construct the full path to the file and append it to the list
                file_path = os.path.join(root, file)
                file_paths.append(file_path)

    return file_paths


def get_pg3_address(mac:str):
    if mac == None:
        return None 

    segments = mac.split(":")
    mac_integer = int("".join(segments), 16)
    return format(mac_integer, '012x')  # '012x' ensures zero-padding to 12 characters

def get_mac_address(mac_integer_str:str):
    mac_integer = int(mac_integer_str, 16)
    # Convert the integer back to hexadecimal string representation
    mac_hex_string = format(mac_integer, '012x')  # '012x' ensures zero-padding to 12 characters

    # Insert ":" to separate each segment of the MAC address
    return ":".join([mac_hex_string[i:i+2] for i in range(0, len(mac_hex_string), 2)])


class BTSVCController(udi_interface.Node):

    id = 'BltSvc'
    drivers = [
    #Status:enabled/disabled
        {'driver': 'ST', 'value': 0, 'uom': 25},
        #Paried device in text
        {'driver': 'GV0', 'value': 0, 'uom': 25}
    ]

    def __init__(self, polyglot):
        super().__init__(polyglot, btCtrlAddress, btCtrlAddress, btCtrlName)
        self.Parameters = Custom(polyglot, 'customparams')
        #self.name = "MQTT Controller"
        self.name = btCtrlName 
        self.address = btCtrlAddress 
        self.primary = self.address
        self._mqttc = None
        self.poly.subscribe(polyglot.START, self.start, btCtrlAddress)
        self.poly.subscribe(polyglot.CUSTOMPARAMS, self.parameter_handler)
        # self.poly.subscribe(polyglot.POLL, self.poll)
        self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.ready()
        self.poly.addNode(self)   

    def start(self):
        self.addAllNodes()
        self.poly.updateProfile()
        self.poly.setCustomParamsDoc()
        try:
            mqttThread = threading.Thread(target=self._startMqtt, name='SysConfigMqtt')
            mqttThread.daemon = False
            mqttThread.start()
        except Exception as ex:
            LOGGER.error(str(ex))

    def stop(self):
        pass

    def parameter_handler(self, params):
        self.poly.Notices.clear()
        self.Parameters.load(params)
        return True

    def _startMqtt(self)->bool:
        cafile= '/usr/local/etc/ssl/certs/ud.ca.cert'
        certs = find_files_with_extension('./','.cert')
        keys = find_files_with_extension('./','.key')
        if len(certs) == 0 or len(keys) == 0:
            LOGGER.warning("no cert/key for mqtt connectivity")
            return False

        LOGGER.info('Using SSL cert: {} key: {} ca: {}'.format(certs[0], keys[0], cafile))
        try:
            self._mqttc=mqtt.Client(self.id, True)
            self.sslContext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, cafile=cafile)
            self.sslContext.load_cert_chain(certs[0], keys[0])
            self._mqttc.tls_set_context(self.sslContext)
            self._mqttc.tls_insecure_set(True)
            self._mqttc.on_connect=self.on_connect
            self._mqttc.on_message = self.on_message
            self._mqttc.on_disconnect = self.on_disconnect
            self._mqttc.on_subscribe = self.on_subscribe
            self._mqttc.on_publish = self.on_publish
            self._mqttc.on_log = self.on_log
        except Exception as ex:
            LOGGER.error(str(ex))
        while True: 
            try:
                self._mqttc.connect_async('{}'.format(polyglot._server), int(polyglot._port), 10)
                self._mqttc.loop_forever()
            except ssl.SSLError as e:
                LOGGER.error("MQTT Connection SSLError: {}, Will retry in a few seconds.".format(e), exc_info=True)
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                LOGGER.exception("MQTT Connection error: {}".format(
                    message), exc_info=True)
                time.sleep(3)
        return True

    def on_connect(self, mqttc, userdata, flags, rc):
        self._mqttc.subscribe('sconfig/bluetooth/#', 0)
        self._mqttc.publish('config/bluetooth')
        self._mqttc.publish('config/bluetooth/list')

    def on_message(self, mqttc, userdata, msg):
        if msg == None or msg.topic == None:
            return
        if msg.topic == "sconfig/bluetooth/enabled":
            self.updateBTStatus(True)
        elif msg.topic == "sconfig/bluetooth/disabled":
            self.updateBTStatus(False)
        elif msg.topic == "sconfig/bluetooth/list":
            self.updateBTList(msg.payload)
        elif msg.topic == "sconfig/bluetooth/scan":
            self.processScanResults(msg.payload)
        elif msg.topic == "sconfig/bluetooth/pair":
            self.processPair(msg.payload, True)
        elif msg.topic == "sconfig/bluetooth/unpair":
            self.processPair(msg.payload, False)
        elif msg.topic == "sconfig/bluetooth/forget":
            self.processForget(msg.payload)

    def on_disconnect(self, mqttc, userdata, rc):
        pass

    def on_publish(self, mqttc, userdata, mid):
        pass

    def on_subscribe(self, mqttc, userdata, mid, granted_qos):
        pass


    def on_log(self, mqttc, userdata, level, string):
        pass

    def updateBTStatus(self, enabled:bool):
        if enabled:
            self.setDriver('ST', 1, uom=25, force=True)
        else:
            self.setDriver('ST', 0, uom=25, force=True)

    def updateBTList(self, payload:str):
        try:
            data_array:[str] = json.loads(payload)
        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False

        if len(data_array) == 0:
            return False
        try:
            for devInfo in data_array:
                uuid=devInfo['uuid']
                name=devInfo['name']
                if uuid != None:
                    node=self.poly.getNode(get_pg3_address(uuid))
                    if node == None:
                        node = self.addDevice(uuid, name)
                    node.updatePairedStatus(True)

        except Exception as ex:
            LOGGER.error(str(ex))

    def processBT(self, index:int):
        if index == 0:
            self._mqttc.publish('config/bluetooth/disable')
        else:
            self._mqttc.publish('config/bluetooth/enable')

    def processScan(self):
        self._mqttc.publish('config/bluetooth/scan')

    def processScanResult(self, devInfo:str)->bool:
        if devInfo == None:
            return False

        try:
            uuid=devInfo['uuid']
            name=devInfo['name']
            self.addDevice(uuid, name, True)
            return True

        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False

    def processPair(self, payload, bPaired:bool)->bool:

        try:
            dInfo=json.loads(payload)
            uuid=dInfo['uuid']
            name=dInfo['name']
            if uuid != None:
                uuid = get_pg3_address(uuid)
                node = self.poly.getNode(uuid)
                if node == None:
                    return False
                node.updatePairedStatus(bPaired)
                return True 
            
        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False

    def processForget(self, payload)->bool:

        try:
            dInfo=json.loads(payload)
            uuid=dInfo['uuid']
            name=dInfo['name']
            if uuid != None:
                uuid = get_pg3_address(uuid)
                polyglot.delNode(uuid)
                return True
            return False

        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False


    def processScanResults(self, payload:str):
        try:
            data_array:[str] = json.loads(payload)
        except Exception as ex:
            LOGGER.error(
                "Failed to parse MQTT Payload as Json: {} {}".format(ex, payload)
            )
            return False

        if len(data_array) == 0:
            return False

        for devInfo in data_array:
            self.processScanResult(devInfo)
        return True

    def addAllNodes(self): 
        config = self.poly.getConfig()
        if config == None or config['nodes'] == None:
            return

        for node in config['nodes']:
            nodeDef = node['nodeDefId']
            if nodeDef == "BltSvc":
                continue
            address = node['address']
            primary = node['primaryNode']
            name = node['name']
            if nodeDef == "BltDev":
                self.addDevice(address, name, False)

        LOGGER.info("Done adding bluetooth devices, ...")

    def addDevice(self, endDeviceAddress:str, devName:str, convert=True):
        if endDeviceAddress == None or devName == None:
            return

        normalizedAddress=endDeviceAddress
        if convert == True: 
            normalizedAddress=get_pg3_address(endDeviceAddress)
        devNode=BluetoothDevNode(self, self.poly, normalizedAddress, devName)
#        if convert == True:
#            endDeviceAddress=get_mac_address(normalizedAddress)
        if devNode == None:
            LOGGER.error("failed creating bt device node ..." )
            return
        self.poly.addNode(devNode)
        return devNode

    def query(self):
        self._mqttc.publish('config/bluetooth')
        self._mqttc.publish('config/bluetooth/list')
    
    def processCommand(self, cmd)->bool:
        LOGGER.info('Got command: {}'.format(cmd))
        if 'cmd' in cmd:
            if cmd['cmd'] == 'BT' :
                index=int(cmd['value'])
                self.processBT(index)
                return True

            elif cmd['cmd'] == 'SCAN':
                self.processScan()
                return True

            elif cmd['cmd'] == 'QUERY':
                self.query()
                return True
            return False

    commands = {
            'BT': processCommand,
            'SCAN': processCommand,
            'QUERY': processCommand,
            }

    def publishCommand(self, tc:str, cmd:str):
        self._mqttc.publish(topic=tc, payload=cmd)

class BluetoothDevNode(udi_interface.Node):

    id = 'BltDev'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]

    def __init__(self, controller, polyglot, address, name):
        super(BluetoothDevNode, self).__init__(polyglot, btCtrlAddress, address, name)
        self.controller=controller
        self.updatePairedStatus(False)

    def updatePairedStatus(self, paired:bool):
        if paired:
            self.setDriver('ST', 1, uom=25, force=True)
        else:
            self.setDriver('ST', 0, uom=25, force=True)

    def getUUID(self):
        return self.address.replace('_',':')

    def query(self):
        pass

    def getDeviceJson(self):
        dev=dict()
        dev['uuid']=get_mac_address(self.address)
        dev['name']=self.name
        return json.dumps(dev)

    def processPair(self):
        self.controller.publishCommand('config/bluetooth/pair', self.getDeviceJson())

    def processUnpair(self):
        self.controller.publishCommand('config/bluetooth/unpair', self.getDeviceJson())

    def processForget(self):
        self.controller.publishCommand('config/bluetooth/forget', self.getDeviceJson())

    def processCommand(self, cmd)->bool:
        if 'cmd' in cmd:
            if cmd['cmd'] == 'PAIR' :
                self.processPair()

            elif cmd['cmd'] == 'UNPAIR':
                self.processUnpair()

            elif cmd['cmd'] == 'FORGET':
                self.processForget()

            elif cmd['cmd'] == 'QUERY':
                self.query()
            return True
        else:
            return False

    commands = {
            'PAIR': processCommand,
            'UNPAIR': processCommand,
            'FORGET': processCommand,
            'QUERY': processCommand,
            }

    


def poll(polltype):

    if 'shortPoll' in polltype:
        LOGGER.info("short poll")
    elif 'longPoll' in polltype:
        LOGGER.info("long poll")

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start(version.ud_plugin_version)
        BTSVCController(polyglot)
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
