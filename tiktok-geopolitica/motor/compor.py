"""Compositor: frames do Blender + legenda palavra-a-palavra + rótulos + pílulas + CTA -> final.mp4
Uso: python3 compor.py <pasta_producao> <grafismos.json>"""
import json, os, sys, subprocess, re, math
from PIL import Image, ImageDraw, ImageFont

PASTA, GRAF = sys.argv[1], sys.argv[2]
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")
W, H, FPS = 1080, 1920, 30
G = json.load(open(GRAF, encoding="utf-8"))
LEG = json.load(open(os.path.join(PASTA, "legendas.json"), encoding="utf-8"))

def fonte(tam, peso="ExtraBold", italico=False):
    f = ImageFont.truetype(os.path.join(FONTS, "Montserrat-Italic[wght].ttf" if italico else "Montserrat[wght].ttf"), tam)
    pesos = {"Medium": 500, "SemiBold": 600, "Bold": 700, "ExtraBold": 800, "Black": 900}
    f.set_variation_by_axes([pesos[peso]]); return f

F_LEG = fonte(84); F_ROT = fonte(96, "Black", True); F_PIL = fonte(38, "ExtraBold"); F_SELO = fonte(26, "SemiBold")
F_CTA1 = fonte(46, "ExtraBold"); F_CTA2 = fonte(104, "Black"); F_FONTE = fonte(26, "Medium")
AMARELO = (255, 214, 10); VERM = (230, 45, 40); AZUL = (40, 140, 255); BRANCO = (255, 255, 255); PRETO = (0, 0, 0)

# ---------- palavras da legenda ----------
def tempo(seg, palavra, n=0):
    hits = [x["s"] for x in LEG if x["seg"] == seg and palavra.lower() in x["w"].lower()]
    return hits[min(n, len(hits) - 1)]

SUBST = G.get("subst", {"quatro": "4", "cem": "100", "I-F-F.": "IFF"})
palavras = []
pular = 0
for i, x in enumerate(LEG):
    if pular: pular -= 1; continue
    w = x["w"]; lw = re.sub(r"[^\wÀ-ÿ-]", "", w)
    LEGADO = "subst" not in G   # ajustes fixos do vídeo 01 só valem sem "subst" no grafismos.json
    if LEGADO and lw.lower() == "trinta": lw = "35"; pular = 2
    elif LEGADO and lw.lower() == "cinco" and x["seg"] == 5: lw = "5x"
    else: lw = SUBST.get(w, SUBST.get(lw.lower(), lw))
    if not lw: continue
    palavras.append({"w": lw[:1].upper() + lw[1:], "s": x["s"], "e": x["e"], "seg": x["seg"], "i": i})
# palavras-chave em amarelo: tudo depois de "Esse/Essa é" até o fim da frase + CTA
amarelas = set()
for k, p in enumerate(palavras):
    if p["w"] in ("Esse", "Essa") and k + 1 < len(palavras) and palavras[k + 1]["w"] in ("É", "é"):
        j = k + 2
        while j < len(palavras) and palavras[j]["seg"] == p["seg"]:
            amarelas.add(j); src = LEG[palavras[j]["i"]]["w"]
            if src.endswith((".", "?", "!")): break
            j += 1
for k, p in enumerate(palavras):
    if p["w"].lower() in ("general", "recruta", "antiaérea", "parabéns") or (p["seg"] == 11 and p["w"].lower() == "defesa"): amarelas.add(k)
for k in list(amarelas):
    if palavras[k]["w"].lower() in ("o", "a", "de", "em", "e"): amarelas.discard(k)

def resolver(t):
    """Aceita número ou ["seg", "palavra", n]."""
    if isinstance(t, (int, float)): return float(t)
    seg, pal = t[0], t[1]; n = t[2] if len(t) > 2 else 0; d = t[3] if len(t) > 3 else 0
    if pal == "@fim": return max(x["e"] for x in LEG if x["seg"] == seg) + d
    if pal == "@ini": return min(x["s"] for x in LEG if x["seg"] == seg) + d
    return tempo(seg, pal, n) + d

for item in G["rotulos"] + G["pilulas"]:
    item["_a"] = resolver(item["de"]); item["_b"] = resolver(item["ate"])

# ---------- desenho ----------
def texto_contorno(d, xy, txt, fnt, cor, contorno=8, anchor="mm"):
    d.text(xy, txt, font=fnt, fill=cor, anchor=anchor, stroke_width=contorno, stroke_fill=PRETO)

