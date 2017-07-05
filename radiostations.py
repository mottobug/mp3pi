#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Das Modul lädt Stationslisten (entweder von radio.de oder aus
custom.json).
"""

import os
import sys
import requests
import json

#import pdb

reload(sys)
sys.setdefaultencoding('utf-8')


class RadioStations():
  """Die Klasse für Stationslisten und -daten."""

  _user_agent = {'User-agent': 'User-Agent: XBMC Addon Radio'}
  _favorites_filename = 'favorites.json'

  data = []
  favorites = []
  no_data = True

  def __init__(self, **kwargs):
    if os.path.exists(self._favorites_filename):
      with open(self._favorites_filename, "r") as fd:
        self.favorites = json.load(fd)

  def load_playlist(self, playlist):
    """Laden der Playlist.
    
    Für 'custom' wird die Playlist aus custom.json geladen,
    für 'favorites' wird sie aus favorites.json geladen,
    für 'radio.de' wird sie von radio.de abgerufen.
    """
    if playlist == "custom" or playlist == 'favorites':
      filename = playlist + ".json"
      if os.path.exists(filename) is True:
        with open(filename, "r") as fd:
          self.data = json.load(fd)
        self.no_data = False
      else:
        print("file missing %s" % filename)
        self.no_data = True
    elif playlist == "radio.de":
      self.update()
    else:
      self.data = []
      self.no_data = True
  
  def update(self):
    """Abrufen der Top100-Playlist von radio.de."""

    url = "http://radio.de/info/menu/broadcastsofcategory?category=_top"
    #url = "http://radio.de/info/account/getmostwantedbroadcastlists?sizeoflists=20"
    #url = "http://radio.de/info/broadcast/editorialreccomendationsembedded"

    try:
      response  = requests.get(url, headers = self._user_agent)
      #print(response.status_code)
      self.data = response.json()
      self.no_data = False
    except requests.HTTPError, e:
      print("HTTP error %s" % e.code)
      self.no_data = False
    except requests.ConnectionError, e:
      self.data.append({'name': 'no station data'}) 
      self.no_data = True
      print("Connection error %s", e)

#  def getStations(self):
#    """Zurückgeben der geladenen Playlist."""
##   for item in self.data:
##     print(item['pictureBaseURL'])
##     print(item['picture1TransName'])
##     print(item['name'])
##     print(item['subdomain'])
##     print(item['bitrate'])
##     print(item['id'])
#
#    return(self.data)

  def getStation(self, id):
    """Zu 'id' die Stationsdaten von radio.de liefern."""
    url = "http://radio.de/info/broadcast/getbroadcastembedded?broadcast=" + str(id)

    response = requests.get(url, headers = self._user_agent)
    #print(response.status_code)
    station_data = response.json()

    if "errorCode" in station_data.keys():
      print("no such entry")
      return({})

    return(station_data)

  def getIndexByName(self, name):
    """Zur Station 'name' den Index in der data-Liste liefern."""
    for i,station in enumerate(self.data):
      if station['name'] == name:
        return(i)

  def getListItemByName(self, list, name):
    """Findet das Element mit Schüssel name in list.
    
    Existiert der Schlüssel nicht, wird None zurückgeliefert.
    """
    for item in list:
      if item['name'] == name:
        return(item)
  
  def getImageUrlByName(self, name):
    """Zur Station 'name' die URL der Stationsgrafik liefern."""
    item = self.getListItemByName(self.data, name)
    if item is not None:
      return(item['pictureBaseURL'] + item['picture1Name'])

  def getStreamURLbyName(self, name):
    """Zur Station 'name' die StreamURL liefern.
    
    Falls die ID der Station 0 ist, wird der Wert
    des Schlüssels streamURL zurückgeliefert, sonst
    wird von radio.de die StreamURL geholt und zurückgeliefert.
    """
    item = self.getListItemByName(self.data, name)
    if item is not None:
      id = item.get('id', 0)
      if id != 0:
        item = self.getStation(id)
      return(item.get('streamURL', None))

  def addToFavorites(self, name):
    """Hinzufügen der Station mit dem Namen zu den Favoriten."""
    if self.getListItemByName(self.favorites, name) is not None:
      return
    item = self.getListItemByName(self.data, name)
    if item is not None:
      self.favorites.append(item)
      with open(self._favorites_filename, "w") as fd:
        json.dump(self.favorites, fd)

  def removeFromFavorites(self, name):
    """Entfernen der Station mit dem Namen aus den Favoriten."""
    if self.getListItemByName(self.favorites, name) is None:
      return
    for i,item in enumerate(self.favorites):
      if item['name'] == name:
        del self.favorites[i]
        break
    with open(self._favorites_filename, "w") as fd:
      json.dump(self.favorites, fd)


if __name__ == '__main__':
  ### Test der Methoden ###

  Stations = RadioStations()
  #Stations.load_playlist('custom')
  Stations.load_playlist('radio.de')

  if Stations.no_data:
    print('no data')
  else:
    for i,station in enumerate(Stations.data):
      print "{:5}: {}, {} - {}".format(
        i,
        station['name'],
        station['country'],
        station['genresAndTopics']
      )
