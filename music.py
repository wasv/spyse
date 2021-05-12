from mingus.containers.note import Note
from mingus.containers.track import Track
from mingus.containers.composition import Composition


def xpose(seq, offset):
    return [((n + offset) % 12, d) for n, d in seq]


def inverse(seq):
    return [((12 - n) % 12, d) for n, d in seq]


def retrograde(seq):
    return seq[::-1]


def get_row(p0, n, invert=False, retro=False):
    row = p0
    if invert:
        row = inverse(row)
    if retro:
        row = retrograde(row)
    return xpose(row, n)


def to_seq(row, root=None):
    if root is None:
        root = row[0][0]
    offset = int(Note(root))
    return [((int(Note(n)) - offset) % 12, d) for n, d in row]


def to_names(seq, root="C"):
    offset = int(Note(root))
    return [(Note(offset + n).name, d) for n, d in seq]


def to_track(seq, root=Note("C", 4), instrument=None):
    track = Track(instrument)
    offset = int(root)
    for n, d in seq:
        if n is not None:
            n = Note(offset + n)
        track.add_notes(n, 1/d)
    return track


if __name__ == "__main__":
    import random

    from itertools import repeat

    import mingus.extra.lilypond as LilyPond
    import mingus.midi.midi_file_out as MidiFileOut
    import mingus.midi.fluidsynth as FluidSynth

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
        20,
        20,
        20,
        10,
        10,
        5,
        5,
        5,
        5,
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
