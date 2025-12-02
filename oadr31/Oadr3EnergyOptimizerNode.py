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
        'driver': 'CSP_F', 'value': 0, 'uom': 17, 'name':
        'Comfort Cooling Setpoint'}, {'driver': 'HSP_F', 'value': 0, 'uom':
        17, 'name': 'Comfort Heating Setpoint'}, {'driver': 'CLL', 'value':
        0, 'uom': 51, 'name': 'Comfort Light Level'}, {'driver':
        'MIN_OFF_DEG', 'value': 0, 'uom': 17, 'name':
        'Min Comfort Setpoint Offset'}, {'driver': 'MAX_OFF_DEG', 'value': 
        0, 'uom': 17, 'name': 'Max Comfort Setpoint Offset'}, {'driver':
        'MIN_LAO', 'value': 0, 'uom': 51, 'name':
        'Min Comfort Light Adjustment Offset'}, {'driver': 'MAX_LAO',
        'value': 0, 'uom': 51, 'name':
        'Max Comfort Light Adjustment Offset'}, {'driver': 'MIN_DCO',
        'value': 0, 'uom': 51, 'name': 'Min Comfort Duty Cycle Offset'}, {
        'driver': 'MAX_DCO', 'value': 0, 'uom': 51, 'name':
        'Max Comfort Duty Cycle Offset'}]

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

    def updateComfortCoolingSetpoint(self, value, force: bool=None, text:
        str=None):
        return self.setDriver("CSP_F", value, 17, force, text)

    def getComfortCoolingSetpoint(self):
        return self.getDriver("CSP_F")

    def updateComfortHeatingSetpoint(self, value, force: bool=None, text:
        str=None):
        return self.setDriver("HSP_F", value, 17, force, text)

    def getComfortHeatingSetpoint(self):
        return self.getDriver("HSP_F")

    def updateComfortLightLevel(self, value, force: bool=None, text: str=None):
        return self.setDriver("CLL", value, 51, force, text)

    def getComfortLightLevel(self):
        return self.getDriver("CLL")

    def updateMinComfortSetpointOffset(self, value, force: bool=None, text:
        str=None):
        return self.setDriver("MIN_OFF_DEG", value, 17, force, text)

    def getMinComfortSetpointOffset(self):
        return self.getDriver("MIN_OFF_DEG")

    def updateMaxComfortSetpointOffset(self, value, force: bool=None, text:
        str=None):
        return self.setDriver("MAX_OFF_DEG", value, 17, force, text)

    def getMaxComfortSetpointOffset(self):
        return self.getDriver("MAX_OFF_DEG")

    def updateMinComfortLightAdjustmentOffset(self, value, force: bool=None,
        text: str=None):
        return self.setDriver("MIN_LAO", value, 51, force, text)

    def getMinComfortLightAdjustmentOffset(self):
        return self.getDriver("MIN_LAO")

    def updateMaxComfortLightAdjustmentOffset(self, value, force: bool=None,
        text: str=None):
        return self.setDriver("MAX_LAO", value, 51, force, text)

    def getMaxComfortLightAdjustmentOffset(self):
        return self.getDriver("MAX_LAO")

    def updateMinComfortDutyCycleOffset(self, value, force: bool=None, text:
        str=None):
        return self.setDriver("MIN_DCO", value, 51, force, text)

    def getMinComfortDutyCycleOffset(self):
        return self.getDriver("MIN_DCO")

    def updateMaxComfortDutyCycleOffset(self, value, force: bool=None, text:
        str=None):
        return self.setDriver("MAX_DCO", value, 51, force, text)

    def getMaxComfortDutyCycleOffset(self):
        return self.getDriver("MAX_DCO")

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

    def __setComfortCoolingSetpoint(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            value = command.get('value', None)
            if 'CSP_F.uom17' in jparam:
                CSP_F = int(jparam['CSP_F.uom17'])
            elif value:
                CSP_F = int(value)
            return self.setComfortCoolingSetpoint(CSP_F)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setComfortHeatingSetpoint(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            value = command.get('value', None)
            if 'HSP_F.uom17' in jparam:
                HSP_F = int(jparam['HSP_F.uom17'])
            elif value:
                HSP_F = int(value)
            return self.setComfortHeatingSetpoint(HSP_F)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setComfortLightLevel(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            value = command.get('value', None)
            if 'CLL.uom51' in jparam:
                CLL = int(jparam['CLL.uom51'])
            elif value:
                CLL = int(value)
            return self.setComfortLightLevel(CLL)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setMinComfortSetpointOffset(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            value = command.get('value', None)
            if 'MIN_OFF_DEG.uom17' in jparam:
                MIN_OFF_DEG = int(jparam['MIN_OFF_DEG.uom17'])
            elif value:
                MIN_OFF_DEG = int(value)
            return self.setMinComfortSetpointOffset(MIN_OFF_DEG)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setMaxComfortSetpointOffset(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            value = command.get('value', None)
            if 'MAX_OFF_DEG.uom17' in jparam:
                MAX_OFF_DEG = int(jparam['MAX_OFF_DEG.uom17'])
            elif value:
                MAX_OFF_DEG = int(value)
            return self.setMaxComfortSetpointOffset(MAX_OFF_DEG)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setMinComfortLightAdjustmentOffset(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            value = command.get('value', None)
            if 'MIN_LAO.uom51' in jparam:
                MIN_LAO = int(jparam['MIN_LAO.uom51'])
            elif value:
                MIN_LAO = int(value)
            return self.setMinComfortLightAdjustmentOffset(MIN_LAO)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setMaxComfortLightAdjustmentOffset(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            value = command.get('value', None)
            if 'MAX_LAO.uom51' in jparam:
                MAX_LAO = int(jparam['MAX_LAO.uom51'])
            elif value:
                MAX_LAO = int(value)
            return self.setMaxComfortLightAdjustmentOffset(MAX_LAO)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setMinComfortDutyCycleOffset(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            value = command.get('value', None)
            if 'MIN_DCO.uom51' in jparam:
                MIN_DCO = int(jparam['MIN_DCO.uom51'])
            elif value:
                MIN_DCO = int(value)
            return self.setMinComfortDutyCycleOffset(MIN_DCO)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setMaxComfortDutyCycleOffset(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            value = command.get('value', None)
            if 'MAX_DCO.uom51' in jparam:
                MAX_DCO = int(jparam['MAX_DCO.uom51'])
            elif value:
                MAX_DCO = int(value)
            return self.setMaxComfortDutyCycleOffset(MAX_DCO)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False
    """This is a list of commands that were defined in the nodedef"""
    commands = {'CL': __setComfortLevel, 'CSP_F':
        __setComfortCoolingSetpoint, 'HSP_F': __setComfortHeatingSetpoint,
        'CLL': __setComfortLightLevel, 'MIN_OFF_DEG':
        __setMinComfortSetpointOffset, 'MAX_OFF_DEG':
        __setMaxComfortSetpointOffset, 'MIN_LAO':
        __setMinComfortLightAdjustmentOffset, 'MAX_LAO':
        __setMaxComfortLightAdjustmentOffset, 'MIN_DCO':
        __setMinComfortDutyCycleOffset, 'MAX_DCO':
        __setMaxComfortDutyCycleOffset}
    """    """

    def queryAll(self):
        self.queryPrice()
        self.queryGHG()
        self.queryComfortLevel()
        self.queryCurrentGridStatus()
        self.queryComfortCoolingSetpoint()
        self.queryComfortHeatingSetpoint()
        self.queryComfortLightLevel()
        self.queryMinComfortSetpointOffset()
        self.queryMaxComfortSetpointOffset()
        self.queryMinComfortLightAdjustmentOffset()
        self.queryMaxComfortLightAdjustmentOffset()
        self.queryMinComfortDutyCycleOffset()
        self.queryMaxComfortDutyCycleOffset()

    """########WARNING: DO NOT MODIFY THIS LINE!!! NOTHING BELOW IS REGENERATED!#########"""


    def set_settings(self):
        from ven_settings import VENSettings
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

    def queryComfortCoolingSetpoint(self):
        try:
            return self.updateComfortCoolingSetpoint(self.settings.get('CSP_F', 74))
        except:
            return False

    def queryComfortHeatingSetpoint(self):
        try:
            return self.updateComfortHeatingSetpoint(self.settings.get('HSP_F', 77))
        except:
            return False

    def queryComfortLightLevel(self):
        try:
            return self.updateComfortLightLevel(self.settings.get('CLL', 100))
        except:
            return False

    def queryMinComfortSetpointOffset(self):
        try:
            return self.updateMinComfortSetpointOffset(self.settings.get('MIN_OFF_DEG', 1))
        except:
            return False

    def queryMaxComfortSetpointOffset(self):
        try:
            return self.updateMaxComfortSetpointOffset(self.settings.get('MAX_OFF_DEG', 4))
        except:
            return False

    def queryMinComfortLightAdjustmentOffset(self):
        try:
            return self.updateMinComfortLightAdjustmentOffset(self.settings.get('MIN_LAO', 10))
        except:
            return False

    def queryMaxComfortLightAdjustmentOffset(self):
        try:
            return self.updateMaxComfortLightAdjustmentOffset(self.settings.get('MAX_LAO', 50))
        except:
            return False

    def queryMinComfortDutyCycleOffset(self):
        try:
            return self.updateMinComfortDutyCycleOffset(self.settings.get('MIN_DCO', 0))
        except:
            return False

    def queryMaxComfortDutyCycleOffset(self):
        try:
            return self.updateMaxComfortDutyCycleOffset(self.settings.get('MAX_DCO', 50))
        except:
            return False

    def setComfortLevel(self, cl):
        try:
            if self.settings.set('CL', cl):
                return self.updateComfortLevel(cl)
            return False 
        except:
            return False

    def setComfortCoolingSetpoint(self, cspf):
        try:
            if self.settings.set('CSP_F', cspf):
                return self.updateComfortCoolingSetpoint(cspf)
            return False
        except:
            return False

    def setComfortHeatingSetpoint(self, hspf):
        try:
            if self.settings.set('HSP_F', hspf):
                return self.updateComfortHeatingSetpoint(hspf)
            return False
        except:
            return False

    def setComfortLightLevel(self, cll ):
        try:
            if self.settings.set('CLL', cll ):
                return self.updateComfortLightLevel(cll)
            return False
        except:
            return False

    def setComfortMinSetpointOffset(self, minoffdeg):
        try:
            if self.settings.set('MIN_OFF_DEG', minoffdeg):
                return self.updateMinComfortSetpointOffset(minoffdeg)
            return False
        except:
            return False

    def setMaxComfortSetpointOffset(self, maxoffdeg):
        try:
            if self.settings.set('MAX_OFF_DEG', maxoffdeg):
                return self.updateMaxComfortSetpointOffset(maxoffdeg)
            return False
        except:
            return False

    def setMinComfortLightAdjustmentOffset(self, minlao):
        try:
            if self.settings.set('MIN_LAO', minlao):
                return self.updateMinComfortLightAdjustmentOffset(minlao)
            return False
        except:
            return False

    def setMaxComfortLightAdjustmentOffset(self, maxlao):
        try:
            if self.settings.set('MAX_LAO', maxlao):
                return self.updateMaxComfortLightAdjustmentOffset(maxlao)
            return False
        except:
            return False

    def setMinComfortDutyCycleOffset(self, mindco):
        try:
            if self.settings.set('MIN_DCO', mindco):
                return self.updateMinComfortDutyCycleOffset(mindco)
            return False
        except:
            return False

    def setMaxComfortDutyCycleOffset(self, maxdco):
        try:
            if self.settings.set('MAX_DCO', maxdco):
                return self.updateMaxComfortDutyCycleOffset(maxdco)
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