#!/usr/bin/env python3
"""Música y sound design sintetizados para los reels TallerLab.

Lee <out>/<id>.json (duración, bpm, eventos de la timeline) y escribe <out>/<id>.wav (48 kHz, estéreo).
Todo se genera con numpy/scipy: no hay samples externos, así el resultado es reproducible y libre de derechos.

Capas:
  · Música: kick, sub 808, clap, hats, pad detuned, pluck/arpegio y percusión metálica, con sidechain al kick.
    El beat entra en el "drop" (el primer impacto del hook) y se corta en el "outro" (tarjeta final).
  · SFX disparados por eventos: riser, impactos, whooshes, palabras del titular, ticks, pops, contador,
    arranque de motor (spinup), chispas (grind), tildes/buzz, tachado, tarjetas y campana del logo.
"""
import json
import math
import sys
import wave
from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(20261006)


# ───────────────────────────── utilidades ─────────────────────────────
def sec(n):
    return int(round(n * SR))


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def t_axis(n):
    return np.arange(n) / SR


def adsr(n, a=0.005, d=0.1, s=0.0, r=0.1, curve=4.0):
    """Envolvente ADSR exponencial; devuelve n muestras."""
    a_n, d_n, r_n = sec(a), sec(d), sec(r)
    s_n = max(0, n - a_n - d_n - r_n)
    out = np.zeros(n)
    i = 0
    if a_n:
        out[i:i + a_n] = np.linspace(0, 1, a_n) ** (1 / 2)
        i += a_n
    if d_n:
        out[i:i + d_n] = s + (1 - s) * np.exp(-np.linspace(0, curve, d_n))
        i += d_n
    if s_n:
        out[i:i + s_n] = s
        i += s_n
    if r_n and i < n:
        k = min(r_n, n - i)
        out[i:i + k] = out[i - 1] * np.exp(-np.linspace(0, curve, k))
    return out[:n]


def exp_decay(n, tau):
    return np.exp(-t_axis(n) / tau)


