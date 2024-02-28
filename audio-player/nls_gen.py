import os
import udi_interface
from typing import List
import re
LOGGER = udi_interface.LOGGER


class DefaultNls() :

    nls = '''
#Controller
ND-mpgPlayer-NAME = MPG Player 
ND-mpgPlayer-ICON = Siren

ST-mpgPlayer-ST-NAME = Playing Status 
ST-mpgPlayer-GV0-NAME = Playing 
ST-mpgPlayer-GV1-NAME = Bluetooth 
ST-mpgPlayer-GV2-NAME = Output 
ST-mpgPlayer-GV3-NAME = Volume 

#Shared command names

CMD-STOP-NAME = Stop 
CMD-PLAY-NAME = Play 
CMD-BT-NAME = Bluetooth
CMD-OUTPUT-NAME = Output
CMD-VOLUME-NAME = Volume
CMDP-mpgNames-PLAYLIST-NAME = 
CMDP-BTSTATUS-NAME = 
CMDP-OUTPUT-NAME = 
CMDP-VOLUME-NAME = 

PLAYSTATUS-0 = Idle
PLAYSTATUS-1 = Playing

BTSTATUS-0 = Disabled
BTSTATUS-1 = Enabled
OUTPUT-0 = Speaker Jack
OUTPUT-1 = Bluetooth

'''

listFile='./m.list'

class DefaultEditor ():
    editors='''
    <editors>
    	<editor id="playStatus">
	    	<range uom="25" min="0" max="1" prec="0" nls="PLAYSTATUS" /> 
    	</editor>
        <editor id="mpgNames">
            <range uom="25" min="0" max="100" nls="MPGNAME"/>
        </editor>
    </editors>
    '''

class NLSGenerator :

    def __init__(self) -> None:
        self.musicList:[str]=[]
        self.stationsList:[str,str]=[]
        self.load()

        #Given a path, recreate the NLS document for the list of files

    def load(self)->bool():
        if not os.path.exists(listFile):
            self.save()
            return True
        try:
            with open(listFile, 'r') as file:
                self.musicList = [line.strip() for line in file.readlines()]
            return True
        except Exception as ex:
            LOGGER.error("failed loading the list file {}".format (ex))
            return False

    def save(self)->bool():
        try:
            if len(self.musicList) == 0 :
                self.musicList.append("None")
            
            with open(listFile, 'w') as file:
            # Write each string to a new line in the file
                for music in self.musicList:
                    file.write(music + '\n')
        except Exception as ex:
            LOGGER.error("failed saving the dev map file {}".format (ex))
            return False

    def isMusicFileName(self,name) -> str:
        if name == None:
            return None
        music_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a']

        filename, file_extension = os.path.splitext(name)

        # Check if the file extension is in the list of music extensions
        if file_extension.lower() in music_extensions:
            return name
        return None

    def isMusicFile(self,entry) -> str:
        if not entry.is_file():
            return None
        return self.isMusicFileName(entry.name)

    #remove any songs that have been deleted from our list since the last runtime
    def removeDeleted(self, dir_content:[])->bool:
        try:
            if dir_content == None:
                return False
        
            if len(self.musicList) == 0:
                return True
            if len(dir_content) == 0:
                self.musicList = []
                return True
            #now go through our list and see whether or not it still exists
            for index, music in enumerate(self.musicList):
                if music == "n/a" or music == "None":
                    continue
                if music in dir_content:
                    continue
                self.musicList[index]="n/a"
                LOGGER.debug(f"removing {music}")
            return True
        except Exception as ex:
            LOGGER.error(f"{ex}")
            return False

    #add any songs that may have been added to the directory since the last runtime
    def addNew(self, dir_content:[])->bool:
        if dir_content == None:
            return False
        if len(dir_content) == 0:
            self.musicList = []
            return True
        try:
            for index, music in enumerate(dir_content):
                if self.isMusicFileName(music) == None:
                    continue
                if music in self.musicList:
                    continue
                found:bool=False
                #otherwise add in the first available n/a or append to the last
                for i, m in enumerate(self.musicList):
                    if m == "n/a":
                        self.musicList[i]=music
                        LOGGER.debug(f"replacing {index} with {music} ...")
                        found=True
                        break
                if not found:
                    LOGGER.debug(f"adding {music} ...")
                    self.musicList.append(music)
            return True 
        except Exception as ex:
            LOGGER.error(f"{ex}")

    def getSortedDirContent(self, path:str)->[str]:
        if path == None:
            return None
        return os.listdir(path)
#        return sorted(os.listdir(path))

    def dump(self):
        if len (self.musicList) == 0:
            print("nothing to list ...")
            return

        for index, music in enumerate(self.musicList):
            print(f"{index}-{music}")


    def parseStation(self, station):
        if station == None:
            return None
        parts = station.replace('"', '').split('===')
        if len(parts) == 2:
            return {'name': parts[0], 'url': parts[1]}
        else:
            return None

    def parseStations(self, stations:str)->bool:
        if stations == None:
            return False
        stations_array = stations.split(',')
        for station in stations_array:
            parsed_station = self.parseStation(station)
            if parsed_station:
                self.stationsList.append(parsed_station)

    def generate(self, path:str, stations:str) -> bool :
        # There is only one nls, so read the nls template and write the new one
        if path == None:
            LOGGER.error('Need the path for where to find the mpg files ... ')
            return False
        self.parseStations(stations)
        dir_content = self.getSortedDirContent(path)
        self.removeDeleted(dir_content)
        self.addNew(dir_content)
        self.save()
        en_us_txt = "profile/nls/en_us.txt"
        try:
            self.make_file_dir(en_us_txt)
            nls = open(en_us_txt,  "w")
            nls.write(DefaultNls.nls)
            last:int=0
            for index, music in enumerate(self.musicList):
                if music == "n/a":
                    continue
                nls.write(f"MPGNAME-{index} = {music}\n")
                last=index
            last+=1
            for index, station in enumerate(self.stationsList):
                if station == None:
                    continue
                nls.write(f"MPGNAME-{last+index} = {station['name']}\n")
            nls.write("\n\n")
            nls.close()

## in case we want to update the editors with actual max number of songs
#            editor_xml = "profile/editor/editor.xml"
#            editor = open(editor_xml, "w")
#            editors = DefaultEditor.editors.replace("max=\"100\"", "max=\"{}\"".format(index))
#            editor.write(editors)
#            editor.close()
        except Exception as e:
            LOGGER.error('Failed to generate NLS: {}'.format(str(e)))

    def getFilePath(self, parent_path:str, index: int):
        if parent_path == None:
            LOGGER.error('Need parent path')
            return None
        if index < 0: 
            LOGGER.error('Failed getting path requested index {}, array len {}'.format(index, len(self.musicList)))
            return None
        musicFileEndIndex=len(self.musicList)
        if index < musicFileEndIndex: 
            return parent_path + "/" + self.musicList[index] 
        LOGGER.info(f"Playing live stream at {musicFileEndIndex}")
        stationIndex=index-musicFileEndIndex
        if stationIndex < 0 or stationIndex >= len(self.stationsList):
            LOGGER.error('Failed getting url for requested index {}, array len {}'.format(index, len(self.stationsList)))
            return None
        return self.stationsList[stationIndex]['url']
            


    def make_file_dir(self, file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True


if __name__ == "__main__":
    try:
        nlsGen = NLSGenerator()
        nlsGen.generate("/usr/home/admin/Chimes", None)
        nlsGen.dump()

    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)