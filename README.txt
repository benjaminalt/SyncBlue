SyncBlue Version 0.3 03/24/2016

SyncBlue is a cross-platform program that allows file and folder
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
        and type "python eu/syncblue/syncblue.py".

        Make sure you are running the correct version of Python
        (Python 2.7, https://www.python.org/download/releases/2.7/)
        and install the following modules:

        PyBluez (https://code.google.com/p/pybluez/downloads/list)
        PyOBEX (https://pypi.python.org/pypi/PyOBEX/0.26)
        PyQt4 (http://sourceforge.net/projects/pyqt/files/PyQt4)

        If the program does not launch or you are not able to connect to a
        device, it is most likely that the Python Bluetooth libraries do not
        support your system's Bluetooth stack. For further assistance, just
        email me at benjamin_alt@outlook.com.


2. USAGE & OPTIONS

    2.1. Connecting to a device

        Select the device you want to connect to from the topmost list and click
        "Sync". If your device does not show up or the connection fails, check
        section 2.1.1 ("Troubleshooting connections") for possible reasons.

        Most (but not all) target devices will only accept an incoming Bluetooth
        connection if the device has been paired with your computer. Therefore, when
        the "Sync" button is clicked, SyncBlue will wait for you to accept the pairing
        on the target device and continue automatically once the devices are paired.

        2.1.1 Troubleshooting connections

        1. Make sure Bluetooth is turned on both on your computer and on the target device.
        2. Ensure that the target device is within range ( < 5 m.)
        3. Check that your target device is discoverable and can accept incoming connection requests.

        If the problem persists, your target device probably does not support OBEX file transfer
        and is incompatible with SyncBlue. Windows computers do not advertise OBEX file transfer
        out of the box and are thus (still) not suitable as target devices.

    2.2. Synchronization

        The default sync mode is "manual sync". To change the sync mode, click "settings".

        One-way sync and two-way sync require the user to specify a sync folder on the
        home device (i.e. the computer running SyncBlue) and remote sync folder on the target device.
        It is possible to specify a target folder that does not exist yet.
        As long as the parent directory exists, SyncBlue will create the sync folder at the desired
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

Does not work with Windows 7, 8 or 8.1 computers as target (!!) devices. Generally, compatibility does not
depend on the platform of the target device (cross-platform synchronization is supported, so Mac/Android/Linux
target devices are no problem) but only on whether the target device advertises and supports the OBEX File
Transfer protocol as well as SDP (Service Discovery Protocol).

Copyright 03/24/2016 Benjamin Alt (benjamin_alt@outlook.com)
