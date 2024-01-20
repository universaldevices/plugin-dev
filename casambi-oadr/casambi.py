#!/usr/bin/env python3
"""
Polyglot v3 node server communicating with Casambi USB dongle 
Copyright (C) 2023  Universal Devices
"""

import os
current_path = os.environ['PATH']
ffprog_path='/usr/local/bin'
os.environ['PATH'] = f'{ffprog_path}:{current_path}'

import udi_interface
import sys
import time
import threading
import serial

LOGGER = udi_interface.LOGGER
polyglot = None

ser = None
serial_port = '/dev/pg3.casambi'
lock = threading.Lock()
oadrLock = threading.Lock()
isGetParamComplete=False
casambiNode=None

def processSerialError(e):
    global polyglot
    global ser
    if ser != None:
        if ser.isOpen():
            ser.close()
        ser = None
    polyglot.Notices.clear()
    LOGGER.error('Unable to open serial port-crap {}'.format(serial_port))
    LOGGER.error(str(e))
    polyglot.Notices['port'] = 'Unable to open serial port {}'.format(serial_port)

def QueryCasambi()->bool:
    global ser
    global isGetParamComplete
    if ser == None:
       LOGGER.ERROR("Serial port is not open") 
       return False
    init = [1,3,0]
    ser.write(bytearray(init)) # force status request
    getParams=[1,0x1d]
    isGetParamComplete=False
    ser.write(bytearray(getParams)) # force status request
    return True

def getInitSerial()->bool:
    global polyglot
    global ser
    global serial_port 
    global isGetParamComplete
    global casambiNode

    lock.acquire()
    if ser == None:
        try:
            isGetParamComplete=False
            ser = serial.Serial(serial_port, 115200, timeout=5)
            if ser.isOpen() == False: 
                ser.open()
        except Exception as e:
            processSerialError(e)
            if lock.locked():
                lock.release()
            return False
    else:
        if ser.isOpen():
            if lock.locked():
                lock.release()
            return True
    if lock.locked():
        lock.release()
    return ser.isOpen()

class CasambiNode(udi_interface.Node):
    id = 'casambi'
    drivers = [
            #oadr status
            {'driver': 'ST', 'value': 0, 'uom': 25},
            #oadr start time
            {'driver': 'GV1', 'value': 0, 'uom': 151},
            #oadr end time
            {'driver': 'GV2', 'value': 0, 'uom': 151},
            #oadr Mode
            {'driver': 'GV3', 'value': 0, 'uom': 25},
            #oadr Price
            {'driver': 'GV4', 'value': 0, 'uom': 103},
            #Cas Control Mode
            {'driver': 'GV5', 'value': 0, 'uom': 25},
            #Cas Level 1 
            {'driver': 'GV6', 'value': 0, 'uom': 51},
            #Cas Level 2 
            {'driver': 'GV7', 'value': 0, 'uom': 51},
            #Cas Level 3 
            {'driver': 'GV8', 'value': 0, 'uom': 51},
            #Cas Price 1 
            {'driver': 'GV9', 'value': 0, 'uom': 103},
            #Cas Price 2 
            {'driver': 'GV10', 'value': 0, 'uom': 103},
            #Cas Price 3 
            {'driver': 'GV11', 'value': 0, 'uom': 103},
            #Cas Shed Limit 
            {'driver': 'GV12', 'value': 0, 'uom': 51},
            ]

    def __init__(self, polyglot, primary, address, name):
        super(CasambiNode, self).__init__(polyglot, primary, address, name)

    def updateState(self, state, index):
        if state == 1:
            self.setDriver('ST', 1, uom=25, force=True)
            self.setDriver('GV0', index, uom=25, force=True)
        else:
            self.setDriver('ST', 0, uom=25, force=True)
            self.setDriver('GV0', 0, uom=25, force=True)

    def processCommand(self, cmd):
        LOGGER.info('Got command: {}'.format(cmd))
        if 'cmd' in cmd:
            if cmd['cmd'] == 'QUERY':
                QueryCasambi() 
            ## you can add more commands in the array and handle them here:
            '''
            elif cmd['cmd'] == 'TEST':
                do something here
            '''
               

    commands = {
            'QUERY': processCommand
            #test command
            #'TEST': test 
            }

