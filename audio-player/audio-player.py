#!/usr/bin/env python3
"""
Polyglot v3 plugin for audio playback 
Copyright (C) 2023  Universal Devices
"""

import os
current_path = os.environ['PATH']
ffprog_path='/usr/local/bin'
os.environ['PATH'] = f'{ffprog_path}:{current_path}'
isAudioPlayerChild =  os.path.basename(__file__) != 'audio-player.py'

from nls_gen import NLSGenerator
import udi_interface
import sys
import time
import json
import threading
import paho.mqtt.client as mqtt
import ssl
import vlc
import pyaudio
from pydub import AudioSegment
import subprocess
import shutil
if not isAudioPlayerChild: 
    from ud_tts import UDTTS
import version
import secrets
import random

MUSIC_TEMP_DIR="tmp_sounds"

LOGGER = udi_interface.LOGGER
polyglot = None
path:str = None
defaultSoundPath='./sounds'
PAUDIO_SPEAKER_OUT=2
SPEAKER_OUT = '/dev/dsp1' 
PAUDIO_BLUETOOTH_OUT=0
BLUETOOTH_OUT = '/dev/dsp'
defaultOutputDevice=SPEAKER_OUT
stations:str = None
DATA_PATH="./data"

#create vlc instance
#vlc_instance = vlc.Instance('--no-xlib')
#vlc_instance = vlc.Instance('--no-xlib', '--demux=playlist', '--no-video')
#vlc_instance = vlc.Instance('--no-xlib', '--no-video')
vlc_instance = vlc.Instance('--no-xlib', '--no-video' )

def getPyAudioDevice(dev:str):
    if dev == SPEAKER_OUT:
        return PAUDIO_SPEAKER_OUT
    elif dev == BLUETOOTH_OUT:
        return PAUDIO_BLUETOOTH_OUT
    else:
        return getPyAudioDevice(defaultOutputDevice)

'''
if you want to log locally, uncomment
'''

#@vlc.CallbackDecorators.LogCb
#def log_callback(instance, level, ctx, fmt, args):
#    try:
#        module, _file, _line = vlc.libvlc_log_get_context(ctx)
#    except TypeError:
#        print("vlc.libvlc_log_get_context(ctx)")

#vlc_instance.log_set(log_callback,None)


class MediaList:

    def __init__(self):
        self.clear(False)

    def clear(self, shuffle:bool):
        self.elements = [] 
        self.current_index = -1
        self.used_indices = set()
        self.shuffle=shuffle

    def append(self,element:str):
        if str == None:
            return
        self.elements.append(element)

    def next(self):
        if self.shuffle:
            return self.random()
        if self.current_index < len(self.elements) - 1:
            self.current_index += 1
        else:
            self.current_index = 0
        self.used_indices.add(self.current_index)
        return self.elements[self.current_index]

    def previous(self):
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.elements) - 1
        self.used_indices.add(self.current_index)
        return self.elements[self.current_index]

    def random(self):
        available_indices = set(range(len(self.elements))) - self.used_indices
        if not available_indices:
            self.used_indices = set()
            available_indices = set(range(len(self.elements)))
        self.current_index = random.choice(list(available_indices))
        self.used_indices.add(self.current_index)
        return self.elements[self.current_index]

def play_stopped(event, nums):
    global udAudioPlayer
    udAudioPlayer.stopped()

def audio_player_thread():
    global udAudioPlayer
    if udAudioPlayer.isTTS:
        udAudioPlayer.playTTS()
    else:
        udAudioPlayer.playVLC()

def audio_list_play_next():
    global udAudioPlayer
    udAudioPlayer.next()

