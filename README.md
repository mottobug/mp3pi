# mp3pi

Requirements:

apt-get install mpg123 python-kivy libbluetooth-dev bc

pip install pyalsaaudio pybluez python-networkmanager pygments

systemctl set-default multi-user.target

cp systemd/mp3pi.service /etc/systemd/system
systemctl enable mp3pi

https://github.com/graysky2/pulseaudio-ctl

![alt text](screenshots/screenshot.png "Description goes here")