def escala_pop(t, a, dur=0.18):
    u = (t - a) / dur
    if u >= 1: return 1.0
    if u <= 0: return 0.0
    return 0.6 + 0.55 * math.sin(u * math.pi * 0.75) if u < 1 else 1

def camada_texto(txt, fnt, cor, contorno, escala):
    """Renderiza um texto numa camada própria para poder escalar (efeito pop)."""
    bb = fnt.getbbox(txt, stroke_width=contorno)
    im = Image.new("RGBA", (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - bb[0], 10 - bb[1]), txt, font=fnt, fill=cor, stroke_width=contorno, stroke_fill=PRETO)
    if escala != 1.0:
        im = im.resize((max(1, int(im.width * escala)), max(1, int(im.height * escala))), Image.LANCZOS)
    return im

def colar_centro(base, im, cx, cy):
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def pilula(txt, ponto, escala=1.0, fnt=None):
    fnt = fnt or F_PIL
    bb = fnt.getbbox(txt); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad, dot = 26, 22; w = tw + pad * 2 + dot + 16; h = th + 34
    im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 6, w + 4, h + 6), radius=h // 2, fill=(0, 0, 0, 90))
    d.rounded_rectangle((2, 2, w + 2, h + 2), radius=h // 2, fill=(255, 255, 255, 245))
    cor = VERM if ponto == "vermelho" else AZUL
    cy = 2 + h // 2; d.ellipse((pad, cy - dot // 2, pad + dot, cy + dot // 2), fill=cor)
    d.text((pad + dot + 16 - bb[0], cy - th // 2 - bb[1]), txt, font=fnt, fill=(25, 25, 25))
    if escala != 1.0: im = im.resize((max(1, int(im.width * escala)), max(1, int(im.height * escala))), Image.LANCZOS)
    return im

# Selo "Conteúdo gerado com IA" na tela: LIGADO (decisão do dono, 24/11), além de isAigc / isAiGeneratedContent no post.
SELO = None
if G.get("selo_ia", True):
    SELO = pilula("Conteúdo gerado com IA", "azul", fnt=F_SELO); SELO.putalpha(SELO.getchannel("A").point(lambda a: int(a * 0.55)))

# ---------- capa: título grande no meio nos primeiros segundos ----------
# O TikTok (conta pessoal) usa o 1º quadro como capa na grade do perfil; por isso o título entra no início
# do vídeo e some em fade. Em grafismos.json: "capa": {"linhas": ["33 KM", "QUE PODEM", "PARAR O MUNDO"],
# "destaque": [0], "dur": 1.3}. Linhas de destaque saem em amarelo; as outras em branco.
def camada_capa():
    c = G.get("capa")
    if not c: return None
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # faixa escura suave atrás do título (gradiente vertical)
    for y in range(int(H * 0.30), int(H * 0.62)):
        u = (y - H * 0.30) / (H * 0.32); a = int(150 * math.sin(math.pi * u))
        d.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    linhas = c["linhas"]; dest = set(c.get("destaque", [0]))
    tams = []
    for txt in linhas:
        tam = 190
        while tam > 60 and fonte(tam, "Black").getbbox(txt, stroke_width=12)[2] > W * 0.90: tam -= 6
        tams.append(tam)
    alt = sum(t * 1.08 for t in tams); y = H * 0.46 - alt / 2
    for txt, tam, i in zip(linhas, tams, range(len(linhas))):
        y += tam * 0.54
        texto_contorno(d, (W / 2, y), txt, fonte(tam, "Black"), AMARELO if i in dest else BRANCO, 12)
        y += tam * 0.54
    return im
CAPA = camada_capa()
CAPA_DUR = G.get("capa", {}).get("dur", 1.3)

# Pedido de like no final (decisão do dono, 24/11): voz + tela, LIGADO por padrão. "curtir": false desliga.
CURTIR = G.get("curtir", True)
CURTIR_FALA = G.get("curtir_fala", "Gostou do conteúdo? Então deixa o seu like!") if CURTIR else None
def _dur(a): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a], capture_output=True, text=True).stdout)
DUR_NARR = _dur(os.path.join(PASTA, "narracao.mp3"))

