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
kivy.require('1.11.1')
from kivy.app import App 
from kivy.uix.screenmanager import ScreenManager, Screen 
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from playsound import playsound
from kivy.core.window import Window

# Manager for the screens
class WindowManager(ScreenManager):
	pass
		

class TitleScreen(Screen):
	pass


# Wrapper for the screens so that they are all similar
class ScreenWrapper(Screen):
	pass


class Comparison(ScreenWrapper):

	compare_text = StringProperty()
	scale = StringProperty()
	scale_text = StringProperty()
	is_recording = BooleanProperty()
	is_sharp = BooleanProperty()
	is_right = BooleanProperty()

	def __init__(self, **kwargs):
		super(Comparison, self).__init__(**kwargs)
		self.compare_text = "Comparison"
		self.scale_text = "None"
		self.scale = ""
		self.is_recording = False
		self.is_sharp = True
		self.is_right = True
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
		if len(self.notes) < len(self.scale_dict[self.scale]):
			self.is_right = False
		else:
			for note in self.notes:
				if note not in self.scale_dict[self.scale]:
					self.is_right = False
		if self.is_right == True:
			print('You are Correct!')
			playsound('music/victory.wav')
		else:
			print('You are incorrect.')
			playsound('music/failure.wav')
			self.is_right = True

	def on_leave(self):
		self.is_recording = False

class Analysis(ScreenWrapper):

	pitch_text = StringProperty()
	is_recording = BooleanProperty()
	bpm = StringProperty()
	key = StringProperty()

	def __init__(self, **kwargs):
		super(Analysis, self).__init__(**kwargs) 
		self.pitch_text	= "Analysis"
		self.is_recording = False
		self.bpm = "None"
		self.key = "None"
		self.key_dict = {
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

	def analyze(self):
		self.gate = True
		while self.state == 'down':
			if self.gate == True:
				Analysis.record_init(self, self.state)
				self.gate = False
		Analysis.get_bpm_init(self, 'output.wav')
		self.bpm = str(round(self.q.get(), 2))
		self.gate = True
		self.key_running = True
		while self.key_running == True:
			if self.gate == True:
				Analysis.get_key_init(self, 'output.wav')
				self.gate = False
		self.key = str(self.q.get())
		raise Exception("Thread Terminated")

	def get_key_init(self, filename):
		self.filename = filename
		t = Thread(target=Analysis.get_key, args=(self,))
		t.daemon = True
		t.start()

	def get_key(self):
		Analysis.get_pitch_init(self, self.filename)
		notes = self.q.get()
		key_list = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
		for note in notes:
			#print(note)
			for key in key_list:
				#print(key)
				if note not in self.key_dict[key]:
					key_list.remove(key)
		print(key_list)
		self.q.put(key_list)
		self.key_running = False
		raise Exception("Thread Terminated")

	def get_bpm_init(self, filename):
		self.filename = filename
		t = Thread(target=Analysis.get_bpm, args=(self,))
		t.daemon = True
		t.start()


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
	            #if o.get_confidence() > .2 and len(beats) > 2.:
	            #    break
	        total_frames += read
	        if read < hop_s:
	            break

	    def beats_to_bpm(beats):
	        # if enough beats are found, convert to periods then to bpm
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


	def get_pitch_init(self, filename):
		self.filename = filename
		self.t = Thread(target=Analysis.get_pitch, args=(self,))
		self.t.daemon = True
		self.t.start()

	# Gets the musical notes from a file
	def get_pitch(self):
		if path.exists(self.filename) == False:
			self.pitch_text = "Path does not exist"
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

			#print(notes)
			self.q.put(notes)
			#raise Exception("Thread Terminated")

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
				sleep(.05)
			#print(freq2note(pitch))

		raise Exception("Thread Terminated") # Terminates the thread


class Metronome(ScreenWrapper):
	
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
				sleep(bpm - .034)
			elif self.format_text == '3/4':
				if counter == 0 or counter%3 == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep(bpm - .034)
			elif self.format_text == '4/4':
				if counter == 0 or counter%4 == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep(bpm - .034)
			elif self.format_text == '6/8':
				if counter == 0 or counter%6 == 0:
					playsound('music/highmet.wav')
				elif counter%3 == 0:
					playsound('music/medmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep(bpm - .034)
			elif self.format_text == '2/2':
				if counter%2 == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')
				sleep(bpm - .034)
			else:
				if counter%int(self.format_text[0]) == 0:
					playsound('music/highmet.wav')
				else:
					playsound('music/lowmet.wav')

			counter += 1
		raise Exception("Thread Terminated")


class BandApp(App):

	def build(self):
		Window.clearcolor = (.3, .3, .3, 1)

if __name__ == '__main__':
	BandApp().run()
