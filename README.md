# mp3pi

# Installation on Debian 9:

```
git clone https://github.com/mottobug/mp3pi
cd mp3pi
./setup.sh
```

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

## Wifi connect to hidden AP:
  nmcli c add type wifi con-name <conname> ifname wlan0 ssid <hiddenssid>
  nmcli device wifi connect "SSID" password "WLANPSK" hidden yes


## Play with custom Playlists
```
curl -A "User-Agent: XBMC Addon Radio" 'http://radio.de/info/menu/broadcastsofcategory?category=_top' | jq "." > radio.de.json

jq '[.[]|select(.name=="NDR 2" or .name=="RADIO BOB!")]' < radio.de.json


```


## Screenshots
![alt text](screenshots/screenshot.png "Description goes here")

