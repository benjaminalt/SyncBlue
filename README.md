# BTSync
Software for peer-to-peer, cloudless, cross-platform file synchronization.

Version 0.1 02/15/2015


BTSync is a cross-platform program that allows file and folder
synchronization via Bluetooth.
It is open source and published under the GNU General Public License
(GPL, http://www.gnu.org/licenses/gpl-3.0.txt).


CONTENTS

1. Installation
1.1. MS Windows 7 or higher
1.2. Python source (Windows XP, Linux/UNIX)

2. Usage & options
2.1. Connecting to a device
2.2. Synchronization
2.2.1. One-way-sync
2.2.2. Two-way-sync
2.2.3. Manual sync

3. Known bugs & limitations



1. INSTALLATION

    1.1. Microsoft Windows (7 or higher)

        Run the installer.

    1.2. Python source (Python 2.7 on Windows XP, Linux/UNIX)
        
        It is possible to run the program on other platforms directly from
        the source code. To do so, extract the source folder, open a
        terminal/command-line utility, make the source folder your working directory
        and type "python BTSync.py".
        
        Make sure you are running the correct version of Python
        (Python 2.7, https://www.python.org/download/releases/2.7/)
        and install the following modules:
        
        PyBluez 0.20 (https://code.google.com/p/pybluez/downloads/list)
        PyOBEX 0.26 (https://pypi.python.org/pypi/PyOBEX/0.26)
        PyQt4 (http://sourceforge.net/projects/pyqt/files/PyQt4)
        
        If the program does not launch or you are not able to connect to a device,
        it is most likely that the Python Bluetooth libraries do not support your
        system's Bluetooth stack.
    
    

2. USAGE & OPTIONS
    
    2.1. Connecting to a device
    
        Most (but not all) target devices will only accept an incoming Bluetooth
        connection if the device has been paired with your computer. Therefore, before
        you attempt to establish a connection through BTSync, ensure that your
        computer and your device are paired.
        
        When BTSync is launched for the first time, the dropdown menu next to the
        "add device" button will be empty. To add a device, simply click "add device" and
        enter the Bluetooth name (not MAC address) of the target device when prompted.
        BTSync will save all added devices fur future use.
        Devices can always be added and removed in the settings.
        
        Select the device to connect to from the dropdown menu and click on "find services".
        If your device supports OBEX file transfer, "OBEX File Transfer" should appear
        in the box. If it does not, make sure Bluetooth is turned on both on your computer
        and on the target device, that the target device is within range ( < 5 m.)
        and that your target device is discoverable and can accept incoming connection requests.
        If the problem persists, your target device does not support OBEX file transfer
        and is incompatible with BTSync. Windows computers do not advertise OBEX file transfer
        out of the box and are thus (still) not suitable as target devices.
        
    2.2. Synchronization
    
        The default sync mode is "one-way sync". To change the sync mode, click "settings".
        
        One-way sync and two-way sync require the user to specify a sync folder on the
        home device (i.e. the computer running BTSync) and remote sync folder on the target device.
        It is possible to specify a target folder that does not exist yet.
        As long as the parent directory exists, BTSync will create the sync folder at the desired
        location.
        
        2.2.1. One-way sync
        
            By default, keeps the contents of the target folder identical to those on the home
            folder, i.e. deletes all contents of the target folder and replaces them with the
            contents of the home folder. The sync direction can be changed in the settings.
            
        2.2.2. Two-way sync
        
            Synchronizes the target and the home folder, i.e. keeps the most recent files and adds
            files and folders to either folder that are not present in the other folder. Does not
            delete files unless there is a more recent file in the other folder to replace it.
            
        2.2.3. Manual sync
        
            Enables the user to browse the files and folders on the remote device. Supports "put",
            "get", "delete" and "make folder" operations.
        
    
    
3. KNOWN BUGS & LIMITATIONS

Does not work with Windows 7, 8 or 8.1 computers as target devices. Generally, compatibility does not
depend on the platform of the target device (cross-platform synchronization is supported) but only on
whether the target device advertises and supports the OBEX File Transfer protocol as well as SDP
(Service Discovery Protocol).


Copyright 02/15/2015 Benjamin Alt (benjaminalt@arcor.de)