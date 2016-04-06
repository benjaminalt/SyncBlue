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
import os, sys, shutil

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
    # Side-effects: Advertises the service.
    # TODO: Do this in own Thread
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
        return socket

    # Re-implementation of process_request: Called every time a request arrives
    def process_request(self, connection, request):

        print request
        for header in request.header_data:
            print header
            print header.decode()

        if isinstance(request, requests.Connect):
            print "Received connection request."
            self.connect(connection, request)

        elif isinstance(request, requests.Disconnect):
            print "Received disconnection request."
            self.disconnect(connection, request)

        elif isinstance(request, requests.Get_Final):
            print "Received get_final request."
            self.get_final(connection, request)

        elif isinstance(request, requests.Put_Final):
            print "Received put_final request."
            self.put_final(connection, request)

        elif isinstance(request, requests.Put):
            print "Received put request."
            self.put(connection, request)

        elif isinstance(request, requests.Set_Path):
            print "Received setpath request."
            self.set_path(connection, request)
            print "New path: ", self.path

        elif isinstance(request, requests.Get):
            print "Received get request."
            self.get(connection, request)

        else:
            self._reject(connection)

    # Handles Get_Final request ("listdir")
    def get_final(self, socket, request):
        xmlString = utils.get_files_xml(self.path)
        responseHeaders = [headers.End_Of_Body(data=xmlString, encoded=False)]
        response = responses.Success(header_data=responseHeaders)
        self.send_response(socket, response)
        print "Get_final response sent successfully!"

    # Handles Put_Final request ("delete")
    def put_final(self, socket, request):
        for header in request.header_data:
            if isinstance(header, headers.Name):
                name = header.decode()
                filename = os.path.join(self.path, name)
                if (os.path.exists(filename)):
                    try:
                        if os.path.isfile(filename):
                            os.remove(filename)
                        else:
                            shutil.rmtree(filename)
                        self.send_response(socket, responses.Success())
                        print "Response sent successfully!"
                    except IOError:
                        print "An error occurred deleting the item. Sending failure response..."
                        self.send_response(socket, responses.Forbidden())
                        print "Failure response sent successfully!"
                else:
                    print "Requested item does not exist. Sending failure response..."
                    self.send_response(socket, responses.Bad_Request())
                    print "Failure response sent successfully!"

    # Handles put request
    def put(self, socket, request):
        name = ""
        length = 0
        body = ""
        while True:
            for header in request.header_data:
                if isinstance(header, headers.Name):
                    name = header.decode()
                elif isinstance(header, headers.Length):
                    length = header.decode()
                elif isinstance(header, headers.Body):
                    body += header.decode()
                elif isinstance(header, headers.End_Of_Body):
                    body += header.decode()
            if request.is_final():
                break
            # Ask for more data.
            self.send_response(socket, responses.Continue())
            # Get the next part of the data.
            request = self.request_handler.decode(socket)
        name = name.strip("\x00").encode(sys.getfilesystemencoding())
        name = os.path.split(name)[1]
        filepath = os.path.join(self.path, name)
        print "Writing {}...".format(filepath)
        try:
            with open(filepath, "wb") as outfile:
                outfile.write(body)
            self.send_response(socket, responses.Success())
            print "Response sent successfully!"
        except IOError:
            print "IOError occurred. Sending failure response..."
            self.send_response(socket, responses.Forbidden())
            print "Failure response sent successfully!"

    # Handles get request
    def get(self, socket, request):
        name = ""
        type = ""
        for header in request.header_data:
            if isinstance(header, headers.Name):
                name = header.decode().strip("\x00")
                print "Receiving request for {}".format(name)

            elif isinstance(header, headers.Type):
                type = header.decode().strip("\x00")
                print "Type {}".format(type)

        filepath = os.path.abspath(os.path.join(self.path, name))
        # TODO: Get a file
        self.send_response(socket, responses.Success())

    # Set the current directory
    def set_path(self, socket, request):
        try:
            for header in request.header_data:
                if isinstance(header, headers.Name):
                    header_content = header.decode().replace("\x00", "")
                    if not header_content: # Set path to parent directory
                        temp_path = os.path.abspath(os.path.join(self.path, os.pardir))
                        os.listdir(temp_path) # Will throw WindowsError if permission denied
                        self.path = temp_path
                    else: # Set new current path
                        temp_path = os.path.join(self.path, header_content)
                        os.listdir(temp_path)
                        self.path = temp_path # Will throw WindowsError if permission denied
            self.send_response(socket, responses.Success())
            print "Set_path response sent successfully!"
        except WindowsError:
            print "Permission denied on setpath request. Sending error response..."
            self.send_response(socket, responses.Forbidden())
            print "Set_path error response sent successfully!"

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
