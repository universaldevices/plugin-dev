#!/usr/bin/env python3
"""
Directory listing class
Copyright (C) 2023  Universal Devices
"""
import udi_interface
import os

audio_node_drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25}
            ]

class AudioNode(udi_interface.Node):

    def __init__(self, polyglot, primary, address, name):
        super(RelayNode, self).__init__(polyglot, primary, address, name)

        try:
            #relay_id = bytes([int(address[2:])])

            self.on_str = 'AT+CH' + address[2:] + '=1'
            self.off_str = 'AT+CH' + address[2:] + '=0'

        except Exception as e:
            LOGGER.error('Failed to create on/off command strings: {}'.format(str(e)))


class AudioDirListing:
    path:str = None

    def __init__(path:str):
        self.path=path

    