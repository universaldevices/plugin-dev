#!/usr/bin/env python3

"""
Class for handling node properties
Copyright (C) 2024 Universal Devices
"""

import json
import os
from editor import Editors
from log import LOGGER 



class NodePropertyDetails:
    def __init__(self, node_property):
        self.id = None
        self.name = None
        self.mode = None
        self.editor = None
        self.hide = False

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
            if 'hide' in node_property:
                self.hide = node_property['hide']
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def getMode(self):
        return self.mode

    def isSet(self)->bool:
        if self.mode == None:
            return true
        return 'set' in self.mode 

    def toXML(self, node_id:str)->(str, str):
        nls = ""
        st = f"<st id=\"{self.id}\" editor=\"{self.editor.id}\" />"
        nls = f"ST-{node_id}-{self.id}-NAME = {self.name}"
        return st, nls


class NodeProperties:
    def __init__(self, node_properties):
        self.node_properties={}
        if node_properties == None:
            LOGGER.critical("no node properties were given ... ")
            return
        try:
            for node_property in node_properties:
                np = NodePropertyDetails(node_property)
                self.node_properties[np.id]=np
                
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def getProperty(self, property):
        if property == None:
            LOGGER.warn("property is null ... ")
            return

        return self.node_properties[property]

    def toXML(self, node_id:str)->(str, str):
        nls = ""
        sts = "<sts>"
        try:
            for np in self.node_properties:
                node_property = self.node_properties[np]
                sts_np, nls_np = node_property.toXML(node_id)
                if sts_np:
                    sts += f"\n{sts_np}"
                if nls_np:
                    nls += f"\n{nls_np}"
            sts += "\n</sts>"
            return sts, nls
        except Exception as ex:
            LOGGER.critical(str(ex))


    def getAll(self):
        return self.node_properties