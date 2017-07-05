#!/usr/bin/python

import os
import sys
import signal
from os.path import dirname,join
from random import choice
from glob import glob

os.environ['KIVY_NO_FILELOG'] = '1'
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.lang import Builder

class ImageViewer(Screen):

  source = StringProperty(None)
  imagedir = 'images';
  interval = 10
  _cache = []
  _curEvent = None

  def __init__(self, **kwargs):
    super(ImageViewer, self).__init__(**kwargs)
    
  def start(self, *nargs):
    Logger.info("ImageViewer: starting")
    if self._curEvent:
      Clock.unschedule(self._curEvent)
    if self.interval != 0:
      self.reload()
      self.update()
      self._curEvent = Clock.schedule_interval(self.update, self.interval)

  def stop(self, *nargs):
    Logger.info("ImageViewer: stopping")
    if self._curEvent:
      Clock.unschedule(self._curEvent)
    self.source = ''

  def reload(self):
    imagedir = join(dirname(__file__), self.imagedir)
    self._cache = glob(join(imagedir, '*.png'))

  def update(self, *nargs):
    if len(self._cache) != 0:
      curimage = choice(self._cache)
      Logger.debug("ImageViewer: showing file " + curimage)
      self.source = curimage
    else:
      Logger.debug("ImageViewer: no PNG files in " + imagedir)

class ImageViewerTestApp(App):

  def build(self):
    sm = ScreenManager()
    iv = ImageViewer()
    iv.interval = 10
    sm.add_widget(iv)
    iv.start()
    #Clock.schedule_once(iv.stop, 3*iv.interval)
    return(sm)

def signal_handler(signal, frame):
  print("Signal {} received".format(signal))
  App.get_running_app().stop()
  sys.exit(0);

if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal_handler)
  Builder.load_string('''
<ImageViewer>:
  name: 'imageviewer'
  fullscreen: True
  Image:
    source: root.source
    size_hint: 1,1
    #size: self.parent.size
    allow_stretch: True
  ''')

  ImageViewerTestApp().run()
