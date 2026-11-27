"""Composição final do vídeo Pix x maquininha: quadros 3D do Blender + camadas 2D por cima + áudio.
Uso:
  python3 compor.py previa          -> usa frames_previa/ (540x960, passo 2), gera previa.mp4 em 1080x1920
  python3 compor.py                 -> usa frames/ (1080x1920, todos os quadros), gera final.mp4
  python3 compor.py teste 12.5 48   -> salva teste2d_<s>.png (usa a pasta que tiver o quadro)"""
import os, sys, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "motor"))
from video import *  # Video, chip_fonte, entra, baloes + visual (W, H, cores, fonte, ...)

V = Video(AQUI, subst=[
    ("cem reais", "R$ 100"), ("zero a noventa centavos", "R$ 0 a R$ 0,90"), ("um real a dois e quarenta", "R$ 1 a R$ 2,40"),
    ("três e quinze a cinco e cinquenta", "R$ 3,15 a R$ 5,50"), ("trinta dias", "30 dias"), ("dois reais", "R$ 2"),
    ("cada cem", "cada R$ 100"), ("doze vezes", "12x"), ("doze e quarenta a dezoito e trinta", "R$ 12,40 a R$ 18,30"),
    ("doze parcelas", "12 parcelas"), ("custo zero", "custo R$ 0")], cauda=1.5)
INI, tw = V.ini, V.tw
MODO = sys.argv[1] if len(sys.argv) > 1 else "final"
PASTAS = [f"{AQUI}/frames", f"{AQUI}/frames_previa"] if MODO != "previa" else [f"{AQUI}/frames_previa"]

def base3d(t):
    """Quadro 3D mais próximo do instante t (na prévia só existem os quadros ímpares)."""
    f = int(round(t * FPS)) + 1
    for p in PASTAS:
        for g in (f, f - 1, f + 1, f - 2):
            arq = f"{p}/{g:05d}.png"
            if os.path.exists(arq):
                im = Image.open(arq).convert("RGB")
                return im if im.size == (W, H) else im.resize((W, H), Image.LANCZOS)
    return fundo()

_sombra = None
def sombra_topo(im):
    """Escurece o alto da tela para o texto 2D ler bem sobre o 3D."""
    global _sombra
    if _sombra is None:
        _sombra = Image.new("L", (W, H), 0); d = ImageDraw.Draw(_sombra)
        for y in range(0, 900): d.line([(0, y), (W, y)], fill=int(200 * (1 - y / 900) ** 1.4))
    im.paste((5, 8, 12), (0, 0), _sombra)

def escurecer(im, a):
    return Image.blend(im, Image.new("RGB", (W, H), BG), a) if a > 0 else im

# ---------- peças 2D ----------
ESCALA = 20.0  # régua de taxa vai de 0 a 20% para todas as formas (o 12x aparece grande de verdade)

def regua(d, y, pmin, pmax, cor, p):
    x0, x1 = 100, 980
    d.rounded_rectangle([x0, y, x1, y + 34], radius=17, fill=GRADE)
    a = x0 + (x1 - x0) * pmin / ESCALA * ease(p); b = x0 + (x1 - x0) * pmax / ESCALA * ease(p)
    d.rounded_rectangle([x0, y, max(x0 + 34, b), y + 34], radius=17, fill=tuple(int(c * 0.45) for c in cor))
    if a > x0 + 2: d.rounded_rectangle([x0, y, max(x0 + 34, a), y + 34], radius=17, fill=cor)
    for k in (0, 5, 10, 15, 20):
        x = x0 + (x1 - x0) * k / ESCALA
        d.text((x, y + 44), f"{k}%", font=fonte(22, "Medium"), fill=CINZA2, anchor="ma")

