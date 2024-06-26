#!/usr/bin/env python3
"""
Polyglot v3 node server communicating with Casambi USB dongle 
Copyright (C) 2023  Universal Devices
"""

import os
import udi_interface
import sys
import time
import threading
import serial
import xml.etree.cElementTree as ET
import oadr
import struct
import json

LOGGER = udi_interface.LOGGER
polyglot = None

ser = None
serial_port = '/dev/pg3.casambi'
lock = threading.Lock()
oadrLock = threading.Lock()
isGetParamComplete=False
casambiNode=None
isy=None

#some constants
#oadr status
CASOADR_PROPERTY_STATUS='ST'
#oadr start time
CASOADR_PROPERTY_START_TIME='GV1'
#oadr end time
CASOADR_PROPERTY_END_TIME='GV2'
#oadr Mode
CASOADR_PROPERTY_MODE='GV3'
#oadr Price
CASOADR_PROPERTY_PRICE='GV4'
#Cas Control Mode
CASOADR_PROPERTY_CTL_MODE='GV5'
#Cas Level 1 
CASOADR_PROPERTY_LEVEL_1='GV6'
#Cas Level 2 
CASOADR_PROPERTY_LEVEL_2='GV7'
#Cas Level 3 
CASOADR_PROPERTY_LEVEL_3='GV8'
#Cas Price 1 
CASOADR_PROPERTY_PRICE_1='GV9'
#Cas Price 2 
CASOADR_PROPERTY_PRICE_2='GV10'
#Cas Price 3 
CASOADR_PROPERTY_PRICE_3='GV11'
#Cas Shed Limit 
CASOADR_PROPERTY_SHEDLIMIT='GV12'
#OpenADR Testing
CASOADR_PROPERTY_TEST_OADR='GV13'

OADR_STATUS_INACTIVE:int        = 0
OADR_STATUS_PENDING:int         = 1
OADR_STATUS_ACTIVE:int          = 2

OADR_MODE_NORMAL:int            = 0
OADR_MODE_MODERATE:int          = 1
OADR_MODE_HIGH:int              = 2
OADR_MODE_SPECIAL:int           = 3

CONTROL_MODE_LEVEL:int          = 0
CONTROL_MODE_PRICE:int          = 1
CONTROL_MODE_LEVEL_N_PRICE:int  = 2

#Some Casambi Constants
CAS_PING_OP = 1
CAS_PONG_OP = 2
CAS_INIT_OP = 3
CAS_SET_CHANNEL_0_OP = 0x05
CAS_SET_M_CHANNELS_OP = 13
CAS_GET_SENSOR_VAL_OP = 0x18 #24
CAS_SET_SENSOR_VAL_OP = 0x19 #25
CAS_SET_PARAM_OP = 0x1A #26
CAS_PARAM_COMP_OP = 0x1B #27

#sensor tags
CAS_SENSOR_STATUS_TAG = 0x00
CAS_SENSOR_CTL_MODE_TAG = 0x01
CAS_SENSOR_MODE_TAG = 0x02
CAS_SENSOR_SHED_LEVEL_TAG = 0x03
CAS_SENSOR_PRICE_TAG = 0x04

#parameter tags
CAS_PARAM_CTL_MODE_TAG = 0x09
CAS_PARAM_L1_TAG = 0x0A #10
CAS_PARAM_L2_TAG = 0x0B #11
CAS_PARAM_L3_TAG = 0x0C #12
CAS_PARAM_P1_TAG = 0x0D #13
CAS_PARAM_P2_TAG = 0x0E #14
CAS_PARAM_P3_TAG = 0x0F #15

#periodic timeout
CAS_PERIODIC_TIMEOUT = 0x05 

def processSerialError(e):
    global polyglot
    global ser
    if ser != None:
        try:
            ser.close()
        except Exception as e:
            pass
        ser = None
    polyglot.Notices.clear()
    LOGGER.error('Unable to open serial port {}'.format(serial_port))
    LOGGER.error(str(e))
    polyglot.Notices['port'] = 'Unable to open serial port {}'.format(serial_port)

