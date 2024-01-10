#!/usr/bin/env python3
"""
Polyglot v3 node server communicating with Casambi USB dongle 
Copyright (C) 2023  Universal Devices
"""
from ud_audio import UDAudioPlayer
from nls_gen import NLSGenerator
import udi_interface
import sys
import os
import time
import threading
import json

LOGGER = udi_interface.LOGGER
polyglot = None
path = None
lock = threading.Lock()
udAudioPlayer = UDAudioPlayer()
nlsGen = NLSGenerator()

class AudioPlayerNode(udi_interface.Node):
    id = 'mpgPlayer'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV0', 'value': 0, 'uom': 25}
            ]

    def __init__(self, polyglot, primary, address, name):
        super(AudioPlayerNode, self).__init__(polyglot, primary, address, name)

    def updateState(self, state, index):
        if state == 1:
            self.setDriver('ST', 1, uom=25, force=True)
            self.setDriver('GV0', index, uom=25, force=True)
        else:
            self.setDriver('ST', 0, uom=25, force=True)
            self.setDriver('GV0', 0, uom=25, force=True)

    def processCommand(self, cmd):
        LOGGER.info('Got command: {}'.format(cmd))
        if 'cmd' in cmd:
            if cmd['cmd'] == 'PLAY':
                try:
                    sparam = str(cmd['query']).replace("'","\"")
                    jparam=json.loads(sparam)
                    index=int(jparam['PLAYLIST.uom25'])
                    if index == 0:
                        return
                    filename=nlsGen.getFilePath(path, index)
                    if filename == None:
                        return
                    LOGGER.info('Playing #{}:{}'.format(index, filename))
                    udAudioPlayer.stop(self)
                    udAudioPlayer.play(self, index, filename)
                except Exception as ex:
                    LOGGER.error(ex)
        
            elif cmd['cmd'] == 'STOP':
                udAudioPlayer.stop(self)

            elif cmd['cmd'] == 'QUERY':
                udAudioPlayer.query(self)

    commands = {
            'PLAY': processCommand,
            'STOP': processCommand,
            'QUERY': processCommand
            }

def addAudioNode(address)->bool:
    if address == None:
        address = "0"
    if polyglot.getNode(address):
        LOGGER.info('AudioNode already exists ...')
        return False
    else:
        name = 'AudioPlayer'
        LOGGER.info('Adding AudioPlayer node')
        node = AudioPlayerNode(polyglot, address, address, name)
        polyglot.addNode(node)
        udAudioPlayer.query(node)
        return True

'''
Read the user entered custom parameters. This should only be the serial
port.
'''

def parameterHandler(params):
    global polyglot
    global path
    global nlsGen

    if params == None:
        polyglot.Notices['path'] = 'path cannot be blank ...' 
    elif 'path' in params:
        path=params['path']
        if path == None:
            polyglot.Notices['path'] = 'path cannot be blank ...' 
        elif os.path.isdir(path):
            LOGGER.info('we are using {} as path'.format(path))
            polyglot.Notices.clear()
            nlsGen.generate(path)
            polyglot.updateProfile()
            addAudioNode("0")
        else:
            polyglot.Notices['path'] = '{} is not a directory'.format(path)

def poll(polltype):

    if 'shortPoll' in polltype:
        LOGGER.info("short poll")
    elif 'longPoll' in polltype:
        LOGGER.info("long poll")


def listener():

    LOGGER.info('Starting serial port listener')
    while (True):
        LOGGER.info("listener thread")
        time.sleep(10)

        
        #status = ser.readline().decode('utf-8')
        # status looks like: OK+CH1=0
        #LOGGER.info('incoming: {}'.format(status))

def oldCrap(): 
        try: 
            if status.startswith('OK'):
                status = status.split('+')[1]

            (channel, state) = status.split('=')
            address = channel.lower()

            if polyglot.getNode(address):
                LOGGER.info('Updatiung {} status to {}'.format(address, state.rstrip()))
                polyglot.getNode(address).update(state.rstrip())
            else:
                name = 'Relay-{}'.format(channel)
                LOGGER.info('Adding new node for channel {}'.format(channel))
                node = RelayNode(polyglot, address, address, name, ser)
                polyglot.addNode(node)
                node.update(state.rstrip())

        except Exception as e:
            LOGGER.error('Error parsing relay status: {}'.format(str(e)))
        




if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start('1.0.4')


        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.POLL, poll)

        # Start running
        polyglot.ready()
        polyglot.setCustomParamsDoc()

        # Start serial port listener
        listen_thread = threading.Thread(target = listener)
        listen_thread.daemon = True
        listen_thread.start()

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

