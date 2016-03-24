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

from distutils.core import setup
from glob import glob
import os
import sys
import py2exe

sys.path.append(r"C:\Users\benjaminalt\Documents\Visual Studio 2013\Projects\SyncBlue\dlls")
sys.path.append(r"C:\Python27\Lib\site-packages\PyQt4\plugins\imageformats")

setup(windows = [{"script": r"\eu\syncblue\syncblue.py", "icon_resources": [(0, r"icon.ico")]}],
      options =  {
          "py2exe":
          {"packages":   ["PyOBEX", "bluetooth", "PyQt4"], "includes": ["sip"]
          , "bundle_files": 1,
          "dll_excludes":['QtCore4.dll','QtGui4.dll'],}
          },
      data_files = [("Microsoft.VC90.CRT", glob(os.path.normcase(r"C:\Users\benjaminalt\Documents\Visual Studio 2013\Projects\SyncBlue\dlls\*.*"))),
              ('imageformats', [r'C:\Python27\Lib\site-packages\PyQt4\plugins\imageformats\qico4.dll']),
               ('.',[r'C:\Python27\Lib\site-packages\PyQt4\QtCore4.dll',
                r'C:\Python27\Lib\site-packages\PyQt4\QtGui4.dll']),
      ('.',[r"C:\Users\benjaminalt\Documents\Visual Studio 2013\Projects\SyncBlue\icon.ico",
            r"C:\Users\benjaminalt\Documents\Visual Studio 2013\Projects\SyncBlue\network-bluetooth.ico",
            "addresses.txt", "data.txt", "README.txt", "LICENSE.txt"])])