def cartao_taxa(im, t, t0, titulo, valor, t_val, pct, prazo, cor, sobra, pmin, pmax):
    """Painel do alto: título da forma de pagamento, valor que some (entra na fala do número), régua e sobra."""
    d = ImageDraw.Draw(im); q = entra(t, t0, 0.4); y = 190 + int(40 * (1 - q))
    d.rounded_rectangle([60, y, 1020, y + 560], radius=36, fill=BG2, outline=cor, width=4)
    d.text((100, y + 34), titulo, font=fonte(44, "ExtraBold"), fill=BRANCO)
    d.text((100, y + 92), "quanto some de R$ 100:", font=fonte(32, "Medium"), fill=CINZA)
    if t >= t_val:
        p = entra(t, t_val, 0.3); f = fonte(int(104 * (0.85 + 0.15 * p)), "Black")
        d.text((100, y + 140), valor, font=f, fill=cor)
        d.text((100, y + 268), pct, font=fonte(36, "SemiBold"), fill=BRANCO)
        regua(d, y + 330, pmin, pmax, cor, (t - t_val) / 0.6)
        d.text((100, y + 440), "SOBRA", font=fonte(30, "SemiBold"), fill=CINZA)
        d.text((100, y + 476), sobra, font=fonte(48, "ExtraBold"), fill=VERDE)
    if prazo and t >= prazo[1]:
        s = prazo[0]; f = fonte(34, "ExtraBold"); w = d.textlength(s, font=f)
        p = entra(t, prazo[1], 0.3)
        d.rounded_rectangle([980 - w - 44, y + 450, 980, y + 520], radius=35, fill=AMBAR)
        d.text((980 - w - 22, y + 485 + int(10 * (1 - p))), s, font=f, fill=BG, anchor="lm")

def faixa_alerta(im, t, t0, linhas, y=780):
    if t < t0: return
    d = ImageDraw.Draw(im); p = entra(t, t0, 0.35); x1 = 60 + 960 * p
    d.rounded_rectangle([60, y, x1, y + 70 + 52 * (len(linhas) - 1)], radius=20, fill=AMBAR)
    if p > 0.9:
        for k, s in enumerate(linhas):
            d.text((90, y + 16 + 52 * k), s, font=fonte(36 if k == 0 else 30, "ExtraBold" if k == 0 else "SemiBold"), fill=BG)

def selo(im, t, t0, cx, cy, grande, peq, cor):
    if t < t0: return
    d = ImageDraw.Draw(im); p = entra(t, t0, 0.3); r = int(150 * (0.6 + 0.4 * p))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cor)
    d.text((cx, cy - 18), grande, font=fonte(int(110 * p) + 1, "Black"), fill=BG, anchor="mm")
    d.text((cx, cy + 64), peq, font=fonte(int(38 * p) + 1, "ExtraBold"), fill=BG, anchor="mm")

# ---------- cenas ----------
def cena0(im, t):
    d = ImageDraw.Draw(im)
    texto_centro(d, 200, "UMA VENDA DE", fonte(46, "SemiBold"), CINZA)
    numero_grande(im, 260, 100, (t - 0.2) / 1.0, BRANCO, 190)
    tq = tw(0, "veja")
    if t >= tq:
        q = entra(t, tq); texto_centro(d, 500 + int(30 * (1 - q)), "Quanto fica com você?", fonte(68, "ExtraBold"), AMBAR)
    if t >= tw(0, "cartão"):
        q = entra(t, tw(0, "cartão"))
        d.rounded_rectangle([250, 620, 830, 720], radius=50, fill=(255, 255, 255))
        d.text((540, 670 + int(10 * (1 - q))), "“Pode ser no cartão?”", font=fonte(44, "ExtraBold"), fill=TINTA, anchor="mm")

def cena1(im, t):
    d = ImageDraw.Draw(im); q = entra(t, INI[1], 0.4); y = 190 + int(40 * (1 - q))
    d.rounded_rectangle([60, y, 1020, y + 520], radius=36, fill=BG2, outline=VERDE, width=4)
    d.text((100, y + 34), "PIX NA CHAVE OU QR IMPRESSO", font=fonte(42, "ExtraBold"), fill=BRANCO)
    d.text((100, y + 92), "conta de MEI, em regra:", font=fonte(32, "Medium"), fill=CINZA)
    selo(im, t, tw(1, "zero"), 300, y + 320, "R$ 0", "custo", VERDE)
    selo(im, t, tw(1, "hora"), 760, y + 320, "D+0", "cai na hora", AZUL)
    faixa_alerta(im, t, tw(1, "banco"), ["ATENÇÃO: o BC permite cobrar do MEI", "no Pix de venda (Res. BCB 19/2020, art. 4º)"], y=y + 560)
    if t >= tw(1, "leia"):
        p = entra(t, tw(1, "leia")); texto_centro(d, y + 700 + int(20 * (1 - p)), "LEIA O CONTRATO DA SUA CONTA", fonte(46, "Black"), AMBAR)

