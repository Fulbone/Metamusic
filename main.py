import kivy
kivy.require('1.11.1')
from kivy.app import App 
from kivy.uix.label import Label 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button 

class BandScreen(BoxLayout):
	pass
		
		



class BandApp(App):
	def build(self):
		return BandScreen()



if __name__ == '__main__':
	BandApp().run()