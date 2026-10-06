#!/usr/bin/env python3
"""Música y sound design sintetizados para los reels de TallerLab.
Lee salida/<reel>.timeline.json (eventos exportados por el HTML) y escribe salida/<reel>.wav (48 kHz, estéreo).
Todo se genera por código: no usa muestras externas."""
import json, sys, math
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
rng = np.random.default_rng(42)

# ---------- utilidades ----------
def sec(n): return int(round(n * SR))
def t_axis(n): return np.arange(n) / SR
def env_exp(n, tau): return np.exp(-t_axis(n) / tau)
def env_adsr(n, a=0.005, d=0.1, s=0.7, r=0.1):
    t = t_axis(n); e = np.ones(n)
    na, nd, nr = sec(a), sec(d), sec(r)
    if na: e[:na] = np.linspace(0, 1, na)
    if nd: e[na:na + nd] = np.linspace(1, s, nd)[:max(0, n - na)]
    e[na + nd:] = s
    if nr and n > nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e
def hann(n): return np.hanning(n)
def noise(n): return rng.standard_normal(n).astype(np.float64)
def lp(x, fc, order=2): sos = signal.butter(order, min(fc, SR / 2 - 100), 'low', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def hp(x, fc, order=2): sos = signal.butter(order, max(fc, 20), 'high', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def bp(x, lo, hi, order=2): sos = signal.butter(order, [max(lo, 20), min(hi, SR / 2 - 100)], 'band', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def sweep_filter(x, f_from, f_to, kind='low', chunk=256, order=2):
    """Filtro con corte que barre en el tiempo (procesado por bloques con estado)."""
    out = np.zeros_like(x); n = len(x); zi = None
    for i in range(0, n, chunk):
        u = i / n; fc = f_from * (f_to / f_from) ** u
        sos = signal.butter(order, min(max(fc, 30), SR / 2 - 100), kind, fs=SR, output='sos')
        if zi is None: zi = signal.sosfilt_zi(sos) * x[i]
        out[i:i + chunk], zi = signal.sosfilt(sos, x[i:i + chunk], zi=zi)
    return out
def sat(x, k=1.0): return np.tanh(x * k) / math.tanh(k)
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
NOTE = {'C': 60, 'C#': 61, 'D': 62, 'D#': 63, 'E': 64, 'F': 65, 'F#': 66, 'G': 67, 'G#': 68, 'A': 69, 'A#': 70, 'B': 71}

class Mix:
    def __init__(self, dur): self.n = sec(dur) + SR; self.L = np.zeros(self.n); self.R = np.zeros(self.n)
    def add(self, x, t, gain=1.0, pan=0.0, xr=None):
        """x mono (o par L/R con xr). pan -1..1."""
        i = sec(t); 
        if i >= self.n or i < 0: return
        x = np.asarray(x); m = min(len(x), self.n - i)
        gl, gr = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        self.L[i:i + m] += x[:m] * gain * gl
        self.R[i:i + m] += (xr[:m] if xr is not None else x[:m]) * gain * gr
    def stereo(self): return np.stack([self.L, self.R], 1)

def reverb_ir(seconds=1.9, bright=0.35):
    n = sec(seconds); t = t_axis(n)
    ir = np.stack([noise(n), noise(n)], 1) * np.exp(-t / (seconds / 4.2))[:, None]
    ir[:, 0] = lp(ir[:, 0], 8500); ir[:, 1] = lp(ir[:, 1], 8500)
    # cola más oscura: segunda capa filtrada
    ir = ir * (1 - bright) + np.stack([lp(ir[:, 0], 1800), lp(ir[:, 1], 1800)], 1) * bright
    ir[:sec(0.012)] *= 0  # pre-delay
    # normalizar por energía: una entrada tipo ruido sale con ganancia unitaria
    return ir / np.sqrt(np.sum(ir ** 2, 0))
IR = reverb_ir()
def reverb(st, amount):
    out = np.zeros_like(st)
    for c in range(2): out[:, c] = signal.fftconvolve(st[:, c], IR[:, c])[:len(st)]
    return st + out * amount

# ---------- instrumentos ----------
def kick(punch=1.0):
    n = sec(0.45); t = t_axis(n)
    f = 42 + 150 * np.exp(-t / 0.045) * punch
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t / 0.16)
    click = hp(noise(sec(0.004)), 2500) * 0.5; x[:len(click)] += click * np.linspace(1, 0, len(click))
    return sat(x * 1.6, 1.5) * 0.9

def hat(decay=0.035, open_=False):
    n = sec(0.35 if open_ else 0.08); x = hp(noise(n), 6500, 4) * env_exp(n, 0.12 if open_ else decay)
    return x * 0.5

def rim():
    n = sec(0.05); t = t_axis(n)
    x = np.sin(2 * np.pi * 1750 * t) * env_exp(n, 0.006) + bp(noise(n), 2500, 9000) * env_exp(n, 0.008)
    return x * 0.5

def clap():
    n = sec(0.35); x = np.zeros(n)
    for k, off in enumerate([0, 0.011, 0.022, 0.034]):
        i = sec(off); m = n - i; x[i:] += bp(noise(m), 900, 5200, 2) * env_exp(m, 0.012 if k < 3 else 0.14) * (0.8 if k < 3 else 1)
    return x * 0.55

def sub_note(note, dur):
    n = sec(dur); t = t_axis(n); f = midi(note)
    x = np.sin(2 * np.pi * f * t) + 0.18 * np.sin(2 * np.pi * 2 * f * t)
    return sat(x, 1.3) * env_adsr(n, 0.004, 0.05, 0.85, 0.06) * 0.62

def bass_note(note, dur):
    n = sec(dur); t = t_axis(n); f = midi(note)
    saw = 2 * ((f * t) % 1) - 1
    x = lp(saw, 700) * 0.6 + np.sin(2 * np.pi * f * t) * 0.5
    return sat(x, 2.0) * env_adsr(n, 0.004, 0.08, 0.7, 0.05) * 0.55

def pad_chord(notes, dur, cutoff):
    n = sec(dur); t = t_axis(n); L = np.zeros(n); R = np.zeros(n)
    for nt in notes:
        f = midi(nt)
        for det, side in [(-7, 'L'), (7, 'R'), (0, 'B')]:
            ff = f * 2 ** (det / 1200); saw = 2 * ((ff * t + rng.random()) % 1) - 1
            if side in 'LB': L += saw * (0.5 if side == 'B' else 1)
            if side in 'RB': R += saw * (0.5 if side == 'B' else 1)
    # filtro que abre con la envolvente
    e = env_adsr(n, 0.35, 0.4, 0.8, 0.5)
    L = sweep_filter(L, cutoff * 0.5, cutoff, 'low', 1024) * e; R = sweep_filter(R, cutoff * 0.5, cutoff, 'low', 1024) * e
    g = 0.26 / max(1, len(notes))
    return L * g, R * g

def pluck(note, dur=0.5, bright=0.55):
    """Karplus-Strong simple."""
    f = midi(note); N = int(SR / f); n = sec(dur)
    buf = (noise(N) * 0.5); buf = lp(buf, 6000); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % N]
        j = (i + 1) % N
        buf[i % N] = (bright * buf[i % N] + (1 - bright) * buf[j]) * 0.996 if False else 0.996 * (0.5 * buf[i % N] + 0.5 * buf[j])
    return out * env_adsr(n, 0.001, 0.02, 1.0, 0.05) * 0.5

def crash(dur=1.6):
    n = sec(dur); return hp(noise(n), 5000, 2) * env_exp(n, dur / 4) * 0.35

def reverse_swell(dur=0.6):
    n = sec(dur); x = hp(noise(n), 3000) * (np.linspace(0, 1, n) ** 3); return x * 0.4

# ---------- SFX ----------
def sfx_impact(gain=1.0, hi=False):
    if hi:
        n = sec(0.32); t = t_axis(n)
        f = 90 + 260 * np.exp(-t / 0.03); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.07)
        x += bp(noise(n), 1500, 6000) * env_exp(n, 0.03) * 0.8
        return sat(x, 1.5) * 0.7 * gain
    n = sec(1.1); t = t_axis(n)
    f = 26 + 70 * np.exp(-t / 0.08); boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.33)
    body = lp(noise(n), 420) * env_exp(n, 0.09) * 1.4
    crack = hp(noise(sec(0.02)), 1800) * env_exp(sec(0.02), 0.004) * 0.9
    x = boom * 1.2 + body; x[:len(crack)] += crack
    return sat(x, 1.8) * 0.95 * gain

