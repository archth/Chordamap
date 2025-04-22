import os
import sys
import mido

def make_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)

def set_dir(filename, path):
    make_folder(path)
    return f"{path}/{filename}"

def write_to_file(sequence, key, scale, savetype):
    if sequence != []:
        miditime = 0
        midifile = mido.MidiFile()
        track = mido.MidiTrack()
        midifile.tracks.append(track)
        chord_names = [chord[0] for chord in sequence]
        
        for i, chord in enumerate(sequence):
            for note in chord[1]:
                track.append(mido.Message('note_on', note=note, velocity=100, time=0))
            miditime = 1920
            for note in chord[1]:
                track.append(mido.Message('note_off', note=note, velocity=127, time=miditime))
                miditime = 0

        # Generate filename
        if len(chord_names) > 12:
            filename = " ".join(chord_names[:12]) + " (+)"
        else:
            filename = " ".join(chord_names)

        # Select folder for saving
        if savetype == "scale":
            filename = set_dir(filename, f"output/{scale}")
        elif savetype == "key":
            filename = set_dir(filename, f"output/{key}")
        elif savetype == "scalekey":
            filename = set_dir(filename, f"output/{scale}/{key}")
        elif savetype == "keyscale":
            filename = set_dir(filename, f"output/{key}/{scale}")
        else:
            filename = set_dir(filename, "output")

        # Ensure filenames are uniqie
        base_name = filename
        number = 0
        if os.path.exists(f"{filename}.mid"):
            number += 1
            filename = f"{base_name} {number}"
            while os.path.exists(f"{filename}.mid"):
                number += 1
                filename = f"{base_name} {number}"

        #Save the file 
        midifile.save(f"{filename}.mid")
        print("Sequence Saved")

    # If sequence is empty
    else:
        print("Error: Sequence is empty. Nothing saved.")
