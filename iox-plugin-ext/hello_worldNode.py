import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
from micNode import micNode
class hello_worldNode(udi_interface.Node):
    id = 'hello_worldCtrl'
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2, 'name': 'Status'}]
    commands = [{'discover': Discover}, {'query': Query}]

    def __init__(self, poly, controller='hello_worldCtrl', address=
        'hello_worldCtrl', name='hello_world'):
        super.__init__(self, poly, controller, address, name)
        self.Parameters = Custom(polyglot, 'customparams')
        self.valid_configuration = False
        self.poly(polyglot.START, self.start)
        self.poly(polyglot.CUSTOMPARAMS, self.parameter_handler)
        self.poly(polyglot.POLL, self.poll)
        self.poly(polyglot.STOP, self.stop)
        self.poly(polyglot.CONFIG, self.config)
        self.poly.ready()
        self.addAllNodes()

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

    def updateStatus(self, value, force: bool):
        return self.setDriver("ST", value, 2, force)

    def getStatus(self):
        return self.getDriver("ST")

    def Discover(self, command):
        return True

    def Query(self, command):
        return True
