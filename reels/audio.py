"""Sintetiza a trilha (beat leve, 118 BPM) e os efeitos sonoros a partir de build/cues.json.

Tudo gerado do zero com numpy: sem samples de terceiros, sem problema de direitos.
Saídas: build/musica.wav e build/sfx.wav (44,1 kHz, estéreo).
"""
import json
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = 44100
rng = np.random.default_rng(7)


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.005, r=None):
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    if r:
        e *= np.exp(-np.arange(n) / (r * SR))
    return e


def lowpass(x, alpha):
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += alpha * (v - acc)
        y[i] = acc
    return y


def note(f):
    return 440 * 2 ** ((f - 69) / 12)


# ---------------- música ----------------
def music(dur):
    bpm = 118
    beat = 60 / bpm
    n = int(dur * SR)
    L = np.zeros(n)
    R = np.zeros(n)
    t = np.arange(n) / SR
    # progressão Am – F – C – G (um compasso cada)
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    bar = beat * 4
    # pad com leve detune e filtro "abrindo" ao longo do vídeo
    pad = np.zeros(n)
    for ci in range(int(dur / bar) + 1):
        s0, s1 = int(ci * bar * SR), min(n, int((ci + 1) * bar * SR))
        if s0 >= n:
            break
        tt = np.arange(s1 - s0) / SR
        seg = np.zeros(s1 - s0)
        for m in chords[ci % 4]:
            for det in (-0.08, 0.08):
                f = note(m + 12) * (1 + det / 100)
                seg += np.sign(np.sin(2 * np.pi * f * tt)) * 0.5 + np.sin(2 * np.pi * f * tt)
        fade = np.minimum(1, np.minimum(tt / 0.25, (bar - tt) / 0.25))
        pad[s0:s1] += seg * fade
    pad = lowpass(pad / 12, 0.05)
    # baixo sincopado
    bass = np.zeros(n)
    for k in range(int(dur / (beat / 2))):
        s0 = int(k * beat / 2 * SR)
        if k % 8 in (0, 3, 4, 6):
            ci = int(k * beat / 2 / bar) % 4
            f = note(chords[ci][0] - 12)
            d = int(beat * 0.45 * SR)
            tt = np.arange(min(d, n - s0)) / SR
            bass[s0:s0 + len(tt)] += np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.25) * 0.55
    # bateria
    drums = np.zeros(n)
    for k in range(int(dur / beat)):
        s0 = int(k * beat * SR)
        # kick
        d = int(0.32 * SR)
        tt = np.arange(min(d, n - s0)) / SR
        f = 50 + 90 * np.exp(-tt / 0.04)
        drums[s0:s0 + len(tt)] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.12) * 0.9
        # clap nos tempos 2 e 4
        if k % 2 == 1:
            d = int(0.18 * SR)
            nz = rng.standard_normal(min(d, n - s0))
            nz = nz - lowpass(nz, 0.15)
            drums[s0:s0 + len(nz)] += nz * np.exp(-np.arange(len(nz)) / (0.05 * SR)) * 0.35
        # hi-hat no contratempo
        sh = s0 + int(beat / 2 * SR)
        d = int(0.05 * SR)
        if sh + d < n:
            nz = rng.standard_normal(d)
            nz = nz - lowpass(nz, 0.5)
            drums[sh:sh + d] += nz * np.exp(-np.arange(d) / (0.012 * SR)) * 0.22
    # intro só com pad até o "reveal" ficaria vazio; mantemos tudo desde o início, com fade
    mix = pad * 0.55 + bass * 0.5 + drums * 0.55
    L = mix + pad * 0.12 * np.sin(2 * np.pi * 0.2 * t)
    R = mix - pad * 0.12 * np.sin(2 * np.pi * 0.2 * t)
    out = np.stack([L, R], 1)
    fade_in, fade_out = int(0.05 * SR), int(1.8 * SR)
    out[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    out[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None]
    return out / np.max(np.abs(out)) * 0.8


# ---------------- efeitos ----------------
def sfx_whoosh():
    d = 0.4
    nz = rng.standard_normal(int(d * SR))
    tt = t_axis(d)
    e = np.sin(np.pi * tt / d) ** 2
    y = lowpass(nz, 0.08) * 3 + (nz - lowpass(nz, 0.3)) * 0.15
    return y * e * 0.5


def sfx_stamp():
    d = 0.6
    tt = t_axis(d)
    f = 45 + 120 * np.exp(-tt / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.18)
    nz = rng.standard_normal(len(tt)) * np.exp(-tt / 0.04) * 0.5
    return (body + nz) * 0.9


def sfx_pop():
    d = 0.09
    tt = t_axis(d)
    f = 1100 - 500 * tt / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(tt), 0.002, 0.03) * 0.45


