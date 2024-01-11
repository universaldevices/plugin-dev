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
ST-mpgPlayer-GV0-NAME = Play List 

#Shared command names

CMD-STOP-NAME = Stop 
CMD-PLAY-NAME = Play 
CMDP-mpgNames-PLAYLIST-NAME = Playlist

PLAYSTATUS-0 = Idle
PLAYSTATUS-1 = Playing

MPGNAME-0 = None 
    
'''

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

    musicList:[str] = []
        
    def __init__(self) -> None:
        pass

        #Given a path, recreate the NLS document for the list of files

    def isMusicFile(self,entry) -> str:
        if not entry.is_file():
            return None
        music_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a']

        # Extract the file extension
        filename, file_extension = os.path.splitext(entry.name)

        # Check if the file extension is in the list of music extensions
        if file_extension.lower() in music_extensions:
            return entry.name
        return None


    def generate(self, path:str) -> bool :
        # There is only one nls, so read the nls template and write the new one
        if path == None:
            LOGGER.error('Need the path for where to find the mpg files ... ')
            return False
        en_us_txt = "profile/nls/en_us.txt"
        try:
            self.make_file_dir(en_us_txt)
            nls = open(en_us_txt,  "w")
            nls.write(DefaultNls.nls)
            self.musicList.append("None")
            index: int = 1
            with os.scandir(path) as entries:
                for entry in entries:
                    name = self.isMusicFile(entry)
                    if name != None:
                        nls.write("MPGNAME-{} = {}\n".format(index, name))
                        self.musicList.append(name)
                        index+=1
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
        if index < 0 or index >= len(self.musicList):
            LOGGER.error('Failed getting path requested index {}, array len {}'.format(index, len(self.musicList)))
            return None

        return parent_path + "/" + self.musicList[index] 

    def make_file_dir(self, file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True


if __name__ == "__main__":
    try:
        nlsGen = NLSGenerator()
        nlsGen.generate("/usr/home/admin/Chimes")

    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)