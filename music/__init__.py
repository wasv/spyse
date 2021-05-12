from mingus.containers.note import Note
from mingus.containers.track import Track


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
