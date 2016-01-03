from kivy.app import App

from objbrowser import browse

from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.graphics import Color

import pdb

import threading
import time
import os
import subprocess
import alsaaudio
import sys
import json
import pprint
import requests
import signal
import NetworkManager
import re

reload(sys)
sys.setdefaultencoding('utf-8')

import select

import markup

from kivy.logger import Logger
from signal import SIGTSTP, SIGTERM, SIGABRT

import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

RootApp = "init"
RoRoRo = "lala"

class NetworkManagerWrapper:
  
  ssid = None
  strength = None
  frequency = None
  ip = None
  psk = None
  
  # visible aps
  aps = []
  
  def __init__(self):
    self.Update()
  
  def Update(self):
    self.aps = []

    for conn in NetworkManager.NetworkManager.ActiveConnections:
      settings = conn.Connection.GetSettings()

      secrets = conn.Connection.GetSecrets()
      
      if secrets['802-11-wireless-security']:
        if secrets['802-11-wireless-security']['psk']:
          self.psk = secrets['802-11-wireless-security']['psk']

      for dev in conn.Devices:
        for addr in dev.Ip4Config.Addresses:
          self.ip = addr[0]
        for route in dev.Ip4Config.Routes:
          time.time()
          # route
        for ns in dev.Ip4Config.Nameservers:
          time.time()
      

    for device in NetworkManager.NetworkManager.GetDevices():
      if device.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
        continue
      
      specific_device = device.SpecificDevice()
      active = specific_device.ActiveAccessPoint
      # active.Ssid
      for ap in device.SpecificDevice().GetAccessPoints():
        self.aps.append({
          "ssid": ap.Ssid,
          "strength": ap.Strength,
          "frequency": ap.Frequency})
              
        if ap.object_path == active.object_path:
          self.ssid = ap.Ssid
          self.strength = ap.Strength
          self.frequency = ap.Frequency

  def ListKnownConnections(self):
    active = []
    for x in NetworkManager.NetworkManager.ActiveConnections:
      active.append(x.Connection.GetSettings()['connection']['id'])
  
    connections = []
    for x in NetworkManager.Settings.ListConnections():
      if x.GetSettings()['connection']['type'] != "802-11-wireless":
        continue

      if x.GetSettings()['connection']['id'] in active:
        current_connection = True
      else:
        current_connection = False

      connections.append(
          (current_connection,
            x.GetSettings()['connection']['id'], 
            x.GetSettings()['connection']['type']))

    return(connections)

class AlsaInterface():

  mixer = ""

  def __init__(self): # picks first mixer and set as default
    all_mixers = self.list_mixers()
    self.mixer = all_mixers[0]
    Logger.info("AlsaInterface: Setting default mixer to: " + self.mixer)

  def list_mixers(self, **kwargs):
    return(alsaaudio.mixers(**kwargs))
    #for m in alsaaudio.mixers(**kwargs):
      #print("  '%s'" % m)

  def set_mixer(self, name, args, kwargs):
      if not name:
        name = self.mixer
      try:
          mixer = alsaaudio.Mixer(name, **kwargs)
      except alsaaudio.ALSAAudioError:
          print("No such mixer")
          sys.exit(1)

      channel = alsaaudio.MIXER_CHANNEL_ALL

      volume = int(args)
      mixer.setvolume(volume, channel)

  def get_mixer(self, name, kwargs):
      if not name:
        name = self.mixer    
      try:
          mixer = alsaaudio.Mixer(name, **kwargs)
      except alsaaudio.ALSAAudioError:
          print("No such mixer")
          sys.exit(1)
      volumes = mixer.getvolume()
      return(volumes[0])

# pactl set-sink-volume  bluez_sink.0C_A6_94_E3_76_DA 35%


##
#
##
class radioStations():

  user_agent = {'User-agent': 'User-Agent: XBMC Addon Radio'}

  data = []

  def __init__(self):
    url = "http://radio.de/info/menu/broadcastsofcategory?category=_top"
    response  = requests.get(url, headers = self.user_agent)
    #print(response.status_code)
    self.data = response.json()

  def getStations(self):
    return(self.data)

#   for item in self.data:
#     print(item['pictureBaseURL'])
#     print(item['picture1TransName'])
#     print(item['name'])
#     print(item['subdomain'])
#     print(item['bitrate'])
#     print(item['id'])

  def getStation(self, id):
    url = "http://radio.de/info/broadcast/getbroadcastembedded?broadcast=" + id

    response = requests.get(url, headers = self.user_agent)
    #print(response.status_code)
    station_data = response.json()

    if "errorCode" in station_data.keys():
      print("no such entry")
      return(0)

    return(station_data)

  def getImageUrl(self, id):
    for item in self.data:
      if str(item['id']) == str(id):
        return(item['pictureBaseURL'] + item['picture1Name'])

  def getIdByName(self, name):
    for item in self.data:
      #if str(item['name']) == name:
      if item['name'] == name:
        return(item['id'])

  def getStreamURLbyName(self, name):

    id = self.getIdByName(name)
    station_data = self.getStation(str(id))

    return(station_data['streamURL'])
    
