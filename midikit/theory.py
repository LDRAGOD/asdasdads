"""Muzik teorisi yardimcilari: notalar, gamlar, akorlar."""

NOTE_NAMES = {
    "C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3, "E": 4,
    "F": 5, "F#": 6, "GB": 6, "G": 7, "G#": 8, "AB": 8, "A": 9,
    "A#": 10, "BB": 10, "B": 11,
}

# Gamlar: kok notaya gore yarim ton araliklari
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "minor_pentatonic": [0, 3, 5, 7, 10],
    "major_pentatonic": [0, 2, 4, 7, 9],
}

# Populer akor yuruyusleri (gam derecesi olarak, 0 tabanli)
PROGRESSIONS = {
    "minor": [
        [0, 5, 2, 6],  # i - VI - III - VII (efsane trap/pop dizisi)
        [0, 3, 5, 4],  # i - iv - VI - v
        [0, 5, 3, 4],  # i - VI - iv - v
        [0, 6, 5, 4],  # i - VII - VI - v
    ],
    "major": [
        [0, 4, 5, 3],  # I - V - vi - IV
        [0, 3, 4, 4],  # I - IV - V - V
        [5, 3, 0, 4],  # vi - IV - I - V
        [0, 5, 3, 4],  # I - vi - IV - V
    ],
}


def root_midi(key: str, octave: int = 4) -> int:
    """Nota adini MIDI numarasina cevirir. Orn: A, oktav 4 -> 69."""
    pc = NOTE_NAMES[key.strip().upper()]
    return 12 * (octave + 1) + pc


def scale_note(root: int, scale: list[int], degree: int) -> int:
    """Gam derecesini MIDI notasina cevirir; negatif/tasan dereceler oktav kaydirir."""
    octave, idx = divmod(degree, len(scale))
    return root + 12 * octave + scale[idx]


def triad(root: int, scale: list[int], degree: int, add7: bool = False) -> list[int]:
    """Gamin verilen derecesi uzerine kurulu akor (1-3-5, istege bagli 7)."""
    steps = [0, 2, 4] + ([6] if add7 else [])
    return [scale_note(root, scale, degree + s) for s in steps]
