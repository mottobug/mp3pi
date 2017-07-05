#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Das Modul definiert die Klasse nmcli zur Kommunikation mit dem
Network Manager zum Thema WLAN-Verbindungen.
"""

import os
import subprocess
import re

class nmcli:
  """
  Klasse zur Kommunikation mit nmcli (Network Manager Command Line
  Interface).
  """

  def shell(self, command):
    """Methode, die ein Shellkommando 'command' ausführt.
    
    Rückgaben sind Returncode, stdout, stderr.
    """
    os.environ['LANG'] = 'C'
    process = subprocess.Popen(command,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    retcode = process.returncode

    return retcode, stdout, stderr

  def get_fields(self, fields, args):
    """Methode, welche die 'fields' eines nmcli-Kommandos mit 'args' liefert.
    
    Rückgabe ist eine Liste von Dictionaries mit 'fields' als Schlüsseln.
    Im Fehlerfall wird eine leere Liste geliefert.
    """
    command = ['nmcli', '--terse', '--fields', ','.join(fields)]
    command.extend(args)
    retcode, stdout, stderr = self.shell(command)
    
    data = []
    if retcode == 0:
      for line in stdout.split("\n"):
        values = line.split(':', len(fields)-1)
        row = dict(zip(fields, values))
        data.append(row)
    return data

  def list_ap(self):
    """Methode, die Daten zu den verfügbaren WLAN-Netzen liefert.
    
    Rückgabe ist eine Liste von Dictionaries mit den Schlüsseln
    'ACTIVE', 'NAME', 'SSID', 'SIGNAL', 'SECURITY', 'BSSID'.
    """
    fields = ['ACTIVE', 'NAME', 'SSID', 'SIGNAL', 'SECURITY', 'BSSID']
    args = ['device', 'wifi', 'list']
    data = self.get_fields(fields, args)
    return data

  def list_connections(self):
    """Methode, die Daten zu den konfigurierten WLAN-Verbindungen liefert.
    
    Rückgabe ist eine Liste von Dictionaries mit den Schlüsseln
    'ACTIVE', 'NAME', 'UUID', 'TYPE'.
    """
    fields = ['ACTIVE', 'NAME', 'UUID', 'TYPE']
    args = ['connection', 'show']
    data = self.get_fields(fields, args)

    for d in data:
      if d.get('TYPE') != '802-11-wireless':
        data.remove(d)
    
    return data
  
  def activate_connection(self, name):
    """Methode, welche die Verbindung 'name' aktiviert.
    
    'name' ist der Name einer NetworkManager-Verbindung.
    Es wird zurückgeliefert, ob die Aktivierung erfolgreich war..
    """
    command = ['nmcli', 'connection', 'up', 'id', name]
    retcode, stdout, stderr = self.shell(command)
    return(retcode == 0)

  def current_connection(self):
    """Methode, die Daten der aktiven WLAN-Verbindung liefert.

    Rückgabe ist ein Dictionary mit den Schlüsseln
    'ACTIVE', 'NAME', 'SSID', 'SIGNAL', 'SECURITY', 'BSSID'.
    Besteht keine aktive WLAN-Verbindung, wird None zurückgegeben
    """
    data = self.list_ap()
    for d in data:
      if d.get('ACTIVE') == 'yes':
        return d
    return None

  def connection_detail(self):
    """Methode, die Detaildaten der aktiven WLAN-Verbindung liefert.
    
    Rückgabe ist ein Dictionary mit allen von 'nmcli connection show <uuid>'
    gelieferten Werten.
    Besteht keine aktive WLAN-Verbindung, wird None zurückgegeben.
    """
    connection = None
    for d in self.list_connections():
      if d.get('ACTIVE') == 'yes':
        connection = d
        break
    else:
      return None

    command = ['nmcli', '--terse', 'connection', 'show', connection['UUID']]
    retcode, stdout, stderr = self.shell(command)    

    if retcode != 0:
      return None

    data = {}
    for line in stdout.split("\n"):
      values = line.split(':', 2)        
      if len(values) == 2:
        data[values[0]] = values[1]    
    return data

  def get_ip(self):
    """Methode, welche die IP-Adresse der aktiven WLAN-Verbindung liefert.
    
    Besteht keine aktive WLAN-Verbindung, wird None zurückgegeben.
    """
    data = self.connection_detail()
    if data is not None:
      ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', data.get('IP4.ADDRESS[1]', '') )
      if len(ip) > 0:
        return ip[0]
    return None


if __name__ == '__main__':
  ### Test der Methoden ###

  NMCLI = nmcli()
  import json
  print 'AP list:'
  print json.dumps(NMCLI.list_ap(), indent=2)
  print 'Connections:'
  print json.dumps(NMCLI.list_connections(), indent=2)
  print 'Current connection:'
  print json.dumps(NMCLI.current_connection(), indent=2)
  print 'Connection detail:'
  print json.dumps(NMCLI.connection_detail(), indent=2, sort_keys=True)
  print 'IP: {}'.format(NMCLI.get_ip())

