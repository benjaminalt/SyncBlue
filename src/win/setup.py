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

sys.path.append(r"C:\Users\benjaminalt\Desktop\build_SyncBlue\Microsoft.VC90.CRT")
sys.path.append(r"C:\Python27\Lib\site-packages\PyQt4\plugins\imageformats")

setup(windows = [{"script": r"eu\syncblue\syncblue.py", "icon_resources": [(0, r"icon.ico")]}],
      options =  {
          "py2exe":
          {"packages":   ["PyOBEX", "bluetooth", "PyQt4"], "includes": ["sip"]
          , "bundle_files": 1,
          "dll_excludes":['QtCore4.dll','QtGui4.dll', "MSVCP90.dll","libzmq.pyd","geos_c.dll","api-ms-win-core-string-l1-1-0.dll","api-ms-win-core-registry-l1-1-0.dll","api-ms-win-core-errorhandling-l1-1-1.dll","api-ms-win-core-string-l2-1-0.dll","api-ms-win-core-profile-l1-1-0.dll","api-ms-win*.dll","api-ms-win-core-processthreads-l1-1-2.dll","api-ms-win-core-libraryloader-l1-2-1.dll","api-ms-win-core-file-l1-2-1.dll","api-ms-win-security-base-l1-2-0.dll","api-ms-win-eventing-provider-l1-1-0.dll","api-ms-win-core-heap-l2-1-0.dll","api-ms-win-core-libraryloader-l1-2-0.dll","api-ms-win-core-localization-l1-2-1.dll","api-ms-win-core-sysinfo-l1-2-1.dll","api-ms-win-core-synch-l1-2-0.dll","api-ms-win-core-heap-l1-2-0.dll","api-ms-win-core-handle-l1-1-0.dll","api-ms-win-core-io-l1-1-1.dll","api-ms-win-core-com-l1-1-1.dll","api-ms-win-core-memory-l1-1-2.dll","api-ms-win-core-version-l1-1-1.dll","api-ms-win-core-version-l1-1-0.dll"]
,}
          },
      data_files = [("Microsoft.VC90.CRT", glob(os.path.normcase(r"C:\Users\benjaminalt\Desktop\build_SyncBlue\Microsoft.VC90.CRT\*.*"))),
              ('imageformats', [r'C:\Python27\Lib\site-packages\PyQt4\plugins\imageformats\qico4.dll']),
               ('.',[r'C:\Python27\Lib\site-packages\PyQt4\QtCore4.dll',
                r'C:\Python27\Lib\site-packages\PyQt4\QtGui4.dll']),
      ('.',[r"icon.ico", r"C:\Users\benjaminalt\Desktop\Projects\SyncBlue\README.txt", r"C:\Users\benjaminalt\Desktop\Projects\SyncBlue\LICENSE.txt"])])