def cena5(im, t):
    d = ImageDraw.Draw(im); q = entra(t, INI[5], 0.4); y = 190 + int(40 * (1 - q))
    d.rounded_rectangle([60, y, 1020, y + 470], radius=36, fill=BG2, outline=AMBAR, width=4)
    d.text((100, y + 34), "ANTECIPAÇÃO", font=fonte(52, "Black"), fill=AMBAR)
    d.text((100, y + 104), "receber na hora em vez de esperar 30 dias", font=fonte(32, "Medium"), fill=CINZA)
    if t >= tw(5, "dois"):
        p = entra(t, tw(5, "dois"), 0.3)
        d.text((100, y + 160), "≈ R$ 2", font=fonte(int(150 * (0.85 + 0.15 * p)), "Black"), fill=AMBAR)
        d.text((100, y + 340), "a mais a cada R$ 100", font=fonte(44, "ExtraBold"), fill=BRANCO)
        d.text((100, y + 400), "de R$ 1,80 a R$ 2,34 no crédito à vista", font=fonte(30, "Medium"), fill=CINZA)

def linha_12(im, t, t0):
    """Linha do tempo com as 12 parcelas pingando (sincronizada com as moedas do 3D)."""
    d = ImageDraw.Draw(im); y = 820; x0, x1 = 110, 970
    p = entra(t, t0 - 0.3, 0.4)
    d.rounded_rectangle([60, y - 90, 1020, y + 150], radius=30, fill=BG2)
    d.text((100, y - 70), "SEM ANTECIPAR: 1 PARCELA POR MÊS", font=fonte(34, "ExtraBold"), fill=BRANCO)
    d.line([(x0, y + 40), (x0 + (x1 - x0) * p, y + 40)], fill=CINZA2, width=6)
    for k in range(12):
        x = x0 + (x1 - x0) * k / 11; tk = t0 + k * 0.32
        on = t >= tk; r = 20 if on else 9
        d.ellipse([x - r, y + 40 - r, x + r, y + 40 + r], fill=VERDE if on else GRADE)
        if k in (0, 11) and on:
            d.text((x, y + 76), f"mês {k + 1}", font=fonte(28, "SemiBold"), fill=AMBAR if k == 11 else CINZA, anchor="ma")

RANK = [("Pix na chave (MEI)", 0.00, VERDE), ("Pix na maquininha", 0.90, VERDE), ("Débito", 2.39, AZUL),
        ("Crédito à vista", 5.49, AMBAR), ("Crédito 12x", 18.29, VERM)]
def cena7(im, t):
    d = ImageDraw.Draw(im)
    texto_centro(d, 200, "QUANTO SOME DE R$ 100", fonte(56, "Black"), BRANCO)
    texto_centro(d, 270, "teto de cada faixa · pequeno MEI", fonte(32, "Medium"), CINZA)
    for i, (rot, v, cor) in enumerate(RANK):
        p = ease((t - INI[7]) / 0.5 - i * 0.35); y = 360 + i * 175
        d.text((80, y), rot, font=fonte(38, "SemiBold"), fill=BRANCO)
        d.text((1000, y), f"sobra {brl(100 - v * p)}", font=fonte(34, "SemiBold"), fill=CINZA, anchor="ra")
        d.rounded_rectangle([80, y + 56, 1000, y + 126], radius=18, fill=GRADE)
        if p > 0:
            d.rounded_rectangle([80, y + 56, 80 + max(24, 920 * v / 20 * p), y + 126], radius=18, fill=cor)
            d.text((100 + max(24, 920 * v / 20 * p), y + 64), "– " + brl(v * p), font=fonte(44, "Black"), fill=BRANCO)
    if t >= tw(7, "desconto"):
        p = entra(t, tw(7, "desconto"))
        texto_centro(d, 1240 + int(20 * (1 - p)), "Saber o custo mostra onde cabe desconto", fonte(42, "ExtraBold"), AMBAR)

def cena8(im, t):
    d = ImageDraw.Draw(im)
    texto_centro(d, 200, "E NA SUA CIDADE?", fonte(76, "Black"), BRANCO)
    baloes(im, t, [("O cliente ainda pede crédito?", INI[8] + 0.3), ("Quanto a sua maquininha cobra?", tw(8, "quanto"))], y0=330)
    if t >= tw(8, "comenta"):
        p = entra(t, tw(8, "comenta")); texto_centro(d, 860 + int(20 * (1 - p)), "Comenta aqui", fonte(80, "Black"), AMBAR)

