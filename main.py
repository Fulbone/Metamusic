import sys
import aubio
from aubio import source, pitch, midi2note, freq2note, note2freq
from os import path
import numpy as np 
import pyaudio
import wave
import queue
from time import sleep
from math import log
from threading import Thread
import kivy
kivy.require('1.11.1')
from kivy.app import App 
from kivy.uix.screenmanager import ScreenManager, Screen 
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from playsound import playsound
from kivy.core.window import Window

# Manager for the screens
class WindowManager(ScreenManager):
	pass
		
# Wrapper for the screens so that they are all similar
class ScreenWrapper(Screen):
	pass


class Comparison(ScreenWrapper, Screen):

	compare_text = StringProperty()
	scale = StringProperty()
	scale_text = StringProperty()
	is_recording = BooleanProperty()
	is_sharp = BooleanProperty()

	def __init__(self, **kwargs):
		super(Comparison, self).__init__(**kwargs)
		self.compare_text = "Comparison"
		self.scale_text = "None"
		self.scale = ""
		self.is_recording = False
		self.is_sharp = True
		self.scale_dict = {
		"A Scale": ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#', 'A', 'G#', 'F#', 'E', 'D', 'C#', 'B', 'A'],
		"A# Scale": ['A#', 'C', 'D', 'D#', 'F', 'G', 'A', 'A#', 'A' 'G', 'F', 'D#', 'D', 'C', 'A#'],
		"B Scale": ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#', 'B', 'A#', 'G#', 'F#', 'E', 'D#', 'C#', 'B'],
		"C Scale": ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C', 'B', 'A', 'G', 'F', 'E', 'D', 'C'],
		"C# Scale": ['C#', 'D#', 'F', 'F#', 'G#', 'A#', 'C' 'C#', 'C', 'A#', 'G#', 'F#', 'F', 'D#', 'C#'],
		"D Scale": ['D', 'E', 'F#', 'G', 'A', 'B', 'C#', 'D', 'C#', 'B', 'A', 'G', 'F#', 'E', 'D'],
		"D# Scale": ['D#', 'F', 'G', 'G#', 'A#', 'C', 'D', 'D#', 'D', 'C', 'A#', 'G#', 'G', 'F', 'D#'],
		"E Scale": ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#', 'E', 'D#', 'C#', 'B', 'A', 'G#', 'F#', 'E'],
		"F Scale": ['F', 'G', 'A', 'A#', 'C', 'D', 'E', 'F', 'E', 'D', 'C', 'A#', 'A', 'G', 'F'],
		"F# Scale": ['F#', 'G#', 'A#', 'B', 'C#', 'D#', 'F', 'F#', 'F', 'D#', 'C#', 'B', 'A#', 'G#', 'F#'],
		"G Scale": ['G', 'A', 'B', 'C', 'D', 'E', 'F#', 'G', 'F#', 'E', 'D', 'C', 'B', 'A', 'G'],
		"G# Scale": ['G#', 'A#', 'C', 'C#', 'D#', 'F', 'G', 'G#', 'G', 'F', 'D#', 'C#',  'C', 'A#', 'G#'],
		"A Scale": ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#', 'A', 'G#', 'F#', 'E', 'D', 'C#', 'B', 'A'],
		}

	# Compares pitches of 2 files using the get pitch method
	def compare_pitch(self, file1, file2):
		file1_pitch = self.a.get_pitch(file1)	
		file2_pitch = self.a.get_pitch(file2)	

		if file1_pitch == file2_pitch:
			self.compare_text = "You are correct"
			print("\nYou are correct.")
		else:
			self.compare_text = "You are incorrect"
			print("\nYou are incorrect.")

	def record_scale(self, state):
		if self.scale == "":
			self.scale_text = "Select a Scale"
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

	def record_compare(self):
		self.gate = True
		while self.state == 'down':
			if self.gate == True:
				Analysis.record_init(self, self.state)
				self.gate = False
		Analysis.get_pitch_init(self, 'output.wav')
		self.notes = self.q.get()

		if self.notes == self.scale_dict[self.scale]:
			playsound('music/victory.wav')
		else:
			print('FUCK NOOOOOOOOOOOO')

	def on_leave(self):
		self.is_recording = False

