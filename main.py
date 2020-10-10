import sys
from aubio import source, pitch, midi2note
from os import path
import numpy as np 
import pyaudio
import wave
from threading import Thread
import kivy
kivy.require('1.11.1')
from kivy.app import App 
from kivy.uix.screenmanager import ScreenManager, Screen 
from kivy.clock import Clock
from playsound import playsound


class WindowManager(ScreenManager):
	pass
		

class ScreenWrapper(Screen):
	pass


class Comparison(ScreenWrapper, Screen):

	def get_pitches(self, file1, file2):

		a = Analysis()
		file1_pitch = a.get_pitch(file1)	
		file2_pitch = a.get_pitch(file2)	

		if file1_pitch == file2_pitch:
			print("\nYou are correct.")
		else:
			print("\nYou are incorrect.")	


class Analysis(ScreenWrapper, Screen):

	def get_pitch(self, filename):

		if path.exists(filename) == False:
			raise Exception(f"File Path to {filename} does not exist")

		else:
			downsample = 1
			samplerate = 44100 // downsample
			if len( sys.argv ) > 2: samplerate = int(sys.argv[2])

			win_s = 4096 // downsample # fft size
			hop_s = 512  // downsample # hop size

			s = source(filename, samplerate, hop_s)
			samplerate = s.samplerate

			tolerance = 0.8

			pitch_o = pitch("yin", win_s, hop_s, samplerate)
			pitch_o.set_unit("midi")
			pitch_o.set_tolerance(tolerance)

			pitches = []
			confidences = []

			# total number of frames read
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
			return notes

	def record_init(self, state):

		self.state = state
		t = Thread(target=Analysis.record, args=(self, self.state))
		t.daemon = True
		t.start()

	def record(self, state, chunk=1024, wavformat=pyaudio.paInt16, channels=1, rate=44100, wave_output_filename="output.wav"):
		self.chunk = chunk
		self.wavformat = wavformat
		self.channels = channels
		self.rate = rate
		self.wave_output_filename = wave_output_filename
		if self.state == 'down':

			p = pyaudio.PyAudio()

			stream = p.open(format=self.wavformat,
							channels=self.channels,
							rate=self.rate,
							input=True,
							frames_per_buffer=self.chunk)

			print("Recording...")

			frames = []

			while self.state == 'down':
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

		else:
			pass


class Tuner(ScreenWrapper, Screen):
	pass


class Metronome(ScreenWrapper, Screen):
	
	def met(self, state, bpm):

		self.state = state
		self.bpm = bpm
		if self.state == 'down':
			if self.bpm.isdigit() == False :
				raise Exception("Input was not a natural number")
			else:
				self.bpm = int(self.bpm)
				if self.bpm < 1:
					raise Exception("Input was not a natural number")
				else:
					self.bpm = 60/self.bpm
					met_event = Clock.schedule_interval(Metronome.playmet, self.bpm)
		else:
			Clock.unschedule(met_event)

	def playmet(time):
		playsound('met.wav')


class BandApp(App):

	def build(self):
		pass


if __name__ == '__main__':
	BandApp().run()