def sfx_whoosh(length=0.5, soft=False):
    n = sec(length + 0.15); x = noise(n)
    x = sweep_filter(x, 250, 3800 if not soft else 2200, 'band' if False else 'low', 256)
    x = sweep_filter(x, 120, 900, 'high', 256)
    e = np.sin(np.linspace(0, np.pi, n)) ** (1.6 if soft else 1.1)
    x = x * e
    pan = np.linspace(-1, 1, n)
    L = x * np.cos((pan + 1) * np.pi / 4); R = x * np.sin((pan + 1) * np.pi / 4)
    g = 0.42 if soft else 0.62
    return L * g, R * g

def sfx_riser(length=0.5):
    n = sec(length); t = t_axis(n)
    x = sweep_filter(noise(n), 400, 6000, 'high', 256) * (np.linspace(0, 1, n) ** 2.2)
    f = np.geomspace(180, 1400, n); x += np.sin(2 * np.pi * np.cumsum(f) / SR) * (np.linspace(0, 1, n) ** 3) * 0.35
    return x * 0.45

def sfx_tick(pitch=1.0, vel=1.0):
    n = sec(0.03); t = t_axis(n)
    x = np.sin(2 * np.pi * 1900 * pitch * t) * env_exp(n, 0.006) + hp(noise(n), 4000) * env_exp(n, 0.0025) * 0.6
    return x * 0.33 * vel

