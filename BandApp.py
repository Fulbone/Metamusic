import os
import sys
from time import sleep
from playsound import playsound
from aubio import source, pitch, midi2note
import numpy as np 

os.system("cls")

def main():
	global pitch
	
	print("""
Select which operation you would like to perform
1 Analysis
2 Sample Comparison
3 Metronome
4 Tuner (NOT YET IMPLEMENTED)

Enter one of the numbers displayed to select the operation
""")

	answer = input()
	while answer not in ("1", "2", "3", "4"):
		answer = input("Invalid Input, select one of the numbers")

	if answer == "1":

		sample = input("\nPut in the file name of the sample you want to be analyzed, including extension: ")

		print("\nAnalyzing the file...")
		sample_analyzed = get_pitch(sample)
		print("\nSample's Pitches:", end= ' ')
		for midi in sample_analyzed:
			print(midi2note(midi), end = ' ')

	elif answer == "2":

		template = input("\nInput sound template file name, including extension: ")
		sample = input("Input your sample file name, including extension: ")

		print("\nComparing the two...\n")

		template_pitch = get_pitch(template)
		sample_pitch = get_pitch(sample)
		
		print("Template Pitches:", end = ' ')
		for midi in template_pitch:
			print(midi2note(midi), end = ' ')
		print("\nSample Pitches:", end =  ' ')
		for midi in sample_pitch:
			print(midi2note(midi), end = ' ')

		if sample_pitch == template_pitch:
			print("\nYou are correct.")
		else:
			print("\nYou are incorrect.")

	elif answer == "3":

		bpm = input("\nInput the bpm you want the metronome to go at: ")
		while bpm.isdigit() == False:
			bpm = input("Invalid input, enter a postive natural number: ")
		bpm = int(bpm)
		print("\nPress any key to stop the metronome")
		sleep(1)
		print("\nPlaying Metronome...")

		bpm = 60/bpm
		while True:
			playsound("met.wav")
			sleep(bpm)
	else:
		print("The tuner is not yet implemented")


def get_pitch(filename):
	global pitch

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

	for midi in pitches:
		note = midi2note(midi)
		#print(note)

	return pitches

if __name__ == "__main__":
	main()