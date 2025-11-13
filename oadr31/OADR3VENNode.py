import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class OADR3VENNode(udi_interface.Node):
    id = 'oadr3ven'
    """This is a list of properties that were defined in the nodedef"""
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 103, 'name': 'Price'}, {
        'driver': 'GHG', 'value': 0, 'uom': 108, 'name': 'GHG'}, {'driver':
        'CL', 'value': 0, 'uom': 25, 'name': 'Comfort Level'}, {'driver':
        'CGS', 'value': 0, 'uom': 25, 'name': 'Current Grid Status'}, {
        'driver': 'CSP_F', 'value': 0, 'uom': 17, 'name':
        'Desired Cooling Setpoint'}, {'driver': 'HSP_F', 'value': 0, 'uom':
        17, 'name': 'Desired Heating Setpoint'}, {'driver': 'OL', 'value': 
        0, 'uom': 51, 'name': 'Desired Light Level'}, {'driver':
        'MIN_OFF_DEG', 'value': 0, 'uom': 17, 'name': 'Min Setpoint Offset'
        }, {'driver': 'MAX_OFF_DEG', 'value': 0, 'uom': 17, 'name':
        'Max Setpoint Offset'}, {'driver': 'MIN_LAO', 'value': 0, 'uom': 51,
        'name': 'Min Light Adjustment Offset'}, {'driver': 'MAX_LAO',
        'value': 0, 'uom': 51, 'name': 'Max Light Adjustment Offset'}, {
        'driver': 'MIN_DCO', 'value': 0, 'uom': 51, 'name':
        'Min Duty Cycle Offset'}, {'driver': 'MAX_DCO', 'value': 0, 'uom': 
        51, 'name': 'Max Duty Cycle Offset'}]

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

    def updateComfortLevel(self, value, force: bool=None, text: str=None):
        return self.setDriver("CL", value, 25, force, text)

    def getComfortLevel(self):
        return self.getDriver("CL")

    def updateCurrentGridStatus(self, value, force: bool=None, text: str=None):
        return self.setDriver("CGS", value, 25, force, text)

    def getCurrentGridStatus(self):
        return self.getDriver("CGS")

    def updateDesiredCoolingSetpoint(self, value, force: bool=None, text:
        str=None):
        return self.setDriver("CSP_F", value, 17, force, text)

    def getDesiredCoolingSetpoint(self):
        return self.getDriver("CSP_F")

    def updateDesiredHeatingSetpoint(self, value, force: bool=None, text:
        str=None):
        return self.setDriver("HSP_F", value, 17, force, text)

    def getDesiredHeatingSetpoint(self):
        return self.getDriver("HSP_F")

    def updateDesiredLightLevel(self, value, force: bool=None, text: str=None):
        return self.setDriver("OL", value, 51, force, text)

    def getDesiredLightLevel(self):
        return self.getDriver("OL")

    def updateMinSetpointOffset(self, value, force: bool=None, text: str=None):
        return self.setDriver("MIN_OFF_DEG", value, 17, force, text)

    def getMinSetpointOffset(self):
        return self.getDriver("MIN_OFF_DEG")

    def updateMaxSetpointOffset(self, value, force: bool=None, text: str=None):
        return self.setDriver("MAX_OFF_DEG", value, 17, force, text)

    def getMaxSetpointOffset(self):
        return self.getDriver("MAX_OFF_DEG")

    def updateMinLightAdjustmentOffset(self, value, force: bool=None, text:
        str=None):
        return self.setDriver("MIN_LAO", value, 51, force, text)

    def getMinLightAdjustmentOffset(self):
        return self.getDriver("MIN_LAO")

    def updateMaxLightAdjustmentOffset(self, value, force: bool=None, text:
        str=None):
        return self.setDriver("MAX_LAO", value, 51, force, text)

    def getMaxLightAdjustmentOffset(self):
        return self.getDriver("MAX_LAO")

    def updateMinDutyCycleOffset(self, value, force: bool=None, text: str=None
        ):
        return self.setDriver("MIN_DCO", value, 51, force, text)

    def getMinDutyCycleOffset(self):
        return self.getDriver("MIN_DCO")

    def updateMaxDutyCycleOffset(self, value, force: bool=None, text: str=None
        ):
        return self.setDriver("MAX_DCO", value, 51, force, text)

    def getMaxDutyCycleOffset(self):
        return self.getDriver("MAX_DCO")

    def __setComfortLevel(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'CL.uom25' in jparam:
                CL = int(jparam['CL.uom25'])
            return self.setComfortLevel(CL)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setDesiredCoolingSetpoint(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'CSP_F.uom17' in jparam:
                CSP_F = int(jparam['CSP_F.uom17'])
            return self.setDesiredCoolingSetpoint(CSP_F)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setDesiredHeatingSetpoint(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'HSP_F.uom17' in jparam:
                HSP_F = int(jparam['HSP_F.uom17'])
            return self.setDesiredHeatingSetpoint(HSP_F)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setDesiredLightLevel(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'OL.uom51' in jparam:
                OL = int(jparam['OL.uom51'])
            return self.setDesiredLightLevel(OL)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setMinSetpointOffset(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'MIN_OFF_DEG.uom17' in jparam:
                MIN_OFF_DEG = int(jparam['MIN_OFF_DEG.uom17'])
            return self.setMinSetpointOffset(MIN_OFF_DEG)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setMaxSetpointOffset(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'MAX_OFF_DEG.uom17' in jparam:
                MAX_OFF_DEG = int(jparam['MAX_OFF_DEG.uom17'])
            return self.setMaxSetpointOffset(MAX_OFF_DEG)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setMinLightAdjustmentOffset(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'MIN_LAO.uom51' in jparam:
                MIN_LAO = int(jparam['MIN_LAO.uom51'])
            return self.setMinLightAdjustmentOffset(MIN_LAO)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setMaxLightAdjustmentOffset(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'MAX_LAO.uom51' in jparam:
                MAX_LAO = int(jparam['MAX_LAO.uom51'])
            return self.setMaxLightAdjustmentOffset(MAX_LAO)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setMinDutyCycleOffset(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'MIN_DCO.uom51' in jparam:
                MIN_DCO = int(jparam['MIN_DCO.uom51'])
            return self.setMinDutyCycleOffset(MIN_DCO)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setMaxDutyCycleOffset(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'MAX_DCO.uom51' in jparam:
                MAX_DCO = int(jparam['MAX_DCO.uom51'])
            return self.setMaxDutyCycleOffset(MAX_DCO)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False
    """This is a list of commands that were defined in the nodedef"""
    commands = {'CL': __setComfortLevel, 'CSP_F':
        __setDesiredCoolingSetpoint, 'HSP_F': __setDesiredHeatingSetpoint,
        'OL': __setDesiredLightLevel, 'MIN_OFF_DEG': __setMinSetpointOffset,
        'MAX_OFF_DEG': __setMaxSetpointOffset, 'MIN_LAO':
        __setMinLightAdjustmentOffset, 'MAX_LAO':
        __setMaxLightAdjustmentOffset, 'MIN_DCO': __setMinDutyCycleOffset,
        'MAX_DCO': __setMaxDutyCycleOffset}
    """    """

    def queryAll(self):
        self.queryPrice()
        self.queryGHG()
        self.queryComfortLevel()
        self.queryCurrentGridStatus()
        self.queryDesiredCoolingSetpoint()
        self.queryDesiredHeatingSetpoint()
        self.queryDesiredLightLevel()
        self.queryMinSetpointOffset()
        self.queryMaxSetpointOffset()
        self.queryMinLightAdjustmentOffset()
        self.queryMaxLightAdjustmentOffset()
        self.queryMinDutyCycleOffset()
        self.queryMaxDutyCycleOffset()

    """########WARNING: DO NOT MODIFY THIS LINE!!! NOTHING BELOW IS REGENERATED!#########"""

    from ven_settings import VENSettings
    settings = VENSettings()

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

    def queryDesiredCoolingSetpoint(self):
        try:
            return self.updateDesiredCoolingSetpoint(self.settings.get('CSP_F', 74))
        except:
            return False

    def queryDesiredHeatingSetpoint(self):
        try:
            return self.updateDesiredHeatingSetpoint(self.settings.get('HSP_F', 77))
        except:
            return False

    def queryDesiredLightLevel(self):
        try:
            return self.updateDesiredLightLevel(self.settings.get('OL', 100))
        except:
            return False

    def queryMinSetpointOffset(self):
        try:
            return self.updateMinSetpointOffset(self.settings.get('MIN_OFF_DEG', 1))
        except:
            return False

    def queryMaxSetpointOffset(self):
        try:
            return self.updateMaxSetpointOffset(self.settings.get('MAX_OFF_DEG', 4))
        except:
            return False

    def queryMinLightAdjustmentOffset(self):
        try:
            return self.updateMinLightAdjustmentOffset(self.settings.get('MIN_LAO', 10))
        except:
            return False

    def queryMaxLightAdjustmentOffset(self):
        try:
            return self.updateMaxLightAdjustmentOffset(self.settings.get('MAX_LAO', 50))
        except:
            return False

    def queryMinDutyCycleOffset(self):
        try:
            return self.updateMinDutyCycleOffset(self.settings.get('MIN_DCO', 0))
        except:
            return False

    def queryMaxDutyCycleOffset(self):
        try:
            return self.updateMaxDutyCycleOffset(self.settings.get('MAX_DCO', 50))
        except:
            return False

    def setComfortLevel(self, cl):
        try:
            if self.settings.set('CL', cl):
                return self.updateComfortLevel(cl)
            return False 
        except:
            return False

    def setDesiredCoolingSetpoint(self, cspf):
        try:
            if self.settings.set('CSP_F', cspf):
                return self.updateDesiredCoolingSetpoint(cspf)
            return False
        except:
            return False

    def setDesiredHeatingSetpoint(self, hspf):
        try:
            if self.settings.set('HSP_F', hspf):
                return self.updateDesiredHeatingSetpoint(hspf)
            return False
        except:
            return False

    def setDesiredLightLevel(self, ol):
        try:
            if self.settings.set('OL', ol):
                return self.updateDesiredLightLevel(ol)
            return False
        except:
            return False

    def setMinSetpointOffset(self, minoffdeg):
        try:
            if self.settings.set('MIN_OFF_DEG', minoffdeg):
                return self.updateMinSetpointOffset(minoffdeg)
            return False
        except:
            return False

    def setMaxSetpointOffset(self, maxoffdeg):
        try:
            if self.settings.set('MAX_OFF_DEG', maxoffdeg):
                return self.updateMaxSetpointOffset(maxoffdeg)
            return False
        except:
            return False

    def setMinLightAdjustmentOffset(self, minlao):
        try:
            if self.settings.set('MIN_LAO', minlao):
                return self.updateMinLightAdjustmentOffset(minlao)
            return False
        except:
            return False

    def setMaxLightAdjustmentOffset(self, maxlao):
        try:
            if self.settings.set('MAX_LAO', maxlao):
                return self.updateMaxLightAdjustmentOffset(maxlao)
            return False
        except:
            return False

    def setMinDutyCycleOffset(self, mindco):
        try:
            if self.settings.set('MIN_DCO', mindco):
                return self.updateMinDutyCycleOffset(mindco)
            return False
        except:
            return False

    def setMaxDutyCycleOffset(self, maxdco):
        try:
            if self.settings.set('MAX_DCO', maxdco):
                return self.updateMaxDutyCycleOffset(maxdco)
            return False    
        except:
            return False
        
    def calculateGridStatus(self, price):
        # Determine Current Grid Status based on GHG and Price
        # if price is < 0.35, grid status is normal (0)
        if price < 0.35:
            status = 0
        # if price is between 0.35 and 0.50, grid status is moderate (1)
        elif 0.35 <= price < 0.50:
            status = 1
        # if price is between 0.50 and 0.75, grid status is high (2)
        elif 0.50 <= price < 0.75:
            status = 2
        # if price is >= 0.75, grid status is emergency (3)
        else:
            status = 3

        self.updateCurrentGridStatus(status)