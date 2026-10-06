#!/usr/bin/env python3
"""Música original + sound design para los reels de hidrolavadoras.

Lee ../salida/tmp/reel-N-events.json (lo exporta render.mjs) y escribe
../salida/tmp/reel-N-audio.wav (48 kHz, estéreo). Todo se sintetiza con numpy/scipy:
no se usan samples de terceros.

    python3 audio.py --reel 1
"""
import argparse
import json
import os
import sys
import wave

import numpy as np
from scipy import signal

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, '..', 'salida', 'tmp')


# ----------------------------------------------------------------- utilidades
def sec(n):
    return int(round(n * SR))


def t_axis(n):
    return np.arange(n) / SR


def env_adsr(n, a=0.005, d=0.1, s=0.7, r=0.2):
    a_n, d_n, r_n = sec(a), sec(d), sec(r)
    s_n = max(0, n - a_n - d_n - r_n)
    e = np.concatenate([
        np.linspace(0, 1, max(a_n, 1)),
        np.linspace(1, s, max(d_n, 1)),
        np.full(s_n, s),
        np.linspace(s, 0, max(r_n, 1)),
    ])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))


def env_exp(n, tau):
    return np.exp(-t_axis(n) / tau)


def sos_lp(fc, order=2):
    return signal.butter(order, min(fc, SR * 0.49) / (SR / 2), 'low', output='sos')


def sos_hp(fc, order=2):
    return signal.butter(order, max(fc, 10) / (SR / 2), 'high', output='sos')


def sos_bp(lo, hi, order=2):
    lo = max(10, lo); hi = min(hi, SR * 0.49)
    return signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band', output='sos')


def lp(x, fc, order=2):
    return signal.sosfilt(sos_lp(fc, order), x)


def hp(x, fc, order=2):
    return signal.sosfilt(sos_hp(fc, order), x)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(sos_bp(lo, hi, order), x)


def sweep_lp(x, f0, f1, curve=1.0, order=2, block=256):
    """Pasa-bajos con corte que barre de f0 a f1 a lo largo de x."""
    out = np.empty_like(x)
    zi = None
    n = len(x)
    for i in range(0, n, block):
        k = (i / n) ** curve
        fc = f0 * (f1 / f0) ** k
        sos = sos_lp(fc, order)
        if zi is None:
            zi = signal.sosfilt_zi(sos) * x[0]
        out[i:i + block], zi = signal.sosfilt(sos, x[i:i + block], zi=zi)
    return out


def sweep_bp(x, lo0, lo1, width=1.8, order=2, block=256):
    out = np.empty_like(x)
    zi = None
    n = len(x)
    for i in range(0, n, block):
        k = i / n
        lo = lo0 * (lo1 / lo0) ** k
        sos = sos_bp(lo, lo * width, order)
        if zi is None:
            zi = signal.sosfilt_zi(sos) * 0
        out[i:i + block], zi = signal.sosfilt(sos, x[i:i + block], zi=zi)
    return out


def saw(f, n, detune=0.0):
    t = t_axis(n)
    return signal.sawtooth(2 * np.pi * f * (1 + detune) * t)


def sine(f, n, phase=0.0):
    return np.sin(2 * np.pi * f * t_axis(n) + phase)


def sine_sweep(f0, f1, n, curve=1.0):
    t = t_axis(n)
    k = (t / t[-1]) ** curve if n > 1 else t
    f = f0 * (f1 / f0) ** k
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph)


def noise(n, rng):
    return rng.standard_normal(n).astype(np.float64)


def reverb_ir(rng, tau=0.9, length=1.6, lp_fc=5000):
    n = sec(length)
    ir = noise(n, rng) * env_exp(n, tau)
    ir = lp(ir, lp_fc)
    ir[:sec(0.004)] *= np.linspace(0, 1, sec(0.004))
    return ir / np.sqrt(np.sum(ir ** 2))


def convolve(x, ir):
    y = signal.fftconvolve(x, ir)[:len(x)]
    return y


