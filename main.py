"""
MMMMMMMM               MMMMMMMM                             tttt                                                                                         iiii                           
M:::::::M             M:::::::M                          ttt:::t                                                                                        i::::i                          
M::::::::M           M::::::::M                          t:::::t                                                                                         iiii                           
M:::::::::M         M:::::::::M                          t:::::t                                                                                                                        
M::::::::::M       M::::::::::M    eeeeeeeeeeee    ttttttt:::::ttttttt      aaaaaaaaaaaaa      mmmmmmm    mmmmmmm   uuuuuu    uuuuuu      ssssssssss   iiiiiii     cccccccccccccccc     
M:::::::::::M     M:::::::::::M  ee::::::::::::ee  t:::::::::::::::::t      a::::::::::::a   mm:::::::m  m:::::::mm u::::u    u::::u    ss::::::::::s  i:::::i   cc:::::::::::::::c     
M:::::::M::::M   M::::M:::::::M e::::::eeeee:::::eet:::::::::::::::::t      aaaaaaaaa:::::a m::::::::::mm::::::::::mu::::u    u::::u  ss:::::::::::::s  i::::i  c:::::::::::::::::c     
M::::::M M::::M M::::M M::::::Me::::::e     e:::::etttttt:::::::tttttt               a::::a m::::::::::::::::::::::mu::::u    u::::u  s::::::ssss:::::s i::::i c:::::::cccccc:::::c     
M::::::M  M::::M::::M  M::::::Me:::::::eeeee::::::e      t:::::t              aaaaaaa:::::a m:::::mmm::::::mmm:::::mu::::u    u::::u   s:::::s  ssssss  i::::i c::::::c     ccccccc     
M::::::M   M:::::::M   M::::::Me:::::::::::::::::e       t:::::t            aa::::::::::::a m::::m   m::::m   m::::mu::::u    u::::u     s::::::s       i::::i c:::::c                  
M::::::M    M:::::M    M::::::Me::::::eeeeeeeeeee        t:::::t           a::::aaaa::::::a m::::m   m::::m   m::::mu::::u    u::::u        s::::::s    i::::i c:::::c                  
M::::::M     MMMMM     M::::::Me:::::::e                 t:::::t    tttttta::::a    a:::::a m::::m   m::::m   m::::mu:::::uuuu:::::u  ssssss   s:::::s  i::::i c::::::c     ccccccc     
M::::::M               M::::::Me::::::::e                t::::::tttt:::::ta::::a    a:::::a m::::m   m::::m   m::::mu:::::::::::::::uus:::::ssss::::::si::::::ic:::::::cccccc:::::c     
M::::::M               M::::::M e::::::::eeeeeeee        tt::::::::::::::ta:::::aaaa::::::a m::::m   m::::m   m::::m u:::::::::::::::us::::::::::::::s i::::::i c:::::::::::::::::c     
M::::::M               M::::::M  ee:::::::::::::e          tt:::::::::::tt a::::::::::aa:::am::::m   m::::m   m::::m  uu::::::::uu:::u s:::::::::::ss  i::::::i  cc:::::::::::::::c     
MMMMMMMM               MMMMMMMM    eeeeeeeeeeeeee            ttttttttttt    aaaaaaaaaa  aaaammmmmm   mmmmmm   mmmmmm    uuuuuuuu  uuuu  sssssssssss    iiiiiiii    cccccccccccccccc  
Licensed under the MIT License
Metamusic was a project for the Congressional App Challenge of 2020
It was created by Jake Fulford and Will Sugden.
Metamusic is able to tell if one is playing a musical scale correctly.
It can analyze the bpm and a key of a recording.
It also has a built in tuner and metronome.
And to my Band Director, thank you for these amazing years! Sorry that you can't hear us play. :(
"""

# Importing
print("Loading...")
import sys
import aubio
from aubio import source, pitch, tempo, midi2note, freq2note, note2freq
from os import path
import numpy as np
from numpy import median, diff
import pyaudio
import wave
import queue
from time import sleep
from math import log
from threading import Thread
import kivy
kivy.require('1.11.1') # Requires kivy version 1.11.1
from kivy.config import Config 
Config.set('graphics', 'resizable', False)
from kivy.app import App 
from kivy.uix.screenmanager import ScreenManager, Screen 
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.image import Image
from playsound import playsound


