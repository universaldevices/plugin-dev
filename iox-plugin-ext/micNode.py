import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class micNode(udi_interface.Node):
    id = 'hell'
    drivers = [{'driver': 'ACCX', 'value': 0, 'uom': 94, 'name': 'temp'}, {
        'driver': 'CTL', 'value': 0, 'uom': 25, 'name': 'ctl'}, {'driver':
        'GV1', 'value': 0, 'uom': 136, 'name': 'Generic Val'}]
    commands = [{'acc_cmd1': accept1}, {'acc_cmd2': accept2}, {'ACCX':
        setTemp}, {'CTL': setCtl}]

    def __init__(self, poly, controller='hello_worldCtrl', address='hell',
        name='mic'):
        super.__init__(self, poly, controller, address, name)

    def parameter_handler(self, params):
        self.poly.Notices.clear()
        self.Parameters.load(params)
        return True

    def config(self):
        LOGGER.info(f'Config ... ')
        return True

    def start(self):
        LOGGER.info(f'Starting ... ')
        self.addAllNodes()
        polyglot.updateProfile()
        self.poly.setCustomParamsDoc()
        return True

    def stop(self):
        LOGGER.info(f'Stopping ... ')
        return True

    def poll(polltype):
        if 'shortPoll' in polltype:
            LOGGER.info(f'Short poll ... ')
        elif 'longPoll' in polltype:
            LOGGER.info(f'Long poll ... ')

    def addAllNodes(self):
        config = self.poly.getConfig()
        if config is None or config['nodes'] is None:
            self.valid_configuration = True
            return
        for node in config['nodes']:
            nodeDef = node['nodeDefId']
            address = node['address']
            primary = node['primaryNode']
            name = node['name']
            self.__addNode(nodeDef, address, name)
        LOGGER.info(f'Done adding nodes ...')
        self.valid_configuration = True

    def __addNode(self, nodeDef: str, endDeviceAddress: str, devName: str):
        if nodeDef is None:
            return
        devNode = None
        if devNode is None:
            LOGGER.error(f'invalid noddef id ...')
            return
        self.poly.addNode(devNode)

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

    def setTemp(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            ACCX = int(jparam['ACCX.uom94'])
            return True
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def setCtl(self, command):
        try:
            CTL = command.get('CTL')
            return True
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False
