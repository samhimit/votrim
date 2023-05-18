import split
import csv
import os
import transcribe
from vosk import Model
from difflib import SequenceMatcher
import VOLine

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()



# prompt directory name of VO to trim
dir = input("Enter directory: ")
outputdir = input("Enter destination: ")
script = input("Enter script location: ")

# start by splitting all vo by silence
print("Splitting lines...")
split.CutAllLines(dir, outputdir)

# clear out the temp audio folder
dir = "processedAudio"
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))

model_path = "models/vosk-model-en-us-0.22"
model = Model(model_path)

# transcribe all lines
print("Transcribing lines...")
vo_lines = transcribe.TranscribeAllLines("cutAudio/"+outputdir,model)

if not os.path.exists("labeledAudio/"+outputdir):
        os.makedirs("labeledAudio/"+outputdir)

droppedLines = 0

# label all vo
print("Labeling lines...")
with open(script, newline='') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter='|')
    for row in csv_reader:
        count = 0
        for line in vo_lines:
            if similar(line.text, row[1]) > 0.5:
                cutFileName = "cutAudio/"+outputdir+"/"+os.path.basename(line.file)
                if os.path.isfile(cutFileName):
                    name = "labeledAudio/"+outputdir+"/"+row[0]
                    if count > 1:
                        name += "_" + str(count)
                        print("Multiple Files Founds For Line: " + row[0])
                    os.rename(cutFileName, name + ".wav")
                    line.file = name
                    count += 1
                else:
                    print("WARNING: FILE OVERRITE FOR: " + row[0])
                    droppedLines += 1
        if(count == 0):
            print("WARNING: NO FILE FOUND FOR: " + row[0])
            droppedLines += 1

print("Dropped Lines: " + str(droppedLines))

#print out contents of all cut files with their new file names
for line in vo_lines:
    print(line.file + ": " + line.text)