def QueryCasambi()->bool:
    global ser
    global isGetParamComplete
    try:
        isGetParamComplete=False
        init = [1,3,0]
        ser.write(bytearray(init)) # force status request
        getParams=[1,0x1d]
        ser.write(bytearray(getParams)) # force status request
    except Exception as e:
        processSerialError(e)
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
#    else:
#        if ser.isOpen():
#            if lock.locked():
#                lock.release()
            return True
    if lock.locked():
        lock.release()
    return ser.isOpen()

class CasambiNode(udi_interface.Node):
    #local variables to make it easier/faster (instead of using getDriver())
    ##oadr
    ##casambi
    id = 'casambi'
    drivers = [
            #oadr status
            {'driver': CASOADR_PROPERTY_STATUS, 'value': 0, 'uom': 25},
            #oadr start time
            {'driver': CASOADR_PROPERTY_START_TIME, 'value': "N/A", 'uom': 145},
            #oadr end time
            {'driver': CASOADR_PROPERTY_END_TIME, 'value': "N/A", 'uom': 145},
            #oadr Mode
            {'driver': CASOADR_PROPERTY_MODE, 'value': 0, 'uom': 25},
            #oadr Price
            {'driver': CASOADR_PROPERTY_PRICE, 'value': 0, 'uom': 103},
            #Cas Control Mode
            {'driver': CASOADR_PROPERTY_CTL_MODE, 'value': 0, 'uom': 25},
            #Cas Level 1 
            {'driver': CASOADR_PROPERTY_LEVEL_1, 'value': 0, 'uom': 51},
            #Cas Level 2 
            {'driver': CASOADR_PROPERTY_LEVEL_2, 'value': 0, 'uom': 51},
            #Cas Level 3 
            {'driver': CASOADR_PROPERTY_LEVEL_3, 'value': 0, 'uom': 51},
            #Cas Price 1 
            {'driver': CASOADR_PROPERTY_PRICE_1, 'value': 0, 'uom': 103},
            #Cas Price 2 
            {'driver': CASOADR_PROPERTY_PRICE_2, 'value': 0, 'uom': 103},
            #Cas Price 3 
            {'driver': CASOADR_PROPERTY_PRICE_3, 'value': 0, 'uom': 103},
            #Cas Shed Limit 
            {'driver': CASOADR_PROPERTY_SHEDLIMIT, 'value': 0, 'uom': 51},
            #OpenADR Test
            {'driver': CASOADR_PROPERTY_TEST_OADR, 'value': 0, 'uom': 25},
            ]

    def __init__(self, polyglot, primary, address, name):
        super(CasambiNode, self).__init__(polyglot, primary, address, name)
        self.bMode=False
        self.bPrice=False

    def clear(self, init:bool):
        self.bMode=False
        self.bPrice=False
        if init == True:
#            self.setDriver(CASOADR_PROPERTY_START_TIME, "N/A", 145, force=True)
#            self.setDriver(CASOADR_PROPERTY_END_TIME, "N/A", 145, force=True)
            self.setDriver(CASOADR_PROPERTY_STATUS, OADR_STATUS_INACTIVE, 25, force=True)
            self.setDriver(CASOADR_PROPERTY_MODE, OADR_MODE_NORMAL, 25, force=True)
            self.setDriver(CASOADR_PROPERTY_PRICE, 0.00, 25, force=True)
            self.setDriver(CASOADR_PROPERTY_CTL_MODE, CONTROL_MODE_LEVEL , 25, force=True)
            self.setDriver(CASOADR_PROPERTY_SHEDLIMIT, 0.00, uom=51, force=True)
            self.setDriver(CASOADR_PROPERTY_LEVEL_1, 0, uom=51, force=True)
            self.setDriver(CASOADR_PROPERTY_LEVEL_2, 0, uom=51, force=True)
            self.setDriver(CASOADR_PROPERTY_LEVEL_3, 0, uom=51, force=True)
            self.setDriver(CASOADR_PROPERTY_PRICE_1, 0.00, uom=51, force=True)
            self.setDriver(CASOADR_PROPERTY_PRICE_2, 0.00, uom=51, force=True)
            self.setDriver(CASOADR_PROPERTY_PRICE_3, 0.00, uom=51, force=True)
            self.setDriver(CASOADR_PROPERTY_TEST_OADR, 0, uom=25, force=True)



    def setStartTime(self, startTime:str):
        pass
