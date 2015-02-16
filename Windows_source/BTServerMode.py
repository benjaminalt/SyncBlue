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

from bluetooth import *

def launch_server():
    server_sock=BluetoothSocket( RFCOMM )
    print "Socket made..."
    server_sock.bind(("",PORT_ANY))
    print "Socket bound..."
    server_sock.listen(1)
    print "Socket listened..."
    port = server_sock.getsockname()[1]
    print "Port discovered..."

    advertise(server_sock)

    print "Connection successful."
    print "Disconnecting..."
    server_sock.close()
    client_sock.close()

def advertise(server_sock):
    advertise_service( server_sock, "BTSync",
                       service_id = "1106",
                       service_classes = [ "1106", SERIAL_PORT_CLASS ],
                       profiles = [ SERIAL_PORT_PROFILE ],
                       protocols = [ OBEX_UUID ]
                       )
    print("Waiting for connection on RFCOMM")

    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)
    return