class Mix:
    """Bus estéreo de longitud fija con add(t, mono/stereo, gain, pan)."""

    def __init__(self, dur):
        self.n = sec(dur)
        self.L = np.zeros(self.n)
        self.R = np.zeros(self.n)

    def add(self, t, x, gain=1.0, pan=0.0):
        i = sec(t)
        if i >= self.n:
            return
        if x.ndim == 1:
            xl = x * (np.cos((pan + 1) * np.pi / 4))
            xr = x * (np.sin((pan + 1) * np.pi / 4))
        else:
            xl, xr = x[0], x[1]
        if i < 0:
            xl, xr, i = xl[-i:], xr[-i:], 0
        m = min(len(xl), self.n - i)
        self.L[i:i + m] += xl[:m] * gain
        self.R[i:i + m] += xr[:m] * gain

    def stereo(self):
        return np.stack([self.L, self.R])


# ----------------------------------------------------------------- instrumentos
def kick(rng, hard=1.0):
    n = sec(0.55)
    body = sine_sweep(165 * hard, 42, n, curve=0.35) * env_exp(n, 0.16)
    click = hp(noise(sec(0.012), rng), 1500) * env_exp(sec(0.012), 0.003) * 0.5
    x = body.copy(); x[:len(click)] += click
    x = np.tanh(x * 1.8) / 1.8
    return x * 1.1


def snare(rng):
    n = sec(0.32)
    tone = (sine(185, n) + 0.5 * sine(330, n)) * env_exp(n, 0.045)
    nz = bp(noise(n, rng), 900, 7000) * env_exp(n, 0.09)
    x = tone * 0.6 + nz * 0.9
    return np.tanh(x * 1.5) / 1.5


def clank(rng):
    """Golpe metálico seco (percusión industrial)."""
    n = sec(0.22)
    x = np.zeros(n)
    for f, a in ((1830, 1), (2710, .6), (4120, .45), (6230, .3)):
        x += a * sine(f * (1 + rng.uniform(-.01, .01)), n) * env_exp(n, 0.035 / (1 + f / 4000))
    x += bp(noise(n, rng), 2500, 9000) * env_exp(n, 0.012) * 0.8
    return x * 0.35


def hat(rng, open_=False):
    n = sec(0.32 if open_ else 0.06)
    x = hp(noise(n, rng), 7000, 4) * env_exp(n, 0.09 if open_ else 0.012)
    return x * 0.55


def pluck(f, n, rng):
    x = (saw(f, n) + 0.4 * saw(f, n, 0.006)) * env_exp(n, 0.09)
    x = sweep_lp(x, 6000, 500, curve=0.6)
    return x * 0.5


def pad_chord(freqs, n, rng):
    L = np.zeros(n); R = np.zeros(n)
    for f in freqs:
        for det, side in ((-0.007, 'L'), (0.007, 'R'), (0.0, 'C')):
            w = saw(f, n, det) * 0.3 + sine(f, n) * 0.25
            if side == 'L': L += w
            elif side == 'R': R += w
            else: L += w * .7; R += w * .7
    e = env_adsr(n, a=0.9, d=0.5, s=0.9, r=1.2)
    lfo = 1 + 0.08 * np.sin(2 * np.pi * 0.23 * t_axis(n))
    L = lp(L * e, 1900) * lfo; R = lp(R * e, 1900) * lfo
    return np.stack([L, R]) * 0.3


def sub_bass(f, n):
    x = sine(f, n) + 0.25 * sine(2 * f, n) + 0.12 * np.tanh(3 * saw(f, n))
    e = env_adsr(n, a=0.01, d=0.08, s=0.8, r=0.08)
    return lp(x * e, 240) * 0.45


# ----------------------------------------------------------------- música
NOTE = lambda midi: 440.0 * 2 ** ((midi - 69) / 12)
PROGRESSIONS = {
    1: [('A', 45, [57, 60, 64]), ('F', 41, [53, 57, 60]), ('C', 48, [55, 60, 64]), ('G', 43, [55, 59, 62])],
    2: [('D', 38, [50, 53, 57]), ('Bb', 46, [53, 58, 62]), ('F', 41, [53, 57, 60]), ('C', 48, [52, 55, 60])],
    3: [('E', 40, [52, 55, 59]), ('C', 48, [52, 55, 60]), ('G', 43, [50, 55, 59]), ('D', 50, [50, 54, 57])],
    4: [('F#', 42, [54, 57, 61]), ('D', 38, [50, 54, 57]), ('A', 45, [52, 57, 61]), ('E', 40, [52, 56, 59])],
    5: [('C', 36, [48, 51, 55]), ('Ab', 44, [51, 56, 60]), ('Eb', 39, [51, 55, 58]), ('Bb', 46, [50, 53, 58])],
    6: [('B', 47, [59, 62, 66]), ('G', 43, [55, 59, 62]), ('D', 50, [54, 57, 62]), ('A', 45, [52, 57, 61])],
}


