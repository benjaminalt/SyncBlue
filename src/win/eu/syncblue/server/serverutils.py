"""
Copyright 2016 Benjamin Alt
benjamin_al@outlook.com

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
from PyOBEX import requests
import os, sys
import datetime

# Set encoding to prevent UnicodeDecodeError when directory contains files with non-ascii filenames
#reload(sys)  
#sys.setdefaultencoding('utf8')

# Returns XML string for response to "listdir"-type requests
def get_files_xml(path):
    filesAndDirs = get_files_and_dirs(path)
    xmlString = '<?xml version="1.0"?>\r\n<!DOCTYPE folder-listing SYSTEM "obex-folder-listing.dtd">\r\n<folder-listing version="1.0">\r\n'
    if "has_parent" in filesAndDirs:
        xmlString += '<parent-folder/>\r\n'
    for item in filesAndDirs:
        if type(item) is dict:
            xmlString += '<{} name="{}" size="{}" user-perm="{}" modified="{}"/>\r\n'.format(item["type"], item["name"], item["size"], item["user-perm"], item["modified"])
    xmlString += '</folder-listing>\r\n'
    return xmlString

# Returns list of dictionaries with relevant information about files and
# folders in path. List also contains string entry if path has parent dir.
def get_files_and_dirs(path):
    filesAndDirs = []
    for name in os.listdir(path):
        filepath = os.path.join(path, name)
        type = "folder" if os.path.isdir(filepath) else "file"
        size = str(os.stat(filepath).st_size)
        user_perm = get_permissions(filepath)
        modified = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
        modified = modified.strftime("%Y%m%dT%H%M%SZ")
        newEntry = {
            "name": name,
            "type": type,
            "size": size,
            "user-perm": user_perm,
            "modified": modified
        }
        filesAndDirs.append(newEntry)
    if os.path.exists(os.pardir):
        filesAndDirs.append("has_parent")
    return filesAndDirs

# Returns "R" if file readable, "RW" if file readable and writable
def get_permissions(filepath):
    perms = ""
    if os.access(filepath, os.R_OK):
        perms += "R"
    if os.access(filepath, os.W_OK):
        perms += "W"
    return perms

# Dissects a request and prints information if utils.DEBUG is set
def dissect_request(request):
    utils.debug("\n\nRequest: {}".format(request))
    utils.debug("\tIs final: {}".format(request.is_final()))
    for header in request.header_data:
        utils.debug("\t{}: {}".format(header, header.decode()))
    utils.debug("\tData: {}".format(request.data))

# Dissects a response and prints information if utils.DEBUG is set
def dissect_response(response):
    utils.debug("\n\nResponse: {}".format(response))
    for header in response.header_data:
        utils.debug("\t{}: {}".format(header, header.data))
    utils.debug("\tData: {}".format(response.data))