#   print(station_data['link'])
#   print(station_data['name'])
#   print(station_data['streamURL'])

#   if "StreamURLs" in station_data.keys():
#     for item in station_data['streamURLs']:
#       print(station_item['streamURL'])
    #print(data['streamURLs'][0]['streamURL'])

class Mp3PiAppLayout(BoxLayout):

  global RootApp
  
  isPlaying = False
  proc = None

  stop = threading.Event()
  mythread = None

  statusthread_stop = threading.Event()
  statusthread = None

  def args_converter(self, row_index, an_obj):
    if row_index % 2:
      background = [1, 1, 1, 0]
    else:
      background = [1, 1, 1, .5]

    return {'text': an_obj['name'],
            'size_hint_y': None,
            'deselected_color': background}

  def __init__(self, **kwargs):
    global RootApp
    super(Mp3PiAppLayout, self).__init__(**kwargs)
    
    RootApp = self

    self.search_results.adapter.data.extend((Stations.data))
    self.ids['search_results_list'].adapter.bind(on_selection_change=self.change_selection)

    networklist = []
    for net in Network.ListKnownConnections():
      networklist.append(net[1])
      if net[0] is True:
        self.ids['wlan_list'].text = net[1]

    self.ids['wlan_list'].values = networklist
    self.ids['wlan_list'].bind(text=self.change_wlan_selection)

    #self.ids.volume_slider.value = Alsa.get_mixer("", {})

    # XXX validate!!
    self.ids.volume_slider.value = int(subprocess.check_output(["pulseaudio-ctl", "full-status"]).split(" ")[0])


    self.statusthread = threading.Thread(target=self.status_thread)
    self.statusthread.daemon = True
    self.statusthread.start()

  def change_wlan_selection(self, spinner, args):
    print(args)

  def change_volume(self, args):
    #os.system("amixer set Master %s%%" % int(args))
    #os.system("pactl set-sink-volume  bluez_sink.0C_A6_94_E3_76_DA %s%%" % int(args))
    #Alsa.set_mixer("", int(args), {})
    os.system("pulseaudio-ctl set %s%%" % int(args))

  def change_selection(self, args):
    if args.selection:
      self.change_image(args.selection[0].text)
      self.stop_second_thread()
      self.start_second_thread(Stations.getStreamURLbyName(args.selection[0].text))
    else:
      self.stop_second_thread()

  def stop_second_thread(self):
    if self.isPlaying == True: # stop playing
      if self.proc is not None:
        if self.mythread.isAlive(): 
          print("set stop")
          self.stop.set()    
        #self.proc.kill() ??
        Logger.info("mpg123: killing %s" % self.proc.pid)
        os.kill(self.proc.pid, SIGTERM)
        self.proc = None
    self.isPlaying = False

  def start_second_thread(self, l_text):
    if self.isPlaying == False:
      Logger.info("Player: starting player " + l_text)
      
      self.isPlaying = True
      self.mythread = threading.Thread(target=self.infinite_loop, args=(l_text,))
      self.mythread.daemon = True
      self.mythread.start()
        
    else:
      Logger.info("Player: already playing")
      
  def infinite_loop(self, url):
    iteration = 0

    self.proc = subprocess.Popen(["mpg123", "-o", "pulse", "-@", url], stderr=subprocess.PIPE, bufsize = 0)
  
    line = []
    while True:
      if self.stop.is_set():
        Logger.info("Player: stopping thread")
        self.stop.clear()
        return
     
      while (select.select([self.proc.stderr], [], [], 0)[0]):

        # check if mpg123 is died
        #print(self.proc.returncode)
        #print(self.proc.pid)
        if self.proc.returncode is not None:
          print("died")
          return

        if self.stop.is_set():
          Logger.info("Player: stopping thread")
          self.stop.clear()
          return


        char = self.proc.stderr.read(1)
        if char != '\n':
          line.append(char)
        else:
          line_joined = "".join(line)

          Logger.info("MPG123: says %s " % line_joined)
          
          if "ICY-META: StreamTitle=" in line_joined:
            pairs = {}
            elements = line_joined.split(";")
            for element in elements:
              if element:
                res = re.search(r"([A-Za-z]*)='(.*)'", element)
                pairs[res.group(1)] = res.group(2)

            self.ids.icytags.text = pairs['StreamTitle']

          
          if "ICY-NAME: " in line_joined:
            Logger.debug("ICYTAGS: ICY name found: %s " % line_joined.replace("ICY-NAME: ", ""))

          if "ICY-URL: " in line_joined:
            Logger.debug("ICYTAGS: ICY url found: %s " % line_joined.replace("ICY-URL: ", ""))

          if "ICY-META: StreamTitle=" in line_joined:
            Logger.debug("ICYTAGS: ICY StreamTitle found: %s " % line_joined.replace("ICY-META: StreamTitle=", ""))

          line = []

      iteration += 1
      #print('Infinite loop, iteration {}.'.format(iteration))
      time.sleep(.1)
  
  def status_thread(self):
    while True:
      if self.statusthread_stop.is_set():
        self.statusthread_stop.clear()
        return

      if not int(time.time()) % 5:
        Network.Update()

      self.ids.wlanstatus.text = "%s %s%%\n%s" % (Network.ssid, Network.strength, Network.ip)
      #self.ids.wlanstatus.text = "%s %s%%\n%s" % ("myNetwork", Network.strength, "192.168.47.11")
      
      lines = []
      for i in self.ids.wlanstatus.canvas.get_group(None)[1:]:
        if type(i) is Color:
          lines.append(i)
          i.a = 1

      if Network.strength < 50:
        for i in lines[0:3]:
          i.a = .5

      if Network.strength < 60:
        for i in lines[0:2]:
          i.a = .5

      if Network.strength < 70:
        for i in lines[0:1]:
          i.a = .5

      #self.ids.wlanstatus.canvas.clear()
      #self.ids.wlanstatus.canvas.ask_update()
      time.sleep(.5)
    
  def change_image(self, station_name):
    imageUrl = Stations.getImageUrl(Stations.getIdByName(station_name)) 
    Logger.info("ImageLoader: Loading Image from %s" % (imageUrl))
    self.ids.imageid.source = imageUrl    

  def pause(self):
    self.stop.set()
    self.search_results.adapter.deselect_list(self.search_results.adapter.selection)

  def next(self):
    self.stop.set()
    if self.search_results.adapter.selection:
      index = self.search_results.adapter.selection[0].index
      if index < len(self.search_results.adapter.data):
        self.search_results.adapter.get_view(index+1).trigger_action(duration=0)

  def prev(self):
    self.stop.set()
    if self.search_results.adapter.selection:
      index = self.search_results.adapter.selection[0].index
      if index >= 1:
        self.search_results.adapter.get_view(index-1).trigger_action(duration=0)

  def poweroff(self):
    print("poweroff")

  def reboot(self):
    print("reboot")

