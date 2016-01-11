
import gi
gi.require_version('NM', '1.0')
from gi.repository import NM

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

  def __init__(self):
    self.Update()

  def activate(self, name):
    client = NM.Client.new(None)

    connections = client.get_connections()

    for c in connections:
      if c.get_id() == name:
        client.activate_connection_async(c, None)
        return
    
    print("connection not found")


  def mode_to_string(self, mode):
    if mode == getattr(NM, '80211Mode').INFRA:
      return "INFRA"
    if mode == getattr(NM, '80211Mode').ADHOC:
      return "ADHOC"
    if mode == getattr(NM, '80211Mode').AP:
      return "AP"
    return "UNKNOWN"
 
  def flags_to_security(self, flags, wpa_flags, rsn_flags):
    str = ""
    if ((flags & getattr(NM, '80211ApFlags').PRIVACY) and
      (wpa_flags == 0) and (rsn_flags == 0)):
      str = str  + " WEP"
    if wpa_flags != 0:
      str = str + " WPA1"
    if rsn_flags != 0:
      str = str + " WPA2"
    if ((wpa_flags & getattr(NM, '80211ApSecurityFlags').KEY_MGMT_802_1X) or
      (rsn_flags & getattr(NM, '80211ApSecurityFlags').KEY_MGMT_802_1X)):
      str = str + " 802.1X"
    return str.lstrip()

  def Update(self):
    self.visible_aps = []
    self.known_aps = []

    client = NM.Client.new(None)
    devs = client.get_devices()

    for dev in devs:
      if dev.get_device_type() == NM.DeviceType.WIFI:
        active_ap = dev.get_active_access_point()

        if active_ap is not None:
          self.ssid = active_ap.get_ssid().get_data()
          print(self.ssid)
          self.strength = active_ap.get_strength()
          interface = dev.get_iface()
        

          ip_cfg = dev.get_ip4_config() 
          if ip_cfg is not None:
            addresses = ip_cfg.get_addresses()
            for address in addresses:
              self.ip = address.get_address()

        for ap in dev.get_access_points():
          self.visible_aps.append({
            "ssid": ap.get_ssid().get_data(),
            "strength": ap.get_strength(),
            "frequency": ap.get_frequency,
            "bssid": ap.get_bssid(),
            "mode": self.mode_to_string(ap.get_mode()),
            "security": self.flags_to_security(ap.get_flags(), ap.get_wpa_flags(), ap.get_rsn_flags())})