def sfx_ticks(length=0.8, rate=24):
    n = sec(length + 0.05); x = np.zeros(n); k = int(length * rate)
    for i in range(k):
        s = sfx_tick(1 + 0.25 * i / max(1, k), 0.6 + 0.4 * rng.random()); j = sec(i / rate); m = min(len(s), n - j); x[j:j + m] += s[:m]
    return x

def sfx_blip(up=True):
    n = sec(0.11); t = t_axis(n)
    f = np.geomspace(720, 1180, n) if up else np.geomspace(1000, 700, n)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_adsr(n, 0.004, 0.03, 0.5, 0.05)
    x += np.sin(2 * np.pi * np.cumsum(f * 2) / SR) * env_exp(n, 0.02) * 0.25
    return x * 0.3

def sfx_pop():
    n = sec(0.09); t = t_axis(n); f = np.geomspace(260, 640, n)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.025)
    x[:sec(0.004)] += hp(noise(sec(0.004)), 3000) * 0.5
    return x * 0.45

def sfx_typing(n_keys=14, cps=34):
    n = sec(n_keys / cps + 0.05); x = np.zeros(n)
    for i in range(n_keys):
        s = hp(noise(sec(0.012)), 3500) * env_exp(sec(0.012), 0.002) * (0.5 + 0.5 * rng.random()); j = sec(i / cps + rng.random() * 0.004)
        m = min(len(s), n - j); x[j:j + m] += s[:m]
    return x * 0.3

def sfx_warn():
    n = sec(0.33); x = np.zeros(n); t = t_axis(sec(0.1))
    buzz = lp(signal.square(2 * np.pi * 165 * t), 1400) * env_adsr(sec(0.1), 0.004, 0.02, 0.8, 0.03)
    x[:len(buzz)] += buzz; j = sec(0.15); x[j:j + len(buzz)] += buzz
    return x * 0.22

