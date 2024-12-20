
import udi_interface, os, shutil, sys, json, time, threading
from udi_interface import OAuth
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
from ioxplugin import Plugin, OAuthService

DATA_PATH='./data'
from ShellyGenericDimmerNode import ShellyGenericDimmerNode
from ShellyGenericSwitchNode import ShellyGenericSwitchNode
class ShellyControllerNode(udi_interface.Node):
    id = 'shellycontroll'
    """This is a list of properties that were defined in the nodedef"""
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Status'}]
    children = [{'node_class': 'ShellyGenericDimmerNode', 'id': 'sdimmer',
        'name': 'Shelly Generic Dimmer', 'parent': 'shellycontroll'}, {
        'node_class': 'ShellyGenericSwitchNode', 'id': 'sswitch', 'name':
        'Shelly Generic Switch', 'parent': 'shellycontroll'}]

    def __init__(self, polyglot, protocolHandler, controller=
        'shellycontroll', address='shellycontroll', name='Shelly Controller'):
        super().__init__(polyglot, controller, address, name)
        self.protocolHandler = protocolHandler
        self.Parameters = Custom(polyglot, 'customparams')
        self.poly.addNode(self, conn_status='ST')
        self.oauthService = None
        self.poly.subscribe(polyglot.START, self.start, address)
        self.poly.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(polyglot.POLL, self.poll)
        self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(polyglot.CONFIG, self.configHandler)
        self.poly.subscribe(polyglot.CONFIGDONE, self.configDoneHandler)
        self.poly.subscribe(polyglot.ADDNODEDONE, self.addNodeDoneHandler)
        self.poly.subscribe(polyglot.CUSTOMNS, self.customNSHandler)
        self.poly.subscribe(polyglot.CUSTOMDATA, self.customDataHandler)
        self.poly.subscribe(polyglot.DISCOVER, self.discover)
        self.poly.subscribe(polyglot.BONJOUR, self.bonjourHandler)
        self.configDone = threading.Condition()
        self.initOAuth()
        self.configDoneAlready = False

    def getUOM(self, driver: str):
        try:
            for driver_def in self.drivers:
                if driver_def['driver'] == driver:
                    return driver_def['uom']
            return None
        except Exception as ex:
            return None


    def setProtocolHandler(self, protocolHandler):
        self.protocolHandler = protocolHandler

    def initOAuth(self):
        if self.protocolHandler and self.protocolHandler.plugin and self.protocolHandler.plugin.meta and self.protocolHandler.plugin.meta.getEnableOAUTH2():
            self.oauthService = OAuthService(self.polyglot)
            self.poly.subscribe(polyglot.OAUTH, self.oauthHandler)

    def parameterHandler(self, params):
        self.Parameters.load(params)
        return self.protocolHandler.processParams(self.Parameters)

    def configHandler(self, param):
        try:
            if os.path.exists(DATA_PATH):
                self.protocolHandler.filesUploaded(DATA_PATH)
                shutil.rmtree(DATA_PATH)
            if param:
                return self.protocolHandler.processConfig(param)
        except Exception as ex:
            LOGGER.warn(str(ex))

        return True

    def bonjourHandler(self, message):
        try:
            command = message['command']
            if command == None or command != "bonjour": 
                return
            mdns = message['mdns']
            self.protocolHandler.processMDNSResults(mdns)
        except Exception as ex:
            LOGGER.error(str(ex))

    def start(self):
        LOGGER.info(f'Starting... ')
        try:
            self.poly.setCustomParamsDoc()
            if not self.configDoneAlready:
                with self.configDone:
                    result = self.configDone.wait(timeout=10)
                    if not result:
                        #timedout
                        LOGGER.info("timed out while waiting for configDone")
                        self.updateStatus(0, True) 
                        return False
            if self.protocolHandler.start():
                self.addAllNodes()
                self.poly.updateProfile()
                self.updateStatus(1, True) 
                return True
            else:
                LOGGER.info("protocol handler failed processing config ...")
                self.updateStatus(0, True) 
                return False
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    def stop(self):
        LOGGER.info(f'Stopping ... ')
        self.protocolHandler.stop()
        self.updateStatus(0,True)
        return True

    def poll(self, polltype):
        if not self.configDoneAlready:
            return
        if 'shortPoll' in polltype:
            self.protocolHandler.shortPoll()
        elif 'longPoll' in polltype:
            self.protocolHandler.longPoll()

    def addAllNodes(self):
        config = self.poly.getConfig()
        if config is None or config['nodes'] is None or len(config['nodes']) <= 0:
            config = {}
            config['nodes'] = []

        if self.protocolHandler.plugin.areNodesStatic():
            for child in self.children:
                try:
                    config['nodes'].append({'nodeDefId': child['id'], 'address':
                    child['id'], 'name': child['name'],
                    'primaryNode': child['parent']})
                except Exception as ex:
                    LOGGER.error(str(ex))
                    return

        for node in config['nodes']:
            if node['nodeDefId'] == self.id:
                continue
            if not self.__addNode(node):
                return
        LOGGER.info(f'Done adding nodes ...')

