
#!/usr/bin/env python3

"""
Manages iox to modbus mappings 
Copyright (C) 2024 Universal Devices
"""
import udi_interface
LOGGER = udi_interface.LOGGER
import os
from datetime import datetime
from ioxplugin import NodePropertyDetails, NodeProperties, NodeDefs, NodeDefDetails, Plugin, IoXTransport, IoXTCPTransport
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian


MODBUS_REGISTER_TYPES=('coil', 'discrete-input', 'input', 'holding')
MODBUS_REGISTER_DATA_TYPES=('int16','uint16','int32','uint32', 'int64', 'uint64', 'float32','float64', 'string')


#MODBUS_COMMUNICATION_MODES=('TCP', 'Serial')
#for now just TCP
MODBUS_COMMUNICATION_MODES=('TCP')
MODBUS_ADDRESSING_MODES=('0-based', '1-based')

iox_modbus_byte_order = Endian.BIG
iox_modbus_word_order = Endian.LITTLE


class ModbusComm:
    def __init__(self, comm_data):
        self.addressing_mode = '1-based'
        self._transport:IoXTransport = None
        self.transport = None 
        self._client = None
        self.bRtu = False
        if comm_data == None:
            LOGGER.warning("no comm data, using defaults ...")
            return
        comm_data = comm_data.getDetails()
        if comm_data == None:
            LOGGER.warning("no comm data, using defaults ...")
            return

        if 'config' in comm_data:
            comm_data = comm_data['config']
        else:
            LOGGER.warning("no config in comm data, using defaults ...")
            return

        try: 
            global iox_modbus_byte_order
            global iox_modbus_word_order
            if 'transport' in comm_data:
                self._transport:IoXTransport = IoXTransport(comm_data['transport'])
            if 'addressing_mode' in comm_data:
                self.addressing_mode = comm_data['addressing_mode']
            if 'is_rtu' in comm_data:
                self.bRtu = bool(comm_data['is_rtu'])
            if 'byte_order' in comm_data:
                iox_modbus_byte_order = comm_data['byte_order']
            if 'word_order' in comm_data:
                iox_modbus_word_order = comm_data['word_order']
            
        except Exception as ex:
            raise

    def is_valid(self):
        if self._transport == None:
            return True
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
        self.unit = 0
        self.is_master = True
        self.last_updated_time = datetime.now()
        self._client:ModbusTcpClient = None

        try:
            if 'register_address' in protocol_data:
                address = protocol_data['register_address']
                self.register_address = int(protocol_data['register_address'], 16) if address else 0
            if 'register_type' in protocol_data:
                self.register_type = protocol_data['register_type']
            if 'register_data_type' in protocol_data:
                self.register_data_type = protocol_data['register_data_type']
            if 'num_registers' in protocol_data:
                self.num_registers = protocol_data['num_registers']
            if 'unit' in protocol_data:
                self.unit = protocol_data['unit']
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
            elif self.register_data_type == 'int32' or self.register_data_type == 'uint32' or self.register_data_type == 'float32':
                self.num_registers = 2
            elif self.register_data_type == 'int64' or self.register_data_type == 'uint64' or self.register_data_type == 'float64':
                self.num_registers = 4


        except Exception as ex:
            raise

    def canRead(self):
        now = datetime.now()
        elapsed_time:datetime = now - self.last_updated_time
        return True if (elapsed_time.total_seconds() * 1000) >= 750 else False

    #return the last value stored and apply the eval expression
    #the eval expression that is passed takes precedence over the eval expression in the object
    def getRegisterValue(self, eval_expression):
        #apply eval
        eeval = eval_expression if eval_expression else self.eval
        if not eeval:
            return self.val

        eeval = eeval.replace('{rval}', f'{self.val}')
        unsafe_array = ['return','def','class','import', 'as', 'from', 'os', 'json', 'with', 'file', 'for', 'while', 'url', 'requests']
        for unsafe in unsafe_array:
            if unsafe in eeval:
                LOGGER.error(f"eval expression is not safe and cannot be run for {self.register_address if self.is_master else self.ref_address}")
                return None
        try:
            return eval(eeval)
        except Exception as ex:
            LOGGER.error(str(ex))
            return None
    
    def readRegister(self, eval_expression):
        if self._client == None or not self._client.connected:
            return None

        if not self.canRead():
            return self.getRegisterValue(None)

        try:
            response = None

            if self.register_type == 'coil':
                response = self._client.read_coils(self.register_address, self.num_registers, slave=self.unit)
            elif self.register_type == 'holding':
                response = self._client.read_holding_registers(self.register_address, self.num_registers, slave=self.unit)
            elif self.register_type == 'input':
                response = self._client.read_input_registers(self.register_address, self.num_registers, slave=self.unit)
            elif self.register_type == 'discrete-input':
                response = self._client.read_discrete_inputs(self.register_address, self.num_registers, slave=self.unit)
            
            if response.isError():
                LOGGER.error(f"Failed reading {self.register_type} @ {self.register_address}")
                return None

            global iox_modbus_byte_order
            global iox_modbus_word_order
            decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=iox_modbus_byte_order, wordorder=iox_modbus_word_order)
        
            if self.register_data_type == 'int16': 
                self.val = decoder.decode_16bit_int()
            elif self.register_data_type == 'int32':
                self.val = decoder.decode_32bit_int()
            elif self.register_data_type == 'int64':
                self.val = decoder.decode_64bit_int()
            elif self.register_data_type == 'uint16': 
                self.val = decoder.decode_16bit_uint()
            elif self.register_data_type == 'uint32':
                self.val = decoder.decode_32bit_uint()
            elif self.register_data_type == 'uint64': 
                self.val = decoder.decode_64bit_uint()
            elif self.register_data_type == 'float32':
                self.val = decoder.decode_32bit_float()
            elif self.register_data_type == 'float64':
                self.val = decoder.decode_64bit_float()
            elif self.register_data_type == 'string':
                byte_array = decoder.decode_string(self.num_registers*2)
                self.val = byte_array.decode('utf-8').rstrip('\x00')
            else:
                LOGGER.error(f"Invalid register data type : {self.register_data_type}")
                return None

            return self.getRegisterValue(eval_expression) 

        except Exception as ex:
            LOGGER.critical(str(ex))
            return None
        
    def writeRegister(self, value)->bool:
        try:
            if value == None:
                return False
            if not self.is_master:
                LOGGER.error(f"This is a reference register {self.ref_address} ... ignore writing to it ")
                return False

            global iox_modbus_byte_order
            global iox_modbus_word_order
            builder = BinaryPayloadBuilder(byteorder=iox_modbus_byte_order.BIG, wordorder=iox_modbus_word_order)
            #get the value from modbus sending it the number of registers to be read
            if self.register_data_type == 'string': 
                if not isinstance(value, str):
                    LOGGER.error(f"{value} is not a string ")
                    return False
                builder.add_string(value)
            elif self.register_data_type == 'int16':
                builder.add_16bit_int(value) 
            elif self.register_data_type == 'int32': 
                builder.add_32bit_int(value) 
            elif self.register_data_type == 'int64': 
                builder.add_64bit_int(value) 
            elif self.register_data_type == 'uint16':
                builder.add_16bit_uint(value) 
            elif self.register_data_type == 'uint32': 
                builder.add_32bit_uint(value) 
            elif self.register_data_type == 'uint64': 
                builder.add_64bit_uint(value) 
            elif self.register_data_type == 'float32':
                builder.add_32bit_float(value) 
            elif self.register_data_type == 'float64':
                builder.add_64bit_float(value) 
            else:
                LOGGER.error(f"Invalid data type {self.register_data.type}")
                return False

            payload = builder.to_registers()
            if not payload:
                LOGGER.error(f"Failed encoding the value for data type {self.register_data.type}")
                return False

            self._client.write_registers(self.register_address, payload)

            value = (value)
            #set the value
            return True
        except Exception as ex:
            LOGGER.critical(str(ex))
            return False 

    def setClient(self, client):
        self._client = client

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

        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def setClient(self, client):
        for _, register in self.registers.items():
            register.setClient(client)

    def getMaster(self, ref:str)->ModbusRegister:
        for _, register in self.registers.items():
            if not register.is_master:
                continue
            if register.register_address == ref:
                return register

        return None

    def queryProperty(self, property_id:str):
        if property_id == None:
            LOGGER.error("You need to have a property id ...")
            return None
        mregister:ModbusRegister = self.registers[property_id]
        if mregister == None:
            LOGGER.error(f"No registers for {property_id}")
            return None
        eval_expression = None
        if not mregister.is_master:
            eval_expression = mregister.eval
            mregister = self.getMaster(mregister.ref_address)

        if mregister == None:
            LOGGER.error(f"Couldn't find master register for {property_id}")
            return None

        return mregister.readRegister(eval_expression)
    
    def setProperty(self, property_id:str, value):
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
        self.host = None
        self.port = None
        self.is_rtu = False
        
        if plugin == None or plugin.nodedefs == None:
            LOGGER.error("No plugin and/or node definitions provided ...")
            return 
        try:
            if not plugin.protocol.isModbus():
                LOGGER.error("This plugin does not support modbus")
                raise Exception("This plugin does not support modbus")

            comm = ModbusComm(plugin.protocol)
            if not comm.is_valid():
                raise Exception ("Invalid protocol. Currently TCP only ...")
            self.is_rtu=comm.bRtu

            nodedefs=plugin.nodedefs.getNodeDefs()
            for n in nodedefs: 
                node:NodeDefDetails=nodedefs[n]
                if not node.isController:
                    self.nodes[node.id]=ModbusIoXNode(node)
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def isConnected(self):
        return True if (self._client and self._client.connected) else False
        
    def disconnect(self):
        if self.isConnected():
            self._client.close()
            self._client = None
            for _, node in self.nodes.items():
                node.setClient(None)
        
    def connect(self, host, port)->bool:
        if self.isConnected():
            LOGGER.warn("Already connected ... ignoring")
            return True

        if host == None or len (host) <= 0 or port == None or port <= 0:
            LOGGER.error("To connect to modbus tcp, both host and port are mandatory ...")
            return False

        if self.host == None or self.host != host:
            self.host = host

        if self.port == None or self.port != port:
            self.port = port

        try:
            if self.is_rtu:
                from pymodbus.transaction import ModbusRtuFramer as ModbusFramer
                self._client = ModbusTcpClient(host=host, port=port, framer=ModbusFramer)
            else:
                self._client = ModbusTcpClient(host=host, port=port)
            self._client.comm_params.timeout_connect=20 
            self._client.comm_params.timeout=20 
            connection = self._client.connect()
            if not connection:
                LOGGER.error(f"failed connecting to modbus server @ {client.host}:{client.port}")
                return False
            LOGGER.info(f"connected to modbus server @ {host}:{port}")

            for _,node in self.nodes.items():
                node.setClient(self._client)
            
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    def queryProperty(self, node_id:str, property_id:str):
        if node_id == None or property_id == None:
            LOGGER.error("Need node id and property id ...")
            return None

        node:ModbusIoXNode = self.nodes[node_id]
        if node == None:
            LOGGER.error(f"No node for {node_id} ...")
            return None

        if not self.isConnected():
            LOGGER.warning("Modbus client is not connected ... trying to reconnect")
            if not self.connect(self.host, self.port):
                LOGGER.warning("Failed connecting to modbus client ...")
                return None

        return node.queryProperty(property_id) 

    def setProperty(self, node_id:str, property_id:str, value):
        if nodeid == None or property_id == None or value == None:
            LOGGER.error("Need node id, property id, and value ...")
            return None

        node:ModbusIoXNode = self.nodes[node_id]
        if node == None:
            LOGGER.error(f"No node for {node_id} ...")
            return None

        if not self.isConnected():
            LOGGER.error("Modbus client is not connected ... trying to reconnect")
            return self.connect(self.host, self.port)

        return node.setProperty(propety_id, value) 
