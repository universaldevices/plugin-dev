
#!/usr/bin/env python3
"""
OpenADR Classes
Copyright (C) 2023  Universal Devices
"""

import xml.etree.cElementTree as ET
import xml.etree.ElementTree  as ElementTree

from typing import List


class Duration:
    element : ElementTree.Element = None

    def __init__(self, element : ElementTree.Element):
        self.element = element

    def getUnit(self) -> str:
        if self.element == None:
            return "n/a" 
        return self.element.attrib.get('unit')

    def __str__(self) -> str:
        if self.element == None:
            return "n/a" 
        return self.getDuration() + ' ' + self.getUnit()
    
    def getDuration(self) -> str:
        if self.element == None:
            return "n/a" 
        return self.element.text

class Tolerance:
    element : ElementTree.Element = None
    startAfter: Duration = None

    def __init__(self, element : ElementTree.Element):
        self.element = element
        if element == None:
            return
        self.startAfter = Duration (element.find('startAfter')) 

    def getStartAfter(self) -> Duration:
        return self.startAfter 


class Value:
    element : ElementTree.Element = None

    def __init__(self, element : ElementTree.Element):
        self.element = element

    def getType(self) -> str :
        if self.element == None:
            return None
        return self.element.attrib.get('type')

    def getUnit(self) -> str :
        if self.element == None:
            return None
        return self.element.attrib.get('unit')

    def getValue(self) -> str :
        if self.element == None:
            return None
        return self.element.text



class CurrentValue:
    element : ElementTree.Element = None
    value: Value = None

    def __init__(self, element : ElementTree.Element):
        self.element = element
        if element == None:
            return
        self.value = Value(element.find('value'))

    def getId(self) -> str :
        if self.element == None:
            return None
        return self.element.attrib.get('id')
        
    def getStatus(self) -> str :
        if self.element == None:
            return None
        return self.element.attrib.get('status')

    def getMode(self) -> str :
        if self.element == None:
            return None
        return self.element.find('mode').text


class Interval:
    element : ElementTree.Element = None

    value: Value = None
    duration: Duration = None

    def __init__(self, element : ElementTree.Element):
        self.element = element
        if element == None:
            return
        self.value = Value(element.find('value'))
        self.duration = Duration(element.find('duration'))
    
    def getId(self) -> str :
        if self.element == None:
            return None
        return self.element.attrib.get('id')
        
    def getStatus(self) -> str :
        if self.element == None:
            return None
        return self.element.attrib.get('status')

    def getMode(self) -> str :
        if self.element == None:
            return None
        return self.element.find('mode').text

    def getStartTime(self) -> str :
        if self.element == None:
            return None
        return self.element.find('startTime').text

    def getEndTime(self) -> str :
        if self.element == None:
            return None
        return self.element.find('endTime').text

    def getValue(self) -> Value:
        return self.value

    def getDuration(self) -> Duration:
        return self.duration


class EiEventSignal:
    element : ElementTree.Element = None
    intervals: Interval = []
    currentValue: CurrentValue
    
    def __init__(self, element : ElementTree.Element) -> None:
        self.element = element
        if element == None:
            return
        intervals : ElementTree.Element = element.find('intervals')
        if intervals != None:
            for interval in intervals.findall('interval'):
                self.intervals.append(Interval(interval))
        currValue = element.find('currentValue') 
        if currValue != None:
            self.currentValue = CurrentValue(currValue)

    def getId(self) -> str:
        if self.element == None:
            return None
        return self.element.attrib.get('id')

    def getName(self) -> str:
        if self.element == None:
            return None
        return self.element.attrib.get('name')

    def getType(self) -> str:
        if self.element == None:
            return None
        return self.element.attrib.get('type')

    def getCurrentValue(self) -> CurrentValue:
        return self.currentValue 



class EiActivePeriod:
    #notification_time: str
    #ramp_up_time: str
    #recovery_time: str
    duration: Duration = None
    tolerance: Tolerance = None
    element: ElementTree.Element = None

    def __init__(self, element:ElementTree.Element):
        self.element=element
        if element == None:
            return
        self.duration = Duration(element.find('duration'))
        self.tolerance = Tolerance(element.find('tolerance'))

    def getStartTime(self) -> str:
        if self.element == None:
            return None
        return self.element.attrib.get('startTime')

    def getActualStartTime(self) -> str:
        if self.element == None:
            return None
        return self.element.attrib.get('actualStartTime')

    def getEndTime(self) -> str:
        if self.element == None:
            return None
        return self.element.attrib.get('endTime')

    def getDuration(self) -> Duration:
        return self.duration
    