def addUpdateNode(address)->bool:
    global casambiNode

    if address == None:
        address = "0"
    if polyglot.getNode(address):
        LOGGER.info('CasambiNode already exists ...')
        return False

    if getInitSerial():
        casambiNode = CasambiNode(polyglot, address, address, 'Casambi DR USB')
        polyglot.addNode(casambiNode)
        polyglot.updateProfile()
        QueryCasambi()
#        getOADRInfo()
        return True

'''
Read the user entered custom parameters. This should only be the serial
port.
'''
def parameterHandler(params):
    global polyglot
    global serial_port

    polyglot.Notices.clear()

    if params == None:
            polyglot.Notices['port'] = 'Using default serial port {}'.format(serial_port)
    elif 'serial port' in params:
        if params['serial port'] == '':
            polyglot.Notices['port'] = 'Using default serial port {}'.format(serial_port)
        else:
            serial_port = params['serial port']
            polyglot.Notices['port'] = 'Using serial port {}'.format(serial_port)
    else:
            polyglot.Notices['port'] = 'Using default serial port {}'.format(serial_port)

    addUpdateNode('0')

def poll(polltype):
    ''' 
    you can do things based on short/long polls as you will be called for each
    for now, we have nothing to do
    '''
   # if 'shortPoll' in polltype:
   #     LOGGER.info("short poll")
   # elif 'longPoll' in polltype:
   #     LOGGER.info("long poll")

class OADRSensor:

    _status:int = 0 
    _type:int = 0 #0 = Mode, 1 = Price
    _mode:int = 0 
    _level:int = 0 #0-255 for 0 to 100%
    _price:int = 0 #precision 2
    global ser
    
    def __init__(self):
        pass

    def setStatus(self, status:int)->bool:
        self._status=status
        return True
        
    def setType(self, itype:int)->bool:
        if itype !=0 and itype != 1:
            LOGGER.error("Type can only be 0 for Mode and 1 for Price")
            return False
        self._type=itype
        return True


    def setMode(self, mode:int)->bool:
        if mode < 0 or mode > 3:
            LOGGER.error("Mode can only be 0, 1, 2, and 3")
            return False
        self._mode = mode
        return True

    def setLevel(self, level:int)->bool:
        if level < 0 or level > 255:
            Logger.error('Level can only be between 0 and 255')
            return False
        self._level=level
        return True

    def setPrice(self, price:float, precision:int)->bool:
        self._price = int (price * (10^precision))
        return True

    def getStatus(self) -> int:
        return self._status

    def getType(self) -> int:
        return self._type

    def getMode(self) -> int:
        return self._mode

    def getLevel(self) -> int:
        return self._level

    def getPrice(self) -> int:
        return self._price

    def getValue(self, payload) -> int:
        if payload == None:
            return 0 
        if payload[1] == 0:
            return self.getStatus()
        elif payload[1] == 1:
            return self.getType()
        elif payload[1] == 2:
            return self.getMode()
        elif payload[1] == 3:
            return self.getLevel()
        elif payload[1] == 4:
            return self.getPrice()
        LOGGER.error("OADR Sensor does not have a {} attribute".format(payload[1]))
        return  0

