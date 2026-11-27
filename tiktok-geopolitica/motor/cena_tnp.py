"""Vídeo TNP — "Por que Israel não está no tratado nuclear?" (resposta ao comentário). Uso:
REALISTA=1 blender -b --factory-startup -P cena_tnp.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
import bpy, bmesh, sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
from lowpoly import *
from lowpoly import _id, _lin, _new_obj, _viga, _mats

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
random.seed(2611)

CONC = (0.80, 0.79, 0.76, 1); METAL = (0.74, 0.76, 0.78, 1)
VERDE = (0.25, 1.0, 0.35, 1); VERMELHO = (1.0, 0.15, 0.10, 1); AMBAR = (1.0, 0.72, 0.25, 1)
UF6 = (0.86, 0.80, 0.30, 1); AZUL_AG = (0.15, 0.40, 0.80, 1); BRANCO = C["branco"]; YELLOW = (0.95, 0.80, 0.15, 1)
CORES_PAIS = [(0.20, 0.45, 0.85, 1), (0.95, 0.85, 0.20, 1), (0.25, 0.70, 0.35, 1), (0.95, 0.55, 0.15, 1), (0.60, 0.30, 0.75, 1),
              (0.15, 0.70, 0.75, 1), (0.95, 0.95, 0.95, 1), (0.85, 0.35, 0.55, 1)]
def andar(ob, t0, t1, a, b):
    ob.location = a; ob.keyframe_insert("location", frame=f(t0)); ob.location = b; ob.keyframe_insert("location", frame=f(t1))
def rumo(ob, t, graus):
    ob.rotation_euler = (0, 0, math.radians(graus)); ob.keyframe_insert("rotation_euler", frame=f(t), index=2)
def polar(r, ang, z=0.0): return (r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang)), z)

# =====================================================================
# TERRENO
# =====================================================================
caixa("chao", (0, 0, -0.5), (1400, 1400, 1.0), C["grama"])
caixa("estradaAg", (-20, 70, 0.03), (6, 60, 0.06), C["rua"])
caixa("estradaO", (-75, 0, 0.03), (70, 5, 0.06), C["rua"])
caixa("estradaSO", (-100, -40, 0.03), (5, 60, 0.06), C["rua"])
for _ in range(30):
    m = esfera("morro", (random.uniform(-450, 450), random.uniform(170, 380), -4), random.uniform(18, 42), random.choice([C["morro"], C["grama2"]]), sub=2)
    m.scale = (1.7, 1.0, 0.5)
for _ in range(170):
    x = random.uniform(-200, 200); y = random.uniform(-140, 150)
    if math.hypot(x, y) < 48 or math.hypot(x - 90, y + 16) < 24 or (-140 < x < -80 and -10 < y < 40) or (-130 < x < -70 and -100 < y < -45): continue
    if (-45 < x < 10 and 75 < y < 125) or abs(x + 20) < 5 and y > 40 or abs(y) < 5 and x < -40: continue
    if 45 < x < 75 and -45 < y < 45: continue
    arvore((x, y), random.uniform(0.9, 1.6))

# =====================================================================
# 1) PRAÇA DO TRATADO (0,0): cerca redonda, mastros dos países, púlpito com o tratado
# =====================================================================
R_PRACA = 40
cilindro("praca", (0, 0, 0.1), R_PRACA, 0.2, (0.82, 0.80, 0.75, 1), seg=64)
anel("bordaPraca", (0, 0, 0.25), R_PRACA, 0.25, (0.60, 0.58, 0.55, 1), seg=64)
# cerca: postes + 2 trilhos (anéis), com um portão aberto a leste (ângulo 0)
for k in range(48):
    a = k * 7.5
    if abs(((a + 180) % 360) - 180) < 6: continue
    cilindro(_id("poste"), polar(R_PRACA + 1.5, a, 1.1), 0.12, 2.2, (0.45, 0.47, 0.50, 1), seg=6)
for z in (1.0, 2.0): anel(_id("trilho"), (0, 0, z), R_PRACA + 1.5, 0.06, (0.55, 0.57, 0.60, 1), seg=96)
# mastros dos países-membros (genéricos, sem bandeira real)
membros = []
random.seed(31)
for r, n in ((20, 12), (27, 16), (34, 19)):
    for k in range(n):
        a = k * 360 / n + random.uniform(-3, 3) + (r * 1.3)
        if abs(((a + 180) % 360) - 180) < 9 and r > 30: continue
        b_ = bandeira(_id("membro"), polar(r, a), random.choice(CORES_PAIS), h=7.5, larg=3.4, alt=2.1, fase=random.uniform(0, 6))
        b_.rotation_euler = (0, 0, math.radians(a + 90 + random.uniform(-25, 25)))
        membros.append(b_)
# 5 potências reconhecidas: pedestais altos com míssil em pé, perto do centro
POT = []
for k in range(5):
    a = 200 + k * 35
    loc = polar(10.5, a)
    ped = cilindro(_id("pedestal"), (loc[0], loc[1], 1.0), 1.6, 2.0, (0.30, 0.32, 0.36, 1), seg=12)
    ms = missil(_id("misPot"), cor=(0.88, 0.89, 0.90, 1), escala=0.9); ms.rotation_euler = (math.radians(90), 0, 0)
    ms.location = (loc[0], loc[1], 2.0)
    bd = bandeira(_id("bandPot"), (loc[0] + 1.9, loc[1], 0), CORES_PAIS[k], h=10.0, larg=4.0, alt=2.5, fase=k)
    bd.rotation_euler = (0, 0, math.radians(a + 90))
    POT.append((ped, ms, bd))
anel_verde = cilindro("anelVerde", (0, 0, 0.23), 37, 0.05, (0.35, 0.72, 0.38, 1), seg=64, unico="anelVerde")
pulp, selo_ouro = documento("tratado", (0, 0))

# =====================================================================
# 2) FORA DA CERCA (leste): 4 mastros vermelhos + complexo "Israel" (cúpula) mais longe
# =====================================================================
FORA = []
for k, a in enumerate((34, 12, -10, -32)):
    loc = polar(58, a)
    caixa(_id("lajeFora"), (loc[0], loc[1], 0.1), (7, 7, 0.2), (0.70, 0.68, 0.64, 1))
    b_ = bandeira(_id("fora"), loc, VERMELHO, h=11.0, larg=4.6, alt=2.8, fase=k, unico="foraVerm")
    b_.rotation_euler = (0, 0, math.radians(a + 90)); FORA.append((b_, loc))
ISR = polar(88, -10)
caixa("lajeIsr", (ISR[0], ISR[1], 0.1), (34, 30, 0.2), (0.86, 0.80, 0.66, 1))
cupula = esfera("cupula", (ISR[0], ISR[1], 0), 7.5, (0.62, 0.64, 0.66, 1), sub=3)
for pl in cupula.data.polygons: pl.use_smooth = True
cilindro("baseCup", (ISR[0], ISR[1], 1.2), 7.6, 2.4, (0.84, 0.82, 0.76, 1), seg=32)
for dx, dy, w, d, h in ((-11, 7, 6, 5, 4), (11, 6, 7, 6, 5), (-10, -8, 5, 6, 3.5), (10, -9, 8, 4, 4)):
    predio((ISR[0] + dx, ISR[1] + dy), w, d, h, (0.88, 0.84, 0.74, 1))
cilindro("chamineIsr", (ISR[0] + 13, ISR[1] - 1, 6), 0.9, 12, CONC, seg=10)
for k in range(36):
    a = k * 10
    cilindro(_id("cercaIsr"), (ISR[0] + 16 * math.cos(math.radians(a)), ISR[1] + 14 * math.sin(math.radians(a)), 1.2), 0.1, 2.4, (0.40, 0.42, 0.45, 1), seg=5)
cd = bpy.data.curves.new("interrog", "FONT"); cd.body = "?"; cd.extrude = 0.6; cd.size = 12; cd.align_x = "CENTER"; cd.bevel_depth = 0.08
interrog = bpy.data.objects.new("interrog", cd); scn.collection.objects.link(interrog)
interrog.data.materials.append(mat(YELLOW, "interrog")); interrog.rotation_euler = (math.radians(90), 0, math.radians(80))
piv_q = vazio("pivQ", (ISR[0], ISR[1], 13)); filho(piv_q, interrog); interrog.location = (0, 0, 0)
# Coreia do Norte: mastro dentro da praça que sai pelo portão
NK_IN = polar(33, 50); NK_OUT = polar(60, 58)
nk = bandeira("nk", (0, 0, 0), (0.55, 0.15, 0.15, 1), h=11.0, larg=4.6, alt=2.8, unico="nk")

# =====================================================================
# 3) AGÊNCIA (o vigia) + USINA com pátio de cilindros (salvaguarda)
# =====================================================================
AG = (-20, 100)
for k, (dx, dy, h) in enumerate(((-9, 0, 26), (0, 5, 32), (9, 0, 22))):
    t_ = cilindro(_id("torreAg"), (AG[0] + dx, AG[1] + dy, h / 2), 4.2, h, (0.92, 0.93, 0.95, 1), seg=20)
    for z in range(3, int(h) - 1, 3):
        v_ = cilindro(_id("tAgVid"), (0, 0, 0), 4.26, 1.3, (0.22, 0.40, 0.60, 1), seg=20); filho(t_, v_); v_.location = (0, 0, z - h / 2)
caixa("pracaAg", (AG[0], AG[1] - 16, 0.1), (30, 10, 0.2), (0.80, 0.78, 0.74, 1))
UX, UY = -115, 18
reat, torres_topo = reator("reator"); reat.location = (UX, UY, 0)
PATIO = (UX + 6, UY - 16)
caixa("patioCil", (PATIO[0], PATIO[1], 0.1), (24, 9, 0.2), (0.66, 0.65, 0.62, 1))
cils, selos = [], []
for k in range(6):
    c = cilindro_uf6(_id("uf6"), (PATIO[0] - 9 + k * 3.6, PATIO[1], 1.0)); c.rotation_euler = (math.radians(90), 0, 0); cils.append(c)
    s_ = caixa(_id("selo"), (c.location[0], c.location[1] - 0.1, c.location[2] + 0.82), (0.35, 0.35, 0.6), AZUL_AG, unico="selo"); selos.append(s_)

# =====================================================================
# 4) FÁBRICA DE CENTRÍFUGAS (Irã, genérica) — salão aberto com câmeras e selos
# =====================================================================
FX, FY = -100, -72
caixa("lajeFab", (FX, FY, 0.15), (40, 24, 0.3), (0.70, 0.70, 0.68, 1))
caixa("paredeFundo", (FX, FY + 12, 4.5), (40, 0.8, 9), CONC)
for sx in (-1, 1): caixa("paredeLado", (FX + sx * 20, FY, 2.0), (0.8, 24, 4), CONC)
caixa("muretaFrente", (FX, FY - 12, 1.0), (40, 0.8, 2), CONC)
tubos = []
for ly in (-6, -1.5, 3, 7.5):
    for k in range(9):
        b, t = centrifuga(_id("cf"), (FX - 16 + k * 4, FY + ly), h=5.2, r=0.55); tubos.append(t)
for t_ in tubos: girar(t_, 0.0, rps=random.uniform(1.2, 1.8))
cams = []
for k, (x, y) in enumerate(((FX - 20.5, FY - 12.5), (FX + 20.5, FY - 12.5), (FX, FY - 12.5))):
    poste = cilindro(_id("pcam"), (x, y, 2.8), 0.12, 5.6, (0.30, 0.32, 0.36, 1), seg=6)
    cx_ = caixa(_id("cam"), (0, 0, 0), (0.7, 1.3, 0.7), BRANCO); filho(poste, cx_); cx_.location = (0, 0.6, 2.9); cx_.rotation_euler = (math.radians(20), 0, 0)
    led = esfera(_id("led"), (0, 0, 0), 0.16, VERMELHO, sub=1, unico="led"); filho(cx_, led); led.location = (0, 0.68, 0)
    cams.append(poste)
selos_f = []
for k in range(9):
    s_ = caixa(_id("seloF"), (FX - 16 + k * 4, FY - 8.6, 0.9), (0.4, 0.4, 0.7), AZUL_AG, unico="selo"); selos_f.append(s_)

# =====================================================================
# VAN E INSPETORES
# =====================================================================
van, _ = caminhao("vanInspetores", (0, 0, 1.0), cor=BRANCO, tubos=False)
filho(van, caixa("bauVan", (0, -1.0, 1.25), (2.4, 4.6, 1.9), BRANCO))
filho(van, caixa("faixaVan", (0, -1.0, 1.25), (2.45, 4.62, 0.35), AZUL_AG))
ins1, bd1, be1 = boneco("insp1", (0, 0, 0), camisa=AZUL_AG, capacete=False)
ins2, bd2, be2 = boneco("insp2", (0, 0, 0), camisa=AZUL_AG, capacete=False)
for ins in (ins1, ins2): filho(ins, esfera(_id("capBranco"), (0, 0, 2.12), 0.38, BRANCO, sub=1))

cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 24; cam_d.clip_end = 6000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def shot(t0, t1, loc0, tgt0, loc1=None, tgt1=None):
    for fr, loc, tgt in ((f(t0), loc0, tgt0), (f(t1) - 1, loc1 or loc0, tgt1 or tgt0)):
        for ob, v in ((cam, loc), (alvo, tgt)):
            ob.location = v; ob.keyframe_insert("location", frame=fr)

# ---------- S0: gancho (cúpula com "?", praça enchendo de mastros, Israel fora) ----------
t0, t1 = S[0]
tc_ = T(0, "Cento") - 0.1; ti_ = T(0, "Israel", 1) - 0.1; tp_ = T(0, "Peça") - 0.1
pop(interrog, 0.0, 1.0, 0.01)
piv_q.rotation_euler = (0, 0, 0); piv_q.keyframe_insert("rotation_euler", frame=1, index=2)
piv_q.rotation_euler = (0, 0, math.radians(360 * 3)); piv_q.keyframe_insert("rotation_euler", frame=f(S[6][0]), index=2)
for fc in piv_q.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
visivel_janelas(interrog, [(0.0, tc_), (T(5, "silêncio"), S[6][0])])
shot(t0, tc_, (ISR[0] - 30, ISR[1] - 30, 16), (ISR[0], ISR[1], 9), (ISR[0] - 24, ISR[1] - 24, 14), (ISR[0], ISR[1], 9))
order = sorted(membros, key=lambda o: math.hypot(o.location[0], o.location[1]))
for k, o in enumerate(order): pop(o, tc_ + 0.05 + 2.6 * k / len(order), 1.0, 0.25)
shot(tc_, ti_, (0, -70, 60), (0, 0, 0), (0, -62, 52), (0, 2, 0))
for k, (b_, loc) in enumerate(FORA): pop(b_, ti_ + 0.05 if k == 2 else T(4, ("Índia", "Paquistão", "Israel", "Sudão")[k]), 1.0, 0.35)
shot(ti_, tp_, polar(30, -4, 5), polar(58, -10, 6), polar(33, -6, 5.5), polar(58, -10, 6.5))
shot(tp_, t1, (-30, -95, 70), (20, 0, 0), (-20, -90, 80), (25, 0, 0))

# ---------- S1: o acordo (púlpito com o tratado; selo dourado na assinatura) ----------
t0, t1 = S[1]
ta = T(1, "acordo"); tas = T(1, "Assinado"); te = T(1, "Esse")
pop(pulp, ta - 0.1, 1.0, 0.4)
visivel(selo_ouro, tas + 0.6); pop(selo_ouro, tas + 0.6, 1.0, 0.4)
shot(t0, ta - 0.15, (-26, -32, 22), (0, 0, 2), (-22, -28, 18), (0, 0, 2))
shot(ta - 0.15, te - 0.1, (0, -9, 8), (0, 0, 2.6), (2, -7.5, 6.5), (0.5, -0.5, 2.7))
shot(te - 0.1, t1, (8, -30, 24), (0, 0, 3), (14, -36, 30), (0, 0, 3))

# ---------- S2: 5 potências reconhecidas; os outros prometem ----------
t0, t1 = S[2]
tk = T(2, "Reconhece")
for k, (ped, ms, bd) in enumerate(POT):
    tt = T(2, ("Estados", "Rússia", "China", "Reino", "França")[k]) - 0.05
    for o in (ped, ms, bd): pop(o, tt, 1.0, 0.35)
to = T(2, "outros")
pop(anel_verde, to, 1.0, 0.5); visivel(anel_verde, to - 0.05)
shot(t0, tk - 0.1, (30, -40, 30), (0, 0, 0), (26, -36, 26), (0, 0, 0))
shot(tk - 0.1, to - 0.1, (-6, -30, 10), (0, -8, 3.5), (6, -28, 9), (0, -8, 3.5))
shot(to - 0.1, t1, (0, -58, 34), (0, 0, 0), (0, -50, 44), (0, 4, 0))

# ---------- S3: salvaguarda (van da agência até a usina; selos nos cilindros) ----------
t0, t1 = S[3]
tin = T(3, "Inspetores"); tco = T(3, "contam"); tes = T(3, "Essa")
rumo(van, 0, 90)
VSTART = (AG[0], AG[1] - 25, 1.0); VMID = (AG[0], 0, 1.0); VEND = (PATIO[0] + 3, PATIO[1] - 7, 1.0)
van.location = VSTART; van.keyframe_insert("location", frame=1); van.keyframe_insert("location", frame=f(t0))
rumo(van, t0, 180)
andar(van, t0, t0 + 2.0, VSTART, (AG[0], 3, 1.0)); rumo(van, t0 + 2.0, 180); rumo(van, t0 + 2.3, 90)
andar(van, t0 + 2.0, tin + 0.6, (AG[0], 3, 1.0), (PATIO[0] + 3, 3, 1.0)); rumo(van, tin + 0.6, 90); rumo(van, tin + 0.9, 180)
andar(van, tin + 0.6, tco - 0.4, (PATIO[0] + 3, 3, 1.0), VEND)
for ins, a, b in ((ins1, (VEND[0] - 2, VEND[1] - 1, 0), (PATIO[0] - 4, PATIO[1] - 3, 0)), (ins2, (VEND[0] + 2, VEND[1] - 1, 0), (PATIO[0] + 3, PATIO[1] - 3, 0))):
    andar(ins, tco - 0.4, tes, a, b)
for k, s_ in enumerate(selos): visivel(s_, tco + 0.15 * k); pop(s_, tco + 0.15 * k, 1.0, 0.3)
shot(t0, tin - 0.1, (AG[0] + 22, AG[1] - 60, 26), (AG[0], AG[1] - 10, 8), (AG[0] + 18, 20, 22), (AG[0] - 10, 5, 1))
shot(tin - 0.1, t1, (PATIO[0] + 16, PATIO[1] - 22, 9), (PATIO[0], PATIO[1], 1.5), (PATIO[0] + 10, PATIO[1] - 18, 8), (PATIO[0] - 2, PATIO[1], 1.5))

# ---------- S4: o tratado é voluntário (4 mastros fora; Coreia do Norte sai) ----------
t0, t1 = S[4]
tnk = T(4, "Coreia"); tsa = T(4, "saída")
nk.location = NK_IN; nk.keyframe_insert("location", frame=1); nk.keyframe_insert("location", frame=f(tnk))
def nk_pos(u):
    if u < 0.5: return polar(36, 50 * (1 - 2 * u))
    v = 2 * u - 1; return polar(36 + 26 * v, 52 * v * v)
caminho(nk, tnk, tsa + 0.8, nk_pos, orientar=False, passo=2)
nk.rotation_mode = "XYZ"
shot(t0, T(4, "Índia") - 0.1, (-10, 0, 9), (R_PRACA, 0, 3), (0, 0, 10), (R_PRACA, 0, 3))
shot(T(4, "Índia") - 0.1, tnk - 0.1, (-22, 0, 46), (58, 0, 2), (-12, 0, 42), (58, 0, 2))
shot(tnk - 0.1, T(4, "Essa") - 0.1, (14, -18, 26), (32, 30, 0), (18, -14, 30), (38, 30, 0))
shot(T(4, "Essa") - 0.1, t1, (-10, -90, 70), (30, 0, 0), (0, -95, 74), (34, 0, 0))

# ---------- S5: Israel — ambiguidade (cúpula e "?") ----------
t0, t1 = S[5]
tsil = T(5, "silêncio")
interrog.scale = (0.001,) * 3; interrog.keyframe_insert("scale", frame=f(tsil) - 1)
interrog.scale = (1.15,) * 3; interrog.keyframe_insert("scale", frame=f(tsil + 0.25)); interrog.scale = (1,) * 3; interrog.keyframe_insert("scale", frame=f(tsil + 0.35))
interrog.scale = (1,) * 3; interrog.keyframe_insert("scale", frame=f(S[6][0] - 0.2)); interrog.scale = (0.001,) * 3; interrog.keyframe_insert("scale", frame=f(S[6][0]))
shot(t0, tsil - 0.1, (ISR[0] - 40, ISR[1] - 34, 12), (ISR[0], ISR[1], 5), (ISR[0] - 32, ISR[1] - 30, 14), (ISR[0], ISR[1], 6))
shot(tsil - 0.1, T(5, "instituto") - 0.1, (ISR[0] - 22, ISR[1] - 20, 16), (ISR[0], ISR[1], 10), (ISR[0] - 16, ISR[1] - 26, 18), (ISR[0], ISR[1], 10))
shot(T(5, "instituto") - 0.1, t1, (ISR[0] + 10, ISR[1] - 44, 40), (ISR[0], ISR[1], 4), (ISR[0] + 26, ISR[1] - 34, 44), (ISR[0], ISR[1], 4))

# ---------- S6: Irã assinou — inspetores na fábrica de centrífugas ----------
t0, t1 = S[6]
tre = T(6, "recebe"); tte = T(6, "Teerã")
FV = (FX + 22, FY - 20, 1.0)
van.location = FV; van.keyframe_insert("location", frame=f(t0)); rumo(van, t0, 90)
van.keyframe_insert("location", frame=f(t1))
for ins, a, b in ((ins1, (FX + 18, FY - 16, 0), (FX + 6, FY - 9.6, 0)), (ins2, (FX + 20, FY - 16, 0), (FX - 4, FY - 9.6, 0))):
    ins.location = a; ins.keyframe_insert("location", frame=f(t0)); andar(ins, tre - 0.2, tre + 2.4, a, b)
for k, c in enumerate(cams): pop(c, tre + 0.3 * k, 1.0, 0.35)
for k, s_ in enumerate(selos_f): visivel(s_, tre + 0.1 * k); pop(s_, tre + 0.1 * k, 1.0, 0.3)
shot(t0, tre - 0.1, (FX + 34, FY - 38, 22), (FX, FY, 3), (FX + 28, FY - 34, 20), (FX, FY, 3))
shot(tre - 0.1, tte - 0.1, (FX + 12, FY - 24, 6), (FX, FY - 6, 3), (FX + 6, FY - 22, 6.5), (FX - 3, FY - 6, 3))
shot(tte - 0.1, t1, (FX - 10, FY - 30, 18), (FX, FY + 2, 3), (FX - 18, FY - 36, 24), (FX, FY + 2, 3))

for ins in (ins1, ins2): visivel_janelas(ins, [(T(3, "contam") - 0.4, S[4][0]), (S[6][0], S[7][0])])

# ---------- S7-S8: parabéns (visão geral) + CTA + like ----------
t0, _ = S[7]
shot(t0, S[8][0], (-30, -95, 60), (15, 0, 0), (-10, -100, 70), (20, 0, 0))
shot(S[8][0], FIM, (24, -34, 16), (0, 0, 3), (34, -24, 22), (0, 0, 3))

for ob in (cam, alvo):
    for fc in ob.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

if os.environ.get("REALISTA"):
    HD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "hdri")
    bg, sol = modo_realista(os.path.join(HD, "ceu_parcialmente_nublado_2k.hdr"), samples=int(os.environ.get("AMOSTRAS", "4")), foco=alvo)
    def emissivo(chave, cor, forca):
        for m in bpy.data.materials:
            if any(v == m and k[1] == chave for k, v in _mats.items()):
                b = m.node_tree.nodes.get("Principled BSDF"); b.inputs["Emission Color"].default_value = _lin(cor); b.inputs["Emission Strength"].default_value = forca
    emissivo("led", VERMELHO, 6.0); emissivo("selo", AZUL_AG, 0.8); emissivo("interrog", YELLOW, 1.4)
    emissivo("selo_ouro", (0.95, 0.75, 0.2, 1), 1.0); emissivo("anelVerde", (0.3, 0.8, 0.35, 1), 0.25); emissivo("foraVerm", VERMELHO, 0.5)
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
