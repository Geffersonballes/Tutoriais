"""Motor ILUSTRADO (estilo B): anima ilustrações geradas por IA e gera os quadros em <pasta>/frames/.
Depois, rode compor.py normalmente (legenda, rótulos, pílulas, CTA e áudio).

Uso: python3 ilustrado.py <pasta_producao> [preview t1,t2,...]
Lê <pasta>/tomadas.json:
{
  "tomadas": [
    {"img": "img/01.png", "de": [0, "@ini"], "mov": "zoom_in", "foco": [0.5, 0.5], "zoom": [1.0, 1.18],
     "efeitos": [
        {"tipo": "aneis",   "x": 0.3, "y": 0.6, "cor": "ciano", "de": [1, "grita"], "ate": [1, "Esse"]},
        {"tipo": "rastro",  "pts": [[0.9,0.2],[0.6,0.1],[0.4,0.3]], "cor": "branco", "de": 3.0, "ate": 4.2},
        {"tipo": "explosao","x": 0.4, "y": 0.3, "t": [0, "derrubar", 0, 1.2]},
        {"tipo": "seta",    "de_xy": [0.2,0.8], "para_xy": [0.5,0.5], "cor": "vermelho", "de": 5, "ate": 7},
        {"tipo": "pulso",   "x": 0.5, "y": 0.5, "cor": "amarelo", "de": 5, "ate": 7},
        {"tipo": "alvo",    "x": 0.5, "y": 0.5, "cor": "amarelo", "de": 5, "ate": 7}
     ]}
  ]
}
Coordenadas x, y são frações da ILUSTRAÇÃO (0..1). Tempos: segundos ou [cena, "palavra", n, deslocamento]
(também "@ini" / "@fim"), resolvidos com legendas.json — sempre sincronizados com a narração.
movimentos: zoom_in, zoom_out, pan_esq, pan_dir, pan_cima, pan_baixo, parado.
"""
import json, math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 1080, 1920, 30
PASTA = sys.argv[1]
LEG = json.load(open(os.path.join(PASTA, "legendas.json"), encoding="utf-8"))
CFG = json.load(open(os.path.join(PASTA, "tomadas.json"), encoding="utf-8"))
CORES = {"ciano": (80, 230, 255), "branco": (255, 255, 255), "vermelho": (240, 50, 40), "amarelo": (255, 214, 10),
         "laranja": (255, 140, 20), "verde": (60, 230, 110), "azul": (60, 140, 255)}
FIM = LEG[-1]["e"] + 1.2

def T(v):
    if isinstance(v, (int, float)): return float(v)
    seg, pal = v[0], v[1]; n = v[2] if len(v) > 2 else 0; d = v[3] if len(v) > 3 else 0
    xs = [x for x in LEG if x["seg"] == seg]
    if pal == "@ini": return (0.0 if seg == 0 else min(x["s"] for x in xs) - 0.12) + d
    if pal == "@fim": return max(x["e"] for x in xs) + d
    hits = [x["s"] for x in xs if pal.lower() in x["w"].lower()]
    if not hits: raise ValueError(f"palavra '{pal}' não está na cena {seg}")
    return hits[min(n, len(hits) - 1)] + d

def suave(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)

tomadas = CFG["tomadas"]
for i, tm in enumerate(tomadas):
    tm["_a"] = T(tm["de"])
for i, tm in enumerate(tomadas):
    tm["_b"] = tomadas[i + 1]["_a"] if i + 1 < len(tomadas) else FIM
    for ef in tm.get("efeitos", []):
        for k in ("de", "ate", "t"):
            if k in ef: ef["_" + k] = T(ef[k])

_cache = {}
def base_img(path):
    if path not in _cache:
        im = Image.open(os.path.join(PASTA, path)).convert("RGB")
        s = max(W / im.width, H / im.height)  # cobre o quadro 9:16
        _cache.clear(); _cache[path] = im.resize((math.ceil(im.width * s), math.ceil(im.height * s)), Image.LANCZOS)
    return _cache[path]

