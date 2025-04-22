import os
import mido
import threading
import configparser
import tkinter as tk
from tkinter import ttk
from operator import setitem
from lib import export
from lib import notation
from tkinter import simpledialog
from lib.notation import scales, scales_list, chords, chords_list, note_letters, note_letters_list, roman_numerals, midi_values

# ================= Initialize Program Configurations =================

config = configparser.ConfigParser()
if os.path.exists("config.ini"):
    config.read('config.ini')
else:
    config['DEFAULT'] = {
        "ThemeEnabled": "yes",
        "DefaultPort": "loopMidi",
        "SaveType": "none"}

with open('config.ini', 'w') as configfile:
  config.write(configfile)   
        
if config["DEFAULT"]["ThemeEnabled"] == "yes":
    theme_enabled = True
else:
    theme_enabled = False

# ================== Variables ==================

# ['C',[0,4,7]]
sequence = []

playing_notes = []

key = {
    "scale": "Major",
    "letter": 0,
    "note": 48
}

settings = {
    "octave": [4,3],
    "bass": True,
    "invert": True
}

row = 0
port = ""
available_ports = mido.get_output_names()

lock = threading.Lock()

# ================== Functions ==================

# ---------- Setter Functions ----------

# Set Key 
def set_key(event):
    global key, row

    key["letter"] = note_letters_list.index(keylist.get())
    key["note"] = key["letter"] + (settings["octave"][0]*12)

    for widget in diachord_frame.winfo_children():
        widget.destroy()
    row = 1
    generate_diatonic_chords()

# Set Scale
def set_scale(event):
    global key, row

    key["scale"] = scalelist.get()

    for widget in diachord_frame.winfo_children():
        widget.destroy()
    row = 1
    generate_diatonic_chords()

# Set Octave
def set_octave(event):
    global key, settings
    settings["octave"][0] = int(octavelist.get())
    key["note"] = key["letter"] + (settings["octave"][0]*12)

# Set Bass Octave
def set_bass(event):
    global settings
    settings["octave"][1] = int(boctavelist.get())

# Set Default Port
def set_default_port():
    global config
    config["DEFAULT"]["DefaultPort"] = portlist.get()
    with open('config.ini', 'w') as configfile:
      config.write(configfile) 


# ---------- MIDI Port Functions ----------

# Set Port From Button
def port_select(event):
    x = portlist.get()
    set_port(x)

# Set Port
def set_port(x):
    global port

    if port != "":
        port.close()
    port = mido.open_output(x)
    print(f"Port set to {x}")

def port_initialize():
    global available_ports
    
    # Get list of all avaliable ports
    available_ports = mido.get_output_names()

    # No Ports Found
    if available_ports == []:
        tk.messagebox.showerror("Error", "No MIDI output ports found")

    # Check if default port is avaliable
    if config["DEFAULT"]["DefaultPort"] in available_ports:
        set_port(config["DEFAULT"]["DefaultPort"])
    else:
        set_port(available_ports[0])
        

# ---------- MIDI Playback ----------

# Debug
def print_note(note):
    print(f"{midi_values[note]} - {note}")


# Play MIDI Note
def play_note(note):
    global playing_notes
    playing_notes.append(note)
    with lock:
        port.send(mido.Message('note_on', note=note, velocity=100, channel=0))


# Stop MIDI Note
def stop_note(note):
    with lock:
        port.send(mido.Message('note_off', note=note, velocity=0, channel=0))


# On Chord Button Press
def play_chord(event, quality, note_letter, name, mouse):
    global key, settings, sequence

    # If shift or ctrl is being pressed
    if event.state & 0x0001:
        chord_properties = {"octave_shift": 1}
    elif event.state & 0x0004:
        chord_properties = {"octave_shift": -1}
    else:
        chord_properties = {"octave_shift": 0}

    # Genertate the full MIDI chord 
    chord = notation.cc_to_mc(chords[quality][3], note_letter, chord_properties, key, settings)
    # Play the chord
    for note in chord:
	    play_note(note)

    # Only print to console and add to sequence if left clicked
    if mouse == "left":
        # Print played chord and note to console
        notes = " ".join([notation.get_note_notation(note) for note in chord])
        print(name + " - " + notes)
        # Add chord to sequence
        sequence.append([name, chord])


# On Chord Button Release
def stop_chord(quality, note_letter):
    global playing_notes

    for note in playing_notes:
	    stop_note(note)

# MIDI Panic
def midi_panic():
    for note in range(128):
        port.send(mido.Message('note_off', note=note, velocity=0, channel=0))


