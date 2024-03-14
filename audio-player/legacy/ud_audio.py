#!/usr/bin/env python3
"""
Audio management function for audio-player plugin
Copyright (C) 2023  Universal Devices
"""

import pyaudio
import sys
from pydub import AudioSegment
import threading
import time

class _AudioPlayerParams:
    isPlaying :bool = False
    toStop :bool = False
    mediaPath: str = None
    node = None
    index: int = 0


AudioPlayerParams:_AudioPlayerParams = _AudioPlayerParams()

chunk = 4096
#fn = 'sounds/schime.mp3'
fn = './output.mp3'
#0 = BT
#2 = Speaker
defaultOutputDevice=2


def audio_player_thread():
    if AudioPlayerParams.node != None:
        AudioPlayerParams.node.updateState(1, AudioPlayerParams.index)
    pd = AudioSegment.from_file(AudioPlayerParams.mediaPath)
    p = pyaudio.PyAudio()
    print(pd.frame_rate)

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
        # Start serial port listener
        listen_thread = threading.Thread(target = audio_player_thread)
        listen_thread.daemon = False
        listen_thread.start()

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

ap = UDAudioPlayer()

if __name__ == "__main__":
    try:
#        while True:
        ap.play(None, 0, fn)
#            time.sleep(5)
#            ap.stop(None)
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        




