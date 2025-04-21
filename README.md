# Chordamap

## What is Chordamap?
Chordamap is a Python tool that allows you to send MIDI chord data as simply as possible, that way you can easily input chords on a computer without the need for a MIDI keyboard. Chordamap also features the ability to save a sequence of chords to a MIDI file for later use or to import into other applications.

'Chordamap' is a portmanto of 'chord array map', a way to describe a MIDI controller that has buttons for chords arranged in an array. It can referer to any chord based MIDI controler, not just this one.

This is a tool I developed for my own use while composing music, I will work on it/update it in my spare time.

Anyone is welcome to modify, branch, rewrite or create new tools based on the code or off the same idea. I would greatly appreciate more tools like this be developed to make music composition faster and easier.

## How to use
Once open you can select a MIDI port to send MIDI note data too. Each button when held, will play the associated chord, sorted by chord quality. Chord inversion is automaticly applied to each chord based on the selected key. Holding shift or control while pressing a button will shift the octave up and down respectively, allowing a range of three octaves when inputting chord progressions.

Each time you press a chord button, the MIDI data is writen to the sequence. From the 'Seqence' menu you can save the sequence to a MIDI file or you can clear the sequence.

## Installation
You can download a compiled build of the program in the releases tab for ease of use.

If you wish to use the program from the source code you need to first install the two depencedies, [mido](https://github.com/mido/mido) and [python-rtmidi](https://github.com/SpotlightKid/python-rtmidi) via this command.
```
python3 -m pip install mido[ports-rtmidi]
```
⚠️ You must be using Python version 3.8 - 3.12, not the latest verion (3.13).

If you try to use the above command in Python 3.13 you will be prompted to compile python-rtmidi's C++ components.

## Getting MIDI into a DAW
To use Chordamap with a DAW you need a MIDI port that can route to your DAW. [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) is the simpilest solution.

Start loopMIDI before openining Chordamap. After Chordamap opens, you can select loopMIDI from the dropdown list of avaliable MIDI ports.

In your DAW, ensure you configue loopMIDI as a MIDI input.
