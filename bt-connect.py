#!/usr/bin/python


import dbus
import bluezutils


def dev_connect(path):
  dev = dbus.Interface(bus.get_object("org.bluez", path), "org.bluez.Device1")
  dev.Connect()


bus = dbus.SystemBus()
device = bluezutils.find_device("0C:A6:94:E3:76:DA")

dev_connect(device.object_path)

dev_path = device.object_path

print(device.object_path)

