"""
Copyright 2016 Benjamin Alt
benjamin_alt@outlook.com

syncblue.py

Entry point to SyncBlue.
Main GUI functions & application logic.

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

Entry point to SyncBlue. Contains main GUI components & logic.

"""

import server, autosync, devicefinder, manualmode, connect
import bluetooth
import os
import PyOBEX.client, PyOBEX.responses, PyOBEX.requests
import shutil
from PyQt4 import QtCore, QtGui
import os
import sys
import ctypes
from threading import Thread

DEBUG = False
myappid = 'SyncBlue'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

def module_path():
    if hasattr(sys, "frozen"):
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

def loadData():
    timeout = "60"
    path = str(os.path.expanduser("~"))
    target_path = "target path here"
    mode = "manual"
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

def saveData(timeout, path, target_path, mode, verbose):
    fo = open(os.path.join(module_path(), "data.txt"), "w")
    fo.write("{0}\n{1}\n{2}\n{3}\n{4}".format(str(timeout), str(path), str(target_path), str(mode), str(verbose)))
    fo.close()

class SyncBlueMainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(SyncBlueMainWindow, self).__init__()
        if not DEBUG:
            sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.timeout, self.path, self.target_path, self.mode, self.verbose = loadData()
        self.availableDevices = {}
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

        # Menu bar
        self.menubar = self.menuBar()
        self.launchServerMode = QtGui.QAction("Server Mode", self)
        self.launchServerMode.triggered.connect(self.launch_server)
        # self.launchServerMode.setEnabled(False)
        self.menubar.addAction(self.launchServerMode)
        self.settingsAction = QtGui.QAction("Settings", self)
        self.settingsAction.triggered.connect(self.launchSettings)
        self.menubar.addAction(self.settingsAction)

        # Status bar
        self.statusBar().showMessage("Ready")

        # Central widget
        self.frame = QtGui.QWidget(self)
        self.setCentralWidget(self.frame)
        self.frame.mainLayout = QtGui.QVBoxLayout()

        ##################### DEVICE SELECTION #################################

        # Select device name
        self.frame.nameLayout = QtGui.QVBoxLayout()
        self.frame.mainLayout.addLayout(self.frame.nameLayout)
        self.nameLabel = QtGui.QLabel("Choose a device name to connect to:")
        self.frame.nameLayout.addWidget(self.nameLabel)
        self.frame.nameSubLayout = QtGui.QHBoxLayout()
        self.frame.nameLayout.addLayout(self.frame.nameSubLayout)
        self.chooseName = QtGui.QListWidget(self)
        self.chooseName.setMaximumHeight(90)
        self.frame.nameSubLayout.addWidget(self.chooseName)
        # Listwidget is populated asynchronously at the end of initUI (after self.show())
        self.chooseName.itemClicked.connect(self.nameSelected)
        self.frame.nameSubSubLayout = QtGui.QVBoxLayout()
        self.frame.nameSubLayout.addLayout(self.frame.nameSubSubLayout)
        self.rescanButton = QtGui.QPushButton("Rescan")
        self.rescanButton.setEnabled(True)
        self.rescanButton.clicked.connect(self.populateDeviceSelection)
        self.frame.nameSubSubLayout.addWidget(self.rescanButton)
        self.syncTypeLabel = QtGui.QLabel("Current mode:")
        self.syncTypeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.frame.nameSubSubLayout.addWidget(self.syncTypeLabel)
        self.syncType = QtGui.QLabel("<span style='font-weight:700;'>" + self.getCurrentMode() + "</span>")
        self.syncType.setAlignment(QtCore.Qt.AlignCenter)
        self.frame.nameSubSubLayout.addWidget(self.syncType)
        self.syncButton = QtGui.QPushButton("Sync")
        self.syncButton.setEnabled(False)
        self.frame.nameSubSubLayout.addWidget(self.syncButton)
        self.syncButton.clicked.connect(self.connect)

        ##################### FOLDER CONFIG ####################################

        self.folderGroupBox = QtGui.QGroupBox("Folder config")
        self.frame.folderLayout = QtGui.QVBoxLayout()

         # Local sync folder
        self.frame.browseFolderLayout = QtGui.QHBoxLayout()
        self.frame.browseFolderLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.currentFolderLabel = QtGui.QLabel("Current local sync folder:")
        self.frame.browseFolderLayout.addWidget(self.currentFolderLabel)
        self.displayLocalFolderLabel = QtGui.QLabel(self.path)
        self.frame.browseFolderLayout.addWidget(self.displayLocalFolderLabel)
        self.frame.browseFolderLayout.addStretch(1)
        self.selectSyncFolderButton = QtGui.QPushButton("Select sync folder")
        self.frame.browseFolderLayout.addWidget(self.selectSyncFolderButton)
        self.selectSyncFolderButton.clicked.connect(self.browse)
        self.selectSyncFolderButton.setMaximumWidth(99)
        self.frame.folderLayout.addLayout(self.frame.browseFolderLayout)

        # Remote target path
        self.frame.setTargetLayout = QtGui.QHBoxLayout()
        self.targetFolderLabel = QtGui.QLabel("Current remote target folder:")
        self.frame.setTargetLayout.addWidget(self.targetFolderLabel)
        self.targetFolderText = QtGui.QLineEdit(self.target_path)
        self.frame.setTargetLayout.addWidget(self.targetFolderText)
        self.selectTargetFolderButton = QtGui.QPushButton("Save")
        self.frame.setTargetLayout.addWidget(self.selectTargetFolderButton)
        self.selectTargetFolderButton.clicked.connect(self.setTarget)
        self.frame.folderLayout.addLayout(self.frame.setTargetLayout)
        self.folderGroupBox.setLayout(self.frame.folderLayout)
        self.frame.mainLayout.addWidget(self.folderGroupBox)

        if self.mode == "manual":
            self.enableManual(True)

        ############################### LOG ####################################

        self.textEdit = QtGui.QTextEdit(self)
        if self.verbose == "0":
            self.textEdit.hide()
            self.setGeometry(300, 300, 200, 200)
        self.frame.mainLayout.addWidget(self.textEdit)

        ############################## QUIT ####################################

        self.frame.actionLayout = QtGui.QHBoxLayout()
        self.frame.actionLayout.addStretch(2)
        self.frame.mainLayout.addLayout(self.frame.actionLayout)
        self.quitButton = QtGui.QPushButton("Cancel", self) # button is a child of window
        self.quitButton.clicked.connect(self.quit)
        self.frame.actionLayout.addWidget(self.quitButton)
        self.frame.setLayout(self.frame.mainLayout)

        ############################## OTHER ###################################

        self.show()
        # Populate device selection listwidget
        self.populateDeviceSelection()

    ############################### FUNCTIONS ##################################

    # For device selection listwidget: Populates/updates the list
    def populateDeviceSelection(self):
        self.rescanButton.setEnabled(False)
        self.syncButton.setEnabled(False)
        print "Scanning for devices..."
        if not (self.chooseName.count() == 0):
            self.chooseName.clear()
        self.deviceDiscoveryThread = devicefinder.DeviceDiscoveryThread()
        self.deviceDiscoveryThread.discoveryDone.connect(self.onDeviceDiscoveryDone)
        self.deviceDiscoveryThread.start()

    def onDeviceDiscoveryDone(self, availableDevices):
        if availableDevices:
            if len(availableDevices) == 0:
                print "No Bluetooth device in range. Please ensure your Bluetooth device is discoverable."
            for name in availableDevices:
                self.chooseName.addItem(name)
        self.chooseName.setEnabled(True)
        self.rescanButton.setEnabled(True)
        self.syncButton.setEnabled(False)
        print "Done."

    # For sync info (on the right of device selection): Return "readable" string for sync mode
    def getCurrentMode(self):
        prettyStrings = { "manual" : "Manual sync", "one-way0" : "One-way, PC >> device", "one-way1" : "One-way, device >> PC", "two-way" : "Two-way" }
        return prettyStrings[self.mode]

    # For menubar: Launches the settings window
    @QtCore.pyqtSlot()
    def launchSettings(self):
        self.settingsWindow = SettingsWindow(self)
        self.settingsWindow.exec_()
        self.timeout, self.path, self.target_path, self.mode, self.verbose = loadData()
        self.statusBar().showMessage("Ready")
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
            self.enableManual(True)
        else:
            self.enableManual(False)

    # For menubar: Launches the server
    @QtCore.pyqtSlot()
    def launch_server(self):
        self.serverWindow = ServerWindow(self)
        self.serverWindow.exec_()
        if not DEBUG:
            sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

    # When in manual mode, sets up UI for manual file sync
    def launch_manual(self):
        self.enableTop(False)
        self.container = QtGui.QWidget(self)
        self.container.manualSyncLayout = QtGui.QVBoxLayout()
        self.container.setLayout(self.container.manualSyncLayout)
        self.frame.mainLayout.addWidget(self.container)
        self.manualSync = QtGui.QListWidget(self)
        self.manualSync.itemDoubleClicked.connect(lambda: manualmode.openFolder(self)) # Make this a callable with self as parameter (not QListWidgetItem object)
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
        self.manualDisconnButton.clicked.connect(lambda: manualmode.disconnect(self))
        self.getButton.clicked.connect(lambda: manualmode.get(self))
        self.putFileButton.clicked.connect(lambda: manualmode.putFile(self))
        self.putFolderButton.clicked.connect(lambda: manualmode.putFolder(self))
        self.deleteButton.clicked.connect(lambda: manualmode.delete(self))
        self.backButton.clicked.connect(lambda: manualmode.back(self))
        self.newDirButton.clicked.connect(lambda: manualmode.newdir(self))
        manualmode.refresh(self)

    # If enable True, preps GUI for manual mode. Undoes this if enable False
    def enableManual(self, enable):
        self.folderGroupBox.setEnabled(not enable)

    # If enable True, enables the top section of the GUI. Undoes this if enable False
    def enableTop(self, enable):
        self.nameLabel.setEnabled(enable)
        self.chooseName.setEnabled(enable)
        self.rescanButton.setEnabled(enable)
        self.syncButton.setEnabled(enable)
        self.syncTypeLabel.setEnabled(enable)
        self.syncType.setEnabled(enable)

    # Handles log output
    def normalOutputWritten(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()

    # Handles closing event
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, "Quit", "Are you sure you want to quit? All settings will be saved.", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            saveData(self.timeout, self.path, self.target_path, self.mode, self.verbose)
            event.accept()
        else:
            event.ignore()

    # For quit button
    def quit(self):
        reply = QtGui.QMessageBox.question(self, "Quit", "Are you sure you want to quit? All settings will be saved.", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            saveData(self.timeout, self.path, self.target_path, self.mode, self.verbose)
            QtCore.QCoreApplication.instance().quit()

    # Enables the sync button when device name is selected
    def nameSelected(self):
        self.syncButton.setEnabled(True)

    # For get sync folder
    def browse(self):
        startingDir = os.path.expanduser("~")
        self.path = str(QtGui.QFileDialog.getExistingDirectory(None, 'Open working directory', startingDir, QtGui.QFileDialog.ShowDirsOnly))
        self.displayLocalFolderLabel.setText(self.path)

    # For save target folder
    def setTarget(self):
        self.target_path = str(self.targetFolderText.text())

    # Establish a connection to the selected device
    def connect(self):
        self.enableTop(False)
        self.connectThread = connect.ConnectionThread(self.getCurrentMode(), str(self.chooseName.selectedItems()[0].text()))
        self.connectThread.connectDone.connect(self.onConnect)
        self.connectThread.start()

    def onConnect(self, client):
        if not client:
            message = "Could not connect to target device. Make sure the target device has Bluetooth turned on, is discoverable and paired with this computer. Also, make sure that your device supports OBEX file transfer and that you select 'OBEX File Transfer' from the services menu."
            QtGui.QMessageBox.warning(self, "Connection Error", message, QtGui.QMessageBox.Ok)
            return
        self.client = client
        try:
            if "one-way" in self.mode:
                if "0" in self.mode:
                    message = "Are you sure you want to one-way-sync {0} to the remote device? The contents of {1} on the remote device will be lost and overwritten by the new contents.".format(self.path, self.target_path)
                    reply = QtGui.QMessageBox.question(self, "Attention: Possible loss of files", message, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        autosync.find_target_folder(self.client, self.target_path)
                        print "Syncing..."
                        autosync.one_way_sync(self.client, self.path, self.target_path)
                    else: pass
                else:
                    message = "Are you sure you want to one-way-sync {0} from the remote device? The contents of {1} on the computer will be lost and overwritten by the new contents.".format(self.target_path, self.path)
                    reply = QtGui.QMessageBox.question(self, "Attention: Possible loss of files", message, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        autosync.find_target_folder(self.client, self.target_path)
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
                        autosync.get_folder(self.client, self.path, "")
                    else: pass
                disconn = self.client.disconnect()
                if isinstance(disconn, PyOBEX.responses.Success):
                    print "Disconnected successfully."
                else:
                    print "Disconnection failed."
                self.enableTop(True)
            elif self.mode == "two-way":
                message = "Are you sure you want to two-way-sync {0} with {1} on the remote device? Files that do not exist in one of the locations will be added to the other, and older file versions will be overwritten.".format(self.path, self.target_path)
                reply = QtGui.QMessageBox.question(self, "Attention: Possible loss of files", message, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes:
                    autosync.find_target_folder(self.client, self.target_path)
                    print "Syncing..."
                    autosync.two_way_sync(self.client, self.path)
                else: pass
                disconn = self.client.disconnect()
                if isinstance(disconn, PyOBEX.responses.Success):
                    print "Disconnected successfully."
                else:
                    print "Disconnection failed."
                self.enableTop(True)
            elif self.mode == "manual":
                self.launch_manual()
        except IOError:
            message = "Could not connect to target device. Make sure the target device has Bluetooth turned on, is discoverable and paired with this computer. Also, make sure that your device supports OBEX file transfer and that you select 'OBEX File Transfer' from the services menu."
            QtGui.QMessageBox.warning(self, "Connection Error", message, QtGui.QMessageBox.Ok)
            self.enableTop(True)
            return

# Helper class for StdOut IO
class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

# Server window class
class ServerWindow(QtGui.QDialog):
    def __init__(self, parent=SyncBlueMainWindow):
        super(ServerWindow, self).__init__(parent)
        if not DEBUG:
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
        self.server = eu.syncblue.server.SyncBlueServer()
        self.abortServerButton.setEnabled(True)
        self.startServerButton.setEnabled(False)
        self.server_sock = self.server.start_service() # Returns BluetoothSocket object
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
        except IOError: # If attempting to disconnect a disconnected socket
            print "The connection has been lost. Terminating server..."
            self.server_sock.close()
            print "Server terminated."

# Settings window class
class SettingsWindow(QtGui.QDialog):
    def __init__(self, parent=SyncBlueMainWindow):
        super(SettingsWindow, self).__init__(parent)
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
        self.timeoutButton.clicked.connect(self.timeoutSetting)
        self.horizontalLayout_2.addWidget(self.timeoutButton)
        self.horizontalLayout_2.addStretch(2)
        # Sub-Layout for select sync mode
        self.groupBox = QtGui.QGroupBox("Set sync mode:")
        self.oneWaySyncLayout = QtGui.QHBoxLayout()
        self.oneWaySyncButton = QtGui.QRadioButton("One-way synchronization:")
        self.oneWaySyncButton.clicked.connect(self.selectSyncMode)
        self.oneWaySyncLayout.addWidget(self.oneWaySyncButton)
        self.oneWaySyncLabel1 = QtGui.QLabel("PC >> Device")
        self.oneWaySyncLayout.addWidget(self.oneWaySyncLabel1)
        self.oneWaySyncSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.oneWaySyncSlider.setMaximum(1)
        self.oneWaySyncLayout.addWidget(self.oneWaySyncSlider)
        self.oneWaySyncLabel2 = QtGui.QLabel("Device >> PC")
        self.oneWaySyncLayout.addWidget(self.oneWaySyncLabel2)
        self.twoWaySyncButton = QtGui.QRadioButton("Two-way synchronization")
        self.twoWaySyncButton.clicked.connect(self.selectSyncMode)
        self.manualSyncButton = QtGui.QRadioButton("Manual synchronization")
        self.manualSyncButton.clicked.connect(self.selectSyncMode)
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
    app_icon.addPixmap(QtGui.QPixmap(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'icon.ico'))), QtGui.QIcon.Normal)
    app.setWindowIcon(app_icon)
    window = SyncBlueMainWindow()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()