def janela(tm, t, bw, bh):
    """Ken Burns: devolve (x0, y0, z) — canto da janela e zoom."""
    u = suave((t - tm["_a"]) / max(0.01, tm["_b"] - tm["_a"]))
    mov = tm.get("mov", "zoom_in"); fx, fy = tm.get("foco", [0.5, 0.5])
    z0, z1 = tm.get("zoom", [1.0, 1.15] if mov != "zoom_out" else [1.15, 1.0])
    if mov == "zoom_out": z0, z1 = max(z0, z1), min(z0, z1)
    z = z0 + (z1 - z0) * u
    if mov.startswith("pan"):
        z = max(z0, z1, 1.12); d = 0.5 * (1 - 1 / z)
        off = {"pan_esq": (d - 2 * d * u, 0), "pan_dir": (-d + 2 * d * u, 0), "pan_cima": (0, d - 2 * d * u), "pan_baixo": (0, -d + 2 * d * u)}[mov]
        fx, fy = 0.5 + off[0], 0.5 + off[1]
    ww, wh = W / z, H / z
    cx, cy = fx * bw, fy * bh
    x0 = min(max(cx - ww / 2, 0), bw - ww); y0 = min(max(cy - wh / 2, 0), bh - wh)
    return x0, y0, z

def para_tela(px, py, bw, bh, x0, y0, z):
    return ((px * bw - x0) * z, (py * bh - y0) * z)

def bez(pts, u):
    while len(pts) > 1:
        pts = [((1 - u) * a[0] + u * b[0], (1 - u) * a[1] + u * b[1]) for a, b in zip(pts, pts[1:])]
    return pts[0]