def sfx_strike():
    n = sec(0.32); x = sweep_filter(noise(n), 2600, 500, 'band' if False else 'low', 256); x = hp(x, 700)
    return x * np.sin(np.linspace(0, np.pi, n)) ** 0.7 * 0.5

def sfx_engine(length=3.5, ramp=None):
    """Arranque (crank) y ralentí de motor de combustión, sintético."""
    n = sec(length); t = t_axis(n); x = np.zeros(n)
    # crank: 4 golpes
    for i in range(4):
        j = sec(0.11 * i); m = sec(0.09); seg = lp(noise(m), 500) * env_exp(m, 0.02) * 1.2 + np.sin(2 * np.pi * 65 * t_axis(m)) * env_exp(m, 0.03)
        x[j:j + m] += seg
    t0 = 0.5
    f0 = np.full(n, 29.0)
    if ramp:
        # subidas de carga: frecuencia de explosiones y nivel suben
        r = np.array(ramp) - ramp[0]
        for k, rt in enumerate(r[1:], 1): f0 += np.where(t > rt, 3.0, 0)
    ph = np.cumsum(f0) / SR
    pulses = np.exp(-((ph % 1) / 0.12) ** 2)  # tren de explosiones
    tone = lp(signal.sawtooth(2 * np.pi * ph), 380) * 0.8 + lp(noise(n), 900) * pulses * 1.5 + np.sin(2 * np.pi * f0 * t) * 0.5
    tone = tone * (1 + 0.15 * np.sin(2 * np.pi * 7.3 * t)) * (f0 / 29.0) ** 1.6
    gate = np.clip((t - t0) / 0.5, 0, 1) * np.clip((length - t) / 0.5, 0, 1)
    x += lp(tone, 2200) * gate * 0.5
    return sat(x, 1.2) * 0.42

def sfx_hum(length=2.0):
    n = sec(length); t = t_axis(n)
    x = np.sin(2 * np.pi * 50 * t) * 0.6 + np.sin(2 * np.pi * 100 * t) * 0.25 + np.sin(2 * np.pi * 150 * t) * 0.18
    x += bp(noise(n), 2500, 4500) * 0.05 * (1 + 0.5 * np.sin(2 * np.pi * 100 * t))
    e = np.clip(t / 0.4, 0, 1) * np.clip((length - t) / 0.5, 0, 1)
    return x * e * 0.28

def sfx_sting(root):
    """Golpe final de marca: acorde + sub + shimmer."""
    n = sec(2.6); t = t_axis(n)
    chord = [root, root + 7, root + 12, root + 14, root + 19]
    L, R = pad_chord(chord, 2.6, 5200)
    e = env_adsr(n, 0.01, 0.9, 0.35, 1.2); L = L * e * 9; R = R * e * 9
    sub = sub_note(root - 12, 1.6) * 0.9
    shim = sweep_filter(noise(n), 9000, 1500, 'high', 512) * env_exp(n, 0.5) * 0.12
    m = len(sub); L[:m] += sub; R[:m] += sub
    return L + shim, R + shim

