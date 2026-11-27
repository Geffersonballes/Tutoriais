"""Vídeo 01 — açaí de R$ 20 no iFood. Uso: python3 render.py [segundo_de_teste]
Lê legendas.json (alinhar.py) e narracao.mp3; gera audio_mix.wav e final.mp4."""
import sys, os, json, re, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "motor"))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "..", "tiktok-geopolitica", "motor"))
from visual import *

FPS = 30
LEG = json.load(open(f"{AQUI}/legendas.json", encoding="utf-8"))
NSEG = max(x["seg"] for x in LEG) + 1
INI = {k: min(x["s"] for x in LEG if x["seg"] == k) for k in range(NSEG)}
FIM = {k: max(x["e"] for x in LEG if x["seg"] == k) for k in range(NSEG)}
DUR = FIM[NSEG - 1] + 1.6

def norm(w): return re.sub(r"[^\wÀ-ÿ]", "", w.lower())
def tw(seg, palavra, n=0):
    hits = [x["s"] for x in LEG if x["seg"] == seg and norm(x["w"]) == palavra]
    return hits[min(n, len(hits) - 1)] if hits else INI[seg]

# legenda: números por extenso viram algarismos curtos na tela
SUBST = [("vinte e três por cento", "23%"), ("três vírgula dois por cento", "3,2%"), ("quatro reais e sessenta", "R$ 4,60"),
         ("sessenta e quatro centavos", "64 centavos"), ("cento e cinquenta reais", "R$ 150"), ("oitenta e dois", "R$ 82"),
         ("cinco e quarenta e nove", "R$ 5,49"), ("vinte reais", "R$ 20"), ("sete reais", "R$ 7"), ("onze reais", "R$ 11"),
         ("um e cinquenta", "R$ 1,50"), ("oitenta centavos", "80 centavos"), ("trezentos", "300")]
PAL = []; i = 0
while i < len(LEG):
    feito = False
    for chave, val in SUBST:
        ps = chave.split()
        seq = LEG[i:i + len(ps)]
        if len(seq) == len(ps) and all(norm(a["w"]) == b for a, b in zip(seq, ps)):
            pont = re.sub(r"[\wÀ-ÿ]", "", seq[-1]["w"])
            PAL.append({"w": val + pont, "s": seq[0]["s"], "e": seq[-1]["e"]}); i += len(ps); feito = True; break
    if not feito:
        PAL.append({"w": LEG[i]["w"], "s": LEG[i]["s"], "e": LEG[i]["e"]}); i += 1

LINHAS = [("AÇAÍ 500 ML", 20, "base", INI[1]),
          ("COMISSÃO iFOOD 23%", 4.60, "menos", tw(1, "comissão")),
          ("TAXA PAGTO APP 3,2%", 0.64, "menos", tw(2, "mais")),
          ("POLPA + COMPLEMENTOS*", 7.00, "menos", tw(3, "polpa")),
          ("COPO, TAMPA, SACOLA*", 1.50, "menos", tw(3, "copo", 1)),
          ("MENSALIDADE + DAS / COPO", 0.77, "menos", tw(4, "dividindo"))]
FONTES = {0: "Fontes de cada número no rodapé", 1: "Fonte: Serasa e Diário do Pará (2026) · iFood Plano Entrega",
          2: "Fonte: Serasa e Diário do Pará (2026)", 3: "*Custo de exemplo: o seu pode ser diferente",
          4: "DAS 2026: Agência Brasil e O Povo · iFood: Serasa e Diário do Pará",
          5: "Sem contar luz, aluguel e mão de obra", 6: "Débito: 1% a 2% (tabelas InfinitePay e iDinheiro); usei 1,5%",
          7: "", 8: "Fontes: Serasa · Diário do Pará · Agência Brasil · O Povo · InfinitePay · iDinheiro"}

def chip_fonte(im, s, alfa=1.0):
    if not s: return
    d = ImageDraw.Draw(im); f = fonte(26, "Medium")
    w = d.textlength(s, font=f)
    if w > 940:
        f = fonte(22, "Medium"); w = d.textlength(s, font=f)
    x = (W - w) / 2
    d.rounded_rectangle([x - 22, 1508, x + w + 22, 1556], radius=24, fill=BG2, outline=CINZA2, width=2)
    d.text((x, 1516), s, font=f, fill=CINZA if alfa >= 1 else CINZA2)

def entra(t, t0, d=0.35): return ease((t - t0) / d)

