import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class OADR3VENNode(udi_interface.Node):
    id = 'oadr3ven'
    """This is a list of properties that were defined in the nodedef"""
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 103, 'name': 'Price'}, {
        'driver': 'GHG', 'value': 0, 'uom': 108, 'name': 'GHG'}]

    def __init__(self, polyglot, protocolHandler, controller=
        'oadr3controlle', address='oadr3ven', name='OADR3VEN'):
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

    def updatePrice(self, value, force: bool):
        return self.setDriver("ST", value, 103, force)

    def getPrice(self):
        return self.getDriver("ST")

    def queryPrice(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'ST')
            if val != None:
                self.updatePrice(val, True)
                return True
        return False

    def updateGHG(self, value, force: bool):
        return self.setDriver("GHG", value, 108, force)

    def getGHG(self):
        return self.getDriver("GHG")

    def queryGHG(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GHG')
            if val != None:
                self.updateGHG(val, True)
                return True
        return False

    def queryAll(self):
        self.queryPrice()
        self.queryGHG()
    """This is a list of commands that were defined in the nodedef"""
    commands = {}