def efeitos(ov, d, tm, t, conv, tremor):
    for ef in tm.get("efeitos", []):
        tp = ef["tipo"]; cor = CORES.get(ef.get("cor", "amarelo"), (255, 214, 10))
        if tp == "explosao":
            dt = t - ef["_t"]
            if 0 <= dt < 1.0:
                x, y = conv(ef["x"], ef["y"]); r0 = ef.get("r", 140)
                for k, (c, f) in enumerate([((255, 250, 220), 0.5), ((255, 200, 60), 0.8), ((255, 120, 30), 1.0)]):
                    r = r0 * f * (0.3 + 1.4 * dt); a = int(255 * max(0, 1 - dt * 1.3))
                    d.ellipse((x - r, y - r, x + r, y + r), fill=c + (a // (k + 1),))
                random.seed(int(ef["_t"] * 100))
                for _ in range(16):
                    ang = random.uniform(0, 2 * math.pi); v = random.uniform(0.6, 1.4) * r0 * 1.8 * dt
                    px, py = x + math.cos(ang) * v, y + math.sin(ang) * v + 200 * dt * dt
                    s = 10 * (1 - dt); d.ellipse((px - s, py - s, px + s, py + s), fill=(255, 170, 40, int(255 * (1 - dt))))
                if dt < 0.35: tremor[0] = max(tremor[0], 18 * (1 - dt / 0.35))
            continue
        if not (ef["_de"] <= t < ef["_ate"]): continue
        u = (t - ef["_de"]) / max(0.01, ef["_ate"] - ef["_de"])
        if tp == "aneis":
            x, y = conv(ef["x"], ef["y"]); per = ef.get("periodo", 0.9); rmax = ef.get("raio", 700); ach = ef.get("achatado", 0.4)
            for k in range(3):
                f = ((t - ef["_de"]) / per + k / 3) % 1.0
                r = rmax * f; a = int(220 * (1 - f))
                d.ellipse((x - r, y - r * ach, x + r, y + r * ach), outline=cor + (a,), width=7)
        elif tp == "rastro":
            pts = [conv(*p) for p in ef["pts"]]; n = 40; uu = suave(u) if ef.get("suave", True) else u
            trilha = [bez(pts, uu * i / n) for i in range(n + 1)]
            for i in range(1, len(trilha)):
                a = int(230 * (i / len(trilha)) ** 1.5)
                d.line([trilha[i - 1], trilha[i]], fill=(245, 245, 245, a), width=int(6 + 14 * i / len(trilha)))
            hx, hy = trilha[-1]
            d.ellipse((hx - 16, hy - 16, hx + 16, hy + 16), fill=cor + (255,))
            d.ellipse((hx - 30, hy - 30, hx + 30, hy + 30), outline=cor + (150,), width=4)
        elif tp == "seta":
            (x1, y1), (x2, y2) = conv(*ef["de_xy"]), conv(*ef["para_xy"]); g = suave(min(1, u * 2.5))
            ex, ey = x1 + (x2 - x1) * g, y1 + (y2 - y1) * g
            d.line([(x1, y1), (ex, ey)], fill=cor + (240,), width=16)
            ang = math.atan2(ey - y1, ex - x1); L = 46
            d.polygon([(ex + math.cos(ang) * 20, ey + math.sin(ang) * 20), (ex - math.cos(ang - 0.5) * L, ey - math.sin(ang - 0.5) * L),
                       (ex - math.cos(ang + 0.5) * L, ey - math.sin(ang + 0.5) * L)], fill=cor + (250,))
        elif tp == "pulso":
            x, y = conv(ef["x"], ef["y"]); f = ((t - ef["_de"]) * 1.4) % 1.0; r = ef.get("raio", 90) * (0.6 + f)
            d.ellipse((x - r, y - r, x + r, y + r), outline=cor + (int(255 * (1 - f)),), width=10)
            r2 = ef.get("raio", 90) * 0.55; d.ellipse((x - r2, y - r2, x + r2, y + r2), outline=cor + (230,), width=8)
        elif tp == "alvo":
            x, y = conv(ef["x"], ef["y"]); r = ef.get("raio", 70) * (1.6 - 0.6 * suave(min(1, u * 4)))
            d.ellipse((x - r, y - r, x + r, y + r), outline=cor + (240,), width=8)
            for a in range(4):
                c, s = math.cos(a * math.pi / 2), math.sin(a * math.pi / 2)
                d.line([(x + c * r * 0.6, y + s * r * 0.6), (x + c * r * 1.35, y + s * r * 1.35)], fill=cor + (240,), width=8)

def quadro(t):
    tm = next(x for x in tomadas if x["_a"] <= t < x["_b"]) if t >= tomadas[0]["_a"] else tomadas[0]
    b = base_img(tm["img"]); bw, bh = b.size
    x0, y0, z = janela(tm, t, bw, bh)
    tremor = [0.0]
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    efeitos(ov, d, tm, t, lambda px, py: para_tela(px, py, bw, bh, x0, y0, z), tremor)
    if tremor[0] > 0:
        random.seed(int(t * 1000)); x0 += random.uniform(-1, 1) * tremor[0] / z; y0 += random.uniform(-1, 1) * tremor[0] / z
        x0 = min(max(x0, 0), bw - W / z); y0 = min(max(y0, 0), bh - H / z)
    fr = b.crop((int(x0), int(y0), int(x0 + W / z), int(y0 + H / z))).resize((W, H), Image.BILINEAR).convert("RGBA")
    # flash curto no corte
    if t - tm["_a"] < 0.08 and tm is not tomadas[0]:
        fr = Image.blend(fr, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.35)
    fr.alpha_composite(ov)
    return fr.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "preview":
        os.makedirs(os.path.join(PASTA, "preview"), exist_ok=True)
        for t in [float(v) for v in sys.argv[3].split(",")]:
            quadro(t).save(os.path.join(PASTA, "preview", f"i_{t:06.2f}.jpg"), quality=88)
        sys.exit()
    out = os.path.join(PASTA, "frames"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    n = int(FIM * FPS)
    if len(sys.argv) > 2 and sys.argv[2] == "ate": n = int(float(sys.argv[3]) * FPS)  # render parcial para teste
    for k in range(n):
        quadro(k / FPS).save(os.path.join(out, "f_%04d.jpg" % (k + 1)), quality=92)
    print("FRAMES", n)
