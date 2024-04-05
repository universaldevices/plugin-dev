#!/usr/bin/env python3

"""
Class for handling node commands
Copyright (C) 2024 Universal Devices
"""

import json
import os
from editor import Editors 

class CommandParam:

    def __init__(self, param):
        self.id = None
        self.name = None
        self.editor: None
        if param == None:
            return

        try:
            if 'id' in param:
                self.id = param['id']
            if 'name' in param:
                self.name = param['name']
            if 'editor' in param:
                self.editor = Editors.getEditors().addEditor(param['editor']) 
        except Exception as ex:
            raise


class CommandDetails:

    def __init__(self, command):
        self.id = None
        self.name = None
        self.params = {}
        if command == None:
            return

        try: 
            if 'id' in command:
                self.id = command['id']
            if 'name' in command:
                self.name = command['name']
            if 'params' in command:
                params = command['params']
                for param in params:
                    p = CommandParam(param)
                    self.params[p.id]=p

        except Exception as ex:
            raise

class Commands:
    def __init__(self, commands):
        self.acceptCommands={}
        self.sendCommands={}
        if commands == None:
            return
        try:
            if 'accepts' in commands:
                accepts = commands['accepts']
                for accept in accepts:
                    a = CommandDetails(accept)
                    self.acceptCommands[a.id]=a

            if 'sends' in commands:
                sends = commands['sends']
                for send in sends:
                    s = CommandDetails(send)
                    self.sendCommands[s.id]=s
        except Exception as ex:
            raise

