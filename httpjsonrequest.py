#!/usr/bin/python
import sys
import requests
import pprint

#from requests import Request, Session

user_agent = {'User-agent': 'User-Agent: XBMC Addon Radio'}


def getStations():

	url = "http://radio.de/info/menu/broadcastsofcategory?category=_top"

	response  = requests.get(url, headers = user_agent)
	print(response.status_code)
	print(response.history)
	#print(response.text)

	data = response.json()

	for item in data:
		print(item['pictureBaseURL'])
		print(item['picture1TransName'])
		print(item['name'])
		print(item['subdomain'])
		print(item['bitrate'])
		print(item['id'])

def getStation(id):
	url = "http://radio.de/info/broadcast/getbroadcastembedded?broadcast=" + id

	response = requests.get(url, headers = user_agent)
	print(response.status_code)
	data = response.json()

	if "errorCode" in data.keys():
		print("no such entry")
		return(0)
	
	print(data['link'])
	print(data['name'])
	print(data['streamURL'])

	if "StreamURLs" in data.keys():
		for item in data['streamURLs']:
			print(item['streamURL'])
	#print(data['streamURLs'][0]['streamURL'])

getStation("33450")
getStation("1382")
getStation("0815")
