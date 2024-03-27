#!/usr/bin/env python3

"""
Polyglot v3 plugin
Copyright (C) 2024 Universal Devices

MIT License
"""

import sys
import traceback
import udi_interface 
import version
from udi_interface import Interface as Interface
from youtube_svc import YouTubeService
from youtube_svc import PLAYLISTS_DIRECTORY as PLAYLISTS_DIRECTORY
import audio_player 
from nls_gen import NLSGenerator

LOGGER = udi_interface.LOGGER

class YTMNode(audio_player.AudioPlayerNode):

    def __init__(self, polyglot, primary, address, name, ytService):
        super(YTMNode, self).__init__(polyglot, primary, address, name)
        self.ytService = ytService
        self.polyglot=polyglot

    def configDoneHandler(self):
        # We use this to discover devices, or ask to authenticate if user has not already done so
        self.polyglot.Notices.clear()

        # First check if user has authenticated
        try:
            self.ytService.getAccessToken()
            # If getAccessToken did raise an exception, then proceed with device discovery
        except ValueError as err:
            LOGGER.warning('Access token is not yet available. Please authenticate.')
            polyglot.Notices['auth'] = 'Please initiate authentication using the Authenticate Buttion'
            return False

        self.ytService.processPlaylists()
        nlsGen = NLSGenerator()
        nlsGen.generate(PLAYLISTS_DIRECTORY, None)
        polyglot.updateProfile()
        polyglot.Notices.clear()

        return True

    def oauthHandler(self, token):
        # When user just authorized, pass this to your service, which will pass it to the OAuth handler
        self.ytService.oauthHandler(token)

        # Then proceed with device discovery
        self.configDoneHandler()


    def addNodeDoneHandler(self, node):
        pass
        # We will automatically query the device after discovery
        #controller.addNodeDoneHandler(node)

    def stopHandler(self):
        # Set nodes offline
        for node in polyglot.nodes():
            if hasattr(node, 'setOffline'):
                node.setOffline()
        polyglot.stop()

    def parameterHandler(self, params):
        #nlsGen.generate(path, stations)
        #polyglot.updateProfile()
        #self.configDoneHandler()
        pass

if __name__ == "__main__":
    try:
        polyglot = Interface([])
        polyglot.start(version.ud_plugin_version)
        #polyglot.start({ 'version': '1.0.0', 'requestId': True })

        # Show the help in PG3 UI under the node's Configuration option
        polyglot.setCustomParamsDoc()

        # Update the profile files
        #polyglot.updateProfile()

        # Implements the API calls & Handles the oAuth authentication & token renewals
        ytService = YouTubeService(polyglot)

        # then you need to create the controller node
        ytmNode = YTMNode(polyglot, 'ytsvc', 'ytsvc', 'YouTube Player', ytService)
        polyglot.addNode(ytmNode)
        ytmNode.query()

        # subscribe to the events we want
        # polyglot.subscribe(polyglot.POLL, pollHandler)
        polyglot.subscribe(polyglot.STOP, ytmNode.stopHandler)
        polyglot.subscribe(polyglot.CUSTOMPARAMS, ytmNode.parameterHandler)
        polyglot.subscribe(polyglot.CUSTOMDATA, None) # ytService.customDataHandler)
        polyglot.subscribe(polyglot.OAUTH, ytmNode.oauthHandler)
        polyglot.subscribe(polyglot.CONFIGDONE, ytmNode.configDoneHandler)
        polyglot.subscribe(polyglot.ADDNODEDONE, ytmNode.addNodeDoneHandler)
        polyglot.subscribe(polyglot.CUSTOMNS, ytService.customNsHandler)

        # We can start receive events
        polyglot.ready()

        # Just sit and wait for events
        polyglot.runForever()

    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)

    except Exception as ex:
        LOGGER.error(f"Error starting plugin: {traceback.format_exc()}")
        polyglot.stop()