def music(meta, events, rng):
    dur = meta['dur']
    reel = meta['reel']
    bpm = {1: 112, 2: 116, 3: 118, 4: 114, 5: 108, 6: 112}[reel]
    step = 60 / bpm / 4
    bar = step * 16
    prog = PROGRESSIONS[reel]
    # el beat entra en la primera escena después del hook; el cierre está en 'logo'
    t_drop = min(e['t'] for e in events if e['type'] in ('whoosh',) and e['t'] > 1.0)
    t_logo = next(e['t'] for e in events if e['type'] == 'logo')
    t_verdict = max([e['t'] for e in events if e['type'] == 'slam' and e['t'] > t_drop] + [t_logo - 4])
    mix = Mix(dur + 2)      # percusión
    ton = Mix(dur + 2)      # pad, bajo y plucks (van con sidechain)

    # --- intro: dron tenso + pulso + riser hasta el drop
    n_intro = sec(t_drop + 0.2)
    root = NOTE(prog[0][1])
    drone = (sine(root / 2, n_intro) * 0.5 + lp(saw(root, n_intro) * 0.2 + saw(root, n_intro, 0.005) * 0.2, 500))
    drone *= env_adsr(n_intro, a=0.4, d=0.3, s=0.85, r=0.5)
    pulse = 0.55 + 0.45 * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * (bpm / 60) * t_axis(n_intro))))
    mix.add(0, drone * pulse, 1.0)
    riser = noise(n_intro, rng)
    riser = sweep_bp(riser, 180, 5000, width=2.2) * (t_axis(n_intro) / (n_intro / SR)) ** 2.2
    mix.add(0, riser, 0.32, pan=0.0)
    mix.add(0, sine_sweep(root, root * 4, n_intro, curve=2.5) * (t_axis(n_intro) / (n_intro / SR)) ** 3, 0.12)

    # --- groove
    n_bars = int(np.ceil((dur - t_drop) / bar)) + 1
    kick_s = kick(rng); snare_s = snare(rng); clank_s = clank(rng)
    hat_c = hat(rng); hat_o = hat(rng, True)
    kick_steps = {0, 7, 10}
    snare_steps = {8}
    clank_steps = {4, 12}
    sc = np.ones(mix.n)  # sidechain env
    for b in range(n_bars):
        tb = t_drop + b * bar
        chord = prog[(b // 2) % len(prog)]
        croot = NOTE(chord[1] + 12)
        in_verdict = tb >= t_verdict - 0.05 and tb < t_logo
        in_outro = tb >= t_logo - 0.05
        # pad
        if not in_outro:
            pc = pad_chord([NOTE(m) for m in chord[2]], sec(bar * 2 + 1.5), rng)
            if b % 2 == 0:
                ton.add(tb, pc, 1.0)
        for st in range(16):
            ts = tb + st * step + (0.012 if st % 2 == 1 else 0)  # swing leve
            if ts >= t_logo:
                break
            vel = 1.0 if not in_verdict else 0.75
            if st in kick_steps and not (in_verdict and st == 10):
                mix.add(ts, kick_s, 0.95 * vel)
                i = sec(ts); m = sec(0.28)
                sc[i:i + m] *= np.minimum(1, 0.35 + (np.arange(min(m, mix.n - i)) / m) ** 1.5)
            if st in snare_steps:
                mix.add(ts, snare_s, 1.0 * vel, pan=0.05)
            if st in clank_steps and not in_verdict:
                mix.add(ts, clank_s, 0.85, pan=-0.35 if st == 4 else 0.35)
            if st % 2 == 0:
                mix.add(ts, hat_c, (1.0 if st % 4 == 0 else 0.6) * vel, pan=0.25)
            if st == 14:
                mix.add(ts, hat_o, 0.6 * vel, pan=0.25)
            # bajo
            if st in (0, 3, 6, 10, 12):
                ln = step * (3 if st in (0, 6) else 2)
                ton.add(ts, sub_bass(croot / 2, sec(ln)), 0.95)
            # arpegio de plucks (16avos, solo fuera del veredicto)
            if not in_verdict and st % 2 == 1:
                notes = chord[2]
                m = notes[(st // 2) % 3] + (12 if st in (7, 15) else 0)
                ton.add(ts, pluck(NOTE(m), sec(step * 1.8), rng), 0.55, pan=(-0.4 if (st // 2) % 2 == 0 else 0.4))
    # --- cierre: pad final largo + sub
    chord = prog[0]
    n_end = sec(dur - t_logo + 1.5)
    pc = pad_chord([NOTE(m) for m in chord[2]] + [NOTE(chord[2][0] + 12)], n_end, rng)
    pc *= np.linspace(1, 0.0, n_end) ** 0.6
    ton.add(t_logo, pc, 1.3)
    ton.add(t_logo, sub_bass(NOTE(chord[1]), n_end) * np.linspace(1, 0, n_end) ** 0.8, 0.8)
    st = mix.stereo() + ton.stereo() * sc
    # reverb suave de sala en la música
    ir = reverb_ir(rng, tau=0.5, length=0.9, lp_fc=3500)
    st = st + 0.12 * np.stack([convolve(st[0], ir), convolve(st[1], reverb_ir(rng, tau=0.5, length=0.9, lp_fc=3500))])
    return st[:, :sec(dur)]


# ----------------------------------------------------------------- sound design
def sfx_slam(rng, accent):
    n = sec(1.4)
    boom = sine_sweep(95, 34, n, curve=0.3) * env_exp(n, 0.32)
    imp = bp(noise(sec(0.09), rng), 150, 2500) * env_exp(sec(0.09), 0.02)
    x = boom * 1.0; x[:len(imp)] += imp * 1.4
    crack = hp(noise(sec(0.02), rng), 3000) * env_exp(sec(0.02), 0.004)
    x[:len(crack)] += crack * 0.6
    if accent:
        ring = np.zeros(n)
        for f, a in ((880, 1), (1318, .5), (1975, .35)):
            ring += a * sine(f, n) * env_exp(n, 0.25)
        x += ring * 0.08
    return np.tanh(x * 1.3) / 1.3


def sfx_whoosh(rng):
    n = sec(0.6)
    x = noise(n, rng)
    x = sweep_bp(x, 250, 5200, width=2.5)
    e = (np.sin(np.pi * (t_axis(n) / (n / SR))) ** 1.6)
    x = x * e
    pan = np.linspace(-0.8, 0.8, n)
    return np.stack([x * np.cos((pan + 1) * np.pi / 4), x * np.sin((pan + 1) * np.pi / 4)]) * 0.5


def sfx_thud(rng):
    n = sec(0.4)
    x = sine_sweep(120, 45, n, curve=0.4) * env_exp(n, 0.12)
    imp = bp(noise(sec(0.03), rng), 200, 1800) * env_exp(sec(0.03), 0.008)
    x[:len(imp)] += imp
    return np.tanh(x * 1.4) / 1.4 * 0.9


def sfx_tick(rng):
    n = sec(0.04)
    x = hp(noise(n, rng), 2500) * env_exp(n, 0.004) + sine(2200, n) * env_exp(n, 0.008) * 0.6
    return x * 0.55


def sfx_ding(rng):
    n = sec(0.7)
    x = np.zeros(n)
    for f, a in ((1568, 1), (3136, .35), (4704, .15)):
        x += a * sine(f, n) * env_exp(n, 0.22)
    return x * 0.16


def sfx_buzz(rng):
    n = sec(0.18)
    x = np.sign(np.sin(2 * np.pi * 110 * t_axis(n))) * 0.5 + np.sign(np.sin(2 * np.pi * 116 * t_axis(n))) * 0.5
    x = bp(x, 150, 900) * env_adsr(n, a=0.005, d=0.05, s=0.7, r=0.08)
    return x * 0.35


def sfx_pop(rng):
    n = sec(0.09)
    x = sine_sweep(720, 320, n, curve=0.7) * env_exp(n, 0.025)
    return x * 0.5


def sfx_count(rng, dur):
    n = sec(dur)
    x = np.zeros(n)
    tk = sfx_tick(rng) * 0.5
    k = 0.0
    while k < dur:
        i = sec(k); m = min(len(tk), n - i)
        x[i:i + m] += tk[:m]
        k += 0.045
    return x * np.linspace(1, 0.4, n)


def sfx_rise(rng, dur):
    n = sec(dur)
    x = sweep_bp(noise(n, rng), 300, 3500, width=2.0) * (t_axis(n) / dur) ** 1.5
    x += sine_sweep(220, 880, n, curve=1.2) * (t_axis(n) / dur) ** 2 * 0.3
    x[-sec(0.05):] *= np.linspace(1, 0, sec(0.05))
    return x * 0.35


def sfx_drop(rng, dur):
    n = sec(dur)
    x = sine_sweep(660, 165, n, curve=0.8) * env_adsr(n, a=0.02, d=0.2, s=0.5, r=0.2) * 0.35
    x += sweep_bp(noise(n, rng), 3500, 300, width=2.0) * np.sin(np.pi * t_axis(n) / dur) * 0.4
    return x * 0.8


def sfx_logo(rng):
    n = sec(2.4)
    boom = sine_sweep(80, 30, n, curve=0.3) * env_exp(n, 0.45)
    imp = bp(noise(sec(0.12), rng), 120, 3000) * env_exp(sec(0.12), 0.03)
    x = boom * 1.1; x[:len(imp)] += imp * 1.2
    shimmer = np.zeros(n)
    for f, a in ((1760, 1), (2637, .6), (3520, .5), (5274, .3)):
        shimmer += a * sine(f * (1 + rng.uniform(-.003, .003)), n) * env_adsr(n, a=0.3, d=0.5, s=0.5, r=1.2)
    x += shimmer * 0.05
    return np.tanh(x * 1.2) / 1.2


def sfx_spray(rng, dur, mode):
    """Chorro de hidrolavadora: siseo filtrado con flutter + motor/bomba + gotas."""
    n = sec(dur)
    t = t_axis(n)
    hiss = noise(n, rng)
    if mode == 'narrow':
        hiss = bp(hiss, 2500, 11000, 3)
    elif mode == 'wide':
        hiss = bp(hiss, 900, 7000, 3)
    else:
        hiss = bp(hiss, 1400, 9500, 3)
    flutter = 1 + 0.22 * np.sin(2 * np.pi * 7.3 * t) * np.sin(2 * np.pi * 1.9 * t) + 0.12 * lp(noise(n, rng), 12) * 3
    hiss = hiss * flutter
    # motor eléctrico + pulso de bomba
    motor = (saw(100, n) * 0.5 + saw(200, n, 0.002) * 0.25 + sine(50, n) * 0.6)
    motor = lp(motor, 420) * (0.8 + 0.2 * np.sign(np.sin(2 * np.pi * 29 * t)))
    # gotas
    drops = np.zeros(n)
    k = 0.0
    while k < dur:
        f = rng.uniform(1800, 4200); m = sec(rng.uniform(0.02, 0.05))
        i = sec(k); m = min(m, n - i)
        if m > 10:
            drops[i:i + m] += sine_sweep(f, f * 0.55, m) * env_exp(m, 0.008) * rng.uniform(0.2, 0.6)
        k += rng.uniform(0.04, 0.22)
    e = env_adsr(n, a=0.25, d=0.1, s=1.0, r=0.5)
    x = (hiss * 0.5 + motor * 0.22 + drops * 0.25) * e
    pan = np.full(n, 0.35 if mode == 'hook' else 0.0)
    return np.stack([x * np.cos((pan + 1) * np.pi / 4), x * np.sin((pan + 1) * np.pi / 4)]) * 0.7


def sound_design(meta, events, rng):
    dur = meta['dur']
    mix = Mix(dur + 2)
    duck = np.ones(mix.n)
    for e in events:
        t, ty = e['t'], e['type']
        if ty == 'slam':
            mix.add(t, sfx_slam(rng, e.get('accent', False)), 0.8)
            d = 0.42
        elif ty == 'whoosh':
            mix.add(t - 0.3, sfx_whoosh(rng), 0.7); d = 0
        elif ty == 'thud':
            mix.add(t, sfx_thud(rng), 0.7); d = 0.25
        elif ty == 'tick':
            mix.add(t, sfx_tick(rng), 0.8, pan=rng.uniform(-0.3, 0.3)); d = 0
        elif ty == 'ding':
            mix.add(t, sfx_ding(rng), 0.9, pan=0.3); d = 0
        elif ty == 'buzz':
            mix.add(t, sfx_buzz(rng), 0.8, pan=-0.3); d = 0
        elif ty == 'pop':
            mix.add(t, sfx_pop(rng), 0.7); d = 0
        elif ty == 'count':
            mix.add(t, sfx_count(rng, e.get('dur', 0.9)), 0.6); d = 0
        elif ty == 'rise':
            mix.add(t, sfx_rise(rng, e.get('dur', 0.8)), 0.7); d = 0
        elif ty == 'drop':
            mix.add(t, sfx_drop(rng, e.get('dur', 0.9)), 0.8); d = 0
        elif ty == 'logo':
            mix.add(t, sfx_logo(rng), 0.9); d = 0.6
        elif ty == 'spray':
            mix.add(t, sfx_spray(rng, e.get('dur', 3), e.get('mode', 'hook')), 0.75); d = 0
        else:
            d = 0
        if d:
            i = sec(t); m = sec(d)
            seg = np.arange(min(m, mix.n - i)) / m
            duck[i:i + m] *= np.minimum(1, 0.3 + seg ** 1.3)
    st = mix.stereo()
    ir = reverb_ir(rng, tau=0.7, length=1.3, lp_fc=4500)
    st = st + 0.16 * np.stack([convolve(st[0], ir), convolve(st[1], reverb_ir(rng, tau=0.7, length=1.3, lp_fc=4500))])
    return st[:, :sec(dur)], duck[:sec(dur)]


# ----------------------------------------------------------------- master
def limiter(x, ceiling=0.89, lookahead=0.004, release=0.08):
    peak = np.max(np.abs(x), axis=0)
    la = sec(lookahead)
    env = np.maximum.accumulate(np.pad(peak, (la, 0))[:len(peak)])  # aproximación de lookahead
    need = np.maximum(1.0, env / ceiling)
    g = np.ones_like(need)
    rel = np.exp(-1 / (release * SR))
    cur = 1.0
    for i in range(len(need)):  # suavizado con release
        tgt = 1 / need[i]
        cur = tgt if tgt < cur else cur * rel + tgt * (1 - rel)
        g[i] = cur
    return x * g


def write_wav(path, st):
    x = np.clip(st.T, -1, 1)
    data = (x * 32767).astype('<i2').tobytes()
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data)


def read_wav(path):
    with wave.open(path, 'rb') as w:
        n = w.getnframes(); x = np.frombuffer(w.readframes(n), '<i2').reshape(-1, 2).T / 32768.0
    return x


def master(path, gain_db, ceiling_db=-2.0):
    """Aplica la ganancia medida (hacia -14 LUFS) y limita a un techo por muestra."""
    x = read_wav(path) * 10 ** (gain_db / 20)
    x = limiter(x, ceiling=10 ** (ceiling_db / 20))
    write_wav(path, x)
    print('master', path, f'gain {gain_db:+.2f} dB', 'pico', round(float(np.max(np.abs(x))), 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reel', type=int)
    ap.add_argument('--master', help='wav a masterizar')
    ap.add_argument('--gain-db', type=float, default=0.0)
    a = ap.parse_args()
    if a.master:
        master(a.master, a.gain_db); return
    with open(os.path.join(TMP, f'reel-{a.reel}-events.json')) as f:
        d = json.load(f)
    meta, events = d['meta'], d['events']
    rng = np.random.default_rng(1000 + a.reel)
    mus = music(meta, events, rng)
    sfx, duck = sound_design(meta, events, rng)
    mus = mus / (np.max(np.abs(mus)) + 1e-9) * 0.72
    sfx = sfx / (np.max(np.abs(sfx)) + 1e-9) * 0.85
    if os.environ.get('AUDIO_DEBUG'):
        write_wav(os.path.join(TMP, f'reel-{a.reel}-musica.wav'), mus)
        write_wav(os.path.join(TMP, f'reel-{a.reel}-sfx.wav'), sfx)
    mixdown = mus * duck + sfx
    # fade final de 0,4 s para que el corte sea limpio
    n = mixdown.shape[1]; f = sec(0.4)
    mixdown[:, n - f:] *= np.linspace(1, 0, f)
    mixdown = np.tanh(mixdown * 1.15) / 1.15
    mixdown = limiter(mixdown)
    out = os.path.join(TMP, f'reel-{a.reel}-audio.wav')
    write_wav(out, mixdown)
    print('audio listo', out, f'{n / SR:.1f}s', 'pico', round(float(np.max(np.abs(mixdown))), 3))


if __name__ == '__main__':
    main()
