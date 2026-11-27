"""Vídeo 02 — bastidores Balles Tech: quanto custa conseguir um cliente de energia solar."""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "motor"))
from video import *

V = Video(AQUI, cauda=1.2, subst=[
    ("duzentos e oitenta reais", "R$ 280"), ("mil e setecentos", "R$ 1.700"), ("dois mil e novecentos reais", "R$ 2.900"),
    ("vinte e trinta reais", "R$ 20 e R$ 30"), ("quarenta a sessenta", "40 a 60"), ("quatro em cada cem", "4 em cada 100"),
    ("mil e quinhentos reais", "R$ 1.500"), ("vinte e uma vezes", "21x"), ("vinte e cinco a quarenta e cinco dias", "25 a 45 dias")])
tw, I = V.tw, V.ini
FONTE = "Dados reais da Balles Tech Energia · nov/2026"
FONTES = {0: "", 1: FONTE, 2: FONTE, 3: FONTE, 4: FONTE, 5: "R$ 2.900 por mês ÷ cerca de 2 clientes", 6: FONTE, 7: "", 8: ""}

def g0(im, t):
    d = ImageDraw.Draw(im); p = entra(t, 0, 0.5)
    icone_solar(im, W // 2, 560, 1.25, p, raio_sol=0.6 + 0.4 * abs(math.sin(t * 2)))
    texto_centro(d, 860, "QUANTO CUSTA CONSEGUIR", fonte(50, "ExtraBold"), CINZA)
    texto_centro(d, 925, "1 CLIENTE DE ENERGIA SOLAR?", fonte(50, "ExtraBold"), BRANCO)
    if t >= tw(0, "sapezal"):
        q = entra(t, tw(0, "sapezal"))
        texto_centro(d, 1090 + int(20 * (1 - q)), "Sapezal, Mato Grosso", fonte(46, "SemiBold"), VERDE)
    if t >= tw(0, "abrir"):
        texto_centro(d, 1170, "os números reais da minha empresa", fonte(42, "Medium"), AMBAR)

def g1(im, t):
    d = ImageDraw.Draw(im)
    ls = [("ANÚNCIO (R$ 280/SEMANA)", 1200, "base", I[1]), ("AGÊNCIA DE MARKETING", 1700, "base", tw(1, "mil")),
          ("TOTAL NO MÊS", 2900, "total", tw(1, "total"))]
    prog = sum(min(1, max(0, (t - l[3]) / 0.5)) for l in ls)
    fim = cupom(im, [l[:3] for l in ls], prog, y=300, titulo="MARKETING DO MÊS")
    d.text((110, fim + 50), "≈ R$ 280 × 4,3 semanas", font=fonte(34, "Medium"), fill=CINZA)

def g2(im, t):
    d = ImageDraw.Draw(im)
    texto_centro(d, 330, "CADA CONTATO NO WHATSAPP", fonte(48, "ExtraBold"), CINZA)
    p = entra(t, I[2], 0.6)
    texto_centro(d, 420 - int(30 * (1 - p)), "R$ 20 a 30", fonte(190, "Black"), BRANCO)
    if t >= tw(2, "dá"):
        q = entra(t, tw(2, "dá"))
        for k in range(5):  # balões de conversa empilhando
            if q * 5 > k:
                y = 680 + k * 95; x = 140 if k % 2 == 0 else 420
                d.rounded_rectangle([x, y, x + 520, y + 72], radius=36, fill=(37, 211, 102) if k % 2 else BG2)
                d.text((x + 34, y + 14), "Oi! Quero um orçamento", font=fonte(36, "SemiBold"), fill=BG if k % 2 else BRANCO)
        texto_centro(d, 1210, "40 a 60 conversas por mês", fonte(58, "ExtraBold"), VERDE)

def g3(im, t):
    d = ImageDraw.Draw(im)
    etapas = [("Pedem orçamento", 1.0, I[3]), ("Mandam a conta de luz", 1.0, tw(3, "manda")),
              ("Visita técnica (na maioria)", 0.85, tw(3, "vou")), ("Recebem proposta", 1.0, tw(3, "recebe"))]
    texto_centro(d, 300, "O CAMINHO DO CLIENTE", fonte(54, "ExtraBold"), BRANCO)
    for k, (s, larg, ts) in enumerate(etapas):
        if t < ts: continue
        q = entra(t, ts, 0.4); y = 420 + k * 150; w = 900 * larg * q
        d.rounded_rectangle([(W - w) / 2, y, (W + w) / 2, y + 110], radius=24, fill=AZUL if k < 3 else VERDE)
        if q > 0.6: texto_centro(d, y + 30, s, fonte(44, "Bold"), BG)
    if t >= tw(3, "padrão"):
        itens = [("padrão de energia", tw(3, "padrão")), ("parte elétrica", tw(3, "elétrica")), ("telhado aguenta as placas?", tw(3, "telhado"))]
        for k, (s, ts) in enumerate(itens):
            if t >= ts: d.text((140, 1060 + k * 70), "✓ " + s if False else "— " + s, font=fonte(42, "SemiBold"), fill=AMBAR)

def g4(im, t):
    d = ImageDraw.Draw(im)
    texto_centro(d, 300, "O NÚMERO QUE DÓI", fonte(60, "Black"), VERM)
    grade_pontos(im, (t - I[4]) / 1.6, 4, y=410, passo=74)
    if t >= tw(4, "quatro"):
        texto_centro(d, 1130, "4 em cada 100 fecham", fonte(70, "Black"), VERDE)
    if t >= tw(4, "uns"):
        texto_centro(d, 1225, "≈ 2 clientes por mês deste canal", fonte(42, "Medium"), CINZA)

def g5(im, t):
    d = ImageDraw.Draw(im)
    texto_centro(d, 380, "R$ 2.900 ÷ 2 CLIENTES", fonte(56, "ExtraBold"), CINZA)
    p = entra(t, tw(5, "perto"), 0.6)
    texto_centro(d, 520 - int(40 * (1 - p)), "≈ R$ 1.500", fonte(200, "Black"), AMBAR)
    if t >= tw(5, "para"):
        texto_centro(d, 820, "de marketing para", fonte(50, "SemiBold"), BRANCO)
        texto_centro(d, 890, "cada cliente fechado", fonte(50, "SemiBold"), BRANCO)

def g6(im, t):
    d = ImageDraw.Draw(im)
    cards = [("À vista", tw(6, "vista")), ("Financiamento", tw(6, "financia")), ("Entrada no Pix + até 21x no cartão", tw(6, "entrada"))]
    texto_centro(d, 290, "COMO O CLIENTE PAGA", fonte(52, "ExtraBold"), BRANCO)
    for k, (s, ts) in enumerate(cards):
        if t < ts: continue
        q = entra(t, ts); y = 400 + k * 140 + int(20 * (1 - q))
        d.rounded_rectangle([110, y, 970, y + 110], radius=24, fill=BG2, outline=VERDE, width=3)
        f = fonte(44, "Bold") if len(s) < 30 else fonte(38, "Bold")
        d.text((150, y + 55), s, font=f, fill=BRANCO, anchor="lm")
    tp = tw(6, "primeiro")
    if t >= tp:
        q = ease((t - tp) / 2.0); y = 1020
        texto_centro(d, y - 80, "25 a 45 dias", fonte(80, "Black"), AMBAR)
        d.rounded_rectangle([110, y + 40, 970, y + 64], radius=12, fill=GRADE)
        d.rounded_rectangle([110, y + 40, 110 + 860 * q, y + 64], radius=12, fill=AMBAR)
        d.text((110, y + 90), "1º \"oi\"", font=fonte(36, "SemiBold"), fill=CINZA)
        s = "gerando energia"; f = fonte(36, "SemiBold"); d.text((970 - d.textlength(s, font=f), y + 90), s, font=f, fill=CINZA)

def g7(im, t):
    d = ImageDraw.Draw(im)
    texto_centro(d, 360, "A MAIOR LIÇÃO", fonte(54, "ExtraBold"), CINZA)
    tr = tw(7, "relacionamento")
    if t >= tw(7, "quanto"):
        texto_centro(d, 470, "mais relacionamento", fonte(52, "SemiBold"), BRANCO)
        texto_centro(d, 540, "= mais confiança", fonte(52, "SemiBold"), BRANCO)
    if t >= tr:
        q = entra(t, tr, 0.3)
        texto_centro(d, 720, "RELACIONAMENTO", fonte(int(110 * (0.8 + 0.2 * q)), "Black"), VERDE)
        texto_centro(d, 850, "vende mais do que", fonte(52, "SemiBold"), CINZA)
        texto_centro(d, 920, "PREÇO BAIXO", fonte(int(110 * (0.8 + 0.2 * q)), "Black"), VERM)

def g8(im, t):
    d = ImageDraw.Draw(im)
    texto_centro(d, 330, "E NO SEU NEGÓCIO?", fonte(76, "Black"), BRANCO)
    baloes(im, t, [("Quanto custa cada cliente?", I[8] + 0.3), ("Você já fez essa conta?", tw(8, "você"))])
    if t >= tw(8, "comentários"):
        texto_centro(d, 1110, "Comenta aqui embaixo", fonte(60, "Black"), AMBAR)

CENAS = [g0, g1, g2, g3, g4, g5, g6, g7, g8]
def quadro(t):
    im = fundo(); cabecalho(im, "BASTIDORES DA BALLES TECH")
    s = V.seg(t); CENAS[s](im, t); chip_fonte(im, FONTES.get(s, "")); legenda(im, V.pal, t)
    return V.transicao(im, t, range(1, V.nseg))

V.rodar(quadro, cortes=[I[k] for k in range(1, V.nseg)], pops=[tw(4, "quatro"), tw(5, "perto")], riser_ate=I[4])
