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

from eu.syncblue.core import utils
from PyQt4 import QtGui, QtCore

# Settings window class
class SettingsWindow(QtGui.QDialog):
    def __init__(self, parent):
        super(SettingsWindow, self).__init__(parent)
        self.tempTimeout, self.path, self.target_path, self.mode, self.verbose = utils.loadData()
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
        utils.saveData(self.tempTimeout, self.path, self.target_path, self.mode, self.verbose)
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
