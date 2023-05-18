import wave
import json
from vosk import Model, KaldiRecognizer, SetLogLevel
import VOLine
from pydub import AudioSegment, effects
import os
 

def TranscribeAllLines(dir,model):
    retval = []
    for f in os.listdir(dir):
        if(f.endswith('.wav')):
            retval.append(TranscribeLine(dir + "/" + f,model))
    return retval


def TranscribeLine(filePath,model):
    audio_filename = filePath

    rawsound = AudioSegment.from_wav(audio_filename)
    singlechannelsound = rawsound.set_channels(1)
    singlechannelsound = singlechannelsound.set_sample_width(2)
    singlechannelsound = effects.compress_dynamic_range(singlechannelsound)
    normalizedsound = effects.normalize(singlechannelsound,.01)
    normalizedsound = normalizedsound.set_frame_rate(48000)
    shortenedsound = effects.normalize(normalizedsound)

    audio_filename = "processedAudio/" + os.path.basename(audio_filename)
    shortenedsound.export(audio_filename, format="wav")



    
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

    subtitle = ""

    for sentence in results:
        if len(sentence) == 1:
            continue
        for obj in sentence['result']:
            subtitle += obj["word"] + " "
            
    l = VOLine.VOLine(subtitle, audio_filename)

    wf.close()  # close audiofile
    return l