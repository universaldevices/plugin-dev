import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class Oadr3EnergyOptimizerNode(udi_interface.Node):
    id = 'oadr3ven'
    """This is a list of properties that were defined in the nodedef"""
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 103, 'name': 'Price'}, {
        'driver': 'GHG', 'value': 0, 'uom': 108, 'name': 'GHG'}, {'driver':
        'CL', 'value': 0, 'uom': 25, 'name': 'Comfort Level'}, {'driver':
        'CGS', 'value': 0, 'uom': 25, 'name': 'Current Grid Status'}, {
        'driver': 'PRPUSH', 'value': 0, 'uom': 25, 'name':
        'Notify Price Changes'}, {'driver': 'DRPUSH', 'value': 0, 'uom': 25,
        'name': 'Notify DR Events'}, {'driver': 'DEVOPT', 'value': 0, 'uom':
        25, 'name': 'Notify Device States'}]

    def __init__(self, polyglot, plugin, controller='oadr31controll',
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

    def updateNotifyPriceChanges(self, value, force: bool=None, text: str=None
        ):
        return self.setDriver("PRPUSH", value, 25, force, text)

    def getNotifyPriceChanges(self):
        return self.getDriver("PRPUSH")

    def updateNotifyDREvents(self, value, force: bool=None, text: str=None):
        return self.setDriver("DRPUSH", value, 25, force, text)

    def getNotifyDREvents(self):
        return self.getDriver("DRPUSH")

    def updateNotifyDeviceStates(self, value, force: bool=None, text: str=None
        ):
        return self.setDriver("DEVOPT", value, 25, force, text)

    def getNotifyDeviceStates(self):
        return self.getDriver("DEVOPT")

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

    def __setNotifyPriceChanges(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            value = command.get('value', None)
            if 'PRPUSH.uom25' in jparam:
                PRPUSH = int(jparam['PRPUSH.uom25'])
            elif value:
                PRPUSH = int(value)
            return self.setNotifyPriceChanges(PRPUSH)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setNotifyDREvents(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            value = command.get('value', None)
            if 'DRPUSH.uom25' in jparam:
                DRPUSH = int(jparam['DRPUSH.uom25'])
            elif value:
                DRPUSH = int(value)
            return self.setNotifyDREvents(DRPUSH)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setNotifyDeviceStates(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            value = command.get('value', None)
            if 'DEVOPT.uom25' in jparam:
                DEVOPT = int(jparam['DEVOPT.uom25'])
            elif value:
                DEVOPT = int(value)
            return self.setNotifyDeviceStates(DEVOPT)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False
    """This is a list of commands that were defined in the nodedef"""
    commands = {'CL': __setComfortLevel, 'PRPUSH': __setNotifyPriceChanges,
        'DRPUSH': __setNotifyDREvents, 'DEVOPT': __setNotifyDeviceStates}
    """    """

    def queryAll(self):
        self.queryPrice()
        self.queryGHG()
        self.queryComfortLevel()
        self.queryCurrentGridStatus()
        self.queryNotifyPriceChanges()
        self.queryNotifyDREvents()
        self.queryNotifyDeviceStates()

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

    def queryNotifyPriceChanges(self):
        try:
            return self.updateNotifyPriceChanges(self.settings.get('PRPUSH', 0))
        except:
            return False

    def queryNotifyDREvents(self):
        try:
            return self.updateNotifyDREvents(self.settings.get('DRPUSH', 0))
        except:
            return False

    def queryNotifyDeviceStates(self):
        try:
            return self.updateNotifyDeviceStates(self.settings.get('DEVOPT', 0))
        except:
            return False


    def setComfortLevel(self, cl):
        try:
            if self.settings.set('CL', cl):
                return self.updateComfortLevel(cl)
            return False 
        except:
            return False

    def setNotifyPriceChanges(self, pc):
        try:
            if self.settings.set('PRPUSH', pc):
                return self.updateNotifyPriceChanges(pc)
        except:
            return False

    def setNotifyDREvents(self, dr):
        try:
            if self.settings.set('DRPUSH', dr):
                return self.updateNotifyDREvents(dr)
        except:
            return False

    def setNotifyDeviceStates(self, ds):
        try:
            if self.settings.set('DEVOPT', ds):
                return self.updateNotifyDeviceStates(ds)
            return False 
        except:
            return False


    def calculateGridStatus(self, price):
        from opt_config.ven_settings import GridState
        # Determine Current Grid Status based on GHG and Price
        # if price is < 0.35, grid status is normal (0)
        if price < self.settings.moderate_price_threshold: 
            status = GridState.NORMAL
        # if price is between 0.35 and 0.50, grid status is moderate (1)
        elif self.settings.moderate_price_threshold <= price < self.settings.high_price_threshold: 
            status = GridState.MODERATE
        # if price is between 0.50 and 1.00, grid status is high (2)
        elif self.settings.high_price_threshold <= price < self.settings.dr_thold:
            status = GridState.HIGH
        # if price is >= 1.00, grid status is emergency (3)
        else:
            status = GridState.DR

        self.updateCurrentGridStatus(status)
        return status

    def updateSimple(self, value, force: bool=None, text: str=None):
        if not value:
            return 
        value = int(value)+1
        self.updateCurrentGridStatus(value, force)