# ---------- Generate Chord Buttons ----------

# Generate Chord Button
def generate_button(chord, root, bass, text, name, frame, row, col, width):
    chordbutton = tk.Button(frame, text=text, width=width)
    chordbutton.grid(row=row, column=col)
    chordbutton.bind("<ButtonPress-1>", lambda e: play_chord(e, chord, root, name, "left"))
    chordbutton.bind("<ButtonPress-3>", lambda e: play_chord(e, chord, root, name, "right"))
    chordbutton.bind("<ButtonRelease-1>", lambda e: stop_chord(chord, root))
    chordbutton.bind("<ButtonRelease-3>", lambda e: stop_chord(chord, root))
    apply_theme(chordbutton)

# Generate Chord Buttons
def generate_chords(quality):
    global row
    chordlabel = tk.Label(chord_frame, text=chords[quality][0] + " Chords")
    chordlabel.grid(row = row, column = 0, columnspan = 6)
    apply_theme(chordlabel)
    row += 1
    colshift = 0
    for j in range(12):
        name = notation.get_chord_notation(quality, j)
        generate_button(quality, j, 0, name, name, chord_frame, row, j + colshift, 5)
        # Format Grid
        if j == 5:
            row += 1
            colshift = -6
    row += 1

# Generate Diatonic Chord Buttons
def generate_diatonic_chords():
    global key, scales, row
    
    chordlabel = tk.Label(diachord_frame, text="Diatonic Chords")
    chordlabel.grid(row = row, column = 0, columnspan = 7)
    apply_theme(chordlabel)
    row += 1

    # Create a copy of scale with extended range
    scale_code = scales[key["scale"]][1]
    scale = [note for note in scale_code]
    scale = scale + [note+12 for note in scale_code]
    
    for i in range(7):
        chord = [scale[i], scale[i+2], scale[i+4]]
        quality = notation.get_quality(chord)
        root = notation.in_to_nl(scale[i],key["letter"])
        number = notation.get_roman_chord_notation(quality, i)
        name = notation.get_chord_notation(quality, root)
        generate_button(quality, root, 0, number, name, diachord_frame, row, i, 4)


# ---------- MIDI Sequence Handeling ----------

# Clear Sequence
def clear_sequence():
    global sequence
    print("Sequence Cleared")
    sequence = []

# Save Sequence
def save_sequence():
    key_letter = note_letters[key["letter"]][0]
    scale_name = scales[key["scale"]][1]
    export.write_to_file(sequence, key_letter, key["scale"], config["DEFAULT"]["SaveType"])

# Trim Sequence
def trim(trim, side):
    global sequence

    if trim is None or trim == "0":
        return
    
    if trim.isdigit() == False:
        tk.messagebox.showerror("Error", "Not a number")
        return
    else:
        trim = max(1, min(int(trim), len(sequence)-1))
        if side == "start":
            sequence = sequence[trim:]
        else:
            sequence = sequence[:trim*-1]
        print("Sequence Trimed")

    for chord in sequence:
        notes = " ".join([notation.get_note_notation(note) for note in chord[1]])
        print(chord[0] + " - " + notes)

# Trim Sequence Start
def trim_start():
    global sequence

    if len(sequence) > 1:
        amount = simpledialog.askstring("Trim Start",
            "How many chords?", parent=root)
        trim(amount,"start")

# Trim Sequence End
def trim_end():
    global sequence

    if len(sequence) > 1:
        amount = simpledialog.askstring("Trim End",
            "How many chords?", parent=root)
        trim(amount,"end")


# ---------- Theme Settings----------

def apply_theme(element):
    rbg_c = "#1d2135" # Root Background Color
    bg_c =  "#415666" # Background Color
    fg_c =  "#e6e7eb" # Foreground Color
    
    if theme_enabled:
        _type = element.winfo_class()
        #print(_type)
        if _type == "Button":
            element.config(bg=bg_c , fg=fg_c,
                activebackground=bg_c ,
                activeforeground=fg_c )
        elif _type == "Checkbutton":
            element.config(bg=rbg_c, activebackground=rbg_c)
        elif _type == "Label":
            element.config(bg=rbg_c, fg=fg_c)
        elif _type == "Frame":
            element.config(bg=rbg_c)
        elif _type == "Tk":
            element.config(bg=rbg_c)
    pass

# ================== Program Start ==================

# Set the MIDI Output Port
port_initialize()

# ================== GUI Start ==================

