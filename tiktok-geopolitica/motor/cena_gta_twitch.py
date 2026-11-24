"""Série 2 — 'Como milhões de pessoas assistiram GTA 6 ao mesmo tempo?' (estilo C cartoon, mascote Pixel).
Mecanismo peça por peça: 1 vídeo do streamer -> servidor de entrada (ingest) -> transcodificação em várias
qualidades -> CDN copia para servidores perto das cidades -> cada espectador puxa do mais perto; chat; lag.
Visual 100 % original: nada de logotipo de jogo/plataforma, nenhum rosto real (o Pixel faz 'um streamer').
Uso: blender -b --factory-startup -P cena_gta_twitch.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
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
random.seed(11)

AMARELO = (1.0, 0.82, 0.12, 1); VERDE = (0.20, 0.85, 0.40, 1); VERMELHO = (0.95, 0.22, 0.20, 1)
ROSA = (1.0, 0.55, 0.70, 1); ROXO = (0.60, 0.34, 0.95, 1); AZUL = (0.20, 0.55, 1.0, 1); BRANCO = (0.97, 0.97, 0.98, 1)
CIANO = (0.25, 0.95, 1.0, 1); ESCURO = (0.10, 0.11, 0.14, 1); CINZA = (0.40, 0.42, 0.48, 1)
CORES = [(0.98, 0.45, 0.35, 1), (0.30, 0.70, 1.0, 1), (0.98, 0.80, 0.25, 1), (0.45, 0.85, 0.45, 1), (0.75, 0.50, 0.95, 1), (1.0, 0.60, 0.20, 1)]
Q1080, Q720, Q480 = VERDE, AMARELO, (1.0, 0.45, 0.30, 1)
BRILHO = []   # materiais que ganham emissão no fim (telas, pacotes, lâmpadas)

def girar(ob, graus): ob.rotation_euler = (0, 0, math.radians(graus))
def brilha(ob):
    BRILHO.append(ob.data.materials[0]); return ob

def espectador(loc, cor, tel=True):
    """Espectador mini (bonequinho genérico) com celular aceso na mão."""
    corpo = cilindro(_id("esp"), loc, 0.16, 0.36, cor, seg=10)
    cab = esfera(_id("cabE"), (0, 0, 0), 0.17, random.choice([PELE, (0.75, 0.52, 0.38, 1), (0.50, 0.33, 0.22, 1)]), sub=2)
    filho(corpo, cab); cab.location = (0, 0, 0.36)
    if tel:
        t = caixa(_id("cel"), (0, 0, 0), (0.16, 0.03, 0.24), CIANO); filho(corpo, t); t.location = (0.05, -0.22, 0.14)
        t.rotation_euler = (math.radians(-25), 0, 0)
    return corpo

def pacote(nome, loc, s=0.45, cor=CIANO):
    """'Pacote de vídeo': cubo brilhante com um triângulo de play branco."""
    c = caixa(nome, loc, (s, s, s), cor)
    tri = cilindro(_id("play"), (0, 0, 0), s * 0.28, s * 0.06, BRANCO, seg=3); filho(c, tri)
    tri.rotation_euler = (math.radians(90), math.radians(90), 0); tri.location = (0, -s * 0.52, 0)
    return c

def torre(nome, loc, h=1.4):
    """Servidor de borda (edge): torrinha com lâmpada no topo. Retorna (torre, material da lâmpada)."""
    b = caixa(nome, (loc[0], loc[1], h / 2), (0.5, 0.5, h), (0.22, 0.24, 0.32, 1))
    for j in range(3):
        l = caixa(_id("ledT"), (0, 0, 0), (0.36, 0.02, 0.06), VERDE); filho(b, l); l.location = (0, -0.26, -h * 0.3 + j * 0.22)
    lamp = esfera(_id("lampT"), (0, 0, 0), 0.24, CINZA, sub=2, unico=_id("lt")); filho(b, lamp); lamp.location = (0, 0, h / 2 + 0.22)
    return b, lamp.data.materials[0]

def tubo(nome, a, b, r, cor):
    """Cilindro ligando os pontos a e b."""
    from mathutils import Vector
    a, b = Vector(a), Vector(b); d = b - a
    c = cilindro(nome, (a + b) / 2, r, d.length, cor, seg=10)
    c.rotation_mode = "QUATERNION"; c.rotation_quaternion = d.to_track_quat("Z", "Y"); return c

BRILHO.append(mat(CIANO))
cam, alvo, cam_key, plano = camera_cartoon(24)

# =====================================================================
# ZONA H (x = -40) — arquibancada de espectadores + telão  (bloco 0, gancho)
# =====================================================================
t0, t1 = S[0]
caixa("Hpiso", (-40, 2, -0.1), (24, 22, 0.2), (0.30, 0.34, 0.52, 1))
caixa("Hfundo", (-40, 11.5, 9), (24, 0.4, 20), (0.22, 0.20, 0.40, 1))
telao = caixa("telao", (-40, 11.0, 7.6), (9.0, 0.3, 4.2), ESCURO)
tlz = caixa("telaTelao", (0, 0, 0), (8.5, 0.05, 3.8), (0.35, 0.80, 1.0, 1), unico="tt"); filho(telao, tlz); tlz.location = (0, -0.18, 0); brilha(tlz)
playG = cilindro("playTelao", (0, 0, 0), 1.0, 0.1, BRANCO, seg=3); filho(telao, playG); playG.rotation_euler = (math.radians(90), math.radians(90), 0); playG.location = (0, -0.25, 0)
torcida = []
for row in range(7):
    z = row * 0.55; y = 1.6 + row * 1.25
    caixa(_id("degrau"), (-40, y, z / 2 - 0.05), (16, 1.25, max(z, 0.1)), (0.40 + 0.05 * (row % 2), 0.44, 0.66, 1))
    for k in range(17):
        x = -47.6 + k * 0.95 + (0.45 if row % 2 else 0) + random.uniform(-0.1, 0.1)
        e = espectador((x, y - 0.1 + random.uniform(-0.15, 0.15), z + 0.18), random.choice(CORES))
        torcida.append(e)
eu0 = pixel("eu0", (-40.3, -0.6, 0)); girar(eu0["raiz"], 8); respirar(eu0, 0, t1 + 0.5)
tcaiu = T(0, "caiu")
# ola: a torcida pula em onda no "Como isso não caiu?"
for i, e in enumerate(torcida[::2]):
    z0 = e.location.z; dt = (e.location.x + 48) * 0.06
    for tt, dz in ((T(0, "milhões") + dt, 0), (T(0, "milhões") + dt + 0.2, 0.35), (T(0, "milhões") + dt + 0.4, 0)):
        e.location.z = z0 + dz; e.keyframe_insert("location", index=2, frame=f(tt))
    e.location.z = z0
apontar(eu0, T(0, "pessoas") - 0.2, 1.6, "D", 70); espanto(eu0, T(0, "Como") - 0.1, 1.6)
cam_key(0, (-40.0, -8.5, 4.4), (-40.0, 5.0, 4.4)); cam_key(T(0, "Twitch"), (-39.6, -7.4, 4.2), (-39.8, 4.0, 3.3))
cam_key(T(0, "Como") - 0.15, (-40.2, -4.4, 2.6), (-40.3, 0.5, 2.6)); cam_key(t1 - 0.05, (-40.3, -4.1, 2.6), (-40.3, 0.5, 2.7))

# =====================================================================
# ZONA A (x = 0) — quarto do streamer: o Pixel faz 'um streamer'  (blocos 1 e 6)
# =====================================================================
QA = quarto_gamer(0)
brilha(QA["tela"])
st = pixel("streamer", (0, 1.0, 0)); respirar(st, 0, FIM)
# medidor de público na parede (barra que sobe)
caixa("medTubo", (-1.6, 3.3, 2.6), (0.6, 0.25, 3.6), (0.18, 0.18, 0.24, 1))
barra = cilindro("medBarra", (-1.6, 3.12, 0.9), 0.22, 1.0, ROXO, seg=16)
for v in barra.data.vertices: v.co.z += 0.5
t0, t1 = S[1]
def nivel(b, t, h): b.scale = (1, 1, h); b.keyframe_insert("scale", frame=f(t))
nivel(barra, 0, 0.05); nivel(barra, t0 + 0.2, 0.05); nivel(barra, T(1, "pico"), 2.6); nivel(barra, T(1, "duzentas") + 0.4, 3.3)
cor_key(QA["live"].data.materials[0], t0, (0.35, 0.10, 0.12, 1))
k = 0; t = t0 + 0.2
while t < FIM:   # lâmpada 'ao vivo' pisca
    cor_key(QA["live"].data.materials[0], t, (0.95, 0.15, 0.18, 1) if k % 2 == 0 else (0.55, 0.10, 0.12, 1)); t += 0.6; k += 1
# o único vídeo sai do PC e voa para fora (direita, alto)
tv0 = T(1, "único") - 0.1
pk1 = pacote("pacote1", (2.4, 0.0, 1.2), 0.5)
visivel(pk1, tv0, t1 + 0.1); pop(pk1, tv0)
caminho(pk1, tv0 + 0.35, t1 + 0.1, lambda u: bez((2.4, 0.0, 1.4), (2.6, -0.8, 3.6), (6.5, 0.5, 3.4), suave(u)), orientar=False)
acenar(st, t0 + 0.1, 1.2); apontar(st, T(1, "pico") - 0.2, 1.5, "E", 70); comemorar(st, T(1, "duzentas") - 0.1, 1.3)
apontar(st, tv0, 1.6, "D", 30)
plano(t0, (0.0, 1.0), "medio", altura=2.0); plano(T(1, "pico") - 0.3, (-0.7, 1.4), "medio", altura=2.3)
plano(T(1, "duzentas") + 0.6, (0.2, 1.0), "close", altura=2.1); plano(tv0 - 0.2, (1.4, 0.6), "medio", altura=2.0)
plano(t1 - 0.05, (2.2, 0.6), "medio", altura=2.3)

# =====================================================================
# ZONA B (x = 40) — servidor de entrada (ingest): a porta da live  (bloco 2)
# =====================================================================
t0, t1 = S[2]
data_center(40)
ing = caixa("ingest", (41.0, 1.8, 2.3), (2.8, 1.8, 4.6), (0.20, 0.30, 0.60, 1), unico="ing")
for j in range(5):
    l = caixa(_id("ledI"), (0, 0, 0), (2.2, 0.04, 0.14), VERDE); filho(ing, l); l.location = (0, -0.92, -1.9 + j * 0.3)
porta = anel("porta", (41.0, 0.86, 3.2), 0.75, 0.13, CINZA, unico="porta"); porta.rotation_euler = (math.radians(90), 0, 0)
fundoP = cilindro("fundoPorta", (41.0, 0.88, 3.2), 0.66, 0.04, (0.05, 0.10, 0.25, 1), seg=24); fundoP.rotation_euler = (math.radians(90), 0, 0)
cabo = tubo("caboIn", (35.5, 0.6, 3.2), (40.3, 0.6, 3.2), 0.12, (0.25, 0.25, 0.30, 1))
gB = pixel("guiaB", (38.6, -1.0, 0)); girar(gB["raiz"], 14); respirar(gB, t0, t1 + 0.5)
trc = T(2, "receber"); tsv = T(2, "servidor"); tpt = T(2, "porta")
pk2 = pacote("pacote2", (35.5, 0.6, 3.2), 0.5)
visivel(pk2, t0, trc + 1.2)
caminho(pk2, t0 + 0.2, trc, lambda u: (35.5 + 5.4 * u, 0.6, 3.2), orientar=False)
key(pk2, "scale", trc, (1, 1, 1)); key(pk2, "scale", trc + 0.5, (0.05, 0.05, 0.05))
mp = porta.data.materials[0]
cor_key(mp, trc - 0.2, CINZA); cor_key(mp, trc + 0.1, CIANO); cor_key(mp, tpt - 0.1, CIANO); cor_key(mp, tpt + 0.15, AMARELO); cor_key(mp, tpt + 0.6, CIANO)
destacar(ing.data.materials[0], tsv, (0.20, 0.30, 0.60, 1), 1.4)
# fluxo contínuo de pacotes pequenos entrando depois
t = trc + 0.4
while t < t1:
    p = pacote(_id("pk"), (35.5, 0.6, 3.2), 0.26); visivel(p, t, t + 1.3)
    caminho(p, t, t + 1.2, lambda u: (35.5 + 5.4 * u, 0.6, 3.2), orientar=False); t += 0.45
pensar(gB, t0 + 0.1, 1.6); apontar(gB, trc - 0.3, 1.5, "D", 40); apontar(gB, tsv - 0.2, 1.6, "D", 25)
comemorar(gB, tpt - 0.1, 1.0)
plano(t0, (38.2, 0.4), "medio", altura=2.4); plano(trc - 0.4, (39.4, 0.4), "medio", altura=2.6)
plano(tsv - 0.2, (40.4, 0.6), "geral", altura=2.6); plano(tpt - 0.2, (40.6, 0.7), "medio", altura=2.8)
plano(t1 - 0.05, (40.6, 0.7), "medio", altura=2.8)

# =====================================================================
# ZONA C (x = 80) — a máquina de transcodificação: 1 vídeo vira 3 qualidades  (bloco 3)
# =====================================================================
t0, t1 = S[3]
sala_fechada("C", 80, (0.70, 0.74, 0.86, 1), (0.98, 0.70, 0.52, 1), prof=4.2)
caixa("Calto", (80, 4.2, 10), (22, 0.4, 8), (0.98, 0.70, 0.52, 1))
maq = caixa("maquina", (79.4, 1.4, 2.7), (2.2, 1.6, 5.4), (0.55, 0.36, 0.95, 1), unico="maq")
chamine = cilindro("funil", (78.6, 1.4, 5.8), 0.6, 0.9, (0.75, 0.55, 1.0, 1), seg=16, r2=0.25)
engr = cilindro("engrenagem", (79.4, 0.58, 3.6), 0.5, 0.12, AMARELO, seg=10); engr.rotation_mode = "XYZ"
key(engr, "rotation_euler", t0, (math.radians(90), 0, 0)); key(engr, "rotation_euler", t1, (math.radians(90), math.radians(900), 0))
for fc in engr.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
SAIDAS = [(4.6, 0.48, Q1080, T(3, "mil")), (3.1, 0.34, Q720, T(3, "setecentos")), (1.6, 0.22, Q480, T(3, "quatrocentos"))]
for z, s, cor, ta in SAIDAS:
    tr = caixa(_id("trilho"), (82.3, 1.0, z - s / 2 - 0.08), (3.6, 0.7, 0.1), (0.22, 0.24, 0.30, 1))
    visivel(tr, ta - 0.2); pop(tr, ta - 0.2)
    t = ta
    while t < t1 + 0.3:
        p = pacote(_id("q"), (80.5, 1.0, z), s, cor); visivel(p, t, t + 1.5)
        caminho(p, t, t + 1.5, lambda u, z=z: (80.6 + 3.4 * u, 1.0, z), orientar=False); t += 0.3
# entrada: o vídeo original cai no funil
tm = T(3, "máquina")
t = tm - 0.6
while t < t1:
    p = pacote(_id("in"), (78.6, 1.4, 8.0), 0.5); visivel(p, t, t + 0.75)
    caminho(p, t, t + 0.7, lambda u: (78.6, 1.4, 8.0 - 2.3 * u), orientar=False); t += 0.7
# a internet fraca: um espectador com celular e barrinha de sinal baixa
gC = pixel("guiaC", (78.6, -1.2, 0), escala=0.85); girar(gC["raiz"], 14); respirar(gC, t0, t1 + 0.5)
pensar(gC, t0 + 0.1, 1.8); apontar(gC, tm - 0.2, 1.4, "D", 50); apontar(gC, T(3, "mil") - 0.2, 1.4, "D", 70)
apontar(gC, T(3, "quatrocentos") - 0.2, 1.6, "D", 20); comemorar(gC, T(3, "transcodificação"), 1.2)
destacar(maq.data.materials[0], T(3, "transcodificação"), (0.55, 0.36, 0.95, 1), 1.2)
plano(t0, (78.7, -0.4), "close", altura=2.0); plano(tm - 0.3, (79.4, 0.2), "medio", altura=3.6)
plano(T(3, "mil") - 0.2, (80.9, 0.6), "geral", altura=3.0); plano(t1 - 0.05, (81.0, 0.6), "geral", altura=3.0)

# =====================================================================
# ZONA D (x = 120) — mapa em miniatura: um servidor só derrete; a CDN espalha cópias  (bloco 4)
# =====================================================================
t0, t1 = S[4]
caixa("Dfundo", (120, 9, 3), (30, 0.4, 12), (0.55, 0.78, 1.0, 1))
caixa("mapa", (120, 2.5, -0.1), (30, 20, 0.2), (0.48, 0.80, 0.42, 1))
for (x, y, w, d) in ((116.0, 5.6, 3.2, 2.2), (124.6, -1.0, 2.4, 3.0)):
    caixa(_id("lago"), (x, y, 0.01), (w, d, 0.04), (0.35, 0.65, 0.98, 1))
orig = caixa("origem", (120, 4.0, 1.6), (1.6, 1.4, 3.2), (0.20, 0.30, 0.60, 1), unico="orig")
for j in range(4):
    l = caixa(_id("ledO"), (0, 0, 0), (1.2, 0.04, 0.12), VERDE); filho(orig, l); l.location = (0, -0.72, -1.0 + j * 0.45)
CIDADES = [(116.6, 1.6), (123.4, 2.4), (117.4, -2.4), (122.6, -3.6), (120.2, -0.6)]
torres = []
for i, (cx, cy) in enumerate(CIDADES):
    for k in range(4):
        predio((cx + (k % 2) * 0.9 - 1.1, cy + (k // 2) * 0.9 + 0.2, 0), 0.6, 0.6, 0.6 + ((i + k) % 3) * 0.4, PREDIOS[(i + k) % 6])
    tw, ml = torre(_id("edge"), (cx + 0.8, cy - 0.5)); torres.append((tw, ml, cx + 0.8, cy - 0.5))
    tlig = T(4, "cidade") + 0.25 * i
    visivel(tw, tlig - 0.1); pop(tw, tlig - 0.1)
td = T(4, "derretia"); tq = T(4, "três")
# fase 1: todo mundo puxando do mesmo servidor -> linhas convergindo, servidor fica vermelho e sacode
fios = []
for k in range(16):
    a = k / 16 * math.tau
    px, py = 120 + 6.0 * math.cos(a), 1.2 + 4.8 * math.sin(a)
    e = espectador((px, py, 0.18), random.choice(CORES)); visivel(e, tq - 0.1, T(4, "rede"))
    fl = tubo(_id("fio"), (px, py, 0.5), (120, 4.0, 2.4), 0.03, VERMELHO); visivel(fl, tq + 0.1 + k * 0.05, T(4, "rede"))
cor_key(orig.data.materials[0], tq, (0.20, 0.30, 0.60, 1)); cor_key(orig.data.materials[0], td, VERMELHO)
cor_key(orig.data.materials[0], T(4, "rede") + 0.3, VERMELHO); cor_key(orig.data.materials[0], T(4, "rede") + 0.8, (0.20, 0.30, 0.60, 1))
orig.rotation_mode = "XYZ"
for k in range(10):
    key(orig, "rotation_euler", td - 0.4 + k * 0.1, (0, math.radians(4 if k % 2 else -4), 0))
key(orig, "rotation_euler", td + 0.6, (0, 0, 0))
rastro(lambda u: (120 + 0.3 * math.sin(u * 9), 4.0, 3.4 + 2.0 * u), td - 0.2, T(4, "rede"), cor=(0.6, 0.6, 0.65, 1), r=0.35, cada=0.1, vida=1.0)
# fase 2: a rede copia a live para cada cidade (pacotes em arco) e as lâmpadas acendem
tcp = T(4, "copia")
for i, (tw, ml, tx, ty) in enumerate(torres):
    ta = tcp + 0.18 * i
    for r in range(3):
        p = pacote(_id("cp"), (120, 4.0, 3.4), 0.32); visivel(p, ta + r * 1.3, ta + r * 1.3 + 0.95)
        caminho(p, ta + r * 1.3, ta + r * 1.3 + 0.9, lambda u, tx=tx, ty=ty: bez((120, 4.0, 3.4), ((120 + tx) / 2, (4 + ty) / 2, 5.0), (tx, ty, 1.8), u), orientar=False)
    cor_key(ml, ta + 0.85, CINZA); cor_key(ml, ta + 0.95, CIANO)
# fase 3: espectadores ao redor de cada torre (cada um puxa do mais perto)
tvc = T(4, "Você")
for i, (tw, ml, tx, ty) in enumerate(torres):
    for k in range(5):
        a = k / 5 * math.tau + i
        e = espectador((tx + 1.0 * math.cos(a), ty + 0.9 * math.sin(a), 0.18), random.choice(CORES))
        visivel(e, tvc - 0.4 + 0.05 * k); pop(e, tvc - 0.4 + 0.05 * k)
        fl = tubo(_id("fioV"), (tx + 1.0 * math.cos(a), ty + 0.9 * math.sin(a), 0.5), (tx, ty, 1.0), 0.025, CIANO); visivel(fl, tvc + 0.1 + 0.05 * k)
gD = pixel("guiaD", (117.2, -5.6, 0), escala=0.9); girar(gD["raiz"], 15); respirar(gD, t0, t1 + 0.5)
espanto(gD, td - 0.2, 1.4); apontar(gD, tcp - 0.2, 1.8, "D", 50); comemorar(gD, T(4, "C-D-N") - 0.1, 1.2); apontar(gD, tvc, 1.6, "D", 30)
cam_key(t0, (120.0, -9.0, 6.0), (120.0, 1.6, 1.6)); cam_key(td, (120.0, -6.4, 5.0), (120.0, 3.0, 2.2))
cam_key(tcp - 0.1, (120.0, -10.6, 8.4), (120.0, 0.6, 0.6)); cam_key(T(4, "C-D-N"), (119.4, -10.2, 7.6), (119.8, 0.0, 0.8))
cam_key(tvc + 0.3, (118.6, -7.2, 5.0), (118.6, -0.6, 0.6)); cam_key(t1 - 0.05, (118.8, -7.4, 5.0), (118.8, -0.6, 0.6))

# =====================================================================
# ZONA E (x = 160) — o paredão do chat: mensagens subindo cada vez mais rápido  (bloco 5, 1ª parte)
# =====================================================================
t0, t1 = S[5]
tq5 = T(5, "quando")
sala_fechada("E", 160, (0.30, 0.30, 0.42, 1), (0.16, 0.16, 0.24, 1), prof=3.4)
caixa("molduraChat", (160.6, 3.0, 4.0), (5.6, 0.3, 8.0), (0.10, 0.10, 0.16, 1))
rolo = vazio("rolo", (160.6, 2.78, 0))
NM = 70
for k in range(NM):
    L = random.uniform(1.2, 3.8); cor = CORES[k % 6]
    b = caixa(_id("msg"), (0, 0, 0), (L, 0.06, 0.34), (0.92, 0.93, 0.98, 1)); filho(rolo, b)
    b.location = (-2.5 + L / 2 + 0.35, 0, -k * 0.55)
    av = esfera(_id("av"), (0, 0, 0), 0.17, cor, sub=2); filho(rolo, av); av.location = (-2.45, -0.05, -k * 0.55)
# máscara: tampas em cima e embaixo da moldura
caixa("tampaCima", (160.6, 2.6, 9.3), (6.0, 0.4, 2.6), (0.16, 0.16, 0.24, 1))
caixa("tampaBaixo", (160.6, 2.6, -0.7), (6.0, 0.4, 2.2), (0.16, 0.16, 0.24, 1))
tml = T(5, "milhares")
rolo.location.z = 7.5; rolo.keyframe_insert("location", index=2, frame=f(t0))
rolo.location.z = 11.5; rolo.keyframe_insert("location", index=2, frame=f(tml))
rolo.location.z = rolo.location.z + 22.0; rolo.keyframe_insert("location", index=2, frame=f(tq5 + 0.3))
for fc in rolo.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
gE = pixel("guiaE", (158.6, -0.6, 0)); girar(gE["raiz"], 12); respirar(gE, t0, tq5 + 0.5)
apontar(gE, T(5, "chat") - 0.1, 1.4, "D", 60); pensar(gE, T(5, "mensagem"), 1.2); espanto(gE, tml - 0.1, 1.6)
plano(t0, (159.4, 0.6), "medio", altura=2.8); plano(tml - 0.3, (160.0, 0.8), "geral", altura=3.2)
plano(tq5 - 0.25, (160.0, 0.8), "geral", altura=3.2)

# =====================================================================
# ZONA F (x = 200) — o lag: servidor da região lota, a imagem cai de qualidade e trava  (bloco 5, 2ª parte)
# =====================================================================
sala_fechada("F", 200, (0.95, 0.80, 0.58, 1), (0.48, 0.82, 0.70, 1), prof=3.6)
caixa("rackTV", (200.6, 2.6, 0.45), (4.2, 1.0, 0.9), (0.55, 0.36, 0.24, 1))
tvF = caixa("tvF", (200.6, 2.9, 2.3), (3.6, 0.2, 2.2), ESCURO)
telaF = caixa("telaF", (0, 0, 0), (3.36, 0.04, 1.96), (0.35, 0.80, 1.0, 1), unico="telaF"); filho(tvF, telaF); telaF.location = (0, -0.12, 0)
# 'pixels' grandes na tela (qualidade caindo)
blocos = []
for i in range(6):
    for j in range(4):
        b = caixa(_id("pxl"), (0, 0, 0), (0.52, 0.02, 0.45), random.choice(CORES)); filho(tvF, b); b.location = (-1.4 + i * 0.56, -0.16, -0.72 + j * 0.48)
        blocos.append(b)
tql = T(5, "qualidade"); ttv = T(5, "trava")
for b in blocos: visivel(b, tql, None)
# rodinha de carregando
roda = vazio("roda", (200.6, 2.6, 2.3)); roda.rotation_mode = "XYZ"
for k in range(8):
    a = k / 8 * math.tau
    s = esfera(_id("rd"), (0, 0, 0), 0.09 + 0.012 * k, BRANCO, sub=2); filho(roda, s); s.location = (0.5 * math.cos(a), 0, 0.5 * math.sin(a))
visivel(roda, ttv)
for k in range(12):
    key(roda, "rotation_euler", ttv + k * 0.25, (0, math.radians(-45 * k), 0), interp="CONSTANT")
# torre da região (lotando: lâmpada verde -> vermelha, muitos fios)
twF, mlF = torre("edgeF", (203.6, 1.0), 2.0)
cor_key(mlF, tq5, VERDE); cor_key(mlF, T(5, "lota"), VERMELHO)
for k in range(10):
    a = 0.3 + k * 0.28
    fl = tubo(_id("fioF"), (203.6 + 2.0 * math.cos(a), 1.0 - 1.2 * math.sin(a), 0.2), (203.6, 1.0, 2.2), 0.025, VERMELHO); visivel(fl, T(5, "lota") + 0.05 * k)
sofa = caixa("sofa", (199.4, -0.2, 0.4), (2.6, 1.0, 0.8), (0.30, 0.55, 0.95, 1))
caixa("encosto", (199.4, 0.25, 0.95), (2.6, 0.3, 1.0), (0.26, 0.48, 0.88, 1))
gF = pixel("guiaF", (199.4, -0.2, 0.2), escala=0.85); girar(gF["raiz"], 180 + 20)
respirar(gF, tq5 - 0.3, S[5][1] + 0.5)
apontar(gF, T(5, "lota") - 0.2, 1.4, "E", 40); espanto(gF, ttv - 0.1, 1.2); pensar(gF, T(5, "lag") - 0.2, 1.4)
plano(tq5 - 0.12, (202.6, 0.8), "medio", altura=2.2); plano(tql - 0.4, (201.0, 0.8), "medio", altura=2.2)
plano(t1 - 0.05, (200.8, 0.8), "medio", altura=2.2)

# =====================================================================
# 6 — CTA de volta ao quarto (câmera mais aberta: o CTA não encosta na cabeça — backlog #9)
# =====================================================================
t0 = S[6][0]
acenar(st, t0 + 0.15, 1.6); comemorar(st, T(6, "estava") - 0.1, 1.2); pensar(st, T(6, "Não") - 0.1, 1.2); apontar(st, T(6, "perdi") - 0.2, 1.4, "D", 60)
cam_key(t0, (0.2, -6.4, 2.9), (0.2, 1.0, 2.6)); cam_key(FIM, (0.3, -5.9, 2.9), (0.2, 1.0, 2.6))

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