def overlay(t):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    if CAPA is not None and t < CAPA_DUR:
        f = min(1.0, (CAPA_DUR - t) / 0.3)
        cam = CAPA if f >= 1 else CAPA.copy()
        if f < 1: cam.putalpha(cam.getchannel("A").point(lambda a: int(a * f)))
        ov.alpha_composite(cam)
        if SELO is not None: ov.alpha_composite(SELO, (36, 60))
        return ov  # durante a capa, só o título (e o selo de IA)
    # selo IA
    if SELO is not None: ov.alpha_composite(SELO, (36, 60))
    # rótulos (nome do conceito)
    for r in G["rotulos"]:
        if r["_a"] <= t < r["_b"]:
            s = escala_pop(t, r["_a"], 0.25)
            colar_centro(ov, camada_texto(r["texto"], F_ROT if len(r["texto"]) < 14 else fonte(74, "Black", True), AMARELO, 9, s), W / 2, H * r.get("y", 0.22))
    # pílulas
    for p in G["pilulas"]:
        if p["_a"] <= t < p["_b"]:
            s = escala_pop(t, p["_a"])
            im = pilula(p["texto"], p["ponto"], s, fonte(p["tam"], "ExtraBold") if "tam" in p else None)
            colar_centro(ov, im, W * p.get("x", 0.5), H * p.get("y", 0.34))
    # fontes
    for fo in G.get("fontes", []):
        a, b = resolver(fo["de"]), resolver(fo["ate"])
        if a <= t < b:
            texto_contorno(d, (W / 2, H * 0.80), fo["texto"], F_FONTE, (235, 235, 235), 3)
    # pedido de like (depois da narração): só ele + marca, por cima de uma faixa escura
    if CURTIR and t >= DUR_NARR + 0.1:
        a = DUR_NARR + 0.1
        faixa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(faixa)
        fd.rectangle((0, int(H * 0.36), W, int(H * 0.60)), fill=(0, 0, 0, 150)); ov.alpha_composite(faixa)
        colar_centro(ov, camada_texto("GOSTOU DO CONTEÚDO?", F_CTA1, BRANCO, 6, escala_pop(t, a)), W / 2, H * 0.42)
        colar_centro(ov, camada_texto("DEIXA O LIKE", F_CTA2, AMARELO, 10, escala_pop(t, a + 0.4)), W / 2, H * 0.51)
        if SELO is not None: ov.alpha_composite(SELO, (36, 60))
        return ov
    # CTA final
    cta = G.get("cta")
    if cta:
        a1, a2 = resolver(cta["linha1"]), resolver(cta["linha2"])
        if t >= a1:
            colar_centro(ov, camada_texto(cta["t1a"], F_CTA1, BRANCO, 6, escala_pop(t, a1)), W / 2, H * 0.14)
            colar_centro(ov, camada_texto(cta["t1b"], F_CTA2, BRANCO, 10, escala_pop(t, a1 + 0.5)), W / 2, H * 0.205)
        if t >= a2:
            colar_centro(ov, camada_texto(cta["t2a"], F_CTA1, BRANCO, 6, escala_pop(t, a2)), W / 2, H * 0.28)
            colar_centro(ov, camada_texto(cta["t2b"], F_CTA2, (80, 170, 255), 10, escala_pop(t, a2 + 0.5)), W / 2, H * 0.345)
        if t >= resolver(cta["marca_de"]):
            im = pilula(cta["marca"], "vermelho", escala_pop(t, resolver(cta["marca_de"])), fonte(40, "ExtraBold"))
            colar_centro(ov, im, W / 2, H * 0.74)
    # legenda palavra-a-palavra
    atual = None
    for k, p in enumerate(palavras):
        if p["s"] <= t + 0.03:
            atual = k
        else:
            break
    if atual is not None:
        p = palavras[atual]
        prox = palavras[atual + 1]["s"] if atual + 1 < len(palavras) else p["e"] + 1.0
        if t < max(p["e"] + 0.35, prox - 0.02) and t < prox:
            cor = AMARELO if atual in amarelas else BRANCO
            colar_centro(ov, camada_texto(p["w"], F_LEG, cor, 9, escala_pop(t, p["s"], 0.12)), W / 2, H * 0.63)
    return ov

