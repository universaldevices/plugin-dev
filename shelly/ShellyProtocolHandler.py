
import udi_interface, os, sys, json, time, ipaddress
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom


ShellyTypeToNodeDef={
    'ShellyPlusWDUS':'sdimmer',
    'shelly1pmminig3':'sswitch'
}

class ShellyDeviceInfo(dict):
    '''
        Holds type/ip/port/host information for a Shelly device
        endpoint
                    dev_info={
                        'dev_address': dev_address,
                        'dev_type':dev_type,
                        'nodedef_id':nodedef_id, 
                        'ip':ip,
                        'port':result['port'],
                        'host':result['host'],
                    }

    '''

    def getDeviceAddress(self):
        try:
            return self['dev_address']
        except:
            return None

    def setDeviceAddress(self, address:str):
        try:
            self['dev_address']=address
        except:
            return None


    def getDeviceType(self):
        try:
            return self['dev_type']
        except:
            return None

    def setDeviceType(self, type:str):
        try:
            self['dev_type']=type
        except:
            return None

    def setNodeDefId(self, nodedef_id):
        try:
            self['nodedef_id']=nodedef_id
        except:
            return None

    def getIp(self):
        try:
            return self['ip']
        except:
            return None

    def setIp(self, ip:str):
        try:
            self['ip']=ip
        except:
            return None

    def getPort(self):
        try:
            return self['port']
        except:
            return None

    def setPort(self, port:int):
        try:
            self['port']=port
        except:
            return None

    def getHost(self):
        try:
            return self['host']
        except:
            return None

    def setHost(self, host):
        try:
            self['host']=host
        except:
            return None


class ShellyProtocolHandler:
    ##
    #Implementation and Protocol Handler class
    ##

    ##
    #The plugin has all the information that's stored in the json file.
    #The controller allows you to communicate with the underlying system (PG3).
    #

    def __init__(self, plugin):
        self.plugin = plugin
        self.deviceMap = None
        ### In case you want to have a mapping of nodes, you can use something like this
        #self.nodes = {}
        ### See nodeAdded and nodeRemoved
        ###

    def setController(self, controller):
        self.controller = controller
        self.deviceMap = self.createCustomParam('dev_map') 

    ####
    #  You need to implement these methods!
    ####

    ####
    # MANDATORY
    # This method is called by IoX to set a property
    # in the node/device or service
    ####
    def setProperty(self, node, property_id, value):
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'setProperty {property_id} failed .... ')
            return False
    
    ####
    # MANDATORY
    # This method is called by IoX to query a property
    # in the node/device or service. Return the actual 
    # value
    ####
    def queryProperty(self, node, property_id):
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'queryProperty {property_id} failed .... ')
            return False

    ####
    # MANDATORY if and only if you have commands
    # This method is called by IoX to send a command 
    # to the node/device or service
    ####
    def processCommand(self, node, command_name, **kwargs):
        try:
            #michel
            address=node.address
            dev_info = self.deviceMap[address]
            if not dev_info:
                LOGGER.error(f"Couldn't find device info for {address}") 
                return False

            LOGGER.info(f"Processing command {command_name}") 
            if kwargs != None:
                for key, value in kwargs.items():
                    LOGGER.info(f"-param: {key}: {value}")
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # MANDATORY if and only if you have commands
    # This method is called at start so that you can do whatever initialization
    # you need. If you return false, the status of the controller node shows 
    # disconnected. So, make sure you return the correct status.
    ####
    def start(self)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'start failed .... ')
            LOGGER.error(str(ex))
            return False

#michel
    def addNode(self, address:str, nodeDefId:str, name:str ):
        try:
            return self.controller.addNode(address, nodeDefId, name, self.controller.id)
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