def sfx_tap():
    d = 0.05
    nz = rng.standard_normal(int(d * SR))
    return (nz - lowpass(nz, 0.4)) * env(len(nz), 0.001, 0.006) * 0.6


def sfx_tick():
    d = 0.08
    tt = t_axis(d)
    return np.sin(2 * np.pi * 1600 * tt) * env(len(tt), 0.001, 0.02) * 0.35


def sfx_ding():
    d = 1.0
    tt = t_axis(d)
    y = np.sin(2 * np.pi * 1318.5 * tt) * np.exp(-tt / 0.35)
    y2 = np.zeros_like(y)
    off = int(0.12 * SR)
    y2[off:] = np.sin(2 * np.pi * 1760 * tt[: len(tt) - off]) * np.exp(-tt[: len(tt) - off] / 0.45)
    return (y + y2) * 0.3


def sfx_alarm():
    d = 0.5
    tt = t_axis(d)
    gate = ((tt % 0.18) < 0.09).astype(float)
    return np.sign(np.sin(2 * np.pi * 880 * tt)) * gate * np.exp(-tt / 0.3) * 0.12


def sfx_riser():
    d = 0.9
    tt = t_axis(d)
    f = 300 + 1500 * (tt / d) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15
    nz = lowpass(rng.standard_normal(len(tt)), 0.25) * 0.6
    return (tone + nz) * (tt / d) ** 2 * 0.6


def sfx_swipe():
    d = 0.22
    nz = rng.standard_normal(int(d * SR))
    tt = t_axis(d)
    return (nz - lowpass(nz, 0.2)) * np.sin(np.pi * tt / d) * 0.25


SFX = {"whoosh": (sfx_whoosh, 0.2), "stamp": (sfx_stamp, 0.0), "pop": (sfx_pop, 0.0), "tap": (sfx_tap, 0.0),
       "tick": (sfx_tick, 0.0), "ding": (sfx_ding, 0.0), "alarm": (sfx_alarm, 0.0), "riser": (sfx_riser, 0.9),
       "swipe": (sfx_swipe, 0.1)}


def main():
    timing = json.load(open(os.path.join(BUILD, "timing.json")))
    cues = json.load(open(os.path.join(BUILD, "cues.json")))
    dur = timing["duration"]
    write_wav(os.path.join(BUILD, "musica.wav"), music(dur))
    n = int(dur * SR) + SR
    fx = np.zeros(n)
    cache = {}
    for c in cues:
        fn, pre = SFX[c["k"]]
        if c["k"] not in cache:
            cache[c["k"]] = fn()
        y = cache[c["k"]]
        s0 = int(max(0, c["t"] - pre) * SR)
        e = min(n, s0 + len(y))
        fx[s0:e] += y[: e - s0]
    write_wav(os.path.join(BUILD, "sfx.wav"), fx[: int(dur * SR)] * 0.9)
    print(f"música e {len(cues)} efeitos gerados ({dur:.1f}s)")


if __name__ == "__main__":
    main()
