#!/usr/bin/env python3

"""
Plugin schema processor and validator
Copyright (C) 2024 Universal Devices
"""

import fastjsonschema
import json
import os

NODE_PROPERTIES_SCHEMA_FILE="schemas/node.properties.schema.json"

def validate_json(schema:str, json:str)->bool:
    if schema == None or json == None:
        return False
    try:
        validate = fastjsonschema.compile(schema)
        validate(json)
        return True
    except Exception as ex:
        return False

class NodeProperty:
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