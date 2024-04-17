
import udi_interface

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class PluginMain:


    def stop(self):
        LOGGER.info(f"Stopping {self.name}")

    def poll(polltype):
        if 'shortPoll' in polltype:
            LOGGER.info("short poll")
        elif 'longPoll' in polltype:
            LOGGER.info("long poll")

    def addAllNodes(self):
        config = self.poly.getConfig()
        if config == None or config['nodes'] == None:
            self.valid_configuration=True
            return

        for node in config['nodes']:
            nodeDef = node['nodeDefId']
            if nodeDef == "DROPCTRL":
                continue
            address = node['address']
            primary = node['primaryNode']
            name = node['name']
            self.__addNode(nodeDef, address, name)
        LOGGER.info("Done adding nodes, ...")
        self.valid_configuration=True

    def __addNode(self, nodeDef:str, endDeviceAddress:str, devName:str):
        if nodeDef == None:
            return
        devNode = None
        ##Make the devNode

        if devNode == None:
            LOGGER.error(f"invalid nodedef id {nodeDef}")
            return
        self.poly.addNode(devNode)


if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start('1.0.4')
        PluginMain(polyglot)
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.info("exiting ..." )
        sys.exit(0)
