"""Série 2 — 'Como o anti-cheat pega o trapaceiro?' (estilo C cartoon, mascote Pixel).
Mecanismo peça por peça: onda de 960 mil contas de robôs -> 3 truques: (1) assinatura na memória comparada
com uma lista, (2) vigia no núcleo (kernel) que liga junto com o sistema, (3) servidor/IA olhando como
você joga -> banimento atrasado em onda.
Visual 100 % original: nenhum logotipo, personagem, mapa ou tela de jogo/empresa.
Uso: blender -b --factory-startup -P cena_anticheat.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
import bpy, sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowpoly import *
from lowpoly import _id
from cartoon import *

args = sys.argv[sys.argv.index("--") + 1:]
PASTA = args[0]
LEG = json.load(open(os.path.join(PASTA, "legendas.json"), encoding="utf-8"))
FIM = LEG[-1]["e"] + 5.6          # inclui o pedido de like (o Pixel continua animado, sem quadro congelado)
NSEG = max(x["seg"] for x in LEG) + 1
def seg_ini(i): return 0.0 if i == 0 else min(x["s"] for x in LEG if x["seg"] == i) - 0.15
def seg_fim(i): return seg_ini(i + 1) if i < NSEG - 1 else FIM
def T(i, palavra, n=0):
    hits = [x["s"] for x in LEG if x["seg"] == i and palavra.lower() in x["w"].lower()]
    return hits[min(n, len(hits) - 1)] if hits else seg_ini(i) + 0.5
S = [(seg_ini(i), seg_fim(i)) for i in range(NSEG)]

bpy.ops.wm.read_factory_settings(use_empty=True)
configurar_render()
scn = bpy.context.scene
scn.frame_start, scn.frame_end = 1, f(FIM)
random.seed(25)

AMARELO = (1.0, 0.82, 0.12, 1); VERDE = (0.20, 0.85, 0.40, 1); VERMELHO = (0.95, 0.20, 0.18, 1)
ROXO = (0.60, 0.34, 0.95, 1); AZUL = (0.20, 0.55, 1.0, 1); BRANCO = (0.97, 0.97, 0.98, 1)
CIANO = (0.25, 0.95, 1.0, 1); ESCURO = (0.10, 0.11, 0.14, 1); CINZA = (0.45, 0.47, 0.54, 1)
CORES = [(0.98, 0.45, 0.35, 1), (0.30, 0.70, 1.0, 1), (0.98, 0.80, 0.25, 1), (0.45, 0.85, 0.45, 1), (0.75, 0.50, 0.95, 1), (1.0, 0.60, 0.20, 1)]
BRILHO = []

def girar(ob, graus): ob.rotation_euler = (0, 0, math.radians(graus))
def brilha(ob): BRILHO.append(ob.data.materials[0]); return ob
def linear(ob):
    for fc in ob.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

def tubo(nome, a, b, r, cor, unico=None):
    from mathutils import Vector
    a, b = Vector(a), Vector(b); d = b - a
    c = cilindro(nome, (a + b) / 2, r, d.length, cor, seg=10, unico=unico)
    c.rotation_mode = "QUATERNION"; c.rotation_quaternion = d.to_track_quat("Z", "Y"); return c

def xis(loc, s=0.5):
    """X vermelho de 'banido' (virado para a câmera)."""
    r = vazio(_id("xis"), loc)
    for a in (45, -45):
        b = caixa(_id("xb"), (0, 0, 0), (s * 1.4, s * 0.2, s * 0.28), VERMELHO); filho(r, b); b.rotation_euler = (0, math.radians(a), 0)
    return r

def robo(loc, s=1.0, cor=CINZA):
    """Robozinho genérico (conta automática): corpo, cabeça, olhos e antena."""
    b = caixa(_id("robo"), (loc[0], loc[1], loc[2] + 0.32 * s), (0.5 * s, 0.4 * s, 0.6 * s), cor)
    h = caixa(_id("roboC"), (0, 0, 0), (0.46 * s, 0.38 * s, 0.36 * s), tuple(c * 0.75 for c in cor[:3]) + (1,)); filho(b, h); h.location = (0, 0, 0.52 * s)
    for dx in (-0.1, 0.1):
        o = caixa(_id("roboO"), (0, 0, 0), (0.1 * s, 0.03, 0.1 * s), CIANO); filho(b, o); o.location = (dx * s, -0.2 * s, 0.54 * s)
    an = cilindro(_id("roboA"), (0, 0, 0), 0.02 * s, 0.22 * s, ESCURO, seg=6); filho(b, an); an.location = (0, 0, 0.8 * s)
    bo = esfera(_id("roboB"), (0, 0, 0), 0.06 * s, VERMELHO, sub=2); filho(b, bo); bo.location = (0, 0, 0.94 * s)
    return b

def diabinho(nome, loc, s=0.6, cor=VERMELHO):
    """'Programa de trapaça': cubo com chifres e cara de mau (símbolo original)."""
    c = caixa(nome, loc, (s, s, s), cor)
    esc = tuple(x * 0.55 for x in cor[:3]) + (1,)
    for dx in (-0.3, 0.3):
        h = cilindro(_id("chifre"), (0, 0, 0), s * 0.14, s * 0.42, esc, seg=8, r2=0.0); filho(c, h); h.location = (dx * s, 0, s * 0.68)
        o = caixa(_id("olhoD"), (0, 0, 0), (s * 0.22, s * 0.04, s * 0.12), BRANCO); filho(c, o); o.location = (dx * s * 0.75, -s * 0.52, s * 0.12)
        o.rotation_euler = (0, math.radians(22 if dx < 0 else -22), 0)
    b = caixa(_id("bocaD"), (0, 0, 0), (s * 0.5, s * 0.04, s * 0.08), ESCURO); filho(c, b); b.location = (0, -s * 0.52, -s * 0.22)
    return c

def lupa(nome, loc, R=0.45):
    r = vazio(nome, loc)
    a = anel(_id("lupaA"), (0, 0, 0), R, R * 0.14, ESCURO); filho(r, a); a.location = (0, 0, 0); a.rotation_euler = (math.radians(90), 0, 0)
    v = cilindro(_id("lupaV"), (0, 0, 0), R * 0.9, 0.03, (0.70, 0.95, 1.0, 1), seg=24, unico="vidro"); filho(r, v); v.rotation_euler = (math.radians(90), 0, 0); brilha(v)
    d = (R + R * 0.75) * 0.707
    c = cilindro(_id("lupaC"), (0, 0, 0), R * 0.16, R * 1.3, (0.55, 0.36, 0.20, 1), seg=8); filho(r, c); c.location = (d, 0, -d); c.rotation_euler = (0, math.radians(135), 0)
    return r

def escudo(nome, loc, s=0.6):
    r = vazio(nome, loc)
    a = cilindro(_id("escA"), (0, 0, 0), s, 0.14, AZUL, seg=6); filho(r, a); a.rotation_euler = (math.radians(90), 0, 0)
    b = cilindro(_id("escB"), (0, 0, 0), s * 0.62, 0.18, BRANCO, seg=6); filho(r, b); b.rotation_euler = (math.radians(90), 0, 0)
    return r

def olho(nome, loc, s=0.5):
    r = vazio(nome, loc)
    e = esfera(_id("olhoE"), (0, 0, 0), s, BRANCO, sub=3); filho(r, e); e.scale = (1, 0.5, 0.64); liso(e)
    i = esfera(_id("olhoI"), (0, 0, 0), s * 0.42, AZUL, sub=3); filho(r, i); i.location = (0, -s * 0.36, 0); i.scale = (1, 0.5, 1); liso(i)
    p = esfera(_id("olhoP"), (0, 0, 0), s * 0.2, ESCURO, sub=2); filho(r, p); p.location = (0, -s * 0.5, 0); p.scale = (1, 0.5, 1); liso(p)
    return r

def capanga(loc, s=1.0):
    """Trapaceiro mini (boneco genérico de capuz escuro com chifrinhos)."""
    r = vazio(_id("cap"), loc)
    c = cilindro(_id("capB"), (0, 0, 0), 0.27 * s, 0.7 * s, (0.20, 0.20, 0.27, 1), seg=12); filho(r, c); c.location = (0, 0, 0.35 * s)
    cb = esfera(_id("capC"), (0, 0, 0), 0.3 * s, random.choice([PELE, (0.75, 0.52, 0.38, 1), (0.50, 0.33, 0.22, 1)]), sub=3); filho(r, cb); cb.location = (0, 0, 0.96 * s); liso(cb)
    for dx in (-0.16, 0.16):
        h = cilindro(_id("capH"), (0, 0, 0), 0.07 * s, 0.22 * s, VERMELHO, seg=8, r2=0.0); filho(r, h); h.location = (dx * s, 0, 1.28 * s)
        o = esfera(_id("capO"), (0, 0, 0), 0.045 * s, ESCURO, sub=2); filho(r, o); o.location = (dx * 0.65 * s, -0.27 * s, 1.0 * s)
    return r

def bob(ob, t0, t1, dz=0.12, per=0.5, fase=0.0):
    z0 = ob.location.z; t = t0 + fase; k = 0
    while t < t1:
        ob.location.z = z0 + (dz if k % 2 else 0); ob.keyframe_insert("location", index=2, frame=f(t)); t += per; k += 1
    ob.location.z = z0

cam, alvo, cam_key, plano = camera_cartoon(24)
_ult = [None]
def ck(t, loc, tgt, corte=False):
    """Chave de câmera; corte=True repete o enquadramento anterior 2 quadros antes (corte seco na mesma zona)."""
    if corte and _ult[0]: cam_key(t - 0.07, *_ult[0])
    cam_key(t, loc, tgt); _ult[0] = (loc, tgt)

# =====================================================================
# ZONA H (x = -40) — arquibancada de 'contas' sendo banidas em onda  (bloco 0, gancho)
# =====================================================================
t0, t1 = S[0]
caixa("Hpiso", (-40, 2, -0.1), (24, 22, 0.2), (0.30, 0.34, 0.52, 1))
caixa("Hfundo", (-40, 11.5, 9), (24, 0.4, 20), (0.20, 0.18, 0.38, 1))
tb = 1.4
for row in range(7):
    z = row * 0.55; y = 1.6 + row * 1.25
    caixa(_id("degrau"), (-40, y, z / 2 - 0.05), (16, 1.25, max(z, 0.1)), (0.40 + 0.05 * (row % 2), 0.44, 0.66, 1))
    for k in range(15):
        x = -46.9 + k * 0.98 + (0.45 if row % 2 else 0)
        e = robo((x, y - 0.1, z), 0.95, random.choice(CORES))
        dt = (x + 47.5) * 0.07 + row * 0.02
        sumir(e, tb + dt, 0.18)
        xx = xis((x, y - 0.15, z + 0.55), 0.36); pop(xx, tb + dt + 0.12, dur=0.25)
eu0 = pixel("eu0", (-40.3, -0.6, 0)); girar(eu0["raiz"], 8); respirar(eu0, 0, t1 + 0.5)
espanto(eu0, 1.3, 1.5); pensar(eu0, T(0, "Como") - 0.1, 2.6)
ck(0, (-40.0, -8.5, 4.4), (-40.0, 5.0, 4.4)); ck(2.7, (-39.8, -7.6, 4.2), (-39.9, 4.0, 3.4))
ck(T(0, "Como") - 0.1, (-40.2, -4.4, 2.6), (-40.3, 0.5, 2.6)); ck(t1 - 0.05, (-40.3, -4.1, 2.6), (-40.3, 0.5, 2.7))

# =====================================================================
# ZONA R (x = -80) — fazenda de robôs farmando itens + os 3 truques  (bloco 1)
# =====================================================================
t0, t1 = S[1]
sala_fechada("R", -80, (0.34, 0.38, 0.50, 1), (0.16, 0.42, 0.48, 1), prof=5.4)
caixa("Ralto", (-80, 5.4, 11), (22, 0.4, 8), (0.16, 0.42, 0.48, 1))
hud("hudR", (-80, 5.1, 5.5), w=4.4, h=1.4)          # placa de HUD no cenário (backlog #3); o número vai na pílula
tbr = T(1, "novecentas")
for row in range(3):
    z = 1.0 + row * 0.6; y = 1.2 + row * 1.3
    caixa(_id("degR"), (-80, y, z / 2), (7.4, 1.3, z), (0.28 + 0.05 * row, 0.34, 0.50, 1))
    for k in range(5):
        x = -82.4 + k * 1.2 + (0.3 if row % 2 else 0) - 0.15
        e = robo((x, y, z), 1.0, (0.62, 0.66, 0.74, 1))
        cx = caixa(_id("item"), (x, y, z + 1.45), (0.3, 0.3, 0.3), AMARELO); bob(cx, t0, tbr + 1.6, 0.22, 0.32, (k + row) * 0.11)
        dt = k * 0.13 + row * 0.28
        sumir(e, tbr + dt, 0.18); sumir(cx, tbr + dt, 0.15)
        xx = xis((x, y - 0.1, z + 0.55), 0.42); pop(xx, tbr + dt + 0.12, dur=0.25)
ck(t0, (-80.0, -5.6, 3.3), (-80.0, 2.4, 2.9)); ck(tbr, (-80.0, -4.9, 3.2), (-80.0, 2.4, 2.8)); ck(T(1, "Mas") - 0.1, (-80.0, -4.7, 3.2), (-80.0, 2.4, 2.8))
# os três truques: lupa (assinatura), escudo (vigia no núcleo), olho (servidor)
eu1 = pixel("eu1", (-73.5, -0.5, 0)); girar(eu1["raiz"], -6); respirar(eu1, t0, t1 + 0.5)
tq = T(1, "três")
ICONES = [lupa("icLupa", (-75.1, 1.5, 3.95), 0.42), escudo("icEsc", (-73.5, 1.5, 4.15), 0.52), olho("icOlho", (-71.9, 1.5, 3.95), 0.5)]
for i, ic in enumerate(ICONES):
    pop(ic, tq + 0.18 * i, dur=0.3)
pensar(eu1, T(1, "Mas"), 1.6); comemorar(eu1, tq - 0.1, 1.2)
ck(T(1, "Mas"), (-73.5, -6.8, 2.8), (-73.5, -0.2, 2.8), corte=True); ck(t1 - 0.05, (-73.5, -6.3, 2.9), (-73.5, -0.2, 3.0))

# =====================================================================
# ZONA A (x = 0) — quarto: programa de trapaça deixa rastros na memória; lupa compara com a lista (bloco 2) + CTA (6)
# =====================================================================
t0, t1 = S[2]
sala_fechada("A", 0, (0.36, 0.40, 0.62, 1), (0.55, 0.38, 0.85, 1), prof=3.6, larg=30)
caixa("Aalto", (0, 3.6, 11), (30, 0.4, 8), (0.55, 0.38, 0.85, 1))
caixa("mesa", (1.0, 0.9, 1.0), (3.9, 1.2, 0.12), (0.30, 0.22, 0.18, 1))
for dx in (-1.7, 1.7): caixa(_id("peM"), (1.0 + dx, 0.9, 0.5), (0.12, 1.0, 1.0), (0.18, 0.18, 0.22, 1))
pc = caixa("pcA", (2.2, 0.9, 1.96), (0.9, 1.0, 1.8), (0.12, 0.12, 0.16, 1))
led = caixa("ledA", (0, 0, 0), (0.08, 0.04, 1.4), ROXO, unico="ledA"); filho(pc, led); led.location = (-0.3, -0.51, 0); brilha(led)
mon = caixa("monA", (0.5, 1.1, 1.95), (1.9, 0.1, 1.1), ESCURO)
tela = caixa("telaA", (0, 0, 0), (1.76, 0.03, 0.96), (0.30, 0.85, 1.0, 1), unico="telaA"); filho(mon, tela); tela.location = (0, -0.06, 0); brilha(tela)
caixa("peMon", (0.5, 1.15, 1.25), (0.14, 0.14, 0.4), ESCURO); caixa("teclado", (0.5, 0.5, 1.1), (1.2, 0.4, 0.06), (0.85, 0.85, 0.9, 1))
trap = pixel("trap", (-1.2, -0.3, 0), moletom=(0.22, 0.22, 0.28, 1), calca=(0.10, 0.10, 0.12, 1), escala=0.9); girar(trap["raiz"], 22)
respirar(trap, t0, t1); comemorar(trap, T(2, "programa") - 0.1, 1.2); espanto(trap, T(2, "rastros"), 1.4)
visivel(trap["raiz"], t0 - 0.3, t1 + 0.1)
tpg = T(2, "programa"); tra = T(2, "rastros"); tas = T(2, "assinatura"); tcp = T(2, "compara"); tli = T(2, "lista"); tco = T(2, "conhecidas")
dia = diabinho("diaA", (2.2, 0.7, 3.35), 0.62); pop(dia, tpg, dur=0.3); bob(dia, tpg + 0.4, t1, 0.12, 0.35); visivel(dia, tpg - 0.1, t1 + 0.1)
# pente de memória (RAM) flutuando acima da mesa
ram = caixa("ram", (0.4, 2.2, 4.4), (3.2, 0.12, 0.9), (0.15, 0.60, 0.32, 1), unico="ram")
for k in range(4):
    c = caixa(_id("chip"), (0, 0, 0), (0.55, 0.06, 0.5), ESCURO); filho(ram, c); c.location = (-1.14 + k * 0.76, -0.08, 0.08)
ct = caixa("contatos", (0, 0, 0), (3.0, 0.06, 0.14), AMARELO); filho(ram, ct); ct.location = (0, -0.05, -0.42)
pop(ram, T(2, "então"), dur=0.3); visivel(ram, T(2, "então") - 0.1, t1 + 0.1)
# trilha de pontinhos do programa até a memória + 5 'pegadas' (a assinatura) na memória
for i in range(5):
    u = (i + 1) / 6; p = bez((2.2, 0.7, 3.5), (2.4, 1.2, 4.6), (1.5, 2.0, 4.5), u)
    d = esfera(_id("trl"), p, 0.09, VERMELHO, sub=2); pop(d, T(2, "deixa") + 0.07 * i, dur=0.2); visivel(d, T(2, "deixa"), t1 + 0.1)
PEG = [(-1.14, 0.12), (-0.5, -0.1), (0.0, 0.16), (0.55, -0.08), (1.14, 0.1)]
pegadas = vazio("pegadas", (0.4, 2.06, 4.4))
for i, (px, pz) in enumerate(PEG):
    d = esfera(_id("peg"), (0, 0, 0), 0.14, VERMELHO, sub=2, unico="peg"); filho(pegadas, d); d.location = (px, 0, pz + 0.08); d.scale = (1, 0.5, 1)
    pop(d, tra + 0.12 * i, dur=0.2); d.scale = (1, 0.5, 1)
BRILHO.append(mat(VERMELHO, "peg")); visivel(pegadas, tra - 0.1, t1 + 0.1)
destacar(ram.data.materials[0], T(2, "memória"), (0.15, 0.60, 0.32, 1), 0.7)
# a lupa varre a memória e depois leva a amostra até a lista
lp = lupa("lupaA", (-1.3, 1.5, 4.45), 0.5); pop(lp, tas - 0.35, dur=0.25); visivel(lp, tas - 0.4, t1 + 0.1)
caminho(lp, tas - 0.1, tcp - 0.05, lambda u: (-1.3 + 2.9 * suave(u), 1.5, 4.45 + 0.1 * math.sin(u * 9)), orientar=False)
caminho(lp, tcp, tli + 0.1, lambda u: (-3.4 + 0.7 * suave(u), 1.9, 2.5 + 0.2 * suave(u)), orientar=False)
# lista de trapaças conhecidas (placa com 5 linhas); a amostra (tira com as mesmas 5 pegadas) chega e casa com a linha 3
lista = caixa("lista", (-6.0, 3.0, 3.8), (3.2, 0.15, 3.6), (0.12, 0.13, 0.20, 1))
linhas = []
for j in range(5):
    z = 5.0 - j * 0.6
    ic = caixa(_id("liI"), (-7.1, 2.9, z), (0.36, 0.06, 0.36), [ROXO, AMARELO, VERMELHO, AZUL, VERDE][j])
    ba = caixa(_id("liB"), (-5.75, 2.9, z), (2.0, 0.06, 0.34), (0.90, 0.92, 0.98, 1), unico=f"li{j}"); linhas.append(ba)
    filho(lista, ic, ba); ic.location = (-1.1, -0.1, z - 3.8); ba.location = (0.25, -0.1, z - 3.8)
    if j == 2:
        for i, (px, pz) in enumerate(PEG):
            d = esfera(_id("pegL"), (0, 0, 0), 0.085, VERMELHO, sub=2); filho(ba, d); d.location = (px * 0.62, -0.04, pz * 0.5); d.scale = (1, 0.4, 1)
visivel(lista, t0 - 0.2, t1 + 0.1)
amo = caixa("amostra", (0.4, 2.0, 4.4), (2.0, 0.08, 0.5), (0.15, 0.60, 0.32, 1), unico="amo")
for i, (px, pz) in enumerate(PEG):
    d = esfera(_id("pegA"), (0, 0, 0), 0.085, VERMELHO, sub=2); filho(amo, d); d.location = (px * 0.62, -0.05, pz * 0.5); d.scale = (1, 0.4, 1)
visivel(amo, tcp - 0.05, t1 + 0.1)
caminho(amo, tcp - 0.05, tli + 0.15, lambda u: bez((-1.2, 2.0, 4.6), (-2.6, 1.6, 4.4), (-3.25, 2.6, 3.8), suave(u)), orientar=False)
mli = linhas[2].data.materials[0]; mam = amo.data.materials[0]
for m, base in ((mli, (0.90, 0.92, 0.98, 1)), (mam, (0.15, 0.60, 0.32, 1))):
    cor_key(m, tco - 0.1, base); cor_key(m, tco + 0.05, AMARELO); cor_key(m, tco + 0.3, base); cor_key(m, tco + 0.5, AMARELO)
ligacao = tubo("ligacao", (-4.75, 2.85, 3.8), (-4.2, 2.65, 3.8), 0.07, AMARELO); visivel(ligacao, tco, t1 + 0.1)
xa = xis((-3.25, 2.3, 3.8), 0.7); pop(xa, tco + 0.35, dur=0.25); visivel(xa, tco + 0.3, t1 + 0.1)
ck(t0, (0.4, -6.2, 2.5), (0.4, 0.6, 2.4)); ck(tpg + 0.3, (0.7, -6.0, 2.8), (0.8, 0.8, 2.8))
ck(T(2, "então") - 0.1, (0.6, -6.6, 3.5), (0.5, 1.5, 3.6)); ck(tas - 0.5, (0.6, -6.4, 3.6), (0.5, 1.5, 3.7))
ck(tas - 0.15, (0.4, -3.6, 4.4), (0.4, 2.2, 4.35)); ck(tcp - 0.1, (0.5, -3.3, 4.4), (0.5, 2.2, 4.35))
ck(tcp, (-5.3, -4.6, 3.7), (-5.3, 3.0, 3.6), corte=True); ck(t1 - 0.05, (-5.2, -4.1, 3.7), (-5.2, 3.0, 3.7))

# =====================================================================
# ZONA K (x = 40) — o 'prédio' do sistema: programas em cima, sistema no meio, núcleo (kernel) embaixo  (bloco 3)
# =====================================================================
t0, t1 = S[3]
caixa("Kpiso", (40, 2, -0.1), (30, 22, 0.2), (0.26, 0.28, 0.44, 1))
caixa("Kfundo", (40, 6.0, 7), (30, 0.4, 16), (0.15, 0.16, 0.32, 1))
ANDAR = [(0.44, 0.36, 0.70, 1), (0.28, 0.52, 0.92, 1), (0.55, 0.82, 1.0, 1)]
for i, cor in enumerate(ANDAR):
    z0 = 0.1 + i * 2.5
    caixa(_id("andF"), (41, 2.7, z0 + 1.2), (5.0, 0.2, 2.4), cor, unico=f"and{i}")
    caixa(_id("andP"), (41, 1.7, z0), (5.2, 2.2, 0.18), tuple(c * 0.7 for c in cor[:3]) + (1,))
    for dx in (-2.5, 2.5): caixa(_id("andL"), (41 + dx, 1.7, z0 + 1.2), (0.16, 2.2, 2.4), tuple(c * 0.8 for c in cor[:3]) + (1,))
caixa("Kteto", (41, 1.7, 7.6), (5.4, 2.4, 0.2), (0.40, 0.60, 0.80, 1))
for k, cor in enumerate((AMARELO, VERDE, (1.0, 0.55, 0.70, 1))):      # programas comuns no andar de cima
    a = caixa(_id("app"), (40.7 + k * 1.0, 2.2, 5.62), (0.6, 0.6, 0.6), cor); bob(a, t0, t1, 0.06, 0.6, k * 0.2)
# andar do meio: botão de ligar (liga junto com o sistema)
bt = anel("botao", (41, 2.5, 3.75), 0.55, 0.09, CINZA, unico="pw"); bt.rotation_euler = (math.radians(90), 0, 0)
caixa("botaoB", (41, 2.5, 4.2), (0.16, 0.14, 0.62), CINZA, unico="pw")
mpw = bt.data.materials[0]; tlg = T(3, "liga"); cor_key(mpw, tlg - 0.15, CINZA); cor_key(mpw, tlg + 0.1, VERDE)
# andar de baixo: o núcleo (chip dourado)
chip = caixa("nucleo", (41.2, 2.5, 1.35), (1.3, 0.2, 1.3), AMARELO, unico="nuc")
for k in range(4):
    for sx in (-1, 1): caixa(_id("pino"), (41.2 + sx * 0.78, 2.5, 0.9 + k * 0.3), (0.26, 0.1, 0.1), (0.75, 0.75, 0.8, 1))
tes = T(3, "esconder"); tsi = T(3, "sistema"); tvg = T(3, "vigia"); tnu = T(3, "núcleo"); tke = T(3, "kernel")
# a lupa comum procura só no andar de cima
lk = lupa("lupaK", (42.2, 1.2, 6.2), 0.45)
caminho(lk, t0, tsi + 1.2, lambda u: (41.6 + 1.0 * math.sin(u * 7), 1.2, 6.25 + 0.2 * math.sin(u * 11)), orientar=False)
dk = diabinho("diaK", (39.6, 1.5, 5.5), 0.55)
def desce(u):
    P = [(39.6, 1.5, 5.5), (37.9, 1.0, 5.5), (37.9, 1.0, 0.8), (39.9, 1.4, 0.55)]
    v = u * 3; i = min(2, int(v)); return lerp(P[i], P[i + 1], suave(v - i))
caminho(dk, tes - 0.1, tsi + 0.35, desce, orientar=False)
# o vigia (anti-cheat de núcleo): robô azul com escudo e lanterna
vg = robo((42.6, 1.4, 0.2), 1.7, (0.25, 0.50, 1.0, 1)); pop(vg, tvg - 0.1, dur=0.3)
ev = escudo("escV", (41.95, 1.0, 0.95), 0.36); pop(ev, tvg + 0.1, dur=0.3)
feixe = cilindro("feixe", (41.0, 1.2, 1.15), 0.06, 1.9, (1.0, 0.95, 0.55, 1), seg=16, r2=0.55, unico="feixe"); feixe.rotation_euler = (0, math.radians(-90 - 14), 0)
visivel(feixe, tnu - 0.05); brilha(feixe)
destacar(chip.data.materials[0], tke, AMARELO, 0.1); destacar(bpy.data.materials[mat(ANDAR[0], "and0").name], tnu, ANDAR[0], 0.9)
for k in range(8): key(dk, "location", tke - 0.1 + k * 0.07, (39.9 + (0.08 if k % 2 else -0.08), 1.4, 0.55))
sumir(dk, tke + 0.55, 0.25); xk = xis((39.9, 1.2, 0.75), 0.6); pop(xk, tke + 0.25, dur=0.25)
gK = pixel("guiaK", (38.3, -1.3, 0), escala=0.72); girar(gK["raiz"], 22); respirar(gK, t0, t1 + 0.5)
pensar(gK, T(3, "Então"), 1.6); apontar(gK, tvg - 0.2, 1.6, "D", 30); comemorar(gK, tke + 0.2, 1.2)
ck(t0, (40.9, -5.8, 6.5), (41.0, 2.0, 6.25)); ck(tes, (40.9, -5.6, 6.4), (41.0, 2.0, 6.2))
ck(tsi + 0.4, (40.6, -5.8, 2.2), (40.8, 2.0, 1.6)); ck(T(3, "Então") + 0.4, (40.6, -8.4, 2.5), (40.8, 2.0, 1.8))
ck(tnu - 0.25, (40.6, -8.2, 2.5), (40.8, 2.0, 1.8)); ck(tnu + 0.3, (41.0, -4.9, 1.7), (41.0, 2.0, 1.35)); ck(t1 - 0.05, (41.0, -4.6, 1.7), (41.0, 2.0, 1.35))

# =====================================================================
# ZONA S (x = 86) — trapaça nova -> o servidor olha como você joga; a IA aprende assistindo partidas  (bloco 4)
# =====================================================================
t0, t1 = S[4]
TNO = T(4, "Counter") - 0.28   # "No Counter-Strike" (T(4, "No") casaria com "nova?")
data_center(86, n=12)
caixa("Salto", (86, 5.0, 11), (22, 0.4, 8), (0.20, 0.24, 0.42, 1))
gS = pixel("guiaS", (78.7, -1.0, 0)); girar(gS["raiz"], 10); respirar(gS, t0, T(4, "Então") + 0.3)
dn = diabinho("diaNovo", (80.0, -0.5, 2.95), 0.5, cor=ROXO); pop(dn, T(4, "trapaça"), dur=0.3); bob(dn, T(4, "trapaça") + 0.4, T(4, "Então") + 0.2, 0.1, 0.3)
pensar(gS, t0 + 0.1, 2.2)
ck(t0, (79.2, -5.7, 2.6), (79.3, -0.6, 2.65)); ck(T(4, "Então") - 0.1, (79.3, -5.4, 2.6), (79.3, -0.6, 2.7))
# palco: 3 alvos + uma mira (seta) que pula de alvo em alvo rápido demais; o servidor com olho observa de cima
ALVOS = [(84.7, 3.0, 3.0), (86.0, 3.0, 3.5), (87.3, 3.0, 3.0)]
mats_alvo = []
for i, (ax, ay, az) in enumerate(ALVOS):
    caixa(_id("poste"), (ax, ay + 0.1, az / 2), (0.12, 0.12, az), CINZA)
    for r, cor, un, dy in ((0.52, VERMELHO, None, 0.0), (0.36, BRANCO, None, -0.04), (0.2, VERMELHO, f"alvo{i}", -0.08)):
        d = cilindro(_id("alvo"), (ax, ay + dy, az), r, 0.1, cor, seg=24, unico=un); d.rotation_euler = (math.radians(90), 0, 0)
    mats_alvo.append(mat(VERMELHO, f"alvo{i}"))
PIV = (86.0, 0.3, 2.3)
cilindro("pedestal", (86.0, 0.3, 1.1), 0.34, 2.2, CINZA, seg=16); esfera("rotula", PIV, 0.3, ESCURO, sub=3)
mira = vazio("mira", PIV); mira.rotation_mode = "XYZ"
br = caixa("miraB", (0, 0, 0), (0.2, 1.3, 0.2), (1.0, 0.55, 0.15, 1)); filho(mira, br); br.location = (0, 0.75, 0)
pt = cilindro("miraP", (0, 0, 0), 0.24, 0.45, (1.0, 0.55, 0.15, 1), seg=12, r2=0.0); filho(mira, pt); pt.location = (0, 1.6, 0); pt.rotation_euler = (math.radians(-90), 0, 0)
def ang(i):
    ax, ay, az = ALVOS[i]; dx, dy, dz = ax - PIV[0], ay - PIV[1], az - PIV[2]
    return (math.atan2(dz, math.hypot(dx, dy)), 0, math.atan2(-dx, dy))
tmi = T(4, "mira"); ten = T(4, "Então")
key(mira, "rotation_euler", ten, ang(1)); key(mira, "rotation_euler", ten + 1.0, ang(0)); key(mira, "rotation_euler", tmi - 0.1, ang(2))
SEQ = [0, 2, 1, 0, 2, 1, 2, 0, 1, 2, 0, 1, 2]
for k, i in enumerate(SEQ):
    ts = tmi + k * 0.2
    key(mira, "rotation_euler", ts, ang(i), interp="CONSTANT")
    tr = tubo(_id("tiro"), PIV, ALVOS[i], 0.035, AMARELO, unico="tiro"); visivel(tr, ts + 0.02, ts + 0.13)
    m = mats_alvo[i]; cor_key(m, ts, VERMELHO); cor_key(m, ts + 0.04, AMARELO); cor_key(m, ts + 0.16, VERMELHO)
BRILHO.append(mat(AMARELO, "tiro"))
srv = caixa("srvOlho", (86.0, 3.0, 4.75), (3.9, 0.8, 1.0), (0.14, 0.16, 0.26, 1))
for k in range(6):
    l = caixa(_id("ledS"), (0, 0, 0), (0.3, 0.04, 0.1), VERDE); filho(srv, l); l.location = (-1.6 + (k if k < 3 else k + 5) * 0.4, -0.42, -0.3)
ol = olho("olhoS", (86.0, 2.5, 4.8), 0.56); pop(ol, T(4, "olha") - 0.15, dur=0.3)
lampS = esfera("lampS", (84.4, 3.0, 5.45), 0.22, VERDE, sub=3, unico="lampS"); liso(lampS); ml = lampS.data.materials[0]
td2 = T(4, "demais", 1); cor_key(ml, td2 - 0.2, VERDE)
for k in range(8): cor_key(ml, td2 + k * 0.18, VERMELHO if k % 2 == 0 else (0.45, 0.08, 0.08, 1))
ck(ten, (86.0, -7.2, 3.6), (86.0, 1.4, 3.15), corte=True); ck(tmi, (86.0, -6.8, 3.6), (86.0, 1.4, 3.2)); ck(TNO - 0.1, (86.0, -6.4, 3.6), (86.0, 1.4, 3.25))
# a IA que aprende assistindo partidas: robô de cabeça grande + 3 telinhas de 'partida'
tia = T(4, "uma")
caixa("iaCorpo", (92.9, 2.0, 1.0), (1.5, 1.1, 2.0), (0.20, 0.24, 0.42, 1))
iac = caixa("iaCabeca", (92.9, 1.9, 2.95), (2.2, 1.5, 1.6), BRANCO)
vis = caixa("iaVisor", (0, 0, 0), (1.8, 0.06, 0.7), ESCURO); filho(iac, vis); vis.location = (0, -0.77, 0.05)
for dx in (-0.45, 0.45):
    o = cilindro(_id("iaO"), (0, 0, 0), 0.2, 0.06, CIANO, seg=20, unico="iaO"); filho(iac, o); o.location = (dx, -0.81, 0.05); o.rotation_euler = (math.radians(90), 0, 0)
BRILHO.append(mat(CIANO, "iaO"))
an = cilindro("iaAnt", (0, 0, 0), 0.04, 0.5, ESCURO, seg=8); filho(iac, an); an.location = (0, 0, 1.05)
lia = esfera("iaLamp", (0, 0, 0), 0.16, AMARELO, sub=3, unico="iaL"); filho(iac, lia); lia.location = (0, 0, 1.38)
k = 0; t = tia
while t < t1:
    cor_key(lia.data.materials[0], t, AMARELO if k % 2 == 0 else CIANO); t += 0.3; k += 1
key(iac, "rotation_euler", tia, (0, 0, 0)); key(iac, "rotation_euler", T(4, "aprende"), (0, 0, math.radians(-14))); key(iac, "rotation_euler", t1, (0, 0, math.radians(-18)))
for j in range(3):
    z = 2.0 + j * 0.95
    mo = caixa(_id("tvP"), (95.0, 1.6, z), (1.2, 0.1, 0.78), ESCURO); mo.rotation_euler = (0, 0, math.radians(-12))
    tl = caixa(_id("tvT"), (0, 0, 0), (1.08, 0.03, 0.66), (0.25, 0.62, 0.40, 1), unico=f"tvT{j}"); filho(mo, tl); tl.location = (0, -0.06, 0); brilha(tl)
    for q in range(2):
        b = esfera(_id("jog"), (0, 0, 0), 0.07, [AMARELO, VERMELHO][q], sub=2); filho(mo, b)
        caminho(b, tia, t1, lambda u, j=j, q=q: (0.36 * math.sin(u * 14 + j * 2 + q * 3), -0.1, 0.2 * math.cos(u * 9 + j + q * 2)), orientar=False, passo=2)
    pop(mo, T(4, "assistindo") - 0.6 + j * 0.15, dur=0.3)
    t = T(4, "aprende") + j * 0.2
    while t < t1:   # 'aprendizado': bolinhas indo das telas para a cabeça
        p = esfera(_id("dado"), (0, 0, 0), 0.08, CIANO, sub=2, unico="iaO"); visivel(p, t, t + 0.5)
        caminho(p, t, t + 0.5, lambda u, z=z: bez((94.4, 1.5, z), (94.0, 1.2, z + 0.4), (93.9, 1.3, 3.0), u), orientar=False); t += 0.45
gS2 = pixel("guiaS2", (91.2, -0.9, 0), escala=0.8); girar(gS2["raiz"], 18); respirar(gS2, TNO - 0.3, t1 + 0.5)
apontar(gS2, tia - 0.1, 1.6, "D", 50); comemorar(gS2, T(4, "assistindo"), 1.2)
ck(TNO, (93.1, -6.4, 3.0), (93.1, 1.0, 2.8), corte=True); ck(t1 - 0.05, (93.2, -6.0, 3.0), (93.2, 1.0, 2.9))

# =====================================================================
# ZONA W (x = 120) — pegou, mas o banimento demora (relógio/calendário); depois vem a onda  (bloco 5)
# =====================================================================
t0, t1 = S[5]
sala_fechada("W", 120, (0.95, 0.80, 0.58, 1), (0.48, 0.82, 0.70, 1), prof=4.2, larg=30)
caixa("Walto", (120, 4.2, 10), (30, 0.4, 8), (0.48, 0.82, 0.70, 1))
caixa("palco", (121.0, 2.3, 1.0), (6.6, 1.9, 2.0), (0.86, 0.50, 0.38, 1))
XS = [119.0, 120.0, 121.0, 122.0, 123.0]
tpe = T(5, "pegou"); tdm = T(5, "demorar"); ton = T(5, "onda"); tw0 = ton - 0.15; tw1 = T(5, "junto") + 0.25
TAGS = [tpe, T(5, "dias"), T(5, "semanas"), T(5, "criador"), T(5, "descobrir")]
ORD = [2, 0, 4, 1, 3]
def xonda(t): return 127.0 + (114.0 - 127.0) * (t - tw0) / (tw1 - tw0)
for n, x in enumerate(XS):
    c = capanga((x, 2.1, 2.0), 1.0); bob(c, t0, tw0, 0.1, 0.42, n * 0.13)
    tg = vazio(_id("tag"), (0, 0, 1.85)); filho(c, tg)
    b1 = caixa(_id("tagB"), (0, 0, 0), (0.12, 0.1, 0.36), AMARELO, unico="tag"); filho(tg, b1); b1.location = (0, 0, 0.1)
    b2 = esfera(_id("tagP"), (0, 0, 0), 0.08, AMARELO, sub=2, unico="tag"); filho(tg, b2); b2.location = (0, 0, -0.2)
    pop(tg, TAGS[ORD.index(n)], dur=0.25)
    ti = tw0 + (x + 0.9 - 127.0) / (114.0 - 127.0) * (tw1 - tw0)
    sumir(c, ti, 0.12); xx = xis((x, 1.9, 2.75), 0.6); pop(xx, ti + 0.3, dur=0.25)
BRILHO.append(mat(AMARELO, "tag"))
# relógio de parede (ponteiros girando rápido = o tempo passando) + folhas do calendário voando
rel = cilindro("relogio", (121.0, 3.95, 5.55), 1.0, 0.16, BRANCO, seg=32); rel.rotation_euler = (math.radians(90), 0, 0)
ar = anel("relAro", (121.0, 3.9, 5.55), 1.0, 0.09, ESCURO); ar.rotation_euler = (math.radians(90), 0, 0)
for nome, comp, vel in (("pontG", 0.8, 6), ("pontP", 0.5, 0.5)):
    pv = vazio(nome, (121.0, 3.82, 5.55)); pv.rotation_mode = "XYZ"
    h = caixa(_id("pont"), (0, 0, 0), (0.09, 0.05, comp), ESCURO); filho(pv, h); h.location = (0, 0, comp / 2)
    key(pv, "rotation_euler", t0, (0, 0, 0)); key(pv, "rotation_euler", tdm, (0, math.radians(40 * vel), 0))
    key(pv, "rotation_euler", tw0, (0, math.radians(40 * vel + 360 * vel * 1.5), 0)); key(pv, "rotation_euler", t1, (0, math.radians(40 * vel + 360 * vel * 1.6), 0)); linear(pv)
caixa("calBase", (123.2, 3.9, 5.5), (0.9, 0.12, 1.0), BRANCO); caixa("calTopo", (123.2, 3.85, 5.92), (0.9, 0.14, 0.22), VERMELHO)
for k in range(7):
    tk = T(5, "dias") - 0.1 + k * 0.42
    fo = caixa(_id("folha"), (123.2, 3.7, 5.4), (0.8, 0.03, 0.8), BRANCO); visivel(fo, tk, tk + 0.8)
    caminho(fo, tk, tk + 0.8, lambda u, k=k: bez((123.2, 3.7, 5.4), (124.0, 3.0, 6.2 + 0.2 * (k % 2)), (125.6, 2.4, 4.2), u), orientar=False)
# a onda de banimento: rolo azul com espuma varrendo o palco
onda = cilindro("onda", (127.0, 2.3, 2.9), 1.45, 2.3, (0.20, 0.50, 1.0, 1), seg=28); onda.rotation_mode = "XYZ"
for k in range(6):
    e = esfera(_id("espuma"), (0, 0, 0), 0.36 + 0.06 * (k % 2), BRANCO, sub=2); filho(onda, e); e.location = (1.3 * math.cos(k * 1.05), 1.3 * math.sin(k * 1.05), -1.0 + k * 0.4)
key(onda, "location", tw0, (127.0, 2.3, 2.9)); key(onda, "location", tw1, (114.0, 2.3, 2.9))
key(onda, "rotation_euler", tw0, (math.radians(90), 0, 0)); key(onda, "rotation_euler", tw1, (math.radians(90), math.radians(-520), 0)); linear(onda)
visivel(onda, tw0 - 0.05, tw1 + 0.05)
gW = pixel("guiaW", (118.9, -1.0, 0), escala=0.8); girar(gW["raiz"], 16); respirar(gW, t0, t1 + 0.5)
apontar(gW, tpe - 0.15, 1.2, "D", 55); pensar(gW, T(5, "Nem") - 0.1, 1.6); apontar(gW, tdm - 0.1, 1.5, "D", 75); espanto(gW, ton - 0.2, 1.0); comemorar(gW, T(5, "banido") + 0.1, 1.2)
ck(t0, (120.5, -6.6, 3.5), (120.7, 2.0, 3.2)); ck(tdm, (120.5, -6.9, 3.6), (120.7, 2.0, 3.5))
ck(T(5, "Aí") - 0.1, (120.6, -7.0, 3.6), (120.8, 2.0, 3.5)); ck(ton, (120.6, -7.6, 3.6), (120.8, 2.0, 3.2)); ck(t1 - 0.05, (120.6, -7.2, 3.5), (120.8, 2.0, 3.1))

# =====================================================================
# 6 — CTA de volta ao quarto (câmera aberta: o CTA não encosta na cabeça — backlog #9) + pedido de like
# =====================================================================
t0 = S[6][0]
st = pixel("pixelCTA", (-0.6, -0.6, 0)); girar(st["raiz"], 6); respirar(st, t0 - 0.3, FIM); visivel(st["raiz"], t0 - 0.3)
acenar(st, t0 + 0.15, 1.6); espanto(st, T(6, "roubado") - 0.15, 1.2); pensar(st, T(6, "Nunca") - 0.1, 1.2); apontar(st, T(6, "sorte") - 0.2, 1.3, "D", 60)
tlike = LEG[-1]["e"] + 1.3
comemorar(st, tlike + 0.2, 1.3); acenar(st, tlike + 1.9, 1.6)
ck(t0, (-0.5, -7.3, 2.9), (-0.5, 0.6, 2.6)); ck(tlike, (-0.5, -6.8, 2.9), (-0.5, 0.6, 2.6)); ck(FIM, (-0.5, -6.5, 2.9), (-0.5, 0.6, 2.6))

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
