import udi_interface, os, sys, json, time
import version
from micNode import micNode
from helloworldNode import helloworldNode
LOGGER = udi_interface.LOGGER
if __name__ == '__main__':
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start(version.ud_plugin_version)
        controller = helloworldNode(polyglot)
        polyglot.addNode(controller)
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.info('exiting ...')
        sys(0)
