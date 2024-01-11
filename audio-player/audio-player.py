#!/usr/bin/env python3
"""
Polyglot v3 node server communicating with Casambi USB dongle 
Copyright (C) 2023  Universal Devices
"""

import os
current_path = os.environ['PATH']
ffprog_path='/usr/local/bin'
os.environ['PATH'] = f'{ffprog_path}:{current_path}'

from nls_gen import NLSGenerator
import udi_interface
import sys
import time
import threading
import json
import pyaudio
from pydub import AudioSegment

LOGGER = udi_interface.LOGGER
polyglot = None
path = None
defaultSoundPath='./sounds'
#the speaker on the back
defaultOutputDevice=2
#lock = threading.Lock()

class _AudioPlayerParams:
    isPlaying :bool = False
    toStop :bool = False
    mediaPath: str = None
    node = None
    index: int = 0


AudioPlayerParams:_AudioPlayerParams = _AudioPlayerParams()

chunk = 4096
def audio_player_thread():
    if AudioPlayerParams.node != None:
        AudioPlayerParams.node.updateState(1, AudioPlayerParams.index)
    pd = AudioSegment.from_file(AudioPlayerParams.mediaPath)
    p = pyaudio.PyAudio()

    stream = p.open(output_device_index=defaultOutputDevice, format =
        p.get_format_from_width(pd.sample_width),
        channels = pd.channels,
        rate = pd.frame_rate,
        output = True)
    i = 0
    data = pd[:chunk]._data
    while data and not AudioPlayerParams.toStop:
        stream.write(data)
        i += chunk
        data = pd[i:i + chunk]._data

    stream.close()    
    p.terminate()
    if AudioPlayerParams.node != None:
        AudioPlayerParams.node.updateState(0, 0)
    AudioPlayerParams.isPlaying = False
    AudioPlayerParams.toStop = False

class UDAudioPlayer:

    def play(self, node, index, path:str) -> bool:
        while AudioPlayerParams.isPlaying:
            time.sleep(0.5) 
        AudioPlayerParams.isPlaying = True
        AudioPlayerParams.toStop = False
        AudioPlayerParams.mediaPath = path
        AudioPlayerParams.node = node
        AudioPlayerParams.index = index
        # Start audio player thread 
        ap_thread = threading.Thread(target = audio_player_thread)
        ap_thread.daemon = False
        ap_thread.start()

    def stop(self, node):
        if not AudioPlayerParams.isPlaying:
            return
        AudioPlayerParams.node = node
        AudioPlayerParams.toStop = True

    def query(self, node):
        if AudioPlayerParams.isPlaying:
            node.updateState(1, AudioPlayerParams.index)
        else:
            node.updateState(0, 0)

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
    global defaultSoundPath

    if params == None:
        LOGGER.info("using default sounds ...")
        path=defaultSoundPath
    elif 'path' in params:
        path=params['path']

    if path == None or path == '':
        LOGGER.info("using default sounds ...")
        path=defaultSoundPath

    if not os.path.isdir(path):
        polyglot.Notices['path'] = '{} is not a valid directory. Using defaults ... '.format(path)
        path=defaultSoundPath

    LOGGER.info('we are using {} as path'.format(path))
    polyglot.Notices.clear()
    nlsGen.generate(path)
    polyglot.updateProfile()
    addAudioNode("0")

def poll(polltype):

    if 'shortPoll' in polltype:
        LOGGER.info("short poll")
    elif 'longPoll' in polltype:
        LOGGER.info("long poll")


if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start('1.0.2')


        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.POLL, poll)

        # Start running
        polyglot.ready()
        polyglot.setCustomParamsDoc()

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

