import os

class Rpi_ScreenSaver:
  rpi_display = "/sys/class/backlight/rpi_backlight/bl_power"
  
  running_on_rpi = False

  display_state = True

  def __init__(self):
    if os.path.exists(self.rpi_display):
      self.running_on_rpi = True
      self.display_on()
      
  def set_bl_power(self, value):
    with open(self.rpi_display, "w") as f:
      f.write(value)
      f.close()
  
  def display_on(self):
    if self.running_on_rpi:
      self.set_bl_power("0")
    self.display_state = True

  def display_off(self):
    if self.running_on_rpi:
      self.set_bl_power("1")
    self.display_state = False
