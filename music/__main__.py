from . import get_row, to_seq, to_track

import random

from itertools import repeat

import mingus.extra.lilypond as LilyPond
import mingus.midi.midi_file_out as MidiFileOut
import mingus.midi.fluidsynth as FluidSynth

from mingus.containers.note import Note
from mingus.containers.composition import Composition

random.seed("Billie")

n_cycles = 30
pr = ["D", "F", "G#", "D#", "F#", "A", "C", "G", "A#", "C#", "E", "B"]

#    N  Invert Retro
variants = [
    (0, False, False),
    (1, True,  False),
    (4, False, True),
    (6, False, False),
    (5, True,  True),
    (9, False, True),
]
v_weights = [
    5,
    15,
    20,
    25,
    20,
    15,
]

segments = [
    [(None, 1)],
    to_seq([("A#", 1/4), ("C",  1/4), ("D",  1/2)]),
    to_seq([("D#", 1/4), ("C#", 1/4), ("F",  1/2)]),
    to_seq([("G",  1/4), ("B",  3/8), ("B",  1/8), ("A",  1/4)]),
    to_seq([("E",  1/4), ("F#", 3/8), ("F#", 1/8), ("G#", 1/4)]),
    to_seq([("A#", 1/4), ("C",  1/4), ("C",  1/4), ("D",  1/4)]),
    to_seq([("G",  1/4), ("G",  1/4), ("B",  1/4), ("A",  1/4)]),
    to_seq([("E",  1/4), ("F#", 1/4), ("F#", 1/4), ("G#", 1/4)]),
    to_seq([("D#", 1/4), ("D#", 1/4), ("C#", 1/4), ("E",  1/4)]),
]
s_weights = [
    10,
    20,
    20,
    5,
    5,
    10,
    10,
    10,
    10,
]


# Generate

root = pr[0]
p0 = to_seq(zip(pr, repeat(1/4)), root)

treble_seq = []
bass_seq = []

for s in random.choices(segments, weights=s_weights, k=3):
    treble_seq.extend(s)
bass_seq.extend(p0)

for v in random.choices(variants, weights=v_weights, k=n_cycles):
    for s in random.choices(segments, weights=s_weights, k=3):
        treble_seq.extend(s)
    row = get_row(p0, *v)
    bass_seq.extend(row)

for s in random.choices(segments, weights=s_weights, k=3):
    treble_seq.extend(s)
bass_seq.extend(p0)

treble_track = to_track(treble_seq, Note(root, 4))
bass_track = to_track(bass_seq, Note(root, 2))

# Export

treble_ly = LilyPond.from_Track(treble_track)
bass_ly = LilyPond.from_Track(bass_track)

ly_track = f"""
\\book{{
\\paper {{
  #(set-paper-size "letter")
}}
\\header {{
  tagline = ##f
}}

\\score {{
  \\new PianoStaff <<
    \\new Staff <<
      \\repeat unfold {n_cycles+1} {{s1 \\noBreak s1 \\noBreak s1 \\break}}
      {treble_ly} >>

    \\new Staff <<
      \\repeat unfold {n_cycles+1} {{s1 \\noBreak s1 \\noBreak s1 \\break}}
      {{ \\clef bass {bass_ly} }} >>
  >>
  \\layout {{
    indent = 0\\mm
  }}
}}

}}
"""

LilyPond.to_pdf(ly_track, "comp.pdf")

comp = Composition()
comp.add_track(treble_track)
comp.add_track(bass_track)
MidiFileOut.write_Composition("comp.midi", comp)

FluidSynth.init("/usr/share/soundfonts/default.sf2", file="comp.wav")
FluidSynth.play_Composition(comp, channels=[0, 0])
FluidSynth.stop_everything()
