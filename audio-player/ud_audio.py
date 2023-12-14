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

class AudioPlayerParams:
    isPlaying :bool = False
    toStop :bool = False
    mediaPath: str = None


chunk = 4096
fn = '/usr/home/admin/Downloads/example.mp3' 

def audio_player_thread():
    pd = AudioSegment.from_file(AudioPlayerParams.mediaPath)
    p = pyaudio.PyAudio()

    stream = p.open(format =
        p.get_format_from_width(pd.sample_width),
        channels = pd.channels,
        rate = pd.frame_rate,
        output = True)
    i = 0
    data = pd[:chunk]._data
    while data and not AudioPlayerParams.toStop:
        stream.write(data)
        i += chunk

    stream.close()    
    p.terminate()
    AudioPlayerParams.isPlaying = False
    AudioPlayerParams.toStop = False

class UDAudioPlayer:

    def play(self, path:str) -> bool:
        while AudioPlayerParams.isPlaying:
            time.sleep(0.5) 
        AudioPlayerParams.isPlaying = True
        AudioPlayerParams.toStop = False
        AudioPlayerParams.mediaPath = path
        # Start serial port listener
        listen_thread = threading.Thread(target = audio_player_thread)
        listen_thread.daemon = False
        listen_thread.start()


    def stop(self):
        if not AudioPlayerParams.isPlaying:
            return
        AudioPlayerParams.toStop = True

ap = UDAudioPlayer()

if __name__ == "__main__":
    try:
        while True:
            ap.play(fn)
            time.sleep(5)
            ap.stop()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        




