#!/usr/bin/python3
# -*- coding: utf-8 -*-

# apt-get install python3-pyqt5 acpi

"""
Battery 0: Full, 100%
Battery 0: Discharging, 100%, 00:50:19 remaining
Battery 0: Charging, 82%, 00:06:17 until charged
"""

from PyQt5.QtWidgets import QMainWindow, QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer
from tempfile import NamedTemporaryFile
from base64 import b64decode
from re import sub, match
from sys import argv, exit
from subprocess import Popen, PIPE
from os import path

class Battery:
    command = '/usr/bin/acpi'

    def __init__(self):
        pass

    def getInfo(self):
        result = Popen(self.command, shell=False, stdout=PIPE)
        stdout, stderr = result.communicate()

        result = {}

        if stderr != None:
            result['error'] = stderr.decode('utf-8')
        else:
            """
            Battery 0: Full, 100%
            Battery 0: Discharging, 100%, 00:50:19 remaining
            Battery 0: Charging, 82%, 00:06:17 until charged
            """            
            r = stdout.decode('utf-8')
            # r = 'Battery 0: Full, 100%'
            # r = 'Battery 0: Discharging, 100%, 00:50:19 remaining'
            # r = 'Battery 0: Charging, 82%, 00:06:17 until charged'
            r = sub(r"^Battery [0-9]+:\s*", '', r)
            r = sub(r"\s+$", '', r);
            p = match(r"([^,]+),\s+([0-9]+)%($|,\s+([0-9]{2}:[0-9]{2}:[0-9]{2})\s+([^$]+)$)", r)

            result['error'] = None
            result['type'] = p.group(1).lower()
            result['percent'] = int(p.group(2))
            result['text'] = r

        return result

class Window(QMainWindow):
    _skin_dir = path.dirname(path.realpath(__file__))+"/skins"

    def __init__(self, argv):
        # QMainWindow-en construct-a
        super(Window, self).__init__()
        # Bateriaren informazioa kargatu
        b = Battery()
        self.battery = b.getInfo()        
        # kontsolatik bidali dizkiogun parametroak programan sartu
        self._parseArgv(argv)
        # focus mota teklatu eta saguarenak aukeratzen ditugu
        self.setFocusPolicy(Qt.StrongFocus)
        self._initUI()

    def _parseArgv(self, argv):
        self._credentials = {}
        self._interval = 1000
        self._tray = True
        self._desktop = True
        i = 0
        for arg in argv:
            if argv[i]=='-i' or argv[i]=='--interval':
                self._interval = eval(argv[i+1])
            if argv[i]=='-nt' or argv[i]=='--no-tray':
                self._tray = False
            if argv[i]=='-nd' or argv[i]=='--no-desktop':
                self._desktop = False
            if argv[i]=='-s' or argv[i]=='--skin':
                self._skin_dir = self._skin_dir+"/"+argv[i+1]+"/"
            else:
                self._skin_dir = self._skin_dir+"/default/"

            if argv[i]=='-ap' or argv[i]=='--alert-percent':
                self._alert_percent = int(argv[i+1])
            else:
                self._alert_percent = 10

            i = i + 1

        if self._tray == False and self._desktop == False:
            print('Tray or Desktop option required')
            self._help()

    def _initUI(self):
        # tray-a jarri
        self._trayUI()

        # interval parametroan sartu dugun aldiro informazioa eguneratu
        self._setTimer()

        # desktop aplikazioa jarri
        self._desktopUI()

        # kargatzerakoan datuak hartu
        self._updateInfo(True)        

    def _trayUI(self):
        if self._tray:
            self._setIcon()

            # menua sortu
            self._setMenu()

            # tray_icon-ean click/right click egiterakoan sortzen den ebentoa
            self.tray_icon.activated.connect(self._iconActivated)

            # tray-a erakutsi
            self.tray_icon.show()

    def _desktopUI(self):
        if self._desktop:
            self._setIcon()
            self.showMinimized()

    # ikonoa base64-n enkodeatu
    def _getIcon(self):
        # hondarrarekin jolasten dugu, iconoaren path-a egokitzeko
        p = self.battery['percent']
        pp = int(p / 10) * 10
        if p%10>5:
            pp = pp + 10
        pp = str(pp)

        icon = self._skin_dir+self.battery['type']+"_"+pp+".png"
        return icon

    def _setIcon(self):
        icon = self._getIcon()

        if self._desktop:
            self.setWindowIcon(QIcon(icon))

        if self._tray:
            self.tray_icon = QSystemTrayIcon(QIcon(icon), self)            

    def _setMenu(self):
        menu = QMenu()
        action_exit = menu.addAction('Exit')
        action_exit.triggered.connect(exit)
        self.tray_icon.setContextMenu(menu)

    def _iconActivated(self, reason):
        if reason == 1:
            # right click
            pass
        elif reason == 3:
            # left click
            self._updateInfo(True)
            pass

    def _setTimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._updateInfoFalse)
        self.timer.start(self._interval)

    def _updateInfoFalse(self):
        self._updateInfo(False)

    def _updateInfo(self, interactive):
        battery_old = self.battery

        b = Battery()
        self.battery = b.getInfo()

        if self.battery['error']==None:

            if self._tray and interactive == True:
                self.tray_icon.showMessage('pyqt-battery:', self.battery['text'])

            if self._desktop:
                self.setWindowTitle(self.battery['text'])

            self._setIcon()
        else:
            print(self.battery['error'])
            exit()

    def _help(self):
        h = """
py-battery:
Arguments:
    -i,  --interval    time to refresh in miliseconds
    -nd, --no-desktop  no desktop application
    -nt, --no-tray     no tray application
    -s, --skin         default skin is: default
        """
        print(h)
        exit()

    def focusInEvent(self, event):
        self._updateInfo(True)
        self.showMinimized()

if __name__ == '__main__':
    app = QApplication([])
    w = Window(argv)
exit(app.exec_())
