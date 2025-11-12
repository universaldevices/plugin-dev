import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class ShellyGenericSwitchNode(udi_interface.Node):
    id = 'sswitch'
    """This is a list of properties that were defined in the nodedef"""
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 51, 'name': 'Status'}]

    def __init__(self, polyglot, protocolHandler, controller=
        'shellycontroll', address='sswitch', name='Shelly Generic Switch'):
        super().__init__(polyglot, controller, address, name)
        self.protocolHandler = protocolHandler

    def setProtocolHandler(self, protocolHandler):
        self.protocolHandler = protocolHandler

    def getUOM(self, driver: str):
        try:
            for driver_def in self.drivers:
                if driver_def['driver'] == driver:
                    return driver_def['uom']
            return None
        except Exception as ex:
            return None

    def updateStatus(self, value, force: bool):
        return self.setDriver("ST", value, 51, force)

    def getStatus(self):
        return self.getDriver("ST")

    def queryStatus(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'ST')
            if val != None:
                self.updateStatus(val, True)
                return True
        return False

    def queryAll(self):
        self.queryStatus()

    def On(self, command):
        try:
            if self.protocolHandler:
                return self.protocolHandler.processCommand(self, 'On')
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def Off(self, command):
        try:
            if self.protocolHandler:
                return self.protocolHandler.processCommand(self, 'Off')
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False
    """This is a list of commands that were defined in the nodedef"""
    commands = {'on': On, 'off': Off}
