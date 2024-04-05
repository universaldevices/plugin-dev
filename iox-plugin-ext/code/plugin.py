#!/usr/bin/env python3

"""
Plugin schema processor and validator
Copyright (C) 2024 Universal Devices
"""

import fastjsonschema
import json
import os
import node
import editor
import plugin_meta

PLUGIN_SCHEMA_FILE="schemas/plugin.schema.json"


class Plugin:

    def __init__(self, json, schema=PLUGIN_SCHEMA_FILE):
        self.meta = None
        self.editors:Editors=Editors()
        self.nodes:Nodes 
        self.isValid = False
        if json == None:
            return
        self.isValid=self.validate_json(schema, json)
        if not isValid:
            return 

        if 'plugin' in json:
            self.meta = PluginMetaData(json['plugin'])
        if 'editors' in json:
            self.editors.addEditors(json['editors'])
        if 'nodes' in json:
            self.nodes = Nodes(json['nodes'])

    def validate_json(self, schema:str, json:str)->bool:
        if schema == None or json == None:
            return False
        try:
            validate = fastjsonschema.compile(schema)
            validate(json)
            return True
        except Exception as ex:
            return False

         