FONTES = {0: "Fontes: tabelas oficiais das maquininhas (nov/2026) e Banco Central",
          1: "Fonte: Res. BCB 19/2020 e Agência Sebrae · conta PJ em banco que cobra: até ~1,45%",
          2: "Fonte: tabelas oficiais InfinitePay, SumUp, Ton e Mercado Pago (nov/2026)",
          3: "Fonte: tabelas oficiais SumUp, InfinitePay e PagBank (nov/2026)",
          4: "Fonte: tabelas oficiais InfinitePay, PagBank e SumUp (nov/2026)",
          5: "Fonte: tabelas oficiais PagBank, Mercado Pago e InfinitePay (nov/2026)",
          6: "Fonte: tabelas oficiais InfinitePay e SumUp (nov/2026)",
          7: "Faixa de entrada: até R$ 20 mil/mês, Visa/Master · taxas mudam por contrato",
          8: ""}

def quadro(t):
    seg = V.seg(t)
    im = base3d(t)
    if seg == 7: im = escurecer(im, 0.78)
    elif seg == 8: im = escurecer(im, 0.35)
    sombra_topo(im); cabecalho(im, "CONTAS REAIS")
    if seg == 0: cena0(im, t)
    elif seg == 1: cena1(im, t)
    elif seg == 2:
        cartao_taxa(im, t, INI[2], "PIX PELA MAQUININHA", "R$ 0 a 0,90", tw(2, "zero"), "0 a 0,9% da venda", ("CAI NA HORA", tw(2, "hora")),
                    VERDE, "R$ 99,10 a R$ 100,00", 0, 0.9)
    elif seg == 3:
        cartao_taxa(im, t, INI[3], "DÉBITO", "R$ 0,99 a 2,39", tw(3, "um"), "1 a 2,4% da venda", ("D+1", tw(3, "dia")),
                    AZUL, "R$ 97,61 a R$ 99,01", 0.99, 2.39)
    elif seg == 4:
        cartao_taxa(im, t, INI[4], "CRÉDITO À VISTA", "R$ 3,15 a 5,49", tw(4, "três"), "3,1 a 5,5% da venda", ("+ RÁPIDO = + CARO", tw(4, "rápido")),
                    AMBAR, "R$ 94,51 a R$ 96,85", 3.15, 5.49)
    elif seg == 5: cena5(im, t)
    elif seg == 6:
        cartao_taxa(im, t, INI[6], "CRÉDITO PARCELADO 12x", "R$ 12,40 a 18,29", tw(6, "doze", 1), "12,4 a 18,3% · recebendo tudo de uma vez", None,
                    VERM, "R$ 81,71 a R$ 87,60", 12.4, 18.29)
        if t >= tw(6, "sem") - 0.3: linha_12(im, t, tw(6, "sem"))
    elif seg == 7: cena7(im, t)
    else: cena8(im, t)
    if seg > 0 or t >= tw(0, "fonte"): chip_fonte(im, FONTES.get(seg, ""))
    legenda(im, V.pal, t)
    return V.transicao(im, t, range(1, 9))

if __name__ == "__main__":
    if MODO == "teste":
        for s in sys.argv[2:]: quadro(float(s)).save(f"{AQUI}/teste2d_{s}.png")
        sys.exit()
    saida = f"{AQUI}/previa.mp4" if MODO == "previa" else f"{AQUI}/final.mp4"
    pops = [tw(2, "zero"), tw(3, "um"), tw(4, "três"), tw(5, "dois"), tw(6, "doze", 1)] + [tw(6, "sem") + k * 0.32 for k in range(12)]
    a = V.audio(cortes=[INI[k] for k in range(1, 9)], pops=pops, riser_ate=INI[7])
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", a, "-vf", "vignette=a=PI/5,noise=alls=3:allf=t+u", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "20", "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "192k",
                           "-shortest", "-movflags", "+faststart", saida], stdin=subprocess.PIPE)
    for f in range(int(V.dur * FPS)): ff.stdin.write(quadro(f / FPS).tobytes())
    ff.stdin.close(); ff.wait(); print("ok", saida, round(V.dur, 1), "s")