# ---------- áudio: narração + whooshes nos cortes ----------
def audio():
    """Voz tratada + trilha original por clima (abaixa sozinha quando a voz fala) + efeitos -> audio_mix.wav.
    grafismos.json: "trilha": {"clima": "curioso|tenso|epico|divertido", "volume": -16}  ou  "trilha": false"""
    import audio as AU
    narr = os.path.join(PASTA, "narracao.mp3"); out = os.path.join(PASTA, "audio_mix.wav")
    if CURTIR:
        cur = os.path.join(PASTA, "curtir.mp3")
        if not os.path.exists(cur):
            subprocess.run(["edge-tts", "--voice", "pt-BR-AntonioNeural", "--rate=+12%", "--text", CURTIR_FALA, "--write-media", cur], check=True)
        junto = os.path.join(PASTA, "narracao_com_like.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", narr, "-i", cur, "-filter_complex",
                        "[0]aresample=44100,apad=pad_dur=0.25[n];[1]aresample=44100,apad=pad_dur=1.2[c];[n][c]concat=n=2:v=0:a=1[a]",
                        "-map", "[a]", junto], check=True)
        narr = junto
    dur = _dur(narr)
    segs = range(1, max(x["seg"] for x in LEG) + 1)
    cortes = sorted(set(round(min(x["s"] for x in LEG if x["seg"] == s), 2) for s in segs))
    pops = [it["_a"] for it in G["rotulos"]]
    cfg = G.get("trilha", {})
    clima = (cfg or {}).get("clima") or ("curioso" if "serie-games" in os.path.abspath(PASTA) else "tenso")
    cta_ini = cortes[-1] if cortes else DUR_NARR
    fx = AU.efeitos(dur, cortes=cortes, pops=pops, impacto=CAPA_DUR if CAPA is not None else None,
                    riser_ate=cta_ini, ding=(DUR_NARR + 0.1) if CURTIR else None)
    fx_wav = os.path.join(PASTA, "efeitos.wav"); AU.salvar(fx_wav, fx * 0.3)
    inputs = ["-i", narr, "-i", fx_wav]
    fl = [f"[0]aresample=44100,{AU.VOZ_FILTRO},aformat=channel_layouts=stereo,asplit=2[v][sc]"]
    mix = "[v][1]"; n = 2
    if cfg is not False:
        mus_wav = os.path.join(PASTA, "trilha.wav")
        AU.salvar(mus_wav, AU.trilha(dur, clima, entra=CAPA_DUR if CAPA is not None else 0.0,
                                     sai=(DUR_NARR + 0.1) if CURTIR else dur, respiros=[c - 0.6 for c in cortes[1:]]))
        inputs += ["-i", mus_wav]
        fl.append(f"[2]volume={(cfg or {}).get('volume', -16)}dB[m0];[m0][sc]sidechaincompress=threshold=0.03:ratio=6:attack=25:release=350[m]")
        mix += "[m]"; n = 3
    else:
        fl.append("[sc]anullsink")
    fl.append(f"{mix}amix=inputs={n}:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(fl), "-map", "[a]", "-ar", "44100", out], check=True)
    return out

if __name__ == "__main__":
    frames = sorted(x for x in os.listdir(os.path.join(PASTA, "frames")) if x.endswith(".jpg"))
    so_preview = len(sys.argv) > 3
    if so_preview:
        for t in [float(v) for v in sys.argv[3].split(",")]:
            fr = os.path.join(PASTA, "frames", "f_%04d.jpg" % (int(round(t * FPS)) + 1))
            base = Image.open(fr).convert("RGBA").resize((W, H), Image.LANCZOS) if os.path.exists(fr) else Image.new("RGBA", (W, H), (90, 150, 230, 255))
            base.alpha_composite(overlay(t)); base.convert("RGB").save(os.path.join(PASTA, "preview", f"c_{t:06.2f}.jpg"), quality=88)
        sys.exit()
    aud = audio()
    out = os.path.join(PASTA, "final.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", aud, "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    dur_audio = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", aud], capture_output=True, text=True).stdout)
    # quadros podem ter sido renderizados com passo (ex.: 1 a cada 2): usa o último quadro disponível
    nums = sorted(int(x[2:6]) for x in frames)
    import bisect
    for k in range(int(dur_audio * FPS)):
        t = k / FPS
        nome = "f_%04d.jpg" % nums[max(0, bisect.bisect_right(nums, k + 1) - 1)]
        base = Image.open(os.path.join(PASTA, "frames", nome)).convert("RGBA").resize((W, H), Image.BICUBIC)
        base.alpha_composite(overlay(t))
        ff.stdin.write(base.convert("RGB").tobytes())
        if k == (0 if CAPA is not None else int(5.6 * FPS)): base.convert("RGB").save(os.path.join(PASTA, "capa.jpg"), quality=92)
    ff.stdin.close(); ff.wait()
    print("OK", out)