# Manager for the screens
class WindowManager(ScreenManager):
	pass
		

#Controls the Title Screen
class TitleScreen(Screen):
	pass


# Wrapper for the screens so that they are all similar
class ScreenWrapper(Screen):
	pass


# Handles the Comparison Screen
class Comparison(ScreenWrapper):

	compare_text = StringProperty()
	scale = StringProperty()
	scale_text = StringProperty()
	is_recording = BooleanProperty()
	is_sharp = BooleanProperty()
	is_right = BooleanProperty()
	is_correct = StringProperty()

	def __init__(self, **kwargs):
		super(Comparison, self).__init__(**kwargs)
		self.compare_text = "Comparison"
		self.scale_text = "None"
		self.scale = ""
		self.is_recording = False
		self.is_sharp = True
		self.is_right = True
		self.is_correct = ''
		self.scale_dict = {
		"A Scale": ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#'],
		"A# Scale": ['A#', 'C', 'D', 'D#', 'F', 'G', 'A'],
		"B Scale": ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#'],
		"C Scale": ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
		"C# Scale": ['C#', 'D#', 'F', 'F#', 'G#', 'A#', 'C'],
		"D Scale": ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'],
		"D# Scale": ['D#', 'F', 'G', 'G#', 'A#', 'C', 'D'],
		"E Scale": ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'],
		"F Scale": ['F', 'G', 'A', 'A#', 'C', 'D', 'E'],
		"F# Scale": ['F#', 'G#', 'A#', 'B', 'C#', 'D#', 'F'],
		"G Scale": ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
		"G# Scale": ['G#', 'A#', 'C', 'C#', 'D#', 'F', 'G']
		}

	# Starts the thread that records and compares scales
	def record_scale(self, state):
		if self.scale == "":
			self.is_correct = "Select a Scale"
		else:
			self.state = state
			if self.state == 'down':
				self.is_recording = True
				self.q = queue.Queue()
				self.t = Thread(target=Comparison.record_compare, args=(self,))
				self.t.daemon = True
				self.t.start()
			else:
				self.is_recording = False

	# Calls the funcs to compare the scales
	def record_compare(self):
		self.gate = True
		while self.state == 'down':
			if self.gate == True:
				Analysis.record_init(self, self.state)
				self.gate = False
		if path.exists('output.wav') == False:
			sleep(1)
			if path.exists('output.wav') == False:
				raise Exception("No file found")
		Analysis.get_pitch_init(self, 'output.wav')
		self.notes = self.q.get()
		if len(self.notes) < len(self.scale_dict[self.scale]):
			self.is_right = False
		else:
			for note in self.notes:
				if note not in self.scale_dict[self.scale]:
					self.is_right = False
		if self.is_right == True:
			print('You are Correct!')
			self.is_correct = 'You were Correct!'
			playsound('music/victory.wav')
		else:
			print('You are incorrect.')
			self.is_correct = 'You were Incorrect'
			playsound('music/failure.wav')
			self.is_right = True

	# Stops recording on leave
	def on_leave(self):
		self.is_recording = False


