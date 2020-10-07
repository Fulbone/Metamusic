import kivy
kivy.require('1.11.1')
from kivy.app import App 
from kivy.uix.screenmanager import ScreenManager, Screen 

class WindowManager(ScreenManager):
	pass
		
class ScreenWrapper(Screen):
	pass

class Comparison(ScreenWrapper, Screen):
	pass

class Analysis(ScreenWrapper, Screen):
	pass

class Tuner(ScreenWrapper, Screen):
	pass

class Metronome(ScreenWrapper, Screen):
	pass

class BandApp(App):
	def build(self):
		pass


if __name__ == '__main__':
	BandApp().run()