import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class ShellyGenericDimmerNode(udi_interface.Node):
    id = 'sdimmer'
    """This is a list of properties that were defined in the nodedef"""
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 51, 'name': 'Status'}, {
        'driver': 'RAMP_RATE', 'value': 0, 'uom': 57, 'name': 'Ramp Rate'},
        {'driver': 'ON_LEVEL', 'value': 0, 'uom': 51, 'name': 'On Level'}]

    def __init__(self, polyglot, protocolHandler, controller=
        'shellycontroll', address='sdimmer', name='Shelly Generic Dimmer'):
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

    def updateRampRate(self, value, force: bool):
        return self.setDriver("RAMP_RATE", value, 57, force)

    def getRampRate(self):
        return self.getDriver("RAMP_RATE")

    def queryRampRate(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'RAMP_RATE')
            if val != None:
                self.updateRampRate(val, True)
                return True
        return False

    def updateOnLevel(self, value, force: bool):
        return self.setDriver("ON_LEVEL", value, 51, force)

    def getOnLevel(self):
        return self.getDriver("ON_LEVEL")

    def queryOnLevel(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'ON_LEVEL')
            if val != None:
                self.updateOnLevel(val, True)
                return True
        return False

    def queryAll(self):
        self.queryStatus()
        self.queryRampRate()
        self.queryOnLevel()

    def On(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            onlevel = int(jparam['onlevel.uom51'])
            ramprate = int(jparam['ramprate.uom57'])
            if self.protocolHandler:
                return self.protocolHandler.processCommand(self, 'On',
                    Level=onlevel, RampRate=ramprate)
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def Off(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            ramprate = int(jparam['ramprate.uom57'])
            if self.protocolHandler:
                return self.protocolHandler.processCommand(self, 'Off',
                    RampRate=ramprate)
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def FastOn(self, command):
        try:
            if self.protocolHandler:
                return self.protocolHandler.processCommand(self, 'FastOn')
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def FastOff(self, command):
        try:
            if self.protocolHandler:
                return self.protocolHandler.processCommand(self, 'FastOff')
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def setRampRate(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            RAMP_RATE = int(jparam['RAMP_RATE.uom57'])
            if self.protocolHandler:
                if self.protocolHandler.setProperty(self, 'RAMP_RATE',
                    RAMP_RATE):
                    self.updateRampRate(RAMP_RATE, True)
                    return True
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def setOnLevel(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            ON_LEVEL = int(jparam['ON_LEVEL.uom51'])
            if self.protocolHandler:
                if self.protocolHandler.setProperty(self, 'ON_LEVEL', ON_LEVEL
                    ):
                    self.updateOnLevel(ON_LEVEL, True)
                    return True
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False
    """This is a list of commands that were defined in the nodedef"""
    commands = {'on': On, 'off': Off, 'faston': FastOn, 'fastoff': FastOff,
        'RAMP_RATE': setRampRate, 'ON_LEVEL': setOnLevel}