# Handles the Analysis Screen
class Analysis(ScreenWrapper):

	pitch_text = StringProperty()
	is_recording = BooleanProperty()
	bpm = StringProperty()
	key = StringProperty()
	is_major = BooleanProperty()

	def __init__(self, **kwargs):
		super(Analysis, self).__init__(**kwargs) 
		self.pitch_text	= "Analysis"
		self.is_recording = False
		self.bpm = "None"
		self.key = "None"
		self.is_major = True
		self.major_dict = {
		"A": ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#'],
		"A#": ['A#', 'C', 'D', 'D#', 'F', 'G', 'A'],
		"B": ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#'],
		"C": ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
		"C#": ['C#', 'D#', 'F', 'F#', 'G#', 'A#', 'C'],
		"D": ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'],
		"D#": ['D#', 'F', 'G', 'G#', 'A#', 'C', 'D'],
		"E": ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'],
		"F": ['F', 'G', 'A', 'A#', 'C', 'D', 'E'],
		"F#": ['F#', 'G#', 'A#', 'B', 'C#', 'D#', 'F'],
		"G": ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
		"G#": ['G#', 'A#', 'C', 'C#', 'D#', 'F', 'G']
		}
		self.minor_dict = {
		"A": ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
		"A#": ['A#', 'C', 'C#', 'D#', 'F', 'F#', 'G#'],
		"B": ['B', 'C#', 'D', 'E', 'F#', 'G', 'A'],
		"C": ['C', 'D', 'D#', 'F', 'G', 'G#', 'A#'],
		"C#": ['C#', 'D#', 'E', 'F#', 'G#', 'A', 'B'],
		"D": ['D', 'E', 'F', 'G', 'A', 'A#', 'C'],
		"D#": ['D#', 'F', 'F#', 'G#', 'A#', 'B', 'C#'],
		"E": ['E', 'F#', 'G', 'A', 'B', 'C', 'D'],
		"F": ['F', 'G', 'G#', 'A#', 'C', 'C#', 'D#'],
		"F#": ['F#', 'G#', 'A', 'B', 'C#', 'D', 'E'],
		"G": ['G', 'A', 'A#', 'C', 'D', 'E', 'F'],
		"G#": ['G#', 'A#', 'B', 'C#', 'D#', 'E', 'F#']
		}

	# Sets the bpm and key to "None" on enter
	def on_enter(self):
		self.bpm = "None"
		self.key = "None"

	# Starts the thread that analyzes a recording
	def analyze_init(self, state):
		self.state = state
		if self.state == 'down':
			self.is_recording = True
			self.q = queue.Queue()
			t = Thread(target=Analysis.analyze, args=(self,))
			t.daemon = True
			t.start()
		else:
			self.is_recording = False

	# Calls the funcs to analyze
	def analyze(self):
		self.gate = True
		while self.state == 'down':
			if self.gate == True:
				Analysis.record_init(self, self.state)
				self.gate = False
		if path.exists('output.wav') == False:
			sleep(1)
			if path.exists('output.wav') == False:
				raise Exception("No file found")
		Analysis.get_bpm_init(self, 'output.wav')
		bpm = self.q.get()
		if bpm == 0:
			self.bpm = "Unsure"
		else:
			self.bpm = str(round(bpm, 2))
		self.gate = True
		self.key_running = True
		while self.key_running == True:
			if self.gate == True:
				Analysis.get_key_init(self, 'output.wav')
				self.gate = False
		key = self.q.get()
		if len(key) > 3 or len(key) == 0:
			self.key = "Unsure"
		else:
			self.key = str(key)
		raise Exception("Thread Terminated")

	# Starts the key analysis
	def get_key_init(self, filename):
		self.filename = filename
		t = Thread(target=Analysis.get_key, args=(self,))
		t.daemon = True
		t.start()

	# Analyses the key from a recording
	def get_key(self):
		Analysis.get_pitch_init(self, self.filename)
		notes = self.q.get()
		print(notes)
		key_list = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
		if self.is_major == True:
			for note in notes:
				for key in key_list:
					if note not in self.major_dict[key]:
						key_list.remove(key)
		else:
			for note in notes:
				for key in key_list:
					if note not in self.minor_dict[key]:
						key_list.remove(key)
		print(key_list)
		self.q.put(key_list)
		self.key_running = False
		raise Exception("Thread Terminated")

	# Starts the BPM analysis
	def get_bpm_init(self, filename):
		self.filename = filename
		t = Thread(target=Analysis.get_bpm, args=(self,))
		t.daemon = True
		t.start()

	# Gets the BPM from a recording
	def get_bpm(self):
	    samplerate, win_s, hop_s = 44100, 1024, 512

	    s = source(self.filename, samplerate, hop_s)
	    samplerate = s.samplerate
	    o = tempo("specdiff", win_s, hop_s, samplerate)
	    # List of beats, in samples
	    beats = []
	    # Total number of frames read
	    total_frames = 0

	    while True:
	        samples, read = s()
	        is_beat = o(samples)
	        if is_beat:
	            this_beat = o.get_last_s()
	            beats.append(this_beat)
	        total_frames += read
	        if read < hop_s:
	            break

	    # Changes the beats into BPM
	    def beats_to_bpm(beats):
	        if len(beats) > 1:
	            if len(beats) < 4:
	                print("Few beats found")
	            bpms = 60./diff(beats)
	            return median(bpms)
	        else:
	            print("Not enough beats found")
	            return 0

	    self.q.put(beats_to_bpm(beats))
	    raise Exception("Thread Terminated")

	# Starts the pitch analysis
	def get_pitch_init(self, filename):
		self.filename = filename
		self.t = Thread(target=Analysis.get_pitch, args=(self,))
		self.t.daemon = True
		self.t.start()

	# Gets the pitches from a recording
	def get_pitch(self):		
		while path.exists('output.wav') == False:
			pass

		else:
			samplerate = 44100
			win_s = 4096
			hop_s = 512

			s = source(self.filename, samplerate, hop_s)
			samplerate = s.samplerate

			tolerance = 0.8

			pitch_o = pitch("yin", win_s, hop_s, samplerate)
			pitch_o.set_unit("midi")
			pitch_o.set_tolerance(tolerance)

			pitches = []
			confidences = []

			# Total number of frames read
			total_frames = 0

			while True:
			    samples, read = s()
			    pitch_midi = pitch_o(samples)[0]
			    pitch_midi = int(round(pitch_midi))
			    confidence = pitch_o.get_confidence()
			    if confidence < 0.9: pitch_midi = 0.
			    if len(pitches) == 0 and pitch_midi != 0:
			    	pitches.append(pitch_midi)
			    elif len(pitches) > 0:
			    	if pitch_midi != pitches[-1] and pitch_midi != 0:
			    		pitches.append(pitch_midi)
			    else:
			    	pass
			    
			    confidences += [confidence]
			    total_frames += read
			    if read < hop_s: break

			notes = []
			for midi in pitches:
				note = midi2note(midi)
				notes.append(note.strip("0123456789"))

			self.q.put(notes)
			raise Exception("Thread Terminated")

	# Starts the thread to record from mic
	def record_init(self, state):
		self.state = state

		if self.state == 'down': # Checks if the button is in a pressed state
			self.is_recording = True
			self.t = Thread(target=Analysis.record, args=(self, self.state))
			self.t.daemon = True
			self.t.start()
		else:
			self.is_recording = False

	# Records input from the default mic
	def record(self, state, chunk=1024, wavformat=pyaudio.paInt16, channels=1, rate=44100, wave_output_filename="output.wav"):
		self.state = state

		p = pyaudio.PyAudio()

		stream = p.open(format=wavformat,
						channels=channels,
						rate=rate,
						input=True,
						frames_per_buffer=chunk)

		print("Recording...")

		frames = []

		while self.state == 'down': # Reads data while button is pressed
				data = stream.read(chunk)
				frames.append(data)

		print("Done Recording")

		stream.close()
		p.terminate()

		# Converts the array into a .wav file
		if len(frames) == 0:
			raise Exception('Not enough frames')
		else:
			wf = wave.open(wave_output_filename, 'wb')
			wf.setnchannels(channels)
			wf.setsampwidth(p.get_sample_size(wavformat))
			wf.setframerate(rate)
			wf.writeframes(b''.join(frames))
			wf.close()
			while path.exists('output.wav') == False:
				pass
			raise Exception("Thread Terminated")

	# Stops recording on leave
	def on_leave(self):
		self.state = 'up'


