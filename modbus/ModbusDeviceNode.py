import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class ModbusDeviceNode(udi_interface.Node):
    id = 'modbus'
    """This is a list of properties that were defined in the nodedef"""
    drivers = [{'driver': 'GV0', 'value': 0, 'uom': 25, 'name':
        'Load Shave'}, {'driver': 'GV1', 'value': 0, 'uom': 1, 'name':
        'Batt DC Current'}, {'driver': 'GV2', 'value': 0, 'uom': 4, 'name':
        'Battery Temperature'}, {'driver': 'GV3', 'value': 0, 'uom': 1,
        'name': 'Load Shave Amps'}, {'driver': 'GV4', 'value': 0, 'uom': 72,
        'name': 'Batt DC Voltage'}, {'driver': 'GV5', 'value': 0, 'uom': 25,
        'name': 'Force Charge'}, {'driver': 'GV6', 'value': 0, 'uom': 25,
        'name': 'AC1 Qualification'}]

    def __init__(self, polyglot, protocolHandler, controller=
        'modbuscontroll', address='modbus', name='ModbusDevice'):
        super().__init__(polyglot, controller, address, name)
        self.protocolHandler = protocolHandler

    def setProtocolHandler(self, protocolHandler):
        self.protocolHandler = protocolHandler
    """Use this method to update LoadShave in IoX"""

    def updateLoadShave(self, value, force: bool):
        return self.setDriver("GV0", value, 25, force)

    def getLoadShave(self):
        return self.getDriver("GV0")

    def queryLoadShave(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GV0')
            if val != None:
                self.updateLoadShave(val, True)
                return True
        return False
    """Use this method to update BattDCCurrent in IoX"""

    def updateBattDCCurrent(self, value, force: bool):
        return self.setDriver("GV1", value, 1, force)

    def getBattDCCurrent(self):
        return self.getDriver("GV1")

    def queryBattDCCurrent(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GV1')
            if val != None:
                self.updateBattDCCurrent(val, True)
                return True
        return False
    """Use this method to update BatteryTemperature in IoX"""

    def updateBatteryTemperature(self, value, force: bool):
        return self.setDriver("GV2", value, 4, force)

    def getBatteryTemperature(self):
        return self.getDriver("GV2")

    def queryBatteryTemperature(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GV2')
            if val != None:
                self.updateBatteryTemperature(val, True)
                return True
        return False
    """Use this method to update LoadShaveAmps in IoX"""

    def updateLoadShaveAmps(self, value, force: bool):
        return self.setDriver("GV3", value, 1, force)

    def getLoadShaveAmps(self):
        return self.getDriver("GV3")

    def queryLoadShaveAmps(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GV3')
            if val != None:
                self.updateLoadShaveAmps(val, True)
                return True
        return False
    """Use this method to update BattDCVoltage in IoX"""

    def updateBattDCVoltage(self, value, force: bool):
        return self.setDriver("GV4", value, 72, force)

    def getBattDCVoltage(self):
        return self.getDriver("GV4")

    def queryBattDCVoltage(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GV4')
            if val != None:
                self.updateBattDCVoltage(val, True)
                return True
        return False
    """Use this method to update ForceCharge in IoX"""

    def updateForceCharge(self, value, force: bool):
        return self.setDriver("GV5", value, 25, force)

    def getForceCharge(self):
        return self.getDriver("GV5")

    def queryForceCharge(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GV5')
            if val != None:
                self.updateForceCharge(val, True)
                return True
        return False
    """Use this method to update AC1Qualification in IoX"""

    def updateAC1Qualification(self, value, force: bool):
        return self.setDriver("GV6", value, 25, force)

    def getAC1Qualification(self):
        return self.getDriver("GV6")

    def queryAC1Qualification(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GV6')
            if val != None:
                self.updateAC1Qualification(val, True)
                return True
        return False

    def queryAll(self):
        self.queryLoadShave()
        self.queryBattDCCurrent()
        self.queryBatteryTemperature()
        self.queryLoadShaveAmps()
        self.queryBattDCVoltage()
        self.queryForceCharge()
        self.queryAC1Qualification()

    def setLoadShave(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            GV0 = int(jparam['GV0.uom25'])
            if self.protocolHandler:
                if self.protocolHandler.setProperty(self, 'GV0', GV0):
                    self.updateLoadShave(GV0, True)
                    return True
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def setLoadShaveAmps(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            GV3 = int(jparam['GV3.uom1'])
            if self.protocolHandler:
                if self.protocolHandler.setProperty(self, 'GV3', GV3):
                    self.updateLoadShaveAmps(GV3, True)
                    return True
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def setForceCharge(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            GV5 = int(jparam['GV5.uom25'])
            if self.protocolHandler:
                if self.protocolHandler.setProperty(self, 'GV5', GV5):
                    self.updateForceCharge(GV5, True)
                    return True
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False
    """This is a list of commands that were defined in the nodedef"""
    commands = {'GV0': setLoadShave, 'GV3': setLoadShaveAmps, 'GV5':
        setForceCharge}
