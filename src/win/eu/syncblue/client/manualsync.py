"""
Copyright 2016 Benjamin Alt
benjamin_alt@outlook.com

manualmode.py

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

Contains static methods and a Thread class for manual sync with a remote device.

"""
from PyQt4 import QtGui, QtCore
import obexfilebrowser, autosync
import os, sys
import PyOBEX.responses

# TODO: Do this in a separate thread
def get(window):
    try:
        attributes = obexfilebrowser.get_folder_attributes_remote(window.client)
        row = window.manualSync.row(window.manualSync.selectedItems()[0])
        if attributes[row]["type"] == "file":
            headers, data = window.client.get(str(window.manualSync.selectedItems()[0].text()))
            dialog = QtGui.QFileDialog()
            dialog.setFileMode(QtGui.QFileDialog.AnyFile)
            filepath = str(QtGui.QFileDialog.getExistingDirectory(window, "Save as...", window.tempPath, QtGui.QFileDialog.ShowDirsOnly))
            print "Getting file..."
            print "Saving file at: ", filepath
            with open(os.path.join(filepath, attributes[row]["name"]), "wb") as fo:
                fo.write(data)
            print "File transferred."
        else:
            window.tempPath = str(QtGui.QFileDialog.getExistingDirectory(window,
                                                         'Save as...',
                                                         window.tempPath,
                                                         QtGui.QFileDialog.ShowDirsOnly))
            window.client.setpath(str(window.manualSync.currentItem().text()))
            print "Getting folder..."
            autosync.get_folder(window.client, window.tempPath, "")
            window.client.setpath(to_parent = True)
            print "Folder transferred."
        refresh(window)
    except IndexError:
        print "Please select a file or folder."

# TODO: Do this in a separate thread
def putFile(window):
    filepath = (str(QtGui.QFileDialog.getOpenFileName(window, "Select File", window.tempPath)))
    if "/" in filepath:
        cutoff = filepath.rfind("/")
        window.tempPath = filepath[:cutoff]
    else:
        cutoff = 0
        window.tempPath = ""
    if os.path.isfile(filepath):
        with open(filepath, "rb") as fo:
            data = fo.read()
            if cutoff != 0:
                window.client.put(filepath[cutoff+1:], data)
            else:
                window.client.put(filepath[cutoff:], data)
    refresh(window)

# TODO: Do this in a separate thread
def putFolder(window):
    filepath = str(QtGui.QFileDialog.getExistingDirectory(window, "Select Folder", window.tempPath, QtGui.QFileDialog.ShowDirsOnly))
    if filepath:
        if "\\" in filepath:
            cutoff = filepath.rfind("\\")
            window.tempPath = filepath[:cutoff]
        else:
            cutoff = 0
            window.tempPath = ""
        # print "Temp path:", window.tempPath
        # print "Filepath:", filepath
        if cutoff != 0:
            window.client.setpath(filepath[cutoff+1:], create_dir = True)
            autosync.one_way_sync(window.client, filepath, filepath[cutoff+1:])
        else:
            window.client.setpath(filepath[cutoff:], create_dir = True)
            autosync.one_way_sync(window.client, filepath, filepath[cutoff:])
    refresh(window)

def newdir(window):
    dirname, ok = QtGui.QInputDialog.getText(window, 'Directory name', 'New folder')
    dirname = str(dirname)
    if ok:
        window.client.setpath(dirname, create_dir = True)
        window.client.setpath(to_parent = True)
        refresh(window)

def back(window):
    response = window.client.setpath(to_parent = True)
    if not isinstance(response, PyOBEX.responses.Success):
        reply = QtGui.QMessageBox.warning(window, "Failure", "The setpath request failed, probably because of bad permissions.", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
    refresh(window)

def delete(window):
     reply = QtGui.QMessageBox.question(window, "Delete", "Are you sure you want to delete permanently?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
     if reply == QtGui.QMessageBox.Yes:
         response = window.client.delete(str(window.manualSync.currentItem().text()))
         if not isinstance(response, PyOBEX.responses.Success):
             reply = QtGui.QMessageBox.warning(window, "Failure", "The delete request failed, probably because of bad permissions.", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
         refresh(window)

def openFolder(window):
    contents = obexfilebrowser.get_folder_attributes_remote(window.client)
    row = window.manualSync.row(window.manualSync.selectedItems()[0]) if len(window.manualSync.selectedItems()) > 0 else 0
    if contents[row]["type"] == "folder":
        response = window.client.setpath(str(window.manualSync.selectedItems()[0].text()))
        if not isinstance(response, PyOBEX.responses.Success):
            reply = QtGui.QMessageBox.warning(window, "Failure", "Could not open folder, probably because of bad permissions.", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
        refresh(window)

def refresh(window):
    contents = obexfilebrowser.get_folder_attributes_remote(window.client)
    window.manualSync.clear()
    for item in contents:
        window.manualSync.addItem(item["name"])

def disconnect(window):
    try:
        print "Disconnecting..."
        disconn = window.client.disconnect()
        if isinstance(disconn, PyOBEX.responses.Success):
            print "Disconnected successfully."
        else:
            print "Disconnection failed."
        window.enableTop(True)
        window.container.hide()
    except (AttributeError, IOError) as e:
        print e
        print "The device is not available anymore."
        window.enableTop(True)
        window.container.hide()
