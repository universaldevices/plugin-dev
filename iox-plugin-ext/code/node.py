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


class NodeDetails:
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

    def toXML(self)->(str,str):
        nls = ""
        nodedef = f"<nodedef id=\"{self.id}\" nls=\"{self.id}\">"
        nls += f"\nND-{self.id}-NAME={self.name}"
        if self.icon != None:
            nls += f"\nND-{self.id}-ICON={self.icon}"

        nprops, nprops_nls = self.properties.toXML(self.id)
        if nprops:
            nodedef += f"\n{nprops}" 
        if nprops_nls:
            nls += f"\n{nprops_nls}"

            #go through all the properties and add them as commands + init if they are set+get
        for p in self.properties.getAll():
            pty = self.properties.getProperty(p)
            if pty.isSet(): #set/init
                editor_id = pty.editor.id
                if pty.editor.isRef():
                    editor_id = pty.editor.idref
                self.commands.addInit("accepts", pty.id, editor_id)

            cmds, cmds_nls = self.commands.toXML(self.id)
            if cmds:
                nodedef+=f"\n{cmds}"
            if cmds_nls:
                nls += f"\n{cmds_nls}"
            

        nodedef += "\n<nodedef>"
        return nodedef, nls

class Nodes:
    
    def __init__(self,nodes):
        self.nodes = {}

        if nodes == None:
            LOGGER.critical("no nodes were given ... ")
            return
        try:
            for node in nodes:
                n = NodeDetails(node)
                self.nodes[n.id] = n
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def toXML(self)->(str, str):
        nls=""
        nodedefs="<nodedefs>\n"
        for n in self.nodes:
            node=self.nodes[n]
            nd, nlsx = node.toXML()
            if nd:
                nodedefs+=f"\n{nd}"
            if nlsx:
                nls+=f"\n{nlsx}"

        nodedefs += "\n<nodedefs>" 
        return nodedefs, nls