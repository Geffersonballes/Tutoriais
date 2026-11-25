"""Áudio do vídeo: trilha original gerada por código (sem direitos de terceiros), efeitos e tratamento de voz.

Uso pelo compor.py:  trilha(dur, clima, marcos) -> numpy estéreo;  efeitos(...) -> numpy estéreo
Uso avulso (teste):  python3 audio.py <saida.wav> <clima> <duracao_s>

Climas (ver CLIMAS): curioso (games/explicação), tenso (guerra), epico (revelação/grandeza), divertido (leve/meme).
Toda a trilha é síntese própria (osciladores + ruído), então pode ser usada e vendida sem licença.
"""
import sys, wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
rng = np.random.default_rng(7)

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def lp(x, fc, o=2): return sosfilt(butter(o, min(fc, SR * 0.45), "low", fs=SR, output="sos"), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, "high", fs=SR, output="sos"), x)
def bp(x, f1, f2): return sosfilt(butter(2, [f1, f2], "band", fs=SR, output="sos"), x)

def env(n, a=0.005, r=0.2, sus=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    if sus is None:
        e *= np.exp(-t / max(r, 1e-3))
    else:
        rel = np.clip((t - sus) / max(r, 1e-3), 0, 1)
        e *= 1 - rel
    return e

def saw(f, n, det=0.0):
    t = np.arange(n) / SR
    s = np.zeros(n)
    for d in (-det, 0, det) if det else (0,):
        ph = (t * f * (1 + d)) % 1.0
        s += 2 * ph - 1
    return s / (3 if det else 1)

def sine(f, n, ph=0): return np.sin(2 * np.pi * f * np.arange(n) / SR + ph)

# ---------- instrumentos ----------
def kick(forte=1.0):
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    s += 0.25 * lp(rng.standard_normal(n), 2500) * np.exp(-t * 120)
    return np.tanh(s * 1.6 * forte)

def chimbal(aberto=False):
    n = int((0.25 if aberto else 0.06) * SR)
    return hp(rng.standard_normal(n), 7000) * env(n, 0.001, 0.08 if aberto else 0.018) * 0.2

def palma():
    n = int(0.25 * SR); s = bp(rng.standard_normal(n), 900, 4000)
    e = np.zeros(n)
    for k, d in enumerate((0, 0.011, 0.022)):
        i = int(d * SR); e[i:] += env(n - i, 0.001, 0.012 if k < 2 else 0.09)
    return s * e * 0.6

def tambor_grave():
    n = int(1.2 * SR); t = np.arange(n) / SR
    f = 55 + 40 * np.exp(-t * 10)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    s += 0.35 * lp(rng.standard_normal(n), 400) * np.exp(-t * 9)
    return np.tanh(s * 1.4)

def pad(notas, n, brilho=1800):
    s = sum(saw(mtof(m), n, det=0.006) for m in notas) / len(notas)
    s = lp(s, brilho)
    return s * env(n, a=min(0.4, n / SR / 3), r=min(0.5, n / SR / 3), sus=n / SR - min(0.5, n / SR / 3)) * 0.5

def baixo(m, n, tipo="sub"):
    if tipo == "sub":
        s = sine(mtof(m), n) + 0.3 * np.tanh(3 * sine(mtof(m), n))
    else:
        s = lp(saw(mtof(m), n), 600)
    return s * env(n, 0.005, 0.0, sus=n / SR - 0.03) * 0.55 if n > SR * 0.04 else np.zeros(n)

def pluck(m, n):
    s = lp(saw(mtof(m), n) + 0.5 * saw(mtof(m + 12), n), 3200)
    return s * env(n, 0.002, 0.22) * 0.35

# ---------- climas ----------
MAIOR = [0, 2, 4, 5, 7, 9, 11]; MENOR = [0, 2, 3, 5, 7, 8, 10]
CLIMAS = {
    "curioso":   dict(bpm=100, raiz=57, escala=MAIOR, prog=[0, 5, 3, 4], kit="leve",   lead=True,  baixo="sub",  brilho=1600),
    "divertido": dict(bpm=116, raiz=60, escala=MAIOR, prog=[0, 4, 5, 3], kit="palma",  lead=True,  baixo="saw",  brilho=2200),
    "tenso":     dict(bpm=88,  raiz=50, escala=MENOR, prog=[0, 0, 5, 6], kit="tambor", lead=False, baixo="pulso", brilho=900),
    "epico":     dict(bpm=120, raiz=50, escala=MENOR, prog=[0, 5, 2, 6], kit="forte",  lead=True,  baixo="saw",  brilho=2600),
}

def acorde(c, grau, oit=0):
    esc = c["escala"]
    return [c["raiz"] + 12 * oit + esc[(grau + k) % 7] + 12 * ((grau + k) // 7) for k in (0, 2, 4)]

def por(dst, src, i, g=1.0):
    if i >= len(dst) or i < 0: return
    m = min(len(src), len(dst) - i); dst[i:i + m] += src[:m] * g

def reverb(x, seg=1.6, mix=0.22):
    n = int(seg * SR); ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 4.0)
    ir = lp(ir, 5000); ir /= np.sqrt((ir ** 2).sum())
    return x * (1 - mix) + fftconvolve(x, ir)[:len(x)] * mix * 1.4

def trilha(dur, clima="curioso", entra=1.3, sai=None, respiros=()):
    """dur: duração total (s); entra: momento do 'drop' (fim da capa);
    sai: quando a batida para (pedido de like); respiros: instantes em que a bateria some por 1 tempo (viradas)."""
    c = CLIMAS[clima]; spb = 60 / c["bpm"]; compasso = 4 * spb
    n = int(dur * SR) + SR
    camada = {k: np.zeros(n) for k in ("pad", "bat", "bx", "lead")}
    sai = sai if sai is not None else dur
    t = 0.0; b = 0
    K, HH, HO, CL, TG = kick(1.0 if c["kit"] != "forte" else 1.2), chimbal(), chimbal(True), palma(), tambor_grave()
    while t < dur:
        grau = c["prog"][b % len(c["prog"])]
        ac = acorde(c, grau)
        i0 = int(t * SR); nc = int(compasso * SR)
        camada["pad"][i0:i0 + nc] += pad([m + 12 for m in ac] + [ac[0]], min(nc, n - i0), c["brilho"])[:max(0, min(nc, n - i0))]
        cheio = entra <= t < sai
        for bt in range(4):
            tb = t + bt * spb; ib = int(tb * SR)
            if tb >= dur: break
            batida = entra <= tb < sai and not any(r <= tb < r + spb for r in respiros)
            # baixo
            if cheio and tb < sai:
                if c["baixo"] == "pulso":
                    for k in range(2):
                        por(camada["bx"], baixo(ac[0] - 12, int(spb / 2 * SR * 0.9), "saw"), ib + int(k * spb / 2 * SR), 0.9)
                else:
                    por(camada["bx"], baixo(ac[0] - 12, int(spb * SR * 0.95), c["baixo"]), ib)
            if not batida: continue
            kit = c["kit"]
            if kit == "tambor":
                if bt in (0, 2): por(camada["bat"], TG, ib, 0.9 if bt == 0 else 0.6)
                por(camada["bat"], HH, ib + int(spb / 2 * SR), 0.25)
            else:
                if bt in (0, 2) or (kit == "forte" and bt == 3): por(camada["bat"], K, ib)
                if bt in (1, 3): por(camada["bat"], CL if kit in ("palma", "forte") else lp(CL, 2500) * 0.7, ib, 0.8)
                for k in range(2): por(camada["bat"], HO if (kit == "forte" and k == 1) else HH, ib + int(k * spb / 2 * SR), 0.6)
            # lead: arpejo em colcheias
            if c["lead"] and cheio:
                for k in range(2):
                    m = (ac + [ac[0] + 12])[(bt * 2 + k) % 4] + 12
                    por(camada["lead"], pluck(m, int(spb / 2 * SR)), ib + int(k * spb / 2 * SR), 0.8)
        t += compasso; b += 1
    # antes do drop: pad abafado; depois: aberto
    corte = int(entra * SR)
    camada["pad"][:corte] = lp(camada["pad"][:corte], 600)
    mix = camada["pad"] * 0.9 + camada["bx"] * 0.8 + camada["bat"] * 0.75 + camada["lead"] * 0.45
    mix = reverb(mix, mix=0.18)
    L = mix + 0.12 * np.roll(camada["lead"], 300); R = mix + 0.12 * np.roll(camada["pad"], 500)
    est = np.stack([L, R], 1)[:int(dur * SR)]
    # fade de entrada curto e saída
    f = np.ones(len(est)); fo = int(1.2 * SR); f[-fo:] = np.linspace(1, 0, fo); f[:int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
    est *= f[:, None]
    return est / (np.abs(est).max() + 1e-9) * 0.9

# ---------- efeitos ----------
def fx_whoosh(d=0.5):
    n = int(d * SR); x = rng.standard_normal(n); t = np.arange(n) / SR
    out = np.zeros(n); pedaco = 512
    for i in range(0, n, pedaco):
        fc = 400 + 5000 * (i / n)
        out[i:i + pedaco] = bp(x[max(0, i - 2048):i + pedaco], fc * 0.6, min(fc * 1.6, 18000))[-len(out[i:i + pedaco]):]
    return out * np.sin(np.pi * t / d) ** 2 * 0.5

def fx_impacto():
    n = int(1.4 * SR); t = np.arange(n) / SR
    f = 38 + 70 * np.exp(-t * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.5)
    s += 0.5 * lp(rng.standard_normal(n), 1200) * np.exp(-t * 14)
    return reverb(np.tanh(1.5 * s), seg=1.8, mix=0.3)

def fx_riser(d=1.5):
    n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); out = np.zeros(n); pedaco = 1024
    for i in range(0, n, pedaco):
        fc = 300 + 7000 * (i / n) ** 2
        out[i:i + pedaco] = bp(x[max(0, i - 4096):i + pedaco], fc * 0.7, min(fc * 1.4, 18000))[-len(out[i:i + pedaco]):]
    return out * (t / d) ** 2 * 0.6

def fx_bloop():
    n = int(0.16 * SR); t = np.arange(n) / SR
    f = 600 + 900 * (t / 0.16)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.05) * 0.5

def fx_ding():
    n = int(1.2 * SR)
    s = sum(sine(mtof(m), n) * a for m, a in ((84, 1), (91, 0.5), (96, 0.3)))
    return reverb(s * env(n, 0.002, 0.35) * 0.4, mix=0.3)

def efeitos(dur, cortes=(), pops=(), impacto=None, riser_ate=None, ding=None):
    n = int(dur * SR) + SR; m = np.zeros(n)
    W, B = fx_whoosh(), fx_bloop()
    for c in cortes: por(m, W, int((c - 0.25) * SR), 0.9)
    for p in pops: por(m, B, int(p * SR), 0.7)
    if impacto is not None: por(m, fx_impacto(), int(impacto * SR), 1.0)
    if riser_ate is not None:
        R = fx_riser(); por(m, R, int((riser_ate - len(R) / SR) * SR), 0.8)
    if ding is not None: por(m, fx_ding(), int(ding * SR), 0.8)
    m = m[:int(dur * SR)]
    return np.stack([m, m], 1)

def salvar(path, est):
    est = np.clip(est, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((est * 32767).astype("<i2").tobytes())

# cadeia de voz (ffmpeg): limpa graves, tira "embolado", dá presença, suaviza "s" e segura a dinâmica
VOZ_FILTRO = ("highpass=f=75,equalizer=f=220:t=q:w=1.2:g=-2.5,equalizer=f=3200:t=q:w=1.4:g=3,"
              "equalizer=f=9000:t=q:w=1:g=1.5,deesser=i=0.35:m=0.5:f=0.5,"
              "acompressor=threshold=-21dB:ratio=3:attack=6:release=120:makeup=2.5")

if __name__ == "__main__":
    out, clima, d = sys.argv[1], sys.argv[2], float(sys.argv[3])
    salvar(out, trilha(d, clima, entra=1.3, sai=d - 3) * 0.7 + efeitos(d, cortes=[8, 16], impacto=1.3, riser_ate=d - 3, ding=d - 2.5))
    print("OK", out)
