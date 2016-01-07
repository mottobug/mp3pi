
import time
import NetworkManager

class NetworkManagerWrapper:
  
  ssid = None
  strength = None
  frequency = None
  ip = None
  psk = None
  
  # visible aps
  aps = []
  
  def __init__(self):
    self.Update()
  
  def Update(self):
    self.aps = []

    for conn in NetworkManager.NetworkManager.ActiveConnections:
      settings = conn.Connection.GetSettings()

      secrets = conn.Connection.GetSecrets()
      
      if secrets['802-11-wireless-security']:
        if secrets['802-11-wireless-security']['psk']:
          self.psk = secrets['802-11-wireless-security']['psk']

      for dev in conn.Devices:
        for addr in dev.Ip4Config.Addresses:
          self.ip = addr[0]
        for route in dev.Ip4Config.Routes:
          time.time()
          # route
        for ns in dev.Ip4Config.Nameservers:
          time.time()
      

    for device in NetworkManager.NetworkManager.GetDevices():
      if device.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
        continue
      
      specific_device = device.SpecificDevice()
      active = specific_device.ActiveAccessPoint
      # active.Ssid
      for ap in device.SpecificDevice().GetAccessPoints():
        self.aps.append({
          "ssid": ap.Ssid,
          "strength": ap.Strength,
          "frequency": ap.Frequency})
              
        if ap.object_path == active.object_path:
          self.ssid = ap.Ssid
          self.strength = ap.Strength
          self.frequency = ap.Frequency

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

