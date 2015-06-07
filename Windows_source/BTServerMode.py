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
""" Server should support put, get, listdir, change dir, mkdir """

from bluetooth import *
from PyOBEX.common import OBEX_Version
from PyOBEX import server
from PyOBEX import requests
from PyOBEX import responses
from os.path import expanduser

class SyncBlueServer(server.Server):
    
    def __init__(self, address = ""):
        print "Creating server object..."
        self.address = address
        self.max_packet_length = 0xffff
        self.obex_version = OBEX_Version()
        self.request_handler = requests.RequestHandler()
        self.path = expanduser("~")                             # Default path: Home directory
        print "Server object created."

    # Re-implementation of start_service
    def start_service(self, port = None):
    
        if port is None:
            port = 0
        
        name = "SyncBlue Server"
        uuid = "F9EC7BC4-953C-11d2-984E-525400DC9E09"
        service_classes = [OBEX_FILETRANS_CLASS]
        service_profiles = [OBEX_FILETRANS_PROFILE]
        provider = ""
        description = "SyncBlue"
        protocols = [OBEX_UUID]
        
        # Returns a BluetoothSocket instance
        return server.Server.start_service(
            self, port, name, uuid, service_classes, service_profiles,
            provider, description, protocols
            )

    # Re-implementation of process_request: Called every time a request arrives
    def process_request(self, connection, request):
        
        if isinstance(request, requests.Connect):
            print "Received connection request."
            self.connect(connection, request)
        
        elif isinstance(request, requests.Disconnect):
            print "Received disconnection request."
            self.disconnect(connection, request)
        
        # Automatically rejects for now
        elif isinstance(request, requests.Put):
            print "Received put request."
            self.put(connection, request)
        
        # Doesn't exist yet
        elif isinstance(request, requests.Set_Path):
            print "Received setpath request."
            self.set_path(connection, request)
            print "New path: ", self.path

        else:
            self._reject(connection)

    # Handles put request
    def put(self, socket, request):
        # Read in the data, save it 
        header_data = request.read_data()
        print "Got something, here is what it contains:"
        for item in header_data:
            print item
        print "Sending CONTINUE response"
        self.send_response(socket, responses.Continue())                         # Check if response arrived
        # self._reject(socket)
    
        # Set the current directory
    def set_path(self, connection, request):
        pass

    def send_response(self, socket, response, header_list = []):
    
        ### TODO: This needs to be able to split messages that are longer than
        ### the maximum message length agreed with the other party.
        while header_list:
        
            if response.add_header(header_list[0], self._max_length()):
                header_list.pop(0)
            else:
                # Need to call send repeatedly until all data is sent!!!
                socket.send(response.encode())
                response.reset_headers()
        
        # Always send at least one request.                 WHAT IS THIS ABOUT?
        socket.send(response.encode())