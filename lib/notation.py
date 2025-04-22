# NAME		    ABRV.   TYPE	RANGE       RELATIVE TO...
# ----------------------------------------------------------------
# Chord Quality     cq	    str		-	    Root Note
# Chord Code 	    cc	    int array	any int	    Root Note
# Integer Note 	    in	    int		any int	    octave
# Note Letter 	    nl	    int		0-11	    octave
# MIDI Note 	    mn	    int		0-127	    [Absolute]
# MIDI Chord 	    mc	    int array	0-127	    [Absolute]

scales = {
    'Major': ['Major Scale', [0,2,4,5,7,9,11]],
    'Minor': ['Minor Scale', [0,2,3,5,7,8,10]],
    'Ionian': ['Ionian I', [0,2,4,5,7,9,11]],
    'Dorian': ['Dorian II', [0,2,3,5,7,9,10]],
    'Phrygian': ['Phrygian III', [0,1,3,5,7,8,10]],
    'Lydian': ['Lydian IV', [0,2,4,6,7,9,11]],
    'Mixolydian': ['Mixolydian V', [0,2,4,5,7,9,10]],
    'Aeolian': ['Aeolian VI', [0,2,3,5,7,8,10]],
    'Locrian': ['Locrian VII', [0,1,3,5,6,8,10]],
    'Harmonic Minor': ['Harmonic Minor', [0,2,3,5,7,8,11]],
    'Melonic Minor': ['Melonic Minor', [0,2,3,5,7,9,11]]
    }
 
scales_list = [scale[0] for scale in scales.items()]

chords = {
    "maj": ["Major", "", 0, [0,4,7]],
    "min": ["Minor", "", 1, [0,3,7]],
    "dom7": ["Dominant 7th", "7", 0, [0,4,7,10]],
    "maj7": ["Major 7th", "maj7", 0, [0,4,7,11]],
    "min7": ["Minor 7th", "7", 1, [0,3,7,10]],
    "dim": ["Diminished", "°", 1, [0,3,6]],
    "aug": ["Augmented", "+", 0, [0,4,8]],
    "sus2": ["Suspended Second", "sus2", 0, [0,2,7]],
    "sus4": ["Suspended Fourth", "sus4", 0, [0,5,7]],
    "unk": ["Unknown", "", 0, [0]],
    }

chords_list = [chord[0] for chord in chords.items()][:-1]

note_letters = [['C','c'], ['C#','c#'], ['D','d'], ['D#','d#'],
                ['E','e'], ['F','f'], ['F#','f#'], ['G','g'],
                ['G#','g#'], ['A','a'], ['A#','a#'], ['B','b']]

note_letters_list = [letter[0] for letter in note_letters]

roman_numerals = [['I','i'], ['II','ii'], ['III','iii'],
                  ['IV','iv'], ['V','v'], ['VI','vi'],
                  ['VII','vii'], ['VIII','viii'], ['IX','ix'],
                  ['X','x'], ['XI','xi'], ['XII','xii']]

midi_values = [note_letters[i%12][0] + str(int(i//12)) for i in range(128)]

# ---------- Functions ----------

# ---------- Note Conversion ----------

# Integer Note to Note Letter (INTEGER NOTE -> NOTE LETTER)
def in_to_nl (integer_note, root):
    return (integer_note + root)%12

# Integer Note to MIDI
def in_to_mn(note, key, octave):
    return note + key + (octave*12)

# Get Note Notation (MIDI NOTE -> STRING)
def get_note_notation(note):
    return note_letters[note%12][0] + str(note//12)

# Invert a note
def invert(note_a, note_b):
    while note_a > note_b + 12:
        note_a += -12
    while note_a < note_b:
        note_a += 12
    return note_a

# ---------- Chord Conversion ----------

# Get Chord Notation
def get_chord_notation(quality, root):
    return note_letters[root%12][chords[quality][2]] + chords[quality][1]

def get_roman_chord_notation(quality, root):
    return roman_numerals[root%12][chords[quality][2]]+chords[quality][1]

# Integer Chord to MIDI
def ic_to_mc(chord, key, octave):
    return [in_to_mn(note, key, octave) for note in chord]

# Get Quality of Chord
def get_quality(chord):
    offset = chord[0]
    chord = [note-offset for note in chord]
    for quality, chord_info in chords.items():
        if chord == chord_info[3]:
            return quality
    return "unk"

# Chord Code to MIDI Chord
def cc_to_mc(chord_code, note_letter, chord_properties, key, settings):

    shift = chord_properties["octave_shift"]
    relative_root = (note_letter - key["letter"])%12
    octave = settings["octave"][0] + shift
    bass = settings["octave"][1] + shift
    keynote = key["note"] + (shift * 12)
    rootnote = keynote + relative_root

    # Convert the chord code into a MIDI chord
    chord = [rootnote + note for note in chord_code]

    # Apply inversion to the chord
    if settings["invert"]:
        if shift == 1:
            pivot_note =  key["note"] + (relative_root + 1)
        elif shift == -1:
            pivot_note =  key["note"] + (relative_root - 12)
        else:
            pivot_note = key["note"]
        #print(f"Pivot: {pivot_note}")
        
        for i, note in enumerate(chord[:3]):
            chord[i] = invert(note, pivot_note)

    # Append bass note
    if settings["bass"]:
        bass_note = (key["note"]%12) + (bass*12) + relative_root
        chord.append(bass_note)

    # Ensure note ranges are valid
    for i, note in enumerate(chord):
        chord[i] = max(0, min(note, 127))

    return chord
