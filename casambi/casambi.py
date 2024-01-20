#!/usr/bin/env python3
"""
Polyglot v3 node server communicating with Casambi USB dongle 
Copyright (C) 2023  Universal Devices
"""
import udi_interface
import sys
import time
import serial
import threading
import xml.etree.cElementTree as ET
import oadr

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

    def noop(self, cmd):
        LOGGER.info('Got command: {}'.format(cmd))
        ### You can add commands here
        ### map them to the commands array below
        '''
        if 'cmd' in cmd:
            if cmd['cmd'] == 'DON':
                # check value
                if 'value' in cmd:
                    if cmd['value'] == '100':
                        ser.write(bytes(self.on_str, 'utf-8'))
                    else:
                        ser.write(bytes(self.off_str, 'utf-8'))
                else:
                    ser.write(bytes(self.on_str, 'utf-8'))
            elif cmd['cmd'] == 'DOF':
                ser.write(bytes(self.off_str, 'utf-8'))
        '''

    def query(self):
        QueryCasambi()
    
    #this is a list of supported commands
    commands = {
            'QUERY': query
            }

def addUpdateNode()->bool:
    global casambiNode
    global polyglot
    
    if polyglot.getNode("0"):
        LOGGER.info('CasambiNode already exists ...')
        return False
    
    if getInitSerial():
        casambiNode = CasambiNode(polyglot, '0', '0', 'Casambi DR USB')
        polyglot.addNode(casambiNode)
        polyglot.updateProfile()
        QueryCasambi()
#        getOADRInfo()


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

    addUpdateNode()


def poll(polltype):
    global ser

    if 'shortPoll' in polltype:
        addUpdateNode()
    #    getOADRInfo()


if __name__ == "__main__":
    try:
        # Start serial port listener
       # listen_thread = threading.Thread(target = listener)
       # listen_thread.daemon = True
       # listen_thread.start()

        polyglot = udi_interface.Interface([])
        polyglot.start('1.0.5')


        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.POLL, poll)

        # Start running
        polyglot.setCustomParamsDoc()
        polyglot.ready()
   #     polyglot.updateProfile()

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        


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
        self.p1=p1
        casambiNode.setDriver('GV9', p1, uom=103, force=True)
        return True

    def setP2(self,p2:int)->bool:
        casambiNode.setDriver('GV10', p2, uom=103, force=True)
        self.p2=p2
        return True

    def setP3(self,p3:int)->bool:
        self.p3=p3
        casambiNode.setDriver('GV11', p3, uom=103, force=True)
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


oadrSensor:OADRSensor=OADRSensor()        
casParams:CasambiParameters=CasambiParameters()        
pingOp = 1
pongOp = 2
initOp = 3
setManyChannelsOp = 13
getSensorValueOp = 0x18 #24
setSensorValueOp = 0x19 #25
setParamOp = 0x1A #26
paramCompOp = 0x1B #27



def getOADRInfo() -> oadr.OpenADR:
    oadrLock.acquire()
    oadr_xml = None
    isy = udi_interface.ISY(polyglot)
    if isy == None:
        LOGGER.error("no iox")
        oadrLock.release()
        return None
    try:
        oadr_xml = isy.cmd('/rest/oadr')
    except Exception as e:
        LOGGER.error(str(e))
        oadrLock.release()
        return None

    if oadr_xml == None:
        LOGGER.error("No oadr response")
        oadrLock.release()
        return None

    out = oadr.OpenADR()
    if out.parse_xml(oadr_xml) == False:
        out = None

    if out != None:
        events = out.getEvents()
        num_events = len(events) 
        if num_events > 0:
            oadrSensor.setStatus(1)
            print('Number of events {}', num_events)
            event :oadr.EiEvent
            for event in events:
                LOGGER.info('Start time: {}, end time: {}, duration: {}, status: {}'.format(event.getStartTime(), event.getEndTime(), event.getDuration(), event.getStatus()))
        else:
            oadrSensor.setStatus(0)



    oadrLock.release()
    out = None
    




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
    payload=[setSensorValueOp,payload[1],val]
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


def listener():
    global polyglot
    global ser

    LOGGER.info('Starting serial port listener')
    while (True):

        if getInitSerial() == False:
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

        if op == initOp:
            Init(payload)
        elif op == pingOp:
            Ping(payload)
        elif op == pongOp:
            Pong(payload)
        elif op == setManyChannelsOp:
            SetManyChannels(payload)
        elif op == getSensorValueOp:
            GetSensorValue(payload)
        elif op == setSensorValueOp:
            SetSensorValue(payload)
        elif op == setParamOp:
            SetParameter(payload)
        elif op == paramCompOp:
            SetParamComplete(payload)

        else:
            LOGGER.info('op is {}'.format(op))

        