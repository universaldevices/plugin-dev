
#!/usr/bin/env python3
# Main routine for IoX Plugin. 
# Do NOT Modify 

import udi_interface, os, sys, json, time,shutil
import version
from ioxplugin import Plugin

PLUGIN_FILE_NAME = 'oadr3.iox_plugin.json'
PLUGIN_FILE_NAME_DEST = f"{os.getcwd()}/{PLUGIN_FILE_NAME}"
DATA_PATH = f"{os.getcwd()}/data"
PLUGIN_FILE_NAME_SRC = f"{DATA_PATH}/{PLUGIN_FILE_NAME}"

LOGGER = udi_interface.LOGGER

def configurePluginFile():
   if not os.path.exists(PLUGIN_FILE_NAME):
        if not os.path.exists(PLUGIN_FILE_NAME_SRC):
            return False
        else:
            try:
                shutil.copy(PLUGIN_FILE_NAME_SRC, PLUGIN_FILE_NAME_DEST)
            except Exception as ex:
                LOGGER.error(str(ex))
                return False
   return True


if __name__ == '__main__':
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start(version.ud_plugin_version)
        plugin = None
        if not configurePluginFile(): 
            polyglot.Notices['config']=f"{PLUGIN_FILE_NAME} does not exist. Uplaod it using Configuration tab Zip File Upload then Restart ..."
        else:
            polyglot.Notices.clear()
            plugin = Plugin(PLUGIN_FILE_NAME)
            plugin.toIoX()
            plugin.generateCode(path='./')
            from Oadr3ControllerNode import Oadr3ControllerNode
            controller = Oadr3ControllerNode(polyglot, plugin)
            polyglot.ready()
            polyglot.runForever()
    
    except (KeyboardInterrupt, SystemExit):
        LOGGER.info('exiting ...')
        sys(0)