class AudioPlayer:
    def __init__(self): 
        self.node = None
        self.index: int = 0
        self.outputDevice: str = defaultOutputDevice
        self.player: vlc.MediaPlayer = None 
        self.isTTS: bool = False
        self.toStop: bool = False #used for TTS
        self.path: str = None
        self.volume = 100
        self.shuffle:bool = False
        self.mediaList = MediaList()
        self.isListPlayer = False
        self.isAutoNext = False

    def setNode(self, node):
        self.node=node

    def isPlaylistPlayer(self)->bool:
        return self.isListPlayer
        

    def setVolume(self, volume:int)->bool:
        if volume < 0 or volume > 100:
            return
        self.volume = volume
        if self.player == None:
            return True
        rc = self.player.audio_set_volume(volume)
        if rc == 0:
            return True
        return False

    def getVolume(self)->int:
        if self.player == None:
            return self.volume 
        try:
            return self.player.audio_get_volume()
        except Exception as ex:
            LOGGER.error(str(ex))
            return 0

    def getVolumeInDB(self):
        return max(-60, -60 + (self.volume / 100) * 60)

    def getYouTubeAudioURL(self, videoUrl):
        if videoUrl == None:
            return None
        try:
            from pytubefix import YouTube
            # Create a YouTube object
            #yt = YouTube(videoUrl, client='WEB')
            yt = YouTube(videoUrl)

            # Get the audio stream with the highest bitrate
            audio_stream = yt.streams.get_audio_only()
            if audio_stream == None:
                return None
            # Return the URL of the audio stream
            return audio_stream.url
        except Exception as ex:
            LOGGER.error(str(ex))

    def __setMedia(self, url:str):
        if url == None:
            return False
        if self.player == None:
            return False
        murl=None
        if url.startswith("https://www.youtube.com"):
            murl=self.getYouTubeAudioURL(url)
        else:
            murl=url
        if murl == None:
            return False
        media = vlc_instance.media_new(murl)
            # Set the media to the player
        self.player.set_media(media)
        return True
        

    def playVLC(self):
        global vlc_instance
        try:
            if not self.isAutoNext:
                self.isListPlayer=self.path.endswith('.m3u')
                if self.isListPlayer:
                    self.mediaList.clear(self.shuffle)
                    with open(self.path, 'r') as file:
                        for line in file:
                            self.mediaList.append(line.strip())
                    self.isAutoNext=True
                
            self.player = vlc_instance.media_player_new()
                # Load the stream
            
            self.player.audio_output_device_set(None, self.outputDevice)

            # Attach the event manager to the media player
            event_manager = self.player.event_manager()
            # Register the event and callback
            event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, play_stopped, None)
            event_manager.event_attach(vlc.EventType.MediaPlayerEncounteredError, play_stopped, None)
            if self.node != None:
                self.node.updateState(1, self.index)
            if self.node != None:
                vol = self.getVolume()
                if vol != self.volume:
                    vol=self.volume
                    self.setVolume(vol)
                self.node.updateVolume(vol)
            rc = False
            if self.isListPlayer:
                path = self.mediaList.next()
                rc = self.__setMedia(path)
            else:
                rc = self.__setMedia(self.path)

            if not rc:
                self.isAutoNext=False
                self.isListPlayer=False
                self.stop()
            else: 
                self.player.play()

        except Exception as ex:
            LOGGER.error(str(ex))
            self.stop()

    def playTTS(self):
        try:
            chunk_size=4096
            pd = AudioSegment.from_file(self.path)
            p = pyaudio.PyAudio()

            stream = p.open(output_device_index=getPyAudioDevice(self.outputDevice), format =
            p.get_format_from_width(pd.sample_width),
            channels = pd.channels,
            rate = pd.frame_rate, 
            output = True)
            if self.node != None:
                self.node.updateState(1, self.index)

            for i in range(0, len(pd), chunk_size):
                if self.toStop:
                    break
                chunk = pd[i:i + chunk_size] + self.getVolumeInDB()
                stream.write(chunk.raw_data)

            #i = 0
            #chunk = pd[:chunk_size] + self.getVolumeInDB()
            #while chunk and not self.toStop:
            #    stream.write(chunk.raw_data)
            #    i += chunk_size
            #    chunk = pd[i:i + chunk_size] + self.getVolumeInDB()

            stream.stop_stream()
            stream.close()
            p.terminate()
            pd=None
            self.stopped()
        except Exception as ex:
            LOGGER.error(str(ex))
            self.stopped()

    def startNextPlayDaemon(self):
   #     if self.nextPlayDaemon != None:
   #         self.nextPlayDaemon.join()
        pass

    def stopped(self):
        if self.node != None:
            self.node.updateState(0, self.index)
        self.toStop=False
        if self.isPlaylistPlayer():
            nextPlayDaemon = threading.Thread(target = audio_list_play_next)
            nextPlayDaemon.daemon = False
            nextPlayDaemon.start()
           # self.startNextPlayDaemon()

        else:
            self.player=None

    def stop(self):
        if self.player != None:
            self.player.stop()
            self.player.release()
            self.player=None
            self.stopped()
        else:
            self.toStop=True

    def get_audio_info(self, path:str):
        # Get audio metadata
        ffprobe_cmd = ["ffprobe", "-v", "error", "-show_entries", "stream=channels,bit_rate", "-of", "json", path]
        process = subprocess.Popen(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = process.communicate()
    
        # Parse JSON output
        metadata = json.loads(output)
    
        # Initialize variables to store bitrate and mono status
        bitrate = 0
        is_mono = False
        frame_rate = 0

        # Extract bitrate and mono status from metadata
        if 'streams' in metadata:
            for stream in metadata['streams']:
                if 'bit_rate' in stream:
                    bitrate = int(stream['bit_rate'])
                if 'channels' in stream and stream['channels'] == 1:
                    is_mono = True
                if 'r_frame_rate' in stream:
                # r_frame_rate is a string in the form "numerator/denominator"
                # We can convert it to a float by dividing numerator by denominator
                    numerator, denominator = map(float, stream['r_frame_rate'].split('/'))
                    frame_rate = numerator / denominator
        if frame_rate == 0:
            pd = AudioSegment.from_file(path)
            frame_rate = pd.frame_rate
            pd = None
    
        # Return bitrate and mono status as a tuple
        return bitrate, is_mono, frame_rate

    def make48K(self):
        return UDTTS.make48K(self.path, MUSIC_TEMP_DIR)

       # filename=os.path.basename(self.path)
       # path48=MUSIC_TEMP_DIR+"/iox48."+filename
       # if not os.path.exists(path48):
       # #we have a tts file that we need to convert
       #     pd = AudioSegment.from_file(self.path)
       #     pd=pd.set_frame_rate(48000)
       #     pd.export(path48, format="mp3")
       #     pd = None
       # return path48 

    def play(self, index, path:str) -> bool:
        if self.node == None:
            return False
        while self.node.isPlaying():
            time.sleep(0.5) 
        self.toStop=False
        self.index = index
        self.path = path
        if '_t' in self.path:
            self.isTTS = True
            self.path = self.make48K()
        else:
            self.isTTS = False


        # Start audio player thread
        ap_thread = threading.Thread(target = audio_player_thread)
        ap_thread.daemon = False
        ap_thread.start()
        return True
    
    def play__heuristics(self, index, path:str) -> bool:
        if self.node == None:
            return False
        while self.node.isPlaying():
            time.sleep(0.5) 
        self.toStop=False
        self.index = index
        self.path = path
        if '_nvlc_' in self.path:
            self.isTTS = True
            self.make48K(path48)
            self.path = path48
        else:
            filename=os.path.basename(self.path)
            path48=MUSIC_TEMP_DIR+"/iox48."+filename
            path24=MUSIC_TEMP_DIR+"/iox24."+filename
            #if neither exists, figure out what we have
            
            if not (os.path.exists(path48) or os.path.exists(path24)):
                try:
                    bit_rate, is_mono, frame_rate = self.get_audio_info(path)
                    if (frame_rate != None and frame_rate > 24000) and (bit_rate != None and bit_rate > 32000): 
                    #and (is_mono != None and not is_mono):
                        self.TTS=False
                        with open(path48,'w'):
                            pass
                    else:
                        self.TTS=True
                        with open(path24,'w'):
                            pass
                except Exception as ex:
                    LOGGER.log(str(ex))
                    self.TTS=False

            #now, if path24 exists, 
            if os.path.exists(path24):
                self.isTTS=True 
                self.make48K(path48)
                self.path=path48
            else:
                self.isTTS = False


        # Start audio player thread
        ap_thread = threading.Thread(target = audio_player_thread)
        ap_thread.daemon = False
        ap_thread.start()
        return True

    def resume(self)->bool:
        self.play(self.index, self.path)

    def next(self)->bool:
        if not self.isPlaylistPlayer():
            return False
        if self.player == None:
            return False
        self.player.pause()
        self.__setMedia(self.mediaList.next())
        if self.node != None:
            self.node.updateState(1, self.index)
        self.player.play() 
        return True

    def previous(self)->bool:
        if not self.isPlaylistPlayer():
            return False
        if self.player == None:
            return False
        self.player.pause()
        self.__setMedia(self.mediaList.previous())
        if self.node != None:
            self.node.updateState(1, self.index)
        self.player.play() 
        return True

    def setShuffle(self, index:int)->bool:
        if self.node == None:
            return False

        if index == 0: 
            self.shuffle=False
        else:
            self.shuffle=True
        return True

    def query(self, node)->bool:
        if node.isPlaying():
            node.updateState(1, self.index)
        else:
            node.updateState(0, 0)
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

def find_files_with_extension(directory:str, extension:str):
    if directory == None or extension == None:
        return None
    file_paths = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                # Construct the full path to the file and append it to the list
                file_path = os.path.join(root, file)
                file_paths.append(file_path)

    return file_paths

def find_files_in_directory(directory:str):
    if directory == None :
        return None
    file_paths = []

    for root, _, files in os.walk(directory):
        for file in files:
                # Construct the full path to the file and append it to the list
            file_path = os.path.join(root, file)
            file_paths.append(file_path)

    return file_paths
 
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
            {'driver': 'GV3', 'value': 0, 'uom': 51},
            {'driver': 'GV4', 'value': 0, 'uom': 25}
            ]

    def __init__(self, polyglot, primary, address, name):
        super(AudioPlayerNode, self).__init__(polyglot, primary, address, name)
        udAudioPlayer.setNode(self)
        self.updateState(0,0)
        self.updateOutput(0)
        self.updateBTStatus(False)
        self._mqttc = None
        try:
            mqttThread = threading.Thread(target=self._startMqtt, name='SysConfigMqtt')
            mqttThread.daemon = False
            mqttThread.start()
            config = self.poly.getConfig()
            if config == None:
                return
        except Exception as ex:
            LOGGER.error(str(ex))

    def getNLSGen(self)->NLSGenerator:
        global nlsGen
        return nlsGen

    def _startMqtt(self)->bool:
        cafile= '/usr/local/etc/ssl/certs/ud.ca.cert'
        certs = find_files_with_extension('./','.cert')
        keys = find_files_with_extension('./','.key')
        if len(certs) == 0 or len(keys) == 0:
            LOGGER.warning("no cert/key for mqtt connectivity")
            return False

        LOGGER.info('Using SSL cert: {} key: {} ca: {}'.format(certs[0], keys[0], cafile))
        try:
            rand=secrets.token_hex(6) 
            mqtt_id=f'{self.id}_{rand}'
            self._mqttc=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, mqtt_id, True)
            self.sslContext = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cafile)
            self.sslContext.load_cert_chain(certs[0], keys[0])
            self._mqttc.tls_set_context(self.sslContext)
            self._mqttc.tls_insecure_set(True)
            self._mqttc.on_connect=self.on_connect
            self._mqttc.on_subscribe = self.on_subscribe
            self._mqttc.on_disconnect = self.on_disconnect
            self._mqttc.on_publish = self.on_publish
