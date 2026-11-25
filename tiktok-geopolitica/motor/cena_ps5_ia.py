"""Série 2 — 'Por que a inteligência artificial deixou o PS5 mais caro?' (estilo C cartoon, mascote Pixel).
Mecanismo: console subiu R$ 600 -> o vilão é o chip de memória -> todo console tem 16 GB, feitos por poucas fábricas
-> centros de dados de IA compram montanhas de memória e pagam mais -> a fábrica troca de cliente; a memória de IA
gasta ~3x mais 'fábrica' por giga -> preço da memória quase dobra em 3 meses -> Black Friday -> convite.
Visual 100 % original: console genérico sem marca (caixa branca com faixa azul), nenhum logotipo de empresa.
Base: cena_live.py (T() com casamento exato de palavra).
Uso: blender -b --factory-startup -P cena_ps5_ia.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
import bpy, sys, os, json, math, random, re, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowpoly import *
from lowpoly import _id
from cartoon import *

args = sys.argv[sys.argv.index("--") + 1:]
PASTA = args[0]
LEG = json.load(open(os.path.join(PASTA, "legendas.json"), encoding="utf-8"))
FIM = LEG[-1]["e"] + 1.3
NSEG = max(x["seg"] for x in LEG) + 1
def seg_ini(i): return 0.0 if i == 0 else min(x["s"] for x in LEG if x["seg"] == i) - 0.15
def seg_fim(i): return seg_ini(i + 1) if i < NSEG - 1 else FIM
_norm = lambda s: re.sub(r"[^a-z0-9-]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
def T(i, palavra, n=0):
    hits = [x["s"] for x in LEG if x["seg"] == i and _norm(x["w"]) == _norm(palavra)]
    if not hits:
        hits = [x["s"] for x in LEG if x["seg"] == i and palavra.lower() in x["w"].lower()]
    return hits[min(n, len(hits) - 1)] if hits else seg_ini(i) + 0.5
S = [(seg_ini(i), seg_fim(i)) for i in range(NSEG)]

bpy.ops.wm.read_factory_settings(use_empty=True)
configurar_render()
scn = bpy.context.scene
scn.frame_start, scn.frame_end = 1, f(FIM)
random.seed(27)

AMARELO = (1.0, 0.82, 0.12, 1); VERDE = (0.20, 0.85, 0.40, 1); VERMELHO = (0.95, 0.22, 0.20, 1)
ROSA = (1.0, 0.45, 0.65, 1); ROXO = (0.60, 0.34, 0.95, 1); AZUL = (0.20, 0.55, 1.0, 1); BRANCO = (0.97, 0.97, 0.98, 1)
CIANO = (0.25, 0.95, 1.0, 1); ESCURO = (0.10, 0.11, 0.14, 1); CINZA = (0.40, 0.42, 0.48, 1); OURO = (1.0, 0.72, 0.10, 1)
PRATA = (0.80, 0.82, 0.86, 1); PCB = (0.10, 0.55, 0.30, 1)
CORES = [(0.98, 0.45, 0.35, 1), (0.30, 0.70, 1.0, 1), (0.98, 0.80, 0.25, 1), (0.45, 0.85, 0.45, 1), (0.75, 0.50, 0.95, 1)]
BRILHO = []
def brilha(ob): BRILHO.append(ob.data.materials[0]); return ob
def girarZ(ob, graus): ob.rotation_euler = (0, 0, math.radians(graus))

def console(nome, loc, esc=1.0):
    """Console GENÉRICO (sem marca): torre branca arredondada com faixa azul que acende e base escura."""
    c = caixa(nome, loc, (0.55 * esc, 1.3 * esc, 2.0 * esc), BRANCO); liso(c)
    fx = caixa(_id("faixa"), (0, 0, 0), (0.58 * esc, 0.10 * esc, 1.7 * esc), AZUL, unico=_id("fx")); filho(c, fx); fx.location = (0, -0.62 * esc, 0)
    base = caixa(_id("baseC"), (0, 0, 0), (0.8 * esc, 0.9 * esc, 0.12 * esc), ESCURO); filho(c, base); base.location = (0, 0, -1.0 * esc)
    brilha(fx); return c

def chip(nome, loc, s=0.6, cor=ESCURO):
    """Chip de memória: quadradinho preto com 'perninhas' prateadas dos dois lados e ponto dourado."""
    c = caixa(nome, loc, (s, s * 0.7, s * 0.14), cor)
    for lado in (-1, 1):
        for k in range(4):
            p = caixa(_id("pino"), (0, 0, 0), (s * 0.08, s * 0.14, s * 0.05), PRATA); filho(c, p)
            p.location = (-s * 0.36 + k * s * 0.24, lado * s * 0.40, -s * 0.03)
    d = cilindro(_id("ponto"), (0, 0, 0), s * 0.07, s * 0.02, OURO, seg=10); filho(c, d); d.location = (-s * 0.32, -s * 0.2, s * 0.08)
    return c

def chip_pe(nome, loc, s=0.9, cor=ESCURO):
    """Chip de pé, virado para a câmera (-Y)."""
    c = chip(nome, loc, s, cor); c.rotation_euler = (math.radians(90), 0, 0); return c

def etiqueta(nome, loc, w=2.2, h=1.1, cor=AMARELO):
    """Etiqueta de preço (o valor vai no grafismo 2D): placa com furinho e cordão."""
    e = caixa(nome, loc, (w, 0.08, h), cor, unico=_id("et"))
    fu = cilindro(_id("furo"), (0, 0, 0), 0.08, 0.1, ESCURO, seg=10); filho(e, fu); fu.rotation_euler = (math.radians(90), 0, 0); fu.location = (-w * 0.40, -0.03, h * 0.28)
    return e

def moeda(loc, r=0.28):
    m = cilindro(_id("moeda"), loc, r, 0.08, OURO, seg=16); return m

def pilha(x, y, n, t0, dt=0.06, r=0.32):
    obs = []
    for k in range(n):
        m = moeda((x + random.uniform(-0.04, 0.04), y, 0.05 + k * 0.09), r); visivel(m, t0 + k * dt); pop(m, t0 + k * dt)
        obs.append(m)
    return obs

def fabrica(nome, loc, cor=(0.85, 0.40, 0.30, 1), esc=1.0):
    """Fabriquinha de chips: galpão com telhado serrilhado e chaminé."""
    x, y = loc
    g = caixa(nome, (x, y, 1.0 * esc), (3.0 * esc, 2.0 * esc, 2.0 * esc), cor)
    for k in range(3):
        t = cilindro(_id("telh"), (0, 0, 0), 0.55 * esc, 1.9 * esc, tuple(c * 0.8 for c in cor[:3]) + (1,), seg=3); filho(g, t)
        t.rotation_euler = (math.radians(90), 0, 0); t.location = (-1.0 * esc + k * 1.0 * esc, 0, 1.15 * esc)
    ch = cilindro(_id("chamine"), (0, 0, 0), 0.2 * esc, 1.4 * esc, CINZA, seg=10); filho(g, ch); ch.location = (1.1 * esc, 0.5 * esc, 1.6 * esc)
    porta = caixa(_id("portaF"), (0, 0, 0), (0.8 * esc, 0.06 * esc, 1.1 * esc), ESCURO); filho(g, porta); porta.location = (0, -1.02 * esc, -0.45 * esc)
    return g

def wafer(nome, loc, r=0.7):
    """Disco de silício (wafer): disco prateado-azulado com grade."""
    w = cilindro(nome, loc, r, 0.05, (0.55, 0.65, 0.90, 1), seg=28)
    for k in range(-2, 3):
        l = caixa(_id("gr"), (0, 0, 0), (r * 1.6, 0.02, 0.06), (0.35, 0.45, 0.75, 1)); filho(w, l); l.location = (0, k * r * 0.3, 0.02)
    return w

def esteira(nome, a, b, z=0.6, cor=(0.22, 0.24, 0.30, 1)):
    from mathutils import Vector
    A, B = Vector((a[0], a[1], z)), Vector((b[0], b[1], z)); d = B - A
    c = caixa(nome, (A + B) / 2, (d.length, 0.9, 0.15), cor); c.rotation_euler = (0, 0, math.atan2(d.y, d.x)); return c

cam, alvo, cam_key, plano = camera_cartoon(24)

# =====================================================================
# ZONA A (x = 0) — quarto gamer: o console 'ganha' R$ 600 (pilha de moedas)  (bloco 0 e CTA)
# =====================================================================
t0, t1 = S[0]
QA = quarto_gamer(0)
brilha(QA["tela"])
px = pixel("pixel", (-0.4, 1.0, 0)); respirar(px, 0, FIM)
csA = console("consoleA", (-2.3, 0.2, 1.1), 1.0); girarZ(csA, 20)
etA = etiqueta("etiquetaA", (-2.3, -0.2, 2.9), 1.5, 0.75); girarZ(etA, 15)
tse = T(0, "Seiscentos"); tcul = T(0, "culpa"); tint = T(0, "inteligência"); tcom = T(0, "Como")
pop(etA, tse - 0.1, 1.0)
key(etA, "scale", tse + 0.4, (1, 1, 1)); key(etA, "scale", tse + 0.8, (1.35, 1.35, 1.35))
cor_key(etA.data.materials[0], tse + 0.4, AMARELO); cor_key(etA.data.materials[0], tse + 0.8, VERMELHO)
pilha(-1.2, -0.6, 7, tse + 0.1)
espanto(px, tse - 0.1, 1.3); apontar(px, tcul - 0.2, 1.5, "E", 40); pensar(px, tcom - 0.1, 1.5)
# 'robozinho' de IA (cubo roxo com olhos) aparece na estante: o suspeito
ia = caixa("robo", (0.7, 2.0, 2.9), (0.8, 0.7, 0.7), ROXO); liso(ia)
for dx in (-0.18, 0.18):
    o = esfera(_id("olhoIA"), (0, 0, 0), 0.09, CIANO, sub=2); filho(ia, o); o.location = (dx, -0.36, 0.08); brilha(o)
ant = cilindro(_id("antIA"), (0, 0, 0), 0.03, 0.35, CINZA, seg=6); filho(ia, ant); ant.location = (0, 0, 0.5)
visivel(ia, tint - 0.1, t1 + 0.1); pop(ia, tint - 0.1, 1.0)
plano(0, (-1.2, 0.6), "medio", altura=2.0); plano(tcul - 0.9, (-1.2, 0.6), "medio", altura=2.0); plano(tcul - 0.3, (0.2, 1.0), "medio", altura=2.2)
plano(tcom - 0.4, (-0.4, 0.8), "close", altura=2.0)

# =====================================================================
# ZONA B (x = 40) — loja: etiqueta 4.500 -> 5.100; globo 'economia'; o vilão: o chip de memória  (bloco 1)
# =====================================================================
t0, t1 = S[1]
sala_fechada("B", 40, (0.95, 0.88, 0.70, 1), (0.98, 0.62, 0.45, 1), prof=4.2)
caixa("balcao", (40, 1.4, 0.7), (7.0, 1.4, 1.4), (0.55, 0.36, 0.24, 1))
for k, dx in enumerate((-2.4, 0.0, 2.4)):
    console(_id("consB"), (40 + dx, 1.6, 2.4), 0.6)
etB = etiqueta("etiquetaB", (40.0, 0.4, 4.6), 2.6, 1.2)
tab = T(1, "abril"); tqu = T(1, "quatro"); tci = T(1, "cinco"); tso = T(1, "Sony"); tec = T(1, "economia")
tan = T(1, "analistas"); tvi = T(1, "vilão"); tme = T(1, "memória")
pop(etB, tab - 0.1, 1.0)
cor_key(etB.data.materials[0], tci - 0.1, AMARELO); cor_key(etB.data.materials[0], tci + 0.2, VERMELHO)
key(etB, "rotation_euler", tci - 0.15, (0, 0, 0)); key(etB, "rotation_euler", tci + 0.25, (0, 0, math.radians(360)))
globo = esfera("globo", (37.0, 2.6, 4.6), 0.9, (0.30, 0.60, 1.0, 1), sub=3); liso(globo)
for k in range(5):
    m = esfera(_id("cont"), (0, 0, 0), 0.32, (0.40, 0.80, 0.40, 1), sub=2); filho(globo, m)
    a = k * 1.3; m.location = (0.7 * math.cos(a), -0.4, 0.6 * math.sin(a * 1.7))
visivel(globo, tec - 0.2, tan + 0.2); pop(globo, tec - 0.2, 1.0)
key(globo, "rotation_euler", tec - 0.2, (0, 0, 0)); key(globo, "rotation_euler", tan + 0.2, (0, 0, math.radians(180)))
vil = chip_pe("vilao", (42.6, 0.6, 4.0), 1.6)
for dx in (-0.3, 0.3):   # sobrancelhas bravas
    sb = caixa(_id("sobr"), (0, 0, 0), (0.42, 0.06, 0.08), VERMELHO); filho(vil, sb); sb.location = (dx, 0.18, 0.13)
    sb.rotation_euler = (0, 0, math.radians(-20 if dx < 0 else 20))
visivel(vil, tvi - 0.1, t1 + 0.1); pop(vil, tvi - 0.1, 1.0)
key(vil, "location", tme, (42.6, 0.6, 4.0)); key(vil, "location", tme + 0.25, (42.6, 0.6, 4.3)); key(vil, "location", tme + 0.5, (42.6, 0.6, 4.0))
gB = pixel("guiaB", (39.9, -1.1, 0), escala=0.85); girarZ(gB["raiz"], 8); respirar(gB, t0, t1 + 0.5)
apontar(gB, tab - 0.1, 1.4, "D", 60); espanto(gB, tci - 0.1, 1.2); pensar(gB, tso - 0.1, 1.4); apontar(gB, tvi - 0.2, 1.6, "D", 50)
plano(t0, (40.0, 0.6), "geral", altura=2.8); plano(tso - 0.2, (39.0, 0.8), "geral", altura=3.0)
plano(tvi - 0.3, (41.6, 0.6), "medio", altura=3.2); plano(t1 - 0.05, (41.6, 0.6), "medio", altura=3.2)

# =====================================================================
# ZONA C (x = 80) — por dentro do console: placa com 16 chips; e as poucas fábricas  (bloco 2)
# =====================================================================
t0, t1 = S[2]
sala_fechada("C", 80, (0.62, 0.86, 0.55, 1), (0.55, 0.78, 1.0, 1), prof=5.0)
placa = caixa("placa", (78.0, 1.4, 2.6), (3.6, 0.15, 3.0), PCB); placa.rotation_euler = (math.radians(-8), 0, 0)
soc = caixa("soc", (0, 0, 0), (1.0, 0.1, 1.0), PRATA); filho(placa, soc); soc.location = (0, -0.1, 0)
tcs = T(2, "console"); tch = T(2, "chips"); tde = T(2, "dezesseis"); tfa = T(2, "fábricas"); tsa = T(2, "Samsung"); tmi = T(2, "Micron")
chipsC = []
for k in range(16):
    lado = k // 4; j = k % 4
    pos = [(-1.35, -1.05 + j * 0.7), (1.35, -1.05 + j * 0.7), (-0.9 + j * 0.6, 1.25), (-0.9 + j * 0.6, -1.25)][lado]
    c = chip(_id("ram"), (0, 0, 0), 0.42); filho(placa, c); c.rotation_euler = (math.radians(90), 0, 0); c.location = (pos[0], -0.12, pos[1])
    tp = tch + 0.05 * k if k < 8 else tde + 0.04 * (k - 8)
    visivel(c, tp); pop(c, tp, 1.0); chipsC.append(c)
destacar(soc.data.materials[0], tde, PRATA, 1.0)
for i, (fx, cor) in enumerate(((84.0, (0.85, 0.40, 0.30, 1)), (87.4, (0.35, 0.55, 0.95, 1)), (90.8, (0.95, 0.70, 0.25, 1)))):
    g = fabrica(_id("fab"), (fx, 2.4), cor, 0.8); tp = tfa - 0.1 + 0.2 * i; visivel(g, tp); pop(g, tp)
gC = pixel("guiaC", (80.8, -0.8, 0), escala=0.85); girarZ(gC["raiz"], -8); respirar(gC, t0, t1 + 0.5)
apontar(gC, tch - 0.2, 1.5, "E", 40); comemorar(gC, tde - 0.1, 1.2); apontar(gC, tfa - 0.1, 1.8, "D", 40)
plano(t0, (78.6, 0.6), "medio", altura=2.6); plano(tfa - 0.8, (78.6, 0.6), "medio", altura=2.6); plano(tfa - 0.3, (84.6, 1.0), "geral", altura=2.6)
plano(t1 - 0.05, (86.0, 1.0), "geral", altura=2.6)

# =====================================================================
# ZONA D (x = 120) — centro de dados de IA: racks gigantes engolem montanhas de chips e pagam mais  (bloco 3)
# =====================================================================
t0, t1 = S[3]
data_center(120, n=7)
tce = T(3, "centros"); tgi = T(3, "gigantes"); tmo = T(3, "montanhas"); tpa = T(3, "pagam")
racks = []
for k in range(3):
    r = caixa(_id("rackG"), (116.6 + k * 2.4, 1.6, 0.0), (1.8, 1.4, 5.6), (0.18, 0.18, 0.30, 1))
    for j in range(7):
        l = caixa(_id("ledG"), (0, 0, 0), (1.4, 0.04, 0.14), ROXO); filho(r, l); l.location = (0, -0.72, -2.2 + j * 0.7); brilha(l)
    key(r, "location", tce - 0.1, (116.6 + k * 2.4, 1.6, -2.9)); key(r, "location", tgi + 0.1 + 0.1 * k, (116.6 + k * 2.4, 1.6, 2.8))
    racks.append(r)
# montanha de chips caindo no rack do meio
t = tmo - 0.2
while t < t1 + 0.2:
    c = chip(_id("chipD"), (0, 0, 0), 0.4); visivel(c, t, t + 1.1)
    x0 = random.uniform(114.0, 116.0)
    caminho(c, t, t + 1.0, lambda u, x0=x0: bez((x0, -0.6, 0.4), (117.0, -0.4, 6.0), (119.0, 0.9, 4.6), u), orientar=False)
    t += 0.09
# sacos de dinheiro (moedas) indo da IA para a 'fábrica' fora de quadro
t = tpa - 0.2
while t < t1 + 0.2:
    m = moeda((0, 0, 0), 0.3); m.rotation_euler = (math.radians(90), 0, 0); visivel(m, t, t + 1.0)
    caminho(m, t, t + 1.0, lambda u: bez((121.0, 0.5, 4.0), (124.0, -0.6, 5.5), (127.0, -0.4, 2.0), u), orientar=False); t += 0.12
gD = pixel("guiaD", (123.8, -1.4, 0), escala=0.85); girarZ(gD["raiz"], -10); respirar(gD, t0, t1 + 0.5)
pensar(gD, t0 + 0.05, 1.4); espanto(gD, tgi - 0.1, 1.2); apontar(gD, tmo - 0.1, 1.6, "E", 60); comemorar(gD, tpa - 0.1, 1.2)
plano(t0, (120.0, 0.6), "geral", altura=2.8); plano(tgi - 0.1, (119.6, 0.4), "geral", altura=3.4)
plano(tpa - 0.4, (121.4, 0.6), "geral", altura=3.0); plano(t1 - 0.05, (121.4, 0.6), "geral", altura=3.0)

# =====================================================================
# ZONA E (x = 160) — a fábrica troca de cliente; 3 wafers viram 1 pilha de IA; sobra pouco para console/PC/celular  (bloco 4)
# =====================================================================
t0, t1 = S[4]
sala_fechada("E", 160, (0.80, 0.80, 0.90, 1), (0.98, 0.86, 0.50, 1), prof=5.2)
fE = fabrica("fabE", (160.0, 3.4), (0.35, 0.55, 0.95, 1), 1.1)
esteira("estIA", (160.0, 1.6), (165.0, 0.6))
esteira("estCons", (160.0, 1.6), (155.0, 0.6))
caixaIA = caixa("caixaIA", (165.6, 0.4, 0.8), (1.6, 1.4, 1.6), ROXO)
caixaCo = caixa("caixaCo", (154.4, 0.4, 0.5), (1.6, 1.4, 1.0), BRANCO)
ttr = T(4, "trocam"); tcl = T(4, "cliente"); tpu = T(4, "pulo"); ttres = T(4, "três"); tsob = T(4, "Sobra")
tcn = T(4, "console"); tpc = T(4, "PC"); tcel = T(4, "celular")
# antes de trocar: chips indo para o lado do console; depois: quase todos para a IA
t = t0
while t < t1 + 0.2:
    paraIA = t > ttr or random.random() < 0.3
    if t > ttr and random.random() < 0.15: paraIA = False
    c = chip(_id("chipE"), (0, 0, 0), 0.36); visivel(c, t, t + 1.3)
    dst = (165.0, 0.6, 0.8) if paraIA else (155.0, 0.6, 0.8)
    caminho(c, t, t + 1.3, lambda u, dst=dst: lerp((160.0, 1.6, 0.8), dst, u), orientar=False)
    t += 0.22
destacar(caixaIA.data.materials[0], tcl, ROXO, 1.0)
# 3 wafers -> 1 pilha alta (memória de IA) x 1 wafer -> 1 chip comum
W = []
for k in range(3):
    w = wafer(_id("waf"), (156.8 + k * 1.5, -0.6, 2.9), 0.6); w.rotation_euler = (math.radians(90), 0, 0)
    visivel(w, ttres - 0.2 + 0.15 * k, tsob - 0.1); pop(w, ttres - 0.2 + 0.15 * k); W.append(w)
pilhaIA = caixa("pilhaIA", (162.0, -0.6, 2.9), (0.7, 0.5, 1.4), ROXO)
for j in range(5):
    s = caixa(_id("cam"), (0, 0, 0), (0.74, 0.54, 0.05), PRATA); filho(pilhaIA, s); s.location = (0, 0, -0.56 + j * 0.28)
visivel(pilhaIA, ttres + 0.4, tsob - 0.1); pop(pilhaIA, ttres + 0.4, 1.0)
# 'sobra menos': no lado do console, uma caixinha quase vazia; console, PC e celular piscam
pc = caixa("pcE", (153.4, -1.2, 0.95), (0.8, 1.2, 1.9), (0.15, 0.15, 0.2, 1))
cel = caixa("celE", (155.9, -1.2, 0.8), (0.6, 0.12, 1.2), ESCURO)
csE = console("consE", (154.6, -1.2, 0.85), 0.75)
for ob, tt in ((csE, tcn), (pc, tpc), (cel, tcel)):
    visivel(ob, tsob - 0.2); pop(ob, tt - 0.1, 1.0, 0.3)
gE = pixel("guiaE", (157.6, -1.9, 0), escala=0.8); respirar(gE, t0, t1 + 0.5)
apontar(gE, ttr - 0.2, 1.6, "D", 30); comemorar(gE, tpu - 0.1, 1.2); pensar(gE, ttres + 0.4, 1.4); apontar(gE, tsob - 0.1, 1.8, "E", 40)
plano(t0, (160.0, 0.8), "geral", altura=2.6); plano(tpu - 0.8, (160.0, 0.8), "geral", altura=2.6); plano(tpu - 0.3, (159.4, -0.6), "medio", altura=2.4)
plano(tsob - 0.8, (159.4, -0.6), "medio", altura=2.4); plano(tsob - 0.3, (155.4, -1.2), "medio", altura=1.5); plano(t1 - 0.05, (155.4, -1.2), "medio", altura=1.5)

# =====================================================================
# ZONA F (x = 200) — gráfico de barras: a memória quase dobra; a etiqueta do console sobe junto  (bloco 5)
# =====================================================================
t0, t1 = S[5]
sala_fechada("F", 200, (0.40, 0.42, 0.60, 1), (0.30, 0.36, 0.62, 1), prof=4.6)
trs = T(5, "Resultado"); tdo = T(5, "dobrou"); ttf = T(5, "TrendForce"); ten = T(5, "encarece")
b1 = cilindro("barra1", (197.6, 2.0, 0.0), 0.55, 1.0, AZUL, seg=16, unico="b1")
b2 = cilindro("barra2", (199.6, 2.0, 0.0), 0.55, 1.0, VERMELHO, seg=16, unico="b2")
for b in (b1, b2):
    for v in b.data.vertices: v.co.z += 0.5
def nivel(b, t, h): b.scale = (1, 1, h); b.keyframe_insert("scale", frame=f(t))
nivel(b1, t0, 0.05); nivel(b1, trs + 0.1, 2.0); nivel(b2, t0, 0.05); nivel(b2, tdo - 0.2, 0.05); nivel(b2, tdo + 0.5, 3.9)
chF = chip_pe("chipF", (199.6, 1.8, 4.6), 0.9); visivel(chF, tdo - 0.2); pop(chF, tdo - 0.2)
key(chF, "location", tdo - 0.2, (199.6, 1.8, 2.6)); key(chF, "location", tdo + 0.5, (199.6, 1.8, 4.6))
seta = seta3d("setaF", 2.2, VERMELHO); seta.location = (201.4, 1.6, 2.0); seta.rotation_euler = (0, math.radians(-60), 0)
visivel(seta, tdo); pop(seta, tdo)
csF = console("consF", (203.4, 1.8, 1.2), 0.9)
etF = etiqueta("etF", (203.4, 1.0, 3.1), 1.4, 0.7)
key(etF, "location", ten - 0.2, (203.4, 1.0, 3.1)); key(etF, "location", ten + 0.4, (203.4, 1.0, 4.1))
cor_key(etF.data.materials[0], ten - 0.2, AMARELO); cor_key(etF.data.materials[0], ten + 0.3, VERMELHO)
gF = pixel("guiaF", (200.4, -1.6, 0), escala=0.8); respirar(gF, t0, t1 + 0.5)
pensar(gF, t0 + 0.05, 1.2); espanto(gF, tdo - 0.1, 1.4); apontar(gF, ten - 0.2, 1.6, "D", 40)
plano(t0, (200.0, 0.6), "geral", altura=2.6); plano(tdo - 0.8, (200.0, 0.6), "geral", altura=2.6); plano(tdo - 0.3, (199.6, 0.6), "geral", altura=3.0)
plano(ten - 0.9, (199.6, 0.6), "geral", altura=3.0); plano(ten - 0.4, (202.0, 0.6), "geral", altura=2.6); plano(t1 - 0.05, (202.2, 0.6), "geral", altura=2.6)

# =====================================================================
# ZONA G (x = 240) — Black Friday: placa de desconto pisca, mas o chip continua com a etiqueta vermelha  (bloco 6)
# =====================================================================
t0, t1 = S[6]
sala_fechada("G", 240, (0.25, 0.22, 0.28, 1), (0.14, 0.12, 0.18, 1), prof=4.2)
tbl = T(6, "Black"); tsx = T(6, "sexta"); tds = T(6, "Desconto"); tca = T(6, "cara")
placaG = caixa("placaBF", (240.0, 3.6, 4.4), (5.0, 0.2, 1.4), ESCURO)
neon = caixa("neonBF", (0, 0, 0), (4.6, 0.05, 1.0), AMARELO, unico="neon"); filho(placaG, neon); neon.location = (0, -0.12, 0); brilha(neon)
k = 0; t = tbl
mn = neon.data.materials[0]; cor_key(mn, t0, (0.25, 0.20, 0.05, 1))
while t < t1 + 0.3:
    cor_key(mn, t, AMARELO if k % 2 == 0 else (0.55, 0.40, 0.05, 1)); t += 0.45; k += 1
caixa("balcaoG", (240.0, 1.6, 0.7), (6.0, 1.4, 1.4), (0.30, 0.24, 0.20, 1))
csG = console("consG", (238.6, 1.6, 2.4), 0.7)
etG = etiqueta("etG", (238.6, 0.8, 3.7), 1.3, 0.6, VERDE); visivel(etG, tds - 0.1); pop(etG, tds - 0.1)
chG = chip_pe("chipG", (241.8, 1.4, 2.4), 0.9)
etC = etiqueta("etC", (241.8, 0.8, 3.7), 1.3, 0.6, VERMELHO); visivel(etC, tca - 0.3); pop(etC, tca - 0.3)
gG = pixel("guiaG", (240.2, -1.2, 0), escala=0.8); respirar(gG, t0, t1 + 0.5)
acenar(gG, tbl - 0.1, 1.2); apontar(gG, tds - 0.1, 1.4, "E", 40); pensar(gG, tca - 0.2, 1.5)
plano(t0, (240.0, 0.8), "geral", altura=3.0); plano(tds - 0.8, (240.0, 0.8), "geral", altura=3.0); plano(tds - 0.3, (240.0, 0.6), "medio", altura=2.8)
plano(t1 - 0.05, (240.4, 0.6), "medio", altura=2.8)

# =====================================================================
# 7 — convite: de volta ao quarto, o Pixel acena com o console ao lado (câmera aberta para o CTA)
# =====================================================================
t0 = S[7][0]
acenar(px, t0 + 0.15, 1.6); apontar(px, T(7, "Ainda") - 0.2, 1.6, "E", 35); comemorar(px, T(7, "fila") - 0.1, 1.4)
cam_key(t0, (-0.8, -6.6, 2.9), (-0.8, 1.0, 2.6)); cam_key(FIM, (-0.7, -6.1, 2.9), (-0.7, 1.0, 2.6))

# ---------- corte seco entre zonas: sem isso o Bezier da câmera 'atropela' a zona seguinte ----------
for ob in (cam, alvo):
    fcs = [fc for fc in ob.animation_data.action.fcurves if fc.data_path == "location"]
    fx = [fc for fc in fcs if fc.array_index == 0][0]
    cortes = set()
    kps = list(fx.keyframe_points)
    for a, b in zip(kps, kps[1:]):
        if abs(b.co.y - a.co.y) > 12: cortes.add(round(a.co.x))
    for fc in fcs:
        for kp in fc.keyframe_points:
            if round(kp.co.x) in cortes: kp.interpolation = "CONSTANT"
        ks = list(fc.keyframe_points)
        for a, b in zip(ks, ks[1:]):   # a chave logo depois do corte não 'puxa' a curva de trás
            if round(a.co.x) in cortes: b.handle_left_type = "VECTOR"; b.handle_right_type = "VECTOR"
        fc.update()

# ---------- render ----------
modo_cartoon(samples=int(os.environ.get("AMOSTRAS", "8")))
for m in set(BRILHO):
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Emission Color"].default_value = b.inputs["Base Color"].default_value
        b.inputs["Emission Strength"].default_value = 0.8
if os.environ.get("DBG"): exec(open(os.environ["DBG"]).read())
saida = os.path.join(PASTA, "frames"); os.makedirs(saida, exist_ok=True)
if len(args) > 1 and args[1] == "preview":
    scn.render.resolution_percentage = int(os.environ.get("PCT", "50"))
    for t in [float(x) for x in args[2].split(",")]:
        scn.frame_set(f(t)); scn.render.filepath = os.path.join(PASTA, "preview", f"p_{t:06.2f}.jpg"); bpy.ops.render.render(write_still=True)
elif len(args) > 1 and args[1] == "range":
    a, b2 = [int(x) for x in args[2].split(",")]
    scn.frame_start, scn.frame_end = a, b2
    scn.frame_step = int(os.environ.get("PASSO", "1"))
    scn.render.filepath = os.path.join(saida, "f_")
    bpy.ops.render.render(animation=True)
else:
    print("FRAMES", scn.frame_end)
