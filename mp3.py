
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
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition, FadeTransition
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.config import Config

import pdb

import threading
import time
import os
import subprocess
import sys
import json
import pprint
import signal
import re

#from networking import NetworkManagerWrapper
from nmcli import nmcli
from radiostations import RadioStations
from audio import AlsaInterface
from screensaver import Rpi_ScreenSaver

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
ConfigObject = None

class Mp3PiAppLayout(Screen):

  global RootApp, last_activity_time, ConfigObject
  
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

    self.ids['search_results_list'].adapter.bind(on_selection_change=self.change_selection)

    #self.ids.volume_slider.value = Alsa.get_mixer("", {})

    # XXX validate!!
    self.ids.volume_slider.value = int(subprocess.check_output(["pulseaudio-ctl", "full-status"]).split(" ")[0])


    self.statusthread = threading.Thread(target=self.status_thread)
    self.statusthread.daemon = True
    self.statusthread.start()


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
    global ConfigObject
    
    connection = NMCLI.current_connection() 

    while True:
      if self.statusthread_stop.is_set():
        self.statusthread_stop.clear()
        return

      if not int(time.time()) % 5:
        connection = NMCLI.current_connection() 
      
      ip = NMCLI.get_ip()
      if ip is None: 
        self.ids.wlanstatus.text = "No network connection"
      else:
        self.ids.wlanstatus.text = "%s %s%%\n%s\n%s" % (connection.get('SSID', None), connection.get('SIGNAL', None), ip, time.strftime("%H:%M", time.localtime()))

      #self.ids.wlanstatus.text = "%s %s%%\n%s" % ("myNetwork", Network.strength, "192.168.47.11")
      
      # wlan symbol
      lines = []
      for i in self.ids.wlanstatus.canvas.get_group(None)[1:]:
        if type(i) is Color:
          lines.append(i)
          i.a = 1
      
      if connection is not None:
        if connection['SIGNAL'] < 50:
          for i in lines[0:3]:
            i.a = .5

        if connection['SIGNAL'] < 60:
          for i in lines[0:2]:
            i.a = .5

        if connection['SIGNAL'] < 70:
          for i in lines[0:1]:
            i.a = .5
        

      if Stations.no_data == True:
        print("no data")
        if ConfigObject.get('General', 'playlist') == "radio.de":
          Stations.update()
          if Stations.no_data == False:
            del self.search_results.adapter.data[:]
            self.search_results.adapter.data.extend((Stations.data))
        if ConfigObject.get('General', 'playlist') == "custom":
          Stations.load_playlist("custom")
          if Stations.no_data == False:
            del self.search_results.adapter.data[:]
            self.search_results.adapter.data.extend((Stations.data))
      
      # screensaver
      timeout = ConfigObject.get('General', 'screensaver')
      if timeout < 60:
        timeout = 60

      if (time.time() - last_activity_time) > int(timeout):
        if ScreenSaver.display_state is True:
          Logger.info("ScreenSaver: enabling screensaver")
          ScreenSaver.display_off()
      else:
        if ScreenSaver.display_state is False:
          Logger.info("ScreenSaver: disabling screensaver")
          ScreenSaver.display_on()
      
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
    browse(self.search_results.adapter)
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
    os.system("poweroff")

  def reboot(self):
    print("reboot")
    os.system("reboot")

class Mp3PiApp(App):
  global last_activity_time, ConfigObject

  def build_config(self, config):
    config.setdefaults('General', {'screensaver': "60"})
    config.setdefaults('General', {'name': "name"})
    config.setdefaults('General', {'playlist': "radio.de"})

  def build_settings(self, settings):
    settings.add_json_panel("General", self.config, data="""
      [
        {"type": "numeric",
          "title": "Screensaver Timeout",
          "section": "General",
          "key": "screensaver"
        },
        {"type": "string",
          "title": "String",
          "section": "General",
          "key": "name"
        },
        {"type": "options",
          "title": "Playlist",
          "section": "General",
          "options": ["radio.de", "custom"],
          "key": "playlist"
        }
      ]"""
    )

  def on_stop(self):
    # The Kivy event loop is about to stop, set a stop signal;
    # otherwise the app window will close, but the Python process will
    # keep running until all secondary threads exit.
    
    #layout.clear_widgets()
    #browse(self)
    True

    #main = self.root.manager.get_screen('main').layout
    #main.stop.set()
    #self.root.stop.set()

    #self.root.statusthread_stop.set()

  def build(self):
    global last_activity_time, ConfigObject
    #sm = ScreenManager(transition=FadeTransition())
    
    self.settings_cls = MySettingsWithTabbedPanel

    from kivy.core.window import Window
#    Window.size = (800, 480)
    
    def on_motion(self, etype, motionevent):
      global last_activity_time
      last_activity_time = time.time()
    Window.bind(on_motion=on_motion)

    ConfigObject = self.config

    sm = ScreenManager()
    sm.add_widget(Mp3PiAppLayout())
    sm.add_widget(SettingsScreen())
    return sm
    #return Mp3PiAppLayout()

class SettingsScreen(Screen):
  def __init__(self, **kwargs):
    super(SettingsScreen, self).__init__(**kwargs)
    networklist = []
#    for net in Network.visible_aps:
#      networklist.append(net['ssid'])
#      if net['ssid'] is Network.ssid:
#        self.ids['wlan_list'].text = net[Network.ssid]

#    self.ids['wlan_list'].values = networklist
#    self.ids['wlan_list'].bind(text=self.change_wlan_selection)

  def change_wlan_selection(self, spinner, args):
    Logger.info("WLAN: user selection %s" % args)
#    Logger.info("WLAN: current WLAN %s" % Network.ssid)

#    if args != Network.ssid:
#      Logger.info("WLAN: changing WLAN to %s" % args)
#      Network.activate([args])


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


class MySettingsWithTabbedPanel(SettingsWithTabbedPanel):
  def on_close(self):
    Logger.info("main.py: MySettingsWithTabbedPanel.on_close")

  def on_config_change(self, config, section, key, value):
    if key == "playlist":
      Stations.no_data = True
    Logger.info(
      "main.py: MySettingsWithTabbedPanel.on_config_change: "
      "{0}, {1}, {2}, {3}".format(config, section, key, value))


if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal_handler)

  #Network = NetworkManagerWrapper()
  NMCLI = nmcli() 
  #Alsa = AlsaInterface()
  Stations = RadioStations()
  ScreenSaver = Rpi_ScreenSaver()
  

  httpd = HTTPServer(('', 8080), HTTPHandler)
  httpd_thread = threading.Thread(target=httpd.serve_forever)
  httpd_thread.daemon = True
  httpd_thread.start()

  last_activity_time = time.time()

  Mp3PiApp().run()