# Create Root Widget
root = tk.Tk()
root.title("Chordamap v0.20")
apply_theme(root)

# ========= Menu Frame ==========
menu_frame = tk.Frame(root)
menu_frame.pack()
apply_theme(menu_frame)

# --------- Menu Bar ----------
menubar = tk.Menu(root)
# Sequence Menu
sequencemenu = tk.Menu(menubar, tearoff=0)
sequencemenu.add_command(label="Save Sequence",command=(save_sequence))
sequencemenu.add_command(label="Clear Sequence",command=(clear_sequence))
sequencemenu.add_command(label="Trim Start",command=(trim_start))
sequencemenu.add_command(label="Trim End",command=(trim_end))
menubar.add_cascade(label="Sequence", menu=sequencemenu)
# MIDI Menu
midimenu = tk.Menu(menubar, tearoff=0)
midimenu.add_command(label="Set as Default Port",command=(set_default_port))
midimenu.add_command(label="MIDI Panic",command=(midi_panic))
midimenu.add_command(label="Refresh MIDI Ports",command=(port_initialize))
menubar.add_cascade(label="MIDI", menu=midimenu)

root.config(menu=menubar)

# ========= Port Frame =========
port_frame = tk.Frame(root)
port_frame.pack(side="top", fill="x")
apply_theme(port_frame)
# Port Label
portlabel = tk.Label(port_frame, text="MIDI Port")
portlabel.pack(side="left")
apply_theme(portlabel)
# Select Port
portlist = ttk.Combobox(port_frame, values=available_ports, width=30)
portlist.pack(side="right")
portlist.set(available_ports[0])
portlist.bind("<<ComboboxSelected>>", port_select)
apply_theme(portlist)

# ========= Key Frame =========
key_frame = tk.Frame(root)
key_frame.pack(side="top", fill="x")
apply_theme(key_frame)
# Key Label
keylabel = tk.Label(key_frame, text="Key/Scale")
keylabel.pack(side="left")
apply_theme(keylabel)
# Select Scale
scalelist = ttk.Combobox(key_frame, values=scales_list)
scalelist.pack(side="right")
scalelist.set(scales_list[0])
scalelist.bind("<<ComboboxSelected>>", set_scale)
apply_theme(scalelist)
# Select Key
keylist = ttk.Combobox(key_frame, values=note_letters_list, width=3)
keylist.pack(side="right")
keylist.set(note_letters_list[0])
keylist.bind("<<ComboboxSelected>>", set_key)
apply_theme(keylist)

# ========= Octave Frame =========
octave_frame = tk.Frame(root)
octave_frame.pack(side="top", fill="x")
apply_theme(octave_frame)
# Octave Label
octavelabel = tk.Label(octave_frame, text="Octave")
octavelabel.pack(side="left")
apply_theme(octavelabel)
# Bass Octave Checkbox
bass_var = tk.BooleanVar()
basscheck = tk.Checkbutton(octave_frame, variable=bass_var, onvalue=True, offvalue=False,
    command=lambda:(setitem(settings,"bass",bass_var.get())))
bass_var.set(True)
basscheck.pack(side="right")
apply_theme(basscheck)
# Select Bass Octave
octave_range = [0,1,2,3,4,5,6,7,8,9,10]
boctavelist = ttk.Combobox(octave_frame, values=octave_range, width=3)
boctavelist.pack(side="right")
boctavelist.set(3)
boctavelist.bind("<<ComboboxSelected>>", set_bass)
apply_theme(boctavelist)
# Select Bass Octave Label
boctlabel = tk.Label(octave_frame, text="Bass Note: ")
boctlabel.pack(side="right")
apply_theme(boctlabel)
# Select Octave
octavelist = ttk.Combobox(octave_frame, values=octave_range, width=3)
octavelist.pack(side="right")
octavelist.set(4)
octavelist.bind("<<ComboboxSelected>>", set_octave)
apply_theme(octavelist)
# Select Octave Label
octlabel = tk.Label(octave_frame, text="Root Note: ")
octlabel.pack(side="right")
apply_theme(octlabel)

# ========= Diatonic Chords Frame =========
diachord_frame = tk.Frame(root)
diachord_frame.pack()
apply_theme(diachord_frame)
generate_diatonic_chords()

# ========= Chords Frame =========
chord_frame = tk.Frame(root)
chord_frame.pack()
apply_theme(chord_frame)
for chord in chords_list:
    generate_chords(chord)

# ================== GUI End ==================

# Create Main Loop
root.mainloop()