'''
    OADR values coming from IoX
'''
class OADRSensor:

    _status:int = 0 
    _type:int = 0 #0 = Mode, 1 = Price
    _mode:int = 0 
    _level:int = 0 #0-255 for 0 to 100%
    _price:int = 0 #precision 2
    global ser
    
    def __init__(self):
        pass

    def setStatus(self, status:int)->bool:
        self._status=status
        return True
        
    def setType(self, itype:int)->bool:
        if itype !=0 and itype != 1:
            LOGGER.error("Type can only be 0 for Mode and 1 for Price")
            return False
        self._type=itype
        return True


    def setMode(self, mode:int)->bool:
        if mode < 0 or mode > 3:
            LOGGER.error("Mode can only be 0, 1, 2, and 3")
            return False
        self._mode = mode
        return True

    def setLevel(self, level:int)->bool:
        if level < 0 or level > 255:
            Logger.error('Level can only be between 0 and 255')
            return False
        self._level=level
        return True

    def setPrice(self, price:float, precision:int)->bool:
        self._price = int (price * (10^precision))
        return True

    def getStatus(self) -> int:
        return self._status

    def getType(self) -> int:
        return self._type

    def getMode(self) -> int:
        return self._mode

    def getLevel(self) -> int:
        return self._level

    def getPrice(self) -> int:
        return self._price

    def getValue(self, payload) -> int:
        if payload == None:
            return 0 
        if payload[1] == 0:
            return self.getStatus()
        elif payload[1] == 1:
            return self.getType()
        elif payload[1] == 2:
            return self.getMode()
        elif payload[1] == 3:
            return self.getLevel()
        elif payload[1] == 4:
            return self.getPrice()
        LOGGER.error("OADR Sensor does not have a {} attribute".format(payload[1]))
        return  0

'''
    This class defines Casambi Parameters
'''
class CasambiParameters:

    CONTROL_MODE_LEVEL          = 0
    CONTROL_MODE_PRICE          = 1
    CONTROL_MODE_LEVEL_N_PRICE  = 2

    controlMode:int = 0 
    l1:int = 0 
    l2:int = 0 
    l3:int = 0 
    p1:int = 0 
    p2:int = 0 
    p3:int = 0 
    loadShedLimit:int = 0

    def __init__(self):
        pass

    def setL1(self,l1:int)->bool:
        if l1 < 0 or l1 > 255:
            Logger.error('L1 can only be between 0 and 255')
            return False
        self.l1=l1
        casambiNode.setDriver('GV6', l1, uom=51, force=True)
        return True

    def setL2(self,l2:int)->bool:
        if l2 < 0 or l2 > 255:
            Logger.error('L2 can only be between 0 and 255')
            return False
        self.l2=l2
        casambiNode.setDriver('GV7', l2, uom=51, force=True)
        return True

    def setL3(self,l3:int)->bool:
        if l3 < 0 or l3 > 255:
            Logger.error('L3 can only be between 0 and 255')
            return False
        self.l3=l3
        casambiNode.setDriver('GV8', l3, uom=51, force=True)
        return True

    def setP1(self,p1:int)->bool:
        self.p1=p1/100
        casambiNode.setDriver('GV9', self.p1, uom=103, force=True)
        return True

    def setP2(self,p2:int)->bool:
        self.p2=p2/100
        casambiNode.setDriver('GV10', self.p2, uom=103, force=True)
        return True

    def setP3(self,p3:int)->bool:
        self.p3=p3/100
        casambiNode.setDriver('GV11', self.p3, uom=103, force=True)
        return True

    def setLoadShedLimit(self, loadShedLimit:int)->bool:
        self.loadShedLimit=loadShedLimit
        casambiNode.setDriver('GV12', loadShedLimit, uom=51, force=True)

    def setControlMode(self, controlMode:int)->bool:
        self.controlMode=controlMode
        casambiNode.setDriver('GV5', controlMode, uom=25, force=True)


    def getL1(self):
        return self.l1

    def getL2(self):
        return self.l2

    def getL3(self):
        return self.l3

    def getP1(self):
        return self.p1

    def getP2(self):
        return self.p2

    def getP3(self):
        return self.p3

    def getControlMode(self):
        return self.controlMode

    def isControlModeLevel(self):
        return self.controlMode == self.CONTROL_MODE_LEVEL

    def isControlModePrice(self):
        return self.controlMode == self.CONTROL_MODE_PRICE

    def isControlModeLevelAndPrice(self):
        return self.controlMode == self.CONTROL_MODE_LEVEL_N_PRICE

    def setValue(self, payload)->bool:
        if payload == None:
            Logger.error('payload is null')
            return False

        if payload[1] == 9:
            self.setControlMode(payload[2])
        elif payload[1] == 10:
            self.setL1(payload[2])
        elif payload[1] == 11:
            self.setL2(payload[2])
        elif payload[1] == 12:
            self.setL3(payload[2])
        elif payload[1] == 13:
            self.setP1(payload[2])
        elif payload[1] == 14:
            self.setP2(payload[2])
        elif payload[1] == 15:
            self.setP3(payload[2])
        return True

