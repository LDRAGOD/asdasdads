"""Sifir bagimlilikla Standard MIDI File (SMF format 1) yazici.

FL Studio dahil tum DAW'larin okuyabildigi .mid dosyalari uretir.
"""

from dataclasses import dataclass

PPQ = 480  # ticks per quarter note (dortluk basina tick)


@dataclass
class Note:
    start: int      # tick
    duration: int   # tick
    pitch: int      # 0-127 MIDI nota numarasi
    velocity: int = 100
    channel: int = 0


def _vlq(value: int) -> bytes:
    """MIDI variable-length quantity kodlamasi."""
    buf = [value & 0x7F]
    value >>= 7
    while value:
        buf.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(buf))


def _chunk(tag: bytes, payload: bytes) -> bytes:
    return tag + len(payload).to_bytes(4, "big") + payload


def _tempo_track(bpm: float) -> bytes:
    us_per_quarter = round(60_000_000 / bpm)
    data = b"\x00\xff\x51\x03" + us_per_quarter.to_bytes(3, "big")
    # 4/4 time signature
    data += b"\x00\xff\x58\x04\x04\x02\x18\x08"
    data += b"\x00\xff\x2f\x00"  # end of track
    return _chunk(b"MTrk", data)


def _note_track(name: str, notes: list[Note]) -> bytes:
    events = []  # (tick, order, message_bytes)
    for n in notes:
        ch = n.channel & 0x0F
        # note-off'lar ayni tick'teki note-on'lardan once gelsin ki
        # ust uste binen ayni nota yanlis kesilmesin
        events.append((n.start, 1, bytes((0x90 | ch, n.pitch, n.velocity))))
        events.append((n.start + n.duration, 0, bytes((0x80 | ch, n.pitch, 0))))
    events.sort(key=lambda e: (e[0], e[1]))

    data = b"\x00\xff\x03" + _vlq(len(name.encode())) + name.encode()
    tick = 0
    for ev_tick, _, msg in events:
        data += _vlq(ev_tick - tick) + msg
        tick = ev_tick
    data += b"\x00\xff\x2f\x00"
    return _chunk(b"MTrk", data)


def write_midi(path: str, bpm: float, tracks: dict[str, list[Note]]) -> None:
    """tracks: {track_adi: [Note, ...]} sozlugunu .mid dosyasina yazar."""
    ntracks = 1 + len(tracks)
    header = _chunk(
        b"MThd",
        (1).to_bytes(2, "big") + ntracks.to_bytes(2, "big") + PPQ.to_bytes(2, "big"),
    )
    body = _tempo_track(bpm)
    for name, notes in tracks.items():
        body += _note_track(name, notes)
    with open(path, "wb") as f:
        f.write(header + body)
