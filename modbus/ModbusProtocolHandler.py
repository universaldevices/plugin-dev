
import udi_interface, os, sys, json, time
import socket, ipaddress
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
import shutil
from iox_to_modbus import ModbusIoX
from udi_interface import LOG_HANDLER

class ModbusProtocolHandler:
    ##
    #Implementation and Protocol Handler class
    ##

    ##
    #The plugin has all the information that's stored in the json file.
    #The controller allows you to communicate with the underlying system (PG3).
    #

    def __init__(self, plugin):
        self.plugin = plugin
        self.host = None
        self.port = 502
        self.isValidConfig = False
        self.modbus = ModbusIoX(plugin)
        self.nodes = {}
        self.precisions = {}
        if plugin:
            try:
                self.precisions = (next(iter(plugin.nodedefs.getNodeDefs().values()))).getPrecisions()
            except Exception as ex:
                pass

    @staticmethod
    def isValidHost(host:str)->bool:
        try:
            # First, check if the string is a valid IP address
            ipaddress.ip_address(host)
            return host
        except ValueError:
            # If it's not a valid IP, try resolving it as a domain name
            try:
                resolved_ip = socket.gethostbyname(host)
                return host
            except socket.gaierror:
                return None

    @staticmethod
    def isValidPort(port):
        try:
            # Convert to integer in case the input is a string
            port = int(port)
            # Check if the port number is within the valid range
            if 0 <= port <= 65535:
                return port
            else:
                return -1
        except ValueError:
            # If conversion to integer fails, it's not a valid port
            return -1

    def setController(self, controller):
        self.controller = controller

    ####
    #  You need to implement these methods!
    ####

    ####
    # This method is called by IoX to set a property
    # in the node/device or service
    ####
    def setProperty(self, node, property_id, value):
        try:
            precision = self.precisions[propert_id]
            val = int(value)
            if precision > 0:
                mult = pow(10, precision)
                val = val * mult
            return self.modbus.setProperty(node.address, property_id, value)
        except Exception as ex:
            LOGGER.error(f'setProperty failed .... ')
            return False
    
    ####
    # This method is called by IoX to query a property
    # in the node/device or service
    ####
    def queryProperty(self, node, property_id):
        try:
            precision = self.precisions[property_id]

            val = self.modbus.queryProperty(node.address, property_id)
            if val != None and precision > 0:
                div = pow(10, precision)
                fval = round(float(val/div), precision)
                return fval

            return val
        except Exception as ex:
            LOGGER.error(f'queryProperty failed .... ')
            return False

    ####
    # This method is called by IoX to send a command 
    # to the node/device or service
    ####
    def processCommand(self, node, command_name, **kwargs):
        try:
            if command_name == 'Query':
                return node.queryAll()
            #for key, value in kwargs.items():
            #    print(f"{key}: {value}")
            return False
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # MANDATORY 
    # This method is called in order to get a unique address for your newly created node
    # for the given nodedef_id
    ####
    def getNodeAddress(self, nodedef_id):
        try:
            return nodedef_id
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called at start so that you can do whatever initialization
    # you need. If you return false, the status of the controller node shows 
    # disconnected. So, make sure you return the correct status.
    ####
    def start(self)->bool:
        try:
            if not self.isValidConfig:
                self.setNotices('host','Please provide the host/port in the configuration tab')
                return False

            return self.modbus.connect(self.host, self.port) 
        except Exception as ex:
            LOGGER.error(f'start failed .... ')
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called at stop so that you can do whatever cleaning up 
    # that's necessary. The result is not checked so make sure everything is 
    # cleaned up
    ####
    def stop(self)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'discover failed .... ')
            return False


    # This method is called by IoX to discover  
    # nodes/devices or service
    ####
    def discover(self)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'discover failed .... ')
            return False


    ####
    # Notification methods
    ####

    ####
    # This method is called when a new node as been added to the system
    ####
    def nodeAdded(self, node):
        try:
            if node == None:
                return False
            self.nodes[node.address] = node
            node.queryAll()
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called when a new node as been removed from the system
    ####
    def nodeRemoved(self, node)->bool:
        try:
            if node == None:
                return False
            del self.nodes[node.address]
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    #This method is called upon start and gives you all the configuration parameters
    #used to initialize this plugin including the store, version, etc.
    ####
    def processConfig(self, config):
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called with the configuration is done. This is rarely used as its main function is to facilitate 
    ####
    def configDone(self)->bool:
        try:
            return self.isValidConfig
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called with custom data. Rarely used ...  
    ####
    def customData(self, data)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called when adding a node to the system is completed successfully. Make sure you use isinstance
    # to ensure it's your node and then do any additional processing necessary.
    # oauth
    ####
    def addNodeDone(self, node)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called when files are uplaoded. The path is the directory to which you can find the files
    # Do whatever you need with the files because they will be removed once you are done.
    ####
    def filesUploaded(self, path:str)->bool:
        try:
            for filename in os.listdir(path):
                pass
                ###copy files, something like this:
                #file_path = os.path.join(path, filename)
                #if os.path.isfile(file_path):
                #    dest_path = os.path.join('./', filename)
                #    shutil.copy(file_path, dest_path)
                ###
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called at every short poll interval. The result is not checked
    ####
    def shortPoll(self)->bool:
        try:
            for _, node in self.nodes.items():
                node.queryAll()
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called at every long poll interval. The result is not checked
    ####
    def longPoll(self)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called with the custom parameters provided by the user.
    # It is a dictionary so you get the parameter name/key and the value. e.g.
    # params['path']
    ####
    def processParams(self, params:Custom)->bool:
        self.isValidConfig=False
        try:
            self.host=self.isValidHost(params['host'])
            self.port=self.isValidPort(params['port'])
            if self.host == None or self.port < 0:
                self.hostPortNotice()
                return False

            self.isValidConfig=True
            self.clearNotices()
            return True
        except Exception as ex:
            pass
        
        self.hostPortNotice()
        return False

    ###
    # Convenient methods to access the system
    ###

    ###
    # Call this method to remove the blue ribbon that requests the attention of the user
    ###
    def clearNotices(self):
        self.controller.poly.Notices.clear()

    ###
    # Call this method to add a blue ribbon with notice for the customer to take action
    # This is a dictionary. So, you would need to provide the key (i.e. the parameter's name)
    # And a string that will be displayed in the ribbon
    ###
    def setNotices(self, key:str, notice:str) :
        if key == None or notice == None:
            LOGGER.error("setNotices requires both the key and the notice.")
            return
        self.controller.poly.Notices[key]=notice

    ###
    # Call this method to get a node and then call its methods for updating
    # their state in IoX. Take a look at the class that implements this node
    # it's always a good idea to use isinstance to make sure you are dealing 
    # with the correct node
    # The address is the address of the node.
    ###
    def getNode(self, address:str):
        return self.controller.poly.getNode()

    ###
    # If your plugin is an OAuth client, use this method to call APIs that 
    # automatically include all the tokens for authorization and authentication 
    ###
    def callOAuthApi(self, method='GET', url=None, params=None, body=None)->bool:
        return self.controller.callOAuthApi(method, url, params, body)

    def hostPortNotice(self):
        self.setNotices('host','Please provide the host/port in the configuration tab')
    