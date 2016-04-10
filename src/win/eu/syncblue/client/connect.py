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

Collection of methods and a thread class for connecting to a Bluetooth device.

"""

from eu.syncblue.core.utils import debug
import devicefinder
from PyQt4 import QtCore
import bluetooth
import PyOBEX.client, PyOBEX.responses

# When run, attempts to connect to the specified device (see __init__) and emits
# connectDone signal with BrowserClient object on success or None on failure.
class ConnectThread(QtCore.QThread):

    connectDone = QtCore.pyqtSignal(object)

    def __init__(self, device):
        QtCore.QThread.__init__(self)
        self.device = device

    def run(self):
        try:
            print "Selected device: {}".format(self.device)
            # Find the services at the selected device
            deviceAddress = devicefinder.find_by_name(self.device)
            services = bluetooth.find_service(address = deviceAddress)
            selectedService = {}
            debug("Available services:")
            for item in services:
                debug(item["name"])
                if "service-classes" in item and "1106" in item["service-classes"]:
                    selectedService = item
            if len(selectedService) == 0:
                print "The device does not support OBEX File Transfer and/or is not running a SyncBlue server. Aborting..."
                self.connectDone.emit(None)
                return
            port = selectedService["port"]
            print "Trying to connect to port {}...".format(port)
            client = PyOBEX.client.BrowserClient(deviceAddress, port)
            conn = client.connect()
            if isinstance(conn, PyOBEX.responses.ConnectSuccess):
                print "Connected successfully."
                self.connectDone.emit(client)
            else:
                print "Connection failed."
                self.connectDone.emit(None)
        except IOError:
            self.connectDone.emit(None)
            return
