
import alsaaudio

class AlsaInterface():

  mixer = ""

  def __init__(self): # picks first mixer and set as default
    all_mixers = self.list_mixers()
    self.mixer = all_mixers[0]
    Logger.info("AlsaInterface: Setting default mixer to: " + self.mixer)

  def list_mixers(self, **kwargs):
    return(alsaaudio.mixers(**kwargs))
    #for m in alsaaudio.mixers(**kwargs):
      #print("  '%s'" % m)

  def set_mixer(self, name, args, kwargs):
      if not name:
        name = self.mixer
      try:
          mixer = alsaaudio.Mixer(name, **kwargs)
      except alsaaudio.ALSAAudioError:
          print("No such mixer")
          sys.exit(1)

      channel = alsaaudio.MIXER_CHANNEL_ALL

      volume = int(args)
      mixer.setvolume(volume, channel)

  def get_mixer(self, name, kwargs):
      if not name:
        name = self.mixer    
      try:
          mixer = alsaaudio.Mixer(name, **kwargs)
      except alsaaudio.ALSAAudioError:
          print("No such mixer")
          sys.exit(1)
      volumes = mixer.getvolume()
      return(volumes[0])

# pactl set-sink-volume  bluez_sink.0C_A6_94_E3_76_DA 35%

