#!/usr/bin/env python3

"""
Class for handling node definitions 
Copyright (C) 2024 Universal Devices
"""

import json
import os
from node_properties import NodeProperties
from commands import Commands


class NodeDetails:
    def __init__(self, node):
        self.id = None
        self.name = None
        self.parent = None
        self.icon = None
        self.properties:NodeProperties
        self.commands:Commands

        if node == None:
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
            raise

class Nodes:
    
    def __init__(self,nodes):
        self.nodes = {}

        if nodes == None:
            return
        try:
            for node in nodes:
                n = NodeDetails(node)
                self.nodes[n.id] = n
        except Exception as ex:
            raise
        