class Analysis(ScreenWrapper, Screen):

	pitch_text = StringProperty()
	is_recording = BooleanProperty()

	def __init__(self, **kwargs):
		super(Analysis, self).__init__(**kwargs) 
		self.pitch_text	= "Analysis"
		self.is_recording = False

	def get_pitch_init(self, filename):
		self.filename = filename
		self.t = Thread(target=Analysis.get_pitch, args=(self,))
		self.t.daemon = True
		self.t.start()

	# Gets the musical notes from a file
	def get_pitch(self):
		if path.exists(self.filename) == False:
			raise Exception(f"File Path to {self.filename} does not exist")

		else:
			downsample = 1
			samplerate = 44100 // downsample
			if len( sys.argv ) > 2: samplerate = int(sys.argv[2])

			win_s = 4096 // downsample # fft size
			hop_s = 512  // downsample # hop size

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
			    #print("%f %f %f" % (total_frames / float(samplerate), pitch, confidence))
			    if len(pitches) == 0 and pitch_midi != 0:
			    	pitches.append(pitch_midi)
			    elif len(pitches) > 0:
			    	if pitch_midi != pitches[-1] and pitch_midi != 0:
			    		pitches.append(pitch_midi)
			    else:
			    	pass
			    
			    #print(pitches)
			    confidences += [confidence]
			    total_frames += read
			    if read < hop_s: break

			if 0: sys.exit(0)
			notes = []
			for midi in pitches:
				note = midi2note(midi)
				notes.append(note.strip("0123456789"))

			print(notes)
			self.pitch_text = str(notes)
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

		wf = wave.open(wave_output_filename, 'wb')
		wf.setnchannels(channels)
		wf.setsampwidth(p.get_sample_size(wavformat))
		wf.setframerate(rate)
		wf.writeframes(b''.join(frames))
		wf.close()
		raise Exception("Thread Terminated")

	def on_leave(self):
		self.state = 'up'


class Tuner(ScreenWrapper, Screen):
	
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
				pitch_cent = round(1200 * log(pitch / note2freq(freq2note(pitch)), 2), 2)
				self.note_text = freq2note(pitch)
				self.cent_text = str(pitch_cent)
				if pitch_cent < 0:
					self.posy = .45
				else:
					self.posy = .65
				self.color_red = round((abs(pitch_cent) * .051), 3) 
				self.color_green = round(((abs(pitch_cent) * -.051) + 2.55), 3)
				print(f"Green: {self.color_green} Red: {self.color_red}")
			#print(freq2note(pitch))

		raise Exception("Thread Terminated") # Terminates the thread


class Metronome(ScreenWrapper, Screen):
	
	met_text = StringProperty()
	format_text = StringProperty()
	met_format = NumericProperty()

	def __init__(self, **kwargs):
		super(Metronome, self).__init__(**kwargs) 
		self.met_text = "Metronome OFF"
		self.format_text = 'None'
		self.met_format = 4 
		self.clock = None

	# Schedules the met to be played
	def met(self, state, bpm):
		self.state = state
		self.bpm = bpm
		if self.state == 'down':
			if self.bpm.isdigit() == False :
				self.met_text = "Input was not a natural number"
			else:
				self.bpm = int(self.bpm)
				if self.bpm < 1:
					self.met_text = "Input was not a natural number"
				else:
					self.bpm = 60/self.bpm
					self.met_text = "Metronome ON"
					self.t = Thread(target=Metronome.playmet, args=(self, self.bpm))
					self.is_running = True
					self.t.daemon = True
					self.t.start()

		# Kills the thread running the Metronome
		else:
			self.met_text = "Metronome OFF"
			self.is_running = False

	# Plays the metronome sound
	def playmet(self, bpm):
		counter = 0
		while self.is_running == True:
			if self.format_text == '2/4':
				if counter == 0 or counter%2 == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep(bpm)
			elif self.format_text == '3/4':
				if counter == 0 or counter%3 == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep(bpm)
			elif self.format_text == '4/4':
				if counter == 0 or counter%4 == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep(bpm)
			elif self.format_text == '6/8':
				if counter == 0 or counter%6 == 0:
					playsound('music/highmet.wav')
				elif counter%3 == 0:
					playsound('music/met.wav')
				else:
					playsound('music/lowmet.wav')
				sleep(bpm/3)
			else:
				pass

			counter += 1
		raise Exception("Thread Terminated")


class BandApp(App):

	def build(self):
		pass

Window.clearcolor = (1, 1, 1, 1)

if __name__ == '__main__':
	BandApp().run()