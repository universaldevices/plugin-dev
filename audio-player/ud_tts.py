
#!/usr/bin/env python3
"""
Polyglot v3 plugin for audio playback  - TTS handling
Copyright (C) 2024  Universal Devices
"""
import re
from gtts import gTTS
from udi_interface import LOGGER
import os
import pyaudio
from pydub import AudioSegment
from googletrans import Translator

#for offline text processing use pyttsx3
#py39-pyttsx3-2.90.12           Offline Text To Speech (TTS) converter for Python

class UDTTSDirective:

    def __init__(self, spoken:str):
        try:
            self.lang:str=None
            self.to_lang:str=None
            self.name:str=None
            self.spoken:str=spoken
            
        except Exception as ex:
            LOGGER.error(str(ex))

    def parse_name (self, name:str)->bool:
        try:
            pattern = r'^tts_(\w{2})_(\w{2})_(.*)$'  # Define the regular expression pattern
            match = re.match(pattern, name)  # Try to match the pattern with the name
            if not match:
                LOGGER.error("the format of the name should be tts_lang_name. eg. tts_en_hello world")
                return False

            parts = match.groups()  # Return the extracted parts as a tuple
            self.lang=parts[0]
            self.to_lang=parts[1]
            self.name=parts[2]
            return True

        except Exception as ex:
            LOGGER.error(str(ex))
            return False

class UDTTS:

    def __init__(self, path):
        self.path=path
        self.tts_directives=[UDTTSDirective]

    def parse_params(self, params, pattern=r'^tts_(.*)$'):
        if params == None:
            return None
        try:
            regex = re.compile(pattern)
            self.tts_directives=[]
            for key, spoken in params.items():
                if regex.match(key):
                    directive=UDTTSDirective(spoken)
                    if directive.parse_name(key):
                        self.tts_directives.append(directive)
            return self.tts_directives
        except Exception as ex:
            LOGGER.error(str(ex))
            return None

    def generate_mp3_files(self):
        try:
            for directive in self.tts_directives: 
                LOGGER.debug(f'generating tts mp3 for {directive.name}')
                directive_path=self.path+'/'+directive.name+'_t.mp3'
                spoken=directive.spoken
                clang=directive.lang
                if directive.lang != directive.to_lang:
                    translator = Translator()
                    spoken = translator.translate(directive.spoken, src=directive.lang, dest=directive.to_lang).text
                    clang=directive.to_lang
                
                tts = gTTS(spoken, lang=clang)
                tts.save(directive_path)

        except Exception as ex:
            LOGGER.error(str(ex))

    @staticmethod
    def make48K(path:str, temp_dir:str)-> bool:
        if path == None or temp_dir == None :
            return None

        filename=os.path.basename(path)
        path48=temp_dir+"/iox48."+filename
        if not os.path.exists(path48):
        #we have a tts file that we need to convert
            pd = AudioSegment.from_file(path)
            pd=pd.set_frame_rate(48000)
            pd.export(path48, format="mp3")
            pd = None
        return path48 

