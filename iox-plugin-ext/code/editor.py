#!/usr/bin/env python3

"""
Plugin schema processor and validator
Copyright (C) 2024 Universal Devices
"""

import json
import os

class EditorDetails:
    def __int__(self, editor):
        self.id=None
        self.uom=None
        self.min=None
        self.max=None
        self.step=None
        self.precision=None
        self.subset=None
        self.options=[]
        if editor == None:
            raise
        try:
            if 'idref' in editor:
                self.id = editor['idref']
            else:
                self.id=editor['id']
                self.uom=editor['uom']

                if 'subset' in editor:
                    self.subset = editor ['subset']
                else:
                    if 'min' in editor:
                        self.min = editor['min']
                    if 'max' in editor:
                        self.min = editor['min']
                    if 'step' in editor:
                        self.step = editor['step']
                    if 'precision' in editor:
                        self.precision = editor['precision']
                if 'options' in editor:
                    self.options = editor['options']
        except Exception as ex:
            raise

        def isSubset(self):
            return self.subset != None
        
        def isIdRef(self):
            return self.idref != None

__allEditors = None

class Editors:
    def __init__(self):
        global __allEditors
        self.editors = {}
        __allEditors=self
        
    def addEditors(self, editors):
        if editors == None:
            return
        try:
            for editor in editors:
                self.addEditor(editor)
        except Exception as ex:
            raise

    def addEditor(self, editor)->EditorDetails:
        if editor == None:
            return None
        try:
            ed=Editor(editor)
            if not ed.isIdRef():
                self.editors[ed.id]=ed
            return ed
        except Exception as ex:
            raise
            return None

    @staticmethod
    def getEditors()->Editors:
        global __allEditors
        if __allEditors == None:
            return None
        return __allEditors
