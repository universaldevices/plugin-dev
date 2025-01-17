import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class OADR3VENNode(udi_interface.Node):
    id = 'oadr3ven'
    """This is a list of properties that were defined in the nodedef"""
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 103, 'name': 'Price'}, {
        'driver': 'GHG', 'value': 0, 'uom': 108, 'name': 'GHG'}]

    def __init__(self, polyglot, plugin, controller='oadr3controlle',
        address='oadr3ven', name='OADR3VEN'):
        super().__init__(polyglot, controller, address, name)
        self.plugin = plugin

    def getUOM(self, driver: str):
        try:
            for driver_def in self.drivers:
                if driver_def['driver'] == driver:
                    return driver_def['uom']
            return None
        except Exception as ex:
            return None

    def updatePrice(self, value, force: bool=None, text: str=None):
        return self.setDriver("ST", value, 103, force, text)

    def getPrice(self):
        return self.getDriver("ST")

    def updateGHG(self, value, force: bool=None, text: str=None):
        return self.setDriver("GHG", value, 108, force, text)

    def getGHG(self):
        return self.getDriver("GHG")
    """This is a list of commands that were defined in the nodedef"""
    commands = {}
    """    """

    def queryAll(self):
        self.queryPrice()
        self.queryGHG()

    """########WARNING: DO NOT MODIFY THIS LINE!!! NOTHING BELOW IS REGENERATED!#########"""

    def queryPrice():
        try:
            return True
        except:
            return False

    def queryGHG():
        try:
            return True
        except:
            return False