'''
    The following segment is all about handling serial data coming 
    from the serial port. As the data flows, Casambi Parameters are update
    accordingly.
'''
 
casParams:CasambiParameters=CasambiParameters()        
oadrSensor:OADRSensor=OADRSensor() 

#Some Casambi Constants
CAS_PING_OP = 1
CAS_PONG_OP = 2
CAS_INIT_OP = 3
CAS_SET_M_CHANNELS_OP = 13
CAS_GET_SENSOR_VAL_OP = 0x18 #24
CAS_SET_SENSOR_VAL_OP = 0x19 #25
CAS_SET_PARAM_OP = 0x1A #26
CAS_PARAM_COMP_OP = 0x1B #27


def Init(payload):
    LOGGER.info('Init')

def Ping(payload):
    LOGGER.info('Ping')

def Pong(payload):
    LOGGER.info('Pong')

def SetManyChannels(payload):
    LOGGER.info('SetManyChannels')

def GetSensorValue(payload)->bool:
    if ser == None or ser.isOpen()==False:
        return False
    val : int = oadrSensor.getValue(payload)
    LOGGER.info('GetSensorValue: {}'.format(val))
    payload=[CAS_SET_SENSOR_VAL_OP,payload[1],val]
    try:
        ser.write(bytearray(payload)) 
        return True
    except Exception as e:
        processSerialError(e)
        return False

def SetSensorValue(payload):
    LOGGER.info('SetSensorValue')

def SetParameter(payload):
    LOGGER.info('SetParameter')
    casParams.setValue(payload)

def SetParamComplete(payload):
    global isGetParamComplete
    isGetParamComplete=True


#listen to serial port and do things
def serial_port_listener():
    global polyglot
    global ser

    LOGGER.info('Starting serial port listener')
    while (True):

        if ser == None or ser.isOpen() == False:
            time.sleep(5)
            continue

        try:
            payload = None
            len = int.from_bytes(ser.read(),"big", signed=True)
            if len <= 0:
                continue

            payload = ser.read(len)
            LOGGER.info('payload len is {}'.format(len))

        except Exception as e:
            processSerialError(e)

        if payload == None:
            continue

        op = payload[0]

        if op == CAS_INIT_OP:
            Init(payload)
        elif op == CAS_PING_OP:
            Ping(payload)
        elif op == CAS_PONG_OP:
            Pong(payload)
        elif op == CAS_SET_M_CHANNELS_OP:
            SetManyChannels(payload)
        elif op == CAS_GET_SENSOR_VAL_OP:
            GetSensorValue(payload)
        elif op == CAS_SET_SENSOR_VAL_OP:
            SetSensorValue(payload)
        elif op == CAS_SET_PARAM_OP:
            SetParameter(payload)
        elif op == CAS_PARAM_COMP_OP:
            SetParamComplete(payload)

        else:
            LOGGER.info('op is {}'.format(op))



if __name__ == "__main__":
    try:
       # Start serial port listener
        listen_thread = threading.Thread(target = serial_port_listener)
        listen_thread.daemon = True
        listen_thread.start()


        polyglot = udi_interface.Interface([])
        polyglot.start('1.0.4')


        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.POLL, poll)

        # Start running
        polyglot.ready()
        polyglot.setCustomParamsDoc()

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

