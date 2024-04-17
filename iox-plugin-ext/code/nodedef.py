#!/usr/bin/env python3

"""
Class for handling node definitions 
Copyright (C) 2024 Universal Devices
"""

import json
import os
from node_properties import NodeProperties
from commands import Commands
from log import LOGGER
from validator import validate_id
import ast


class NodeDefDetails:
    def __init__(self, node):
        self.id = None
        self.name = None
        self.parent = None
        self.icon = None
        self.properties:NodeProperties
        self.commands:Commands

        if node == None:
            LOGGER.critical("no node was given ... ")
            return
        try: 
            if 'id' in node:
                self.id = node['id']
            if 'name' in node:
                self.name = node['name']
            if 'parent' in node:
                self.parent = node['parent']
            if 'icon' in node:
                self.icon = node['icon']
            if 'properties' in node:
                self.properties = NodeProperties(node['properties']) 
            if 'commands' in node:
                self.commands=Commands(node['commands'])

        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def getPG3Commands(self)->[]:
        commands = []

        for c in self.commands.acceptCommands:
            command = self.commands.acceptCommands[c]
            commands.append(
                {
                    "id": f"{command.id}",
                    "name": f"{command.name}"
                }
            )
        return commands
                    


    def toIoX(self)->(str,str):
        nls = ""
        nodedef = f"<nodedef id=\"{self.id}\" nls=\"{self.id}\">"
        nls += f"\nND-{self.id}-NAME={self.name}"
        if self.icon != None:
            nls += f"\nND-{self.id}-ICON={self.icon}"

        nprops, nprops_nls = self.properties.toIoX(self.id)
        if nprops:
            nodedef += f"\n{nprops}" 
        if nprops_nls:
            nls += f"\n{nprops_nls}"

            #go through all the properties and add them as commands + init if they are set+get
        for p in self.properties.getAll():
            pty = self.properties.getProperty(p)
            if pty.isSet(): #set/init
                editor_id = pty.editor.getEditorId()
                self.commands.addInit("accepts", pty.id, pty.name, editor_id)

        cmds, cmds_nls = self.commands.toIoX(self.id)
        if cmds:
            nodedef+=f"\n{cmds}"
        if cmds_nls:
            nls += f"\n{cmds_nls}"
            

        nodedef += "\n<nodedef>"
        return nodedef, nls

    def validate(self):
        return validate_id(self.id) and self.commands.validate() and self.properties.validate()

class NodeDefs:
    
    def __init__(self,nodes):
        self.nodedefs = {}

        if nodes == None:
            LOGGER.critical("no nodes were given ... ")
            return
        try:
            for node in nodes:
                n = NodeDefDetails(node)
                self.nodedefs[n.id] = n
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def size(self):
        return len (self.nodedefs)

    def getNodeDefs(self):
        return self.nodedefs

    def toIoX(self)->(str, str):
        nls=""
        nodedefs="<nodedefs>\n"
        for n in self.nodedefs:
            node=self.nodedefs[n]
            nd, nlsx = node.toIoX()
            if nd:
                nodedefs+=f"\n{nd}"
            if nlsx:
                nls+=f"\n{nlsx}"

        nodedefs += "\n<nodedefs>" 
        return nodedefs, nls

    def validate(self):
        try:
            rc = True
            for n in self.nodedefs:
                if not self.nodedefs[n].validate():
                    rc = False
            return rc
        except Exception as ex:
            LOGGER.critical(str(ex))
            return False