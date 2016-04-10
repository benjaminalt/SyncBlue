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

Collection of methods for browsing remote file systems using Bluetooth/OBEX

"""
import sys
import re
import PyOBEX.client
import datetime

# Returns list of dicts with objects' attributes (type, name, date) in the current folder on the target device
def get_folder_attributes_remote(client):
    try:
        # print client.listdir()
        headers, data = client.listdir()
    except TypeError as e:
        print client.listdir()
        print e
        sys.exit(1)
    files_and_folders = data.splitlines()
    if "<parent-folder/>" in files_and_folders:
        files_and_folders = files_and_folders[4:len(files_and_folders)-1]
    else:
        files_and_folders = files_and_folders[3:len(files_and_folders)-1]
    datalist = []
    folder_re = re.compile(r'folder name=".*?"', re.UNICODE)
    file_re = re.compile(r'file name=".*?"', re.UNICODE)
    datetime_re = re.compile(r'modified=".*?"', re.UNICODE)
    for item in files_and_folders:
        tempdict = {}
        tempdict["type"] = "folder" if re.findall(folder_re, item) else "file"
        if tempdict["type"] == "folder":
            tempdict["name"] = re.sub('folder name="', '', re.findall(folder_re, item)[0]).rstrip('"')
        elif tempdict["type"] == "file":
            tempdict["name"] = re.sub('file name="', '', re.findall(file_re, item)[0]).rstrip('"')
        else:
            return
        if (re.findall(datetime_re, item)):
            temptime = re.sub('modified="','', re.findall(datetime_re, item)[0]).rstrip('"').replace("T", "").replace("Z", "")
            tempdict["date"] = datetime.datetime.strptime(temptime, "%Y%m%d%H%M%S").replace(second = 0)
        else:
            tempdict["date"] = datetime.datetime.today()            # Fix this?
        datalist.append(tempdict)
    return datalist
