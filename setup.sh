#!/bin/bash

# Author: Sascha Karnatz <https://github.com/kulturbande>

if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi

clear

echo "This script install all necessary components"
echo "to run the mp3pi - project on a fresh Raspian lite"
echo "installation. This will take a while."
echo
echo "A reboot is necessary!"
echo
echo -n "CONTINUE? [y/N] "
read
if [[ ! "$REPLY" =~ ^(yes|y|Y)$ ]]; then
	echo "Canceled."
	exit 0
fi


# update system
echo
echo "Update and Upgrade sysem..."
echo
apt-get --yes --force-yes update
apt-get --yes --force-yes upgrade

# kivy
echo
echo "Install Kivy..."
echo
## Kivy dependencies
apt-get --yes --force-yes install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
   pkg-config libgl1-mesa-dev libgles2-mesa-dev \
   python-setuptools libgstreamer1.0-dev git-core \
   gstreamer1.0-plugins-{bad,base,good,ugly} \
   gstreamer1.0-{omx,alsa} python-dev libmtdev-dev \
   xclip python-pip

## Cython
pip install -U Cython==0.28.2

## Kivy inself
pip install git+https://github.com/kivy/kivy.git@master

# MPG123
echo
echo "Install MPG123..."
echo
MPG123_VERSION="1.25.10"
# donwload and extract MPG123
wget http://mpg123.de/download/mpg123-$MPG123_VERSION.tar.bz2
tar xvjf mpg123-$MPG123_VERSION.tar.bz2
cd mpg123-$MPG123_VERSION

# install
./configure --with-audio=pulse
make
make install
cd ..
rm -rf mpg123-$MPG123_VERSION
rm mpg123-$MPG123_VERSION.tar.bz2

# set config
echo "/usr/local/lib" > /etc/ld.so.conf.d/locallib.conf
ldconfig

# Pulseaudio
echo
echo "Install Pulseaudio..."
echo
# get pulsaudio
apt-get --yes --force-yes install git pulseaudio pulseaudio-utils libpulse-dev bc
git clone https://github.com/graysky2/pulseaudio-ctl.git
cd pulseaudio-ctl

# install
make install
echo "exit-idle-time = -1" >> /etc/pulse/daemon.conf

# remove folder
cd ..
rm -rf pulseaudio-ctl

# Network Manager
echo
echo "Install Network Manager..."
echo

# install
apt-get --yes --force-yes install network-manager
rm /etc/network/interfaces

# Radio
echo
echo "Setup Radio..."
echo

# additional packages
apt-get --yes --force-yes install python-requests mtdev-tools

# add systemd services
cd systemd
cp mp3pi.service /etc/systemd/system
cp pulseaudio.service /etc/systemd/system

# enable systemd service
systemctl enable mp3pi
systemctl enable pulseaudio
systemctl enable ssh

# configure kivy for touch
cp ~/.kivy/config.ini ~/.kivy/config.orig
cp assets/kivy.ini ~/.kivy/config.ini

# configure hostname
echo "raspiradio" > /etc/hostname
sed -i "s/127.0.1.1.*raspberrypi/127.0.1.1\traspiradio/g" /etc/hosts

# disable auto exit in pulseaudio
echo "exit-idle-time = -1" >> /etc/pulse/daemon.conf

# Reboot
echo "Done."
echo
echo -n "REBOOT NOW? [y/N] "
read
if [[ ! "$REPLY" =~ ^(yes|y|Y)$ ]]; then
	echo "Exiting without reboot."
	exit 0
fi
echo "Reboot started..."
reboot
exit 0
