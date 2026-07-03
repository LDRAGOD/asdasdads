"""Akor, melodi, bass ve davul pattern ureticileri."""

import random

from .midi import PPQ, Note
from .theory import PROGRESSIONS, SCALES, root_midi, scale_note, triad

BAR = 4 * PPQ       # 4/4'te bir olcu
SIXTEENTH = PPQ // 4

# GM davul notalari (FL Studio'da FPC/kanal eslemesi icin standart)
KICK, SNARE, CLAP, CHAT, OHAT = 36, 38, 39, 42, 46

# 808 bass ritim kalibi: (baslangic_16lik, sure_16lik)
BASS_PATTERNS = [
    [(0, 6), (6, 2), (8, 8)],
    [(0, 8), (10, 2), (12, 4)],
    [(0, 4), (6, 2), (8, 4), (14, 2)],
    [(0, 16)],
]

# Melodi ritim kalibi: (baslangic_16lik, sure_16lik)
MELODY_RHYTHMS = [
    [(0, 2), (3, 1), (4, 2), (8, 4), (12, 4)],
    [(0, 4), (6, 2), (8, 2), (10, 2), (12, 4)],
    [(0, 3), (3, 3), (6, 2), (8, 8)],
    [(2, 2), (4, 2), (8, 2), (11, 1), (12, 4)],
    [(0, 8), (8, 4), (12, 4)],
]


def pick_progression(rng: random.Random, scale_name: str, bars: int) -> list[int]:
    """Olcu basina bir akor derecesi dondurur."""
    family = "minor" if "minor" in scale_name or scale_name in ("dorian", "phrygian") else "major"
    prog = rng.choice(PROGRESSIONS[family])
    return [prog[i % len(prog)] for i in range(bars)]


def gen_chords(rng: random.Random, key: str, scale_name: str, degrees: list[int]) -> list[Note]:
    scale = SCALES[scale_name]
    root = root_midi(key, 4)
    notes = []
    for bar, deg in enumerate(degrees):
        add7 = rng.random() < 0.35
        for i, pitch in enumerate(triad(root, scale, deg, add7=add7)):
            # hafif arpej hissi icin cok kucuk gecikmeler
            offset = i * rng.choice((0, 0, 15))
            notes.append(Note(bar * BAR + offset, BAR - offset - 20, pitch, 78))
    return notes


def gen_bass(rng: random.Random, key: str, scale_name: str, degrees: list[int]) -> list[Note]:
    scale = SCALES[scale_name]
    root = root_midi(key, 1)
    notes = []
    for bar, deg in enumerate(degrees):
        pattern = rng.choice(BASS_PATTERNS)
        pitch = scale_note(root, scale, deg)
        for j, (start, dur) in enumerate(pattern):
            p = pitch
            # ara vuruslarda bazen 5'liye ya da oktava kacamak
            if j > 0 and rng.random() < 0.3:
                p = pitch + rng.choice((7, 12))
            notes.append(Note(bar * BAR + start * SIXTEENTH, dur * SIXTEENTH - 10, p, 110))
    return notes


def gen_melody(rng: random.Random, key: str, scale_name: str, degrees: list[int]) -> list[Note]:
    scale = SCALES[scale_name]
    root = root_midi(key, 5)
    notes = []
    current = degrees[0] + 7  # bir oktav ustten basla
    for bar, deg in enumerate(degrees):
        chord_tones = {deg, deg + 2, deg + 4, deg + 7, deg + 9, deg + 11}
        rhythm = rng.choice(MELODY_RHYTHMS)
        for start, dur in rhythm:
            if start % 4 == 0 and rng.random() < 0.7:
                # guclu vuruslarda akor sesine yaklas
                current = min(chord_tones, key=lambda t: abs(t - current))
            else:
                current += rng.choice((-2, -1, -1, 1, 1, 2))
            current = max(deg + 4, min(deg + 12, current))
            pitch = scale_note(root - 12, scale, current)
            vel = rng.randint(85, 110)
            notes.append(Note(bar * BAR + start * SIXTEENTH, dur * SIXTEENTH - 15, pitch, vel))
    return notes


