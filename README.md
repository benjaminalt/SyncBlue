# SyncBlue
Software for peer-to-peer, cloudless, cross-platform file synchronization.

SyncBlue is a cross-platform program that allows file and folder
synchronization via Bluetooth.
It is open source and published under the GNU General Public License
(GPL, http://www.gnu.org/licenses/gpl-3.0.txt).

Current Version: 0.3

For binary **installer downloads** (.exe, .pkg), installation instructions and further information on the releases visit www.syncblue.eu .
You can also get the released installers [here](https://github.com/benjaminalt/SyncBlue/releases).

## Installing & running the source

1.  Fork/clone the repository.
2.  Install dependencies:

         python -m "pip install pybluez"

    Clone [PyOBEX](https://bitbucket.org/dboddie/pyobex/) and install it:

        cd pyobex
        python setup.py install

    Finally, download [PyQT4](https://www.riverbankcomputing.com/software/pyqt/download) for your platform and install it.
3. You should be good to go!

## Still to do

### Release 0.4

* New logo?
* Python client: Threaded manual mode put/get/etc. operations --> gray out put/get/etc. buttons while transferring OR use multiple BrowserClient
instances
* Fully implement SyncBlue server (OBEX server on devices which do not natively support OBEX)
* Manual mode as tree view
* Multithreaded sending (opening more than one Bluetooth connection to the same device at the same time)
* More intelligent two-way-sync (DB to keep track of deleted & moved files to avoid duplication)
* Connection via WiFi (FTP) either when on the same network or establishing Airdrop-style ad-hoc network
