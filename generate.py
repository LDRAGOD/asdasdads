#!/usr/bin/env python3
"""FL Studio icin hazir MIDI loop'lari uretir.

Ornek:
    python generate.py --key A --scale minor --bpm 140 --bars 8 --seed 7

Cikti olarak output/ klasorune 4 dosya yazar:
    chords.mid  -> akorlar (pad/keys kanalina surukle)
    melody.mid  -> ana melodi (lead/pluck kanalina surukle)
    bass.mid    -> 808/bass hatti
    drums.mid   -> davul pattern'i (FPC'ye surukle)
"""

import argparse
import os
import random

from midikit.generators import gen_bass, gen_chords, gen_drums, gen_melody, pick_progression
from midikit.midi import write_midi
from midikit.theory import NOTE_NAMES, SCALES

ROMAN = ["i", "ii", "iii", "iv", "v", "vi", "vii"]


def main() -> None:
    ap = argparse.ArgumentParser(description="FL Studio icin MIDI loop ureticisi")
    ap.add_argument("--key", default="A", choices=sorted(NOTE_NAMES), help="ton (orn: A, C, F#)")
    ap.add_argument("--scale", default="minor", choices=sorted(SCALES), help="gam")
    ap.add_argument("--bpm", type=float, default=140, help="tempo")
    ap.add_argument("--bars", type=int, default=8, help="olcu sayisi")
    ap.add_argument("--seed", type=int, default=None, help="ayni seed = ayni muzik")
    ap.add_argument("--out", default="output", help="cikti klasoru")
    args = ap.parse_args()

    seed = args.seed if args.seed is not None else random.randrange(1_000_000)
    rng = random.Random(seed)
    os.makedirs(args.out, exist_ok=True)

    degrees = pick_progression(rng, args.scale, args.bars)
    parts = {
        "chords": gen_chords(rng, args.key, args.scale, degrees),
        "melody": gen_melody(rng, args.key, args.scale, degrees),
        "bass": gen_bass(rng, args.key, args.scale, degrees),
        "drums": gen_drums(rng, args.bars),
    }

    prefix = f"{args.key}{args.scale}_{int(args.bpm)}bpm_seed{seed}"
    for name, notes in parts.items():
        path = os.path.join(args.out, f"{prefix}_{name}.mid")
        write_midi(path, args.bpm, {name: notes})
        print(f"  yazildi: {path} ({len(notes)} nota)")

    minor_family = "minor" in args.scale or args.scale in ("dorian", "phrygian")
    prog_str = " - ".join(
        ROMAN[d % 7] if minor_family else ROMAN[d % 7].upper() for d in degrees[:4]
    )
    print(f"\nTon: {args.key} {args.scale} | Tempo: {args.bpm:g} BPM | "
          f"Akor yuruyusu: {prog_str} | Seed: {seed}")
    print("Dosyalari FL Studio'ya suruklemen yeterli. Begenmediysen --seed degistir!")


if __name__ == "__main__":
    main()
