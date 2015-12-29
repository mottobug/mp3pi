from kivy.app import App

from objbrowser import browse

from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

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

import re

import select

from kivy.logger import Logger
from signal import SIGTSTP, SIGTERM, SIGABRT
##from threading import Thread


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
  listitems = []

  def __init__(self):
    url = "http://radio.de/info/menu/broadcastsofcategory?category=_top"
    response  = requests.get(url, headers = self.user_agent)
    #print(response.status_code)
    self.data = response.json()

    # array for kivy radio list
    for item in self.data:
      self.listitems.append(item['name'])    


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
  
  stop = threading.Event()
  isPlaying = False
  proc = None
  mythread = None

  def args_converter(self, row_index, an_obj):

    if row_index % 2:
      background = [1, 1, 1, 0]
    else:
      background = [1, 1, 1, .5]

#
    #print("%s %s" % (row_index, an_obj))

    return {'text': an_obj['name'],
            'size_hint_y': None,
            'deselected_color': background}

  def __init__(self, **kwargs):
    super(Mp3PiAppLayout, self).__init__(**kwargs)

    self.search_results.adapter.data.extend((Stations.data))
    self.ids['search_results_list'].adapter.bind(on_selection_change=self.change_selection)
    self.ids.volume_slider.value = Alsa.get_mixer("", {})

  def change_volume(self, args):
    #os.system("amixer set Master %s%%" % int(args))
    os.system("pactl set-sink-volume  bluez_sink.0C_A6_94_E3_76_DA %s%%" % int(args))
    #Alsa.set_mixer("", int(args), {})

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

  def change_image(self, station_name):
    imageUrl = Stations.getImageUrl(Stations.getIdByName(station_name)) 
    Logger.info("ImageLoader: Loading Image from %s" % (imageUrl))
    self.ids.imageid.source = imageUrl    

  def pause(self):
    self.stop.set()
    self.search_results.adapter.deselect_list(self.search_results.adapter.selection)

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

  def build(self):
    return Mp3PiAppLayout()

def signal_handler(signal, frame):
  print("exit");
  sys.exit(0);

if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal_handler)

  Alsa = AlsaInterface()
  Stations = radioStations()
  Mp3PiApp().run()
