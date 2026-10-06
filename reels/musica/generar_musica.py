"""Pistas musicales libres de derechos para los reels, sintetizadas con numpy.

Estilo: electrónico cinemático, 96 BPM (1 compás = 2,5 s). Golpe de impacto al inicio (hook),
transiciones con riser y crash en los cambios de escena, y fundido final.

Uso: python3 reels/musica/generar_musica.py            → genera todas las pistas (.m4a)
     python3 reels/musica/generar_musica.py 15.5 2    → duración y nº de pista
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 44100
BPM = 96
BEAT = 60 / BPM
BAR = BEAT * 4
OUT = Path(__file__).parent

# Notas MIDI → Hz
def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)

# ---- Herramientas de síntesis -------------------------------------------------------------
def t_axis(n):
    return np.arange(n) / SR

def exp_env(n, tau, hold=0.0):
    t = t_axis(n)
    return np.exp(-np.maximum(t - hold, 0) / tau)

def adsr(n, a, d, s, r, total):
    t = t_axis(n)
    env = np.zeros(n)
    env = np.where(t < a, t / max(a, 1e-6), env)
    env = np.where((t >= a) & (t < a + d), 1 - (1 - s) * (t - a) / max(d, 1e-6), env)
    env = np.where((t >= a + d) & (t < total - r), s, env)
    rel = (t >= total - r)
    env = np.where(rel, s * np.clip((total - t) / max(r, 1e-6), 0, 1), env)
    return env

def lowpass(x, cutoff, order=4):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / cutoff) ** (2 * order))
    return np.fft.irfft(X, len(x))

def highpass(x, cutoff, order=4):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    with np.errstate(divide="ignore"):
        g = 1 / np.sqrt(1 + (cutoff / np.maximum(f, 1e-9)) ** (2 * order))
    X *= g
    return np.fft.irfft(X, len(x))

def bandpass(x, lo, hi):
    return highpass(lowpass(x, hi), lo)

def reverb(x, decay=1.4, mix=0.25, predelay=0.02, rng=None):
    rng = rng or np.random.default_rng(7)
    n_ir = int(SR * decay * 3)
    ir = rng.standard_normal(n_ir) * np.exp(-t_axis(n_ir) / decay)
    ir = lowpass(ir, 6000)
    ir[: int(SR * predelay)] = 0
    ir /= np.sqrt(np.sum(ir ** 2)) * 4
    wet = np.fft.irfft(np.fft.rfft(x, len(x) + n_ir) * np.fft.rfft(ir, len(x) + n_ir))[: len(x)]
    return x * (1 - mix) + wet * mix

def delay(x, time, feedback=0.35, mix=0.3):
    d = int(time * SR)
    y = np.copy(x)
    buf = np.copy(x)
    for _ in range(5):
        buf = np.concatenate([np.zeros(d), buf[:-d]]) * feedback
        y += buf * mix
    return y

def saw(freq, n, detune_cents=(0,)):
    t = t_axis(n)
    out = np.zeros(n)
    for c in detune_cents:
        f = freq * 2 ** (c / 1200)
        ph = (t * f) % 1.0
        out += 2 * ph - 1
    return out / len(detune_cents)

def place(track, start_s, sig, gain=1.0):
    i = int(start_s * SR)
    j = min(i + len(sig), len(track))
    if i < len(track):
        track[i:j] += sig[: j - i] * gain

# ---- Instrumentos ------------------------------------------------------------------------
def kick(n=None):
    n = n or int(SR * 0.45)
    t = t_axis(n)
    f = 48 + 170 * np.exp(-t / 0.028)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.22)
    click = np.random.default_rng(1).standard_normal(n) * np.exp(-t / 0.004) * 0.5
    return np.tanh((body + click) * 1.6) * 0.95

def hat(open_=False, rng=None):
    rng = rng or np.random.default_rng(2)
    n = int(SR * (0.22 if open_ else 0.06))
    x = rng.standard_normal(n) * exp_env(n, 0.09 if open_ else 0.018)
    return bandpass(x, 6500, 15000) * 0.7

def clap(rng=None):
    rng = rng or np.random.default_rng(3)
    n = int(SR * 0.35)
    x = np.zeros(n)
    for k in range(3):
        burst = rng.standard_normal(n) * exp_env(n, 0.012)
        x += np.roll(burst, int(k * 0.011 * SR))
    x += rng.standard_normal(n) * exp_env(n, 0.09) * 0.6
    return bandpass(x, 900, 7000) * 0.8

def boom(n=None):
    n = n or int(SR * 1.6)
    t = t_axis(n)
    f = 38 + 60 * np.exp(-t / 0.08)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.tanh(np.sin(ph) * 2.2) * np.exp(-t / 0.55)

def crash(rng=None):
    rng = rng or np.random.default_rng(4)
    n = int(SR * 2.2)
    x = rng.standard_normal(n) * exp_env(n, 0.7)
    return highpass(x, 3000) * 0.35

def riser(dur, rng=None):
    rng = rng or np.random.default_rng(5)
    n = int(SR * dur)
    t = t_axis(n)
    x = rng.standard_normal(n)
    # barrido de banda: 300 Hz → 9 kHz, volumen creciente
    out = np.zeros(n)
    segs = 24
    for k in range(segs):
        a, b = k * n // segs, (k + 1) * n // segs
        c = 300 * (30 ** (k / (segs - 1)))
        out[a:b] = bandpass(x, c * 0.6, c * 1.6)[a:b]
    return out * (t / dur) ** 2 * 0.7

def bass_note(freq, dur, cutoff=260):
    n = int(SR * dur)
    x = saw(freq, n, (0, -4, 4)) * 0.6 + np.sin(2 * np.pi * freq * t_axis(n)) * 0.6
    x = lowpass(x, cutoff)
    return x * adsr(n, 0.006, 0.08, 0.8, 0.05, dur)

def pad_chord(freqs, dur, cutoff=1300):
    n = int(SR * dur)
    x = np.zeros(n)
    for f in freqs:
        x += saw(f, n, (-9, -3, 3, 9))
    x = lowpass(x / len(freqs), cutoff)
    return x * adsr(n, 0.9, 0.4, 0.85, 0.9, dur)

def pluck(freq, dur=0.5):
    n = int(SR * dur)
    t = t_axis(n)
    x = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t / 0.05) + 0.15 * np.sin(2 * np.pi * freq * 3 * t)
    return x * exp_env(n, 0.14) * 0.8

# ---- Arreglo -----------------------------------------------------------------------------
PROGRESSIONS = {
    # grados sobre la tónica menor: (bajo, acorde) por compás
    "A": [(0, (0, 3, 7, 14)), (-4, (-4, 0, 3, 10)), (-2, (-2, 2, 5, 10)), (-5, (-5, -2, 3, 7))],   # i · VI · VII · iv
    "B": [(0, (0, 3, 7, 10)), (-2, (-2, 2, 5, 12)), (-4, (-4, 0, 3, 7)), (-2, (-2, 2, 5, 9))],      # i · VII · VI · VII
    "C": [(0, (0, 3, 7, 12)), (3, (3, 7, 10, 14)), (-4, (-4, 0, 3, 10)), (-2, (-2, 2, 5, 10))],     # i · III · VI · VII
}

TRACKS = [
    # (nombre, tónica MIDI del bajo, progresión, patrón de bajo (corcheas), patrón de pluck (semicorcheas, índice de nota o None), densidad hats)
    ("pista-01", 45, "A", [1, 0, 1, 1, 0, 1, 0, 1], [0, None, 1, None, 2, None, 3, 2, None, 1, None, 2, None, 3, None, None], 1),
    ("pista-02", 43, "B", [1, 0, 0, 1, 0, 1, 1, 0], [None, 0, None, 1, None, 2, None, None, 3, None, 2, None, 1, None, None, 2], 2),
    ("pista-03", 40, "C", [1, 1, 0, 1, 0, 1, 0, 1], [0, 2, None, 3, None, 2, 1, None, 0, 2, None, 3, None, None, 1, None], 1),
    ("pista-04", 48, "A", [1, 0, 1, 0, 1, 0, 1, 1], [None, None, 0, None, 1, 2, None, 3, None, None, 2, None, 1, None, 0, None], 2),
    ("pista-05", 41, "B", [1, 0, 1, 1, 0, 0, 1, 0], [0, None, None, 1, None, None, 2, None, 3, None, None, 2, None, None, 1, None], 1),
    ("pista-06", 45, "C", [1, 0, 1, 0, 1, 1, 0, 1], [None, 0, 1, None, 2, None, 3, None, None, 2, 1, None, 0, None, 2, None], 2),
]

def render_track(name, root, prog_key, bass_pat, pluck_pat, hat_density, duration, hits_at):
    n = int(SR * (duration + 2.5))
    kick_tr = np.zeros(n); hat_tr = np.zeros(n); clap_tr = np.zeros(n)
    bass_tr = np.zeros(n); pad_tr = np.zeros(n); pluck_tr = np.zeros(n); fx_tr = np.zeros(n)
    prog = PROGRESSIONS[prog_key]
    bars = int(np.ceil(duration / BAR)) + 1
    k_sig, h_c, h_o, c_sig = kick(), hat(False), hat(True), clap()
    rng = np.random.default_rng(11)
    kick_times = []
    for bar in range(bars):
        t0 = bar * BAR
        bass_deg, chord = prog[bar % len(prog)]
        # batería
        for beat in range(4):
            tb = t0 + beat * BEAT
            if beat in (0, 2) or (beat == 3 and bar % 2 == 1):
                place(kick_tr, tb, k_sig); kick_times.append(tb)
            if beat in (1, 3):
                place(clap_tr, tb, c_sig, 0.9)
            for s in range(2 if hat_density == 1 else 4):
                ts = tb + s * BEAT / (2 if hat_density == 1 else 4)
                vel = 0.55 if s == 0 else (0.9 + 0.1 * rng.random())
                place(hat_tr, ts, h_c, vel * 0.8)
            if beat == 3:
                place(hat_tr, tb + BEAT / 2, h_o, 0.6)
        # bajo (corcheas)
        for i, on in enumerate(bass_pat):
            if on:
                place(bass_tr, t0 + i * BEAT / 2, bass_note(hz(root + bass_deg), BEAT / 2 * 0.95))
        # pad
        place(pad_tr, t0, pad_chord([hz(root + 12 + d) for d in chord], BAR * 1.02))
        # pluck (semicorcheas) con eco
        for i, idx in enumerate(pluck_pat):
            if idx is not None:
                deg = chord[idx % len(chord)]
                place(pluck_tr, t0 + i * BEAT / 4, pluck(hz(root + 36 + deg)))
    # impactos y transiciones
    for th in hits_at:
        if th > 0:
            place(fx_tr, max(th - BEAT * 1.5, 0), riser(BEAT * 1.5), 0.55)
        place(fx_tr, th, boom(), 0.7 if th == 0 else 0.4)
        place(fx_tr, th, crash(), 0.8 if th == 0 else 0.5)
    # sidechain: todo lo armónico se "agacha" con el bombo
    duck = np.ones(n)
    t = t_axis(n)
    for tk in kick_times:
        i = int(tk * SR)
        seg = slice(i, min(i + int(SR * 0.35), n))
        duck[seg] = np.minimum(duck[seg], 1 - 0.65 * np.exp(-(t[seg] - tk) / 0.11))
    pluck_tr = reverb(delay(pluck_tr, BEAT * 0.75, 0.38, 0.35), 1.6, 0.3)
    pad_tr = reverb(pad_tr, 2.2, 0.35)
    clap_tr = reverb(clap_tr, 1.0, 0.25)
    fx_tr = reverb(fx_tr, 1.8, 0.3)
    bass_tr = highpass(bass_tr, 42, 2)
    mix = (kick_tr * 0.6 + hat_tr * 0.75 + clap_tr * 0.6 + (bass_tr * 0.3 + pad_tr * 0.6 + pluck_tr * 0.72) * duck + fx_tr * 0.45)
    mix = highpass(mix, 30, 2)
    mix = np.tanh(mix * 0.9) / np.tanh(0.9)
    # recortar a la duración y fundir el final
    m = int(SR * duration)
    mix = mix[:m]
    fade = int(SR * 1.4)
    mix[-fade:] *= np.linspace(1, 0, fade) ** 1.5
    mix *= 0.8 / np.max(np.abs(mix))
    stereo = np.stack([mix, mix], axis=1).astype(np.float32)
    out = OUT / f"{name}.m4a"
    tmp = OUT / f".{name}.tmp.m4a"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "aac", "-b:a", "192k", "-f", "mp4", str(tmp)], input=stereo.tobytes(), check=True)
    tmp.replace(out)
    return out

if __name__ == "__main__":
    duration = float(sys.argv[1]) if len(sys.argv) > 1 else 15.5
    only = int(sys.argv[2]) if len(sys.argv) > 2 else None
    hits = [0, BAR, BAR * 3, BAR * 5]  # hook, revelación, detalle, cierre (compases 1, 2, 4, 6)
    for i, (name, root, prog, bp, pp, hd) in enumerate(TRACKS, 1):
        if only and i != only:
            continue
        print("→", render_track(name, root, prog, bp, pp, hd, duration, hits))
