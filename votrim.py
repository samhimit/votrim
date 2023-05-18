
import wave
import json

from vosk import Model, KaldiRecognizer, SetLogLevel
import Word as custom_Word

from pydub import AudioSegment, effects
import os
 
dir = "processedAudio"
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))

audio_filename = input("Enter audio file path: ")
model_path = "models/vosk-model-en-us-0.22"

rawsound = AudioSegment.from_wav(audio_filename)
singlechannelsound = rawsound.set_channels(1)
singlechannelsound = singlechannelsound.set_sample_width(2)
singlechannelsound = effects.compress_dynamic_range(singlechannelsound)
normalizedsound = effects.normalize(singlechannelsound,.01)
normalizedsound = normalizedsound.set_frame_rate(48000)
shortenedsound = effects.normalize(normalizedsound)

audio_filename = "processedAudio/" + os.path.basename(audio_filename)
shortenedsound.export(audio_filename, format="wav")



model = Model(model_path)
wf = wave.open(audio_filename, "rb")

if wf.getnchannels() != 1:
    print("Audio file must be mono")
if wf.getsampwidth() != 2:
    print("Wrong sample width")
if wf.getcomptype() != "NONE":
    print("Wrong comptype")
rec = KaldiRecognizer(model, wf.getframerate())
rec.SetWords(True)
#rec.SetPartialWords(True)

# get the list of JSON dictionaries
results = []
# recognize speech using vosk model
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        part_result = json.loads(rec.Result())
        results.append(part_result)
part_result = json.loads(rec.FinalResult())
results.append(part_result)

# convert list of JSON dictionaries to list of 'Word' objects
list_of_Words = []
print("Sentences found: " + str(len(results)))
accuracyTotal = 0.0
accuracyCount = 0
for sentence in results:
    if len(sentence) == 1:
        # sometimes there are bugs in recognition 
        # and it returns an empty dictionary
        # {'text': ''}
        continue
    for obj in sentence['result']:
        w = custom_Word.Word(obj, audio_filename)  # create custom Word object
        list_of_Words.append(w)  # and add it to list
        accuracyCount += 1
        accuracyTotal += w.conf

wf.close()  # close audiofile

# output to the screen
for word in list_of_Words:
    print(word.to_string())


print("Words found: " + str(accuracyCount))
if(accuracyCount > 0):
    print("Average accuracy: " + str(accuracyTotal / accuracyCount))

