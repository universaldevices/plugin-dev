
#!/usr/bin/env python3

"""
Manages iox to modbus mappings 
Copyright (C) 2024 Universal Devices
"""
import udi_interface
LOGGER = udi_interface.LOGGER
import os
from ioxplugin import NodePropertyDetails, NodeProperties, NodeDefs, NodeDefDetails, Plugin, IoXTransport, IoXTCPTransport
from pymodbus.client import ModbusTcpClient


MODBUS_REGISTER_TYPES=('coil', 'discrete-input', 'input', 'holding')
MODBUS_REGISTER_DATA_TYPES=('int16','uint16','int32','uint32','float32','string')


#MODBUS_COMMUNICATION_MODES=('TCP', 'Serial')
#for now just TCP
MODBUS_COMMUNICATION_MODES=('TCP')
MODBUS_ADDRESSING_MODES=('0-based', '1-based')


class ModbusComm:
    def __init__(self, comm_data):
        if comm_data == None:
            raise Exception ("Need comm data for modbus ...")
            return
        self.addressing_mode = '1-based'
        self._transport:IoXTransport = None
        self.transport = None 
        self._client = None
        try: 
            if 'transport' in comm_data:
                self._transport:IoXTransport = IoXTransport(comm_data['transport'])
            if 'addressing_mode' in comm_data:
                self.addressing_mode = comm_data['addressing_mode']
        except Exception as ex:
            raise

    def is_valid(self):
        if not self._transport.getMode() in MODBUS_COMMUNICATION_MODES:
            LOGGER.error(f"{self._transport.getMode()} is not a valid communication mode for this plugin ..")
            return False
        return True


class ModbusRegister:
    def __init__(self, protocol_data):
        if protocol_data == None:
            raise Exception ("Need protocol data ...")
        
        self.register_address = None
        self.ref_address = None
        self.register_type = None
        self.register_data_type = None
        self.num_registers = 1
        self.eval = None
        self.value = None
        self.is_master = True

        try:
            if 'register_address' in protocol_data:
                self.register_address = protocol_data['register_address']
            if 'register_type' in protocol_data:
                self.register_type = protocol_data['register_type']
            if 'register_data_type' in protocol_data:
                self.register_data_type = protocol_data['register_data_type']
            if 'num_registers' in protocol_data:
                self.num_registers = protocol_data['num_registers']
            if 'eval' in protocol_data:
                self.eval = protocol_data['eval']

            if self.register_address == None:
                raise Exception("Expected a register address ... ")

            if self.register_type == None:
                self.is_master = False
                self.register_type = 'input' 
                self.register_data_type = 'uint16'

            if self.register_data_type ==  None:
                self.is_master = False
                self.register_data_type = 'uint16'

            if not self.register_type in MODBUS_REGISTER_TYPES:
                raise Exception(f"{self.register_type} is not a valid modbus register type ...")

            if not self.register_data_type in MODBUS_REGISTER_DATA_TYPES:
                raise Exception(f"{self.register_data_type} is not a valid modbus register data type ...")


            if self.register_data_type == 'int16' or self.register_data_type == 'uint16':
                self.num_registers = 1
            elif self.register_data_type == 'int32' or self.register_data_type == 'uint32':
                self.num_registers = 2
            elif self.register_data_type == 'float32': 
                self.num_registers = 2


        except Exception as ex:
            raise

        def getRegisterValue(self):
            try:
                #get the value from modbus sending it the number of registers to be read
                val = 1
                if self.register_data_type == 'string':
                    return str(val)

                return (val)
            except Exception as ex:
                LOGGER.critical(str(ex))
                return -1
        
        def setRegisterValue(self, value)->bool:
            try:
                if value == None:
                    return False
                #get the value from modbus sending it the number of registers to be read
                if self.register_data_type == 'string' and not isinstance(value, str):
                    LOGGER.error(f"{value} is not a string ")
                    return False
                    #set the string value
                    return True

                value = (value)
                #set the value
                return True
            except Exception as ex:
                LOGGER.critical(str(ex))
                return False 