#        if startTime == None:
#            self.setDriver(CASOADR_PROPERTY_START_TIME, "N/A", 145, force=False)
#        else:
#            self.setDriver(CASOADR_PROPERTY_START_TIME, startTime, 145, force=False)

    def setEndTime(self, endTime:str):
        pass
#        if endTime == None:
#            self.setDriver(CASOADR_PROPERTY_END_TIME, "N/A", 145, force=False)
#        else:
#            self.setDriver(CASOADR_PROPERTY_END_TIME, endTime, 145, force=False)

    def setDuration(self, duration:int):
        #for now, do nothing
        pass

    def setStatus(self, status:int, startTime:str, endTime:str, duration:int):
        self.setStartTime(startTime)
        self.setEndTime(endTime)
        self.setDuration(duration)

        if status == self.getStatus():
                return
        LOGGER.info('Start time: {}, end time: {}, duration: {}, status: {}'.format(startTime, endTime, duration, status))
        self.setDriver(CASOADR_PROPERTY_STATUS, status, 25, force=True)
        self.sendStatus()
        #doing nothing with duration

    def getStatus(self)-> int:
        try:
            return self.getDriver(CASOADR_PROPERTY_STATUS)
        except Exception as ex:
            return OADR_STATUS_INACTIVE 
        
    def setMode(self, mode:int)->bool:
        if mode < 0 or mode > 3:
            LOGGER.error("Mode can only be 0, 1, 2, and 3")
            return False
        self.bMode=True
        if self.getMode() == mode:
            return True
        self.setDriver(CASOADR_PROPERTY_MODE, mode, 25, force=True)
        self.sendMode()
        return True

    def getMode(self)->int:
        try:
            return self.getDriver(CASOADR_PROPERTY_MODE)
        except Exception as ex:
            return OADR_MODE_NORMAL

    def setMode_s(self, mode:str)->bool:
        if mode == None:
            return False
        if mode.lower() == "normal":
            return self.setMode(OADR_MODE_NORMAL)
        elif mode.lower() == "moderate":
            return self.setMode(OADR_MODE_MODERATE)
        elif mode.lower() == "high":
            return self.setMode(OADR_MODE_HIGH)
        elif mode.lower() == "special":
            return self.setMode(OADR_MODE_SPECIAL)
        return False

    def setPrice(self, price:float)->bool:
        if price == None:
            return False
        self.bPrice=True
        if self.getPrice() == price:
            return 
        self.setDriver(CASOADR_PROPERTY_PRICE, price, 25, force=True)
        self.sendPrice()
        return True

    def getPrice(self)->float:
        try:
            return self.getDriver(CASOADR_PROPERTY_PRICE)
        except Exception as ex:
            return 0.00

    def setLoadShedLimit(self, loadShedLimit:int)->bool:
        if loadShedLimit == self.getLoadShedLimit():
            LOGGER.debug("shed level has not changed ...")
            return
        self.setDriver(CASOADR_PROPERTY_SHEDLIMIT, loadShedLimit, uom=51, force=True)
        self.sendShedLevel()
        self.sendPeriodic()
        return True

    def getLoadShedLimit(self)->int:
        try:
            return self.getDriver(CASOADR_PROPERTY_SHEDLIMIT)
        except Exception as ex:
            return 0

    def setInactive(self):
        self.setStatus(OADR_STATUS_INACTIVE, None, None, 0)
        self.setMode_s("normal")
        self.setPrice(0)
        self.setLoadShedLimit(0)
        self.clear(False)

    def isMode(self)->bool:
        return self.bMode
    
    def isPrice(self)->bool:
        return self.bPrice

    def isTestingOpenADR(self)->bool:
        try:
            return self.getDriver(CASOADR_PROPERTY_TEST_OADR)
        except Exception as ex:
            return False
    
    def setTestingOpenADR(self, enable:int):
        self.setDriver(CASOADR_PROPERTY_TEST_OADR, enable, uom=25, force=True)
        if enable == 0:
            self.clear(True)
            if getInitSerial():
                QueryCasambi()

    def isActive(self)->bool:
        return self.getStatus() == OADR_STATUS_ACTIVE

    def setEvent(self, event:oadr.EiEvent): 
        if event == None:
            LOGGER.error("No event specified .... ")
            self.setInactive()
            return

        #self.clear(False) 
        status:int=OADR_STATUS_INACTIVE
        s_status = event.getStatus()
        if s_status == "Active":
            status=OADR_STATUS_ACTIVE
        elif s_status != "Inactive" and s_status != "Completed":
            status=OADR_STATUS_PENDING
        else:
            self.setInactive()
            return
        self.setStatus(status, event.getStartTime(), event.getEndTime(), event.getDuration())
    
        signals: oadr.EiEventSignal = []
        signals = event.getEventSignals()
        signal:oadr.EiEventSignal=None
        for signal in signals:
            if signal.isMode():
                self.setMode_s(signal.getCurrentValue().getMode())
            elif signal.isPrice():
                val:oadr.CurrentValue=signal.getCurrentValue();
                fval:float=val.getFloatValue()
                self.setPrice(signal.getCurrentValue().getFloatValue())
    

    ### Casambi Specific Parameters
    def setControlMode(self, controlMode:int)->bool:
        if controlMode !=CONTROL_MODE_LEVEL and controlMode != CONTROL_MODE_PRICE:
            LOGGER.error("Type can only be 0 for Mode and 1 for Price")
            controlMode=-1
            return False
        self.setDriver(CASOADR_PROPERTY_CTL_MODE, controlMode, 25, force=False)
        return True
    
    def getControlMode(self)->int:
        try:
            return self.getDriver(CASOADR_PROPERTY_CTL_MODE)
        except Exception as ex:
            return CONTROL_MODE_LEVEL

    def isControlMode_Mode(self)->bool:
        return self.getControlMode()==CONTROL_MODE_LEVEL
        
    def isControlMode_Price(self)->bool:
        return self.getControlMode()==CONTROL_MODE_PRICE
        
    def setL1(self,l1:int)->bool:
        if l1 < 0 or l1 > 255:
            Logger.error('L1 can only be between 0 and 255')
            return False
        self.setDriver(CASOADR_PROPERTY_LEVEL_1, l1, uom=51, force=False)
        return True

    def getL1(self)->int:
        try:
            return self.getDriver(CASOADR_PROPERTY_LEVEL_1)
        except Exception as ex:
            return 0 

    def setL2(self,l2:int)->bool:
        if l2 < 0 or l2 > 255:
            Logger.error('L2 can only be between 0 and 255')
            return False
        self.setDriver(CASOADR_PROPERTY_LEVEL_2, l2, uom=51, force=False)
        return True

    def getL2(self)->int:
        try:
            return self.getDriver(CASOADR_PROPERTY_LEVEL_2)
        except Exception as ex:
            return 0 

    def setL3(self,l3:int)->bool:
        if l3 < 0 or l3 > 255:
            Logger.error('L3 can only be between 0 and 255')
            return False
        self.setDriver(CASOADR_PROPERTY_LEVEL_3, l3, uom=51, force=False)
        return True

    def getL3(self)->int:
        try:
            return self.getDriver(CASOADR_PROPERTY_LEVEL_3)
        except Exception as ex:
            return 0 

    def setP1(self,p1:int)->bool:
        p1=p1/100
        self.setDriver(CASOADR_PROPERTY_PRICE_1, p1, uom=103, force=False)
        return True

    def getP1(self)->float:
        try:
            return self.getDriver(CASOADR_PROPERTY_PRICE_1)
        except Exception as ex:
            return 0.00 

    def setP2(self,p2:int)->bool:
        p2=p2/100
        self.setDriver(CASOADR_PROPERTY_PRICE_2, p2, uom=103, force=False)
        return True

    def getP2(self)->float:
        try:
            return self.getDriver(CASOADR_PROPERTY_PRICE_2)
        except Exception as ex:
            return 0.00 

    def setP3(self,p3:int)->bool:
        p3=p3/100
        self.setDriver(CASOADR_PROPERTY_PRICE_3, p3, uom=103, force=False)
        return True

    def getP3(self)->float:
        try:
            return self.getDriver(CASOADR_PROPERTY_PRICE_3)
        except Exception as ex:
            return 0.00 

    def _getSensorValue(self, tag):
        if tag == None:
            return 0 
        if tag == CAS_SENSOR_STATUS_TAG:
            status=self.getStatus()
            return struct.pack('<H', status)
        elif tag == CAS_SENSOR_CTL_MODE_TAG:
            controlMode=self.getControlMode()
            return struct.pack('<H', controlMode)
        elif tag == CAS_SENSOR_MODE_TAG:
            mode=self.getMode()
            return struct.pack('<H', mode)
        elif tag == CAS_SENSOR_SHED_LEVEL_TAG:
            shedLimit:int=int(self.getLoadShedLimit())
           # shedLimit=int(shedLimit*255/100)
            return struct.pack('<H', shedLimit)
        elif tag == CAS_SENSOR_PRICE_TAG:
            price:float=self.getPrice()
            price=int(round(price*1000))
            return struct.pack('<H', price)
            
        LOGGER.error("OADR Sensor does not have a {} attribute".format(tag))
        return  0

    def saveParameterValue(self, payload)->bool:
        if payload == None:
            Logger.error('payload is null')
            return False

        if payload[1] == CAS_PARAM_CTL_MODE_TAG:
            self.setControlMode(payload[2])
        elif payload[1] == CAS_PARAM_L1_TAG:
            self.setL1(payload[2])
        elif payload[1] == CAS_PARAM_L2_TAG:
            self.setL2(payload[2])
        elif payload[1] == CAS_PARAM_L3_TAG:
            self.setL3(payload[2])
        elif payload[1] == CAS_PARAM_P1_TAG:
            self.setP1(payload[2])
        elif payload[1] == CAS_PARAM_P2_TAG:
            self.setP2(payload[2])
        elif payload[1] == CAS_PARAM_P3_TAG:
            self.setP3(payload[2])
        return True

    def updateLoadShedLimit(self):
        if self.isActive() == False:
            self.setLoadShedLimit(0)
        elif self.isControlMode_Mode() and self.isMode():
            if self.getMode() == OADR_MODE_NORMAL:
                self.setLoadShedLimit(0)
            elif self.getMode() == OADR_MODE_MODERATE:
                self.setLoadShedLimit(self.getL1())
            elif self.getMode() == OADR_MODE_HIGH:
                self.setLoadShedLimit(self.getL2())
            elif self.getMode() == OADR_MODE_SPECIAL:
                self.setLoadShedLimit(self.getL3())
            else:
                LOGGER.error("mode is not valid {}".getMode())
        elif self.isControlMode_Price() and self.isPrice():
            price:float=self.getPrice()
            if price < self.getP1():
                self.setLoadShedLimit(0)
            elif price >= self.getP1() and price < self.getP2():
                self.setLoadShedLimit(self.getL1())
            elif price >= self.getP2() and price < self.getP3():
                self.setLoadShedLimit(self.getL2())
            elif price >= self.getP3():
                self.setLoadShedLimit(self.getL3())
        else:
            LOGGER.error("this combination is not supported: mode={}, control_mode={}".format(self.getMode(), self.getControlMode()))

    #respond to get sensor value
    def getSensorValue(self, payload)->bool:
        if ser == None or ser.isOpen()==False:
            return False
        return self._sendSensorValue(payload[1])

        #
        #val = self._getSensorValue(payload[1])
        #towrite_array=[0x02,CAS_SET_SENSOR_VAL_OP,payload[1]]
        #LOGGER.debug('getSensorValue: {} -> {}'.format(payload[1], val))
        #try:
        #    ser.write(bytearray(towrite_array))
        #    ser.write(val)
        #    return True
        #except Exception as e:
        #    lock.acquire()
        #    processSerialError(e)
        #    lock.release()
        #    return False

    #send sensor value to the dongle
    def _sendSensorValue(self, tag)->bool:
        if ser == None or ser.isOpen()==False:
            return False
        val = self._getSensorValue(tag)
        LOGGER.debug('sendSensorValue: {} -> {}'.format(tag, val))
        try:
            if tag == CAS_SENSOR_PRICE_TAG:
                towrite_array=[0x04,CAS_SET_SENSOR_VAL_OP,tag]
            else:
                towrite_array=[0x03,CAS_SET_SENSOR_VAL_OP,tag]
            
            ser.write(bytearray(towrite_array))
            ser.write(val)
            if tag == CAS_SENSOR_SHED_LEVEL_TAG:
                val:int = int(int.from_bytes(self._getSensorValue(CAS_SENSOR_SHED_LEVEL_TAG), byteorder='little')*255/100)
                shed=struct.pack('<H', val )
                towrite_array=[0x03,CAS_SET_CHANNEL_0_OP,tag]
                ser.write(bytearray(towrite_array))
                ser.write(shed)
            return True
        except Exception as e:
            lock.acquire()
            processSerialError(e)
            lock.release()
            return False

    def sendPeriodic(self):
        pass
        if ser == None or ser.isOpen()==False:
            return False
        LOGGER.debug("sending periodic load shed ... ")
        val:int = int(int.from_bytes(self._getSensorValue(CAS_SENSOR_SHED_LEVEL_TAG), byteorder='little')*255/100)
        shed=struct.pack('<H', val)
        try:
            towrite_array=[0x07,0x47,0x90,0xAC] 
            ser.write(bytearray(towrite_array))
            ser.write(shed)
            towrite_array=[CAS_PERIODIC_TIMEOUT,0x07,0x01]
            ser.write(bytearray(towrite_array))
        except Exception as e:
            lock.acquire()
            processSerialError(e)
            lock.release()

    def sendStatus(self)->bool:
        return self._sendSensorValue(CAS_SENSOR_STATUS_TAG)

    def sendControlMode(self)->bool:
        return self._sendSensorValue(CAS_SENSOR_CTL_MODE_TAG)

    def sendMode(self)->bool:
        return self._sendSensorValue(CAS_SENSOR_MODE_TAG)

    def sendShedLevel(self)->bool:
        return self._sendSensorValue(CAS_SENSOR_SHED_LEVEL_TAG)

    def sendPrice(self)->bool:
        return self._sendSensorValue(CAS_SENSOR_PRICE_TAG)
    
    def ping(self,payload):
        LOGGER.debug('Ping')

    def pong(self,payload):
        LOGGER.debug('Pong')

    def setManyChannels(self,payload):
        LOGGER.debug('SetManyChannels')

    def setSensorValue(self,payload):
        LOGGER.debug('SetSensorValue')

        
    def oadrPoll(self):
        oadrLock.acquire()
        global isGetParamComplete
        retry=0
        while not isGetParamComplete and retry < 5:
            retry+=1
            time.sleep(1)
            

        if isy == None:
            LOGGER.error("No iox instance available in oadrPoll")
            oadrLock.release()
            return None

        try:
            oadr_xml=None
            try:
                if self.isTestingOpenADR():
                    with open('./oadr.xml', 'r') as file:
                        oadr_xml = file.read()
                else:
                    oadr_xml = isy.cmd('/rest/oadr')
                if oadr_xml == None:
                    LOGGER.error("No oadr response")
                    oadrLock.release()
                    return None
            except Exception as ex:
                LOGGER.error(str(ex))

            oadr_p=oadr.OpenADR()
            if oadr_p.parse_xml(oadr_xml) == False:
                oadrLock.release()
                return None
            
            events = oadr_p.getEvents()
            num_events = len(events) 
            if num_events > 0:
                print('Number of events {}', num_events)
                activeEvent:oadr.EiEvent=None
                pendingEvent:oadr.EiEvent=None
                event:oadr.EiEvent=None
                for event in events:
                    if event.getStatus() == "Active":
                        if activeEvent == None:
                            activeEvent = event
                    elif event.getStatus() != "InActive":
                        if pendingEvent == None:
                            pendingEvent = event

                if activeEvent == None and pendingEvent == None:
                    self.setInactive() 
                elif activeEvent != None:
                    self.setEvent(event)
                elif pendingEvent != None:
                    self.setEvent(pendingEvent)
            else:
                self.setInactive()
            oadrLock.release()
        except Exception as e:
            #e.with_traceback()
            LOGGER.error(str(e))
            oadrLock.release()
        self.updateLoadShedLimit()

    ## you can add more commands in the array and handle them here:
    def processCommand(self, cmd):
        LOGGER.info('Got command: {}'.format(cmd))
        if 'cmd' in cmd:
            if cmd['cmd'] == 'QUERY':
                QueryCasambi() 
            if cmd['cmd'] == 'OPENADR_TEST':
                query = str(cmd['query']).replace("'","\"")
                jparam=json.loads(query)
                val=int(jparam['SET.uom25'])
                self.setTestingOpenADR(val)
    
    commands = {
            'QUERY': processCommand,
            'OPENADR_TEST':processCommand
            #test command
            #'TEST': test 
            }



