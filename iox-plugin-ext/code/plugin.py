#!/usr/bin/env python3

"""
Plugin schema processor and validator
Copyright (C) 2024 Universal Devices
"""

import fastjsonschema
import json
import os
from node import Nodes
from editor import Editors
from plugin_meta import PluginMetaData


PLUGIN_SCHEMA_FILE="schemas/plugin.schema.json"

CMD_SCHEMA="schemas/commands.schema.json"
EDITOR_SCHEMA="schemas/editor.schema.json"
ICON_SCHEMA="schemas/icon.schema.json"
NODEP_SCHEMA="schemas/node.properties.schema.json"
NODE_SCHEMA="schemas/node.schema.json"
PMETA_SCHEMA="schemas/plugin.meta.schema.json"
PROP_SCHEMA="schemas/properties.schema.json"
UOM_SCHEMA="schemas/uom.schema.json"

class Plugin:

    def __init__(self, plugin_file, schema=PLUGIN_SCHEMA_FILE):
        self.meta = None
        self.editors=Editors()
        self.nodes:Nodes 
        self.isValid = False
        if plugin_file == None:
            return

        try:
            self.isValid=self.validate_json(schema, plugin_file)
            if not self.isValid:
                return
            with open(plugin_file, 'r') as file:
                plugin_json = json.load(file)

            if 'plugin' in plugin_json:
                self.meta = PluginMetaData(plugin_json['plugin'])
            if 'editors' in plugin_json:
                self.editors.addEditors(plugin_json['editors'])
            if 'nodes' in plugin_json:
                self.nodes = Nodes(plugin_json['nodes'])

        except Exception as ex:
            raise


         


    def validate_json(self, schema:str, payload:str)->bool:
        ''' 
            Does not suppot file refernences
        '''
        return True

        #use later when supported
        if schema == None or json == None:
            return False
        try:
            with open(schema, 'r') as file:
                plugin_schema = json.load(file)
            with open(CMD_SCHEMA,'r') as file:
                cmd_schema = json.load(file)
            with open(EDITOR_SCHEMA,'r') as file:
                editor_schema = json.load(file)
            with open(ICON_SCHEMA,'r') as file:
                icon_schema = json.load(file)
            with open(NODEP_SCHEMA,'r') as file:
                nodep_schema = json.load(file)
            with open(NODE_SCHEMA,'r') as file:
                node_schema = json.load(file)
            with open(PMETA_SCHEMA,'r') as file:
                pmeta_schema = json.load(file)
            with open(PROP_SCHEMA,'r') as file:
                prop_schema = json.load(file)
            with open(UOM_SCHEMA,'r') as file:
                uom_schema = json.load(file)

            handlers={
                    'commands.schema.json': cmd_schema,
                    'editor.schema.json': editor_schema,
                    'icon.schema.json': icon_schema,
                    'node.properties.schema.json': nodep_schema,
                    'node.schema.json': node_schema,
                    'plugin.meta.schema.json': pmeta_schema,
                    'properties.schema.json': prop_schema,
                    'uom.schema.json': uom_schema
                    }

            validate = fastjsonschema.compile(plugin_schema, handlers)
            validate(payload)
            return True
        except Exception as ex:
            return False

         

mod=Plugin("../ext/dimmer.iox_plugin.json")
pass