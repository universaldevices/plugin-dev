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

class RelayNode(udi_interface.Node):
    id = 'relay'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 51},
            ]

    def __init__(self, polyglot, primary, address, name, ser):
        super(RelayNode, self).__init__(polyglot, primary, address, name)
        self.ser = ser

        try:
            #relay_id = bytes([int(address[2:])])

            self.on_str = 'AT+CH' + address[2:] + '=1'
            self.off_str = 'AT+CH' + address[2:] + '=0'

        except Exception as e:
            LOGGER.error('Failed to create on/off command strings: {}'.format(str(e)))


    def update(self, state):
        if state == '1':
            self.setDriver('ST', 100, uom=51, force=True)
        else:
            self.setDriver('ST', 0, uom=51, force=True)

    def noop(self, cmd):
        LOGGER.info('Got command: {}'.format(cmd))
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

    def query(self):
        ser.write(bytes('AT+CH1=?', 'utf-8')) # request status update

    commands = {
            'DON': noop,
            'DOF': noop,
            'QUERY': query
            }

'''
Read the user entered custom parameters. This should only be the serial
port.
'''

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


def getInitSerial():
    global polyglot
    global ser
    global serial_port 

    lock.acquire()
    if ser == None:
        try:
            ser = serial.Serial(serial_port, 115200, timeout=5)
            if ser.isOpen() == False: 
                ser.open()

            # SH-UR01A has only single relay
            node = RelayNode(polyglot, 'ch1', 'ch1', 'Relay 1', ser)
            polyglot.addNode(node)

            LOGGER.info('Have valid serial port, querying board.')
            LOGGER.info('Writing INIT')
            init = [1,3,0]
            ser.write(bytearray(init)) # force status request
            ping = [1,1]
            ser.write(bytearray(ping))
        except Exception as e:
            processSerialError(e)
            lock.release()
            return None
    else:
        if ser.isOpen():
            lock.release()
            return ser
    lock.release()
    return None


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

    if getInitSerial() != None:
        getOADRInfo()

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
            print('Number of events {}', num_events)
            event :oadr.EiEvent
            for event in events:
                LOGGER.info('Start time: {}, end time: {}, duration: {}, status: {}'.format(event.getStartTime(), event.getEndTime(), event.getDuration(), event.getStatus()))



    oadrLock.release()
    out = None
    

def poll(polltype):
    global ser

    if 'shortPoll' in polltype:
        getOADRInfo()
        if getInitSerial() != None:
            ping = [1,1] 
            try:
                ser.write(bytearray(ping))
            except Exception as e:
                processSerialError(e)
               # ser.write(bytes('GetParameter', 'utf-8')) # request status update
               # ser.write(bytes('GetSensor', 'utf-8')) # request status update
           # ser.write(bytes('AT+CH1=?', 'utf-8')) # request status update

def Init(payload):
    LOGGER.info('Init')

def Ping(payload):
    LOGGER.info('Ping')

def Pong(payload):
    LOGGER.info('Pong')

def SetManyChannels(payload):
    LOGGER.info('SetManyChannels')

def GetSensorValue(payload):
    LOGGER.info('GetSensorValue')

def SetSensorValue(payload):
    LOGGER.info('SetSensorValue')


def listener():
    global polyglot
    global ser

    pingOp = 1
    pongOp = 2
    initOp = 3
    setManyChannelsOp = 13
    getSensorValueOp = 24
    setSensorValueOp = 25

    LOGGER.info('Starting serial port listener')
    while (True):

        if getInitSerial() == None:
            time.sleep(10)
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
        else:
            LOGGER.info('op is {}'.format(op))

        
        #status = ser.readline().decode('utf-8')
        # status looks like: OK+CH1=0
        #LOGGER.info('incoming: {}'.format(status))

def oldCrap(): 
        try: 
            if status.startswith('OK'):
                status = status.split('+')[1]

            (channel, state) = status.split('=')
            address = channel.lower()

            if polyglot.getNode(address):
                LOGGER.info('Updatiung {} status to {}'.format(address, state.rstrip()))
                polyglot.getNode(address).update(state.rstrip())
            else:
                name = 'Relay-{}'.format(channel)
                LOGGER.info('Adding new node for channel {}'.format(channel))
                node = RelayNode(polyglot, address, address, name, ser)
                polyglot.addNode(node)
                node.update(state.rstrip())

        except Exception as e:
            LOGGER.error('Error parsing relay status: {}'.format(str(e)))
        




if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start('1.0.4')


        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.POLL, poll)

        # Start running
        polyglot.ready()
        polyglot.setCustomParamsDoc()
        polyglot.updateProfile()

        # Start serial port listener
        listen_thread = threading.Thread(target = listener)
        listen_thread.daemon = True
        listen_thread.start()

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

