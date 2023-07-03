import pyttsx3
import argparse

parser = argparse.ArgumentParser(description='Input Text and Audio')
parser.add_argument('--text', type=str, required=True)
parser.add_argument('--result', type=str, required=True)
args = parser.parse_args()

engine = pyttsx3.init()
voices = engine.getProperty('voices')       #getting details of current voice
#engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
engine.setProperty('voice', voices[1].id) 
engine.setProperty('rate', 140)
engine.save_to_file(args.text, "../src/static/audio/")
engine.runAndWait()