def addUpdateNode(address)->bool:
    global casambiNode
    global isy
    global polyglot


    if casambiNode == None:
        if address == None:
            address = "0"
        casambiNode = CasambiNode(polyglot, address, address, 'Casambi DR USB')
        polyglot.addNode(casambiNode)
        polyglot.updateProfile()
        casambiNode.clear(True)
        if getInitSerial():
            QueryCasambi()
        else:
            return

    if isy == None:
        isy = udi_interface.ISY(polyglot)
        if isy == None:
            LOGGER.error("No iox instance available")

    if getInitSerial():
        casambiNode.oadrPoll()
        return True

'''
Read the user entered custom parameters. This should only be the serial
port.
'''
initCompleted:bool=False
initialPeriodicSent:bool=False
def parameterHandler(params):
    global polyglot
    global serial_port
    global initCompleted

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
    initCompleted=True

    ''' 
    you can do things based on short/long polls as you will be called for each
    for now, we have nothing to do
    '''
    # if 'shortPoll' in polltype:
    #     LOGGER.info("short poll")
    # elif 'longPoll' in polltype:
    #     LOGGER.info("long poll")
def poll(polltype):
    global initCompleted
    global initialPeriodicSent
    if 'shortPoll' in polltype:
        if initCompleted == False:
            return
        if lock.locked() : 
            return
        if oadrLock.locked():
            return
        addUpdateNode('0')
        if initialPeriodicSent==False:
            casambiNode.sendPeriodic()
            initialPeriodicSent=True
    elif 'longPoll' in polltype:
        casambiNode.sendPeriodic()

def Init(payload):
    LOGGER.debug('Init')

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
            LOGGER.debug('payload len is {}'.format(len))

        except Exception as e:
            lock.acquire()
            processSerialError(e)
            lock.release()

        if payload == None:
            continue

        op = payload[0]

        if op == CAS_INIT_OP:
            Init(payload)
        elif op == CAS_PING_OP:
            casambiNode.ping(payload)
        elif op == CAS_PONG_OP:
            casambiNode.pong(payload)
        elif op == CAS_SET_M_CHANNELS_OP:
            casambiNode.setManyChannels(payload)
        elif op == CAS_GET_SENSOR_VAL_OP:
            casambiNode.getSensorValue(payload)
        elif op == CAS_SET_SENSOR_VAL_OP:
            casambiNode.setSensorValue(payload)
        elif op == CAS_SET_PARAM_OP:
            casambiNode.saveParameterValue(payload)
        elif op == CAS_PARAM_COMP_OP:
            global isGetParamComplete
            isGetParamComplete=True
        else:
            LOGGER.debug('op is {}'.format(op))



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
        

