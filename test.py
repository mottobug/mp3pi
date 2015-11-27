from kivy.app import App
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

# Make sure the height is such that there is something to scroll.

class TestApp(App):
    def build(self):
      layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
      layout.bind(minimum_height=layout.setter('height'))
      for i in range(30):
          btn = Button(text=str(i), size_hint_y=None, height=40)
          layout.add_widget(btn)
      root = ScrollView(size_hint=(None, None), size=(400, 400))
      root.add_widget(layout)

if __name__ == "__main__":
    TestApp().run()
