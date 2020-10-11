import sys
import aubio
from aubio import source, pitch, midi2note, freq2note, note2freq
from os import path
import numpy as np 
import pyaudio
import wave
from math import log
from threading import Thread
import kivy
kivy.require('1.11.1')
from kivy.app import App 
from kivy.uix.screenmanager import ScreenManager, Screen 
from kivy.properties import StringProperty
from kivy.clock import Clock
from playsound import playsound


# Manager for the screens
class WindowManager(ScreenManager):
	pass
		
# Wrapper for the screens so that they are all similar
class ScreenWrapper(Screen):
	pass


class Comparison(ScreenWrapper, Screen):

	compare_text = StringProperty()

	def __init__(self, **kwargs):
		super(Comparison, self).__init__(**kwargs)
		self.compare_text = "Awaiting Comparison"

	# Compares pitches of 2 files using the get pitch method
	def compare_pitch(self, file1, file2):
		self.a = Analysis()
		file1_pitch = self.a.get_pitch(file1)	
		file2_pitch = self.a.get_pitch(file2)	

		if file1_pitch == file2_pitch:
			self.compare_text = "You are correct"
			print("\nYou are correct.")
		else:
			self.compare_text = "You are incorrect"
			print("\nYou are incorrect.")	


class Analysis(ScreenWrapper, Screen):

	pitch_text = StringProperty()	

	def __init__(self, **kwargs):
		super(Analysis, self).__init__(**kwargs) 
		self.pitch_text	= "Awaiting Analysis"

	# Gets the musical notes from a file
	def get_pitch(self, filename):
		self.filename = filename

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
				notes += [note]

			print(notes)
			self.pitch_text = str(notes)
			return notes

	# Starts the thread to record from mic
	def record_init(self, state):
		self.state = state
		self.t = Thread(target=Analysis.record, args=(self, self.state))
		self.t.daemon = True
		self.t.start()

	# Records input from the default mic
	def record(self, state, chunk=1024, wavformat=pyaudio.paInt16, channels=1, rate=44100, wave_output_filename="output.wav"):
		self.chunk = chunk
		self.wavformat = wavformat
		self.channels = channels
		self.rate = rate
		self.wave_output_filename = wave_output_filename

		if self.state == 'down': # Checks if the button is in a pressed state
			p = pyaudio.PyAudio()

			stream = p.open(format=self.wavformat,
							channels=self.channels,
							rate=self.rate,
							input=True,
							frames_per_buffer=self.chunk)

			print("Recording...")

			frames = []

			while self.state == 'down': # Reads data while button is pressed
				data = stream.read(self.chunk)
				frames.append(data)

			print("Done Recording")

			stream.close()
			p.terminate()

			wf = wave.open(self.wave_output_filename, 'wb')
			wf.setnchannels(self.channels)
			wf.setsampwidth(p.get_sample_size(self.wavformat))
			wf.setframerate(self.rate)
			wf.writeframes(b''.join(frames))
			wf.close()


class Tuner(ScreenWrapper, Screen):
	
	note_text = StringProperty()
	cent_text = StringProperty()

	def __init__(self, **kwargs):
		super(Tuner, self).__init__(**kwargs)
		self.note_text = " "
		self.cent_text = " "

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

			samples = np.fromstring(data, dtype=aubio.float_type)
			pitch = pDetection(samples)[0]

			if pitch != 0:
				pitch_cent = 1200 * round(log(pitch / int(note2freq(freq2note(pitch))), 2), 2)
				self.note_text = freq2note(pitch)
				self.cent_text = str(pitch_cent)
			print(int(pitch))

		raise Exception("Thread Terminated") # Terminates the thread


class Metronome(ScreenWrapper, Screen):
	
	met_text = StringProperty()

	def __init__(self, **kwargs):
		super(Metronome, self).__init__(**kwargs) 
		self.met_text = "Metronome OFF"
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
					self.clock = Clock.schedule_interval(Metronome.playmet, self.bpm)

		# Unschedules the met after the button is toggled off
		else:
			self.met_text = "Metronome OFF"
			Clock.unschedule(self.clock)

	# Plays the metronome sound
	def playmet(dt):
		playsound('met.wav')


class BandApp(App):

	def build(self):
		pass


if __name__ == '__main__':
	BandApp().run()