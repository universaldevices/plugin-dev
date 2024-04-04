#!/usr/bin/env python3

"""
Python class representing all properties 
Copyright (C) 2024 Universal Devices
"""

import json
import os

PROPERTIES_SCHEMA_FILE="schemas/properties.schema.json"

class PropertyDetails:
    def __init__(self, elements):
        try:
            self.id = elements['enum'][0]
            self.description = elements ['description']
        except Exception as ex:
            raise

class Properties:
    def __init__(self):
       self.properties = {}
       try:
            with open(PROPERTIES_SCHEMA_FILE, 'r') as file:
                json_data = json.load(file)
                self.__init_elements(json_data)
       except Exception as ex:
            raise

    def __init_elements(self, json_data:str)->object:
       all = json_data['oneOf']
       if all == None: 
            return None
       for p in all: 
            prD = PropertyDetails(p)
            self.properties[prD.id]=prD

    def getAll(self):
        return self.properties

    def getProperty(self, property:str)->PropertyDetails:
        return self.properties[property]

properties=Properties()
pass 