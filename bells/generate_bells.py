"""
Bell Library Generator — pingerSLA
Generates .wav tones via waveform synthesis. No external dependencies.
"""
import wave, struct, math, os, random

RATE = 44100
DIR = os.path.dirname(os.path.abspath(__file__))


def write_wav(filename, samples, rate=RATE):
    path = os.path.join(DIR, filename)
    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        for s in samples:
            f.writeframes(struct.pack('<h', max(-32767, min(32767, int(s)))))
    print(f"  {filename} ({len(samples)/rate:.1f}s)")


def sine(freq, duration, volume=0.8):
    n = int(RATE * duration)
    return [volume * 32767 * math.sin(2 * math.pi * freq * i / RATE) for i in range(n)]


def square(freq, duration, volume=0.5):
    n = int(RATE * duration)
    period = RATE / freq
    return [volume * 32767 * (1 if (i % period) < period/2 else -1) for i in range(n)]


def noise(duration, volume=0.3):
    n = int(RATE * duration)
    return [volume * 32767 * (random.random() * 2 - 1) for _ in range(n)]


def fade(samples, fade_in=0.01, fade_out=0.05):
    n = len(samples)
    fi = int(RATE * fade_in)
    fo = int(RATE * fade_out)
    for i in range(min(fi, n)):
        samples[i] *= i / fi
    for i in range(min(fo, n)):
        samples[n - 1 - i] *= i / fo
    return samples


def silence(duration):
    return [0] * int(RATE * duration)


# --- Bell Generators ---

def gen_cyberpunk():
    """Glitchy digital chirps — short burst of random freq hops"""
    out = []
    freqs = [1800, 900, 2400, 600, 3000, 1200, 2100]
    for f in freqs:
        out += square(f, 0.04, 0.4)
        out += silence(0.02)
    return fade(out)


def gen_arcade_80s():
    """Classic 8-bit power-up sound"""
    out = []
    for i in range(12):
        freq = 400 + i * 150
        out += square(freq, 0.06, 0.45)
        out += silence(0.01)
    return fade(out)


def gen_radio_static():
    """White noise burst with embedded tone"""
    out = noise(0.15, 0.2)
    tone = sine(1000, 0.3, 0.6)
    out += tone
    out += noise(0.1, 0.15)
    return fade(out, 0.005, 0.1)


def gen_miyazaki():
    """Soft pentatonic chimes — gentle, warm"""
    pentatonic = [523, 587, 659, 784, 880]  # C5 pentatonic
    out = []
    pattern = [0, 2, 4, 3, 1, 4]
    for idx in pattern:
        freq = pentatonic[idx]
        tone = sine(freq, 0.25, 0.5)
        # Add soft harmonic
        harmonic = sine(freq * 2, 0.25, 0.15)
        combined = [a + b for a, b in zip(tone, harmonic)]
        out += fade(combined, 0.01, 0.15)
        out += silence(0.08)
    return out


def gen_midi_clean():
    """Clean sine melody — classic MIDI feel"""
    notes = [660, 880, 784, 660, 880, 1046]
    out = []
    for f in notes:
        out += fade(sine(f, 0.15, 0.6), 0.005, 0.08)
        out += silence(0.05)
    return out


def gen_alert():
    """Urgent staccato — attention needed"""
    out = []
    for _ in range(4):
        out += square(1200, 0.08, 0.5)
        out += silence(0.06)
    out += silence(0.1)
    for _ in range(4):
        out += square(1600, 0.06, 0.5)
        out += silence(0.04)
    return fade(out)


def gen_completion():
    """Ascending resolution chord — task done"""
    c4 = sine(523, 0.4, 0.4)
    e4 = sine(659, 0.4, 0.35)
    g4 = sine(784, 0.4, 0.3)
    c5 = sine(1046, 0.6, 0.5)

    chord1 = [a + b + c for a, b, c in zip(c4, e4, g4)]
    out = fade(chord1, 0.01, 0.2)
    out += silence(0.05)
    out += fade(sine(784, 0.15, 0.4))
    out += fade(c5 + sine(1046, 0.4, 0.3), 0.01, 0.3)
    return out


def gen_overrun():
    """Low warning drone — SLA missed"""
    out = []
    for _ in range(3):
        tone = sine(220, 0.3, 0.5)
        buzz = square(220, 0.3, 0.2)
        combined = [a + b for a, b in zip(tone, buzz)]
        out += fade(combined, 0.01, 0.15)
        out += silence(0.15)
    return out


def gen_milestone():
    """Quick double-tap ping — checkpoint reached"""
    tap1 = fade(sine(880, 0.1, 0.5), 0.005, 0.05)
    tap2 = fade(sine(1100, 0.12, 0.5), 0.005, 0.06)
    return tap1 + silence(0.08) + tap2


if __name__ == '__main__':
    print("generating bell library...")
    write_wav("cyberpunk.wav", gen_cyberpunk())
    write_wav("arcade_80s.wav", gen_arcade_80s())
    write_wav("radio_static.wav", gen_radio_static())
    write_wav("miyazaki.wav", gen_miyazaki())
    write_wav("midi_clean.wav", gen_midi_clean())
    write_wav("alert.wav", gen_alert())
    write_wav("completion.wav", gen_completion())
    write_wav("overrun.wav", gen_overrun())
    write_wav("milestone.wav", gen_milestone())
    print("done. 9 bells generated.")
