# 🎹 FL Studio MIDI Kit

FL Studio'ya **sürükle-bırak** kullanabileceğin MIDI loop'ları üreten araç.
Tek komutla akor, melodi, 808 bass ve trap davul pattern'i üretir — hepsi
aynı tonda ve birbiriyle uyumlu.

Hiçbir kütüphane kurmana gerek yok, sadece Python 3.9+ yeterli.

## Kullanım

```bash
python generate.py --key A --scale minor --bpm 140 --bars 8 --seed 7
```

`output/` klasörüne 4 dosya yazar:

| Dosya | İçerik | FL Studio'da nereye |
|---|---|---|
| `..._chords.mid` | Akor yürüyüşü | Pad / keys sound'u olan bir kanala |
| `..._melody.mid` | Ana melodi | Lead / pluck / bell kanalına |
| `..._bass.mid` | 808 bass hattı | 808 / sub bass kanalına |
| `..._drums.mid` | Trap davul pattern'i | FPC'ye ya da davul kanallarına |

### Parametreler

| Parametre | Varsayılan | Açıklama |
|---|---|---|
| `--key` | `A` | Ton: `C`, `C#`, `D`, ... `B` |
| `--scale` | `minor` | `minor`, `major`, `harmonic_minor`, `dorian`, `phrygian`, `minor_pentatonic`, `major_pentatonic` |
| `--bpm` | `140` | Tempo |
| `--bars` | `8` | Kaç ölçü |
| `--seed` | rastgele | Aynı seed = aynı müzik. Beğendiğin bir üretimin seed'ini not al! |
| `--out` | `output` | Çıktı klasörü |

### Örnekler

```bash
# Klasik trap: A minör, 140 BPM
python generate.py

# Karanlık drill havası
python generate.py --key F --scale phrygian --bpm 144

# Pop/melodik bir şey
python generate.py --key C --scale major --bpm 120

# Beğenene kadar farklı seed dene
python generate.py --seed 1
python generate.py --seed 2
```

## FL Studio'da nasıl kullanılır?

1. `generate.py`'yi çalıştır, `output/` klasörü oluşur.
2. `.mid` dosyasını FL Studio penceresine **sürükle**.
3. Açılan MIDI import ekranında "Create one channel per track" seç
   (tempo'yu da almak istersen tempo seçeneğini işaretle).
4. Kanala istediğin plugin'i ata: akorlar için FLEX'te bir pad,
   melodi için bir pluck, bass için 808, davul için FPC birebir oturur.
5. Piano roll'da notaları istediğin gibi düzenle — bu loop'lar başlangıç
   noktası, üstüne kendi dokunuşunu ekle!

> 💡 Davul dosyası General MIDI notaları kullanır: kick=C1(36), snare=D1(38),
> clap=D#1(39), closed hat=F#1(42), open hat=A#1(46). FPC'nin varsayılan
> eşlemesiyle uyumludur.

## Proje yapısı

```
generate.py            # CLI giriş noktası
midikit/
  midi.py              # Sıfır bağımlılıklı Standard MIDI File yazıcı
  theory.py            # Gamlar, akorlar, nota isimleri
  generators.py        # Akor / melodi / bass / davul üreticileri
```
