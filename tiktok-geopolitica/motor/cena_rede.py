"""Vídeo 04 — '850 mil no escuro em uma noite' (rede elétrica como alvo). Uso:
REALISTA=1 blender -b --factory-startup -P cena_rede.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
import bpy, bmesh, sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
from lowpoly import *
from lowpoly import _id, _lin, _new_obj

args = sys.argv[sys.argv.index("--") + 1:]
PASTA = args[0]
LEG = json.load(open(os.path.join(PASTA, "legendas.json"), encoding="utf-8"))
FIM = LEG[-1]["e"] + 6.2          # sobra para o pedido de like (a câmera continua andando)
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
scn.world.color = (0.30, 0.60, 0.95)

CONC = (0.78, 0.78, 0.76, 1); BRITA = (0.66, 0.65, 0.62, 1); METAL = (0.74, 0.76, 0.78, 1)
COR_JAN = (0.09, 0.12, 0.17, 1); QUEIMADO = (0.07, 0.07, 0.07, 1); TRAFO = (0.47, 0.56, 0.55, 1)
AMBAR = (1.0, 0.72, 0.25, 1); CIANO = (0.30, 0.85, 1.0, 1); VERMELHO = (1.0, 0.15, 0.10, 1)
PAREDES = [(0.93, 0.85, 0.72, 1), (0.82, 0.87, 0.92, 1), (0.92, 0.76, 0.70, 1), (0.80, 0.85, 0.72, 1), (0.95, 0.93, 0.86, 1), (0.86, 0.80, 0.90, 1)]

def nasce(ob, t, escala=1.0, dur=0.35):
    """Peça que aparece no gancho (flash-forward), some, e 'nasce' de novo quando o roteiro a constrói."""
    visivel_janelas(ob, [(0, S[1][0]), (t - 0.04, FIM + 5)])
    ob.scale = (escala,) * 3; ob.keyframe_insert("scale", frame=1); ob.keyframe_insert("scale", frame=f(S[1][0]))
    pop(ob, t, escala, dur)

def fumaca(loc, t0, t1, r=0.85, cada=0.3, sobe=14.0, vida=2.6, cor=(0.42, 0.41, 0.41, 1)):
    t = t0
    while t < t1:
        o = esfera(_id("fz"), loc, r * random.uniform(0.7, 1.2), cor, sub=2)
        for pl in o.data.polygons: pl.use_smooth = True
        visivel(o, t, t + vida)
        o.location = loc; o.keyframe_insert("location", frame=f(t))
        o.location = (loc[0] + random.uniform(-1.5, 1.5) + sobe * 0.25, loc[1] + random.uniform(-1, 1), loc[2] + sobe); o.keyframe_insert("location", frame=f(t + vida))
        o.scale = (0.4,) * 3; o.keyframe_insert("scale", frame=f(t))
        o.scale = (1.6,) * 3; o.keyframe_insert("scale", frame=f(t + vida * 0.7))
        o.scale = (0.05,) * 3; o.keyframe_insert("scale", frame=f(t + vida))
        t += cada

def fogo(loc, t0, t1, r=0.5):
    for k in range(3):
        o = esfera(_id("fogo"), (loc[0] + (k - 1) * 0.9, loc[1], loc[2] + 0.3 * (k % 2)), r, C["laranja"], sub=1, unico="fogo")
        visivel(o, t0, t1); t = t0
        while t < t1:
            s = random.uniform(0.6, 1.3); o.scale = (s, s, s * 1.5); o.keyframe_insert("scale", frame=f(t)); t += 0.2

def pulsos(pts, janelas, cor, chave, cada=0.7, vel=45.0, r=0.7):
    """Bolinhas de energia correndo pelos cabos (chaves só nos vértices do caminho, interpolação linear)."""
    comp = [(Vector(pts[i + 1]) - Vector(pts[i])).length for i in range(len(pts) - 1)]
    for a, b in janelas:
        t = a
        while t < b:
            o = esfera(_id("pl"), pts[0], r, cor, sub=1, unico=chave); tt = t
            o.location = pts[0]; o.keyframe_insert("location", frame=f(tt))
            for i, L in enumerate(comp):
                tt += L / vel; o.location = pts[i + 1]; o.keyframe_insert("location", frame=f(tt))
            for fc in o.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
            visivel(o, t, min(tt, b)); t += cada

def alvo_vermelho(loc, R, t0, t1):
    o = anel(_id("mira"), loc, R, R * 0.06, VERMELHO, seg=40, unico="mira")
    c1 = caixa(_id("miraX"), (0, 0, 0), (R * 2.5, R * 0.08, R * 0.08), VERMELHO, unico="mira"); c2 = caixa(_id("miraY"), (0, 0, 0), (R * 0.08, R * 2.5, R * 0.08), VERMELHO, unico="mira")
    filho(o, c1, c2); visivel(o, t0, t1); pop(o, t0); return o

# =====================================================================
# TERRENO E CIDADE (sempre visíveis)
# =====================================================================
chao = caixa("chao", (0, 0, -0.5), (1200, 1200, 1.0), C["grama"])
caixa("estrada", (-70, -16, 0.03), (300, 5, 0.06), C["rua"])
caixa("avenida", (106, 0, 0.03), (104, 6, 0.06), C["rua"])
for x in (68, 80, 92, 104, 116, 128, 140):
    caixa("ruaN", (x, 0, 0.03), (3, 90, 0.05), C["rua"])
for _ in range(34):
    m = esfera("morro", (random.uniform(-420, 420), random.uniform(120, 330), -4), random.uniform(18, 40), random.choice([C["morro"], C["grama2"]]), sub=2)
    m.scale = (1.7, 1.0, 0.5)
for k in range(14):   # lavouras: retalhos de cor no campo
    caixa("lavoura", (random.uniform(-250, 40), random.choice([1, -1]) * random.uniform(40, 110), 0.02), (random.uniform(20, 44), random.uniform(14, 30), 0.05), random.choice([(0.62, 0.70, 0.30, 1), (0.74, 0.68, 0.36, 1), (0.42, 0.66, 0.30, 1)]))
for _ in range(260):
    x = random.uniform(-290, 210); y = random.choice([1, -1]) * random.uniform(20, 115)
    if x > 50 and abs(y) < 60: continue
    if -215 < x < -140 and y > -10 and y < 40: continue
    if abs(y + 16) < 5: continue
    arvore((x, y), random.uniform(0.9, 1.6))

BAIRRO = {62: 0, 74: 0, 86: 0, 98: 1, 110: 1, 122: 1, 134: 2, 146: 2}
def janelas(x, y, w, d, h, chave):
    bm = bmesh.new()
    def quad(p, du, dv):
        vs = [bm.verts.new(Vector(p) + Vector(du) * a + Vector(dv) * b) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]; bm.faces.new(vs)
    z = 1.6
    while z < h - 0.8:
        u = -w / 2 + 0.9
        while u < w / 2 - 0.5:
            if random.random() < 0.85: quad((x + u, y - d / 2 - 0.05, z), (0.36, 0, 0), (0, 0, 0.45))
            u += 1.25
        u = -d / 2 + 0.9
        while u < d / 2 - 0.5:
            if random.random() < 0.85:
                quad((x - w / 2 - 0.05, y + u, z), (0, 0.36, 0), (0, 0, 0.45)); quad((x + w / 2 + 0.05, y + u, z), (0, 0.36, 0), (0, 0, 0.45))
            u += 1.25
        z += 1.55
    return _new_obj(_id("jan"), bm, COR_JAN, unico=chave)

HOSP = (62, -36)
for cx, b in BAIRRO.items():
    for cy in (-36, -24, -12, 12, 24, 36):
        if (cx, cy) == HOSP: continue
        w, d, h = random.uniform(6.5, 8.5), random.uniform(6.5, 8.5), random.uniform(6, 17)
        cor = random.choice(PAREDES)
        caixa(_id("pr"), (cx, cy, h / 2), (w, d, h), cor)
        caixa(_id("teto"), (cx, cy, h + 0.15), (w * 1.04, d * 1.04, 0.3), tuple(c * 0.75 for c in cor[:3]) + (1,))
        janelas(cx, cy, w, d, h, "luz%d" % b)
# hospital (branco, placa azul com H)
hx, hy = HOSP
caixa("hospital", (hx, hy, 4.5), (11, 9, 9), (0.96, 0.96, 0.95, 1)); caixa("hospTeto", (hx, hy, 9.15), (11.4, 9.4, 0.3), (0.60, 0.62, 0.66, 1))
janelas(hx, hy, 11, 9, 8.2, "luzH")
caixa("placaH", (hx, hy - 4.56, 7.6), (2.6, 0.1, 2.2), (0.10, 0.35, 0.75, 1))
for dx in (-0.6, 0.6): caixa("hV", (hx + dx, hy - 4.63, 7.6), (0.3, 0.06, 1.5), C["branco"])
caixa("hH", (hx, hy - 4.63, 7.6), (1.2, 0.06, 0.3), C["branco"])
# caixa-d'água e torre de celular (na frente da cidade)
CX_AGUA = (86, -48); CX_CEL = (100, -48)
for sx, sy in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
    cabo("pernaAgua", (CX_AGUA[0] + sx * 1.6, CX_AGUA[1] + sy * 1.6, 0), (CX_AGUA[0] + sx * 1.1, CX_AGUA[1] + sy * 1.1, 8), 0.16, METAL)
cilindro("tanqueAgua", (CX_AGUA[0], CX_AGUA[1], 9.6), 2.6, 3.4, (0.80, 0.88, 0.94, 1), seg=14)
cilindro("tampaAgua", (CX_AGUA[0], CX_AGUA[1], 11.7), 2.7, 0.9, (0.25, 0.50, 0.75, 1), seg=14, r2=0.3)
luz_agua = esfera("luzAgua", (CX_AGUA[0], CX_AGUA[1] - 2.7, 9.6), 0.5, CIANO, sub=1, unico="luzAgua")
tcel, _p = torre_transmissao("torreCel", (CX_CEL[0], CX_CEL[1], 0), h=15, cor=(0.85, 0.30, 0.25, 1))
for k in range(3):
    a = k * 2.094; caixa("antena", (CX_CEL[0] + math.cos(a) * 0.9, CX_CEL[1] + math.sin(a) * 0.9, 13.2), (0.35, 0.35, 1.8), C["branco"])
luz_cel = esfera("luzCel", (CX_CEL[0], CX_CEL[1], 15.6), 0.45, VERMELHO, sub=1, unico="luzCel")

# =====================================================================
# REDE: usina -> elevadora -> torres -> subestação -> postes -> cidade
# =====================================================================
US = (-185, 6, 0)
us, us_topos = usina("usina"); us.location = US
us_topos = [(US[0] + x, US[1] + y, z) for x, y, z in us_topos]
elev, elev_tq, _ = transformador("elevadora", 0.9); elev.location = (-150, 0, 0)
TX = [-124, -100, -76, -52, -30]; HT = 16.0
torres = []; fix = []
for k, x in enumerate(TX):
    t, pts = torre_transmissao(f"torre{k}", (x, 0, 0), HT); torres.append(t); fix.append(pts)
# subestação
PAD = caixa("patio", (0, 0, 0.08), (36, 26, 0.16), BRITA)
from lowpoly import _viga, _mats
bm = bmesh.new()
for x in range(-18, 19, 3):
    for y in (-13, 13): _viga(bm, (x, y, 0), (x, y, 1.8), 0.07)
for y in range(-13, 14, 3):
    for x in (-18, 18): _viga(bm, (x, y, 0), (x, y, 1.8), 0.07)
for z in (0.7, 1.7):
    for a, b in (((-18, -13), (18, -13)), ((18, -13), (18, 13)), ((18, 13), (-18, 13)), ((-18, 13), (-18, -13))):
        _viga(bm, (a[0], a[1], z), (b[0], b[1], z), 0.04)
cerca = _new_obj("cerca", bm, (0.35, 0.37, 0.40, 1))
TRX = [-8, 0, 8]; trafos = []
for k, x in enumerate(TRX):
    p, tq, topos = transformador(f"trafo{k}", 1.0); p.location = (x, 0, 0.16); trafos.append((p, tq, topos))
portais = []
for x in (-14, 14):
    bm = bmesh.new()
    for y in (-7, 7): _viga(bm, (x, y, 0), (x, y, 8.4), 0.22)
    _viga(bm, (x, -7.6, 8.2), (x, 7.6, 8.2), 0.2); _viga(bm, (x, -7, 4.2), (x, 7, 8.2), 0.08); _viga(bm, (x, 7, 4.2), (x, -7, 8.2), 0.08)
    portais.append(_new_obj("portal", bm, METAL))
bm = bmesh.new()
for y in (-3, 0, 3): _viga(bm, (-14, y, 8.0), (14, y, 8.0), 0.07)
for k, x in enumerate(TRX):
    for (bx, by, bz), y in zip(trafos[k][2], (-3, 0, 3)): _viga(bm, (x + bx, by, bz + 0.3), (x + bx, y, 8.0), 0.05)
barras = _new_obj("barramento", bm, C["escuro"])
casa_ctrl = caixa("casaControle", (12, 9.5, 1.7), (6, 4, 3.4), (0.90, 0.88, 0.82, 1)); filho(casa_ctrl, caixa("ctrlTeto", (0, 0, 1.85), (6.4, 4.4, 0.3), (0.45, 0.30, 0.25, 1)))
# cabos da linha de transmissão
PORT_O = [(-14, -3, 8.0), (-14, 3, 8.0), (-14, -1.2, 8.2), (-14, 1.2, 8.2)]
GANT = [(-146, -2.5, 7.5), (-146, 2.5, 7.5), (-146, -1, 7.8), (-146, 1, 7.8)]
bm = bmesh.new()
for y in (-3.2, 3.2): _viga(bm, (-146, y, 0), (-146, y, 8.0), 0.2)
_viga(bm, (-146, -3.6, 7.8), (-146, 3.6, 7.8), 0.18)
gantry = _new_obj("portalUsina", bm, METAL)
vaos = []   # um objeto de cabos por vão (aparece junto com a torre de destino)
nos = [GANT] + fix + [PORT_O]
for k in range(len(nos) - 1):
    bm = bmesh.new()
    for a, b in zip(nos[k], nos[k + 1]): _viga(bm, a, b, 0.06)
    vaos.append(_new_obj(f"vao{k}", bm, C["escuro"]))
bm = bmesh.new(); _viga(bm, (-150, -0.5, 5.2), (-146, 0, 7.8), 0.06); _viga(bm, (-166, 4, 6.0), (-151, 0.2, 4.4), 0.12)
lig_usina = _new_obj("ligUsina", bm, C["escuro"])
# distribuição: postes da subestação até a cidade e ao longo da avenida
PX_POSTES = [26, 40, 54, 68, 80, 92, 104, 116, 128, 140, 152]
bm = bmesh.new()
for x in PX_POSTES:
    _viga(bm, (x, -4.2, 0), (x, -4.2, 7.4), 0.16, seg=6); _viga(bm, (x, -5.2, 6.9), (x, -3.2, 6.9), 0.09)
postes = _new_obj("postes", bm, (0.42, 0.32, 0.24, 1))
bm = bmesh.new(); ant = (14, 0, 8.0)
for x in PX_POSTES:
    for dy in (-0.9, 0.9): _viga(bm, (ant[0], ant[1] + (dy if ant[0] != 14 else dy * 3), ant[2]), (x, -4.2 + dy, 7.0), 0.05)
    ant = (x, -4.2, 7.0)
fios = _new_obj("fiosDistrib", bm, C["escuro"])
LINHA = [(-146, 0, 7.8)] + [(x, 0, HT * 0.88 - 1.0) for x in TX] + [(-14, 0, 8.1), (-8, 0, 8.1)]
DISTR = [(8, 0, 8.1), (14, 0, 8.1)] + [(x, -4.2, 7.1) for x in PX_POSTES]

# câmera
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 24; cam_d.clip_end = 6000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def shot(t0, t1, loc0, tgt0, loc1=None, tgt1=None):
    """Plano de câmera de t0 a t1 (corte seco entre planos: última chave 1 quadro antes do próximo)."""
    for fr, loc, tgt in ((f(t0), loc0, tgt0), (f(t1) - 1, loc1 or loc0, tgt1 or tgt0)):
        for ob, v in ((cam, loc), (alvo, tgt)):
            ob.location = v; ob.keyframe_insert("location", frame=fr)

# agenda de luz: bairros (0,1,2), hospital (H) e ambiente (dia / crepúsculo) — aplicada no fim, no modo realista
LUZ = {"luz0": [(0, 1)], "luz1": [(0, 1)], "luz2": [(0, 1)], "luzH": [(0, 1)], "luzAgua": [(0, 1)], "luzCel": [(0, 1)], "luzBal": [(0, 1)]}
AMB = [(0, "crepusculo")]
def luz(chave, t, v): LUZ[chave].append((t, v))

def queima(tq, janelas_q):
    m = tq.data.materials[0]
    for a, b in janelas_q:
        cor_key(m, a - 0.05, TRAFO); cor_key(m, a + 0.3, QUEIMADO); cor_key(m, b - 0.06, QUEIMADO); cor_key(m, b, TRAFO)

def drone_ataque(alvo_xyz, t_imp, origem, dur=1.6, cor=None, r=7, escala=0.9):
    d = drone(_id("dr"), escala, cor)
    meio = ((origem[0] + alvo_xyz[0]) / 2, (origem[1] + alvo_xyz[1]) / 2, origem[2] * 0.9)
    visivel(d, t_imp - dur, t_imp); caminho(d, t_imp - dur, t_imp, lambda u: bez(origem, meio, alvo_xyz, u), passo=1)
    explosao(alvo_xyz, t_imp, r=r, n=18)

# =====================================================================
# 0 — GANCHO (crepúsculo): drones acertam a subestação e a cidade apaga, bairro por bairro
# =====================================================================
t0, t1 = S[0]
tA, tB = 1.75, 2.65
drone_ataque((0, 0, 4.5), tA, (-30, 150, 75), dur=1.75)
drone_ataque((8, 0, 4.5), tB, (10, 160, 80), dur=1.9)
fogo((0, -0.6, 4.6), tA, t1); fogo((8, -0.6, 4.6), tB, t1, r=0.8)
fumaca((0, 0, 5), tA + 0.2, t1); fumaca((8, 0, 5), tB + 0.2, t1, cada=0.5)
luz("luz0", 2.05, 0); luz("luzH", 2.3, 0); luz("luz1", 2.6, 0); luz("luz2", 3.1, 0); luz("luzAgua", 2.6, 0); luz("luzCel", 2.9, 0)
shot(t0, 4.4, (-21, -22, 8.5), (10, 2, 6.5), (-18, -25, 10), (12, 2, 6.5))
shot(4.4, T(0, "Como") - 0.1, (-9, -17, 6), (4, 0, 6), (-6, -15, 7), (5, 0, 6.5))
shot(T(0, "Como") - 0.1, t1, (44, -66, 30), (100, -8, 12), (50, -70, 34), (102, -8, 12))

# =====================================================================
# 1 — GERAÇÃO (dia): cidade apagada -> a usina nasce
# =====================================================================
t0, t1 = S[1]
AMB.append((t0, "dia"))
tus = T(1, "usina") - 0.15
nasce(us, tus, dur=0.5)
for p in us_topos[:2]: fumaca(p, tus + 0.6, S[2][0] + 5.4, r=1.5, cada=0.6, sobe=12, vida=3.0, cor=(0.93, 0.93, 0.95, 1))
fumaca(us_topos[2], tus + 0.6, S[2][0] + 5.4, r=3.0, cada=0.6, sobe=12, vida=3.0, cor=(0.96, 0.96, 0.98, 1))
tel = T(1, "eletricidade")
for k in range(3):   # anéis de energia saindo do galpão das turbinas
    o = anel(_id("anelE"), (US[0] + 19, US[1], 8.5), 9, 0.35, AMBAR, seg=40, unico="pulsoA"); tt = tel + 0.5 * k
    visivel(o, tt, tt + 1.3); o.scale = (0.05,) * 3; o.keyframe_insert("scale", frame=f(tt)); o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(tt + 1.3))
shot(t0, tus - 0.3, (50, -70, 34), (102, -8, 12), (54, -66, 31), (102, -8, 12))
shot(tus - 0.3, t1, (-134, -50, 11), (-188, 8, 15), (-142, -42, 15), (-188, 8, 15))

# =====================================================================
# 2 — LINHA DE TRANSMISSÃO: elevadora + torres nascendo em sequência
# =====================================================================
t0, t1 = S[2]
tele = T(2, "eleva"); ttor = T(2, "torres") - 0.1
nasce(elev, tele); nasce(gantry, tele + 0.2); nasce(lig_usina, tele + 0.35)
for k, t in enumerate(torres):
    nasce(t, ttor + 0.4 * k); nasce(vaos[k], ttor + 0.4 * k + 0.2)
t_lig = T(3, "transformadores") + 1.1
nasce(vaos[-1], t_lig)
shot(t0, ttor - 0.2, (-262, -46, 44), (-150, 0, 8), (-250, -40, 38), (-140, 0, 8))
shot(ttor - 0.2, t1, (-144, -25, 5), (-120, 0, 10.5), (-72, -29, 9), (-48, 0, 10.5))

# =====================================================================
# 3 — SUBESTAÇÃO: casa queima com alta tensão -> transformadores abaixam -> cidade acende
# =====================================================================
t0, t1 = S[3]
tq_ = T(3, "queimaria") + 0.25; tsub = T(3, "perto") - 0.2; ttr = T(3, "transformadores") - 0.1; tab = T(3, "abaixam"); ttom = T(3, "tomada") - 0.2
casa = caixa("casaTeste", (-24, -11, 1.6), (5, 4.2, 3.2), (0.95, 0.90, 0.80, 1), unico="casaTeste")
filho(casa, cilindro("casaTelhado", (0, 0, 2.5), 3.9, 1.9, (0.70, 0.30, 0.22, 1), seg=4, r2=0.2), caixa("casaPorta", (0, -2.12, -0.7), (0.9, 0.1, 1.8), C["madeira"]))
casa.children[0].rotation_euler = (0, 0, math.radians(45))
fio_casa = cabo("fioCasa", fix[-1][0], (-24, -11, 4.6), 0.06)
for o in (casa, fio_casa): visivel(o, t0, tsub - 0.1)
cor_key(casa.data.materials[0], tq_ - 0.05, (0.95, 0.90, 0.80, 1)); cor_key(casa.data.materials[0], tq_ + 0.3, QUEIMADO)
pulsos([fix[-1][0], (-24, -11, 4.6)], [(t0 + 0.2, tq_)], AMBAR, "pulsoA", cada=0.25, vel=18, r=0.5)
explosao((-24, -11, 3.5), tq_, r=4, n=14); fumaca((-24, -11, 4), tq_ + 0.1, tsub - 0.1, r=0.9, cada=0.3, sobe=9, vida=1.8)
for o in (PAD, cerca): nasce(o, tsub, dur=0.3)
for k, (p, tq, _t) in enumerate(trafos): nasce(p, ttr + 0.28 * k)
for k, o in enumerate(portais): nasce(o, ttr + 0.9 + 0.15 * k)
nasce(barras, ttr + 1.2); nasce(casa_ctrl, ttr + 1.0); nasce(postes, tab - 0.3, dur=0.3); nasce(fios, tab - 0.1, dur=0.3)
luz("luz0", ttom, 1); luz("luzH", ttom + 0.15, 1); luz("luz1", ttom + 0.35, 1); luz("luz2", ttom + 0.7, 1); luz("luzAgua", ttom + 0.35, 1); luz("luzCel", ttom + 0.35, 1)
shot(t0, tsub - 0.1, (-38, -34, 9), (-25, -8, 4.5), (-33, -30, 8), (-24, -9, 4))
shot(tsub - 0.1, ttom - 0.4, (-7, -31, 9.5), (0, 0, 6), (3, -25, 7.5), (1, 0, 6))
shot(ttom - 0.4, t1, (6, -34, 17), (78, -4, 6), (18, -40, 21), (84, -4, 6))

# =====================================================================
# 4 — EQUILÍBRIO DA REDE: balança (palco à parte)
# =====================================================================
t0, t1 = S[4]
PX = 3000
palco = caixa("palcoBal", (PX, 0, -0.5), (700, 700, 1.0), (0.84, 0.82, 0.77, 1))
apoio = cilindro("apoio", (PX, 0, 1.7), 2.6, 3.4, (0.35, 0.38, 0.45, 1), seg=4, r2=0.35); apoio.rotation_euler = (0, 0, math.radians(45))
piv = vazio("pivo", (PX, 0, 3.45))
prancha = caixa("prancha", (0, 0, 0.25), (20, 4.4, 0.5), C["madeira"]); filho(piv, prancha)
def mini_usina(nome, x):
    b = caixa(nome, (x, 0, 1.7), (3.6, 3.0, 2.4), (0.82, 0.82, 0.80, 1)); filho(piv, b)
    filho(b, cilindro(nome + "_c", (-0.9, 0.6, 2.6), 0.4, 3.0, CONC, seg=10, r2=0.28), caixa(nome + "_t", (0, 0, 1.3), (3.8, 3.2, 0.2), (0.42, 0.46, 0.52, 1)),
          caixa(nome + "_v", (0.3, -1.52, 0.2), (2.4, 0.06, 0.6), (0.20, 0.42, 0.62, 1)), esfera(nome + "_e", (0.9, 0, 1.9), 0.55, AMBAR, sub=1, unico="pulsoA"))
    return b
def mini_casa(nome, x, y=0):
    b = caixa(nome, (x, y, 1.4), (2.0, 2.0, 1.8), random.choice(PAREDES)); filho(piv, b)
    tl = cilindro(nome + "_t", (0, 0, 1.45), 1.75, 1.1, (0.70, 0.30, 0.22, 1), seg=4, r2=0.1); tl.rotation_euler = (0, 0, math.radians(45))
    filho(b, tl, caixa(nome + "_j", (0, -1.02, 0.1), (0.7, 0.06, 0.7), COR_JAN, unico="luzBal"))
    return b
obal = [palco, apoio, piv, mini_usina("mu0", -7.0), mini_casa("mc0", 5.4), mini_casa("mc1", 8.0)]
for o in obal: visivel(o, t0, t1)
tga = T(4, "gasta") - 0.1; tpr = T(4, "produzido")
mcx = mini_casa("mcx", 6.7); mcx.location = (6.7, 0, 3.2); visivel(mcx, tga, t1); pop(mcx, tga)   # mais consumo: outra casa em cima
mu1 = mini_usina("mu1", -3.6); visivel(mu1, tpr, t1); pop(mu1, tpr)
piv.rotation_mode = "XYZ"
for t, g in ((t0, 0), (T(4, "eletricidade"), 3), (T(4, "guarda"), -3), (tga - 0.1, 0), (tga + 0.6, 9), (tpr, 9), (tpr + 0.7, -1.5), (tpr + 1.2, 0.8), (tpr + 1.7, 0), (t1, 0)):
    piv.rotation_euler = (0, math.radians(g), 0); piv.keyframe_insert("rotation_euler", frame=f(t))
shot(t0, t1, (PX - 3, -30, 8), (PX, 0, 6.4), (PX + 3, -28, 7.5), (PX, 0, 6.4))

# =====================================================================
# 5 — PONTO FRACO (crepúsculo): não é a usina; é o transformador. Reposição leva mais de um ano
# =====================================================================
t0, t1 = S[5]
AMB.append((t0, "crepusculo"))
tnao = T(5, "inimigo"); tbasta = T(5, "Basta") - 0.15; thit = T(5, "Um") - 0.45; tlev = T(5, "levar") - 0.25
for p in us_topos[:2]: fumaca(p, t0, tbasta, r=1.5, cada=0.6, sobe=12, vida=3.0, cor=(0.80, 0.80, 0.84, 1))
m1 = alvo_vermelho((US[0], US[1], 14), 12, tnao + 0.4, T(5, "não")); m1.rotation_euler = (math.radians(75), 0, 0)
xis = []
for a in (45, -45):
    x = caixa(_id("xis"), (US[0], US[1] - 9, 14), (30, 0.8, 2.4), C["branco"], unico="xis"); x.rotation_euler = (0, math.radians(a), 0)
    visivel(x, T(5, "não"), tbasta); pop(x, T(5, "não")); xis.append(x)
m2 = alvo_vermelho((0, 0, 6.6), 4.2, tbasta + 0.35, thit)
drone_ataque((0, 0, 4.5), thit, (-60, 150, 80), dur=1.5)
fogo((0, -0.6, 4.6), thit, S[7][0]); fumaca((0, 0, 5), thit + 0.2, S[6][1], cada=0.45)
luz("luz0", thit + 0.25, 0)
# carreta com o transformador novo (devagar pela estrada)
car, _l = caminhao("carreta", (0, 0, 0), cor=(0.85, 0.55, 0.12, 1), tubos=False)
prancha_c = caixa("carretaPrancha", (0, -9.0, 0.1), (2.8, 11, 0.5), (0.30, 0.32, 0.34, 1)); filho(car, prancha_c)
for y in (-5.5, -7.5, -9.5, -11.5, -13.5):
    for x in (-1.4, 1.4):
        r = cilindro(_id("rodaC"), (x, y, -0.4), 0.55, 0.4, C["escuro"], seg=8); r.rotation_euler = (0, math.radians(90), 0); filho(car, r)
tn, _tq, _tt = transformador("trafoNovo", 0.62, cor=(0.55, 0.62, 0.70, 1)); tn.rotation_euler = (0, 0, math.radians(90)); tn.location = (0, -9.0, 0.35); filho(car, tn)
visivel(car, tlev - 0.2, t1)
caminho(car, tlev - 0.2, t1, lambda u: (-84 + 9 * u, -16, 1.0), passo=2)
shot(t0, tbasta, (-200, -72, 18), (-183, 6, 12), (-186, -62, 22), (-182, 6, 12))
shot(tbasta, tlev, (-11, -25, 9), (0, 0, 6), (-5, -17, 7), (1, 0, 6))
shot(tlev, t1, (-63, -29, 4.5), (-82, -16, 4.2), (-60, -28, 5), (-78, -16, 4.2))

# =====================================================================
# 6 — EFEITO CASCATA (crepúsculo): sobrecarga, desligamento automático, bairros apagam
# =====================================================================
t0, t1 = S[6]
tsob = T(6, "sobrecarrega") - 0.1; tdes = T(6, "desligam"); tbai = T(6, "Bairro")
bm = bmesh.new()
for y in (-3, 3): _viga(bm, (-14, y, 8.0), (14, y, 8.0), 0.28)
ant = (14, 0, 8.0)
for x in PX_POSTES[:3]: _viga(bm, ant, (x, -4.2, 7.0), 0.28); ant = (x, -4.2, 7.0)
_viga(bm, (-30, 0, HT * 0.88 - 1.0), (-14, 0, 8.1), 0.28)
sobre = _new_obj("sobrecarga", bm, VERMELHO, unico="sobrecarga"); visivel_janelas(sobre, [(tsob + 0.25 * k, tsob + 0.25 * k + 0.13) for k in range(int((tdes - tsob) / 0.25))] + [(tdes - 0.2, tdes + 0.25)])
for x in (-8, 8):
    alvo_vermelho((x, 0, 6.6), 4.0, tsob + 0.2, tdes + 0.2)
    explosao((x, -0.5, 5.6), tdes + 0.2, r=2.5, n=10)
luz("luz1", tbai + 0.15, 0); luz("luzH", tbai + 0.45, 0); luz("luz2", T(6, "tudo"), 0)
luz("luzAgua", T(6, "bombas") + 0.3, 0); luz("luzCel", T(6, "sinal") + 0.2, 0)
gota = cilindro("gota", (CX_AGUA[0], CX_AGUA[1] - 3.2, 4.0), 0.14, 8.0, CIANO, seg=6, unico="luzAgua")   # jato de água que para
visivel_janelas(gota, [(0, 2.6), (S[3][1] - 3, T(6, "bombas") + 0.3), (S[7][0], FIM + 5)])
shot(t0, tbai - 0.1, (-10, -40, 22), (6, 0, 6), (6, -36, 19), (8, 0, 6))
shot(tbai - 0.1, T(6, "Sem") - 0.1, (50, -70, 34), (102, -8, 11), (62, -70, 31), (104, -8, 11))
shot(T(6, "Sem") - 0.1, t1, (74, -78, 11), (88, -46, 8.5), (98, -76, 13), (97, -46, 9.5))

# =====================================================================
# 7 — RESPOSTAS (dia): antiaérea, barreiras, sacos de areia; gerador no hospital; rodízio (crepúsculo)
# =====================================================================
t0, t1 = S[7]
AMB.append((t0, "dia"))
for ch in ("luz0", "luz1", "luz2", "luzH", "luzAgua", "luzCel"): luz(ch, t0, 1)
tdef = T(7, "antiaérea") - 0.2; tbar = T(7, "barreiras") - 0.1; tsac = T(7, "sacos") - 0.1; tger = T(7, "geradores") - 0.1; trod = T(7, "cortes") - 0.1
for k, (x, y) in enumerate(((-16, -10.5), (16, -10.5))):
    cn = canhao(_id("aa"), (x, y, 0.5)); visivel(cn, tdef + 0.2 * k); pop(cn, tdef + 0.2 * k)
rd = radar("radarSub", (-24, 8, 0.75)); rdb, rdg = rd; visivel(rdb, tdef + 0.4); pop(rdb, tdef + 0.4)
rdg.rotation_euler = (0, 0, 0); rdg.keyframe_insert("rotation_euler", frame=f(t0)); rdg.rotation_euler = (0, 0, math.radians(360 * 6)); rdg.keyframe_insert("rotation_euler", frame=f(FIM))
tint = tdef + 1.5; pint = (-4, 36, 20)
di = drone(_id("dint"), 0.9); visivel(di, tint - 1.4, tint); caminho(di, tint - 1.4, tint, lambda u: lerp((30, 170, 70), pint, u))
rastro(lambda u: lerp((-16, -10.5, 3), pint, u), tint - 0.45, tint, C["defesa"], r=0.3, cada=0.04, vida=0.35)
explosao(pint, tint, r=5, n=14)
for k, x in enumerate((-12.2, -4, 4, 12.2)):
    b = caixa(_id("muro"), (x, 0, 2.3), (0.6, 5.6, 4.3), CONC); visivel(b, tbar + 0.12 * k); pop(b, tbar + 0.12 * k)
for k, x in enumerate(TRX):
    sa = sacos_areia(_id("sacos"), 6.4, 5); sa.location = (x, -3.4, 0.16); visivel(sa, tsac + 0.15 * k); pop(sa, tsac + 0.15 * k)
ger = gerador("geradorHosp"); ger.location = (hx + 1.5, hy - 7.5, 0); visivel(ger, tger + 0.3); pop(ger, tger + 0.3, escala=1.25)
cabo_g = cabo("caboGer", (hx + 1.5, hy - 6.6, 1.2), (hx + 1.5, hy - 4.6, 1.2), 0.1, C["laranja"]); visivel(cabo_g, tger + 0.6)
AMB.append((tger, "crepusculo"))
luz("luz0", tger, 0); luz("luzH", tger, 0); luz("luzH", tger + 0.75, 1)
est = [(1, 0, 1), (0, 1, 0)]; k = 0; t = trod
while t < t1:
    for b in range(3): luz("luz%d" % b, t, est[k % 2][b])
    k += 1; t += 0.95
shot(t0, tger, (-18, -31, 11), (0, -3, 6), (-6, -27, 9.5), (1, -3, 6))
shot(tger, trod, (52, -60, 8), (hx + 1, hy - 4, 4.5), (57, -57, 9), (hx + 1, hy - 4, 4.5))
shot(trod, t1, (58, -76, 46), (104, -8, 10), (72, -74, 42), (106, -8, 10))

# =====================================================================
# 8 — OS DOIS LADOS (dia): drones contra uma refinaria (palco à parte)
# =====================================================================
t0, t1 = S[8]
AMB.append((t0, "dia"))
for ch in ("luz0", "luz1", "luz2", "luzH"): luz(ch, t0, 1)
RX = -3000; oref = [caixa("palcoRef", (RX, 0, -0.5), (700, 700, 1.0), (0.78, 0.74, 0.66, 1))]
TQS = [(RX - 12, -2), (RX - 1, -2), (RX - 12, 10), (RX - 1, 10)]
for k, (x, y) in enumerate(TQS):
    tq = cilindro(f"tqRef{k}", (x, y, 3.0), 4.6, 6.0, (0.93, 0.93, 0.91, 1), seg=20, unico=f"tqRef{k}")
    filho(tq, cilindro(f"tqTeto{k}", (0, 0, 3.3), 4.6, 0.7, (0.80, 0.80, 0.80, 1), seg=20, r2=1.0), anel(f"tqAro{k}", (0, 0, 2.2), 4.62, 0.1, (0.55, 0.57, 0.60, 1), seg=28))
    oref.append(tq)
for k, (x, y, h) in enumerate(((RX + 10, 2, 17), (RX + 14, 5, 13), (RX + 10, 9, 10))):
    col = cilindro(f"coluna{k}", (x, y, h / 2), 1.1, h, (0.78, 0.80, 0.84, 1), seg=14)
    for z in range(3, int(h), 3): filho(col, anel(_id("plat"), (0, 0, z - h / 2), 1.5, 0.12, C["defesa"], seg=18))
    oref.append(col)
bm = bmesh.new()
for y in (-8, -7.2): _viga(bm, (RX - 18, y, 1.6), (RX + 18, y, 1.6), 0.25, seg=8)
for x in range(-18, 19, 6): _viga(bm, (RX + x, -8, 0), (RX + x, -8, 1.6), 0.15); _viga(bm, (RX + x, -7.2, 0), (RX + x, -7.2, 1.6), 0.15)
_viga(bm, (RX + 10, 2, 2), (RX + 10, -7.2, 1.6), 0.25, seg=8); _viga(bm, (RX - 1, -2, 1.2), (RX - 1, -7.6, 1.6), 0.2, seg=8)
oref.append(_new_obj("dutosRef", bm, (0.72, 0.74, 0.76, 1)))
tocha = cilindro("tocha", (RX + 19, 12, 11), 0.3, 22, METAL, seg=8); filho(tocha, esfera("chama", (0, 0, 11.8), 1.0, C["laranja"], sub=1, unico="fogo")); oref.append(tocha)
oref.append(caixa("predioRef", (RX + 19, -1, 2.2), (6, 5, 4.4), (0.88, 0.86, 0.80, 1)))
for o in oref: visivel(o, t0, t1)
tdr = T(8, "drones") - 0.2; th1 = T(8, "refinarias") + 0.45
CINZA_D = (0.80, 0.82, 0.85, 1)
drone_ataque((RX - 1, -2, 6.5), th1, (RX + 150, -40, 60), dur=th1 - tdr, cor=CINZA_D, r=8)
drone_ataque((RX - 12, 10, 6.5), th1 + 0.55, (RX + 160, 20, 70), dur=th1 - tdr + 0.5, cor=CINZA_D, r=7)
dp = drone(_id("dpass"), 0.9, CINZA_D); visivel(dp, tdr + 0.3, t1); caminho(dp, tdr + 0.3, t1, lambda u: lerp((RX + 120, 70, 40), (RX - 120, 30, 34), u), passo=2)
fogo((RX - 1, -2.5, 6.8), th1, t1, r=1.3); fumaca((RX - 1, -2, 7), th1 + 0.2, t1, r=1.8, cada=0.3, sobe=16)
fogo((RX - 12, 9.5, 6.8), th1 + 0.55, t1, r=1.1); fumaca((RX - 12, 10, 7), th1 + 0.75, t1, r=1.5, cada=0.4, sobe=14)
for k, d in ((1, 0), (2, 0.55)):
    m = bpy.data.objects[f"tqRef{k}"].data.materials[0]; cor_key(m, th1 + d - 0.05, (0.93, 0.93, 0.91, 1)); cor_key(m, th1 + d + 0.4, (0.22, 0.20, 0.19, 1))
shot(t0, t1, (RX + 15, -37, 9), (RX - 3, 2, 8), (RX + 7, -44, 14), (RX - 3, 2, 8))

# =====================================================================
# 9/10 — FINAL (dia): a rede inteira funcionando, da usina à cidade
# =====================================================================
t0 = S[9][0]
for p in us_topos[:2]: fumaca(p, t0 - 2.5, FIM, r=1.5, cada=0.7, sobe=12, vida=3.0, cor=(0.93, 0.93, 0.95, 1))
fumaca(us_topos[2], t0 - 2.5, FIM, r=3.0, cada=0.7, sobe=12, vida=3.0, cor=(0.96, 0.96, 0.98, 1))
shot(t0, S[10][0], (-36, -28, 13), (18, 0, 8), (-26, -34, 17), (22, 0, 8))
shot(S[10][0], FIM + 0.1, (-26, -34, 17), (22, 0, 8), (-8, -46, 25), (36, 0, 8))

# energia correndo pelos cabos
pulsos([(US[0] + 19, US[1], 7), (-150, 0, 5.0), (-146, 0, 7.8)], [(tel + 0.3, S[2][0] + 5.4), (S[5][0], tbasta), (S[9][0] - 2, FIM)], AMBAR, "pulsoA", cada=0.5, vel=22, r=0.65)
pulsos(LINHA[:-2], [(ttor + 1.0, t_lig)], AMBAR, "pulsoA")
pulsos(LINHA, [(t_lig, S[4][0]), (S[5][0] + 3.0, thit), (S[7][0], tger), (S[9][0] - 3.5, FIM)], AMBAR, "pulsoA")
pulsos(DISTR, [(tab, S[4][0]), (S[5][0] + 3.0, thit), (S[7][0], tger), (S[9][0] - 3.5, FIM)], CIANO, "pulsoB", vel=40)

for ob in (cam, alvo):
    for fc in ob.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

# ---------- render ----------
if os.environ.get("REALISTA"):
    HD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "hdri")
    bg, sol = modo_realista(os.path.join(HD, "ceu_parcialmente_nublado_2k.hdr"), foco=alvo)
    def emissivo(chave, cor, forca):
        saida = []
        for m in bpy.data.materials:
            if any(v == m and k[1] == chave for k, v in _mats.items()):
                b = m.node_tree.nodes.get("Principled BSDF"); b.inputs["Emission Color"].default_value = _lin(cor); b.inputs["Emission Strength"].default_value = forca; saida.append((m, b))
        return saida
    def degrau(idb, dono_anim):
        ad = dono_anim.animation_data
        if ad and ad.action:
            for fc in ad.action.fcurves:
                if "Emission Strength" in fc.data_path or idb in fc.data_path:
                    for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
    FORCA = {"luz0": 4.0, "luz1": 4.0, "luz2": 4.0, "luzH": 4.5, "luzAgua": 5.0, "luzCel": 8.0, "luzBal": 4.0}
    CORL = {"luzAgua": CIANO, "luzCel": VERMELHO}
    for chave, agenda in LUZ.items():
        for m, b in emissivo(chave, CORL.get(chave, (1.0, 0.74, 0.36, 1)), FORCA[chave]):
            sk = b.inputs["Emission Strength"]
            for t, v in sorted(agenda):
                sk.default_value = FORCA[chave] * v; sk.keyframe_insert("default_value", frame=f(t))
            for fc in m.node_tree.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
    emissivo("pulsoA", AMBAR, 9.0); emissivo("pulsoB", CIANO, 9.0); emissivo("fogo", (1.0, 0.20, 0.02, 1), 1.1)
    emissivo("sobrecarga", VERMELHO, 12.0); emissivo("mira", VERMELHO, 5.0); emissivo("xis", (1, 1, 1, 1), 1.5)
    for m in bpy.data.materials:   # explosões brilham (laranja compartilhado)
        if tuple(round(c, 3) for c in m.diffuse_color) == tuple(round(c, 3) for c in C["laranja"]):
            b = m.node_tree.nodes.get("Principled BSDF"); b.inputs["Emission Color"].default_value = _lin((1.0, 0.35, 0.05, 1)); b.inputs["Emission Strength"].default_value = 4.0
    # ambiente: dia (céu parcialmente nublado) x crepúsculo (céu de pôr do sol, sol fraco) — corte seco entre cenas
    nt = scn.world.node_tree
    env1 = next(n for n in nt.nodes if n.type == "TEX_ENVIRONMENT")
    env2 = nt.nodes.new("ShaderNodeTexEnvironment"); env2.image = bpy.data.images.load(os.path.join(HD, "ceu_por_do_sol_2k.hdr"))
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    nt.links.new(env1.outputs["Color"], mix.inputs[6]); nt.links.new(env2.outputs["Color"], mix.inputs[7]); nt.links.new(mix.outputs[2], bg.inputs["Color"])
    AMBV = {"dia": (0.0, 1.1, 4.5, (1.0, 0.80, 0.58)), "crepusculo": (1.0, float(os.environ.get("CREP_BG", "0.42")), float(os.environ.get("CREP_SOL", "0.6")), (1.0, 0.55, 0.35))}
    for t, modo in sorted(AMB):
        fac, forca, e_sol, c_sol = AMBV[modo]; fr = f(t)
        mix.inputs[0].default_value = fac; mix.inputs[0].keyframe_insert("default_value", frame=fr)
        bg.inputs["Strength"].default_value = forca; bg.inputs["Strength"].keyframe_insert("default_value", frame=fr)
        sol.energy = e_sol; sol.keyframe_insert("energy", frame=fr); sol.color = c_sol; sol.keyframe_insert("color", frame=fr)
    for dono in (nt, sol):
        for fc in dono.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
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
