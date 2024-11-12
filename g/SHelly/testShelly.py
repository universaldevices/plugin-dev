from pyShelly import pyShelly
from pyShelly.dimmer import Dimmer
from pyShelly.light import LightWhite
from pyShelly.device import Device
import time
import requests

my_devices=[]

def block_added(block):
  print(block)
  my_devices.append(LightWhite(block,0,0,0))

shelly = pyShelly()
print("version:",shelly.version())

shelly.cb_block_added.append(block_added)
ip="192.168.1.113"
index="0"
shelly.add_device_by_ip(ip, 'ip-addr')  # this takes some time 
shelly.start()

#shelly.discover()

while True:
  if len(my_devices) == 0:
    print("wait")
    time.sleep(2)
  else:
    print("systems go")
    break 


#my_devices[0].turn_on()
#my_devices[0].
r = requests.get('http://192.168.1.113/rpc/Light.Set?id=0&on=true&brightness=50&transition_duration=20')

#http://192.168.1.113/rpc/Light.Set?id=0&on=true&brightness=50&transition_duration=20
#payload = dictionary part 
#IN CONCLUSION PYSHELLY FOR GEN1 USE REQUEST WITH UPDATED SHI FOR GEN 2

