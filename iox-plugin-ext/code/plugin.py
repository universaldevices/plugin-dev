#!/usr/bin/env python3

"""
Plugin schema processor and validator
Copyright (C) 2024 Universal Devices
"""

import fastjsonschema
import json
import os

UOM_SCHEMA_FILE="schemas/uom.schema.json"
EDITOR_SCHEMA_FILE="schemas/editor.schema.json"
PROPERTY_SCHEMA_FILE="schemas/properties.class.schema.json"

def validate_json(schema:str, json:str)->bool:
    if schema == None or json == None:
        return False
    try:
        validate = fastjsonschema.compile(schema)
        validate(json)
        return True
    except Exception as ex:
        return False

class UOMOption:
    def __init__(self, element):
        if element == None:
            return
        self.id=None
        self.min=None
        self.max=None
        self.description=None
        try:
            if 'enum' in element:
                self.id = element['enum'][0]
            elif 'min' in element:
                self.min=element['min']
            elif 'max' in element:
                self.max=element['max']
            self.description = element['description']
        except Exception as ex:
            raise

class UOMDetails:
    def __init__(self, elements):
        
        self.options = {}
        try:
            self.uom = elements['enum'][0]
            self.description = elements ['description']
            if 'oneOf' in elements:
                self.__init_options(elements ['oneOf'])
        except Exception as ex:
            raise

    def __init_options(self, options):
        try:
            if options == None:
                return
            for option in options:
                uomOption = UOMOption(option)
                self.options[uomOption.id]=uomOption
        except Exception as ex:
            raise



class PluginUOM:
    def __init__(self):
       self.uoms = {int,UOMDetails}
       try:
            with open(UOM_SCHEMA_FILE, 'r') as file:
                json_data = json.load(file)
                self.__init_elements(json_data)
       except Exception as ex:
            raise

    def __init_elements(self, json_data:str)->object:
       all = json_data['oneOf']
       if all == None: 
            return None
       for u in all: 
            uomD = UOMDetails(u)
            self.uoms[uomD.uom]=uomD

    def getAll(self):
        return self.uoms

    def getUOM(self, uom:int)->UOMDetails:
        return self.uoms[int]

       

class Property:
    def __init__(self, property_data):
        self._property_data = property_data
        self.isValid=validate_json(PROPERTY_SCHEMA_FILE, property_data)

    @property
    def id(self):
        return self._property_data.get('id')

    @id.setter
    def id(self, value):
        self._property_data['id'] = value

    @property
    def name(self):
        return self._property_data.get('name')

    @name.setter
    def name(self, value):
        self._property_data['name'] = value

    @property
    def mode(self):
        return self._property_data.get('mode')

    @mode.setter
    def mode(self, value):
        self._property_data['mode'] = value

    @property
    def editor(self):
        return self._property_data.get('editor')

    @editor.setter
    def editor(self, value):
        self._property_data['editor'] = value


class Editor:
    def __init__(self, editor_data):
        self._editor_data = editor_data
        self.isValid=validate_json(EDITOR_SCHEMA_FILE, editor_data)

    @property
    def id(self):
        return self._editor_data.get('id')

    @id.setter
    def id(self, value):
        self._editor_data['id'] = value

    @property
    def uom(self):
        return self._editor_data.get('uom')

    @uom.setter
    def uom(self, value):
        self._editor_data['uom'] = value

    @property
    def min(self):
        return self._editor_data.get('min')

    @min.setter
    def min(self, value):
        self._editor_data['min'] = value

    @property
    def max(self):
        return self._editor_data.get('max')

    @max.setter
    def max(self, value):
        self._editor_data['max'] = value

    @property
    def precision(self):
        return self._editor_data.get('precision')

    @precision.setter
    def precision(self, value):
        self._editor_data['precision'] = value

    @property
    def options(self):
        return self._editor_data.get('options')

    @options.setter
    def options(self, value):
        self._editor_data['options'] = value


dir = os.getcwd()
pluginUOM = PluginUOM()
pluginUOM.print()