#            self._mqttc.on_log = self.on_log
            self._mqttc.on_message = self.on_message
        
        except Exception as ex:
            LOGGER.error(str(ex))
        while True: 
            try:
                self._mqttc.connect_async('{}'.format(self.poly._server), int(self.poly._port), 10)
                self._mqttc.loop_forever()
            except ssl.SSLError as e:
                LOGGER.error("MQTT Connection SSLError: {}, Will retry in a few seconds.".format(e), exc_info=True)
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                LOGGER.exception("MQTT Connection error: {}".format(
                    message), exc_info=True)
                time.sleep(3)
        return True


    def on_connect(self, mqttc, userdata, flags, rc, properties):
        if rc == 0:
            self._mqttc.subscribe('sconfig/bluetooth/#', 0)
            self._mqttc.publish('config/bluetooth')
            self._mqttc.publish('config/bluetooth/list')
        else:
            LOGGER.error(f"MQTT Connection failed: {rc}")

    def on_disconnect(self, mqttc, userdata, disconnect_flags, reason_code, properties):
        LOGGER.info(f"MQTT disconnected: {reason_code}")

    def on_publish(self, mqttc, userdata, mid, reason_code, properties):
        pass

    def on_subscribe(self, mqttc, userdata, mid, reason_codes, properties):
        pass

    def on_message(self, mqttc, userdata, msg):
        if msg == None or msg.topic == None:
            return
        if msg.topic == "sconfig/bluetooth/enabled":
            self.updateBTStatus(True)
        elif msg.topic == "sconfig/bluetooth/disabled":
            self.updateBTStatus(False)
        elif msg.topic == "sconfig/bluetooth/list":
            self.updateBTList(msg.payload)
        elif msg.topic == "sconfig/bluetooth/unpair":
            udAudioPlayer.stop()

    def on_log(self, mqttc, userdata, level, string):
        pass

    def isPlaying(self):
        try:
            return self.getDriver('ST') == 1
        except Exception as ex:
            return False

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

    def updateBTStatus(self, enabled:bool):
        if enabled:
            self.setDriver('GV1', 1, uom=25, force=True)
        else:
            self.setDriver('GV1', 0, uom=25, force=True)

    def updateBTList(self, payload:str):
        pass

    def processBT(self, index:int):
        if index == 0:
            self._mqttc.publish('config/bluetooth/disable')
        else:
            self._mqttc.publish('config/bluetooth/enable')
    
    def processOutput(self, index:int):
        if index == 0:
            if udAudioPlayer.setOutputDevice(index):
                self.updateOutput(index)
                if self.isPlaying():
                    udAudioPlayer.stop()
                    udAudioPlayer.resume()
                return True
            else:
                return False

        btStatus=self.getDriver('GV1') 
        if btStatus == 1 or btStatus == '1':
            if udAudioPlayer.setOutputDevice(index):
                self.updateOutput(index)
                if self.isPlaying():
                    udAudioPlayer.stop()
                    udAudioPlayer.resume()
                return True
        return False

    def query(self):
        udAudioPlayer.query(self)


    def processCommand(self, cmd)->bool:
        global path
        global polyglot
        global stations
        LOGGER.info('Got command: {}'.format(cmd))
        if 'cmd' in cmd:
            if cmd['cmd'] == 'PLAY':
                try:
                    index=int(cmd.get('value'))
                    if index == 0:
                        return False
                    filename=nlsGen.getFilePath(path, index)
                    if filename == None:
                        return False
                    LOGGER.info('Playing #{}:{}'.format(index, filename))
                    udAudioPlayer.isAutoNext=False
                    udAudioPlayer.isListPlayer=False
                    udAudioPlayer.stop()
                    return udAudioPlayer.play(index, filename)
                except Exception as ex:
                    LOGGER.error(ex)

            elif cmd['cmd'] == 'REMOVE':
                try:
                    index=int(cmd.get('value'))
                    if index == 0:
                        return False
                    filename=nlsGen.getFilePath(path, index)
                    if filename == None or filename.endswith("n/a"):
                        return False
                    LOGGER.info('Removing #{}:{}'.format(index, filename))
                    if nlsGen.removeFile(filename):
                        nlsGen.generate(path, stations)
                        polyglot.updateProfile()
                    return True

                except Exception as ex:
                    LOGGER.error(ex)
        
            elif cmd['cmd'] == 'STOP':
                udAudioPlayer.isAutoNext=False
                udAudioPlayer.isListPlayer=False
                udAudioPlayer.stop()
            
            elif cmd['cmd'] == 'BT' :
                index=int(cmd.get('value'))
                self.processBT(index)

            elif cmd['cmd'] == 'OUTPUT' :
                index=int(cmd.get('value'))
                self.processOutput(index)

            elif cmd['cmd'] == 'VOLUME' :
                volume=int(cmd.get('value'))
                self.processVolume(volume)

            elif cmd['cmd'] == 'QUERY':
                self.query()

            elif cmd['cmd'] == 'PREVIOUS':
                udAudioPlayer.previous()
            elif cmd['cmd'] == 'NEXT':
                udAudioPlayer.next()
            elif cmd['cmd'] == 'SHUFFLE':
                index=int(cmd.get('value'))
                if udAudioPlayer.setShuffle(index):
                    self.setDriver('GV4', index, uom=25, force=True)

    commands = {
            'PLAY': processCommand,
            'STOP': processCommand,
            'BT': processCommand,
            'OUTPUT': processCommand,
            'QUERY': processCommand,
            'VOLUME': processCommand,
            'PREVIOUS': processCommand,
            'NEXT': processCommand,
            'SHUFFLE': processCommand,
            'REMOVE': processCommand
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

def get_tts_elements(dictionary, pattern="tts_*"):
    regex = re.compile(pattern)
    matched_elements = {}
    for key, value in dictionary.items():
        if regex.match(key):
            matched_elements[key] = value
    return matched_elements

'''
Read the user entered custom parameters. This should only be the serial
port.
'''
def parameterHandler(params):
    global path
    global polyglot
    global stations
    global nlsGen
    global defaultSoundPath
    global MUSIC_TEMP_DIR

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
            if "a , separated " in stations:
                LOGGER.error("Invalid stations list. It has to be in the form name===url,name===url, ....")
                polyglot.Notices['stations'] = 'Stations list is of the form name===url,name===url, ....'
                stations=None

        try:         
            MTemp=path+"/"+MUSIC_TEMP_DIR
            if os.path.exists(MTemp):
                #remove it
                shutil.rmtree(MTemp)
            os.makedirs(MTemp)
            MUSIC_TEMP_DIR=MTemp
        except Exception as ex:
                LOGGER.error(ex)

    tts=UDTTS(path)
    if tts.parse_params(params) != None:
        tts.generate_mp3_files()

    nlsGen.generate(path, stations)
    polyglot.updateProfile()
    addAudioNode("0")
    polyglot.Notices.clear()


def poll(polltype):

    if 'shortPoll' in polltype:
        LOGGER.info("short poll")
    elif 'longPoll' in polltype:
        LOGGER.info("long poll")

def config(param):
    global path
    global stations
    global nlsGen
    global polyglot
    if not os.path.exists(DATA_PATH):
        return
    if path == None:
        LOGGER.warn("no path for the sounds directory ... ")
        return
    try:
        LOGGER.info(f"processing files in {DATA_PATH}")
        new_files=find_files_in_directory(DATA_PATH)

        if new_files == None or len(new_files) == 0:
            LOGGER.warn(f"no files in {DATA_PATH}")
            shutil.rmtree(DATA_PATH)
            return
    
        LOGGER.debug(f"copying files from {DATA_PATH} to {path}") 
        for new_file in new_files:
            LOGGER.debug(f"copying {new_file} to {path}")
            shutil.copy(new_file, path) 
        nlsGen.generate(path, None)
        polyglot.updateProfile()
        shutil.rmtree(DATA_PATH)
    except Exception as ex:
        LOGGER.error(str(ex))
    

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start(version.ud_plugin_version)


        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.POLL, poll)
        polyglot.subscribe(polyglot.CONFIG, config)

        # Start running
        polyglot.ready()
        polyglot.setCustomParamsDoc()

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
    except Exception as ex:
        LOGGER.error(ex)
        

