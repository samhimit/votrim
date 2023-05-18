from pydub import AudioSegment, effects
from pydub.silence import split_on_silence
import os

# Define a function to normalize a chunk to a target amplitude.
def match_target_amplitude(aChunk, target_dBFS):
    ''' Normalize given audio chunk '''
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)

def CutAllLines(dirName,destination):
    '''Trim all voices lines and place them unlabeled in cutAudio'''
    if not os.path.exists("cutAudio/"+destination):
        os.makedirs("cutAudio/"+destination)
    for f in os.listdir(dirName):
        if(f.endswith('.wav') or f.endswith('.WAV')):
            CutAudioFile(dirName + "/" + f,destination)


def CutAudioFile(pathName,destination):
    # Load your audio.
    track = AudioSegment.from_wav(pathName)

    #normalizedsound = effects.normalize(track,.01)

    # Split track where the silence is 2 seconds or more
    chunks = split_on_silence (
        track, 
        min_silence_len = 1750,
        silence_thresh = -52
    )
    # Process each chunk with your parameters
    for i, chunk in enumerate(chunks):
        # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
        silence_chunk = AudioSegment.silent(duration=500)

        # Add the padding chunk to beginning and end of the entire chunk.
        audio_chunk = silence_chunk + chunk + silence_chunk

        # Normalize the entire chunk.
        normalized_chunk = match_target_amplitude(audio_chunk, -20.0)

        # Export the audio chunk with new bitrate.
        print("Exporting line {0}".format(i))
        normalized_chunk.export(
            "cutAudio/"+destination + "/" + os.path.basename(pathName) + "_{0}.wav".format(i),
            format = "wav"
        )