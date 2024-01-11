#!/usr/bin/env python3
"""
Polyglot v3 node server communicating with Casambi USB dongle 
Copyright (C) 2023  Universal Devices
"""

USE THIS METHOD FOR LARGE FILES/BT?

must install the following
pip - sounddevice
pip - soundfile
.... must install py39-numpy package (HUGE)

import os
current_path = os.environ['PATH']
ffprog_path='/usr/local/bin'
os.environ['PATH'] = f'{ffprog_path}:{current_path}'

import threading
import sounddevice as sd
import soundfile as sf
import numpy


devices:[]=sd.query_devices()
print(devices)
device_index:str='/dev/dsp1'

filename ="./sounds/chime.mp3"
event = threading.Event()

try:
    data, fs = sf.read(filename, always_2d=True)

    current_frame = 0

    def callback(outdata, frames, time, status):
        global current_frame
        if status:
            print(status)
        chunksize = min(len(data) - current_frame, frames)
        outdata[:chunksize] = data[current_frame:current_frame + chunksize]
        if chunksize < frames:
            outdata[chunksize:] = 0
            raise sd.CallbackStop()
        current_frame += chunksize

    stream = sd.OutputStream(
        samplerate=fs, device=device_index, channels=data.shape[1],
        callback=callback, finished_callback=event.set)
    with stream:
        event.wait()  # Wait until playback is finished
except KeyboardInterrupt:
    print('\nInterrupted by user')
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))