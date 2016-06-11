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
from eu.syncblue.core import utils
from PyQt4 import QtGui
import sys, os

def main():
    app = QtGui.QApplication(sys.argv)
    app_icon = QtGui.QIcon()
    icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icon.ico")
    app_icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal)
    app.setWindowIcon(app_icon)
    window = mainWindow.SyncBlueMainWindow()
    sys.exit(app.exec_())

if __name__=='__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--debug", "-d", "/debug", "/D", "/d"]:
            utils.DEBUG = True
    main()
