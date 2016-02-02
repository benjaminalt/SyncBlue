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
from PyOBEX import headers
import serverutils as utils
import os, sys

# Reimplements PyOBEX.server.Server
class SyncBlueServer(server.Server):

    # Reimplementation of initializer (mainly for logging)
    def __init__(self, address = ""):
        print "Creating server object..."
        self.address = address
        self.max_packet_length = 0xffff
        self.obex_version = OBEX_Version()
        self.request_handler = requests.RequestHandler()
        self.path = os.path.expanduser("~")                         # Default path: Home directory
        print "Server object created."

    # Re-implementation of start_service that calls original implementation with parameters.
    # Returns a BluetoothSocket instance.
    # Side-effects: Advertises the service. Starts the server.
    def start_service(self, port = 0):

        name = "SyncBlue Server"
        uuid = "F9EC7BC4-953C-11d2-984E-525400DC9E09"
        service_classes = [OBEX_FILETRANS_CLASS]
        service_profiles = [OBEX_FILETRANS_PROFILE]
        provider = ""
        description = "SyncBlue"
        protocols = [OBEX_UUID]

        # Starts the server and returns a BluetoothSocket instance
        socket = server.Server.start_service(
            self, port, name, uuid, service_classes, service_profiles,
            provider, description, protocols
            )
        print "Before self.serve..."
        sys.stdout.flush()
        self.serve(socket)
        return socket

    # Re-implementation of process_request: Called every time a request arrives
    def process_request(self, connection, request):

        print(request)

        if isinstance(request, requests.Connect):
            print "Received connection request."
            self.connect(connection, request)

        elif isinstance(request, requests.Disconnect):
            print "Received disconnection request."
            self.disconnect(connection, request)

        elif isinstance(request, requests.Get_Final):
            print "Received get_final request."
            self.get_final(connection, request)

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

    # Handles Get_Final request ("listdir")
    def get_final(self, socket, request):
        # I need: folder/file name, size (bytes), user-perm ("R"/"RW"), modified
        # Existence of parent folder in xml-formatted string
        xmlString = utils.get_files_xml(self.path)
        header = headers.Connection_ID()
        response = responses.Success(xmlString, header)
        self.send_response(socket, response)

        print "Get_final response sent successfully!"

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

        # Always send at least one request. SENDING RESPONSE INTO SOCKET
        socket.send(response.encode())
