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

################################################################################

Entry point to SyncBlue.

"""

from eu.syncblue.core import main as mainWindow
from PyQt4 import QtGui
import sys

def main():
    app = QtGui.QApplication(sys.argv)
    app_icon = QtGui.QIcon()
    app_icon.addPixmap(QtGui.QPixmap('icon.ico'), QtGui.QIcon.Normal)
    app.setWindowIcon(app_icon)
    window = mainWindow.SyncBlueMainWindow()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()