def gen_power_chords(rng: random.Random, key: str, scale_name: str, degrees: list[int]) -> list[Note]:
    """Elektro gitar icin power chord riff'i: kok + 5'li + oktav, 8'lik chug'lar."""
    scale = SCALES[scale_name]
    root = root_midi(key, 2)
    # 8'lik vuruslar: (baslangic_16lik, sure_16lik) - bosluklar riff hissi verir
    riffs = [
        [(0, 2), (2, 2), (4, 2), (6, 2), (8, 2), (10, 2), (12, 4)],
        [(0, 3), (3, 3), (6, 2), (8, 3), (11, 3), (14, 2)],
        [(0, 2), (2, 2), (4, 4), (8, 2), (10, 2), (12, 2), (14, 2)],
        [(0, 6), (6, 2), (8, 6), (14, 2)],
    ]
    notes = []
    for bar, deg in enumerate(degrees):
        pitch = scale_note(root, scale, deg)
        for start, dur in rng.choice(riffs):
            vel = rng.randint(100, 118)
            for interval in (0, 7, 12):  # kok, 5'li, oktav
                notes.append(Note(bar * BAR + start * SIXTEENTH,
                                  dur * SIXTEENTH - 20, pitch + interval, vel))
    return notes


def gen_rock_bass(rng: random.Random, key: str, scale_name: str, degrees: list[int]) -> list[Note]:
    """Rock bass: kok notayi 8'liklerle pompalar, ara sira oktav atlar."""
    scale = SCALES[scale_name]
    root = root_midi(key, 1)
    notes = []
    for bar, deg in enumerate(degrees):
        pitch = scale_note(root, scale, deg)
        for eighth in range(8):
            p = pitch + (12 if rng.random() < 0.12 else 0)
            notes.append(Note(bar * BAR + eighth * 2 * SIXTEENTH,
                              2 * SIXTEENTH - 15, p, rng.randint(98, 112)))
    return notes


def gen_rock_drums(rng: random.Random, bars: int) -> list[Note]:
    """Klasik rock ritmi: kick 1 ve 3'te, snare 2 ve 4'te, duz 8'lik hi-hat."""
    notes = []

    def hit(bar, sixteenth, pitch, vel, dur=SIXTEENTH // 2):
        notes.append(Note(bar * BAR + sixteenth * SIXTEENTH, dur, pitch, vel, channel=9))

    for bar in range(bars):
        hit(bar, 0, KICK, 118)
        hit(bar, 8, KICK, 112)
        if rng.random() < 0.5:  # senkoplu ekstra kick
            hit(bar, rng.choice((6, 7, 10)), KICK, 100)
        hit(bar, 4, SNARE, 116)
        hit(bar, 12, SNARE, 116)
        for eighth in range(8):
            hit(bar, eighth * 2, CHAT, 92 if eighth % 2 == 0 else 74)
        if bar % 4 == 3:  # 4 olcude bir mini dolgu
            hit(bar, 14, SNARE, 90)
            hit(bar, 15, SNARE, 104)
    return notes


def gen_drums(rng: random.Random, bars: int) -> list[Note]:
    """Trap tarzi davul: agir kick, 3. vurusta snare/clap, isleyen hi-hat."""
    notes = []

    def hit(bar, sixteenth, pitch, vel, dur=SIXTEENTH // 2):
        notes.append(Note(bar * BAR + int(sixteenth * SIXTEENTH), dur, pitch, vel, channel=9))

    for bar in range(bars):
        # Kick: olcu basi + senkoplu ekstralar
        hit(bar, 0, KICK, 118)
        for pos in rng.sample((5, 7, 10, 11, 14), k=rng.randint(1, 2)):
            hit(bar, pos, KICK, 105)

        # Snare + clap: half-time, 3. vurus (8. 16'lik)
        hit(bar, 8, SNARE, 115)
        hit(bar, 8, CLAP, 100)

        # Hi-hat: 8'likler, ara sira 16'lik/32'lik roll
        s = 0.0
        while s < 16:
            if rng.random() < 0.15:  # roll
                step = rng.choice((0.5, 0.25))
                end = min(s + 2, 16)
                while s < end:
                    hit(bar, s, CHAT, rng.randint(55, 80), dur=SIXTEENTH // 4)
                    s += step
            else:
                hit(bar, s, CHAT, rng.randint(70, 95))
                s += 2
        # Olcu sonunda bazen open hat
        if rng.random() < 0.4:
            hit(bar, 15, OHAT, 85, dur=SIXTEENTH)
    return notes
