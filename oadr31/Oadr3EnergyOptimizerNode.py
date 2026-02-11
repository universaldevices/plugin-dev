import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class Oadr3EnergyOptimizerNode(udi_interface.Node):
    id = 'oadr3ven'
    """This is a list of properties that were defined in the nodedef"""
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 103, 'name': 'Price'}, {
        'driver': 'GHG', 'value': 0, 'uom': 108, 'name': 'GHG'}, {'driver':
        'CL', 'value': 0, 'uom': 25, 'name': 'Comfort Level'}, {'driver':
        'CGS', 'value': 0, 'uom': 25, 'name': 'Current Grid Status'}]

    def __init__(self, polyglot, plugin, controller='oadr3controlle',
        address='oadr3ven', name='Oadr3 Energy Optimizer'):
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

    def updateComfortLevel(self, value, force: bool=None, text: str=None):
        return self.setDriver("CL", value, 25, force, text)

    def getComfortLevel(self):
        return self.getDriver("CL")

    def updateCurrentGridStatus(self, value, force: bool=None, text: str=None):
        return self.setDriver("CGS", value, 25, force, text)

    def getCurrentGridStatus(self):
        return self.getDriver("CGS")

    def __setComfortLevel(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            value = command.get('value', None)
            if 'CL.uom25' in jparam:
                CL = int(jparam['CL.uom25'])
            elif value:
                CL = int(value)
            return self.setComfortLevel(CL)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False
    """This is a list of commands that were defined in the nodedef"""
    commands = {'CL': __setComfortLevel}
    """    """

    def queryAll(self):
        self.queryPrice()
        self.queryGHG()
        self.queryComfortLevel()
        self.queryCurrentGridStatus()

    """########WARNING: DO NOT MODIFY THIS LINE!!! NOTHING BELOW IS REGENERATED!#########"""

    def set_settings(self):
        from opt_config.ven_settings import VENSettings
        self.settings = VENSettings()

    def get_settings(self):
        return self.settings

    def queryPrice(self):
        try:
            return self.updatePrice(self.settings.get('Price', 0))
        except:
            return False

    def queryGHG(self):
        try:
            return self.updateGHG(self.settings.get('GHG', 0))
        except:
            return False

    def queryComfortLevel(self):
        try:
            return self.updateComfortLevel(self.settings.get('CL', 0))
        except:
            return False

    def queryCurrentGridStatus(self):
        try:
            return self.updateCurrentGridStatus(self.settings.get('CGS', 0))
        except:
            return False

    def setComfortLevel(self, cl):
        try:
            if self.settings.set('CL', cl):
                return self.updateComfortLevel(cl)
            return False 
        except:
            return False

    def calculateGridStatus(self, price):
        from opt_config.ven_settings import GridState
        # Determine Current Grid Status based on GHG and Price
        # if price is < 0.35, grid status is normal (0)
        if price < 0.35:
            status = GridState.NORMAL
        # if price is between 0.35 and 0.50, grid status is moderate (1)
        elif 0.35 <= price < 0.50:
            status = GridState.MODERATE
        # if price is between 0.50 and 1.00, grid status is high (2)
        elif 0.50 <= price < 1.00:
            status = GridState.HIGH
        # if price is >= 1.00, grid status is emergency (3)
        else:
            status = GridState.DR

        self.updateCurrentGridStatus(status)

    def updateSimple(self, value, force: bool=None, text: str=None):
        if not value:
            return 
        value = int(value)+1
        self.updateCurrentGridStatus(value, force)