# Handles the Tuner Screen
class Tuner(ScreenWrapper):
	
	note_text = StringProperty()
	cent_text = StringProperty()
	posy = NumericProperty()
	color_red = NumericProperty()
	color_green = NumericProperty()
	color_blue = NumericProperty()


	def __init__(self, **kwargs):
		super(Tuner, self).__init__(**kwargs)
		self.note_text = " "
		self.cent_text = " "
		self.posy = .65
		self.color_red = 0
		self.color_green = 0
		self.color_blue = 0

	# Starts the thread to tune from the mic when the screen is entered
	def on_enter(self):
		print("Tuning..")
		self.t = Thread(target=Tuner.tune, args=(self,))
		self.is_running = True
		self.t.daemon = True
		self.t.start()

	# Closes thread on leave
	def on_leave(self):
		self.is_running = False
		print("Done Tuning")

	# Tunes from the mic
	def tune(self):
		pDetection = aubio.pitch("default", 2048, 1024, 44100)
		pDetection.set_unit('Hz')
		pDetection.set_silence(-40)

		p = pyaudio.PyAudio()

		stream = p.open(format=pyaudio.paFloat32,
    					channels=1, 
    					rate=44100, 
    					input=True,
    					frames_per_buffer=1024)

		while self.is_running == True:

			data = stream.read(1024)

			samples = np.frombuffer(data, dtype=aubio.float_type)
			pitch = pDetection(samples)[0]

			if pitch != 0:
				pitch_cent = round(1200 * log(pitch / note2freq(freq2note(pitch)), 2), 2) # Converts Hz to Cents
				self.note_text = freq2note(pitch)
				self.cent_text = str(pitch_cent)
				if pitch_cent < 0:
					self.posy = .4
				else:
					self.posy = .6
				self.color_red = round((abs(pitch_cent) * .051), 3) # Calculates the red 
				self.color_green = round(((abs(pitch_cent) * -.051) + 2.55), 3) # Calculates the green
				print(f"Green: {self.color_green} Red: {self.color_red}")

		raise Exception("Thread Terminated") # Terminates the thread


