from kivy.app import App

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
from signal import SIGTSTP, SIGTERM, SIGABRT

##from threading import Thread

user_agent = {'User-agent': 'User-Agent: XBMC Addon Radio'}


def set_mixer(name, args, kwargs):
    try:
        mixer = alsaaudio.Mixer(name, **kwargs)
    except alsaaudio.ALSAAudioError:
        print("No such mixer")
        sys.exit(1)

    channel = alsaaudio.MIXER_CHANNEL_ALL

    volume = int(args)
    mixer.setvolume(volume, channel)

def get_mixer(name, kwargs):
    try:
        mixer = alsaaudio.Mixer(name, **kwargs)
    except alsaaudio.ALSAAudioError:
        print("No such mixer")
        sys.exit(1)
    volumes = mixer.getvolume()
    return(volumes[0])


listitems = []
def get_Stations():
  json_data = []
  with open('json.json') as data_file:    
    json_data = json.load(data_file)

  for item in json_data:
    listitems.append(item['name'])

def get_Station(name):
  json_data = []
  id = 0
  with open('json.json') as data_file:    
    json_data = json.load(data_file)

  for item in json_data:
    if item['name'] == name:
      id = item['id']

  #
  url = "http://radio.de/info/broadcast/getbroadcastembedded?broadcast=" + str(id)

  response = requests.get(url, headers = user_agent)
#  print(response.status_code)
  data = response.json()

  if "errorCode" in data.keys():
    print("no such entry")
    return(0)
  
  print(data['link'])
  print(data['name'])
  print(data['streamURL'])

  return(data['streamURL'])
#  if "StreamURLs" in data.keys():
#    for item in data['streamURLs']:
#      print(item['streamURL'])




class Mp3PiAppLayout(BoxLayout):
  
  stop = threading.Event()
  isPlaying = False
  proc = None


#  def args_converter(self, row_index, an_obj):
#    
#    if an_obj is "0":
#      text = "HR3"
#    if an_obj is "1":
#      text = "FFH"
#    return {'text': text,
#            'size_hint_y': None,
#            'height': 25}

  def __init__(self, **kwargs):
    super(Mp3PiAppLayout, self).__init__(**kwargs)
    #self.search_results.adapter.data.extend(("HR-Info", "HR3", "Radio Bob"))
    self.search_results.adapter.data.extend((listitems))
    self.ids['search_results_list'].adapter.bind(on_selection_change=self.change_selection)
    self.ids.volume_slider.value = get_mixer("Master", {})

  def change_volume(self, args):
#    os.system("amixer set Master %s%%" % int(args))
    set_mixer("Master", int(args), {})

  def change_selection(self, args):
    get_Stations()
    if args.selection:
      print(args.selection[0].text)
      print(get_Station(args.selection[0].text))
      self.change_image("url", get_Station(args.selection[0].text))
      #self.change_image(args.selection[0].text)

  def start_second_thread(self, l_text):
    if self.isPlaying == 0:
      self.isPlaying = True
      threading.Thread(target=self.infinite_loop, args=(l_text,)).start()
    else:
      self.isPlaying = False
      if self.proc is not None:
        print("killing %s" % self.proc.pid)
        os.kill(self.proc.pid, SIGTERM)
        self.proc = None
        self.stop.set()
      
  def infinite_loop(self, url):
    iteration = 0
    
    self.proc = subprocess.Popen(["mpg123", "-o", "pulse", "-@", url])

    while True:
      if self.stop.is_set():
        # Stop running this thread so the main Python process can exit.
        return
      iteration += 1
      print('Infinite loop, iteration {}.'.format(iteration))
      print(self.isPlaying)
      time.sleep(1)

  def change_image(self, image, url):

    print(self.ids.imageid.source)

#    if args == "Radio Bob":
#      self.ids.imageid.source = "bob.jpg"
#    if args == "HR3":
#      self.ids.imageid.source = "hr3.jpg"
#    if args == "hr-info":
#      self.ids.imageid.source = "hr-info.png"

    self.start_second_thread(url)
    pass

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

if __name__ == "__main__":
  get_Stations()
  Mp3PiApp().run()