class ModbusIoXNode:
    def __init__(self, node:NodeDefDetails):
        self.registers = {}
        if node == None:
            LOGGER.critical("No node definitions provided ...")
            raise Exception ("No node definitions provided ...")
        try:
            nps:NodeProperties=node.properties
            if nps == None:
                raise Exception (f"No properties for {node.name} ...")

            protocol_data = nps.getProtocolData()
            if protocol_data == None or len (protocol_data) == 0:
                raise Exception (f"No protocol data for {node.name} ...")

            for pid in protocol_data:
                self.registers[pid]=ModbusRegister(protocol_data[pid])

            for _, item in self.registers.items():
                if not item.is_master: 
                    continue
                #it's master. So, now find all the other items
                #that have the same address
                for _, sitem in self.registers.items():
                    if sitem.is_master:
                        continue
                    if item.register_address == sitem.register_address:
                        sitem.ref_address = item.register_address
                        sitem.register_address = None

            pass

        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def queryProperty(self, client, property_id:str):
        if property_id == None:
            LOGGER.error("You need to have a property id ...")
            return None
        mregister:ModbusRegister = self.registers[property_id]
        if mregister == None:
            LOGGER.error(f"No registers for {property_id}")
            return None
        return mregister.getRegisterValue()
    
    def read(self, client, unit_id):
 #       if self.type == 'holding':
 #           result = client.read_holding_registers(self.address, 1, unit=unit_id)
 #       elif self.type == 'input':
 #           result = client.read_input_registers(self.address, 1, unit=unit_id)
 #       if result.isError():
 #           print(f"Error reading register {self.name}")
 #       else:
 #           print(f"{self.name}: {result.registers[0]}")
        pass

    def setProperty(self, client, property_id:str, value):
        if property_id == None or value == None:
            LOGGER.error("You need to have a property id and value ...")
            return None
        mregister:ModbusRegister = self.registers[property_id]
        if mregister == None:
            LOGGER.error(f"No registers for {property_id}")
            return None
        return mregister.setRegisterValue(value)

class ModbusIoX:
    def __init__(self, plugin:Plugin):
        self.nodes = {}
        self._client = None
        
        if plugin == None or plugin.nodedefs == None:
            raise Exception ("No plugin and/or node definitions provided ...")
        try:
            if not plugin.protocol.isModbus():
                LOGGER.error("This plugin does not support modbus")
                raise Exception("This plugin does not support modbus")

            nodedefs=plugin.nodedefs.getNodeDefs()
            for n in nodedefs: 
                node:NodeDefDetails=nodedefs[n]
                if not node.isController:
                    self.nodes[node.id]=ModbusIoXNode(node)
            comm = ModbusComm(plugin.protocol.config)
            if not comm.is_valid():
                raise Exception ("Invalid protocol. Currently TCP only ...")
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def is_connected(self):
        return True if (self._client and self._client.is_connected()) else False
        
    def disconnect(self):
        if self.is_connected():
            self._client.close()
            self._client = None
        
    def connect(self, host, port)->bool:
        if self.is_connected():
            LOGGER.warn("Already connected ... ignoring")
            return True

        if host == None or len (host) <= 0 or port == None or port <= 0:
            LOGGER.error("To connect to modbus tcp, both host and port are mandatory ...")
            return False

        try:
            self._client = ModbusTcpClient(host=host, port=port)
        
            connection = self._client.connect()
            if connection == None:
                LOGGER.error(f"failed connecting to modbus server @ {client.host}:{client.port}")
                return False
            LOGGER.info(f"connected to modbus server @ {client.host}:{client.port}")
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    def queryProperty(node_id:str, property_id:str):
        if nodeid == None or property_id == None:
            LOGGER.error("Need node id and property id ...")
            return None

        node:ModbusIoXNode = self.nodes[node_id]
        if node == None:
            LOGGER.error(f"No node for {node_id} ...")
            return None

        return node.queryProperty(self._client, propety_id) 

    def setProperty(node_id:str, property_id:str, value):
        if nodeid == None or property_id == None or value == None:
            LOGGER.error("Need node id, property id, and value ...")
            return None

        node:ModbusIoXNode = self.nodes[node_id]
        if node == None:
            LOGGER.error(f"No node for {node_id} ...")
            return None

        return node.setProperty(self._client, propety_id, value) 