# Handles the Metronome Screen
class Metronome(ScreenWrapper):
	
	met_text = StringProperty()
	format_text = StringProperty()
	met_format = NumericProperty()
	counter = NumericProperty()
	image_source = StringProperty()

	def __init__(self, **kwargs):
		super(Metronome, self).__init__(**kwargs) 
		self.met_text = ""
		self.format_text = 'None'
		self.met_format = 4 
		self.clock = None
		self.counter = 0 
		self.image_source = 'images/metmed.png'

	# Schedules the met to be played
	def met(self, state, bpm):
		self.state = state
		self.bpm = bpm
		if self.state == 'down': # Checks if state is down
			if self.bpm.isdigit() == False: # Checks if the BPM is a int
				self.met_text = "Input the BPM"
			else:
				self.bpm = int(self.bpm)
				if self.bpm < 1: # Checks if the BPM is less than 1
					self.met_text = "Input the BPM"
				else:
					if self.format_text == "None": # Checks if no format was selected
						self.met_text = "Select a format"
					else:
						self.bpm = 60/self.bpm
						self.met_text = ""
						self.t = Thread(target=Metronome.playmet, args=(self, self.bpm))
						self.is_running = True
						self.t.daemon = True
						self.t.start()

		# Kills the thread running the Metronome
		else:
			self.is_running = False

	# Plays the metronome sound
	def playmet(self, bpm):
		self.counter = 0
		while self.is_running == True:
			if self.counter%2 == 0 or self.counter == 0:
				self.image_source = 'images/metleft.png'
			else:
				self.image_source = 'images/metright.png'

			if self.format_text == '2/4':
				if self.counter == 0 or self.counter%2 == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep(bpm - .034)
			elif self.format_text == '3/4':
				if self.counter == 0 or self.counter%3 == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep(bpm - .034)
			elif self.format_text == '4/4':
				if self.counter == 0 or self.counter%4 == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep(bpm - .034)
			elif self.format_text == '3/8':
				if self.counter == 0 or self.counter%3 == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep((bpm/3) - .034)
			elif self.format_text == '6/8':
				if self.counter == 0 or self.counter%6 == 0:
					playsound('music/highmet.wav')
				elif self.counter%3 == 0:
					playsound('music/medmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep((bpm/3) - .034)
			elif self.format_text == '9/8':
				if self.counter == 0 or self.counter%9 == 0:
					playsound('music/highmet.wav')
				elif self.counter%3 == 0:
					playsound('music/medmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep((bpm/3) - .034)
			elif self.format_text == '12/8':
				if self.counter == 0 or self.counter%12 == 0:
					playsound('music/highmet.wav')
				elif self.counter%3 == 0:
					playsound('music/medmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep((bpm/3) - .034)
			elif self.format_text == '2/2':
				if self.counter == 0 or self.counter%2 == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep((bpm/2) - .034)
			elif self.format_text == '5/4':
				if self.counter == 0 or self.counter%5 == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep(bpm - .034)
			elif self.format_text == '6/4':
				if self.counter == 0 or self.counter%6 == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep(bpm - .034)
			else:
				pass

			self.counter += 1
		raise Exception("Thread Terminated")


# Builds the App
class MetamusicApp(App):

	def build(self):
		Window.clearcolor = (.3, .3, .3, 1) # Changes the Background color
		self.icon = 'images/logo.png' # Changes the Icon

if __name__ == '__main__':
	MetamusicApp().run() # Runs the app