class EiEvent:
    #opt_id: int
    #opt_status: str
    #pending_opt_status: str
    #priority: int
    #mod_num: int
    #created_time: str
    #resp_req: str
    #is_test: bool
    activePeriod: EiActivePeriod = None
    
    eventSignals: EiEventSignal = []
    element: ElementTree.Element = None 

    def __init__(self, element):
        self.element=element
        if element == None:
            return 
        self.activePeriod = EiActivePeriod(element.find('eiActivePeriod'))
        signals : ElementTree.Element = element.find('eiEventSignals')
        if signals != None:
            for signal in signals.findall('eiEventSignal'):
                self.eventSignals.append(EiEventSignal(signal))

    def getRequestId(self) -> str:
        if self.element == None:
            return None
        return self.element.find("requestId").text

    def getId(self) -> str:
        if self.element == None:
            return None
        return self.element.attrib.get('id')
    
    def getStatus(self) -> str:
        if self.element == None:
            return None
        return self.element.attrib.get('status')

    def getMarketContext(self) -> str:
        if self.element == None:
            return None
        return self.element.find("marketContext").text

    def getActivePeriod(self) -> EiActivePeriod:
        return self.activePeriod

    def getEventSignals(self) -> [] :
        return self.eventSignals

    def getStartTime(self) -> str:
        return self.getActivePeriod().getActualStartTime()

    def getEndTime(self) -> str:
        return self.getActivePeriod().getEndTime()
    
    def getDuration(self) -> Duration:
        return self.getActivePeriod().getDuration()


class OpenADR:
    events: EiEvent = []

    def __init__(self) -> None:
        self.events = []

    def parse_xml(self, xml_string) -> bool:
        if xml_string == None:
            return False
        try:
            root = ET.fromstring(xml_string)
            for event in root.findall('eiEvent'):
                self.events.append(EiEvent(event))
            return True
        except Exception as e:
            return False

    def getEvents(self) -> []:
        return self.events 

#oadr_xml='<?xml version="1.0" encoding="UTF-8"?><eiEvents><eiEvent id="Event121123_202243_543_0" status="Active" optStatus="Opted In" pendingOptStatus="N/A" priority="0" modNum="1" createdTime="2023/12/11 08:22:45 PM" respReq="Always" isTest="false"><requestID>OadrDisReq121123_202245_560</requestID><marketContext>http://MarketContext1</marketContext><optId>0</optId><eiActivePeriod startTime="2023/12/11 08:21:43 PM" actualStartTime="2023/12/11 08:21:43 PM" endTime="2023/12/11 08:25:43 PM"><duration unit="seconds">240</duration><notificationTime>2023/12/11 08:20:43 PM</notificationTime><rampUpTime>2023/12/11 08:21:43 PM</rampUpTime><recoveryTime>2023/12/11 08:25:43 PM</recoveryTime><tolerance><startAfter unit="seconds">0</startAfter></tolerance></eiActivePeriod><eiEventSignals><eiEventSignal id="String" name="SIMPLE" type="level"><intervals><interval id="0" status="Completed"><value type="float" unit="N/A">1.000000</value><mode>Moderate</mode><duration unit="seconds">60</duration><startTime>2023/12/11 08:21:43 PM</startTime><endTime>2023/12/11 08:22:43 PM</endTime></interval><interval id="1" status="Completed"><value type="float" unit="N/A">1.000000</value><mode>Moderate</mode><duration unit="seconds">60</duration><startTime>2023/12/11 08:22:43 PM</startTime><endTime>2023/12/11 08:23:43 PM</endTime></interval><interval id="2" status="Active"><value type="float" unit="N/A">1.000000</value><mode>Moderate</mode><duration unit="seconds">120</duration><startTime>2023/12/11 08:23:43 PM</startTime><endTime>2023/12/11 08:25:43 PM</endTime></interval></intervals><currentValue id="N/A" status="Completed"><value type="float" unit="N/A">1.000000</value><mode>Moderate</mode></currentValue></eiEventSignal></eiEventSignals></eiEvent></eiEvents>'


#if __name__ == "__main__":
#    try:
#        oadr = OpenADR()
#        if oadr.parse_xml(oadr_xml):
#            print('good job')
#        else:
#            print('bad job')
#    except (KeyboardInterrupt, SystemExit):
#        sys.exit(0)