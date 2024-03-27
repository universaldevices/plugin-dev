#!/usr/bin/env python3
"""
    vlc utilities
"""

import vlc

p=vlc.MediaPlayer("")
mods = p.audio_output_device_enum()
if mods:
    devices=[]
    mod = mods
    while mod:
        mod = mod.contents
        devices.append([mod.device,mod.description])
        mod = mod.next
for d in devices:
    print(d)

def play_vlc(stream_url:str, dsp_device:str):

    # Create VLC instance
    vlc_instance = vlc.Instance('--no-xlib') 
    #vlc_instance = vlc.Instance('--no-xlib --aout=waveout --waveout-audio-device={}'.format(dsp_device))

    
    # Create VLC media player
    player = vlc_instance.media_player_new()

    player.audio_output_device_set(None, dsp_device)

    # Load the stream
    media = vlc_instance.media_new(stream_url)

    # Set the media to the player
    player.set_media(media)

    # Play the stream
    player.play()

    # Wait for the stream to finish (or use some other mechanism to keep the program running)
    input("Press any key to exit")

    # Stop the player
    player.stop()


#play_vlc("./sounds/bells.mp3", '/dev/dsp')
#jack
play_vlc("./sounds/bells.mp3", '/dev/dsp1')