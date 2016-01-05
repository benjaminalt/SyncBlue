""" 
Copyright 2015 Benjamin Alt 
benjaminalt@arcor.de
    
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>. 

"""

import bluetooth

def find_by_name(name):
    target_address = None
    print "Looking up nearby devices..."
    nearby_devices = bluetooth.discover_devices()
    print "Looking for given name..."
    for bdaddr in nearby_devices:
        if name == bluetooth.lookup_name( bdaddr ):
            target_address = bdaddr
            break
    if target_address is not None:
        print "Found target bluetooth device with address", target_address
        return target_address
    else:
        print "Could not find target bluetooth device nearby."
        return False

def find_obex_port(addr):
    print "Looking for OBEX file transfer service..."
    service = bluetooth.find_service(address=addr, uuid="1106")
    if service:
        port = service[0]["port"]
        print "Obex file transfer uses port:", port
        return port
    else:
        print "No such service was detected."
        return

# Test client
if __name__ == "__main__":
    find_obex_port(find_by_name("Benjamin Alt's LG-D415"))