class Mp3PiApp(App):
  def build_config(self, config):
    config.setdefaults('General', {'temp_type': "Metric"})

  def build_settings(self, settings):
    settings.add_json_panel("Weather Settings", self.config, data="""
      [
        {"type": "options",
          "title": "Temperature System",
          "section": "General",
          "key": "temp_type",
          "options": ["Metric", "Imperial"]
        }
      ]"""
    )

  def on_stop(self):
    # The Kivy event loop is about to stop, set a stop signal;
    # otherwise the app window will close, but the Python process will
    # keep running until all secondary threads exit.
    self.root.stop.set()
    self.root.statusthread_stop.set()

  def build(self):
    return Mp3PiAppLayout()

def signal_handler(signal, frame):
  print("exit");
  sys.exit(0);

class HTTPHandler(BaseHTTPRequestHandler):
  global RootApp

  #print(Mp3PiAppClass)
  def do_GET(self):
    if self.path == "/":
      
      self.page = markup.page()
      self.page.init(title="Title")
      
      self.page.table(border="true")

      firstline = True
      for row in RootApp.search_results.adapter.data:
        if firstline is True:
          self.page.tr()
          for column in row:
            #pdb.set_trace()
            string1 = column
            if type(column) == 'float':
              string1 = str(column)
            if type(column) == 'str':
              string1 = unicode(column, "utf8")
            self.page.th(string1, align="left")
          self.page.tr.close()
          firstline = False
          continue

        self.page.tr()
        for column in row:
          #pdb.set_trace()
          string1 = row[column]
          if type(row[column]) == 'float':
            string1 = str(row[column])
          if type(row[column]) == 'str':
            string1 = unicode(row[column], "utf8")
          self.page.td(string1)
        self.page.tr.close()

      self.page.p(time.time())
        
      
      self.send_response(200)
      self.send_header('Content-type',  'text/html')
      self.end_headers()
      self.wfile.write(RootApp.isPlaying)
      self.wfile.write(self.page)
      #self.wfile.write(json.dumps(RootApp.search_results.adapter.data, indent=4, separators=('.', ': ')))
    else:
      print(self.path)


if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal_handler)

  Network = NetworkManagerWrapper()
  Alsa = AlsaInterface()
  Stations = radioStations()

  httpd = HTTPServer(('', 8080), HTTPHandler)
  httpd_thread = threading.Thread(target=httpd.serve_forever)
  httpd_thread.daemon = True
  httpd_thread.start()

  Mp3PiApp().run()


