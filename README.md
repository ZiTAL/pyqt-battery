# pyqt-battery #  
Another fucking battery monitor build in python3 + pyqt5  

# dependencies #  
To install dependencies:  
```
apt-get install python3-pyqt5 acpi
```

# skins #  
Customizable skins, see **skins/default**.  

# standalone #
Standalone version at https://github.com/ZiTAL/pyqt-battery/tree/master/dist  
Also needs **skins** and **acpi** command.

# usage #  
```
Arguments:
     -i, --interval    time to refresh in miliseconds   (default: 1000)
    -nd, --no-desktop  no desktop application           (default: show)
    -nt, --no-tray     no tray application              (default: show)
     -s, --skin         skin folder name                 (default: default)
     -h, --help         show this help

Examples:
    python3 pyqt-battery.py -i 2000 -nd
    python3 pyqt-battery.py -nt
    python3 pyqt-battery.py -s dark
```