
#!/usr/bin/env python3
# Modbus plugin for IoX
from typing import Dict, List

import udi_interface
import os
import sys
import logging
import time
import json
#from jsonschema import validate, ValidationError
from pymodbus.client import ModbusTcpClient

MODBUS_SCHEMA_FILE="./modbus.schema.json"

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class ModbusRegister:
    def __init__(self, register):
        if register == None:
            LOGGER.error("no register is defined ...")
            return

        self.name = register['name']
        self.address = register['address']
        self.type = register['type']
        self.data_type = register['dataType'] 

class ModbusDevice:
    def __init__(self, device):
        if device == None:
            LOGGER.error("no device is defined ...")
            return 

        self.name = device['name']
        self.id = device['id']
        self.pollingInterval = device['pollingInterval']
        self.registers = {}
        for reg in device['registers']:
            register = ModbusRegister(reg)
            self.registers[reg['address']] = register
    
class ModbusClient:
    def __init__(self, config_file, schema_file=MODBUS_SCHEMA_FILE):
        try:
            self.config_file = config_file
            self.schema_file = schema_file
            self.config = None
            self.schema = None
            self.bValid=False
            self.modbusClient = None
            self.devices = {}

            if self.__load_config():
                self.bValid=True
                for device in self.config['modbus']['devices']:
                    self.devices[device['id']] = ModbusDevice(device)

#            self.__load_schema()
#            if self.__validate_config():
#                for device in self.config['modbus']['devices']:
#                    self.devices[device['id']] = ModbuseDevice(device)

        except Exception as ex:
            LOGGER.error("Modbus Config is invalid ...")
            LOGGER.error(str(ex))

    def __load_config(self)->bool:
        try:
            with open(self.config_file, 'r') as file:
                self.config = json.load(file)
            return True
        except Exception as ex:
            LOGGER.error(f"failed loading {self.config_file}")
            return False

    def __load_schema(self):
        try:
            with open(self.schema_file, 'r') as file:
                self.schema = json.load(file)
                return True
        except Exception as ex:
            LOGGER.error(f"failed loading {self.schema}")
            return False

    def __validate_config(self):
        try:
            validate(instance=self.config, schema=self.schema)
            LOGGER.info("Modbus Config is valid ...")
            self.Valid=True
            return True
        except ValidationError as e:
            raise

    def isValidConfig(self)->bool:
        return self.bValid

    def getModusClient(self):
        if not isValidConfig():
            LOGGER.error("cannot connect because config is not valid ... ")
            return None
        try:
            if self.modbusClient == None:
                modbus_config = self.config['modbus']
                self.modbusClient = ModbusTcpClient(host=modbus_config['ip'], port=modbus_config['port'])
            return self.modbusClient
        except Exception as ex:
            LOGGER.error(str(ex))
            return None


    def connect(self)->bool:
        client=self.getModusClient()
        if client == None:
            return False
        if client.is_connected():
            return True

        connection = client.connect()
        if connection == None:
            LOGGER.error(f"failed connecting to modbus server @ {client.host}:{client.port}")
            return False
        LOGGER.info(f"connected to modbus server @ {client.host}:{client.port}")
        return True

    
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

modbus_configurator = ModbusClient('test.json')