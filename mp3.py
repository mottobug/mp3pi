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
from signal import SIGTSTP, SIGTERM, SIGABRT

##from threading import Thread

class Mp3PiAppLayout(BoxLayout):
  
  stop = threading.Event()
  isPlaying = False
  proc = None

  def __init__(self, **kwargs):
    super(Mp3PiAppLayout, self).__init__(**kwargs)
    self.search_results.adapter.data.extend(("HR-Info", "HR3", "Radio Bob"))
    self.ids['search_results_list'].adapter.bind(on_selection_change=self.change_selection)

  def change_volume(self, args):
    os.system("amixer set Master %s" % int(args))
    print(int(args))

  def change_selection(self, args):
    if args.selection:
      print(args.selection[0].text)
      self.change_image(args.selection[0].text)

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
      
  def infinite_loop(self, label):
    iteration = 0
    
    url = "http://mp3channels.webradio.antenne.de/chillout"
    
    if label == "Radio Bob":
      url = "http://streams.radiobob.de/bob-live/mp3-192/mediaplayerbob"

    if label == "HR3":
      url = "http://hr-mp3-m-h3.akacast.akamaistream.net/7/785/142133/v1/gnl.akacast.akamaistream.net/hr-mp3-m-h3"
    
    if label == "HR-Info":
      url = "http://hr-mp3-m-hrinfo.akacast.akamaistream.net/7/698/142135/v1/gnl.akacast.akamaistream.net/hr-mp3-m-hrinfo"
    
    self.proc = subprocess.Popen(["mpg123", url])

    while True:
      if self.stop.is_set():
        # Stop running this thread so the main Python process can exit.
        return
      iteration += 1
      print('Infinite loop, iteration {}.'.format(iteration))
      print(self.isPlaying)
      time.sleep(1)

  def change_image(self, args):
    print(args)
    print(self.ids.imageid.source)

    if args == "Radio Bob":
      self.ids.imageid.source = "bob.jpg"
    if args == "HR3":
      self.ids.imageid.source = "hr3.jpg"
    if args == "hr-info":
      self.ids.imageid.source = "hr-info.png"

    self.start_second_thread(args)
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
  Mp3PiApp().run()