def butter(x, kind, fc, order=2):
    fc = np.clip(np.atleast_1d(fc), 20, SR / 2 - 100)
    fc = fc.tolist() if len(fc) > 1 else float(fc[0])
    sos = signal.butter(order, fc, btype=kind, fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def sweep_filter(x, kind, fc_from, fc_to, order=2, block=256, curve=1.0):
    """Filtro con corte que barre de fc_from a fc_to a lo largo de la señal (por bloques, con estado)."""
    n = len(x)
    out = np.empty_like(x)
    zi = None
    nb = math.ceil(n / block)
    for b in range(nb):
        p = (b / max(1, nb - 1)) ** curve
        fc = fc_from * (fc_to / fc_from) ** p
        if kind == 'band':
            lo, hi = fc / 1.6, fc * 1.6
            sos = signal.butter(order, [max(20, lo), min(SR / 2 - 100, hi)], btype='band', fs=SR, output='sos')
        else:
            sos = signal.butter(order, np.clip(fc, 20, SR / 2 - 100), btype=kind, fs=SR, output='sos')
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        seg = x[b * block:(b + 1) * block]
        y, zi = signal.sosfilt(sos, seg, zi=zi)
        out[b * block:(b + 1) * block] = y
    return out


def noise(n):
    return rng.standard_normal(n)


def saw(freq, n, phase=0.0):
    """Diente de sierra por suma de armónicos (antialias suficiente para esta banda)."""
    t = t_axis(n)
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,)) if np.ndim(freq) else np.full(n, float(freq))
    ph = 2 * np.pi * np.cumsum(f) / SR + phase
    out = np.zeros(n)
    fmax = float(np.max(f))
    kmax = int(min(40, (SR / 2.2) // max(fmax, 1)))
    for k in range(1, kmax + 1):
        out += ((-1) ** (k + 1)) * np.sin(k * ph) / k
    return out * (2 / np.pi)


def sine(freq, n, phase=0.0):
    f = np.asarray(freq, dtype=float)
    if f.ndim:
        return np.sin(2 * np.pi * np.cumsum(f) / SR + phase)
    return np.sin(2 * np.pi * f * t_axis(n) + phase)


def soft_clip(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


class Bus:
    def __init__(self, dur):
        self.n = sec(dur) + sec(1.5)
        self.L = np.zeros(self.n)
        self.R = np.zeros(self.n)

    def add(self, t, x, gain=1.0, pan=0.0):
        """pan ∈ [-1, 1]."""
        i = sec(max(0.0, t))
        if i >= self.n:
            return
        x = np.asarray(x) * gain
        k = min(len(x), self.n - i)
        gl = math.cos((pan + 1) * math.pi / 4)
        gr = math.sin((pan + 1) * math.pi / 4)
        self.L[i:i + k] += x[:k] * gl
        self.R[i:i + k] += x[:k] * gr

    def add_stereo(self, t, l, r, gain=1.0):
        i = sec(max(0.0, t))
        k = min(len(l), self.n - i)
        self.L[i:i + k] += l[:k] * gain
        self.R[i:i + k] += r[:k] * gain


# ───────────────────────────── instrumentos ─────────────────────────────
def kick(vel=1.0, style='dark'):
    n = sec(0.55)
    t = t_axis(n)
    f0, f1 = (170, 54) if style != 'cinematic' else (130, 46)
    f = f1 + (f0 - f1) * np.exp(-t / 0.045)
    body = sine(f, n) * np.exp(-t / 0.22)
    click = butter(noise(sec(0.012)), 'high', 2500) * np.exp(-t_axis(sec(0.012)) / 0.003)
    out = body * 1.0
    out[:len(click)] += click * 0.5
    return soft_clip(out * 1.15 * vel, 1.3)


def sub808(freq, dur, vel=1.0):
    n = sec(dur)
    t = t_axis(n)
    f = freq * (1 + 0.6 * np.exp(-t / 0.03))
    x = (sine(f, n) + 0.55 * sine(f / 2, n)) * np.exp(-t / (dur * 0.6))
    return soft_clip(x * 1.5, 1.6) * 0.55 * vel


def clap(vel=1.0):
    n = sec(0.32)
    out = np.zeros(n)
    for k, d in enumerate([0, 0.011, 0.023]):
        b = butter(noise(n), 'band', [1200, 5200], 2) * exp_decay(n, 0.018 if k < 2 else 0.11)
        out[sec(d):] += b[:n - sec(d)] * (0.6 if k < 2 else 1.0)
    return out * 0.95 * vel


def hat(open_=False, vel=1.0):
    n = sec(0.35 if open_ else 0.07)
    x = butter(noise(n), 'high', 7000, 3) * exp_decay(n, 0.09 if open_ else 0.016)
    # toque metálico
    x += sine(9150, n) * exp_decay(n, 0.01) * 0.1
    return x * 0.7 * vel


def metal_ping(freq, vel=1.0):
    """Percusión inarmónica tipo golpe en chapa."""
    n = sec(0.7)
    out = np.zeros(n)
    for r, g, tau in [(1.0, 1.0, 0.25), (1.73, 0.6, 0.18), (2.41, 0.4, 0.14), (3.72, 0.25, 0.1)]:
        out += sine(freq * r, n) * g * exp_decay(n, tau)
    return out * 0.32 * vel


def pluck(freq, dur=0.5, vel=1.0):
    n = sec(dur)
    t = t_axis(n)
    out = sine(freq, n) + 0.45 * sine(freq * 2, n) + 0.2 * sine(freq * 3, n) + 0.08 * sine(freq * 5.01, n)
    out *= np.exp(-t / 0.13) * (1 - np.exp(-t / 0.002))
    out = butter(out, 'low', 3500 + 2500 * vel)
    return out * 0.62 * vel


def pad_chord(freqs, dur, cutoff=1300, detune=0.006):
    n = sec(dur)
    L = np.zeros(n)
    R = np.zeros(n)
    for i, f in enumerate(freqs):
        for d, side in [(-detune, 'L'), (detune * 0.5, 'L'), (detune, 'R'), (-detune * 0.5, 'R')]:
            v = saw(f * (1 + d), n, phase=rng.uniform(0, 6.28)) * 0.25
            if side == 'L':
                L += v
            else:
                R += v
    env = adsr(n, a=0.35, d=0.4, s=0.75, r=0.6)
    L = butter(sweep_filter(L, 'low', cutoff * 0.6, cutoff, 2, block=1024), 'high', 120) * env
    R = butter(sweep_filter(R, 'low', cutoff * 0.6, cutoff, 2, block=1024), 'high', 120) * env
    return L * 0.12, R * 0.12


# ───────────────────────────── SFX ─────────────────────────────
def sfx_riser(dur):
    n = sec(dur)
    t = t_axis(n)
    p = t / dur
    nz = sweep_filter(noise(n), 'band', 180, 7000, 2, block=256, curve=1.4)
    tone = sine(90 * (14 ** p), n) * 0.35 + sine(90 * (14 ** p) * 1.5, n) * 0.15
    amp = (p ** 2.6) * 1.0
    out = (nz * 0.9 + tone) * amp
    # vibración rítmica que acelera
    out *= 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(4 + 40 * p ** 2) / SR) ** 2
    out = butter(out, 'high', 120)
    return out * 0.7


def sfx_impact(strength=1.0, ring=True, color='#fff'):
    n = sec(1.2)
    t = t_axis(n)
    boom = sine(34 + 38 * np.exp(-t / 0.08), n) * np.exp(-t / 0.45)
    burst = butter(noise(n), 'low', 2800, 2) * np.exp(-t / 0.07)
    crack = butter(noise(n), 'high', 1500, 2) * np.exp(-t / 0.012)
    out = boom * 0.85 + burst * 1.0 + crack * 0.9
    if ring:
        for f, g, tau in [(812, 0.5, 0.35), (1267, 0.3, 0.3), (2130, 0.18, 0.22), (3390, 0.08, 0.16)]:
            out += sine(f, n) * g * np.exp(-t / tau) * 0.25
    out = soft_clip(out * strength, 1.2)
    return out * 0.95


def sfx_thud(strength=0.6):
    n = sec(0.5)
    t = t_axis(n)
    out = sine(90 * np.exp(-t / 0.06) + 42, n) * np.exp(-t / 0.18) + butter(noise(n), 'low', 1200) * np.exp(-t / 0.03) * 0.6
    return soft_clip(out * strength * 1.3, 1.2) * 0.8


def sfx_whoosh(dur=0.55):
    n = sec(dur + 0.25)
    t = t_axis(n)
    env = np.exp(-((t - dur * 0.5) ** 2) / (2 * (dur * 0.22) ** 2))
    nz = sweep_filter(noise(n), 'band', 350, 5200, 2, block=256) * env
    nz = sweep_filter(nz, 'band', 600, 1400, 1, block=256)
    # paneo L → R
    p = np.clip(t / dur, 0, 1)
    gl = np.cos(p * math.pi / 2)
    gr = np.sin(p * math.pi / 2)
    return nz * gl * 0.9, nz * gr * 0.9


def sfx_word(i=0, size=100):
    n = sec(0.22)
    t = t_axis(n)
    f = 150 + 70 * (1 - min(size, 220) / 220) + 12 * ((i * 7) % 5)
    body = sine(f * (1 + 0.8 * np.exp(-t / 0.012)), n) * np.exp(-t / 0.055)
    click = butter(noise(n), 'band', [1800, 5000]) * np.exp(-t / 0.006)
    thock = butter(noise(n), 'low', 900) * np.exp(-t / 0.02)
    return (body * 0.9 + click * 0.5 + thock * 0.5) * 0.55


def sfx_tick(soft=False):
    n = sec(0.08)
    t = t_axis(n)
    x = butter(noise(n), 'band', [2500, 7000]) * np.exp(-t / 0.004) + sine(2100, n) * np.exp(-t / 0.012) * 0.5
    return x * (0.18 if soft else 0.32)


def sfx_alert():
    n = sec(0.35)
    t = t_axis(n)
    f = np.where(t < 0.08, 880, 1174.7)
    x = sine(f, n) * np.exp(-t / 0.12) * (1 - np.exp(-t / 0.003))
    x += sine(f * 2, n) * np.exp(-t / 0.06) * 0.2
    return x * 0.22


def sfx_pop():
    n = sec(0.25)
    t = t_axis(n)
    f = 380 + 700 * (1 - np.exp(-t / 0.03))
    x = sine(f, n) * np.exp(-t / 0.07) * (1 - np.exp(-t / 0.002))
    x += butter(noise(n), 'band', [900, 3000]) * np.exp(-t / 0.008) * 0.8
    return x * 0.45


def sfx_panel():
    n = sec(0.45)
    t = t_axis(n)
    x = sweep_filter(noise(n), 'low', 400, 3200, 2, block=256) * np.exp(-t / 0.12) * (1 - np.exp(-t / 0.01))
    return x * 0.28


def sfx_slide(dur=0.7):
    n = sec(dur)
    t = t_axis(n)
    p = t / dur
    f = 260 * (3.2 ** (1 - (1 - p) ** 3))
    x = sine(f, n) * 0.35 + sweep_filter(noise(n), 'band', 800, 4500, 2, block=256) * 0.6
    amp = (1 - p) ** 1.5 * (1 - np.exp(-t / 0.01))
    return x * amp * 0.3


def sfx_count(dur):
    """Tren de clics que sigue la curva outExpo del contador."""
    out = np.zeros(sec(dur + 0.3))
    ps = np.linspace(0, 0.985, 34)
    for p in ps:
        u = -math.log2(1 - p) / 10
        tk = dur * u
        i = sec(tk)
        c = sfx_tick(soft=True) * 1.4
        k = min(len(c), len(out) - i)
        out[i:i + k] += c[:k]
    return out


def sfx_spinup(dur=1.5, soft=False, sustain=2.4):
    """Motor universal arrancando: fundamental + armónicos + silbido de escobillas, con flutter."""
    total = dur + sustain
    n = sec(total)
    t = t_axis(n)
    p = np.clip(t / dur, 0, 1)
    f = 38 + (170 - 38) * (1 - (1 - p) ** 2.4)
    motor = saw(f, n) * 0.5 + sine(f * 2, n) * 0.25 + saw(f * 3.01, n) * 0.12
    whine = sine(f * 11.0, n) * 0.08 + sine(f * 17.3, n) * 0.04
    hum = butter(noise(n), 'band', [90, 260]) * 0.3
    flutter = 1 + 0.08 * np.sin(2 * np.pi * np.cumsum(f * 0.5) / SR)
    x = (motor + whine + hum) * flutter
    amp = (0.15 + 0.85 * p ** 1.3)
    tail_start = dur + sustain * 0.55
    amp = amp * np.where(t > tail_start, np.exp(-(t - tail_start) / 0.5), 1.0)
    x = butter(x, 'low', 4200, 2) * amp
    return soft_clip(x * 1.2, 1.4) * (0.22 if soft else 0.42)


def sfx_grind(dur=1.5):
    n = sec(dur + 0.3)
    t = t_axis(n)
    env = np.clip(t / 0.12, 0, 1) * np.clip((dur + 0.3 - t) / 0.3, 0, 1)
    body = butter(noise(n), 'band', [1800, 7000], 2)
    crackle = (rng.random(n) < 0.012).astype(float) * rng.uniform(0.3, 1.0, n)
    crackle = butter(crackle, 'band', [2500, 9000], 2) * 2.2
    rumble = butter(noise(n), 'low', 240, 2) * 0.9
    mod = 0.65 + 0.35 * np.abs(butter(noise(n), 'low', 14, 1)) * 4
    x = (body * 0.7 + crackle + rumble) * np.clip(mod, 0.3, 1.4) * env
    return soft_clip(x * 1.1, 1.3) * 0.5


def sfx_check():
    n = sec(0.3)
    t = t_axis(n)
    f = np.where(t < 0.07, 1046.5, 1568.0)
    x = sine(f, n) * np.exp(-t / 0.09) * (1 - np.exp(-t / 0.002)) + butter(noise(n), 'band', [3000, 8000]) * np.exp(-t / 0.004) * 0.6
    return x * 0.26


def sfx_buzz():
    n = sec(0.22)
    t = t_axis(n)
    x = np.sign(sine(110, n)) * 0.5 + np.sign(sine(165, n)) * 0.3
    x = butter(x, 'low', 1800) * adsr(n, 0.003, 0.05, 0.6, 0.08)
    return x * 0.3


def sfx_scratch(dur=0.75):
    n = sec(dur)
    t = t_axis(n)
    swipes = np.sin(2 * np.pi * (3 / dur) * t) ** 2  # tres pasadas
    x = sweep_filter(noise(n), 'band', 900, 2600, 2, block=256) * swipes * (1 - (t / dur) ** 4)
    return x * 0.45


def sfx_card():
    n = sec(0.35)
    t = t_axis(n)
    paper = butter(noise(n), 'band', [1500, 6000]) * np.exp(-t / 0.03)
    thud = sine(120 * np.exp(-t / 0.05) + 60, n) * np.exp(-t / 0.08)
    return (paper * 0.6 + thud * 0.5) * 0.4


def sfx_logo(root_freq=261.63):
    n = sec(2.8)
    t = t_axis(n)
    out = np.zeros(n)
    for r, g, tau in [(1.0, 1.0, 1.2), (1.5, 0.6, 1.0), (2.0, 0.5, 0.9), (2.5, 0.3, 0.7), (4.0, 0.15, 0.5)]:
        out += sine(root_freq * r, n) * g * np.exp(-t / tau)
    out *= (1 - np.exp(-t / 0.004))
    boom = sine(55 + 30 * np.exp(-t / 0.08), n) * np.exp(-t / 0.5) * 0.6
    return (out * 0.22 + boom)


def sfx_disc():
    n = sec(0.3)
    t = t_axis(n)
    x = butter(noise(n), 'band', [600, 2500]) * np.exp(-t / 0.015) + sine(95 * np.exp(-t / 0.04) + 50, n) * np.exp(-t / 0.1) * 0.8
    return x * 0.35


# ───────────────────────────── música ─────────────────────────────
STYLE = {
    'dark': dict(kicks=[0, 2.75, 3.0], hat_div=2, open_hats=[1.5, 3.5], arp=True, pad_cut=1200, ping=[1.5]),
    'punchy': dict(kicks=[0, 1.75, 2.5, 3.0], hat_div=4, open_hats=[1.5, 3.5], arp=True, pad_cut=1600, ping=[0.5, 2.5]),
    'heavy': dict(kicks=[0, 2.5, 3.0, 3.75], hat_div=2, open_hats=[3.5], arp=False, pad_cut=900, ping=[1.0, 3.0]),
    'cinematic': dict(kicks=[0, 3.0], hat_div=2, open_hats=[], arp=False, pad_cut=1000, ping=[2.0]),
    'bright': dict(kicks=[0, 1.5, 2.5, 3.0], hat_div=4, open_hats=[1.5, 3.5], arp=True, pad_cut=2000, ping=[0.5, 2.5]),
}
# i – VI – III – VII (menor), en semitonos relativos a la tónica, con sus tríadas.
PROG = [(0, [0, 3, 7]), (8, [0, 4, 7]), (3, [0, 4, 7]), (10, [0, 4, 7])]


def render_music(bus, meta):
    m = meta['music']
    bpm, root, style = m['bpm'], m['root'], m['style']
    drop, outro = m['drop'], m['outro']
    dur = meta['duration']
    st = STYLE[style]
    beat = 60.0 / bpm
    bar = beat * 4

    music = Bus(dur)
    kicks = Bus(dur)
    duck_times = []

    # Pad desde el inicio (filtrado y suave antes del drop), cambia por compás.
    t = 0.0
    bar_i = 0
    while t < dur + 0.5:
        deg, tri = PROG[bar_i % 4]
        freqs = [midi(root + 12 + deg + k) for k in tri]
        L, R = pad_chord(freqs, bar + 0.4, cutoff=st['pad_cut'] if t >= drop - 0.1 else st['pad_cut'] * 0.45)
        g = (1.0 if t < outro else 1.25) * (1.7 if not st['arp'] else 1.0)
        music.add_stereo(t, L, R, gain=g)
        t += bar
        bar_i += 1

    # Beat entre drop y outro, alineado a la grilla desde el drop.
    t = drop
    bar_i = 0
    while t < outro - 0.05:
        deg, tri = PROG[bar_i % 4]
        sub_f = midi(root + deg)
        for kb in st['kicks']:
            tk = t + kb * beat
            if tk >= outro - 0.05:
                continue
            kicks.add(tk, kick(1.0, style))
            music.add(tk, sub808(sub_f, 0.9, 0.9))
            duck_times.append(tk)
        for cb in [1, 3]:
            tc = t + cb * beat
            if tc < outro - 0.05:
                music.add(tc, clap(0.9 if cb == 1 else 1.0), pan=0.08)
        nh = 4 * st['hat_div']
        for h in range(nh):
            th = t + h * (bar / nh)
            if th >= outro - 0.05:
                continue
            vel = 1.0 if h % st['hat_div'] == 0 else 0.55
            vel *= 0.85 + 0.3 * rng.random()
            if bar_i % 2 == 1 and h >= nh - 3 and style in ('punchy', 'bright'):
                vel *= 1.1  # mini roll al final del compás
            music.add(th, hat(False, vel), pan=0.35 * math.sin(h * 1.7))
        for ob in st['open_hats']:
            to = t + ob * beat
            if to < outro - 0.05:
                music.add(to, hat(True, 0.5), pan=0.4)
        for pb in st['ping']:
            tp = t + pb * beat
            if tp < outro - 0.05:
                music.add(tp, metal_ping(midi(root + 24 + deg) * 1.5, 0.6 if bar_i % 2 else 0.4), pan=-0.5 + (bar_i % 3) * 0.5)
        if st['arp']:
            notes = [midi(root + 24 + deg + k) for k in tri] + [midi(root + 36 + deg)]
            for s16 in range(16):
                ts = t + s16 * (beat / 4)
                if ts >= outro - 0.05:
                    continue
                if s16 % 4 == 3 and rng.random() < 0.35:
                    continue
                f = notes[s16 % len(notes)] if s16 % 2 == 0 else notes[(s16 * 3) % len(notes)]
                music.add(ts, pluck(f, 0.4, 0.55 + 0.35 * (s16 % 4 == 0)), pan=-0.55 + 1.1 * ((s16 % 3) / 2))
        t += bar
        bar_i += 1

    # Golpe final del beat en el outro (un kick + sub largo), y campana la agrega el evento 'logo'.
    kicks.add(outro, kick(1.0, style) * 1.1)
    music.add(outro, sub808(midi(root), 1.8, 1.0))
    duck_times.append(outro)

    # Sidechain: el resto de la música cede ante el kick.
    duck = np.ones(music.n)
    ta = t_axis(music.n)
    for tk in duck_times:
        i = sec(tk)
        seg = ta[i:] - tk
        duck[i:] = np.minimum(duck[i:], 1 - 0.65 * np.exp(-seg / 0.11) * (seg >= 0))
    music.L *= duck
    music.R *= duck
    # Pegamento: compresión suave + pegada
    gl = 0.95
    bus.add_stereo(0, soft_clip(music.L * 1.1, 1.5) * gl + kicks.L, soft_clip(music.R * 1.1, 1.5) * gl + kicks.R, gain=1.0)


# ───────────────────────────── SFX desde eventos ─────────────────────────────
def render_sfx(bus, meta):
    root = meta['music']['root']
    for ev in meta['events']:
        t, ty = ev['t'], ev['type']
        if ty == 'riser':
            bus.add(t, sfx_riser(ev.get('dur', 0.8)), pan=0.0)
        elif ty == 'impact':
            bus.add(t, sfx_impact(ev.get('strength', 1.0)))
        elif ty == 'thud':
            bus.add(t, sfx_thud(ev.get('strength', 0.6)))
        elif ty == 'whoosh':
            l, r = sfx_whoosh(ev.get('dur', 0.55))
            bus.add_stereo(t, l, r)
        elif ty == 'word':
            bus.add(t, sfx_word(ev.get('i', 0), ev.get('size', 100)), pan=-0.15 + 0.3 * ((ev.get('i', 0) % 3) / 2))
        elif ty == 'tick':
            bus.add(t, sfx_tick(ev.get('soft', False)), pan=0.1)
        elif ty == 'alert':
            bus.add(t, sfx_alert(), pan=0.2)
        elif ty == 'pop':
            bus.add(t, sfx_pop(), pan=0.25)
        elif ty == 'panel':
            bus.add(t, sfx_panel(), pan=-0.2)
        elif ty == 'count':
            bus.add(t, sfx_count(ev.get('dur', 1.0)), pan=-0.1)
        elif ty == 'slide':
            bus.add(t, sfx_slide(ev.get('dur', 0.7)), pan=0.0)
        elif ty == 'spinup':
            bus.add(t, sfx_spinup(ev.get('dur', 1.5), ev.get('soft', False)), pan=0.0)
        elif ty == 'grind':
            bus.add(t, sfx_grind(ev.get('dur', 1.5)), pan=0.3)
        elif ty == 'check':
            bus.add(t, sfx_check(), pan=-0.2)
        elif ty == 'buzz':
            bus.add(t, sfx_buzz(), pan=-0.2)
        elif ty == 'scratch':
            bus.add(t, sfx_scratch(ev.get('dur', 0.75)), pan=0.0)
        elif ty == 'card':
            bus.add(t, sfx_card(), pan=0.0)
        elif ty == 'logo':
            bus.add(t, sfx_logo(midi(root + 24)), pan=0.0)
        elif ty == 'disc':
            bus.add(t, sfx_disc(), pan=0.0)


# ───────────────────────────── master ─────────────────────────────
def master(L, R, dur):
    n = sec(dur)
    L, R = L[:n], R[:n]
    # Fade final corto para que el reel loopee limpio.
    fade = np.ones(n)
    k = sec(0.25)
    fade[-k:] = np.linspace(1, 0, k)
    L, R = L * fade, R * fade
    # Filtro de aire y sub-grave controlado.
    L, R = butter(L, 'high', 28), butter(R, 'high', 28)
    # Normalización por RMS y soft clip estilo bus de masterización.
    mono = (L + R) / 2
    rms = math.sqrt(float(np.mean(mono ** 2))) + 1e-9
    target = 10 ** (-17.0 / 20)
    g = target / rms
    L, R = soft_clip(L * g, 1.1), soft_clip(R * g, 1.1)
    peak = max(float(np.max(np.abs(L))), float(np.max(np.abs(R))), 1e-9)
    if peak > 0.98:
        L, R = L / peak * 0.98, R / peak * 0.98
    return L, R


def write_wav(path, L, R):
    x = np.stack([L, R], axis=1)
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def build(json_path: Path, out_wav: Path):
    meta = json.loads(json_path.read_text())
    bus = Bus(meta['duration'])
    render_music(bus, meta)
    render_sfx(bus, meta)
    L, R = master(bus.L, bus.R, meta['duration'])
    write_wav(out_wav, L, R)
    print(f"{meta['id']}: {out_wav} ({meta['duration']}s, {len(meta['events'])} eventos)")


if __name__ == '__main__':
    out_dir = Path(sys.argv[1])
    ids = sys.argv[2:]
    for jp in sorted(out_dir.glob('*.json')):
        if ids and jp.stem not in ids:
            continue
        build(jp, out_dir / f'{jp.stem}.wav')
