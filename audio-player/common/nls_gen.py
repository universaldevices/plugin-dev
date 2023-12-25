import os
import udi_interface
from typing import List
import re
from default_nls import DefaultNls
LOGGER = udi_interface.LOGGER

class NLSGenerator :
        
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
            index: int = 0
            with os.scandir(path) as entries:
                for entry in entries:
                    name = self.isMusicFile(entry)
                    if name != None:
                        nls.write("MPGNAME-{} = {}".format(index, name))
                        index+=1
            nls.write("\n\n")

            nls.close()
        except Exception as e:
            LOGGER.error('Failed to generate NLS: {}'.format(str(e)))


    def make_file_dir(self, file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True


if __name__ == "__main.test__":
    try:
        nlsGen = NLSGenerator()
        nlsGen.generate("/usr/home/admin/workspace/plugin-dev/audio-player")

    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)