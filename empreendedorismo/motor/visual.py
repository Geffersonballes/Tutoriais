"""Identidade visual da série "Negócio Peça por Peça" (motion graphics em PIL).
Peças reutilizáveis: fundo planilha, cabeçalho com selo de IA, número grande, cupom fiscal,
barras comparativas, ícones simples e legenda palavra por palavra discreta.
Tudo desenhado em 1080x1920 (Reels). Zona segura: conteúdo entre y=170 e y=1560, x=60..960."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
INTER = "/usr/share/fonts/opentype/inter/"
MONO = "/usr/share/fonts/truetype/jetbrains-mono/"

# paleta: grafite sóbrio + verde-dinheiro + vermelho de desconto + âmbar de destaque
BG = (11, 15, 20); BG2 = (20, 27, 36); GRADE = (28, 36, 47)
BRANCO = (244, 246, 248); CINZA = (138, 150, 166); CINZA2 = (82, 94, 110)
VERDE = (43, 213, 118); VERM = (255, 92, 80); AMBAR = (255, 197, 61); AZUL = (90, 160, 255)
PAPEL = (246, 243, 236); TINTA = (30, 32, 36); ROXO = (92, 38, 120)

_cache = {}
def fonte(tam, peso="Bold", mono=False):
    k = (tam, peso, mono)
    if k not in _cache:
        if mono:
            arq = MONO + {"Bold": "JetBrainsMono-Bold.ttf", "Regular": "JetBrainsMono-Regular.ttf",
                          "ExtraBold": "JetBrainsMono-ExtraBold.ttf"}[peso]
        else:
            arq = INTER + ("Inter-%s.otf" % peso if peso in ("Regular", "Medium", "SemiBold") else "InterDisplay-%s.otf" % peso)
        _cache[k] = ImageFont.truetype(arq, tam)
    return _cache[k]

def ease(t):  # easeOutCubic
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

def brl(v, centavos=True):
    s = f"{v:,.2f}" if centavos else f"{v:,.0f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

# ---------------- fundo ----------------
_fundo = None
def fundo():
    global _fundo
    if _fundo is None:
        im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
        for x in range(0, W, 90): d.line([(x, 0), (x, H)], fill=GRADE, width=1)
        for y in range(0, H, 90): d.line([(0, y), (W, y)], fill=GRADE, width=1)
        # vinheta: centro levemente mais claro
        luz = Image.new("L", (W, H), 0); dl = ImageDraw.Draw(luz)
        dl.ellipse([-300, 200, W + 300, H - 200], fill=90)
        luz = luz.filter(ImageFilter.GaussianBlur(220))
        im = Image.composite(Image.new("RGB", (W, H), BG2), im, luz)
        _fundo = im
    return _fundo.copy()

def cabecalho(im, episodio="CONTAS REAIS"):
    d = ImageDraw.Draw(im)
    d.rectangle([60, 96, 72, 136], fill=VERDE)
    d.text((88, 92), "NEGÓCIO PEÇA POR PEÇA", font=fonte(30, "ExtraBold"), fill=BRANCO)
    d.text((88, 128), episodio, font=fonte(22, "SemiBold"), fill=CINZA)
    tag = "Conteúdo gerado com IA"
    f = fonte(20, "Medium"); w = d.textlength(tag, font=f)
    d.rounded_rectangle([W - 60 - w - 28, 100, W - 60, 136], radius=18, outline=CINZA2, width=2)
    d.text((W - 60 - w - 14, 106), tag, font=f, fill=CINZA)

def rodape_fonte(im, texto):
    d = ImageDraw.Draw(im)
    d.text((60, 1530), texto, font=fonte(22, "Medium"), fill=CINZA2)

# ---------------- texto ----------------
def texto_centro(d, y, s, f, cor, x=W // 2):
    w = d.textlength(s, font=f); d.text((x - w / 2, y), s, font=f, fill=cor); return w

def numero_grande(im, y, valor, prog, cor=BRANCO, tam=230, prefixo="R$ ", sufixo=""):
    """Número que conta de 0 até valor com o progresso prog (0..1)."""
    d = ImageDraw.Draw(im)
    v = valor * ease(prog)
    s = prefixo + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + sufixo
    f = fonte(tam, "Black")
    texto_centro(d, y, s, f, cor)

# ---------------- ícones ----------------
def icone_acai(im, cx, cy, esc=1.0, alfa=1.0):
    """Copo de açaí estilizado (flat)."""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = int(255 * alfa); s = esc
    topo, base, alt = 150 * s, 105 * s, 230 * s
    d.polygon([(cx - topo, cy - alt / 2), (cx + topo, cy - alt / 2), (cx + base, cy + alt / 2), (cx - base, cy + alt / 2)],
              fill=(236, 238, 242, a))
    d.polygon([(cx - topo * .93, cy - alt / 2 + 18 * s), (cx + topo * .93, cy - alt / 2 + 18 * s),
               (cx + topo * .80, cy + 10 * s), (cx - topo * .80, cy + 10 * s)], fill=ROXO + (a,))
    d.ellipse([cx - topo * 1.02, cy - alt / 2 - 95 * s, cx + topo * 1.02, cy - alt / 2 + 35 * s], fill=(110, 46, 140, a))
    for dx, dy, r, c in [(-60, -150, 26, (255, 240, 200)), (10, -175, 22, (220, 60, 80)), (70, -145, 24, (255, 240, 200)),
                         (-15, -130, 18, (245, 205, 90))]:
        d.ellipse([cx + dx * s - r * s, cy + dy * s - r * s, cx + dx * s + r * s, cy + dy * s + r * s], fill=c + (a,))
    d.rounded_rectangle([cx + 40 * s, cy - alt / 2 - 190 * s, cx + 58 * s, cy - alt / 2 - 20 * s], radius=8, fill=(255, 255, 255, a))
    im.paste(L, (0, 0), L)

# ---------------- cupom fiscal ----------------
def cupom(im, linhas, prog, x=110, y=300, larg=860, titulo="CUPOM — AÇAÍ 500 ML"):
    """linhas: [(descrição, valor, tipo)] tipo: 'base' | 'menos' | 'total'.
    prog vai de 0 a len(linhas): cada linha 'imprime' em sequência."""
    vis = [l for i, l in enumerate(linhas) if prog > i]
    alt = 150 + 74 * len(vis) + 40
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    # sombra
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    ds.rectangle([x + 14, y + 20, x + larg + 14, y + alt + 20], fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(18)); im.paste(sh, (0, 0), sh)
    # papel com borda serrilhada embaixo
    pts = [(x, y), (x + larg, y), (x + larg, y + alt)]
    n = 22
    for k in range(n, -1, -1):
        px = x + larg * k / n
        pts.append((px, y + alt + (14 if k % 2 else 0)))
    pts.append((x, y + alt))
    d.polygon(pts, fill=PAPEL)
    fm = fonte(34, "Bold", mono=True); fmr = fonte(30, "Regular", mono=True)
    tw = d.textlength(titulo, font=fm); d.text((x + (larg - tw) / 2, y + 40), titulo, font=fm, fill=TINTA)
    d.line([(x + 40, y + 104), (x + larg - 40, y + 104)], fill=(170, 165, 155), width=2)
    yy = y + 130
    for i, (desc, val, tipo) in enumerate(vis):
        rev = ease(min(1, prog - i))  # efeito de impressão: linha aparece da esquerda
        cor = {"base": TINTA, "menos": (200, 50, 40), "total": (20, 140, 70)}[tipo]
        f = fm if tipo != "menos" else fmr
        if tipo == "total":
            d.line([(x + 40, yy - 12), (x + larg - 40, yy - 12)], fill=(170, 165, 155), width=2)
        vs = ("- " if tipo == "menos" else "") + brl(val)
        d.text((x + 40, yy), desc, font=f, fill=cor)
        vw = d.textlength(vs, font=fm); d.text((x + larg - 40 - vw, yy), vs, font=fm, fill=cor)
        if rev < 1:
            d.rectangle([x + 40 + (larg - 80) * rev, yy - 4, x + larg - 30, yy + 50], fill=PAPEL)
        yy += 74
    im.paste(L, (0, 0), L)
    return y + alt

# ---------------- barras ----------------
def barras(im, itens, prog, y=640, maxv=None):
    """itens: [(rótulo, valor, cor)] barras horizontais que crescem."""
    d = ImageDraw.Draw(im)
    maxv = maxv or max(v for _, v, _ in itens)
    for i, (rot, v, cor) in enumerate(itens):
        p = ease(prog * 1.3 - i * 0.3)
        yy = y + i * 260
        d.text((80, yy), rot, font=fonte(40, "SemiBold"), fill=CINZA)
        d.rounded_rectangle([80, yy + 66, 1000, yy + 166], radius=20, fill=GRADE)
        if p > 0:
            d.rounded_rectangle([80, yy + 66, 80 + max(40, 920 * v / maxv * p), yy + 166], radius=20, fill=cor)
            s = brl(v * p); f = fonte(56, "Black")
            d.text((110, yy + 82), s, font=f, fill=BG)

# ---------------- legenda palavra por palavra ----------------
def legenda(im, palavras, t, y=1390):
    """palavras: lista {w,s,e}. Mostra a frase atual (bloco de até ~5 palavras) com a palavra falada destacada."""
    blocos, cur = [], []
    f = fonte(54, "Bold"); dm = ImageDraw.Draw(Image.new("L", (1, 1)))
    for p in palavras:
        if cur and sum(dm.textlength(x["w"], font=f) + 18 for x in cur + [p]) > 820:
            blocos.append(cur); cur = []
        cur.append(p)
        if p["w"].endswith((".", "?", "!")):
            blocos.append(cur); cur = []
    if cur: blocos.append(cur)
    bloco = None
    for b in blocos:
        if b[0]["s"] - 0.05 <= t <= b[-1]["e"] + 0.25: bloco = b
    if not bloco: return
    d = ImageDraw.Draw(im); f = fonte(54, "Bold")
    txt = [p["w"] for p in bloco]
    larg = sum(d.textlength(w, font=f) for w in txt) + 18 * (len(txt) - 1)
    x = (W - larg) / 2
    d.rounded_rectangle([x - 30, y - 18, x + larg + 30, y + 84], radius=22, fill=(0, 0, 0))
    for p in bloco:
        on = p["s"] <= t
        atual = p["s"] <= t <= p["e"] + 0.05
        cor = AMBAR if atual else (BRANCO if on else CINZA2)
        d.text((x, y), p["w"], font=f, fill=cor)
        x += d.textlength(p["w"], font=f) + 18

def icone_solar(im, cx, cy, esc=1.0, alfa=1.0, raio_sol=1.0):
    """Painel solar inclinado + sol (flat)."""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); a = int(255 * alfa); s = esc
    sx, sy, r = cx + 150 * s, cy - 170 * s, 70 * s
    for k in range(12):
        ang = k * math.pi / 6; r1, r2 = r * 1.3, r * (1.3 + 0.35 * raio_sol)
        d.line([(sx + r1 * math.cos(ang), sy + r1 * math.sin(ang)), (sx + r2 * math.cos(ang), sy + r2 * math.sin(ang))], fill=AMBAR + (a,), width=int(8 * s))
    d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=AMBAR + (a,))
    tl, tr, br, bl = (cx - 230 * s, cy - 40 * s), (cx + 150 * s, cy - 40 * s), (cx + 230 * s, cy + 130 * s), (cx - 150 * s, cy + 130 * s)
    d.polygon([tl, tr, br, bl], fill=(30, 70, 140, a), outline=(200, 215, 235, a))
    for i in range(1, 4):  # linhas da grade do painel
        f = i / 4
        d.line([(tl[0] + (tr[0] - tl[0]) * f, tl[1]), (bl[0] + (br[0] - bl[0]) * f, bl[1])], fill=(200, 215, 235, a), width=int(4 * s))
    for i in range(1, 3):
        f = i / 3
        d.line([(tl[0] + (bl[0] - tl[0]) * f, tl[1] + (bl[1] - tl[1]) * f), (tr[0] + (br[0] - tr[0]) * f, tr[1] + (br[1] - tr[1]) * f)], fill=(200, 215, 235, a), width=int(4 * s))
    d.rectangle([cx - 10 * s, cy + 130 * s, cx + 10 * s, cy + 230 * s], fill=(160, 170, 185, a))
    im.paste(L, (0, 0), L)

def grade_pontos(im, prog, destaque=4, y=420, cor=VERDE, passo=84):
    """100 pontos (10x10); os 'destaque' primeiros acendem no fim."""
    d = ImageDraw.Draw(im); n = int(100 * ease(prog)); x0 = (W - passo * 9) / 2
    for k in range(100):
        i, j = k % 10, k // 10
        cx, cy = x0 + i * passo, y + j * passo
        on = k < n
        c = (cor if k >= 100 - destaque and prog >= 1 else (CINZA2 if on else GRADE))
        r = int(passo * (0.36 if (k >= 100 - destaque and prog >= 1) else 0.29))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
