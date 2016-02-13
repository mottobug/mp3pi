
import subprocess
import os

class nmcli:
  def shell(self, args):
    os.environ["LANG"] = "C"
    process = subprocess.Popen(args, stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    retcode = process.returncode

    return retcode, stdout, stderr

  def get_values(self, fields, args):
    retcode, stdout, stderr = self.shell(args)
    
    data = []
    if retcode == 0:
      for line in stdout.split("\n"):
        values = line.split(":", len(fields)-1)
        row = dict(zip(fields, values))
        data.append(row)
    return data

  def list_ap(self):
    fields = ['ACTIVE', 'NAME', 'SSID', 'SIGNAL', 'SECURITY', 'BSSID']
    args = ['nmcli', '--terse', '--fields', ",".join(fields), "dev", "wifi", "list"]
    
    data = self.get_values(fields, args)

    return(data)

  def list_connections(self):
    fields = ['ACTIVE', 'NAME', 'UUID', 'TYPE']
    args = ['nmcli', '--terse', '--fields', ",".join(fields), "con", "show"]
    
    data = self.get_values(fields, args)

    for d in data:
      if d.get('TYPE', False) != "802-11-wireless":
        data.remove(d)
    
    return(data)
  
  def activate_connection(self, name):
    args = ['nmcli', "con", "up", "id", name]
    retcode, stdout, stderr = self.shell(args)
    
    if retcode != 0:
      return(False)
    else:
      return(True)

  def current_connection(self):
    data = self.list_ap()
    for d in data:
      if d.get('ACTIVE', False) == "yes":
        return(d)

  def connection_detail(self):
    data = self.list_connections()
    
    connection = None
    for d in data:
      if d.get('ACTIVE', False) == "yes":
        connection = d
        break
    
    if connection is None:
      return(False)

    args = ['nmcli', "--terse", "con", "show", connection['UUID']]
    retcode, stdout, stderr = self.shell(args)    

    if retcode != 0:
      return(False)

    data = {}
    if retcode == 0:
      for line in stdout.split("\n"):
        row = {}
        values = line.split(":", 2)
        
        if len(values) == 2:
          data[values[0]] = values[1]
    
    return(data)

  def get_ip(self):
    data = self.connection_detail()
    if data is not False:
      return(data.get('IP4.ADDRESS[1]', None))





NMCLI = nmcli()
#for i in NMCLI.list_ap():
#  print(i)
#for i in NMCLI.list_connections():
#  print(i)
#print(NMCLI.current_connection())
#print(NMCLI.connection_detail())
print(NMCLI.get_ip())
