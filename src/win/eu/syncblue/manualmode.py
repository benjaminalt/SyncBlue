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

"""
from PyQt4 import QtGui, QtCore
import syncblue
import clientutils as utils
import os

def get(window):
    try:
        attributes = utils.get_attributes_target(window.client)
        row = window.manualSync.row(window.manualSync.selectedItems()[0])
        if attributes[row]["type"] == "file":
            headers, data = window.client.get(str(window.manualSync.selectedItems()[0].text()))
            dialog = QtGui.QFileDialog()
            dialog.setFileMode(QtGui.QFileDialog.AnyFile)
            filepath = str(QtGui.QFileDialog.getExistingDirectory(window, "Save as...", window.tempPath, QtGui.QFileDialog.ShowDirsOnly))
            print "Getting file..."
            print "Saving file at: ", filepath
            if window.tempPath:
                fo = open(os.path.join(filepath, attributes[row]["name"]), "wb")
            else:
                print "Please specify a valid path. \n GET aborted."
                return
            fo.write(data)
            fo.close()
            print "File transferred."
        else:
            window.tempPath = str(QtGui.QFileDialog.getExistingDirectory(window,
                                                         'Save as...',
                                                         window.tempPath,
                                                         QtGui.QFileDialog.ShowDirsOnly))
            window.client.setpath(str(window.manualSync.currentItem().text()))
            print "Getting folder..."
            utils.get_folder(window.client, window.tempPath, "")
            window.client.setpath(to_parent = True)
            print "Folder transferred."
        refresh(window)
    except IndexError:
        print "Please select a file or folder."

def putFile(window):
    filepath = (str(QtGui.QFileDialog.getOpenFileName(window, "Select File", window.tempPath)))
    if "/" in filepath:
        cutoff = filepath.rfind("/")
        window.tempPath = filepath[:cutoff]
    else:
        cutoff = 0
        window.tempPath = ""
    print "Temp path:", window.tempPath
    print "Filepath:", filepath
    if os.path.isfile(filepath):
        fo = open(filepath, "rb")
        data = fo.read()
        if cutoff != 0:
            window.client.put(filepath[cutoff+1:], data)
        else:
            window.client.put(filepath[cutoff:], data)
    refresh(window)

def putFolder(window):
    filepath = str(QtGui.QFileDialog.getExistingDirectory(window, "Select Folder", window.tempPath, QtGui.QFileDialog.ShowDirsOnly))
    print "Filepath:", filepath
    if "\\" in filepath:
        cutoff = filepath.rfind("\\")
        window.tempPath = filepath[:cutoff]
    else:
        cutoff = 0
        window.tempPath = ""
    print "Temp path:", window.tempPath
    print "Filepath:", filepath
    if cutoff != 0:
        window.client.setpath(filepath[cutoff+1:], create_dir = True)
        utils.one_way_sync(window.client, filepath, filepath[cutoff+1:])
    else:
        window.client.setpath(filepath[cutoff:], create_dir = True)
        utils.one_way_sync(window.client, filepath, filepath[cutoff:])
    refresh(window)

def newdir(window):
    dirname, ok = QtGui.QInputDialog.getText(window, 'Directory name', 'New folder')
    dirname = str(dirname)
    if ok:
        window.client.setpath(dirname, create_dir = True)
        window.client.setpath(to_parent = True)
        window.refresh(window)()

def back(window):
    window.client.setpath(to_parent = True)
    refresh(window)

def delete(window):
     reply = QtGui.QMessageBox.question(window, "Delete", "Are you sure you want to delete permanently?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
     if reply == QtGui.QMessageBox.Yes:
         window.client.delete(str(window.manualSync.currentItem().text()))
         refresh(window)

def openFolder(window):
    contents = utils.get_attributes_target(window.client)
    row = window.manualSync.row(window.manualSync.selectedItems()[0])
    if contents[row]["type"] == "folder":
        window.client.setpath(str(window.manualSync.selectedItems()[0].text()))
        refresh(window)

def refresh(window):
    contents = utils.get_attributes_target(window.client)
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
    except (AttributeError, IOError):
        print "The device is not available anymore."
        window.enableTop(True)
        window.container.hide()
