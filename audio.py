import sys
import alsaaudio

class AlsaInterface():

  mixer = ""

  def __init__(self):
    # picks first mixer and set as default
    all_mixers = self.list_mixers()
    self.mixer = all_mixers[0]
    print("AlsaInterface: Setting default mixer to: " + self.mixer)

  def list_mixers(self, **kwargs):
    #for m in alsaaudio.mixers(**kwargs):
      #print("  '%s'" % m)
    return(alsaaudio.mixers(**kwargs))
      
  def get_mixer(self, name):
    if not name:
      name = self.mixer
    try:
      mixer = alsaaudio.Mixer(name, **kwargs)
    except alsaaudio.ALSAAudioError:
      print("No such mixer")
      sys.exit(1)
    return(mixer)

  def set_volume(self, name, volume):
    mixer = self.get_mixer(name)
    mixer.setvolume(int(volume), alsaaudio.MIXER_CHANNEL_ALL)

  def get_volume(self, name):
    mixer = self.get_mixer(name)
    volumes = mixer.getvolume()
    return(volumes[0])
