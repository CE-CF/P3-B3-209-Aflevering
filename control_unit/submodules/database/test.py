
import time


def redefine_mac_address(data):
    new_mac = ''
    mac_chop = data.split(':')
    for x in mac_chop:
        new_mac = new_mac + x
    
    return new_mac

start = time.time()
print(redefine_mac_address('00:1A:C2:7B:00:50'))

print(redefine_mac_address('G7:1A:Y2:4T:80:40'))
stop = time.time()

print(stop-start)