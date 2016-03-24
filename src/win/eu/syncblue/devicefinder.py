"""
Copyright 2016 Benjamin Alt
benjamin_alt@outlook.com

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

################################################################################

Collection of static methods and a thread class for discovering bluetooth devices.

"""

import bluetooth
from PyQt4 import QtCore

class DeviceDiscoveryThread(QtCore.QThread):
    discoveryDone = QtCore.pyqtSignal(object)
    def run(self):
        availableDevices = get_available_devices()
        self.discoveryDone.emit(availableDevices)

# Return a dict {name: address} about the devices in range
def get_available_devices():
    try:
      availableDevices = {}
      addressList =  bluetooth.discover_devices()
      for address in addressList:
          availableDevices[bluetooth.lookup_name(address)] = address
      return availableDevices
    except IOError:
      print "No Bluetooth adapter detected. Please ensure Bluetooth is enabled on this device."
      return None

def find_by_name(name):
    target_address = None
    nearby_devices = bluetooth.discover_devices()
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
