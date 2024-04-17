import udi_interface, os, sys, json, time
import version
from micNode import micNode
from hello_worldNode import hello_worldNode
LOGGER = udi_interface.LOGGER
if __name__ == '__main__':
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start(version.ud_plugin_version)
        controller = hello_worldNode(polyglot)
        polyglot.addNode(controller)
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.info('exiting ...')
        sys(0)
