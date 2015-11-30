#!/usr/bin/python
import sys
import requests
import pprint

#from requests import Request, Session




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

#		for item in self.data:
#			print(item['pictureBaseURL'])
#			print(item['picture1TransName'])
#			print(item['name'])
#			print(item['subdomain'])
#			print(item['bitrate'])
#			print(item['id'])

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
			if str(item['name']) == name:
				return(item['id'])

		
#		print(station_data['link'])
#		print(station_data['name'])
#		print(station_data['streamURL'])

#		if "StreamURLs" in station_data.keys():
#			for item in station_data['streamURLs']:
#				print(station_item['streamURL'])
		#print(data['streamURLs'][0]['streamURL'])


Stations = radioStations()
#print(Stations.getIdByName("N-JOY"))
print(Stations.getImageUrl(Stations.getIdByName("N-JOY")))

#print(Stations.getStations())
#Stations.getStation("1382")

#getStation("33450")
#getStation("1382")
#getStation("0815")
