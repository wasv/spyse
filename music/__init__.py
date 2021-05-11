from mingus.containers.note import Note
from mingus.containers.track import Track


def xpose(seq, offset):
    return [(n + offset) % 12 for n in seq]


def inverse(seq):
    return [(12 - n) % 12 for n in seq]


def retrograde(seq):
    return seq[::-1]


def get_row(p0, n, invert=False, retro=False):
    row = p0
    if invert:
        row = inverse(row)
    if retro:
        row = retrograde(row)
    print(n)
    return xpose(row, n)


def chords(row, n=4):
    return tuple(row[i*n:(i+1)*n] for i in range(0, len(row)//n))


def to_seq(row, root=None):
    if root is None:
        root = row[0]
    offset = int(Note(root))
    return [(int(Note(n)) - offset) % 12 for n in row]


def to_names(seq, root="C"):
    offset = int(Note(root))
    return [Note(offset + n).name for n in seq]


def to_track(seq, root=Note("C", 4), instrument=None):
    track = Track(instrument)
    offset = int(root)
    [track.add_notes(Note(offset + n)) for n in seq]
    return track
