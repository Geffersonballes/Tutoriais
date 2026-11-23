"""Série 2 — 'Como o servidor sabe que seu tiro acertou?' (estilo C cartoon, mascote Pixel). Uso:
blender -b --factory-startup -P cena_servidor.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
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
random.seed(3)

AZUL = (0.20, 0.55, 1.0, 1); LARANJA = MOLETOM; LASER_L = (1.0, 0.55, 0.10, 1); LASER_A = (0.25, 0.75, 1.0, 1)
PISO = (0.32, 0.80, 0.72, 1); MURO = (0.98, 0.84, 0.36, 1); CAIXA_C = (0.90, 0.36, 0.52, 1)

def girar(ob, graus): ob.rotation_euler = (0, 0, math.radians(graus))
def queda(P, t, lado=-1):
    """Personagem cai de costas (pivô nos pés)."""
    raiz = P["raiz"]; raiz.rotation_mode = "XYZ"; z = raiz.rotation_euler[2]
    raiz.rotation_euler = (0, 0, z); raiz.keyframe_insert("rotation_euler", frame=f(t))
    raiz.rotation_euler = (math.radians(-80), 0, z); raiz.keyframe_insert("rotation_euler", frame=f(t + 0.45))
    return raiz
def laser(a, b, t, cor, dur=0.35):
    a = Vector(a); b = Vector(b); d = b - a
    c = cilindro(_id("laser"), tuple((a + b) / 2), 0.09, d.length, cor, seg=10)
    c.rotation_mode = "QUATERNION"; c.rotation_quaternion = d.to_track_quat("Z", "Y")
    visivel(c, t, t + dur); return c
from mathutils import Vector

# =====================================================================
# ARENA (zona A, origem): piso, muros e caixotes coloridos — nada de mapa real
# =====================================================================
caixa("piso", (0, 0, -0.1), (60, 60, 0.2), PISO)
for x, y, w, d, h in ((-9, 6, 6, 1, 3), (9, 6, 6, 1, 3), (0, 9, 8, 1, 3.6)):
    caixa("muro", (x, y, h / 2), (w, d, h), MURO)
for x, y in ((-7, 3), (7, 2.5), (-2.5, 5)):
    caixa("caixote", (x, y, 0.7), (1.4, 1.4, 1.4), CAIXA_C)
parede = caixa("paredeCob", (-5.5, 0.2, 1.6), (0.8, 3.2, 3.2), (0.55, 0.45, 0.95, 1))
for k in range(8):
    arvore((-20 + k * 5.5, 14 + (k % 2) * 3, 0), 1.3)

eu = pixel("eu", (-3.6, 0, 0)); girar(eu["raiz"], 90)
ini = pixel("inimigo", (4, 0, 0), moletom=AZUL); girar(ini["raiz"], -90)
for P in (eu, ini): respirar(P, 0, FIM)

# câmera
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 24; cam_d.clip_end = 2000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def cam_key(t, loc, tgt):
    for ob, v in ((cam, loc), (alvo, tgt)):
        ob.location = v; ob.keyframe_insert("location", frame=f(t))

# =====================================================================
# 0 — GANCHO: eu atiro primeiro... mas quem cai sou eu
# =====================================================================
t0, t1 = S[0]
ta = T(0, "atirou"); tc0 = T(0, "caiu")
apontar(eu, ta - 0.4, 1.4, "D", 85)
laser((-3.0, -0.4, 1.95), (4.0, 0, 1.9), ta, LASER_L)
apontar(ini, tc0 - 0.7, 1.6, "D", 85)
laser((3.4, 0.4, 1.95), (-3.6, 0, 1.9), tc0 - 0.25, LASER_A)
explosao((-3.6, 0, 2.0), tc0 - 0.2, r=1.2, n=10)
q = queda(eu, tc0 - 0.15, -1)
key(q, "rotation_euler", T(0, "Como") + 0.3, (math.radians(-80), 0, math.radians(90))); key(q, "rotation_euler", T(0, "Como") + 0.8, (0, 0, math.radians(90)))
espanto(eu, T(0, "Como") + 0.8, 1.2)
cam_key(t0, (0.3, -9.5, 2.4), (0.2, 0, 1.6)); cam_key(tc0 - 0.3, (0.0, -9.0, 2.3), (0.0, 0, 1.5)); cam_key(tc0 + 0.2, (-2.2, -5.2, 2.2), (-3.6, 0, 1.0)); cam_key(t1 - 0.05, (-1.8, -5.8, 2.4), (-3.0, 0, 1.3))

# =====================================================================
# 1 — o servidor é o juiz (zona B, x = 40)
# =====================================================================
t0, t1 = S[1]
tsv = T(1, "servidor")
caixa("pisoB", (40, 0, -0.08), (24, 24, 0.2), (0.62, 0.72, 0.98, 1))
rack = caixa("rack", (40, 3, 2.2), (2.4, 1.6, 4.4), (0.16, 0.17, 0.22, 1))
leds = []
for k in range(8):
    l = caixa(_id("led"), (40, 2.15, 0.6 + k * 0.48), (1.9, 0.06, 0.18), (0.20, 0.95, 0.45, 1)); leds.append(l)
pedestal = cilindro("pedestal", (40, 3, 0.15), 2.2, 0.3, (0.98, 0.86, 0.36, 1), seg=32)
coroa = cilindro("coroa", (40, 3, 4.75), 0.7, 0.5, (1.0, 0.80, 0.15, 1), seg=10, r2=0.9); visivel(coroa, T(1, "juiz")); pop(coroa, T(1, "juiz"))
minis = []
for k in range(10):
    a = math.radians(200 + k * 14)
    m = pixel(f"mini{k}", (40 + 6.5 * math.cos(a), 3 + 6.5 * math.sin(a), 0), moletom=LARANJA if k < 5 else AZUL, escala=0.5)
    girar(m["raiz"], math.degrees(a) + 90); minis.append(m)
    visivel(m["raiz"], t0 + 0.08 * k); pop(m["raiz"], t0 + 0.08 * k, 0.5)
    laser((40 + 6.5 * math.cos(a), 3 + 6.5 * math.sin(a), 1.0), (40, 3, 2.4), t0 + 0.6 + 0.1 * k, LASER_L if k < 5 else LASER_A, 0.5)
guia = pixel("guia", (36.2, -2.5, 0)); girar(guia["raiz"], 20); respirar(guia, t0, FIM)
apontar(guia, tsv - 0.3, 2.0, "E", 40)
cam_key(t0, (40, -11, 5), (40, 2, 2)); cam_key(tsv, (37.5, -7.5, 3.0), (39, 1, 2.2)); cam_key(t1 - 0.05, (38.5, -8.5, 3.4), (39.5, 1, 2.4))

# =====================================================================
# 2 — ticks: fotos em intervalos fixos (zona C, x = 80)
# =====================================================================
t0, t1 = S[2]
tfo = T(2, "fotos"); ttk = T(2, "tick"); t64 = T(2, "sessenta")
caixa("pisoC", (80, 0, -0.08), (40, 24, 0.2), (0.98, 0.90, 0.70, 1))
esteira = caixa("linhaTempo", (78, 2, 0.4), (20, 1.2, 0.8), (0.20, 0.22, 0.28, 1))
fotos = []
for k in range(9):
    x = 70 + k * 2.0
    fr = caixa(_id("foto"), (x, 2, 2.0), (1.7, 0.12, 1.3), (1, 1, 1, 1))
    filho(fr, caixa(_id("fotoIn"), (0, -0.07, 0), (1.45, 0.02, 1.05), random.choice([LASER_A, LASER_L, (0.6, 0.9, 0.4, 1)])))
    tk = tfo + 0.25 * k
    visivel(fr, tk); pop(fr, tk); fotos.append(fr)
flash = esfera("flash", (68, 1, 2), 0.5, (1, 1, 0.85, 1), sub=3)
visivel(flash, tfo, t1); caminho(flash, tfo, tfo + 0.25 * 8, lambda u: (70 + 16 * u, 1.0, 2.9), orientar=False)
g2 = pixel("guia2", (67.5, -1.8, 0)); girar(g2["raiz"], 30); respirar(g2, t0, FIM)
pensar(g2, t0 + 0.3, 2.0); apontar(g2, ttk - 0.2, 1.8, "E", 30); comemorar(g2, t64, 1.6)
cam_key(t0, (69.5, -5.5, 2.4), (69.2, 0.5, 1.6)); cam_key(tfo, (71, -6.0, 2.6), (71.5, 1.5, 1.8)); cam_key(ttk + 0.5, (76, -7.5, 2.8), (76.5, 1.5, 1.8)); cam_key(t1 - 0.05, (79, -8.0, 3.0), (79, 1.5, 1.8))

# =====================================================================
# 3 — sub-tick: o clique entre duas fotos ganha o instante exato
# =====================================================================
t0, t1 = S[3]
tex = T(3, "exato"); tsub = T(3, "sub")
pino = cilindro("pino", (79.0, 1.2, 4.5), 0.18, 1.6, (1.0, 0.85, 0.10, 1), seg=12, r2=0.0)
pino.rotation_euler = (math.radians(180), 0, 0); visivel(pino, T(3, "clique") - 0.3)
caminho(pino, T(3, "clique") - 0.3, T(3, "clique") + 0.2, lambda u: (79.0, 1.2, 4.5 - 2.3 * suave(u)), orientar=False)
anelSub = anel("anelSub", (79.0, 1.3, 2.0), 0.55, 0.07, (1.0, 0.85, 0.10, 1)); anelSub.rotation_euler = (math.radians(90), 0, 0)
visivel(anelSub, tex); pop(anelSub, tex)
cam_key(t0, (79.0, -4.6, 2.6), (79.0, 2, 2.1)); cam_key(t1 - 0.05, (79.0, -3.8, 2.4), (79.0, 2, 2.1))

# =====================================================================
# 4 — ping: o clique viaja pelo cabo até o servidor (zona D, x = 120)
# =====================================================================
t0, t1 = S[4]
tpg = T(4, "ping"); tat = T(4, "atrasado")
caixa("pisoD", (125, 0, -0.08), (40, 24, 0.2), (0.80, 0.70, 0.98, 1))
mesa = caixa("mesaD", (116, 1.5, 1.4), (3.0, 1.4, 0.15), (0.45, 0.30, 0.20, 1))
caixa("monD", (116, 1.9, 2.3), (2.0, 0.1, 1.2), (0.08, 0.08, 0.1, 1))
caixa("telaD", (116, 1.83, 2.3), (1.8, 0.02, 1.0), LASER_L)
g3 = pixel("guia3", (114.6, -0.6, 0)); girar(g3["raiz"], -20); respirar(g3, t0, FIM)
rack2 = caixa("rack2", (124, 2, 2.2), (2.4, 1.6, 4.4), (0.16, 0.17, 0.22, 1))
for k in range(6): caixa(_id("led2"), (124, 1.15, 0.8 + k * 0.6), (1.9, 0.06, 0.2), (0.2, 0.95, 0.45, 1))
cabo = cilindro("cabo", (120.2, 2, 0.25), 0.12, 6.6, (0.15, 0.15, 0.18, 1), seg=8); cabo.rotation_euler = (0, math.radians(90), 0)
pac = esfera("pacote", (117, 2, 0.5), 0.35, (1.0, 0.85, 0.10, 1), sub=3); visivel(pac, t0 + 0.6)
caminho(pac, t0 + 0.6, tat + 0.4, lambda u: (117 + 6.4 * (u ** 1.6), 2, 0.6), orientar=False)
relogio = cilindro("relogio", (120.2, 3.5, 3.6), 1.0, 0.2, (1, 1, 1, 1), seg=24); relogio.rotation_euler = (math.radians(90), 0, 0)
ponteiro = caixa("ponteiro", (120.2, 3.35, 3.6), (0.08, 0.05, 0.8), (0.9, 0.2, 0.2, 1)); visivel(relogio, tpg - 0.4); visivel(ponteiro, tpg - 0.4)
ponteiro.rotation_mode = "XYZ"
for k in range(6): key(ponteiro, "rotation_euler", tpg - 0.4 + k * 0.5, (0, math.radians(60 * k), 0))
pensar(g3, t0 + 0.3, 2.2); espanto(g3, tat - 0.2, 1.4)
cam_key(t0, (115.5, -5.5, 2.4), (115.5, 0.8, 1.6)); cam_key(t0 + 2.0, (118.6, -10.8, 3.2), (118.9, 1.5, 1.6)); cam_key(t1 - 0.05, (118.8, -11.2, 3.4), (119.0, 1.5, 1.7))

# =====================================================================
# 5 — compensação de lag: o servidor volta no tempo (de volta à arena)
# =====================================================================
t0, t1 = S[5]
tvt = T(5, "volta"); tcl = T(5, "compensação"); tpar = T(5, "parede")
# eu (laranja) corre para trás da parede; o fantasma marca onde eu estava
fant = pixel("fantasma", (-2.5, 0, 0), moletom=(1.0, 0.85, 0.70, 1), calca=(0.75, 0.78, 0.85, 1)); girar(fant["raiz"], 90)
visivel(fant["raiz"], tvt); pop(fant["raiz"], tvt)
eu2 = pixel("eu2", (-2.5, 0, 0)); girar(eu2["raiz"], 90); visivel(eu2["raiz"], t0); respirar(eu2, t0, FIM)
caminho(eu2["raiz"], t0 + 0.2, tvt - 0.2, lambda u: (-2.5 - 4.6 * suave(u), -0.2, 0), orientar=False)
seta_r = seta3d("setaVolta", 3, (1.0, 0.85, 0.1, 1)); seta_r.location = (-4.2, -1.4, 3.2); seta_r.rotation_euler = (0, math.radians(90), 0)
visivel(seta_r, tvt, tcl); pop(seta_r, tvt)
apontar(ini, tcl - 0.3, 1.6, "D", 85)
laser((3.4, 0.4, 1.95), (-2.5, 0, 1.9), tcl + 0.2, LASER_A, 0.5)
qd = queda(eu2, tpar - 0.1, 1)
for o in (eu["raiz"],): visivel(o, 0, t0)
cam_key(t0, (-1.0, -8.5, 3.0), (-2.0, 0, 1.5)); cam_key(tvt, (-2.0, -8.5, 3.4), (-3.5, 0, 1.5)); cam_key(tpar - 0.3, (-9.5, -4.8, 2.6), (-6.8, 0, 1.0)); cam_key(t1 - 0.05, (-10, -5.2, 2.8), (-7.0, 0, 0.6))

# =====================================================================
# 6 — CTA: Pixel comemora no meio da arena
# =====================================================================
t0 = S[6][0]
fin = pixel("final", (0, -1.5, 0)); visivel(fin["raiz"], t0); respirar(fin, t0, FIM)
for o in (fant["raiz"], eu2["raiz"]): visivel(o, tvt if o is fant["raiz"] else t0, t0)
acenar(fin, t0 + 0.2, 1.8); comemorar(fin, T(6, "Não") + 0.2, 1.6)
cam_key(t0, (0, -7.0, 2.5), (0, -1.5, 1.8)); cam_key(FIM, (0.6, -6.0, 2.4), (0, -1.5, 1.9))

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
