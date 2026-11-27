"""Vídeo Ebola e guerra — "Como uma guerra espalha o Ebola?" (Congo, 27/11/2026). Uso:
REALISTA=1 blender -b --factory-startup -P cena_ebola.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
import bpy, bmesh, sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
from lowpoly import *
from lowpoly import _id, _lin, _new_obj, _mats

args = sys.argv[sys.argv.index("--") + 1:]
PASTA = args[0]
LEG = json.load(open(os.path.join(PASTA, "legendas.json"), encoding="utf-8"))
FIM = LEG[-1]["e"] + 6.2          # sobra para o pedido de like
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
random.seed(2711)

VERMELHO = (1.0, 0.15, 0.10, 1); AMARELO = (0.98, 0.82, 0.15, 1); VERDE = (0.25, 0.90, 0.40, 1)
AZUL = (0.15, 0.45, 0.80, 1); BRANCO = C["branco"]; TERRA = (0.62, 0.40, 0.26, 1); OLIVA = C["oliva"]
ROUPAS = [(0.85, 0.30, 0.20, 1), (0.20, 0.50, 0.80, 1), (0.95, 0.75, 0.20, 1), (0.30, 0.65, 0.35, 1), (0.70, 0.35, 0.65, 1), (0.95, 0.55, 0.25, 1)]
def andar(ob, t0, t1, a, b):
    ob.location = a; ob.keyframe_insert("location", frame=f(t0)); ob.location = b; ob.keyframe_insert("location", frame=f(t1))
def rumo(ob, t, graus):
    ob.rotation_euler = (0, 0, math.radians(graus)); ob.keyframe_insert("rotation_euler", frame=f(t), index=2)
def polar(c, r, ang, z=0.0): return (c[0] + r * math.cos(math.radians(ang)), c[1] + r * math.sin(math.radians(ang)), z)
def texto3d(nome, txt, tam, cor, chave):
    cd = bpy.data.curves.new(nome, "FONT"); cd.body = txt; cd.extrude = 0.4; cd.size = tam; cd.align_x = "CENTER"; cd.bevel_depth = 0.05
    o = bpy.data.objects.new(nome, cd); scn.collection.objects.link(o); o.data.materials.append(mat(cor, chave)); return o

# =====================================================================
# TERRENO: savana verde com estrada de terra Bunia (sul) -> front (norte)
# =====================================================================
caixa("chao", (0, 0, -0.5), (1600, 1600, 1.0), C["grama"])
V = (0, 0)            # aldeia
CT = (46, -14)        # centro de tratamento
ENT = (36, 30)        # área de enterro seguro
BU = (-70, -95)       # Bunia (base da resposta)
FR = (-70, 105)       # Iga-Barrière (front, cidade de mineração)
HOSP = (-125, 40)     # hospital cercado (Akwe)
caixa("estradaNS", (-70, 5, 0.03), (6, 210, 0.06), (0.70, 0.52, 0.36, 1))
caixa("estradaV", (-35, -6, 0.03), (70, 5, 0.06), (0.70, 0.52, 0.36, 1))
caixa("estradaCT", (24, -10, 0.03), (44, 4, 0.06), (0.70, 0.52, 0.36, 1))
caixa("estradaH", (-98, 40, 0.03), (56, 4, 0.06), (0.70, 0.52, 0.36, 1))
for _ in range(28):
    m = esfera("morro", (random.uniform(-500, 500), random.uniform(220, 420), -4), random.uniform(20, 46), random.choice([C["morro"], C["grama2"]]), sub=2)
    m.scale = (1.7, 1.0, 0.5)
random.seed(5)
for _ in range(150):
    x = random.uniform(-220, 200); y = random.uniform(-170, 190)
    if math.hypot(x - V[0], y - V[1]) < 30 or math.hypot(x - CT[0], y - CT[1]) < 20 or math.hypot(x - ENT[0], y - ENT[1]) < 12: continue
    if math.hypot(x + 22, y - 62) < 16: continue
    if abs(x + 70) < 8 or math.hypot(x - BU[0], y - BU[1]) < 40 or math.hypot(x - FR[0], y - FR[1]) < 32 or math.hypot(x - HOSP[0], y - HOSP[1]) < 16: continue
    if abs(y + 6) < 5 and -70 < x < 0 or abs(y - 40) < 5 and -126 < x < -70: continue
    arvore((x, y), random.uniform(1.0, 1.9))

# =====================================================================
# 1) ALDEIA: cabanas, moradores (alguns doentes com marcador vermelho)
# =====================================================================
random.seed(17)
CASAS = []
for k in range(16):
    a = k * 360 / 16 + random.uniform(-8, 8); r = random.choice((11, 15, 20, 24))
    loc = polar(V, r, a)
    c_ = cabana(_id("cabana"), loc, r=random.uniform(1.9, 2.5), h=random.uniform(1.8, 2.2))
    c_.rotation_euler = (0, 0, math.radians(a + 90)); CASAS.append(c_)
cilindro("terreiro", (V[0], V[1], 0.05), 9, 0.1, (0.72, 0.56, 0.40, 1), seg=24)
PESS = []
for k in range(22):
    a = random.uniform(0, 360); r = random.uniform(3, 26)
    p_, _, _ = boneco(_id("morador"), polar(V, r, a), camisa=random.choice(ROUPAS), capacete=False)
    p_.rotation_euler = (0, 0, math.radians(random.uniform(0, 360))); PESS.append(p_)
def marcador(pai, cor, chave, r=0.6, z=3.2):
    m_ = esfera(_id("marca"), (0, 0, z), r, cor, sub=2, unico=chave); filho(pai, m_); return m_
# paciente zero (no terreiro) + doentes do gancho
PAC = PESS[0]; PAC.location = (V[0] + 2, V[1] - 1, 0)
DOENTES = PESS[:7]
MARC_D = [marcador(p_, VERMELHO, "caso") for p_ in DOENTES]
# contatos do paciente zero (amarelos) ligados por cabos
CONT = PESS[7:13]
MARC_C = [marcador(p_, AMARELO, "contato") for p_ in CONT]
LIG = []
for p_ in CONT:
    a = Vector(PAC.location) + Vector((0, 0, 3.2)); b = Vector(p_.location) + Vector((0, 0, 3.2))
    LIG.append(cabo(_id("lig"), tuple(a), tuple(b), r=0.07, cor=AMARELO, unico="contato"))
# anel do cerco (verde) ao redor da aldeia
CERCO = anel("cerco", (V[0], V[1], 0.3), 30, 0.35, VERDE, seg=96, unico="cerco")
# casos fora das listas (cerco furado)
FUROS = []
random.seed(81)
for k in range(10):
    a = random.uniform(0, 360); r = random.uniform(36, 60)
    p_, _, _ = boneco(_id("fora"), polar(V, r, a), camisa=random.choice(ROUPAS), capacete=False)
    marcador(p_, VERMELHO, "caso", r=1.1, z=3.6); FUROS.append(p_)

# =====================================================================
# 2) CENTRO DE TRATAMENTO + ENTERRO SEGURO
# =====================================================================
TENDAS = []
for k, (dx, dy) in enumerate(((-7, 5), (7, 5), (-7, -9), (7, -9))):
    TENDAS.append(tenda_medica(_id("tenda"), (CT[0] + dx, CT[1] + dy), w=6, d=10))
for k in range(40):
    a = k * 9
    cilindro(_id("cercaCT"), (CT[0] + 18 * math.cos(math.radians(a)), CT[1] + 16 * math.sin(math.radians(a)), 0.8), 0.08, 1.6, (0.85, 0.85, 0.82, 1), seg=5)
caixa("pisoCT", (CT[0], CT[1], 0.06), (34, 30, 0.12), (0.80, 0.78, 0.72, 1))
TANQUE = cilindro("caixaDagua", (CT[0] + 15, CT[1] + 12, 4), 1.6, 2.4, (0.20, 0.35, 0.60, 1), seg=14)
cilindro("torreAgua", (CT[0] + 15, CT[1] + 12, 1.4), 0.25, 2.8, C["cinza"], seg=6)
# área de enterro: montes de terra + equipe de branco carregando caixa
for k in range(6):
    mt = esfera(_id("monte"), (ENT[0] - 6 + (k % 3) * 5, ENT[1] - 3 + (k // 3) * 6, 0), 1.4, TERRA, sub=1); mt.scale = (1.0, 2.0, 0.35)
EQ = []
for k, (dx, dy) in enumerate(((-1.1, 0), (1.1, 0), (-1.1, -2.6), (1.1, -2.6))):
    e_, bd, be = agente_epi(_id("enterro"), (0, 0, 0)); EQ.append((e_, (dx, dy), bd, be))
caixao = caixa("caixa_enterro", (0, 0, 0), (1.3, 3.4, 0.6), (0.92, 0.92, 0.90, 1))
# agentes de saúde (van)
van, _ = caminhao("vanSaude", (0, 0, 1.0), cor=BRANCO, tubos=False)
filho(van, caixa("bauVan", (0, -1.0, 1.25), (2.4, 4.6, 1.9), BRANCO))
filho(van, caixa("faixaVan", (0, -1.0, 1.25), (2.45, 4.62, 0.35), AZUL))
AG1, a1d, a1e = agente_epi("agente1", (0, 0, 0)); AG2, a2d, a2e = agente_epi("agente2", (0, 0, 0))

# =====================================================================
# 3) PEÇAS DA RESPOSTA (pedestais) — a 4ª (vacina) vazia com "?"
# =====================================================================
PD = (-22, 62)
PEDS = []
for k in range(4):
    loc = (PD[0] - 9 + k * 6, PD[1])
    ped = cilindro(_id("pedestal"), (loc[0], loc[1], 1.0), 2.0, 2.0, (0.30, 0.32, 0.36, 1), seg=14); PEDS.append(ped)
ic1 = esfera("icCaso", (0, 0, 2.2), 1.0, VERMELHO, sub=2, unico="caso"); filho(PEDS[0], ic1)
ic2 = vazio("icRastro"); filho(PEDS[1], ic2); ic2.location = (0, 0, 2.2)
for k in range(5):
    a = k * 72
    filho(ic2, esfera(_id("icC"), (1.1 * math.cos(math.radians(a)), 1.1 * math.sin(math.radians(a)), 0), 0.32, AMARELO, sub=1, unico="contato"))
filho(ic2, esfera(_id("icC0"), (0, 0, 0), 0.4, VERMELHO, sub=1, unico="caso"))
ic3 = anel("icCerco", (0, 0, 0), 1.3, 0.22, VERDE, seg=32, unico="cerco"); filho(PEDS[2], ic3); ic3.location = (0, 0, 2.3)
frasco = cilindro("frascoFantasma", (0, 0, 0), 0.6, 1.8, (0.85, 0.90, 0.95, 1), seg=16); filho(PEDS[3], frasco); frasco.location = (0, 0, 2.0)
filho(frasco, cilindro("tampa", (0, 0, 1.05), 0.45, 0.35, AZUL, seg=16))
interrog = texto3d("interrog", "?", 4.5, AMARELO, "interrog"); interrog.rotation_euler = (math.radians(90), 0, 0)
piv_q = vazio("pivQ", (PEDS[3].location[0], PEDS[3].location[1], 5.0)); filho(piv_q, interrog); interrog.location = (0, 0, 0)

# =====================================================================
# 4) BUNIA (base da resposta), FRONT (Iga-Barrière) e HOSPITAL CERCADO
# =====================================================================
random.seed(44)
for k in range(26):
    x = BU[0] + random.uniform(-32, 32); y = BU[1] + random.uniform(-26, 22)
    if abs(x - BU[0]) < 5: continue
    predio((x, y), random.uniform(4, 7), random.uniform(4, 7), random.uniform(3, 7), random.choice(PREDIOS))
for k in range(4):
    tenda_medica(_id("tendaBase"), (BU[0] + 10 + k * 7, BU[1] + 30), w=5, d=8)
# front: cidade de mineração (cava + barracos) e combates
cava = cilindro("cava", (FR[0] + 16, FR[1] + 6, 0.02), 12, 0.1, (0.55, 0.36, 0.22, 1), seg=24)
for k in range(14):
    x = FR[0] + random.uniform(-22, 6); y = FR[1] + random.uniform(-14, 16)
    if abs(x - FR[0]) < 5: continue
    caixa(_id("barraco"), (x, y, 1.2), (random.uniform(3, 5), random.uniform(3, 4), 2.4), random.choice([(0.70, 0.70, 0.72, 1), (0.60, 0.48, 0.36, 1), (0.75, 0.62, 0.45, 1)]))
# colunas de fumaça permanentes sobre o front (poucos objetos, só "respiram")
FUMACAS = []
for k, (dx, dy) in enumerate(((-12, 16), (4, 20), (16, 26))):
    for j in range(7):
        cz = 2 + j * 2.6; rr = 1.0 + j * 0.45
        o = esfera(_id("fumFront"), (FR[0] + dx + j * 0.9, FR[1] + dy + j * 0.5, cz), rr, (0.30, 0.29, 0.29, 1) if j < 3 else (0.55, 0.54, 0.53, 1), sub=3, unico="fumaca")
        for tt, sc in ((0, 0.9), (20, 1.08), (40, 0.92), (60, 1.1), (90, 0.95)):
            o.scale = (sc,) * 3; o.keyframe_insert("scale", frame=f(tt))
        FUMACAS.append(o)
    fogo = esfera(_id("fogo"), (FR[0] + dx, FR[1] + dy, 0.5), 1.0, (1.0, 0.45, 0.08, 1), sub=2, unico="fogo"); fogo.scale = (1, 1, 0.7)
sa = sacos_areia("sacosFront", comprimento=10, fiadas=3); sa.location = (FR[0], FR[1] - 22, 0)
CAM_M = []
for k in range(3):
    cm, _ = caminhao(_id("caminhaoMil"), (0, 0, 1.0), cor=OLIVA, tubos=False)
    filho(cm, caixa(_id("lona"), (0, -1.0, 1.4), (2.4, 4.4, 1.8), (0.36, 0.40, 0.24, 1))); CAM_M.append(cm)
SOLD = []
for k in range(6):
    s_, _, _ = boneco(_id("soldado"), (FR[0] - 6 + k * 2.4, FR[1] - 24, 0), camisa=OLIVA, capacete=True); SOLD.append(s_)
# barreira na estrada (bloqueia a van)
barreira = sacos_areia("barreira", comprimento=7, fiadas=2); barreira.location = (-70, 20, 0)
# deslocados andando para Bunia
DESL = []
for k in range(14):
    d_, _, _ = boneco(_id("deslocado"), (0, 0, 0), camisa=random.choice(ROUPAS), capacete=False)
    filho(d_, caixa(_id("trouxa"), (0, -0.1, 2.55), (0.7, 0.7, 0.45), random.choice([(0.85, 0.55, 0.25, 1), (0.30, 0.45, 0.70, 1), (0.80, 0.25, 0.25, 1)])))
    DESL.append(d_)
# hospital cercado (Akwe)
hosp = predio((HOSP[0], HOSP[1]), 14, 9, 5, (0.92, 0.90, 0.84, 1))
caixa("faixaHosp", (HOSP[0], HOSP[1] - 4.52, 3.4), (14.02, 0.05, 0.8), AZUL)
for k in range(5):
    caixa(_id("janHosp"), (HOSP[0] - 5.2 + k * 2.6, HOSP[1] - 4.55, 2.0), (1.4, 0.05, 1.0), (0.18, 0.28, 0.36, 1))
PRESOS = []
for k in range(2):
    pr, _, _ = agente_epi(_id("preso"), (HOSP[0] - 1.5 + k * 3, HOSP[1] - 6, 0)); pr.rotation_euler = (0, 0, math.radians(180)); PRESOS.append(pr)

cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 24; cam_d.clip_end = 6000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def shot(t0, t1, loc0, tgt0, loc1=None, tgt1=None):
    for fr, loc, tgt in ((f(t0), loc0, tgt0), (f(t1) - 1, loc1 or loc0, tgt1 or tgt0)):
        for ob, v in ((cam, loc), (alvo, tgt)):
            ob.location = v; ob.keyframe_insert("location", frame=fr)

# ---------- S0: gancho — aldeia enchendo de casos; guerra no horizonte ----------
t0, t1 = S[0]
th = T(0, "história"); tg = T(0, "guerra"); tp = T(0, "Peça")
for k, m_ in enumerate(MARC_D): pop(m_, 0.05 + 0.12 * k, 1.0, 0.25)
visivel_janelas(MARC_D[0], [(0.0, FIM)])
for k, m_ in enumerate(MARC_D[1:]): visivel_janelas(m_, [(0.0, S[1][0]), (S[7][0], FIM)])
for k, p_ in enumerate(FUROS[:6]): visivel_janelas(p_, [(T(0, "cresce") + 0.1 * k, S[1][0])])
for k, p_ in enumerate(FUROS[:6]): pop(p_, T(0, "cresce") + 0.1 * k, 1.0, 0.25)
for k in range(5): explosao((FR[0] + random.uniform(-10, 10), FR[1] + random.uniform(-8, 8), 1.0), tg - 0.25 + 0.3 * k, r=11, n=12)
shot(t0, th, (V[0] + 14, V[1] - 22, 10), (V[0], V[1], 2), (V[0] + 22, V[1] - 34, 22), (V[0], V[1], 1))
shot(th, tg - 0.3, (V[0] + 10, V[1] - 70, 50), (V[0], V[1] + 10, 0), (V[0] - 10, V[1] - 72, 54), (V[0] - 10, V[1] + 20, 0))
shot(tg - 0.3, tp - 0.1, (FR[0] + 22, FR[1] - 34, 14), (FR[0], FR[1], 6), (FR[0] + 18, FR[1] - 30, 13), (FR[0], FR[1], 7))
shot(tp - 0.1, t1, (-10, -150, 110), (-30, 10, 0), (0, -160, 120), (-30, 10, 0))
for k in range(4): explosao((FR[0] + random.uniform(-14, 10), FR[1] + random.uniform(-10, 10), 1.0), tp + 0.3 * k, r=7, n=10)

# ---------- S1: achar cada doente (van chega; caso confirmado) ----------
t0, t1 = S[1]
ta = T(1, "achar"); te = T(1, "Esse")
rumo(van, 0, -90)
VS = (-60, -6, 1.0); VE = (V[0] - 10, V[1] - 6, 1.0)
van.location = VS; van.keyframe_insert("location", frame=1); van.keyframe_insert("location", frame=f(t0))
rumo(van, t0, -90); andar(van, t0, ta + 0.2, VS, VE)
for ag, a, b in ((AG1, (VE[0] + 1, VE[1] + 2, 0), (PAC.location[0] - 1.8, PAC.location[1] - 1.2, 0)), (AG2, (VE[0] - 1, VE[1] + 2, 0), (PAC.location[0] + 1.6, PAC.location[1] - 2.0, 0))):
    ag.location = a; ag.keyframe_insert("location", frame=1); ag.keyframe_insert("location", frame=f(ta + 0.2)); andar(ag, ta + 0.2, te, a, b)
visivel_janelas(AG1, [(ta + 0.2, S[3][0] + 2.5)]); visivel_janelas(AG2, [(ta + 0.2, S[3][0] + 2.5)])
anel_caso = anel("anelCaso", (0, 0, 0), 1.0, 0.12, AMARELO, seg=24, unico="contato"); filho(PAC, anel_caso); anel_caso.location = (0, 0, 3.0)
anel_caso.rotation_euler = (math.radians(90), 0, 0)
visivel(anel_caso, te, S[3][0]); pop(anel_caso, te, 1.6, 0.4)
shot(t0, ta - 0.1, (V[0] - 30, V[1] - 26, 12), (V[0] - 10, V[1] - 6, 1.5), (V[0] - 22, V[1] - 22, 10), (V[0] - 6, V[1] - 4, 1.5))
shot(ta - 0.1, t1, (V[0] + 8, V[1] - 12, 5), (PAC.location[0], PAC.location[1], 2), (V[0] + 6, V[1] - 9, 4.5), (PAC.location[0], PAC.location[1], 2.2))

# ---------- S2: rastreamento (linhas até os contatos, 21 dias) ----------
t0, t1 = S[2]
ts = T(2, "segue"); tv = T(2, "vinte")
for k, (m_, l_) in enumerate(zip(MARC_C, LIG)):
    tt = ts + 0.35 * k
    visivel_janelas(m_, [(tt, T(6, "impediram") + 0.2 * k)]); pop(m_, tt, 1.0, 0.3)
    visivel_janelas(l_, [(tt, T(6, "impediram") + 0.2 * k)])
DIAS = []
for k in range(21):
    a = 90 - k * 360 / 21
    d_ = caixa(_id("dia"), polar(PAC.location, 6.0, a, 0.25), (0.9, 0.9, 0.3), AMARELO, unico="contato"); DIAS.append(d_)
    visivel(d_, tv + 0.05 * k, S[3][0]); pop(d_, tv + 0.05 * k, 1.0, 0.2)
shot(t0, tv - 0.1, (V[0] + 4, V[1] - 30, 22), (V[0], V[1], 1), (V[0] - 4, V[1] - 26, 24), (V[0], V[1] + 2, 1))
shot(tv - 0.1, t1, (V[0] + 2, V[1] - 9, 16), (PAC.location[0], PAC.location[1], 0), (V[0] + 4, V[1] - 8, 18), (PAC.location[0], PAC.location[1], 0))

# ---------- S3: o cerco (isolamento no centro de tratamento, enterro seguro, anel verde) ----------
t0, t1 = S[3]
ti = T(3, "isola"); ten = T(3, "enterra"); tes = T(3, "Esse")
PAC.keyframe_insert("location", frame=f(ti))
andar(PAC, ti, ti + 2.0, tuple(PAC.location), (CT[0] - 7, CT[1] + 0, 0)); visivel_janelas(PAC, [(0, ti + 2.0), (S[7][0], FIM)])
for e_, (dx, dy), bd, be in EQ:
    a = (ENT[0] - 14 + dx, ENT[1] - 8 + dy, 0); b = (ENT[0] - 2 + dx, ENT[1] + 2 + dy, 0)
    e_.location = a; e_.keyframe_insert("location", frame=1); andar(e_, ten - 0.2, tes, a, b)
    bd.rotation_euler = (math.radians(60), 0, 0); be.rotation_euler = (math.radians(60), 0, 0)
    rumo(e_, 0, -50)
    visivel(e_, ten - 0.3, S[4][0])
cx = vazio("pivCaixa"); filho(cx, caixao); caixao.location = (0, -1.3, 1.6)
andar(cx, ten - 0.2, tes, (ENT[0] - 14, ENT[1] - 8, 0), (ENT[0] - 2, ENT[1] + 2, 0)); visivel(caixao, ten - 0.3, S[4][0])
visivel_janelas(CERCO, [(tes, S[4][0] + 0.01), (S[7][0], FIM)]); pop(CERCO, tes, 1.0, 0.5)
shot(t0, ten - 0.1, (CT[0] - 26, CT[1] - 26, 16), (CT[0] - 4, CT[1], 1.5), (CT[0] - 18, CT[1] - 28, 18), (CT[0] - 2, CT[1], 1.5))
shot(ten - 0.1, tes - 0.1, (ENT[0] - 16, ENT[1] - 16, 6), (ENT[0] - 8, ENT[1] - 4, 1.2), (ENT[0] - 10, ENT[1] - 14, 6), (ENT[0] - 3, ENT[1] + 1, 1.2))
shot(tes - 0.1, t1, (V[0] + 6, V[1] - 62, 52), (V[0] + 8, V[1] + 2, 0), (V[0] + 12, V[1] - 66, 58), (V[0] + 8, V[1] + 4, 0))

# ---------- S4: a peça que falta (pedestais; vacina = "?") ----------
t0, t1 = S[4]
tf = T(4, "falta"); tb = T(4, "Bundibugyo"); tsem = T(4, "sem")
for k, ped in enumerate(PEDS): pop(ped, t0 + 0.1 + 0.3 * k, 1.0, 0.35); visivel(ped, t0 + 0.1 + 0.3 * k, S[5][0])
visivel(frasco, t0, tsem + 0.2); sumir(frasco, tsem - 0.05, 0.3)
visivel(interrog, tsem + 0.1, S[5][0]); pop(interrog, tsem + 0.1, 1.0, 0.4)
piv_q.rotation_euler = (0, 0, 0); piv_q.keyframe_insert("rotation_euler", frame=f(tsem), index=2)
piv_q.rotation_euler = (0, 0, math.radians(360)); piv_q.keyframe_insert("rotation_euler", frame=f(S[5][0]), index=2)
shot(t0, tb - 0.1, (PD[0] - 4, PD[1] - 30, 9), (PD[0] - 1, PD[1], 3), (PD[0] - 2, PD[1] - 26, 8.5), (PD[0] - 1, PD[1], 3))
shot(tb - 0.1, t1, (PD[0] + 8, PD[1] - 17, 9), (PD[0] + 7, PD[1], 3.5), (PD[0] + 9, PD[1] - 14, 8.5), (PD[0] + 9, PD[1], 3.8))

# ---------- S5: a guerra (Bunia, estrada, front a 25 km, deslocados) ----------
t0, t1 = S[5]
tl = T(5, "leste"); tcb = T(5, "combates"); tbu = T(5, "Bunia"); tes5 = T(5, "Esse")
for k, cm in enumerate(CAM_M):
    rumo(cm, 0, 0)
    a = (-68 + (k % 2) * 4, -40 + k * 12, 1.0); b = (-68 + (k % 2) * 4, 60 + k * 9, 1.0)
    cm.location = a; cm.keyframe_insert("location", frame=1); andar(cm, tl - 0.5, tcb + 2.0, a, b)
for k in range(10): explosao((FR[0] + random.uniform(-16, 16), FR[1] + random.uniform(-10, 14), 1.0), tcb + 0.45 * k, r=10, n=10)
for k, d_ in enumerate(DESL):
    x0 = -70 + random.choice((-4.5, 4.5)) + random.uniform(-1, 1)
    a = (x0, 70 - k * 3.5, 0); b = (x0, 70 - k * 3.5 - 40, 0)
    rumo(d_, 0, 180); andar(d_, tbu - 1.0, S[6][0] + 1.0, a, b); visivel(d_, tbu - 1.2, S[6][0] + 1.0)
shot(t0, tl - 0.1, (-40, -80, 30), (-70, -10, 1), (-46, -60, 34), (-70, 10, 1))
shot(tl - 0.1, tcb - 0.1, (-20, 20, 70), (-70, 60, 0), (-24, 40, 64), (-70, 80, 0))
shot(tcb - 0.1, tbu - 0.1, (FR[0] + 28, FR[1] - 40, 18), (FR[0], FR[1], 3), (FR[0] + 22, FR[1] - 34, 16), (FR[0], FR[1] + 2, 3))
shot(tbu - 0.1, tes5 - 0.1, (-40, -10, 90), (-70, -20, 0), (-36, -30, 120), (-70, -10, 0))
shot(tes5 - 0.1, t1, (-56, 36, 10), (-70, 60, 2), (-58, 30, 9), (-70, 56, 2))

# ---------- S6: elo quebrado (barreira, linhas somem, hospital sob fogo cruzado) ----------
t0, t1 = S[6]
tim = T(6, "impediram"); tdo = T(6, "Dois"); tho = T(6, "hospital"); tes6 = T(6, "Esse")
VB0 = (-70, -30, 1.0); VB1 = (-70, 14, 1.0)
van.keyframe_insert("location", frame=f(t0 - 0.05)); rumo(van, t0 - 0.05, -90)
van.location = VB0; van.keyframe_insert("location", frame=f(t0)); rumo(van, t0, 0)
andar(van, t0, tim + 0.4, VB0, VB1); van.keyframe_insert("location", frame=f(S[7][0]))
for k in range(3): explosao((-70 + random.uniform(-6, 6), 26 + random.uniform(-2, 4), 1.0), tim + 0.2 + 0.5 * k, r=5, n=9)
visivel(barreira, t0 - 0.05)
for k in range(8): explosao((HOSP[0] + random.choice((-14, 14)) + random.uniform(-4, 4), HOSP[1] + random.uniform(-10, 10), 1.0), tdo + 0.5 * k, r=5, n=8)
for pr in PRESOS: visivel(pr, tdo - 0.1, S[7][0])
shot(t0, tim - 0.1, (-56, -10, 10), (-70, 10, 2), (-60, -14, 9), (-70, 12, 2))
shot(tim - 0.1, tdo - 0.1, (-62, 4, 8), (-70, 20, 1.5), (-64, 6, 8), (-70, 20, 1.5))
shot(tdo - 0.1, tes6 - 0.1, (HOSP[0] + 18, HOSP[1] - 30, 12), (HOSP[0], HOSP[1], 3), (HOSP[0] + 10, HOSP[1] - 26, 10), (HOSP[0], HOSP[1] - 2, 3))
shot(tes6 - 0.1, t1, (V[0] + 6, V[1] - 22, 12), (V[0], V[1], 2), (V[0] + 2, V[1] - 20, 13), (V[0], V[1], 2))

# ---------- S7: cerco furado (casos fora do anel) ----------
t0, t1 = S[7]
to = T(7, "oitenta"); tsu = T(7, "surgiram"); tc7 = T(7, "cerco")
for k, p_ in enumerate(FUROS):
    visivel_janelas(p_, [(T(0, "cresce") + 0.1 * k, S[1][0])] if k < 6 else [])
for k, p_ in enumerate(FUROS):
    tt = tsu - 0.3 + 0.18 * k
    for o in todos(p_):
        o.hide_render = False; o.keyframe_insert("hide_render", frame=f(tt))
    pop(p_, tt, 1.0, 0.3)
cm_ = mat(VERDE, "cerco")
cor_key(cm_, 0, VERDE); cor_key(cm_, tc7 - 0.05, VERDE); cor_key(cm_, tc7 + 0.15, VERMELHO); cor_key(cm_, FIM, VERMELHO)
shot(t0, tsu - 0.4, (V[0] + 6, V[1] - 56, 46), (V[0], V[1], 0), (V[0] + 4, V[1] - 70, 62), (V[0], V[1] + 4, 0))
shot(tsu - 0.4, t1, (V[0] - 10, V[1] - 72, 60), (V[0], V[1] + 4, 0), (V[0] - 14, V[1] - 80, 70), (V[0], V[1] + 6, 0))

# ---------- S8-S9: parabéns (visão geral) + CTA + like ----------
t0, _ = S[8]
shot(t0, S[9][0], (-20, -170, 120), (-30, 0, 0), (0, -180, 130), (-25, 5, 0))
shot(S[9][0], FIM, (CT[0] - 10, CT[1] - 30, 14), (CT[0], CT[1], 2), (CT[0] + 6, CT[1] - 34, 18), (CT[0], CT[1], 2))

for ob in (cam, alvo, piv_q):
    for fc in ob.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

if os.environ.get("REALISTA"):
    HD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "hdri")
    bg, sol = modo_realista(os.path.join(HD, "ceu_parcialmente_nublado_2k.hdr"), samples=int(os.environ.get("AMOSTRAS", "4")), foco=alvo)
    def emissivo(chave, cor, forca):
        for m in bpy.data.materials:
            if any(v == m and k[1] == chave for k, v in _mats.items()):
                b = m.node_tree.nodes.get("Principled BSDF"); b.inputs["Emission Color"].default_value = _lin(cor); b.inputs["Emission Strength"].default_value = forca
    emissivo("caso", VERMELHO, 3.0); emissivo("fogo", (1.0, 0.45, 0.08, 1), 6.0); emissivo("contato", AMARELO, 1.5); emissivo("interrog", AMARELO, 1.4)
    # o anel do cerco muda de verde para vermelho: anima a cor base e a emissão
    for m in bpy.data.materials:
        if any(v == m and k[1] == "cerco" for k, v in _mats.items()):
            b = m.node_tree.nodes.get("Principled BSDF")
            for prop in ("Base Color", "Emission Color"):
                for tt, cc in ((0, VERDE), (T(7, "cerco") - 0.05, VERDE), (T(7, "cerco") + 0.15, VERMELHO)):
                    b.inputs[prop].default_value = _lin(cc); b.inputs[prop].keyframe_insert("default_value", frame=f(tt))
            b.inputs["Emission Strength"].default_value = 1.2
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
