from . import get_row, to_seq, to_track

import random

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

weights = [
        5,
        15,
        20,
        25,
        20,
        15,
]

# Generate

root = pr[0]
p0 = to_seq(pr, root)

treble_seq = []
bass_seq = []

treble_seq.extend(p0)
bass_seq.extend(p0)

for v in random.choices(variants, weights=weights, k=n_cycles):
    treble_seq.extend(get_row(p0, *v))
    bass_seq.extend(p0)

treble_seq.extend(p0)
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
