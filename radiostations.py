
import requests
import os
import json

#from objbrowser import browse

##
#
##
class RadioStations():

  user_agent = {'User-agent': 'User-Agent: XBMC Addon Radio'}

  data = []
  no_data = True

  #def __init__(self):
  #  self.update()
  
  def load_playlist(self, playlist):
    if playlist == "custom":
      filename = playlist + ".json"
      if os.path.exists(filename) is True:
        fd = open(filename, "r")
        self.data = json.load(fd)
        self.no_data = False
      else:
        print("filename missing %s" % filename)
    else:
      self.update()


  def update(self):
    url = "http://radio.de/info/menu/broadcastsofcategory?category=_top"
    #url = "http://radio.de/info/account/getmostwantedbroadcastlists?sizeoflists=20"
    #url = "http://radio.de/info/broadcast/editorialreccomendationsembedded"

    try:
      response  = requests.get(url, headers = self.user_agent)
      #print(response.status_code)
      self.data = response.json()
      self.no_data = False
    except requests.HTTPError, e:
      print("HTTP error %s", e.code)
      self.no_data = False
    except requests.ConnectionError, e:
      self.data.append({'name': 'no station data'}) 
      self.no_data = True
      print("Connection error %s", e)


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

