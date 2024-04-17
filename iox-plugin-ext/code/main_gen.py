
import udi_interface

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom


if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start('1.0.4')
        PluginMain(polyglot)
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.info("exiting ..." )
        sys.exit(0)
