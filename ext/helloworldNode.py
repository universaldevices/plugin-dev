import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
from micNode import micNode
class helloworldNode(udi_interface.Node):
    id = 'helloworldctrl'
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2, 'name': 'Status'}]
    children = [{'node_class': 'micNode', 'id': 'hell', 'name': 'mic',
        'parent': 'helloworldctrl'}]

    def __init__(self, polyglot, controller='helloworldctrl', address=
        'helloworldctrl', name='helloworld'):
        super().__init__(polyglot, controller, address, name)
        self.Parameters = Custom(polyglot, 'customparams')
        self.valid_configuration = False
        self.started = False
        self.poly.subscribe(polyglot.START, self.start)
        self.poly.subscribe(polyglot.CUSTOMPARAMS, self.parameter_handler)
        self.poly.subscribe(polyglot.POLL, self.poll)
        self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(polyglot.CONFIG, self.config)

    def parameter_handler(self, params):
        self.poly.Notices.clear()
        self.Parameters.load(params)
        return True

    def config(self):
        LOGGER.info(f'Config ... ')
        return True

    def start(self):
        LOGGER.info(f'Starting... ')
        self.poly.addNode(self)
        self.addAllNodes()
        self.poly.updateProfile()
        self.poly.setCustomParamsDoc()
        self.poly.ready()
        return True

    def stop(self):
        LOGGER.info(f'Stopping ... ')
        return True

    def poll(self, polltype):
        if 'shortPoll' in polltype:
            LOGGER.info(f'Short poll ... ')
        elif 'longPoll' in polltype:
            LOGGER.info(f'Long poll ... ')

    def addAllNodes(self):
        config = self.poly.getConfig()
        if config is None or config['nodes'] is None or len(config['nodes']
            ) <= 0:
            config = {}
            config['nodes'] = []
            for child in self.children:
                config['nodes'].append({'nodeDefId': child['id'], 'address':
                    child['node_class'], 'name': child['name'],
                    'primaryNode': child['parent']})
        for node in config['nodes']:
            if not self.__addNode(node):
                return
        LOGGER.info(f'Done adding nodes ...')
        self.valid_configuration = True

    def __addNode(self, node_info) ->bool:
        if node_info is None:
            LOGGER.error('node cannot be null')
            return False
        try:
            cls = globals()[node_info['address']]
            node = cls(self.poly, node_info['primaryNode'], node_info[
                'nodeDefId'], node_info['name'])
            if node is None:
                LOGGER.error(f'invalid noddef id ...')
                return False
            else:
                self.poly.addNode(node)
                return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    def updateStatus(self, value, force: bool):
        return self.setDriver("ST", value, 2, force)

    def getStatus(self):
        return self.getDriver("ST")

    def Discover(self, command):
        return True

    def Query(self, command):
        return True
    commands = {'discover': Discover, 'query': Query}
