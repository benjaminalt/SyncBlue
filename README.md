# SyncBlue
Software for peer-to-peer, cloudless, cross-platform file synchronization.

SyncBlue is a cross-platform program that allows file and folder
synchronization via Bluetooth. It also serves as a general-purpose OBEX client and
server.
It is open source and published under the GNU General Public License
(GPL, http://www.gnu.org/licenses/gpl-3.0.txt).

Current Version: 0.4

**Attention: The server functionality is still in a beta stage and has been tested only under Windows 10 with the Python, Windows and Mac clients. Before syncing anything, be sure to backup important files,
as loss of files may occur, particularly when syncing whole folders or using the server in one-way or two-way automatic mode.**

For binary **installer downloads** (.exe, .pkg), installation instructions and further information on the releases, visit [our website](www.syncblue.eu).
You can also get the released installers and corresponding source code archives [here](https://github.com/benjaminalt/SyncBlue/releases).

## Installing & running the source

1.  Fork/clone the repository.
2.  Install dependencies:

         python -m "pip install pybluez"

    Clone [PyOBEX](https://bitbucket.org/dboddie/pyobex/) and install it:

        cd pyobex
        python setup.py install

    Finally, download [PyQT4](https://www.riverbankcomputing.com/software/pyqt/download) for your platform and install it.
3.  You should be good to go! Just run the program:

        python src/win/syncblue.py

## Still to do

### Release 0.5 : Contributers wanted!!!
* New logo?
* Python client: Threaded manual mode put/get/etc. operations --> gray out put/get/etc. buttons while transferring OR use multiple BrowserClient
instances
* Manual mode as tree view
* More intelligent two-way-sync (avoid duplication for deleted/moved files)
* Connection via WiFi ad-hoc network (AirDrop-style) and sync using FTP.
    * Windows: Ad-hoc network via [netsh](http://www.nextofwindows.com/how-to-turn-your-windows-8-computer-into-a-wireless-hotspot-access-point)
