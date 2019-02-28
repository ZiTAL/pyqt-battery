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
    battery = {}
    _skin_dir = path.dirname(path.realpath(__file__))+"/skins"
    _alert_show = True

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
                self._skin_dir = self._skin_dir+"/"+argv[i+1]
            else:
                self._skin_dir = self._skin_dir+"/default"

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
            # ikonoarentzako aldi baterako fitxategi batean sartuko dugu
            fp = NamedTemporaryFile(delete=True)
            fp.write(self._getIcon())
            # ikonoa fitxategia denean, guk base64-n daukagu
            # self.tray_icon = SystemTrayIcon(QtGui.QIcon('favicon3.png'), self)
            #self.tray_icon = QSystemTrayIcon(QIcon(fp[1]), self)
            self.tray_icon = QSystemTrayIcon(QIcon(fp.name), self)
            # ikonoa sortu eta gero ezabatu
            fp.close()

            # menua sortu
            self._setMenu()

            # tray_icon-ean click/right click egiterakoan sortzen den ebentoa
            self.tray_icon.activated.connect(self._iconActivated)

            # tray-a erakutsi
            self.tray_icon.show()

    def _desktopUI(self):
        if self._desktop:
            fp = NamedTemporaryFile(delete=True)
            fp.write(self._getIcon())
            self.setWindowIcon(QIcon(fp.name))
            fp.close()
            self.showMinimized()

    # ikonoa base64-n enkodeatu
    def _getIcon(self):
        print(self._skin_dir)
        
        img = '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'
        img64 = b64decode(img)
        return img64

    def _setMenu(self):
        menu = QMenu()
        # action_refresh = menu.addAction("Refresh")
        # action_refresh.triggered.connect(_updateInfo))
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
        b = Battery()
        self.battery = b.getInfo()        
        print('pyqt-battery:')
        print(self.battery)

        if self.battery['type']=='charging' or self.battery['type']=='full':
            self._alert_show = True

        if self.battery['error']==None:
            if self._tray and self._alert_percent <= self.battery['percent'] and self._alert_show == True and self.battery['type'] == 'discharging':
                self._alert_show = False
                self.tray_icon.showMessage('pyqt-battery: ATTENTION', self.battery['text'])

            elif self._tray and interactive == True:
                self.tray_icon.showMessage('pyqt-battery:', self.battery['text'])
            if self._desktop:
                self.setWindowTitle(self.battery['text'])
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
