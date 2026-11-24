"""Série 2 — 'Por que o GTA 6 roda a só 30 FPS, até no PS5 Pro?' (estilo C cartoon, mascote Pixel).
Visual 100 % original: TV e consoles genéricos sem marca, cidade de brinquedo, nada de arte do jogo. Uso:
blender -b --factory-startup -P cena_gta30.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
import bpy, sys, os, json, math, random
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
def T(i, palavra, n=0):
    hits = [x["s"] for x in LEG if x["seg"] == i and palavra.lower() in x["w"].lower()]
    return hits[min(n, len(hits) - 1)] if hits else seg_ini(i) + 0.5
S = [(seg_ini(i), seg_fim(i)) for i in range(NSEG)]

bpy.ops.wm.read_factory_settings(use_empty=True)
configurar_render()
scn = bpy.context.scene
scn.frame_start, scn.frame_end = 1, f(FIM)
random.seed(7)

AMARELO = (1.0, 0.82, 0.12, 1); VERDE = (0.20, 0.85, 0.40, 1); VERMELHO = (0.95, 0.22, 0.20, 1)
ROSA = (1.0, 0.55, 0.70, 1); ROXO = (0.60, 0.34, 0.95, 1); AZUL = (0.20, 0.55, 1.0, 1); BRANCO = (0.97, 0.97, 0.98, 1)
ESCURO = (0.10, 0.11, 0.14, 1); CORES = [(0.98, 0.45, 0.35, 1), (0.30, 0.70, 1.0, 1), (0.98, 0.80, 0.25, 1),
                                     (0.45, 0.85, 0.45, 1), (0.75, 0.50, 0.95, 1), (1.0, 0.60, 0.20, 1)]

def girar(ob, graus): ob.rotation_euler = (0, 0, math.radians(graus))
def de_baixo(ob):
    """Move a origem da caixa para a base (escala em Z cresce para cima)."""
    for v in ob.data.vertices: v.co.z += ob.dimensions.z / 2 / max(ob.scale.z, 1e-6)
    return ob
def sala(nome, x, piso, parede, prof=4.5):
    """Cenário fechado: piso + parede de fundo + 2 paredes laterais curtas (enquadramento sem vazio)."""
    caixa(nome + "Piso", (x, 0, -0.1), (22, 18, 0.2), piso)
    caixa(nome + "Fundo", (x, prof, 3.5), (22, 0.4, 7.0), parede)
    caixa(nome + "Rodape", (x, prof - 0.25, 0.2), (22, 0.12, 0.4), tuple(c * 0.8 for c in parede[:3]) + (1,))

def console(nome, loc, pro=False):
    """Console genérico SEM marca: torre branca com faixas pretas (Pro = 3 faixas)."""
    corpo = caixa(nome, (loc[0], loc[1], 1.0), (0.7, 1.4, 2.0), BRANCO, unico=nome)
    zs = (-0.45, 0.0, 0.45) if pro else (0.0,)
    for z in zs:
        fx = caixa(_id("faixa"), (0, 0, 0), (0.74, 1.44, 0.12), ESCURO); filho(corpo, fx); fx.location = (0, 0, z)
    led = esfera(_id("led"), (0, 0, 0), 0.06, (0.3, 0.7, 1.0, 1), sub=2); filho(corpo, led); led.location = (0, -0.72, 0.85)
    return corpo

def chip(nome, loc, s=1.0):
    """CPU = chip verde com 'cérebro' rosa em cima. Retorna (objeto, material do chip)."""
    base = caixa(nome, loc, (1.4 * s, 1.4 * s, 0.32 * s), (0.15, 0.60, 0.32, 1), unico=nome)
    for k in range(4):
        for lado in (-1, 1):
            p1 = caixa(_id("pino"), (0, 0, 0), (0.1 * s, 0.3 * s, 0.08 * s), (0.82, 0.82, 0.86, 1)); filho(base, p1)
            p1.location = ((-0.5 + k / 3) * s, lado * 0.82 * s, -0.05 * s)
            p2 = caixa(_id("pino"), (0, 0, 0), (0.3 * s, 0.1 * s, 0.08 * s), (0.82, 0.82, 0.86, 1)); filho(base, p2)
            p2.location = (lado * 0.82 * s, (-0.5 + k / 3) * s, -0.05 * s)
    for dx, dy, r in ((-0.18, 0, 0.36), (0.18, 0, 0.36), (0, 0.05, 0.4)):
        b = esfera(_id("cerebro"), (0, 0, 0), r * s, ROSA, sub=3); filho(base, b); b.location = (dx * s, dy * s, 0.42 * s)
        b.scale = (0.95, 0.85, 0.72); liso(b)
    return base, base.data.materials[0]

def carro(nome, cor):
    corpo = caixa(nome, (0, 0, 0), (0.46, 0.95, 0.3), cor)
    cab = caixa(_id("cab"), (0, 0, 0), (0.4, 0.5, 0.24), (0.78, 0.92, 1.0, 1)); filho(corpo, cab); cab.location = (0, -0.05, 0.25)
    return corpo

def npc(nome, loc, cor):
    corpo = capsula(nome, loc, 0.13, 0.28, cor)
    cab = esfera(_id("cabN"), (0, 0, 0), 0.15, random.choice([PELE, (0.75, 0.52, 0.38, 1), (0.50, 0.33, 0.22, 1)]), sub=2)
    filho(corpo, cab); cab.location = (0, 0, 0.42); return corpo

def trafego(ob, t0, t1, ini, vel, eixo, a, b, fixo, z, rotz):
    """Anda em linha reta com volta ao começo (wrap) — chave a cada quadro, sem 'varrer' a rua."""
    L = b - a; ob.rotation_euler = (0, 0, math.radians(rotz))
    for fr in range(f(t0), f(t1) + 1):
        t = (fr - 1) / 30.0; p = a + ((ini - a) + vel * (t - t0)) % L
        ob.location = (p, fixo, z) if eixo == "x" else (fixo, p, z)
        ob.keyframe_insert("location", frame=fr)

cam, alvo, cam_key, plano = camera_cartoon(24)

# =====================================================================
# ZONA A (x = 0) — sala gamer: TV genérica + console + Pixel  (blocos 0 e 6)
# =====================================================================
sala("A", 0, (0.36, 0.78, 0.74, 1), (0.98, 0.84, 0.40, 1))
caixa("rack", (1.0, 3.2, 0.45), (5.4, 1.4, 0.9), (0.55, 0.36, 0.24, 1))
tv = caixa("tv", (1.0, 3.4, 2.75), (4.4, 0.25, 2.6), ESCURO)
tela = caixa("tela", (0, 0, 0), (4.1, 0.05, 2.3), (0.55, 0.82, 1.0, 1)); filho(tv, tela); tela.location = (0, -0.14, 0)
chaoTela = caixa("chaoTela", (0, 0, 0), (4.1, 0.06, 0.5), (0.40, 0.80, 0.40, 1)); filho(tv, chaoTela); chaoTela.location = (0, -0.17, -0.9)
bola = esfera("bolaTV", (0, 3.15, 2.3), 0.28, AMARELO, sub=3); liso(bola)
cons = console("console", (3.9, 3.0))
caixa("tapete", (0.4, 0.6, 0.02), (5.0, 3.0, 0.04), (0.95, 0.45, 0.45, 1))
puff = esfera("puff", (-2.8, 1.6, 0.45), 0.75, (0.45, 0.55, 1.0, 1), sub=3); puff.scale = (1, 1, 0.62); liso(puff)
for k in range(3):
    caixa(_id("jogo"), (3.0 + k * 0.32, 2.7, 0.05 + 0.08 * k), (0.9, 0.7, 0.08), CORES[k])
eu = pixel("eu", (-1.6, 0.4, 0)); girar(eu["raiz"], 12); respirar(eu, 0, FIM)
# bola "pulando" na TV em DEGRAUS: cada posição é um quadro (a TV mostra uma sequência de desenhos)
def bola_tv(t0, t1, passo):
    k = 0; t = t0
    while t < t1:
        u = (k * 0.09) % 1.0
        key(bola, "location", t, (1.0 - 1.7 + 3.4 * u, 3.15, 1.85 + 1.3 * abs(math.sin(u * math.pi * 3))), interp="CONSTANT")
        t += passo; k += 1
bola_tv(0.0, S[1][0], 1 / 6)
t0, t1 = S[0]
apontar(eu, T(0, "trinta") - 0.2, 1.6, "D", 55)
destacar(cons.data.materials[0], T(0, "PlayStation"), BRANCO, 1.2)
pensar(eu, T(0, "Por") - 0.1, 1.4)
cam_key(t0, (0.4, -5.6, 2.3), (0.6, 2.0, 2.2)); cam_key(T(0, "Até"), (2.8, -5.0, 2.2), (3.1, 2.0, 2.0))
cam_key(T(0, "Por") - 0.2, (-0.6, -4.2, 2.3), (-1.2, 0.4, 2.4)); cam_key(t1 - 0.05, (-0.8, -4.0, 2.3), (-1.3, 0.4, 2.5))

# =====================================================================
# ZONA B (x = 40) — o flipbook: cada página é um quadro  (bloco 1)
# =====================================================================
t0, t1 = S[1]
sala("B", 40, (0.98, 0.88, 0.66, 1), (0.55, 0.78, 1.0, 1))
caixa("cavalete", (40.8, 2.2, 1.9), (0.25, 0.25, 3.8), (0.55, 0.36, 0.24, 1))
caixa("barraTopo", (40.8, 1.9, 4.05), (3.4, 0.4, 0.3), (0.55, 0.36, 0.24, 1))
tf_ini = T(1, "Cada"); t60 = T(1, "sessenta")
flips = []; t = tf_ini
while t < t1 + 0.4:
    flips.append(t); t += 0.25 if t < t60 else 0.125
NP = len(flips) + 3
for k in range(NP):
    h = vazio(_id("dobra"), (40.8, 1.6 + k * 0.012, 3.9))
    pg = caixa(_id("pag"), (0, 0, 0), (3.0, 0.02, 2.6), (1.0, 0.99, 0.94, 1)); filho(h, pg); pg.location = (0, 0, -1.35)
    u = (k * 0.08) % 1.0
    bx = -1.1 + 2.2 * u; bz = -2.35 + 1.6 * abs(math.sin(u * math.pi * 2))
    bb = esfera(_id("bolaP"), (0, 0, 0), 0.22, CORES[k % 6], sub=2); bb.scale = (1, 0.25, 1); filho(h, bb); bb.location = (bx, -0.03, bz)
    ln = caixa(_id("linhaP"), (0, 0, 0), (2.7, 0.01, 0.05), ESCURO); filho(h, ln); ln.location = (0, -0.02, -2.5)
    num = cilindro(_id("canto"), (0, 0, 0), 0.12, 0.02, CORES[(k + 2) % 6], seg=12); num.rotation_euler = (math.radians(90), 0, 0)
    filho(h, num); num.location = (1.25, -0.02, -0.25)
    tvis = 0 if k == 0 else (flips[k - 1] + 0.06 if k - 1 < len(flips) else FIM)
    tsome = flips[k] + 0.11 if k < len(flips) else None
    for o in (bb, num): visivel(o, tvis, tsome)
    if k < len(flips):
        tf = flips[k]; h.rotation_mode = "XYZ"
        key(h, "rotation_euler", tf, (0, 0, 0)); key(h, "rotation_euler", tf + 0.1, (math.radians(165), 0, 0))
        for o in (pg, ln): visivel(o, 0, tsome)
# cronômetro: 33 ms por quadro
crono = cilindro("crono", (41.7, 1.7, 4.75), 0.6, 0.2, BRANCO, seg=28); crono.rotation_euler = (math.radians(90), 0, 0)
aro = anel("aroCrono", (0, 0, 0), 0.62, 0.07, VERMELHO); filho(crono, aro); aro.location = (0, 0, 0); aro.rotation_euler = (0, 0, 0)
botao = cilindro("botaoCrono", (0, 0, 0), 0.14, 0.2, VERMELHO, seg=10); filho(crono, botao); botao.location = (0, 0.78, 0); botao.rotation_euler = (math.radians(90), 0, 0)
ponteiro = caixa("ponteiroC", (41.7, 1.56, 4.75), (0.06, 0.03, 0.5), ESCURO); ponteiro.rotation_mode = "XYZ"
for v in ponteiro.data.vertices: v.co.z += 0.22
tcr = T(1, "trinta", 1) - 0.3
visivel(crono, tcr); pop(crono, tcr); visivel(ponteiro, tcr); pop(ponteiro, tcr)
k = 0; t = tcr
while t < t1:
    key(ponteiro, "rotation_euler", t, (0, math.radians(36 * k * (2 if t > t60 else 1)), 0)); t += 0.25; k += 1
g1 = pixel("guia1", (38.5, 0.0, 0)); girar(g1["raiz"], 12); respirar(g1, t0, t1 + 1)
acenar(g1, t0 + 0.1, 1.3); apontar(g1, T(1, "quadro") - 0.3, 1.8, "D", 50)
apontar(g1, T(1, "trinta", 1) - 0.2, 1.6, "D", 75); espanto(g1, t60 - 0.1, 1.4)
cam_key(t0, (39.2, -4.4, 2.3), (39.2, 1.0, 2.4)); cam_key(T(1, "Cada"), (40.0, -5.6, 2.6), (40.0, 1.6, 2.7))
cam_key(T(1, "trinta", 1) - 0.4, (40.3, -5.4, 3.0), (40.4, 1.6, 3.2)); cam_key(t1 - 0.05, (40.1, -5.8, 2.9), (40.2, 1.6, 3.0))

# =====================================================================
# ZONA C (x = 80) — fábrica de quadros: CPU monta, GPU pinta  (blocos 2 e 5)
# =====================================================================
sala("C", 80, (0.70, 0.74, 0.86, 1), (0.98, 0.70, 0.52, 1))
caixa("esteira", (80.6, 0.0, 0.95), (9.2, 1.3, 0.3), (0.22, 0.24, 0.30, 1))
for x in (76.4, 80.6, 84.8):
    caixa(_id("pe"), (x, 0, 0.4), (0.3, 1.0, 0.8), (0.40, 0.42, 0.48, 1))
for k in range(18):
    caixa(_id("rolo"), (76.3 + k * 0.5, -0.66, 0.95), (0.08, 0.04, 0.26), (0.55, 0.57, 0.62, 1))
# estação CPU
opa = pixel("operario", (78.0, 1.3, 0), moletom=AZUL, escala=0.85); respirar(opa, 0, FIM)
capacete = esfera("capacete", (0, 0, 0), 0.6, AMARELO, sub=3); capacete.scale = (1.05, 1.05, 0.55); filho(opa["cabeca"], capacete); capacete.location = (0, 0.02, 0.98); liso(capacete)
poste = caixa("posteCPU", (76.9, 2.2, 1.7), (0.18, 0.18, 3.4), (0.40, 0.42, 0.48, 1))
chipF, mchipF = chip("chipFab", (76.9, 2.2, 3.55), 1.0)
# estação GPU (pintor)
pin = pixel("pintor", (82.8, 1.3, 0), moletom=ROXO, escala=0.85); respirar(pin, 0, FIM)
boina = cilindro("boina", (0, 0, 0), 0.5, 0.14, VERMELHO, seg=20); filho(pin["cabeca"], boina); boina.location = (0.12, 0.05, 1.08); boina.rotation_euler = (0, math.radians(-12), 0); liso(boina)
pincel = cilindro("pincel", (0, 0, 0), 0.05, 0.7, (0.55, 0.36, 0.24, 1), seg=8); filho(pin["cotoveloD"], pincel); pincel.location = (0, -0.1, -0.75)
ponta = esfera("pontaPincel", (0, 0, 0), 0.1, (0.95, 0.30, 0.55, 1), sub=2); filho(pincel, ponta); ponta.location = (0, 0, -0.4); ponta.scale = (1, 1, 1.6)
paleta = cilindro("paleta", (84.4, 1.2, 1.6), 0.5, 0.06, (0.95, 0.85, 0.62, 1), seg=16)
for j, c in enumerate(CORES[:4]):
    d = esfera(_id("tinta"), (0, 0, 0), 0.09, c, sub=2); filho(paleta, d); d.location = (math.cos(j * 1.4) * 0.3, math.sin(j * 1.4) * 0.3, 0.06)
coroa = cilindro("coroaGPU", (0, 0, 0), 0.38, 0.4, AMARELO, seg=8, r2=0.5); filho(pin["cabeca"], coroa); coroa.location = (0, 0, 1.35)
guiaC = pixel("guiaC", (76.0, -1.9, 0)); girar(guiaC["raiz"], 15); respirar(guiaC, 0, FIM)
X0, X1, VEL, CPUx, GPUx = 75.6, 85.6, 1.6, 78.0, 82.8
def fluxo(ta, tb, cada=0.9, ate=None):
    t = ta - (X1 - X0) / VEL
    while t < tb:
        ch = t + (X1 - X0) / VEL
        q = caixa(_id("quadro"), (X0, -0.05, 1.5), (0.95, 0.06, 0.78), BRANCO, unico=_id("qm"))
        mq = q.data.materials[0]
        for j in range(3):
            bl = caixa(_id("bloco"), (0, 0, 0), (0.18, 0.08, 0.18), CORES[(j + int(t * 3)) % 6]); filho(q, bl)
            bl.location = (-0.28 + j * 0.28, -0.06, -0.12 + 0.12 * (j % 2))
            tcpu = t + (CPUx - X0) / VEL + j * 0.08
            visivel(bl, tcpu, ch); pop(bl, tcpu)
        tgpu = t + (GPUx - X0) / VEL
        cor_key(mq, tgpu - 0.05, BRANCO); cor_key(mq, tgpu + 0.15, random.choice([(0.45, 0.80, 1.0, 1), (1.0, 0.78, 0.45, 1), (0.60, 0.92, 0.55, 1)]))
        visivel(q, max(0.01, t), ch)
        caminho(q, t, ch, lambda u: (X0 + (X1 - X0) * u, -0.05, 1.5), orientar=False)
        t += cada
def trabalho(P, ta, tb, ritmo=0.9, lado="D"):
    t = ta
    while t < tb - 0.6:
        apontar(P, t, ritmo * 0.8, lado, 40); t += ritmo
t0, t1 = S[2]
fluxo(t0 - 0.5, t1 + 0.3)
trabalho(opa, t0, t1, 0.9, "E"); trabalho(pin, t0 + 0.3, t1, 0.9, "D")
visivel(coroa, S[5][0] + 0.2)  # coroa só aparece no bloco 5
acenar(guiaC, t0 + 0.1, 1.2); apontar(guiaC, T(2, "CPU") - 0.3, 1.6, "D", 60); pensar(guiaC, T(2, "decide"), 1.4)
apontar(guiaC, T(2, "GPU") - 0.3, 1.8, "D", 45)
plano(t0, (77.4, 0.2), "geral", altura=1.9); plano(T(2, "CPU") - 0.4, (77.2, 0.6), "medio", altura=2.1)
plano(T(2, "GPU") - 0.4, (82.2, 0.8), "close", altura=2.0); plano(t1 - 0.05, (82.5, 0.8), "close", altura=2.0)

# ---- bloco 5: o Pro = pintor mais forte, mesma CPU ----
t0, t1 = S[5]
tds = T(5, "Segundo")
fluxo(t0, tds + 0.2, cada=0.9)
tf = T(5, "forte"); tg = T(5, "Ganhou")
pin["raiz"].keyframe_insert("scale", frame=f(tg)); pin["raiz"].scale = (1.15,) * 3; pin["raiz"].keyframe_insert("scale", frame=f(tg + 0.4)); pin["raiz"].scale = (0.85,) * 3
pop(coroa, t0 + 0.2)
comemorar(pin, tg + 0.2, 1.4); trabalho(pin, tf + 0.4, T(5, "Pintar"), 0.45, "D")
trabalho(opa, t0, tds, 0.9, "E")
destacar(mchipF, T(5, "CPU"), (0.15, 0.60, 0.32, 1), 1.2)
pensar(pin, T(5, "Pintar") + 0.1, 2.6)
apontar(guiaC, T(5, "CPU") - 0.2, 1.6, "D", 60); espanto(guiaC, T(5, "cérebro") - 0.2, 1.2)
plano(t0, (82.4, 0.6), "medio", altura=2.0); plano(tg + 0.3, (82.8, 0.9), "close", altura=2.2)
plano(T(5, "CPU") - 0.3, (77.4, 1.0), "medio", altura=2.4); plano(T(5, "Pintar") - 0.3, (80.4, 0.5), "geral", altura=2.0)
plano(tds - 0.12, (80.6, 0.5), "geral", altura=2.0)

# =====================================================================
# ZONA D (x = 120) — a cidade enorme: multidões, trânsito, batidas -> tarefas na CPU  (bloco 3)
# =====================================================================
t0, t1 = S[3]
caixa("Dpiso", (120, 2, -0.1), (30, 26, 0.2), (0.50, 0.80, 0.42, 1))
caixa("ruaH", (120, 0.9, 0.01), (30, 1.7, 0.04), (0.40, 0.42, 0.46, 1))
caixa("ruaV", (119.6, 2, 0.012), (1.7, 26, 0.04), (0.40, 0.42, 0.46, 1))
for k in range(14):
    caixa(_id("faixaR"), (113.5 + k * 1.0, 0.9, 0.04), (0.45, 0.06, 0.01), (1, 1, 1, 1))
for y in (-0.25, 2.05):
    caixa(_id("calcada"), (120, y, 0.06), (30, 0.6, 0.12), (0.88, 0.86, 0.80, 1))
for x in range(9):
    xx = 113.6 + x * 1.55
    if abs(xx - 119.6) < 1.3: continue
    predio((xx, 3.6 + (x % 2) * 0.6, 0), 1.3, 1.3, 1.6 + (x * 7 % 5) * 0.8, PREDIOS[x % 6])
for x in range(9):
    xx = 113.2 + x * 1.6
    if abs(xx - 119.6) < 1.3: continue
    predio((xx, 6.2, 0), 1.4, 1.4, 3.5 + (x * 5 % 4) * 1.0, PREDIOS[(x + 3) % 6])
for x in (114.5, 116.2, 123.2, 125.0):
    arvore((x, 2.65, 0), 0.45)
carros = []
for lane, (eixo, fixo, vel, rot, a, b) in enumerate((("x", 0.55, 2.4, -90, 112.0, 128.0), ("x", 1.25, -2.0, 90, 112.0, 128.0),
                                                      ("y", 119.25, 2.2, 0, -5.0, 9.0), ("y", 119.95, -2.6, 180, -5.0, 9.0))):
    n = 6 if eixo == "x" else 4
    for k in range(n):
        c = carro(_id("carro"), CORES[(k + lane) % 6]); carros.append(c)
        L = b - a; ini = a + (k + random.random() * 0.4) * L / n
        trafego(c, t0 - 0.2, t1 + 0.2, ini, vel, eixo, a, b, fixo, 0.2, rot)
        visivel(c, t0 - 0.2, t1 + 0.2)
for k in range(26):
    y = random.choice((-0.25, 2.05)); cor = random.choice(CORES)
    p = npc(_id("npc"), (0, 0, 0), cor)
    vel = random.choice((-1, 1)) * random.uniform(0.6, 1.0)
    trafego(p, t0 - 0.2, t1 + 0.2, random.uniform(112, 128), vel, "x", 112.0, 128.0, y + random.uniform(-0.15, 0.15), 0.42, 0)
    visivel(p, t0 - 0.2, t1 + 0.2)
# batida no cruzamento
tb = T(3, "batidas")
ca = carro("batidaA", VERMELHO); cb = carro("batidaB", AMARELO)
caminho(ca, tb - 1.2, tb, lambda u: (115.0 + 4.3 * u, 0.55, 0.2), orientar=False); ca.rotation_euler = (0, 0, math.radians(-90))
caminho(cb, tb - 1.2, tb, lambda u: (119.25, -3.4 + 3.5 * u, 0.2), orientar=False)
cb.rotation_mode = "XYZ"; ca.rotation_mode = "XYZ"
key(ca, "rotation_euler", tb, (0, 0, math.radians(-90))); key(ca, "rotation_euler", tb + 0.5, (0, 0, math.radians(-140)))
key(cb, "rotation_euler", tb, (0, 0, 0)); key(cb, "rotation_euler", tb + 0.5, (0, 0, math.radians(35)))
for c in (ca, cb): visivel(c, tb - 1.2, t1 + 0.2)
explosao((119.3, 0.4, 0.5), tb, r=0.9, n=8)
# CPU da cidade + pilha de tarefas
caixa("pedestalCPU", (122.7, -2.0, 0.55), (1.8, 1.8, 1.1), (0.35, 0.38, 0.46, 1))
chipD, mchipD = chip("chipCidade", (122.7, -2.0, 1.27), 1.15)
tm = T(3, "Multidões"); trc = T(3, "recalcula")
for k in range(12):
    tk = tm + k * (trc + 1.2 - tm) / 12
    cub = caixa(_id("tarefa"), (122.7 + random.uniform(-0.12, 0.12), -2.0, 2.2 + k * 0.4), (0.62, 0.62, 0.36), CORES[k % 6])
    cub.rotation_euler = (0, 0, math.radians(random.uniform(-15, 15)))
    visivel(cub, tk, t1 + 0.2); pop(cub, tk)
cor_key(mchipD, trc - 0.1, (0.15, 0.60, 0.32, 1)); cor_key(mchipD, trc + 0.8, VERMELHO)
gD = pixel("guiaD", (117.6, -2.4, 0)); girar(gD["raiz"], 15); respirar(gD, t0, t1 + 1)
apontar(gD, T(3, "cidade") - 0.2, 1.6, "D", 30); espanto(gD, tb - 0.1, 1.3)
apontar(gD, trc - 0.2, 1.8, "D", 50); pensar(gD, T(3, "Segundo") + 0.3, 2.0)
cam_key(t0, (119.6, -8.8, 5.4), (119.8, 1.6, 1.0)); cam_key(tm - 0.2, (119.4, -7.4, 4.0), (119.6, 0.8, 1.0))
cam_key(tb + 0.6, (119.6, -7.6, 3.8), (119.8, 0.2, 1.2)); cam_key(trc - 0.2, (121.2, -7.6, 3.4), (121.6, -1.4, 2.4))
cam_key(t1 - 0.05, (121.0, -8.2, 3.6), (121.2, -1.4, 2.6))

# =====================================================================
# ZONA E (x = 160) — 60 instável x 30 travado: duas fileiras de lâmpadas  (bloco 4)
# =====================================================================
t0, t1 = S[4]
sala("E", 160, (0.66, 0.60, 0.92, 1), (0.98, 0.72, 0.84, 1), prof=3.2)
OFF = (0.22, 0.24, 0.30, 1)
def fileira(z, nome):
    caixa(_id("trilho"), (161.4, 2.85, z), (5.2, 0.2, 0.85), (0.16, 0.17, 0.22, 1))
    lamps = []
    for k in range(8):
        lp = cilindro(_id(nome), (159.3 + k * 0.6, 2.7, z), 0.27, 0.12, OFF, seg=20, unico=_id("lm")); lp.rotation_euler = (math.radians(90), 0, 0)
        lamps.append(lp.data.materials[0])
    return lamps
topo = fileira(4.7, "lampT"); baixo = fileira(3.6, "lampB")
def acender(m, t, cor, dur=0.28):
    cor_key(m, t - 0.02, OFF); cor_key(m, t, cor); cor_key(m, t + dur, cor); cor_key(m, t + dur + 0.04, OFF)
# 30 travado: ritmo sempre igual
k = 0; t = t0 + 0.2
while t < t1:
    acender(topo[k % 8], t, VERDE, 0.26); t += 0.3; k += 1
# 60 instável: rápido, rápido... e trava
teng = T(4, "atrasa")
k = 0; t = t0 + 0.2
while t < t1:
    est = (teng - 0.1 <= t < teng + 0.1) or (T(4, "travado") < t < T(4, "travado") + 0.1)
    if est:
        acender(baixo[k % 8], t, VERMELHO, 0.9); t += 1.0
    else:
        acender(baixo[k % 8], t, AMARELO, 0.12); t += random.choice((0.15, 0.15, 0.2, 0.45))
    k += 1
metr = cilindro("metronomo", (163.6, 1.2, 1.3), 0.7, 2.6, (0.55, 0.36, 0.24, 1), seg=4, r2=0.2); metr.rotation_euler = (0, 0, math.radians(45))
pend = vazio("pendulo", (163.6, 0.65, 0.6)); haste = caixa("hastePend", (0, 0, 0), (0.06, 0.06, 2.0), BRANCO); filho(pend, haste); haste.location = (0, 0, 1.0)
peso = caixa("pesoPend", (0, 0, 0), (0.3, 0.12, 0.3), AMARELO); filho(pend, peso); peso.location = (0, 0, 1.4)
pend.rotation_mode = "XYZ"; k = 0; t = t0
while t < t1 + 0.3:
    key(pend, "rotation_euler", t, (0, math.radians(25 if k % 2 else -25), 0)); t += 0.6; k += 1
gE = pixel("guiaE", (160.1, -1.5, 0)); girar(gE["raiz"], 10); respirar(gE, t0, t1 + 1)
pensar(gE, t0 + 0.2, 1.6); apontar(gE, T(4, "Porque") - 0.2, 1.4, "D", 25); espanto(gE, teng, 1.2)
apontar(gE, T(4, "travado") - 0.3, 1.8, "D", 75); comemorar(gE, T(4, "ritmo") - 0.2, 1.2)
cam_key(t0, (161.0, -5.6, 2.9), (161.2, 2.4, 3.2)); cam_key(T(4, "Porque") - 0.3, (161.3, -6.0, 2.9), (161.4, 2.4, 3.3))
cam_key(T(4, "Trinta") - 0.3, (161.4, -5.6, 3.4), (161.4, 2.4, 3.7)); cam_key(t1 - 0.05, (161.3, -6.0, 3.3), (161.3, 2.4, 3.5))

# =====================================================================
# ZONA F (x = 200) — medidor de FPS: Pro quase sempre em 30; o comum às vezes cai  (fim do bloco 5)
# =====================================================================
tds = T(5, "Segundo"); t1 = S[5][1]
sala("F", 200, (0.98, 0.80, 0.60, 1), (0.48, 0.82, 0.70, 1), prof=3.6)
cPro = console("consPro", (199.9, 1.6), pro=True); cBase = console("consBase", (202.7, 1.6))
def medidor(x):
    caixa(_id("tuboM"), (x, 1.9, 1.85), (0.8, 0.3, 3.7), (0.20, 0.22, 0.30, 1))
    b = de_baixo(cilindro(_id("barra"), (x, 1.62, 0.1), 0.27, 1.0, VERDE, seg=16, unico=_id("bm")))
    caixa(_id("linha30"), (x, 1.55, 3.05), (1.0, 0.08, 0.1), AMARELO)
    return b
bPro = medidor(200.85); bBase = medidor(203.65)
def nivel(b, t, h): b.scale = (1, 1, h); b.keyframe_insert("scale", frame=f(t))
t = tds - 0.3
nivel(bPro, t, 0.05); nivel(bBase, t, 0.05)
nivel(bPro, t + 0.5, 2.95); nivel(bBase, t + 0.5, 2.95)
t = t + 0.5; k = 0
tcm = T(5, "comum"); tcai = T(5, "cai")
mB = bBase.data.materials[0]
while t < t1 + 0.4:
    nivel(bPro, t, 2.95 + (0.04 if k % 2 else -0.03))
    queda_ = (tcm + 0.3 < t < tcm + 0.9) or (tcai - 0.1 < t < tcai + 0.5)
    nivel(bBase, t, 2.25 if queda_ else 2.95 + (0.03 if k % 2 else -0.04))
    cor_key(mB, t, VERMELHO if queda_ else VERDE)
    t += 0.3; k += 1
gF = pixel("guiaF", (199.0, -0.8, 0)); girar(gF["raiz"], 12); respirar(gF, tds - 0.3, t1 + 1)
apontar(gF, T(5, "Pro", 1) - 0.2, 1.6, "D", 30); comemorar(gF, T(5, "queda") - 0.2, 1.0); espanto(gF, tcai - 0.1, 1.0)
cam_key(tds - 0.02, (200.3, -5.4, 2.6), (200.3, 1.6, 2.2)); cam_key(tcm - 0.2, (200.5, -5.6, 2.6), (200.5, 1.6, 2.2))
cam_key(tcm + 0.1, (203.0, -4.4, 2.5), (203.1, 1.6, 2.2)); cam_key(t1 - 0.05, (203.0, -4.6, 2.5), (203.1, 1.6, 2.2))

# =====================================================================
# 6 — CTA de volta à sala (Pixel acena; câmera um pouco mais aberta: CTA não encosta na cabeça)
# =====================================================================
t0 = S[6][0]
bola_tv(t0, FIM, 1 / 15)
acenar(eu, t0 + 0.15, 1.6); comemorar(eu, T(6, "Ainda") + 0.2, 1.4); apontar(eu, T(6, "fila") - 0.2, 1.4, "D", 60)
cam_key(t0, (0.0, -6.2, 2.4), (0.0, 1.0, 2.5)); cam_key(FIM, (0.2, -5.6, 2.4), (0.0, 1.0, 2.5))

# ---------- render ----------
modo_cartoon(samples=int(os.environ.get("AMOSTRAS", "8")))
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
