#!/usr/bin/env python3

"""
Class for handling node properties
Copyright (C) 2024 Universal Devices
"""

import json
import os
from editor import Editors 



class NodePropertyDetails:
    def __init__(self, node_property):
        self.id = None
        self.name = None
        self.mode = None
        self.Editor = None

        if node_property == None:
            return
        try: 
            if 'id' in node_property:
                self.id = node_property['id']
            if 'name' in node_property:
                self.name = node_property['name']
            if 'mode' in node_property:
                self.mode = node_property['mode']
            if 'editor' in node_property:
                self.editor = Editors.getEditors().addEditor(node_property['editor'])
        except Exception as ex:
            raise

    def getMode(self):
        return self.mode

    def isSet(self)->bool:
        if self.mode == None:
            return true
        return 'set' in self.mode 

class NodeProperties:
    def __init__(self, node_properties):
        self.node_properties={}
        if node_properties == None:
            return
        try:
            for node_property in node_properties:
                np = NodePropertyDetails(node_property)
                self.node_properties[np.id]=np
                
        except Exception as ex:
            raise

    def getProperty(self, property):
        if property == None:
            return

        return self.node_properties[property]

