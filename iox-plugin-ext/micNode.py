import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class micNode(udi_interface.Node):
    id = 'hell'
    drivers = [{'driver': 'ACCX', 'value': 0, 'uom': 94, 'name': 'temp'}, {
        'driver': 'CTL', 'value': 0, 'uom': 25, 'name': 'ctl'}, {'driver':
        'GV1', 'value': 0, 'uom': 136, 'name': 'Generic Val'}]

    def __init__(self, polyglot, controller='helloworldctrl', address=
        'hell', name='mic'):
        super().__init__(polyglot, controller, address, name)

    def updateTemp(self, value, force: bool):
        return self.setDriver("ACCX", value, 94, force)

    def getTemp(self):
        return self.getDriver("ACCX")

    def updateCtl(self, value, force: bool):
        return self.setDriver("CTL", value, 25, force)

    def getCtl(self):
        return self.getDriver("CTL")

    def updateGenericVal(self, value, force: bool):
        return self.setDriver("GV1", value, 136, force)

    def getGenericVal(self):
        return self.getDriver("GV1")

    def accept1(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            param_c_1 = int(jparam['param_c_1.uom136'])
            param_c_2 = int(jparam['param_c_2.uom1'])
            return True
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def accept2(self, command):
        try:
            hello_param_2_accept = command.get('param_c_1a')
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            param_c_2_a = int(jparam['param_c_2_a.uom103'])
            return True
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False
    commands = [{'acc_cmd1': accept1}, {'acc_cmd2': accept2}]
