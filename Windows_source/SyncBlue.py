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

import sys
import BTDeviceFinder
import BTServerMode
import bluetooth
import os
import PyOBEX.client
import PyOBEX.responses
import PyOBEX.requests
import BTUtils
import shutil
from PyQt4 import QtCore, QtGui
import os
import sys
import ctypes

myappid = 'SyncBlue'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

def module_path():
    if hasattr(sys, "frozen"):
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

def loadAddresses():
    addresses = {}
    if os.path.exists(os.path.join(module_path(), "addresses.txt")):
        fo = open(os.path.join(module_path(), "addresses.txt"), "r")
        for line in fo:
            contents = line.strip().split(",")
            addresses[contents[0]] = contents[1]
        fo.close()
    return addresses

def loadData():
    timeout = "60"
    path = str(os.path.expanduser("~"))
    target_path = "target path here"
    mode = "one-way0"
    verbose = "1"
    if os.path.exists(os.path.join(module_path(), "data.txt")):
        fo = open(os.path.join(module_path(), "data.txt"), "r")
        timeout = fo.readline().rstrip()
        path = fo.readline().rstrip()
        target_path = fo.readline().rstrip()
        mode = fo.readline().rstrip()
        verbose = fo.readline().rstrip()
        fo.close()
    return timeout, path, target_path, mode, verbose

def saveAddresses(addresses):
    fo = open(os.path.join(module_path(), "addresses.txt"), "w")
    count = 1
    for key in addresses:
        if count != len(addresses):
            fo.write("{0},{1}\n".format(key, addresses[key]))
        else:
            fo.write("{0},{1}".format(key, addresses[key]))
        count = count + 1
    fo.close()

def saveData(timeout, path, target_path, mode, verbose):
    fo = open(os.path.join(module_path(), "data.txt"), "w")
    fo.write("{0}\n{1}\n{2}\n{3}\n{4}".format(str(timeout), str(path), str(target_path), str(mode), str(verbose)))
    fo.close()

class SyncBlueMainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(SyncBlueMainWindow, self).__init__()

        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.timeout, self.path, self.target_path, self.mode, self.verbose = loadData()
        self.addresses = loadAddresses()
        self.name = ""
        self.current_services = []
        self.tempPath = os.path.expanduser("~")
        self.initUI()

    # Restore sys.stdout
    def __del__(self):
        sys.stdout = sys.__stdout__

    # Initializes the user interface
    def initUI(self):
        # Set up main window interface
        self.setGeometry(300, 300, 500, 500)
        self.setWindowTitle("SyncBlue")
        self.center()

        # Menu bar
        self.menubar = self.menuBar()
        self.launchServerMode = QtGui.QAction("Server Mode", self)
        self.launchServerMode.triggered.connect(self.launch_server)
        self.launchServerMode.setEnabled(False)
        self.menubar.addAction(self.launchServerMode)
        self.settingsAction = QtGui.QAction("Settings", self)
        self.settingsAction.triggered.connect(self.launch_settings)
        self.menubar.addAction(self.settingsAction)

        # Status bar
        self.statusBar().showMessage("Ready")

        # Central widget
        self.frame = QtGui.QWidget(self)
        self.setCentralWidget(self.frame)
        self.frame.mainLayout = QtGui.QVBoxLayout()

        # Lookup by device name
        self.frame.nameLayout = QtGui.QHBoxLayout()
        self.frame.mainLayout.addLayout(self.frame.nameLayout)
        self.nameLabel = QtGui.QLabel("Choose a device name to connect to:")
        self.frame.nameLayout.addWidget(self.nameLabel)
        self.chooseName = QtGui.QComboBox(self)
        self.frame.nameLayout.addWidget(self.chooseName)
        for key in self.addresses: # Populate the combobox
            self.chooseName.addItem(key)
        self.chooseName.connect(self.chooseName, QtCore.SIGNAL("activated(QString)"), self.selectName)
        self.nameButton = QtGui.QPushButton("Add new device", self)
        self.frame.nameLayout.addWidget(self.nameButton)
        self.nameButton.connect(self.nameButton, QtCore.SIGNAL("clicked()"), self.showNameDialog)

         # Browse folder
        self.frame.browseFolderLayout = QtGui.QHBoxLayout()
        self.frame.browseFolderLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.frame.mainLayout.addLayout(self.frame.browseFolderLayout)
        self.currentFolderLabel = QtGui.QLabel("Current local sync folder:")
        self.frame.browseFolderLayout.addWidget(self.currentFolderLabel)
        self.displayLocalFolderLabel = QtGui.QLabel(self.path)
        self.frame.browseFolderLayout.addWidget(self.displayLocalFolderLabel)
        self.frame.browseFolderLayout.addStretch(1)
        self.selectSyncFolderButton = QtGui.QPushButton("Select sync folder")
        self.frame.browseFolderLayout.addWidget(self.selectSyncFolderButton)
        self.selectSyncFolderButton.connect(self.selectSyncFolderButton, QtCore.SIGNAL("clicked()"), self.browse)
        self.selectSyncFolderButton.setMaximumWidth(99)

        # Get target path
        self.frame.setTargetLayout = QtGui.QHBoxLayout()
        self.frame.mainLayout.addLayout(self.frame.setTargetLayout)
        self.targetFolderLabel = QtGui.QLabel("Current remote target folder:")
        self.frame.setTargetLayout.addWidget(self.targetFolderLabel)
        self.targetFolderText = QtGui.QLineEdit(self.target_path)
        self.frame.setTargetLayout.addWidget(self.targetFolderText)
        self.selectTargetFolderButton = QtGui.QPushButton("Save")
        self.frame.setTargetLayout.addWidget(self.selectTargetFolderButton)
        self.selectTargetFolderButton.connect(self.selectTargetFolderButton, QtCore.SIGNAL("clicked()"), self.setTarget)

        # Available services
        self.frame.servicesLayout = QtGui.QHBoxLayout()
        self.frame.mainLayout.addLayout(self.frame.servicesLayout)
        self.servicesLabel = QtGui.QLabel("Available services:")
        self.servicesLabel.setMaximumWidth(100)
        self.frame.servicesLayout.addWidget(self.servicesLabel)
        self.selectService = QtGui.QListWidget(self.frame)
        self.selectService.setMaximumHeight(80)
        self.frame.servicesLayout.addWidget(self.selectService)
        self.frame.servicesSublayout = QtGui.QVBoxLayout()
        self.frame.servicesLayout.addLayout(self.frame.servicesSublayout)
        self.serviceFindButton = QtGui.QPushButton("Find services")
        self.frame.servicesSublayout.addWidget(self.serviceFindButton)
        self.serviceConnectButton = QtGui.QPushButton("Sync")
        self.serviceConnectButton.setEnabled(False)
        self.frame.servicesSublayout.addWidget(self.serviceConnectButton)
        self.serviceFindButton.connect(self.serviceFindButton, QtCore.SIGNAL("clicked()"), self.populate_selectBox)
        self.serviceConnectButton.connect(self.serviceConnectButton, QtCore.SIGNAL("clicked()"), self.connect)

        if self.mode == "manual":
            self.enable_manual()

        # Log
        self.textEdit = QtGui.QTextEdit(self)
        if self.verbose == "0":
            self.textEdit.hide()
            self.setGeometry(300, 300, 200, 200)
        self.frame.mainLayout.addWidget(self.textEdit)

        # Connect/quit
        self.frame.actionLayout = QtGui.QHBoxLayout()
        self.frame.actionLayout.addStretch(2)
        self.frame.mainLayout.addLayout(self.frame.actionLayout)
        self.quitButton = QtGui.QPushButton("Cancel", self) # button is a child of window
        self.quitButton.connect(self.quitButton, QtCore.SIGNAL('clicked()'),
            self.quitAction)
        self.frame.actionLayout.addWidget(self.quitButton)
        self.frame.setLayout(self.frame.mainLayout)
        self.show()

    # For menubar
    @QtCore.pyqtSlot()
    def launch_settings(self):
        self.settingsWindow = SettingsWindow(self)
        self.settingsWindow.exec_()
        self.addresses = loadAddresses()
        self.timeout, self.path, self.target_path, self.mode, self.verbose = loadData()
        itemsSoFar = [self.chooseName.itemText(i) for i in range(self.chooseName.count())]
        for item in self.addresses:
            if item not in itemsSoFar:
                self.chooseName.addItem(item)
        for item in itemsSoFar:
            if item not in self.addresses.keys():
                self.chooseName.removeItem(self.chooseName.findText(str(item)))
        self.selectService.clear()
        self.statusBar().showMessage("Ready")
        self.serviceConnectButton.setEnabled(False)
        if self.verbose == "0":
            self.textEdit.hide()
            self.setGeometry(300, 300, 200, 200)
        else:
            self.textEdit.show()
            self.setGeometry(300, 300, 500, 500)
        mode = self.mode.capitalize()
        if "one-way" in self.mode:
            if "0" in self.mode:
                mode = "One-way, PC >> device"
            else:
                mode = "One-way, Device >> PC"
        print "Sync mode:", mode
        if self.mode == "manual":
            self.enable_manual()
        else:
            self.disable_manual()

    @QtCore.pyqtSlot()
    def launch_server(self, ):
        self.serverWindow = ServerWindow(self)
        self.serverWindow.exec_()
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

    def launch_manual(self):
        self.disable_top()
        self.container = QtGui.QWidget(self)
        self.container.manualSyncLayout = QtGui.QVBoxLayout()
        self.container.setLayout(self.container.manualSyncLayout)
        self.frame.mainLayout.addWidget(self.container)
        self.manualSync = QtGui.QListWidget(self)
        self.manualSync.itemDoubleClicked.connect(self.open_folder)
        self.container.manualSyncLayout.addWidget(self.manualSync)
        self.container.manualSyncSublayout = QtGui.QHBoxLayout()
        self.container.manualSyncLayout.addLayout(self.container.manualSyncSublayout)
        self.backButton = QtGui.QPushButton("Back")
        self.container.manualSyncSublayout.addWidget(self.backButton)
        self.putFileButton = QtGui.QPushButton("Put file")
        self.container.manualSyncSublayout.addWidget(self.putFileButton)
        self.putFolderButton = QtGui.QPushButton("Put folder")
        self.container.manualSyncSublayout.addWidget(self.putFolderButton)
        self.getButton = QtGui.QPushButton("Get")
        self.container.manualSyncSublayout.addWidget(self.getButton)
        self.deleteButton = QtGui.QPushButton("Delete")
        self.container.manualSyncSublayout.addWidget(self.deleteButton)
        self.newDirButton = QtGui.QPushButton("New folder")
        self.container.manualSyncSublayout.addWidget(self.newDirButton)
        self.manualDisconnButton = QtGui.QPushButton("Disconnect")
        self.container.manualSyncSublayout.addWidget(self.manualDisconnButton)
        self.manualDisconnButton.clicked.connect(self.manual_disconn)
        self.getButton.clicked.connect(self.get)
        self.putFileButton.clicked.connect(self.put_file)
        self.putFolderButton.clicked.connect(self.put_folder)
        self.deleteButton.clicked.connect(self.delete)
        self.backButton.clicked.connect(self.back)
        self.newDirButton.clicked.connect(self.newdir)
        self.refresh()

    def open_folder(self):
        contents = BTUtils.get_attributes_target(self.client)
        row = self.manualSync.row(self.manualSync.selectedItems()[0])
        if contents[row]["type"] == "folder":
            self.client.setpath(str(self.manualSync.selectedItems()[0].text()))
            self.refresh()

    def refresh(self):
        contents = BTUtils.get_attributes_target(self.client)
        self.manualSync.clear()
        for item in contents:
            self.manualSync.addItem(item["name"])

    def manual_disconn(self):
        try:
            print "Disconnecting..."
            disconn = self.client.disconnect()
            if isinstance(disconn, PyOBEX.responses.Success):
                print "Disconnected successfully."
            else:
                print "Disconnection failed."
            self.enable_top()
            self.container.hide()
        except AttributeError:
            print "There was an error in the connection. Disconnected."

    def get(self):
        try:
            attributes = BTUtils.get_attributes_target(self.client)
            row = self.manualSync.row(self.manualSync.selectedItems()[0])
            if attributes[row]["type"] == "file":
                headers, data = self.client.get(str(self.manualSync.selectedItems()[0].text()))
                dialog = QtGui.QFileDialog()
                dialog.setFileMode(QtGui.QFileDialog.AnyFile)
                filepath = str(QtGui.QFileDialog.getExistingDirectory(self, "Save as...", self.tempPath, QtGui.QFileDialog.ShowDirsOnly))
                print "Getting file..."
                print "Saving file at: ", filepath
                if self.tempPath:
                    fo = open(os.path.join(filepath, attributes[row]["name"]), "wb")
                else:
                    print "Please specify a valid path. \n GET aborted."
                    return
                fo.write(data)
                fo.close()
                print "File transferred."
            else:
                self.tempPath = str(QtGui.QFileDialog.getExistingDirectory(self,
                                                             'Save as...',
                                                             self.tempPath,
                                                             QtGui.QFileDialog.ShowDirsOnly))
                self.client.setpath(str(self.manualSync.currentItem().text()))
                print "Getting folder..."
                BTUtils.get_folder(self.client, self.tempPath, "")
                self.client.setpath(to_parent = True)
                print "Folder transferred."
            self.refresh()
        except IndexError:
            print "Please select a file or folder."

    def put_file(self):
        filepath = (str(QtGui.QFileDialog.getOpenFileName(self, "Select File", self.tempPath)))
        if "/" in filepath:
            cutoff = filepath.rfind("/")
            self.tempPath = filepath[:cutoff]
        else:
            cutoff = 0
            self.tempPath = ""
        print "Temp path:", self.tempPath
        print "Filepath:", filepath
        if os.path.isfile(filepath):
            fo = open(filepath, "rb")
            data = fo.read()
            if cutoff != 0:
                self.client.put(filepath[cutoff+1:], data)
            else:
                self.client.put(filepath[cutoff:], data)
        self.refresh()

    def put_folder(self):
        filepath = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Folder", self.tempPath, QtGui.QFileDialog.ShowDirsOnly))
        print "Filepath:", filepath
        if "\\" in filepath:
            cutoff = filepath.rfind("\\")
            self.tempPath = filepath[:cutoff]
        else:
            cutoff = 0
            self.tempPath = ""
        print "Temp path:", self.tempPath
        print "Filepath:", filepath
        if cutoff != 0:
            self.client.setpath(filepath[cutoff+1:], create_dir = True)
            BTUtils.one_way_sync(self.client, filepath, filepath[cutoff+1:])
        else:
            self.client.setpath(filepath[cutoff:], create_dir = True)
            BTUtils.one_way_sync(self.client, filepath, filepath[cutoff:])
        self.refresh()

    def newdir(self):
        dirname, ok = QtGui.QInputDialog.getText(self, 'Directory name', 'New folder')
        dirname = str(dirname)
        if ok:
            self.client.setpath(dirname, create_dir = True)
            self.client.setpath(to_parent = True)
            self.refresh()

    def back(self):
        self.client.setpath(to_parent = True)
        self.refresh()

    def delete(self):
         reply = QtGui.QMessageBox.question(self, "Delete", "Are you sure you want to delete permanently?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
         if reply == QtGui.QMessageBox.Yes:
             self.client.delete(str(self.manualSync.currentItem().text()))
             self.refresh()

    def enable_manual(self):
         self.targetFolderLabel.hide()
         self.targetFolderText.hide()
         self.selectTargetFolderButton.hide()
         self.currentFolderLabel.hide()
         self.displayLocalFolderLabel.hide()
         self.selectSyncFolderButton.hide()

    def disable_manual(self):
        self.targetFolderLabel.show()
        self.targetFolderText.show()
        self.selectTargetFolderButton.show()
        self.currentFolderLabel.show()
        self.displayLocalFolderLabel.show()
        self.selectSyncFolderButton.show()

    def disable_top(self):
        self.nameLabel.setEnabled(False)
        self.nameButton.setEnabled(False)
        self.chooseName.setEnabled(False)
        self.servicesLabel.setEnabled(False)
        self.serviceFindButton.setEnabled(False)
        self.serviceConnectButton.setEnabled(False)
        self.selectService.setEnabled(False)

    def enable_top(self):
        self.nameLabel.setEnabled(True)
        self.nameButton.setEnabled(True)
        self.chooseName.setEnabled(True)
        self.servicesLabel.setEnabled(True)
        self.serviceFindButton.setEnabled(True)
        self.serviceConnectButton.setEnabled(True)
        self.selectService.setEnabled(True)

    # For select services
    def populate_selectBox(self):
        self.selectService.clear()
        current_device = str(self.chooseName.currentText())
        try:
            self.current_services =  bluetooth.find_service(address = self.addresses[current_device])
            if not self.current_services:
                reply = QtGui.QMessageBox.question(self, "Error", "The target device could not be found. Ensure that Bluetooth is turned on both on this computer and on the remote device, and make sure the remote device is discoverable.", QtGui.QMessageBox.Ok)
                return
            for dict in self.current_services:
                """if "1106" in dict["service-classes"]:
                   self.selectService.addItem(dict["name"])
                else:
                     reply = QtGui.QMessageBox.question(self, "Error", "Your device does not suppport OBEX File Transfer.", QtGui.QMessageBox.Ok)
                     return"""
                self.selectService.addItem(dict["name"])
            self.selectService.update();
            self.serviceConnectButton.setEnabled(True)
        except IOError:
            reply = QtGui.QMessageBox.question(self, "Error", "The target device could not be found. Ensure that Bluetooth is turned on both on this computer and on the remote device, and make sure the remote device is discoverable.", QtGui.QMessageBox.Ok)
            return
        except KeyError:
            reply = QtGui.QMessageBox.question(self, "Error", "No target device specified.", QtGui.QMessageBox.Ok)
            return

    # Handles log output
    def normalOutputWritten(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()

    # Handles closing event
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, "Quit", "Are you sure you want to quit? Devices & addresses will be saved.", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            saveAddresses(self.addresses)
            saveData(self.timeout, self.path, self.target_path, self.mode, self.verbose)
            event.accept()
        else:
            event.ignore()

    # For quit button
    def quitAction(self):
        reply = QtGui.QMessageBox.question(self, "Quit", "Are you sure you want to quit? Devices & addresses will be saved.", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            saveAddresses(self.addresses)
            saveData(self.timeout, self.path, self.target_path, self.mode, self.verbose)
            QtCore.QCoreApplication.instance().quit()

    # For lookup by device name
    def selectName(self, text):
        self.name = str(text)

    def showNameDialog(self):
        self.name, ok = QtGui.QInputDialog.getText(self, 'Add new device', 'Find device by name:')
        self.name = str(self.name)
        if ok:
            self.saveEnteredName()

    def saveEnteredName(self):
        address = str(BTDeviceFinder.find_by_name(self.name))
        if address:
            self.addresses[self.name] = address
            saveAddresses(self.addresses)
            self.statusBar().showMessage("Added device '{0}' with address {1}".format(self.name, self.addresses[self.name]))
            self.chooseName.addItem(self.name)
        else:
            self.errorMessage = QtGui.QErrorMessage("No devices with that name were detected.")

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # For get sync folder
    def browse(self):
        startingDir = os.path.expanduser("~")
        self.path = str(QtGui.QFileDialog.getExistingDirectory(None,
                                                         'Open working directory',
                                                         startingDir,
                                                         QtGui.QFileDialog.ShowDirsOnly))
        self.displayLocalFolderLabel.setText(self.path)

    # For save target folder
    def setTarget(self):
        self.target_path = str(self.targetFolderText.text())

    # Actual connection
    def connect(self):
        try:
            print self.mode
            if not self.selectService.currentItem():
                print "Please select a service."
                return
            for item in self.current_services:
                port=0
                service_name=self.selectService.currentItem().text()
                if service_name:
                    if item["name"] == service_name:
                        port = item["port"]
                        break
                else:
                    print "Please select a service."
                    return
            if port == 0:
                print "Unable to find service."
                return
            print "Trying to connect to port {0}...".format(port)
            self.client = PyOBEX.client.BrowserClient(self.addresses[str(self.chooseName.currentText())], port)
            conn = self.client.connect()
            if isinstance(conn, PyOBEX.responses.ConnectSuccess):
                print "Connected successfully."
            else:
                print "Connection failed. Make sure you selected 'OBEX File Transfer'."

            if "one-way" in self.mode:
                self.disable_top()
                if "0" in self.mode:
                    message = "Are you sure you want to one-way-sync {0} to the remote device? The contents of {1} on the remote device will be lost and overwritten by the new contents.".format(self.path, self.target_path)
                    reply = QtGui.QMessageBox.question(self, "Attention: Possible loss of files", message, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        BTUtils.find_target_folder(self.client, self.target_path)
                        print "Syncing..."
                        BTUtils.one_way_sync(self.client, self.path, self.target_path)
                    else: pass
                else:
                    message = "Are you sure you want to one-way-sync {0} from the remote device? The contents of {1} on the computer will be lost and overwritten by the new contents.".format(self.target_path, self.path)
                    reply = QtGui.QMessageBox.question(self, "Attention: Possible loss of files", message, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        BTUtils.find_target_folder(self.client, self.target_path)
                        print "Syncing..."
                        try:
                            if os.path.exists(self.path):
                                shutil.rmtree(self.path, ignore_errors = False)
                        except Exception:
                            print "Error syncing folder on this PC. Make sure not to sync folders containing read-only files."
                            print "Aborting..."
                            disconn = self.client.disconnect()
                            if isinstance(disconn, PyOBEX.responses.Success):
                                print "Disconnected successfully."
                            else:
                                print "Disconnection failed."
                            return
                        os.mkdir(self.path)
                        BTUtils.get_folder(self.client, self.path, "")
                    else: pass
                disconn = self.client.disconnect()
                if isinstance(disconn, PyOBEX.responses.Success):
                    print "Disconnected successfully."
                else:
                    print "Disconnection failed."
                self.enable_top()
            elif self.mode == "two-way":
                self.disable_top()
                message = "Are you sure you want to two-way-sync {0} with {1} on the remote device? Files that do not exist in one of the locations will be added to the other, and older file versions will be overwritten.".format(self.path, self.target_path)
                reply = QtGui.QMessageBox.question(self, "Attention: Possible loss of files", message, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes:
                    BTUtils.find_target_folder(self.client, self.target_path)
                    print "Syncing..."
                    BTUtils.two_way_sync(self.client, self.path)
                else: pass
                disconn = self.client.disconnect()
                if isinstance(disconn, PyOBEX.responses.Success):
                    print "Disconnected successfully."
                else:
                    print "Disconnection failed."
                self.enable_top()
            elif self.mode == "manual":
                self.launch_manual()
        except IOError:
            message = "Could not connect to target device. Make sure the target device has Bluetooth turned on, is discoverable and paired with this computer. Also, make sure that your device supports OBEX file transfer and that you select 'OBEX File Transfer' from the services menu."
            QtGui.QMessageBox.warning(self, "Connection Error", message, QtGui.QMessageBox.Ok)

# Helper class for StdOut IO
class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

# Server window class
class ServerWindow(QtGui.QDialog):
    def __init__(self, parent=SyncBlueMainWindow):
        super(ServerWindow, self).__init__(parent)
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.setWindowTitle("Server Mode")
        self.initUI(parent)

    def initUI(self, parent):
        self.mainLayout = QtGui.QVBoxLayout(self)
        self.log = QtGui.QTextEdit(self)
        self.mainLayout.addWidget(self.log)
        self.buttonLayout = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.buttonLayout)
        self.startServerButton = QtGui.QPushButton("Launch server", self)
        self.buttonLayout.addWidget(self.startServerButton)
        self.startServerButton.connect(self.startServerButton, QtCore.SIGNAL("clicked()"), self.startServer)
        self.abortServerButton = QtGui.QPushButton("Abort", self)
        self.buttonLayout.addWidget(self.abortServerButton)
        self.abortServerButton.connect(self.abortServerButton, QtCore.SIGNAL("clicked()"), self.abortServer)
        self.abortServerButton.setEnabled(False)

    def normalOutputWritten(self, text):
        cursor = self.log.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.log.setTextCursor(cursor)
        self.log.ensureCursorVisible()

    def startServer(self):
        self.server = BTServerMode.SyncBlueServer()
        self.abortServerButton.setEnabled(True)
        self.startServerButton.setEnabled(False)
        self.server_sock = self.server.start_service()          # Returns BluetoothSocket object
        #server.serve(server_sock)

    def abortServer(self):
        try:
            reply = QtGui.QMessageBox.question(self, "Server abort", "Are you sure you want to abort?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.startServerButton.setEnabled(True)
                self.abortServerButton.setEnabled(False)
                if (self.server):
                    self.server.disconnect(self.server_sock, PyOBEX.requests.Disconnect)
                    print "Server terminated."
            else:
                pass
        except IOError:                                         # If attempting to disconnect a disconnected socket
            print "The connection has been lost. Terminating server..."
            self.server_sock.close()
            print "Server terminated."

# Settings window class
class SettingsWindow(QtGui.QDialog):
    def __init__(self, parent=SyncBlueMainWindow):
        super(SettingsWindow, self).__init__(parent)
        self.tempAddresses = loadAddresses()
        self.tempTimeout, self.path, self.target_path, self.mode, self.verbose = loadData()
        self.setWindowTitle("Settings")
        self.initUI(parent)

    def initUI(self, parent):
        # Main grid layout
        self.gridLayoutWidget = QtGui.QWidget(self)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 10, 561, 471))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        # Left vertical layout
        self.verticalLayout = QtGui.QVBoxLayout()
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.deleteLabel = QtGui.QLabel("Select device to be deleted:", self.gridLayoutWidget)
        self.verticalLayout.addWidget(self.deleteLabel)
        self.deleteList = QtGui.QListWidget(self.gridLayoutWidget)
        self.deleteList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.verticalLayout.addWidget(self.deleteList)
        for key in self.tempAddresses:
            self.deleteList.addItem(key)
        # Horizontal layout for add + delete devices
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.deleteDeviceButton = QtGui.QPushButton("Delete device", self.gridLayoutWidget)
        self.deleteDeviceButton.connect(self.deleteDeviceButton, QtCore.SIGNAL("clicked()"), self.deleteDeviceAction)
        self.horizontalLayout.addWidget(self.deleteDeviceButton)
        self.addDeviceButton = QtGui.QPushButton("Add device", self.gridLayoutWidget)
        self.addDeviceButton.connect(self.addDeviceButton, QtCore.SIGNAL("clicked()"), self.addDeviceAction)
        self.horizontalLayout.addWidget(self.addDeviceButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        # OK / Cancel button box
        self.settingsButtonBox = QtGui.QDialogButtonBox(self.gridLayoutWidget)
        self.settingsButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.settingsButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        self.settingsButtonBox.accepted.connect(self.okButtonAction)
        self.settingsButtonBox.rejected.connect(self.reject)
        self.gridLayout.addWidget(self.settingsButtonBox, 1, 1, 1, 1)
        # Right vertical layout
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 1)
        self.verticalLayout_2.setAlignment(QtCore.Qt.AlignTop)
        # Sub-layout for timeout function
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.timeoutLabel = QtGui.QLabel("Timeout after", self.gridLayoutWidget)
        self.horizontalLayout_2.addWidget(self.timeoutLabel)
        self.timeoutField = QtGui.QLineEdit(self.gridLayoutWidget)
        self.timeoutField.setMinimumSize(QtCore.QSize(4, 0))
        self.timeoutField.setText(self.tempTimeout)
        self.horizontalLayout_2.addWidget(self.timeoutField)
        self.timeoutLabel2 = QtGui.QLabel("seconds", self.gridLayoutWidget)
        self.horizontalLayout_2.addWidget(self.timeoutLabel2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.timeoutButton = QtGui.QPushButton("Set", self)
        self.timeoutButton.connect(self.timeoutButton, QtCore.SIGNAL("clicked()"), self.timeoutSetting)
        self.horizontalLayout_2.addWidget(self.timeoutButton)
        self.horizontalLayout_2.addStretch(2)
        # Sub-Layout for select sync mode
        self.groupBox = QtGui.QGroupBox("Set sync mode:")
        self.oneWaySyncLayout = QtGui.QHBoxLayout()
        self.oneWaySyncButton = QtGui.QRadioButton("One-way synchronization:")
        self.oneWaySyncButton.connect(self.oneWaySyncButton, QtCore.SIGNAL("clicked()"), self.selectSyncMode)
        self.oneWaySyncLayout.addWidget(self.oneWaySyncButton)
        self.oneWaySyncLabel1 = QtGui.QLabel("PC >> Device")
        self.oneWaySyncLayout.addWidget(self.oneWaySyncLabel1)
        self.oneWaySyncSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.oneWaySyncSlider.setMaximum(1)
        self.oneWaySyncLayout.addWidget(self.oneWaySyncSlider)
        self.oneWaySyncLabel2 = QtGui.QLabel("Device >> PC")
        self.oneWaySyncLayout.addWidget(self.oneWaySyncLabel2)
        self.twoWaySyncButton = QtGui.QRadioButton("Two-way synchronization")
        self.twoWaySyncButton.connect(self.twoWaySyncButton, QtCore.SIGNAL("clicked()"), self.selectSyncMode)
        self.manualSyncButton = QtGui.QRadioButton("Manual synchronization")
        self.manualSyncButton.connect(self.manualSyncButton, QtCore.SIGNAL("clicked()"), self.selectSyncMode)
        self.setButtonChecked()
        self.selectSyncLayout = QtGui.QVBoxLayout()
        self.selectSyncLayout.addLayout(self.oneWaySyncLayout)
        self.selectSyncLayout.addWidget(self.twoWaySyncButton)
        self.selectSyncLayout.addWidget(self.manualSyncButton)
        self.groupBox.setLayout(self.selectSyncLayout)
        self.verticalLayout_2.addWidget(self.groupBox)
        # Verbose mode
        self.verboseLayout = QtGui.QHBoxLayout()
        self.verboseLabel = QtGui.QLabel("Display log")
        self.verboseLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.verboseButton = QtGui.QCheckBox()
        self.verboseLayout.addWidget(self.verboseButton)
        if self.verbose == "0":
            self.verboseButton.setChecked(False)
        else:
            self.verboseButton.setChecked(True)
        self.verboseLayout.addWidget(self.verboseLabel)
        self.verticalLayout_2.addLayout(self.verboseLayout)

    def addDeviceAction(self):
        # Ask for a name; run BTDevicefinder and save name, address in tempAddresses
        name, ok = QtGui.QInputDialog.getText(self, 'Add new device', 'Find device by name:')
        if ok:
            try:
                address = BTDeviceFinder.find_by_name(name)
                if address:
                    self.tempAddresses[name] = address
                    self.deleteList.addItem(name)
                else:
                    self.errorMessage = QtGui.QErrorMessage("No devices with that name were detected.")
            except IOError:
                self.errorMessage = QtGui.QErrorMessage("The target device could not be found. Ensure that Bluetooth is turned on both on this computer and \
                    on the remote device, and make sure the remote device is discoverable.")
                return

    def deleteDeviceAction(self):
        itm = str(self.deleteList.currentItem().text())
        self.tempAddresses.pop(itm)
        self.deleteList.clear()
        for item in self.tempAddresses:
            self.deleteList.addItem(item)
            print item

    def okButtonAction(self):
        # Set mode to be saved
        if self.oneWaySyncButton.isChecked():
            self.mode = "one-way" + str(self.oneWaySyncSlider.value())
        elif self.twoWaySyncButton.isChecked():
            self.mode = "two-way"
        elif self.manualSyncButton.isChecked():
            self.mode = "manual"
        if self.verboseButton.isChecked():
            self.verbose = "1"
        else:
            self.verbose = "0"
        saveAddresses(self.tempAddresses)
        saveData(self.tempTimeout, self.path, self.target_path, self.mode, self.verbose)
        self.close()

    def timeoutSetting(self):
        self.tempTimeout = self.timeoutField.text()

    def selectSyncMode(self):
        if self.oneWaySyncButton.isChecked():
            self.oneWaySyncLabel1.setEnabled(True)
            self.oneWaySyncLabel2.setEnabled(True)
            self.oneWaySyncSlider.setEnabled(True)
        elif self.twoWaySyncButton.isChecked():
            self.oneWaySyncLabel1.setEnabled(False)
            self.oneWaySyncLabel2.setEnabled(False)
            self.oneWaySyncSlider.setEnabled(False)
        elif self.manualSyncButton.isChecked():
            self.oneWaySyncLabel1.setEnabled(False)
            self.oneWaySyncLabel2.setEnabled(False)
            self.oneWaySyncSlider.setEnabled(False)

    def setButtonChecked(self):
        if "one-way" in self.mode:
            self.oneWaySyncButton.setChecked(True)
            self.oneWaySyncSlider.setEnabled(True)
            self.oneWaySyncLabel1.setEnabled(True)
            self.oneWaySyncLabel2.setEnabled(True)
            self.oneWaySyncSlider.setValue(int(self.mode[7]))
        elif self.mode == "two-way":
            self.twoWaySyncButton.setChecked(True)
            self.oneWaySyncSlider.setEnabled(False)
            self.oneWaySyncLabel1.setEnabled(False)
            self.oneWaySyncLabel2.setEnabled(False)
        elif self.mode == "manual":
            self.manualSyncButton.setChecked(True)
            self.oneWaySyncSlider.setEnabled(False)
            self.oneWaySyncLabel1.setEnabled(False)
            self.oneWaySyncLabel2.setEnabled(False)
        else:
            self.oneWaySyncButton.setChecked(True)
            self.oneWaySyncSlider.setEnabled(True)
            self.oneWaySyncSlider.setValue(0)
            self.oneWaySyncLabel1.setEnabled(True)
            self.oneWaySyncLabel2.setEnabled(True)

class FileDialog(QtGui.QFileDialog):
        def __init__(self, *args):
            QtGui.QFileDialog.__init__(self, *args)
            self.setOption(self.DontUseNativeDialog, True)
            self.setFileMode(self.ExistingFiles)
            btns = self.findChildren(QtGui.QPushButton)
            self.openBtn = [x for x in btns if 'open' in str(x.text()).lower()][0]
            self.openBtn.clicked.disconnect()
            self.openBtn.clicked.connect(self.openClicked)
            self.tree = self.findChild(QtGui.QTreeView)

        def openClicked(self):
            inds = self.tree.selectionModel().selectedIndexes()
            files = []
            for i in inds:
                if i.column() == 0:
                    files.append(os.path.join(str(self.directory().absolutePath()),str(i.data().toString())))
            self.selectedFiles = files
            self.hide()

        def filesSelected(self):
            return self.selectedFiles

def main():
    app = QtGui.QApplication(sys.argv)
    app_icon = QtGui.QIcon()
    app_icon.addPixmap(QtGui.QPixmap("icon.ico"), QtGui.QIcon.Normal)
    app.setWindowIcon(app_icon)
    window = SyncBlueMainWindow()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()