# ---------- música ----------
def render_music(mix, music, dur):
    bpm = music.get('bpm', 104); beat = 60 / bpm; bar = beat * 4
    root = NOTE.get(music.get('root', 'D'), 62) - 12  # bajo en octava grave (C3 ~ 48)
    sections = music.get('sections', [[0, dur, 'full']])
    def energy_at(t):
        for a, b, name in sections:
            if a <= t < b: return name
        return 'outro'
    # progresión i – VI – VII – i (menor) por compás
    prog = [[0, 3, 7], [8, 12, 15], [10, 14, 17], [0, 3, 7]]
    kicks = []
    nbars = int(dur / bar) + 2
    for b in range(nbars):
        tb = b * bar; chord = prog[b % 4]; name = energy_at(tb + 0.01)
        if name == 'outro' and tb > dur - 0.2: continue
        # pad
        cutoff = {'hook': 420, 'build': 1400, 'full': 4800, 'outro': 5200}[name]
        pL, pR = pad_chord([root + 12 + c for c in chord], bar + 0.4, cutoff)
        pad_gain = {'hook': 0.8, 'build': 1.0, 'full': 1.15, 'outro': 1.1}[name]
        mix.add(pL, tb, pad_gain, 0, pR)
        # batería y bajo
        for s in range(16):
            ts = tb + s * beat / 4; nm = energy_at(ts)
            if ts >= dur: break
            on_beat = s % 4 == 0; eighth = s % 2 == 0
            if nm == 'hook':
                if s == 0: mix.add(sub_note(root + chord[0], beat * 1.5), ts, 0.9); kicks.append(ts); mix.add(kick(0.8), ts, 0.7)
                if eighth and s % 4 == 2: mix.add(hat(0.02), ts, 0.25, 0.3)
            elif nm == 'build':
                if s in (0, 8): mix.add(kick(), ts, 0.95); kicks.append(ts)
                if s in (6, 14): mix.add(kick(0.7), ts, 0.5); kicks.append(ts)
                if eighth: mix.add(hat(0.03 if s % 4 else 0.05), ts, 0.3 if s % 4 else 0.45, 0.35)
                if s in (3, 11): mix.add(rim(), ts, 0.35, -0.4)
                if s in (0, 3, 6, 8, 11, 14): mix.add(bass_note(root + chord[0] + (12 if s in (3, 11) else 0), beat / 2 * 0.9), ts, 0.8)
                if s in (2, 10): mix.add(pluck(root + 24 + chord[(s // 2) % 3], 0.4), ts, 0.35, -0.3 if s == 2 else 0.3)
            elif nm == 'full':
                if on_beat: mix.add(kick(), ts, 1.0); kicks.append(ts)
                if s in (4, 12): mix.add(clap(), ts, 0.7)
                if s in (3, 7, 11, 15): mix.add(rim(), ts, 0.3, -0.4 if s % 8 == 3 else 0.4)
                mix.add(hat(0.03 if s % 4 else 0.06), ts, (0.42 if s % 4 == 0 else 0.22 if s % 2 else 0.32), 0.35)
                if s % 4 == 2: mix.add(hat(open_=True), ts, 0.2, -0.3)
                if s % 2 == 0: mix.add(bass_note(root + chord[0] + (12 if s % 8 == 6 else 0), beat / 2 * 0.95), ts, 0.85)
                arp = [0, 1, 2, 1, 0, 2, 1, 2]; nt = root + 24 + chord[arp[s % 8]] + (12 if s >= 8 and s % 3 == 0 else 0)
                mix.add(pluck(nt, 0.35), ts, 0.3, 0.45 * math.sin(s)); mix.add(pluck(nt, 0.35), ts + beat * 3 / 8, 0.14, -0.5)
            elif nm == 'outro':
                if s == 0 and b * bar < dur - 2.6: mix.add(kick(), ts, 0.8); kicks.append(ts)
                if eighth and s % 4 == 2: mix.add(hat(0.02), ts, 0.2, 0.3)
                if s == 0: mix.add(sub_note(root + chord[0], beat * 3), ts, 0.7)
        # transiciones: swell antes de cada cambio de sección y crash al entrar en 'full'
    for a, b, name in sections:
        if a > 0: mix.add(reverse_swell(0.55), a - 0.55, 0.5)
        if name == 'full': mix.add(crash(1.4), a, 0.4, 0.2)
    return kicks

def sidechain(st, kicks, depth=0.62, rel=0.22):
    n = len(st); env = np.ones(n); m = sec(rel + 0.02); t = t_axis(m)
    duck = 1 - depth * np.exp(-t / (rel / 3)) * (t > 0.0)
    duck[:sec(0.005)] = np.linspace(1, 1 - depth, sec(0.005))
    for k in kicks:
        i = sec(k); j = min(n, i + m); env[i:j] = np.minimum(env[i:j], duck[:j - i])
    return st * env[:, None]

def render(name):
    tl = json.load(open(f'salida/{name}.timeline.json'))
    dur = tl['dur']; music = tl.get('music', {}); events = tl['events']
    root_mid = NOTE.get(music.get('root', 'D'), 62) - 12
    # --- música ---
    mus = Mix(dur); kicks = render_music(mus, music, dur)
    m_st = mus.stereo(); m_st = sidechain(m_st, kicks)
    m_st = reverb(m_st, 0.22)
    # salida: la música baja bajo el sting final
    # --- SFX ---
    fx = Mix(dur); fx_dry = Mix(dur)
    for e in events:
        t, k = e['t'], e['kind']
        if k == 'impact': fx.add(sfx_impact(e.get('gain', 1), e.get('hi', False)), t, 1.0)
        elif k == 'whoosh': L, R = sfx_whoosh(e.get('len', 0.5), e.get('soft', False)); fx.add(L, t, 1.0, 0, R)
        elif k == 'riser': fx.add(sfx_riser(e.get('len', 0.5)), t, 1.0)
        elif k == 'ticks': fx_dry.add(sfx_ticks(e.get('len', 0.8), e.get('rate', 24)), t, 1.0, 0.25)
        elif k == 'tick': fx_dry.add(sfx_tick(), t, 1.0, 0.25)
        elif k == 'blip': fx.add(sfx_blip(e.get('up', True)), t, 1.0, -0.2)
        elif k == 'pop': fx.add(sfx_pop(), t, 1.0, 0.3)
        elif k == 'typing': fx_dry.add(sfx_typing(e.get('n', 14)), t, 1.0, -0.4)
        elif k == 'warn': fx.add(sfx_warn(), t, 1.0)
        elif k == 'strike': fx.add(sfx_strike(), t, 1.0, -0.1)
        elif k == 'engine': fx_dry.add(sfx_engine(e.get('len', 3.5), e.get('ramp')), t, 1.0)
        elif k == 'hum': fx_dry.add(sfx_hum(e.get('len', 2.0)), t, 1.0)
        elif k == 'sting': L, R = sfx_sting(root_mid + 12); fx.add(L, t, 1.0, 0, R)
    f_st = reverb(fx.stereo(), 0.3) + fx_dry.stereo()
    # ducking de música en impactos fuertes y sting
    n = len(m_st); env = np.ones(n)
    for e in events:
        if e['kind'] == 'impact' and not e.get('hi') and e.get('gain', 1) >= 0.8:
            i = sec(e['t']); m = sec(0.5); j = min(n, i + m); env[i:j] = np.minimum(env[i:j], 1 - 0.5 * np.exp(-t_axis(j - i) / 0.12))
        if e['kind'] == 'sting':
            i = sec(e['t']); env[i:] = np.minimum(env[i:], np.clip(1 - t_axis(n - i) / 0.25, 0.35, 1))
    m_st = m_st * env[:, None]
    # fade final
    out = m_st * 0.95 + f_st * 1.0
    out = out[:sec(dur)]
    tail = sec(0.35); out[-tail:] *= np.linspace(1, 0, tail)[:, None]
    # master: compresión suave + limitador
    out = out - np.mean(out, 0)
    for c in range(2):
        out[:, c] = hp(out[:, c], 28) + hp(out[:, c], 3000) * 0.9 + hp(out[:, c], 9000) * 0.5
    out = sat(out * 1.1, 1.4)
    out = out / max(1e-6, np.max(np.abs(out))) * 0.92
    wavfile.write(f'salida/{name}.wav', SR, (out * 32767).astype(np.int16))
    print(f'[{name}] audio {dur}s · {len(events)} eventos · {len(kicks)} kicks')

if __name__ == '__main__':
    for name in sys.argv[1:]: render(name)
