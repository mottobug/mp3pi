# mp3pi

## Requirements on Ubuntu:

apt-get install libbluetooth-dev bc pulseaudio

pip install pyalsaaudio pybluez python-networkmanager pygments

# Installation on Debian 9:

```
git clone https://github.com/mottobug/mp3pi
cd mp3pi
./setup.sh
```

(from https://kivy.org/docs/installation/installation-rpi.html)

## Turn auto exit in pulseaudio off
```
echo "exit-idle-time = -1" >> /etc/pulse/daemon.conf
```

Modifications on ~/.kivy/config.ini
```
[input]
mouse = mouse
%(name)s = probesysfs,provider=hidinput
mtdev_%(name)s = probesysfs,provider=mtdev
hid_%(name)s = probesysfs,provider=hidinput
```


```
systemctl set-default multi-user.target

cp systemd/mp3pi.service /etc/systemd/system
cp systemd/pulseaudio.service /etc/systemd/system
systemctl enable mp3pi
systemctl enable pulseaudio
```

https://github.com/graysky2/pulseaudio-ctl

?? gir1.2-networkmanager-1.0 gir1.2-nmgtk-1.0 libnm-dev libnm-glib-dev libnm-glib-vpn-dev libnm-gtk-dev
  libnm-util-dev libnmap-parser-perl libnmz7 libnmz7-dev network-manager-dev ??

## Disable WLAN power management:
  echo "KERNEL==\"wlan*\", ACTION==\"add\", RUN+=\"/sbin/iwconfig wlan0 power off\"" > /etc/udev/rules.d/10-wlan-powersavings-off.rules

## Screen is turned upside down:
  add "lcd_rotate=2" to /boot/config.txt

## Undervolt symbol in upper right is bugging you:
  add "avoid_warnings=1" to /boot/config.txt

## Add Splash Screen:
```
  apt-get install plymouth
  plymouth-set-default-theme tribar
```

  Add "quiet splash" to the kernel cmdline /boot/cmdline.txt

## Turn off console screensaver (1 hour by default)
  add "consoleblank=0" /boot/cmdline.txt

## Wifi list networks:
  nmcli device wifi list

## Wifi connect to AP:
  nmcli device wifi connect "SSID" password "WLANPSK"

## Optional Stuff
Change Hostname
```
echo "raspiradio" > /etc/hostname
sed -i "s/127.0.1.1.*raspberrypi/127.0.1.1\traspiradio/g" /etc/hosts
```

## Play with custom Playlists
```
curl -A "User-Agent: XBMC Addon Radio" 'http://radio.de/info/menu/broadcastsofcategory?category=_top' | jq "." > radio.de.json

jq '[.[]|select(.name=="NDR 2" or .name=="RADIO BOB!")]' < radio.de.json


```


## Screenshots
![alt text](screenshots/screenshot.png "Description goes here")

