#!/usr/bin/env python3
"""
Polyglot v3 plugin for audio playback 
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
import json
import threading
import vlc

LOGGER = udi_interface.LOGGER
polyglot = None
path:str = None
defaultSoundPath='./sounds'
SPEAKER_OUT = '/dev/dsp1' 
BLUETOOTH_OUT = '/dev/dsp'
defaultOutputDevice=SPEAKER_OUT
stations:str = None

#create vlc instance
vlc_instance = vlc.Instance('--no-xlib') 
# Create VLC media player

def play_stopped(event, nums):
    global udAudioPlayer
    udAudioPlayer.stopped()

def audio_player_thread():
    global udAudioPlayer
    udAudioPlayer.playVLC()


class AudioPlayer:
    def __init__(self): 
        self.node = None
        self.index: int = 0
        self.outputDevice: str = defaultOutputDevice
        self.player: vlc.MediaPlayer = None 

    def setNode(self, node):
        self.node=node

    def setVolume(self, volume:int)->bool:
        if volume < 0 or volume > 100:
            return
        if self.player == None:
            return
        rc = self.player.audio_set_volume(volume)
        if rc == 0:
            return True
        return False

    def getVolume(self)->int:
        if self.player == None:
            return 0
        try:
            return self.player.audio_get_volume()
        except Exception as ex:
            LOGGER.error(str(ex))
            return 0

    def playVLC(self):
        if self.node != None:
            self.node.updateState(1, self.index)
        
        if self.player != None:
            # Attach the event manager to the media player
            event_manager = self.player.event_manager()
            # Register the event and callback
            event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, play_stopped, None)
            self.player.play()
        
    def stopped(self):
        if self.node != None:
            self.node.updateState(0, self.index)

#        if self.player != None:
#            self.player.release()

        self.player=None

    def stop(self):
        if self.player != None:
            self.player.stop()
        self.stopped()

    def play(self, index, path:str) -> bool:
        while self.isPlaying():
            time.sleep(0.5) 
        self.index = index
        self.player = vlc_instance.media_player_new()
        self.player.audio_output_device_set(None, self.outputDevice)
        # Load the stream
        media = vlc_instance.media_new(path)
        # Set the media to the player
        self.player.set_media(media)
        if self.node != None:
            vol = self.getVolume()
            self.node.updateVolume(vol)

        # Start audio player thread
        ap_thread = threading.Thread(target = audio_player_thread)
        ap_thread.daemon = False
        ap_thread.start()

    def query(self, node):
        if self.isPlaying():
            node.updateState(1, self.index)
        else:
            node.updateState(0, 0)

    def isPlaying(self)->bool:
        if self.player == None:
            return False
        return True

    def setOutputDevice(self, index:int)->bool:
        if index == 0:
            self.outputDevice=SPEAKER_OUT
            return True
        elif index == 1:
            self.outputDevice=BLUETOOTH_OUT
            return True
        
        LOGGER.error(f"Invalid output device {index}")
        return False


udAudioPlayer:AudioPlayer=AudioPlayer()
nlsGen = NLSGenerator()

class AudioPlayerNode(udi_interface.Node):
    global udAudioPlayer

    id = 'mpgPlayer'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV0', 'value': 0, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 25},
            {'driver': 'GV2', 'value': 0, 'uom': 25},
            {'driver': 'GV3', 'value': 0, 'uom': 51}
            ]

    def __init__(self, polyglot, primary, address, name):
        super(AudioPlayerNode, self).__init__(polyglot, primary, address, name)
        udAudioPlayer.setNode(self)

    def updateState(self, state, index):
        if state == 1:
            self.setDriver('ST', 1, uom=25, force=True)
            self.setDriver('GV0', index, uom=25, force=True)
        else:
            self.setDriver('ST', 0, uom=25, force=True)
            self.setDriver('GV0', 0, uom=25, force=True)

    def updateOutput(self, index):
        if index < 0 or index > 1:
            return
        self.setDriver('GV2', index, uom=25, force=True)

    def updateVolume(self, volume:int):
        if volume < 0 or volume > 100:
            return
        self.setDriver('GV3', volume, uom=51, force=True)

    def processVolume(self, volume:int):
        if volume < 0 or volume > 100:
            return
        if udAudioPlayer.setVolume(volume) == True:
            self.updateVolume(volume)

    def processBT(self, index:int):
        print(index)


    def processOutput(self, index:int):
        if udAudioPlayer.setOutputDevice(index):
            self.updateOutput(index)


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
                    udAudioPlayer.stop()
                    udAudioPlayer.play(index, filename)
                except Exception as ex:
                    LOGGER.error(ex)
        
            elif cmd['cmd'] == 'STOP':
                udAudioPlayer.stop()
            
            elif cmd['cmd'] == 'BT' :
                sparam = str(cmd['query']).replace("'","\"")
                jparam=json.loads(sparam)
                index=int(jparam['BTSTATUS.uom25'])
                self.processBT(index)

            elif cmd['cmd'] == 'OUTPUT' :
                sparam = str(cmd['query']).replace("'","\"")
                jparam=json.loads(sparam)
                index=int(jparam['OUTPUT.uom25'])
                self.processOutput(index)

            elif cmd['cmd'] == 'VOLUME' :
                sparam = str(cmd['query']).replace("'","\"")
                jparam=json.loads(sparam)
                volume=int(jparam['VOLUME.uom51'])
                self.processVolume(volume)

            elif cmd['cmd'] == 'QUERY':
                udAudioPlayer.query(self)

    commands = {
            'PLAY': processCommand,
            'STOP': processCommand,
            'BT': processCommand,
            'OUTPUT': processCommand,
            'QUERY': processCommand,
            'VOLUME': processCommand
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
    global stations
    global nlsGen
    global defaultSoundPath

    if params == None:
        LOGGER.info("using default sounds and no stations ...")
        path=defaultSoundPath
    else:
        if 'path' in params:
            path=params['path']

            if path == None or path == '':
                LOGGER.info("using default sounds ...")
                path=defaultSoundPath

            if not os.path.isdir(path):
                polyglot.Notices['path'] = '{} is not a valid directory. Using defaults ... '.format(path)
                path=defaultSoundPath

                LOGGER.info('we are using {} as path'.format(path))
        if 'stations' in params:
            stations=params['stations']

    nlsGen.generate(path, stations)
    polyglot.updateProfile()
    addAudioNode("0")
    polyglot.Notices.clear()


def poll(polltype):

    if 'shortPoll' in polltype:
        LOGGER.info("short poll")
    elif 'longPoll' in polltype:
        LOGGER.info("long poll")


if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start('1.0.5')


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
        

