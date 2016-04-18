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

"""
""" Server should support put, get, listdir, change dir, mkdir """

from eu.syncblue.core import utils
import serverutils

from bluetooth import *
from PyOBEX.common import OBEX_Version, Socket
from PyOBEX import server
from PyOBEX import requests
from PyOBEX import responses
from PyOBEX import headers
from PyQt4 import QtCore, QtGui
import os, sys, shutil
import uuid
import socket

# Reimplements PyOBEX.server.Server
class SyncBlueServer(server.Server):

    # Reimplementation of initializer (mainly for logging)
    def __init__(self, address = ""):
        self.address = address
        self.max_packet_length = 0xffff
        self.obex_version = OBEX_Version()
        self.request_handler = requests.RequestHandler()
        self.path = os.path.expanduser("~")                         # Default path: Home directory

    # Returns a BluetoothSocket instance.
    # Side effects: Advertises the service.
    def start_service(self, port = 0):

        name = "SyncBlue Server"
        uuid = "F9EC7BC4-953C-11d2-984E-525400DC9E09"
        service_classes = [OBEX_FILETRANS_CLASS]
        service_profiles = [OBEX_FILETRANS_PROFILE]
        provider = ""
        description = "SyncBlue"
        protocols = [OBEX_UUID]

        socket = Socket()
        socket.bind((self.address, port))
        socket.listen(1)
        
        advertise_service(socket, name, uuid, service_classes, service_profiles, provider, description, protocols)
        return socket

    # Re-implementation of process_request: Called every time a request arrives
    def process_request(self, connection, request):
        serverutils.dissect_request(request)
    
        if isinstance(request, requests.Connect):
            self.connect(connection, request)

        elif isinstance(request, requests.Disconnect):
            self.disconnect(connection, request)

        elif isinstance(request, requests.Put_Final):
            self.put_final(connection, request)

        elif isinstance(request, requests.Put):
            self.put(connection, request)

        elif isinstance(request, requests.Set_Path):
            self.set_path(connection, request)
            utils.debug("New path: {}".format(self.path))

        elif isinstance(request, requests.Get):
            self.get(connection, request)

        else:
            self._reject(connection)

    # Handles Put_Final request ("delete")
    def put_final(self, socket, request):
        for header in request.header_data:
            if isinstance(header, headers.Name):
                name = header.decode().strip().replace("\x00", "")
                filename = os.path.join(self.path, name)
                if not (name == "debug.txt"):
                    print "Deleting {}...".format(filename)
                if (os.path.exists(filename)):
                    try:
                        if os.path.isfile(filename):
                            os.remove(filename)
                        else:
                            shutil.rmtree(filename)
                        self.send_response(socket, responses.Success())
                        utils.debug("Response sent successfully!")
                    except IOError:
                        print "An error occurred deleting the item."
                        self.send_response(socket, responses.Forbidden())
                        utils.debug("Failure response sent successfully!")
                else:
                    print "Requested item {} does not exist.".format(filename)
                    self.send_response(socket, responses.Bad_Request())
                    utils.debug("Failure response sent successfully!")

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
            try:
                request = self.request_handler.decode(socket)
            except TypeError: # UnknownMessageClass for request causes exception
                pass
        name = name.strip("\x00").encode(sys.getfilesystemencoding())
        name = os.path.split(name)[1]
        filepath = os.path.join(self.path, name)
        if not (name == "debug.txt"):
            print "Writing {}...".format(filepath)
        try:
            with open(filepath, "wb") as outfile:
                outfile.write(body)
            print "Done."
            self.send_response(socket, responses.Success())
            utils.debug("Response sent successfully!")
        except IOError:
            print "IOError occurred."
            self.send_response(socket, responses.Forbidden())
            utils.debug("Failure response sent successfully!")

    # Handles get request
    def get(self, socket, request):
        name = ""
        type = ""
        for header in request.header_data:
            if isinstance(header, headers.Name):
                name = header.decode().strip("\x00")
            elif isinstance(header, headers.Type):
                type = header.decode().strip("\x00")
        filepath = os.path.abspath(os.path.join(self.path, name))
        max_length = self.remote_info.max_packet_length
        if (name and os.path.isdir(filepath)) or type == "x-obex/folder-listing":
            utils.debug("Handling request as GET_FINAL (listdir) for {}".format(filepath))
            xmlString = serverutils.get_files_xml(filepath)
            response = responses.Success()
            response.add_header(headers.Description(str(uuid.uuid4()), False), max_length)
            response.add_header(headers.End_Of_Body(xmlString, False), max_length)
            self.send_response(socket, response)
            utils.debug("Get_final response sent successfully!")
        elif name: # First request for a file
            if not os.path.isfile(filepath):
                print "Requested file does not exist."
                self.send_response(socket, responses.Bad_Request())
                utils.debug("Failure response sent.")
                return
            print "Handling request as GET for {}...".format(filepath)
            with open(filepath, "rb") as fo:
                file_data = fo.read()
            # Send the file data.
            # The optimum size is the maximum packet length accepted by the
            # remote device minus three bytes for the header ID and length
            # minus three bytes for the response.
            optimum_size = max_length - 3 - 3
            i = 0
            while i < len(file_data):
                data = file_data[i:i+optimum_size]
                i += len(data)
                if i < len(file_data): # Will send more file data, so send Continue response
                    response = responses.Continue()
                    response.add_header(headers.Body(data, False), max_length)
                    self.send_response(socket, response)
                else:
                   response = responses.Success()
                   response.add_header(headers.End_Of_Body(data, False), max_length)
                   utils.debug("Sending success response with end of body header {}".format(data))
                   self.send_response(socket, response)
        # Ignore get requests without name or type

    # Set the current directory
    def set_path(self, socket, request):
        try:
            for header in request.header_data:
                if isinstance(header, headers.Name):
                    header_content = header.decode().replace("\x00", "")
                    if not header_content: # Set path to parent directory
                        utils.debug("Handling request as SETPATH to parent directory...")
                        temp_path = os.path.abspath(os.path.join(self.path, os.pardir))
                        os.listdir(temp_path) # Will throw WindowsError if permission denied
                    elif not os.path.exists(os.path.join(self.path, header_content)): # Create new directory and change dir there
                        temp_path = os.path.join(self.path, header_content)
                        os.mkdir(os.path.join(temp_path))
                        utils.debug("Handling request as SETPATH and creating new directory {}".format(temp_path))
                    else: # Set new current path
                        temp_path = os.path.join(self.path, header_content)
                        os.listdir(temp_path) # Will throw WindowsError if permission denied
                        utils.debug("Handling request as SETPATH and changing dir to {}".format(temp_path))
                    self.path = temp_path
            self.send_response(socket, responses.Success())
            utils.debug("Set_path response sent successfully!")
        except WindowsError:
            print "Permission denied on setpath request."
            self.send_response(socket, responses.Forbidden())
            utils.debug("Set_path error response sent successfully!")

    def disconnect(self, socket, request):
        response = responses.Success()
        self.send_response(socket, response)
        self.connected = False

    def send_response(self, socket, response, header_list = []):
        try:
            ### TODO: This needs to be able to split messages that are longer than
            ### the maximum message length agreed with the other party.
            while header_list:

                if response.add_header(header_list[0], self._max_length()):
                    header_list.pop(0)
                else:
                    serverutils.dissect_response(response)
                    self.sendall(socket, response.encode())
                    response.reset_headers()

            # Always send at least one request.
            serverutils.dissect_response(response)
            self.sendall(socket, response.encode())
        
        except IOError: # If connection broken by client
            self.connected = False
    
    def sendall(self, sock, data):
        while data:
            sent = sock.send(data)
            if sent > 0:
                data = data[sent:]
            elif sent < 0:
                raise socket.error

class ServerThread(QtCore.QThread):

    serverDone = QtCore.pyqtSignal()

    # Creates a new server thread. Param server is a SynBlueServer object
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.server = SyncBlueServer()
        self.socket = None

    @QtCore.pyqtSlot()
    def abort(self):
        try:
            self.server.stop_service(self.socket)
        except IOError:
            self.socket.close()
        self.serverDone.emit()
        self.terminate()

    def run(self):
        print "Launching server..."
        self.socket = self.server.start_service()
        print "Done."
        self.server.serve(self.socket)
        self.serverDone.emit()

# Server window class
class ServerWindow(QtGui.QDialog):

    abortServerSig = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(ServerWindow, self).__init__(parent)
        if not utils.DEBUG:
            sys.stdout = utils.EmittingStream(textWritten=self.normalOutputWritten)
        self.setWindowTitle("Server Mode (Beta)")
        self.initUI(parent)

    def initUI(self, parent):
        self.mainLayout = QtGui.QVBoxLayout(self)
        self.log = QtGui.QTextEdit(self)
        self.mainLayout.addWidget(self.log)
        self.buttonLayout = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.buttonLayout)
        self.startServerButton = QtGui.QPushButton("Launch server", self)
        self.buttonLayout.addWidget(self.startServerButton)
        self.startServerButton.clicked.connect(self.startServer)
        self.abortServerButton = QtGui.QPushButton("Abort", self)
        self.buttonLayout.addWidget(self.abortServerButton)
        self.abortServerButton.clicked.connect(self.abortServer)
        self.abortServerButton.setEnabled(False)

    def normalOutputWritten(self, text):
        cursor = self.log.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.log.setTextCursor(cursor)
        self.log.ensureCursorVisible()

    def startServer(self):
        self.serverThread = ServerThread()
        self.abortServerButton.setEnabled(True)
        self.startServerButton.setEnabled(False)
        self.serverThread.serverDone.connect(self.onServerDone)
        self.abortServerSig.connect(self.serverThread.abort, QtCore.Qt.QueuedConnection)
        self.serverThread.start()

    def abortServer(self):
        try:
            reply = QtGui.QMessageBox.question(self, "Server abort", "Are you sure you want to abort? Before you abort, make sure that all clients are disconnected or they may wait infinitely long for a response.", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.startServerButton.setEnabled(True)
                self.abortServerButton.setEnabled(False)
                if (self.serverThread):
                    self.abortServerSig.emit()
                    print "Server terminated."
            else:
                pass
        except IOError: # If attempting to disconnect a disconnected socket
            print "The connection has been lost. Terminating server..."
            self.serverThread.terminate()
            print "Server terminated."

    def onServerDone(self):
        self.startServerButton.setEnabled(True)
        self.abortServerButton.setEnabled(False)
