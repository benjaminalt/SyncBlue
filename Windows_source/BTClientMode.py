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
import BTDeviceFinder
import PyOBEX.client

# Test client
if __name__ == "__main__":
    name = "Benjamin Alt's LG-D415"
    address = BTDeviceFinder.find_by_name(name)
    port = BTDeviceFinder.find_obex_port(address)
    client = PyOBEX.client.BrowserClient(address, port)
    client.connect()
    client.setpath("Internal storage")
    response, data = client.listdir("")
    print "Response:", response
    print "Data:", data
    client.put("test.txt", "test test test")
    client.disconnect()
