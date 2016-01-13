
import time
import NetworkManager

from objbrowser import browse

class NetworkManagerWrapper:
  
  ssid = None
  strength = None
  frequency = None
  ip = None
  psk = None
  
  # known aps
  known_aps = []

  # visible aps
  visible_aps = []

  connection_types = ['wireless','wwan','wimax']

  
  def __init__(self):
    self.Update()
  
  def Update(self):
    self.visible_aps = []
    self.known_aps = []

    try:
      for conn in NetworkManager.NetworkManager.ActiveConnections:
        settings = conn.Connection.GetSettings()

        secrets = conn.Connection.GetSecrets()
        
        if secrets['802-11-wireless-security']:
          if secrets['802-11-wireless-security']['psk']:
            self.psk = secrets['802-11-wireless-security']['psk']

        for dev in conn.Devices:
          if hasattr(dev.Ip4Config, 'Addresses'):
            for addr in dev.Ip4Config.Addresses:
              self.ip = addr[0]
          if hasattr(dev.Ip4Config, 'Routes'):
            for route in dev.Ip4Config.Routes:
              time.time()
              # route
          if hasattr(dev.Ip4Config, 'Nameservers'):
            for ns in dev.Ip4Config.Nameservers:
              time.time()
    except:
      print("except")
    finally:
      True
      

    for device in NetworkManager.NetworkManager.GetDevices():
      if device.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
        continue
      
      specific_device = device.SpecificDevice()
      active = specific_device.ActiveAccessPoint
      # active.Ssid
      for ap in device.SpecificDevice().GetAccessPoints():
        self.known_aps.append({
          "ssid": ap.Ssid,
          "strength": ap.Strength,
          "frequency": ap.Frequency})
              
        #print(active)
        
        if hasattr(active, 'object_path'):
          if ap.object_path == active.object_path:
            self.ssid = ap.Ssid
            self.strength = ap.Strength
            self.frequency = ap.Frequency

    for device in NetworkManager.NetworkManager.GetDevices():
      if device.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
        continue
      #print("Visible on %s" % device.Udi[device.Udi.rfind('/')+1:])
      device = device.SpecificDevice()
      active = device.ActiveAccessPoint
      aps = device.GetAccessPoints()
      for ap in aps:
        prefix = '* ' if ap.object_path == active.object_path else '  '
        #print("%s %s %s" % (prefix, ap.Ssid, ap.Strength))
        self.visible_aps.append({
          "ssid": ap.Ssid,
          "strength": ap.Strength,
          "frequency": ap.Frequency})

  def ListKnownConnections(self):
    active = []
    for x in NetworkManager.NetworkManager.ActiveConnections:
      active.append(x.Connection.GetSettings()['connection']['id'])
  
    connections = []
    for x in NetworkManager.Settings.ListConnections():
      if x.GetSettings()['connection']['type'] != "802-11-wireless":
        continue

      if x.GetSettings()['connection']['id'] in active:
        current_connection = True
      else:
        current_connection = False

      connections.append(
          (current_connection,
            x.GetSettings()['connection']['id'], 
            x.GetSettings()['connection']['type']))

    return(connections)

  def enable(self, names):
      for n in names:
          if n not in self.connection_types:
              print("No such connection type: %s" % n)
              return
              #sys.exit(1)
          setattr(NetworkManager.NetworkManager, n.title() + 'Enabled', True)

  def activate(self, network):
    connections = NetworkManager.Settings.ListConnections()
    connections = dict([(x.GetSettings()['connection']['id'], x) for x in connections])

    if not NetworkManager.NetworkManager.NetworkingEnabled:
        NetworkManager.NetworkManager.Enable(True)
    for n in network:
        if n not in connections:
            print("No such connection: %s" % n)
            return
            #sys.exit(1)

        print("Activating connection '%s'" % n)
        conn = connections[n]
        ctype = conn.GetSettings()['connection']['type']
        if ctype == 'vpn':
            for dev in NetworkManager.NetworkManager.GetDevices():
                if dev.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED and dev.Managed:
                    break
            else:
                print("No active, managed device found")
                return
                #sys.exit(1)
        else:
            dtype = {
                '802-11-wireless': 'wlan',
                'gsm': 'wwan',
            }
            if dtype in self.connection_types:
                enable(dtype)
            dtype = {
                '802-11-wireless': NetworkManager.NM_DEVICE_TYPE_WIFI,
                '802-3-ethernet': NetworkManager.NM_DEVICE_TYPE_ETHERNET,
                'gsm': NetworkManager.NM_DEVICE_TYPE_MODEM,
            }.get(ctype,ctype)
            devices = NetworkManager.NetworkManager.GetDevices()

            for dev in devices:
                print("s %s %s" % (dev.DeviceType, dev.State))
                print("i %s %s" % (dtype, NetworkManager.NM_DEVICE_STATE_DISCONNECTED))

                if dev.DeviceType == dtype and (dev.State == NetworkManager.NM_DEVICE_STATE_DISCONNECTED or dev.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED):
                    break
            else:
                print(dev.State)
                print("No suitable and available %s device found" % ctype)
                return
                #sys.exit(1)

        NetworkManager.NetworkManager.ActivateConnection(conn, dev, "/")

  def visible():
    for device in NetworkManager.NetworkManager.GetDevices():
      if device.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
        continue
      print("Visible on %s" % device.Udi[device.Udi.rfind('/')+1:])
      device = device.SpecificDevice()
      active = device.ActiveAccessPoint
      aps = device.GetAccessPoints()
      for ap in aps:
        prefix = '* ' if ap.object_path == active.object_path else '  '
        print("%s %s %s" % (prefix, ap.Ssid, ap.Strength))
  