#michel-new
    def addNode(self, address:str, nodeDefId:str, name:str, parent:str=None):
        if address == None or nodeDefId == None:
            LOGGER.error("need address and nodeDefId ...")
            return False

        if parent == None:
            parent = address  

        nodeInfo={}
        nodeInfo['primaryNode']=parent
        nodeInfo['address']=address
        nodeInfo['name']=name
        nodeInfo['nodeDefId']=nodeDefId
        return self.__addNode(nodeInfo)
#end Michel
 
    def __getNodeClass(self, nodeDefId:str)->str:
        for child in self.children:
            if child['id'] == nodeDefId:
                return child['node_class']
        return None

    def __addNode(self, node_info) ->bool:
        if node_info is None:
            LOGGER.error('node cannot be null')
            return False
        try:
            node_class = self.__getNodeClass(node_info['nodeDefId'])
            if node_class == None:
                return False
            node_address=node_info['address'] 
            if not node_address:
                node_address=self.protocolHandler.getNodeAddress(node_info['nodeDefId'])
            cls = globals()[node_class]
            node = cls(self.poly, self.protocolHandler, node_info['primaryNode'], node_address, node_info['name'])
            if node is None:
                LOGGER.error(f'invalid noddef id ...')
                return False
            else:
                node_r = self.poly.addNode(node)
                if node_r:
                    node_r.setProtocolHandler(self.protocolHandler)
                    self.protocolHandler.nodeAdded(node_r)
                    return True
                LOGGER.error("failed adding node ... ") 
                return False
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    def addNodeDoneHandler(self, node):
        try:
            if node['nodeDefId'] == self.id:
                return True
            return self.protocolHandler.addNodeDone(node)

        except ValueError as err:
            LOGGER.error(str(x))
            return False

    def configDoneHandler(self):
        rc = False
        if self.oauthService:
            # First check if user has authenticated
            try:
                self.oauthService.getAccessToken()
                # If getAccessToken did raise an exception, then proceed with device discovery
                rc = self.protocolHandler.configDone()

            except ValueError as err:
                LOGGER.warning('Access token is not yet available. Please authenticate.')
                polyglot.Notices['auth'] = 'Please initiate authentication using the Authenticate Buttion'
                return False
        with self.configDone:
            self.configDoneAlready = True
            self.configDone.notifyAll()
        return rc



    def customNSHandler(self, key, data):
        if key == 'oauth':
            # This provides the oAuth config (key='oauth') and saved oAuth tokens (key='oauthTokens))
            if not self.oauthService:
                return 
            try:
                self.oauthService.customNsHandler(key, data)
            except Exception as ex:
                LOGGER.error(ex)
        else:
            self.protocolHandler.customParamHandler(key, data)

    def oauthHandler(self, token):
        if not self.oauthService:
            return 
        # This provides the oAuth config (key='oauth') and saved oAuth tokens (key='oauthTokens))
        try:
            self.oauthService.oauthHandler(token)
        except Exception as ex:
            LOGGER.error(ex)

    def callOAuthApi(self, method='GET', url=None, params=None, body=None)->bool:
        if not self.oauthService:
            return False

        return self.oauthService(method, url, params, body)

    def customDataHandler(self, data):
        try:
            self.protocolHandler.customData(data)
        except Exception as ex:
            LOGGER.error(ex)
    
    def updateStatus(self, value, force: bool):
        return self.setDriver("ST", value, 2, force)

    def getStatus(self):
        return self.getDriver("ST")

    def discover(self, command):
        return self.protocolHandler.discover()

    def query(self, command):
        nodes = self.poly.getNodes()
        if nodes is None or len(nodes) == 0:
            return True
        for n in nodes:
            node = nodes[n]
            if node is None:
                continue
            else:
                node.query()

    ###
    # This is a list of commands that were defined in the nodedef
    ###
    commands = {'discover': discover, 'x_query': query}