#end michel see below too; it should not be mandatory

    ####
    # MANDATORY #michel, this should not be mandatory 
    # This method is called in order to get a unique address for your newly created node
    # for the given nodedef_id
    ####
    def getNodeAddress(self, nodedef_id):
        try:
            #do any mapping you wish. 
            return nodedef_id
        except Exception as ex:
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


    ####
    # This method is called by IoX to discover  
    # nodes/devices or service
    ####
    def discover(self)->bool:
        try:
            self.searchForDevicesUsingMDNS("http", None, "tcp")
            return True
        except Exception as ex:
            LOGGER.error(f'discover failed .... ')
            return False


    ####
    # Notification methods
    ####

    ####
    # This method is called when a new node as been added to the system.
    ####
    def nodeAdded(self, node):
        try:
            ###You can store your nodes in a dictionary for mapping or otherwise such as
            #if node == None:
            #   return False
            #self.nodes[node.address] = node
            ###
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called when a new node as been removed from the system
    ####
    def nodeRemoved(self, node)->bool:
        try:
            ###if you stored your nodes a dictionary, delete them 
            #if node == None:
            #   return False
            #del self.nodes[node.address]
            ###
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
            return True
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
            pass
            ###copy files to your desired directory, something like this:
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
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'process param failed .... ')
            return False

    ###
    # Creates a user defined/custom parameter for key/value pairs of your own and stores in the 
    # database. Whenever a key is updated the customParamHandler (below) is called with the 
    # key and its updated value. example:
    # myKey = self.createCustomParam('myKey')
    # self.updateCustomParam(myKey, "my value" )
    ###
    def createCustomParam(self, key):
        try:
            return Custom(self.controller.poly, key)
        except Exception as ex:
            LOGGER.error(f'create custom param failed ...')
            return None

    ###
    # Updates a user defined param. Whenever this method is called, customParamHandler is called
    # with the updated values.
    ###
    def updateCustomParam(self, key:Custom, value:str):
        try:
            key = value
        except Exception as ex:
            LOGGER.error(f'failed updating custom param ...' )


    ####
    # This method is called when a custom value (key/value) pair that's stored in the 
    # database is changed. You can use this method to manage custom parameters of your own
    # in the database.
    ####
    #michel
    def customParamHandler(self, key, value):
        try:
            if key == 'dev_map':
                self.deviceMap=value
            return True
        except Exception as ex:
            LOGGER.error(f'process custom param failed .... ')
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
        return self.controller.poly.getNode(address)

    ###
    # Call this method to update a property for a node.
    # The plugin already creates an implementation for you such that you can 
    # call something like updateHeatSetpoint(). This said, however, for dynamically
    # generated code/classes, you might not actually know the method names. In those
    # cases, you can use this method instead.
    # You can use the text just as an arbitrary/freeform text that is displayed as is
    # in the clients without any processing.
    ###
    def updateProperty(self, node_addr:str, property_id:str, value, force:bool, text:str=None):
        try:
            node = self.getNode(node_addr)
            if node == None:
                LOGGER.error(f"Update property failed for {node_address}")
                return False
            return node.setDriver(property_id, value, force=force, text=text)
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ###
    # If your plugin is an OAuth client, use this method to call APIs that 
    # automatically include all the tokens for authorization and authentication 
    ###
    def callOAuthApi(self, method='GET', url=None, params=None, body=None)->bool:
        return self.controller.callOAuthApi(method, url, params, body)


    ###
    # Device Discovery
    ###

    ##
    # You can search the network using mDNS. To do so, call this method
    # type : string = is the type of device you are looking for. If None, then everything
    # subtypes : string = is a list of subtypes [string] you are looking for. If None, then everything
    # protocol : string = either udp or tcp. If None, then everything
    # If any results, processMDNSResults method will be called with a list of devices and their info
    ##
    def searchForDevicesUsingMDNS(self, type:str, subtypes:str, protocol:str):
        self.controller.poly.bonjour(type, subtypes, protocol)

    ##
    # If search using mDNS is successful, this method is called with an array of devices. 
    ##
    def processMDNSResults(self, results:[]):
        try:
            for result in results:
                try:
                    if result['type'] != "http":
                        continue
                except:
                    continue
                ip:str=None
                dev_type:str=None
                dev_address:str=None
                fqdn:str = result['fqdn']
                if "shelly" in fqdn.lower():
                    addresses = result['addresses']
                    for address in addresses:
                        try:
                            if ipaddress.IPv4Address(address):
                                ip=address
                                break
                        except ipaddress.AddressValueError:
                            continue 
                    try:
                        dev_details=fqdn.split('-')
                        if len(dev_details) < 2:
                            continue
                        dev_type=dev_details[0]
                        dev_address=dev_details[1].split('.')[0].lower()
                    except:
                        continue
                    dev_info = ShellyDeviceInfo()
                    dev_info['dev_type']=dev_type
                    dev_info['dev_address']= dev_address
                    dev_info['nodedef_id']= ShellyTypeToNodeDef[dev_type]
                    dev_info['ip']=ip
                    dev_info['port']=result['port']
                    dev_info['host']=result['host']
                    if self.addNode(dev_address, dev_info['nodedef_id'], dev_type):
                        curr=self.deviceMap[dev_address]
                        if curr == None:
                            self.deviceMap[dev_address]=json.dumps(dev_info)
                        
            # Fill out this method based on the results
            return
        except Exception as ex:
            LOGGER.error(str(ex))

    