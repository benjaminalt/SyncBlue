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

from PyQt4 import QtCore
import os, sys

DEBUG = False
DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data.txt")

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
    if os.path.exists(DATA_PATH):
        fo = open(DATA_PATH, "r")
        timeout = fo.readline().rstrip()
        path = fo.readline().rstrip()
        target_path = fo.readline().rstrip()
        mode = fo.readline().rstrip()
        verbose = fo.readline().rstrip()
        fo.close()
    return timeout, path, target_path, mode, verbose

def saveData(timeout, path, target_path, mode, verbose):
    fo = open(DATA_PATH, "w")
    fo.write("{0}\n{1}\n{2}\n{3}\n{4}".format(str(timeout), str(path), str(target_path), str(mode), str(verbose)))
    fo.close()

def debug(message):
    if DEBUG:
        print message
        sys.stdout.flush()

# Helper class for StdOut IO
class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))