def cena_gancho(im, t):
    d = ImageDraw.Draw(im)
    p = entra(t, 0, 0.5)
    icone_acai(im, W // 2, 560 + int(60 * (1 - p)), 1.25 * (0.8 + 0.2 * p), alfa=p)
    texto_centro(d, 820, "VENDEU NO iFOOD POR", fonte(46, "SemiBold"), CINZA)
    numero_grande(im, 900, 20, (t - 0.3) / 1.2, BRANCO, 200)
    if t >= tw(0, "quanto"):
        q = entra(t, tw(0, "quanto"))
        texto_centro(d, 1180 + int(30 * (1 - q)), "Quanto fica com você?", fonte(64, "ExtraBold"), AMBAR)

def cena_cupom(im, t):
    d = ImageDraw.Draw(im)
    prog = 0.0; sobra = 20.0
    for k, l in enumerate(LINHAS):
        if t >= l[3]:
            prog = k + min(1, (t - l[3]) / 0.5)
            if l[2] == "menos": sobra -= l[1] * min(1, (t - l[3]) / 0.5)
    fim = cupom(im, [l[:3] for l in LINHAS], prog, y=230)
    d.text((110, fim + 60), "SOBRANDO ATÉ AQUI", font=fonte(36, "SemiBold"), fill=CINZA)
    d.text((110, fim + 100), brl(max(sobra, 0)), font=fonte(150, "Black"), fill=VERDE if sobra > 10 else AMBAR)

def cena_resultado(im, t):
    d = ImageDraw.Draw(im); t0 = INI[5]
    texto_centro(d, 360, "DOS R$ 20, SOBRAM", fonte(54, "ExtraBold"), CINZA)
    p = entra(t, t0, 0.6)
    texto_centro(d, 450 - int(40 * (1 - p)), brl(5.49), fonte(230, "Black"), VERDE)
    itens = [("luz", tw(5, "luz")), ("aluguel", tw(5, "aluguel")), ("sua hora de trabalho", tw(5, "hora"))]
    texto_centro(d, 800, "e ainda falta pagar:", fonte(44, "Medium"), CINZA) if t >= tw(5, "antes") else None
    for k, (s, ts) in enumerate(itens):
        if t >= ts:
            q = entra(t, ts)
            y = 890 + k * 120
            texto_centro(d, y + int(20 * (1 - q)), "– " + s, fonte(72, "ExtraBold"), VERM)

def cena_comparacao(im, t):
    d = ImageDraw.Draw(im); t0 = INI[6]
    texto_centro(d, 330, "O MESMO AÇAÍ DE R$ 20", fonte(52, "ExtraBold"), BRANCO)
    texto_centro(d, 400, "quanto sobra para quem vende", fonte(38, "Medium"), CINZA)
    barras(im, [("iFood (entrega pelo app)", 5.49, VERM), ("Balcão, pago no débito", 10.93, VERDE)], (t - t0) / 1.6, y=560, maxv=11)
    tq = tw(6, "quase")
    if t >= tq:
        q = entra(t, tq, 0.25); f = fonte(int(110 * (0.7 + 0.3 * q)), "Black")
        texto_centro(d, 1150, "QUASE O DOBRO", f, AMBAR)

def etiqueta(im, cx, y, titulo, preco, cor, p):
    d = ImageDraw.Draw(im); y = y + int(50 * (1 - p))
    d.rounded_rectangle([cx - 210, y, cx + 210, y + 300], radius=28, fill=BG2, outline=cor, width=5)
    d.ellipse([cx - 16, y + 24, cx + 16, y + 56], fill=BG)
    texto_centro(d, y + 90, titulo, fonte(40, "SemiBold"), CINZA, cx)
    texto_centro(d, y + 150, preco, fonte(100, "Black"), cor, cx)

def cena_preco(im, t):
    d = ImageDraw.Draw(im); t0 = INI[7]
    texto_centro(d, 330, "O iFOOD NÃO É O VILÃO", fonte(60, "ExtraBold"), BRANCO)
    tc = tw(7, "traz")
    if t >= tc:
        texto_centro(d, 420, "ele traz cliente novo", fonte(44, "Medium"), VERDE)
    tq = tw(7, "quer", 1)
    if t >= tq:
        etiqueta(im, 290, 620, "no balcão", "R$ 20", VERDE, entra(t, tq))
        etiqueta(im, 790, 620, "no app", "MAIOR", AMBAR, entra(t, tq + 0.3))
        texto_centro(d, 700, "≠", fonte(140, "Black"), BRANCO)
        texto_centro(d, 1020, "Preço do app ≠ preço do balcão", fonte(54, "ExtraBold"), AMBAR)

def cena_cta(im, t):
    d = ImageDraw.Draw(im); t0 = INI[8]
    texto_centro(d, 330, "E NA SUA CIDADE?", fonte(76, "Black"), BRANCO)
    perg = [("Esses custos batem?", t0 + 0.4), ("Que gasto ficou de fora?", tw(8, "ou"))]
    for k, (s, ts) in enumerate(perg):
        if t >= ts:
            q = entra(t, ts); y = 520 + k * 260 + int(30 * (1 - q))
            f = fonte(54, "ExtraBold"); w = d.textlength(s, font=f)
            x0 = 110 if k == 0 else W - 110 - w - 80
            d.rounded_rectangle([x0, y, x0 + w + 80, y + 140], radius=40, fill=(255, 255, 255))
            d.polygon([(x0 + 60, y + 140), (x0 + 110, y + 140), (x0 + 50, y + 190)] if k == 0 else
                      [(x0 + w + 20, y + 140), (x0 + w - 30, y + 140), (x0 + w + 30, y + 190)], fill=(255, 255, 255))
            d.text((x0 + 40, y + 38), s, font=f, fill=TINTA)
    if t >= tw(8, "comentários"):
        texto_centro(d, 1110, "Comenta aqui embaixo 👇".replace(" 👇", ""), fonte(60, "Black"), AMBAR)
        texto_centro(d, 1200, "o seu custo real ajuda outro empreendedor", fonte(38, "Medium"), CINZA)

def quadro(t):
    im = fundo(); cabecalho(im)
    seg = max([k for k in range(NSEG) if INI[k] - 0.15 <= t] or [0])
    if seg == 0: cena_gancho(im, t)
    elif seg <= 4: cena_cupom(im, t)
    elif seg == 5: cena_resultado(im, t)
    elif seg == 6: cena_comparacao(im, t)
    elif seg == 7: cena_preco(im, t)
    else: cena_cta(im, t)
    chip_fonte(im, FONTES.get(seg, ""))
    legenda(im, PAL, t)
    # transição: escurece 0,15 s em volta das trocas de cena (o cupom 1–4 é contínuo)
    for k in (1, 5, 6, 7, 8):
        dd = abs(t - (INI[k] - 0.15))
        if dd < 0.15:
            im = Image.blend(im, Image.new("RGB", (W, H), BG), 0.6 * (1 - dd / 0.15))
    return im

def audio():
    import audio as AU
    narr = f"{AQUI}/narracao.mp3"; out = f"{AQUI}/audio_mix.wav"
    cortes = [INI[k] for k in (1, 5, 6, 7, 8)]
    pops = [l[3] for l in LINHAS[1:]]
    fx = AU.efeitos(DUR, cortes=cortes, pops=pops, riser_ate=INI[5]); AU.salvar(f"{AQUI}/efeitos.wav", fx * 0.25)
    AU.salvar(f"{AQUI}/trilha.wav", AU.trilha(DUR, "curioso", entra=0.5, respiros=[c - 0.6 for c in cortes]))
    fl = [f"[0]aresample=44100,{AU.VOZ_FILTRO},aformat=channel_layouts=stereo,apad=pad_dur=2,asplit=2[v][sc]",
          "[2]volume=-19dB[m0];[m0][sc]sidechaincompress=threshold=0.03:ratio=6:attack=25:release=350[m]",
          "[v][1][m]amix=inputs=3:normalize=0:duration=shortest,loudnorm=I=-14:TP=-1.5:LRA=11[a]"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", narr, "-i", f"{AQUI}/efeitos.wav", "-i", f"{AQUI}/trilha.wav",
                    "-filter_complex", ";".join(fl), "-map", "[a]", "-t", f"{DUR:.2f}", "-ar", "44100", out], check=True)
    return out

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for s in sys.argv[1:]:
            quadro(float(s)).save(f"{AQUI}/teste_{s}.png")
        sys.exit()
    a = audio()
    n = int(DUR * FPS)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", a, "-vf", "vignette=a=PI/5,noise=alls=3:allf=t+u", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "20", "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "192k",
                           "-shortest", "-movflags", "+faststart", f"{AQUI}/final.mp4"], stdin=subprocess.PIPE)
    for f in range(n):
        ff.stdin.write(quadro(f / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    print("ok", round(DUR, 1), "s")
