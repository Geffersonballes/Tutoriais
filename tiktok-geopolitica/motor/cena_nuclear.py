"""Vídeo 05 — 'Como se vigia um programa nuclear' (inspetores da AIEA). Uso:
REALISTA=1 blender -b --factory-startup -P cena_nuclear.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
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
random.seed(2511)
scn.world.color = (0.30, 0.60, 0.95)

CONC = (0.80, 0.79, 0.76, 1); METAL = (0.74, 0.76, 0.78, 1); OCRE = (0.72, 0.52, 0.30, 1)
VERDE = (0.25, 1.0, 0.35, 1); VERMELHO = (1.0, 0.15, 0.10, 1); AMBAR = (1.0, 0.72, 0.25, 1)
CIANO = (0.30, 0.85, 1.0, 1); UF6 = (0.86, 0.80, 0.30, 1)
AZUL_AG = (0.15, 0.40, 0.80, 1); BRANCO = C["branco"]; YELLOW = (0.95, 0.80, 0.15, 1)
PAREDES = [(0.93, 0.85, 0.72, 1), (0.82, 0.87, 0.92, 1), (0.92, 0.76, 0.70, 1), (0.80, 0.85, 0.72, 1), (0.95, 0.93, 0.86, 1)]

def fumaca(loc, t0, t1, r=0.9, cada=0.35, sobe=12.0, vida=2.6, cor=(0.42, 0.41, 0.41, 1)):
    t = t0
    while t < t1:
        o = esfera(_id("fz"), loc, r * random.uniform(0.7, 1.2), cor, sub=2)
        for pl in o.data.polygons: pl.use_smooth = True
        visivel(o, t, t + vida)
        o.location = loc; o.keyframe_insert("location", frame=f(t))
        o.location = (loc[0] + random.uniform(-1.5, 1.5) + sobe * 0.2, loc[1] + random.uniform(-1, 1), loc[2] + sobe); o.keyframe_insert("location", frame=f(t + vida))
        o.scale = (0.4,) * 3; o.keyframe_insert("scale", frame=f(t))
        o.scale = (1.6,) * 3; o.keyframe_insert("scale", frame=f(t + vida * 0.7))
        o.scale = (0.05,) * 3; o.keyframe_insert("scale", frame=f(t + vida))
        t += cada

def ataque(alvo_xyz, t_imp, origem, dur=1.5, r=9):
    m = missil(_id("ms"), escala=0.8)
    meio = ((origem[0] + alvo_xyz[0]) / 2, (origem[1] + alvo_xyz[1]) / 2, origem[2] * 0.9)
    visivel(m, max(0.01, t_imp - dur), t_imp); caminho(m, max(0.01, t_imp - dur), t_imp, lambda u: bez(origem, meio, alvo_xyz, u), passo=1)
    explosao(alvo_xyz, t_imp, r=r, n=22)
    fb = esfera(_id("fb"), alvo_xyz, 1.0, C["laranja"], sub=2); visivel(fb, t_imp, t_imp + 0.9)
    fb.scale = (0.3,) * 3; fb.keyframe_insert("scale", frame=f(t_imp)); fb.scale = (r * 0.7,) * 3; fb.keyframe_insert("scale", frame=f(t_imp + 0.35))
    fb.scale = (0.05,) * 3; fb.keyframe_insert("scale", frame=f(t_imp + 0.9))

def xis(loc, R, t0, t1, rot=0.0):
    p = vazio(_id("xis"), loc)
    for a in (45, -45):
        b = caixa(_id("xbar"), (0, 0, 0), (R * 2.4, R * 0.28, R * 0.28), VERMELHO, unico="xis"); b.rotation_euler = (0, math.radians(a), 0); filho(p, b)
    p.rotation_euler = (0, 0, rot); visivel(p, t0, t1); pop(p, t0); return p

def pulsos(pts, janelas, cor, chave, cada=0.6, vel=30.0, r=0.45):
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

# =====================================================================
# TERRENO
# =====================================================================
caixa("chao", (0, 0, -0.5), (1400, 1400, 1.0), C["grama"])
caixa("estradaS", (-80, -90, 0.03), (6, 110, 0.06), C["rua"])          # estrada que chega no portão
caixa("estradaL", (-30, -40, 0.03), (220, 5, 0.06), C["rua"])           # liga mina, fábrica, usina e cidade
for _ in range(30):
    m = esfera("morro", (random.uniform(-450, 450), random.uniform(160, 380), -4), random.uniform(18, 42), random.choice([C["morro"], C["grama2"]]), sub=2)
    m.scale = (1.7, 1.0, 0.5)
for _ in range(190):
    x = random.uniform(-260, 260); y = random.uniform(-150, 150)
    if (-215 < x < -125 and -40 < y < 40) or (-110 < x < -40 and -50 < y < 25) or (-25 < x < 95 and -30 < y < 50): continue
    if (-20 < x < 30 and 70 < y < 130) or (120 < x < 210 and 10 < y < 80) or (-160 < x < -100 and 40 < y < 90): continue
    if abs(y + 40) < 5 or abs(x + 80) < 5: continue
    arvore((x, y), random.uniform(0.9, 1.6))

# =====================================================================
# 1) MINA DE URÂNIO (x ≈ -170)
# =====================================================================
MINA = (-170, 0)
mina = vazio("mina", (MINA[0], MINA[1], 0))
pec = []
for k, (r, z) in enumerate(((26, 0.0), (21, -0.8), (16, -1.6), (11, -2.4))):   # cava em degraus (anéis que descem)
    pec.append(cilindro(_id("degrau"), (0, 0, z + 0.4), r, 1.0, tuple(c * (1 - 0.07 * k) for c in OCRE[:3]) + (1,), seg=28))
pec.append(cilindro("fundoMina", (0, 0, -2.6), 8, 0.6, (0.55, 0.40, 0.24, 1), seg=24))
for _ in range(14):
    a = random.uniform(0, 6.28); rr = random.uniform(27, 34)
    pec.append(esfera(_id("pedra"), (math.cos(a) * rr, math.sin(a) * rr, 0.6), random.uniform(1.2, 2.6), (0.66, 0.58, 0.42, 1), sub=1))
filho(mina, *pec)
for k in range(6):   # tambores de "yellowcake"
    b = barril(_id("ycake"), 1.0, YELLOW); b.location = (MINA[0] + 30 + (k % 3) * 1.6, MINA[1] - 14 + (k // 3) * 1.6, 0)
cam1, _ = caminhao("caminhaoMina", (MINA[0] + 16, MINA[1] - 22, 1.0), cor=(0.95, 0.70, 0.10, 1), tubos=False)
caixa("cacamba", (MINA[0] + 16, MINA[1] - 23.2, 2.3), (2.6, 4.2, 1.8), (0.95, 0.70, 0.10, 1))
# vitrine de 100 bolinhas: 99 cinzas (U-238) e 1 verde (U-235)
GRADE = (MINA[0] + 40, MINA[1] + 6)
base_g = caixa("baseGrade", (GRADE[0], GRADE[1], 0.3), (15, 15, 0.6), (0.30, 0.32, 0.36, 1))
bolas = []
for i in range(10):
    for j in range(10):
        verde = (i, j) == (6, 3)
        o = esfera(_id("u"), (GRADE[0] - 6.3 + i * 1.4, GRADE[1] - 6.3 + j * 1.4, 1.2), 0.55, VERDE if verde else (0.48, 0.50, 0.52, 1), sub=2, unico="u235" if verde else None)
        for pl in o.data.polygons: pl.use_smooth = True
        bolas.append((o, verde))

# =====================================================================
# 2) FÁBRICA DE ENRIQUECIMENTO (x ≈ -80) — salão aberto em corte
# =====================================================================
FX, FY = -80, 0
caixa("lajeFab", (FX, FY, 0.15), (44, 26, 0.3), (0.70, 0.70, 0.68, 1))
caixa("paredeFundo", (FX, FY + 13, 4.5), (44, 0.8, 9), CONC)
for sx in (-1, 1): caixa("paredeLado", (FX + sx * 22, FY, 2.0), (0.8, 26, 4), CONC)
caixa("muretaFrente", (FX, FY - 13, 1.0), (44, 0.8, 2), CONC)
caixa("vigaTeto1", (FX, FY + 4, 9.2), (44, 0.6, 0.6), (0.40, 0.44, 0.50, 1))
caixa("vigaTeto2", (FX, FY - 4, 9.2), (44, 0.6, 0.6), (0.40, 0.44, 0.50, 1))
for sx in (-21.6, 21.6):
    for sy in (-4, 4): caixa("pilar", (FX + sx, FY + sy, 4.6), (0.6, 0.6, 9.2), (0.40, 0.44, 0.50, 1))
LINHAS_Y = [-7.5, -2.5, 2.5, 7.5]; COLS_X = [FX - 18 + k * 4 for k in range(10)]
tubos = []
for ly in LINHAS_Y:
    for cx in COLS_X:
        b, t = centrifuga(_id("cf"), (cx, FY + ly), h=5.2, r=0.55)
        tubos.append(t)
# tubulação em fila (cascata): coletor por linha + curvas nas pontas, em zigue-zague
bm = bmesh.new(); ZP = 6.4; CASC = []
for k, ly in enumerate(LINHAS_Y):
    xa, xb = (COLS_X[0], COLS_X[-1]) if k % 2 == 0 else (COLS_X[-1], COLS_X[0])
    _viga(bm, (xa, FY + ly, ZP), (xb, FY + ly, ZP), 0.14, seg=6)
    CASC += [(xa, FY + ly, ZP), (xb, FY + ly, ZP)]
    if k < len(LINHAS_Y) - 1: _viga(bm, (xb, FY + ly, ZP), (xb, FY + LINHAS_Y[k + 1], ZP), 0.14, seg=6)
for cx in COLS_X:
    for ly in LINHAS_Y: _viga(bm, (cx, FY + ly, 5.9), (cx, FY + ly, ZP), 0.06, seg=4)
tubulacao = _new_obj("tubulacao", bm, (0.62, 0.64, 0.68, 1))
# pátio de cilindros de UF6 (na frente do salão)
PATIO = (FX - 8, FY - 22)
caixa("patioCil", (PATIO[0], PATIO[1], 0.1), (24, 9, 0.2), (0.66, 0.65, 0.62, 1))
cils = []
for k in range(6):
    c = cilindro_uf6(_id("uf6"), (PATIO[0] - 9 + k * 3.6, PATIO[1], 1.0)); c.rotation_euler = (math.radians(90), 0, 0); cils.append(c)
# câmeras de vigilância (postes) e selos
cams = []
for k, (x, y) in enumerate(((FX - 22.5, FY - 13.5), (FX + 22.5, FY - 13.5), (PATIO[0] + 13, PATIO[1] - 5))):
    poste = cilindro(_id("pcam"), (x, y, 2.8), 0.12, 5.6, (0.30, 0.32, 0.36, 1), seg=6)
    cx_ = caixa(_id("cam"), (0, 0, 0), (0.7, 1.3, 0.7), BRANCO); filho(poste, cx_); cx_.location = (0, -0.6, 2.9); cx_.rotation_euler = (math.radians(-20), 0, 0)
    led = esfera(_id("led"), (0, 0, 0), 0.16, VERMELHO, sub=1, unico="led"); filho(cx_, led); led.location = (0, -0.68, 0)
    cams.append(poste)
selos = []
for c in cils:
    s_ = caixa(_id("selo"), (0, 0, 0), (0.35, 0.35, 0.6), AZUL_AG, unico="selo"); s_.location = (c.location[0], c.location[1] - 0.1, c.location[2] + 0.82); selos.append(s_)
# portão com cancela e guarita
GX, GY = FX, FY - 38
for sx in (-1, 1):
    caixa("cercaP", (GX + sx * 26, GY, 1.2), (44, 0.25, 2.4), (0.45, 0.47, 0.50, 1))
guarita = caixa("guarita", (GX + 5, GY - 1.5, 1.5), (2.6, 2.6, 3.0), (0.90, 0.88, 0.82, 1))
filho(guarita, caixa("guaritaTeto", (0, 0, 1.65), (3.0, 3.0, 0.3), (0.45, 0.30, 0.25, 1)))
piv_canc = vazio("pivCancela", (GX + 3.6, GY, 1.2))
canc = caixa("cancela", (0, 0, 0), (7.2, 0.25, 0.25), (0.95, 0.20, 0.15, 1)); filho(piv_canc, canc); canc.location = (-3.6, 0, 0)
cilindro("postoCancela", (GX + 3.6, GY, 0.6), 0.25, 1.2, (0.30, 0.32, 0.36, 1), seg=8)

# =====================================================================
# 3) BUNKER NA MONTANHA (alvo dos ataques) x ≈ -130, y ≈ 62
# =====================================================================
BK = (-130, 62)
mt = esfera("montanha", (BK[0], BK[1] + 10, -6), 26, (0.56, 0.52, 0.42, 1), sub=3); mt.scale = (1.4, 1.0, 0.75)
for dx in (-8, 0, 8):
    caixa("tunel", (BK[0] + dx, BK[1] - 15.2, 2.0), (3.2, 2.0, 4.0), (0.10, 0.10, 0.11, 1))
    caixa("tunelMoldura", (BK[0] + dx, BK[1] - 15.0, 4.3), (4.0, 2.2, 0.6), CONC)
caixa("acessoBk", (BK[0], BK[1] - 28, 0.03), (6, 22, 0.06), C["rua"])
for gx in (-40, 34, 46): caixa(_id("galpaoBk"), (BK[0] + gx, BK[1] - 30, 2.0), (8, 6, 4), (0.86, 0.84, 0.78, 1))

# =====================================================================
# 4) USINA NUCLEAR + CIDADE (x ≈ 10)
# =====================================================================
UX, UY = 10, 8
reat, torres_topo = reator("reator"); reat.location = (UX, UY, 0)
torres_topo = [(UX + x, UY + y, z) for x, y, z in torres_topo]
for k, x in enumerate((44, 52, 60, 68, 76, 84)):
    for y in (-18, -8, 2, 12):
        h = random.uniform(5, 15); predio((x + random.uniform(-1, 1), y), random.uniform(5, 6.5), random.uniform(5, 6.5), h, random.choice(PREDIOS))
bm = bmesh.new()
for k, x in enumerate(range(34, 44, 5)): _viga(bm, (x, -4, 0), (x, -4, 8), 0.18)
_viga(bm, (26, -4, 7.5), (39, -4, 7.5), 0.06); _viga(bm, (39, -4, 7.5), (46, -10, 6), 0.06)
_new_obj("linhaUsina", bm, (0.35, 0.37, 0.40, 1))
# medidor de enriquecimento (tubo graduado ao lado da fábrica)
MX, MY = -50, -14; MH = 14.0
caixa("baseMedidor", (MX, MY, 0.4), (4.4, 4.4, 0.8), (0.30, 0.32, 0.36, 1))
bm = bmesh.new()
for a in range(6):
    ang = a * math.pi / 3; _viga(bm, (MX + math.cos(ang) * 1.7, MY + math.sin(ang) * 1.7, 0.8), (MX + math.cos(ang) * 1.7, MY + math.sin(ang) * 1.7, 0.8 + MH), 0.07, seg=4)
for z in (0.8, 0.8 + MH):
    for a in range(6):
        a0, a1 = a * math.pi / 3, (a + 1) * math.pi / 3
        _viga(bm, (MX + math.cos(a0) * 1.7, MY + math.sin(a0) * 1.7, z), (MX + math.cos(a1) * 1.7, MY + math.sin(a1) * 1.7, z), 0.07, seg=4)
gaiola = _new_obj("gaiolaMedidor", bm, METAL)
marcas = []
for nivel, cor in ((0.05, VERDE), (0.20, AMBAR), (0.60, (1.0, 0.45, 0.10, 1)), (0.90, VERMELHO)):
    mk = anel(_id("marca"), (MX, MY, 0.8 + MH * nivel), 1.95, 0.09, cor, seg=24); marcas.append(mk)
enchim = cilindro("enchimento", (MX, MY, 0.8), 1.35, 1.0, VERDE, seg=16, unico="enchimento")
enchim.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 0.5)))   # origem na base (escala Z cresce para cima)

# =====================================================================
# 5) AGÊNCIA (o vigia) + GLOBO  x ≈ 5, y ≈ 100
# =====================================================================
AG = (5, 100)
torres_ag = []
for k, (dx, dy, h) in enumerate(((-9, 0, 26), (0, 5, 32), (9, 0, 22))):
    t_ = cilindro(_id("torreAg"), (AG[0] + dx, AG[1] + dy, h / 2), 4.2, h, (0.92, 0.93, 0.95, 1), seg=20)
    for z in range(3, int(h) - 1, 3):
        v_ = cilindro(_id("tAgVid"), (0, 0, 0), 4.26, 1.3, (0.22, 0.40, 0.60, 1), seg=20); filho(t_, v_); v_.location = (0, 0, z - h / 2)
    torres_ag.append(t_)
caixa("praçaAg", (AG[0], AG[1] - 18, 0.1), (36, 14, 0.2), (0.80, 0.78, 0.74, 1))
GLOBO = (AG[0], AG[1] - 20, 9.0)
globo = esfera("globo", GLOBO, 6.0, C["agua"], sub=3)
for pl in globo.data.polygons: pl.use_smooth = True
continentes = []
random.seed(7)
for _ in range(16):
    d = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-0.8, 0.9))).normalized()
    o = esfera(_id("cont"), (0, 0, 0), random.uniform(1.4, 2.6), C["grama2"], sub=2); o.scale = (1, 1, 0.35)
    o.rotation_mode = "QUATERNION"; o.rotation_quaternion = d.to_track_quat("Z", "Y"); o.location = d * 5.75; filho(globo, o)
pinos = []
for _ in range(36):
    d = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-0.7, 0.9))).normalized()
    p_ = cilindro(_id("pino"), (0, 0, 0), 0.16, 1.6, YELLOW, seg=6, unico="pino"); p_.rotation_mode = "QUATERNION"
    p_.rotation_quaternion = d.to_track_quat("Z", "Y"); p_.location = d * 6.5; filho(globo, p_); pinos.append(p_)
filho(globo, esfera(_id("eixo"), (0, 0, -6.6), 0.6, METAL))
cilindro("pedestalGlobo", (GLOBO[0], GLOBO[1], 1.5), 1.2, 3.0, METAL, seg=10)

# =====================================================================
# 6) COMPLEXO NA COREIA DO NORTE (Yongbyon, genérico) x ≈ 165, y ≈ 45 + satélite
# =====================================================================
YB = (165, 45)
caixa("rioYB", (YB[0] - 30, YB[1], 0.04), (14, 160, 0.08), C["agua"])
caixa("lajeYB", (YB[0], YB[1], 0.1), (60, 46, 0.2), (0.64, 0.62, 0.58, 1))
salao = caixa("salaoAzul", (YB[0] - 6, YB[1] + 4, 3.5), (30, 12, 7), (0.88, 0.86, 0.82, 1))
filho(salao, caixa("tetoAzul", (0, 0, 3.75), (30.6, 12.6, 0.5), (0.18, 0.36, 0.72, 1)))
anexo = caixa("anexoNovo", (YB[0] + 16, YB[1] + 4, 3.5), (12, 12, 7), (0.90, 0.88, 0.84, 1))
filho(anexo, caixa("tetoAnexo", (0, 0, 3.75), (12.6, 12.6, 0.5), (0.18, 0.36, 0.72, 1)))
for k in range(4): caixa(_id("galpaoYB"), (YB[0] - 18 + k * 12, YB[1] - 14, 2.5), (8, 7, 5), (0.80, 0.78, 0.72, 1))
cilindro("chamineYB", (YB[0] + 20, YB[1] - 14, 10), 1.4, 20, CONC, seg=12)
sat = satelite("satelite", 1.6)
scan = cilindro("scan", (0, 0, 0), 1.0, 1.0, CIANO, seg=24, r2=0.0, unico="scan")

# =====================================================================
# CARROS, PESSOAS, ATAQUES
# =====================================================================
van, _ = caminhao("vanInspetores", (0, 0, 1.0), cor=BRANCO, tubos=False)
filho(van, caixa("bauVan", (0, -1.0, 1.25), (2.4, 4.6, 1.9), BRANCO))
filho(van, caixa("faixaVan", (0, -1.0, 1.25), (2.45, 4.62, 0.35), AZUL_AG))
ins1, bd1, be1 = boneco("insp1", (0, 0, 0), camisa=AZUL_AG, capacete=False)
ins2, bd2, be2 = boneco("insp2", (0, 0, 0), camisa=AZUL_AG, capacete=False)
for ins in (ins1, ins2):
    filho(ins, esfera(_id("capBranco"), (0, 0, 2.12), 0.38, BRANCO, sub=1))
pano = caixa("pano", (0, 0, 0), (0.6, 0.1, 0.6), BRANCO, unico="pano")

cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 24; cam_d.clip_end = 6000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def shot(t0, t1, loc0, tgt0, loc1=None, tgt1=None):
    for fr, loc, tgt in ((f(t0), loc0, tgt0), (f(t1) - 1, loc1 or loc0, tgt1 or tgt0)):
        for ob, v in ((cam, loc), (alvo, tgt)):
            ob.location = v; ob.keyframe_insert("location", frame=fr)

def andar(ob, t0, t1, a, b):
    ob.location = a; ob.keyframe_insert("location", frame=f(t0)); ob.location = b; ob.keyframe_insert("location", frame=f(t1))
def rumo(ob, t, graus):
    ob.rotation_euler = (0, 0, math.radians(graus)); ob.keyframe_insert("rotation_euler", frame=f(t), index=2)
def cancela(t, aberta):
    piv_canc.rotation_euler = (0, math.radians(-80 if aberta else 0), 0); piv_canc.keyframe_insert("rotation_euler", frame=f(t), index=1)

GIRO_T = 0.0
for t_ in tubos: girar(t_, 0.0, rps=random.uniform(1.2, 1.8))
GATE_OUT = (GX - 1.5, GY - 9, 1.0)

# ---------- S0: gancho (ataque ao bunker, van barrada no portão, salão das centrífugas) ----------
t0, t1 = S[0]
tA, tB = 1.35, 2.25
ataque((BK[0] - 8, BK[1] - 16, 3.0), tA, (BK[0] - 70, BK[1] - 120, 70), dur=1.35)
ataque((BK[0] + 8, BK[1] - 16, 3.0), tB, (BK[0] + 60, BK[1] - 130, 80), dur=1.7)
fumaca((BK[0] - 8, BK[1] - 17, 4), tA + 0.2, S[1][0]); fumaca((BK[0] + 8, BK[1] - 17, 4), tB + 0.2, S[1][0], cada=0.45)
tv = T(0, "passada")
shot(t0, tv - 0.1, (BK[0] - 6, BK[1] - 52, 9), (BK[0], BK[1] - 14, 5), (BK[0] - 2, BK[1] - 47, 11), (BK[0], BK[1] - 14, 6))
# van parada na cancela fechada, com X vermelho (flash-forward do impasse)
cancela(0, False)
van.location = GATE_OUT; van.keyframe_insert("location", frame=1); rumo(van, 0, 0)
xis((GX - 1.5, GY - 0.5, 6.5), 2.0, T(0, "inspetores") - 0.1, T(0, "Como") - 0.1)
van.location = GATE_OUT; van.keyframe_insert("location", frame=f(T(0, "Como") - 0.12))
shot(tv - 0.1, T(0, "Como") - 0.1, (GX + 9, GY - 24, 4.5), (GX - 1, GY - 3, 3.5), (GX + 7, GY - 21, 5.0), (GX - 1, GY - 3, 3.8))
shot(T(0, "Como") - 0.1, t1, (FX + 30, FY - 30, 20), (FX, FY, 3), (FX + 24, FY - 26, 22), (FX - 2, FY, 3))

# ---------- S1: matéria-prima (mina e 100 bolinhas) ----------
t0, t1 = S[1]
tur = T(1, "urânio")
shot(t0, tur + 1.2, (MINA[0] + 32, MINA[1] - 44, 22), (MINA[0], MINA[1], -1), (MINA[0] + 26, MINA[1] - 40, 20), (MINA[0] + 2, MINA[1], -1))
tm = T(1, "menos")
for o, verde in bolas:
    tt = tur + 1.2 + random.uniform(0, 0.8); pop(o, tt, 1.0, 0.3)
    if verde:
        t5 = T(1, "235"); o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(t5)); o.scale = (1.8,) * 3; o.keyframe_insert("scale", frame=f(t5 + 0.4))
shot(tur + 1.2, t1, (GRADE[0] + 2, GRADE[1] - 17, 13), (GRADE[0], GRADE[1], 0.5), (GRADE[0] + 1, GRADE[1] - 14, 11), (GRADE[0] + 0.5, GRADE[1] + 0.5, 0.5))

# ---------- S2: enriquecimento (centrífugas em fila) ----------
t0, t1 = S[2]
tcf = T(2, "centrífugas")
pulsos(CASC, [(T(2, "cada"), S[5][0])], VERDE, "gas", cada=0.35, vel=26)
shot(t0, tcf - 0.2, (FX - 28, FY - 22, 12), (FX - 6, FY, 4), (FX - 22, FY - 20, 11), (FX - 4, FY, 4))
shot(tcf - 0.2, t1, (FX + 6, FY - 15, 5.5), (FX - 6, FY + 2, 4.5), (FX + 2, FY - 14, 6.5), (FX - 10, FY + 2, 4.5))

# ---------- S3: urânio de usina (usina nuclear acende a cidade) ----------
t0, t1 = S[3]
for p in torres_topo: fumaca(p, t0 - 0.3, S[4][0] + 1.0, r=3.0, cada=0.5, sobe=10, vida=3.0, cor=(0.96, 0.96, 0.98, 1))
shot(t0, t1, (UX - 34, UY - 52, 18), (UX + 22, UY + 6, 9), (UX - 28, UY - 56, 20), (UX + 26, UY + 6, 9))

# ---------- S4: grau de arma (medidor sobe 20 / 60 / 90) ----------
t0, t1 = S[4]
m_en = enchim.data.materials[0]
def nivel(t, v): enchim.scale = (1, 1, MH * v); enchim.keyframe_insert("scale", frame=f(t), index=2)
nivel(0, 0.045); nivel(t0, 0.045)
t20, t60, t90 = T(4, "Vinte"), T(4, "sessenta"), T(4, "noventa")
nivel(t20 + 0.4, 0.20); nivel(t60 + 0.4, 0.60); nivel(t90 + 0.5, 0.90)
cor_key(m_en, 0, VERDE); cor_key(m_en, t20, VERDE); cor_key(m_en, t20 + 0.4, AMBAR); cor_key(m_en, t60 + 0.4, (1.0, 0.45, 0.10, 1)); cor_key(m_en, t90 + 0.5, VERMELHO)
shot(t0, T(4, "Com") - 0.1, (MX - 16, MY - 22, 9), (MX - 6, MY + 4, 6), (MX - 14, MY - 20, 10), (MX - 5, MY + 4, 7))
shot(T(4, "Com") - 0.1, t1, (MX + 7, MY - 13, 6), (MX, MY, 6.5), (MX + 6, MY - 11, 12), (MX, MY, 9.5))

# ---------- S5: o vigia (agência + globo com adesões) ----------
t0, t1 = S[5]
tq = T(5, "Quase")
for k, p_ in enumerate(pinos): pop(p_, tq + 0.08 * k, 1.0, 0.25)
globo.rotation_euler = (0, 0, 0); globo.keyframe_insert("rotation_euler", frame=f(t0), index=2)
globo.rotation_euler = (0, 0, math.radians(120)); globo.keyframe_insert("rotation_euler", frame=f(t1), index=2)
shot(t0, tq - 0.1, (AG[0] + 22, AG[1] - 64, 26), (AG[0], AG[1], 14), (AG[0] + 18, AG[1] - 58, 24), (AG[0], AG[1], 14))
shot(tq - 0.1, t1, (GLOBO[0] + 4, GLOBO[1] - 19, 11), (GLOBO[0], GLOBO[1], 9), (GLOBO[0] - 4, GLOBO[1] - 18, 12), (GLOBO[0], GLOBO[1], 9))

# ---------- S6: a inspeção (van entra, selos, câmeras, pano) ----------
t0, t1 = S[6]
van.location = (GX - 1.5, GY - 60, 1.0); van.keyframe_insert("location", frame=f(T(0, "Como")))
van.keyframe_insert("location", frame=f(t0))
cancela(t0, False); cancela(t0 + 0.8, True)
andar(van, t0, t0 + 2.6, (GX - 1.5, GY - 60, 1.0), (GX - 1.5, PATIO[1] - 9, 1.0))
for ins, a, b in ((ins1, (PATIO[0] - 11, PATIO[1] - 6, 0), (PATIO[0] - 7, PATIO[1] - 2, 0)), (ins2, (PATIO[0] - 9, PATIO[1] - 7, 0), (FX - 15.8, FY - 14.4, 0))):
    visivel(ins, t0 + 2.7, S[7][0] + 0.2); andar(ins, t0 + 2.7, t0 + 5.0, a, b)
tl = T(6, "Lacram")
for k, s_ in enumerate(selos): visivel(s_, tl + 0.15 * k); pop(s_, tl + 0.15 * k, 1.0, 0.3)
ti = T(6, "instalam")
for k, c in enumerate(cams): visivel(c, 0.01); pop(c, ti + 0.25 * k, 1.0, 0.35)
tct = T(6, "contam")
destacar(mat(UF6), tct, UF6, dur=1.6)
tpn = T(6, "pano")
visivel(pano, tpn - 0.2, S[7][0]); pano.location = (FX - 14.8, FY - 13.5, 1.5); pano.keyframe_insert("location", frame=f(tpn - 0.2))
for k in range(8):
    pano.location = (FX - 14.8 + (k % 2) * 1.0, FY - 13.5, 1.5 + (k % 3) * 0.3); pano.keyframe_insert("location", frame=f(tpn + 0.3 * k))
be2.rotation_euler = (0, 0, 0); be2.keyframe_insert("rotation_euler", frame=f(tpn - 0.2), index=0); be2.rotation_euler = (math.radians(-80), 0, 0); be2.keyframe_insert("rotation_euler", frame=f(tpn), index=0)
shot(t0, tl - 0.1, (GX + 14, GY - 30, 8), (GX - 1.5, GY - 4, 2), (GX + 10, GY - 22, 9), (GX - 1.5, PATIO[1] - 6, 2))
shot(tl - 0.1, tpn - 0.2, (PATIO[0] + 6, PATIO[1] - 14, 5), (PATIO[0] - 2, PATIO[1], 1.5), (PATIO[0] + 2, PATIO[1] - 13, 6), (PATIO[0] - 5, PATIO[1], 2))
part = esfera("particula", (FX - 12.6, FY - 13.48, 1.9), 0.05, VERDE, sub=2, unico="u235"); visivel(part, T(6, "partícula") - 0.1, S[7][0]); pop(part, T(6, "partícula"), 1.0, 0.4)
shot(tpn - 0.2, T(6, "partícula") - 0.1, (FX - 8, FY - 22, 3.4), (FX - 14.5, FY - 13.5, 1.8), (FX - 9, FY - 21, 3.2), (FX - 14.0, FY - 13.5, 1.8))
shot(T(6, "partícula") - 0.1, t1, (FX - 12.3, FY - 15.0, 2.0), (FX - 12.6, FY - 13.48, 1.9), (FX - 12.4, FY - 14.3, 1.95), (FX - 12.6, FY - 13.48, 1.9))

# ---------- S7: o impasse (porta fechada; ataques; van barrada) ----------
t0, t1 = S[7]
tp = T(7, "porta")
cancela(tp - 0.3, True); cancela(tp + 0.4, False)
van.location = (GX - 1.5, PATIO[1] - 9, 1.0); van.keyframe_insert("location", frame=f(t0)); rumo(van, t0, 0); rumo(van, t0 + 0.6, 180)
andar(van, t0 + 0.1, tp - 0.4, (GX - 1.5, PATIO[1] - 9, 1.0), GATE_OUT)
van.keyframe_insert("location", frame=f(S[8][0]))
xis((GX - 1.5, GY - 0.5, 6.5), 2.0, tp + 0.4, T(7, "Depois") + 0.2)
shot(t0, T(7, "Depois") - 0.1, (GX + 11, GY - 26, 6), (GX - 1, GY - 1, 2.8), (GX + 8, GY - 22, 6.5), (GX - 1, GY - 1, 3.2))
tbm = T(7, "bombardeios")
ataque((BK[0] - 8, BK[1] - 16, 3.0), tbm + 0.3, (BK[0] - 60, BK[1] - 120, 75), dur=1.2)
ataque((BK[0], BK[1] - 16, 3.0), tbm + 1.0, (BK[0] + 50, BK[1] - 120, 80), dur=1.3)
ataque((BK[0] + 8, BK[1] - 16, 3.0), tbm + 1.7, (BK[0] + 10, BK[1] - 140, 90), dur=1.4)
for k, dx in enumerate((-8, 0, 8)): fumaca((BK[0] + dx, BK[1] - 17, 4), tbm + 0.5 + 0.7 * k, T(7, "Washington"), cada=0.4)
shot(T(7, "Depois") - 0.1, T(7, "limitar") - 0.2, (BK[0] + 10, BK[1] - 62, 14), (BK[0], BK[1] - 14, 5), (BK[0] + 4, BK[1] - 56, 16), (BK[0], BK[1] - 14, 6))
shot(T(7, "limitar") - 0.2, T(7, "Washington") - 0.1, (GX - 14, GY - 18, 7), (GX - 1, GY, 2.5), (GX - 11, GY - 16, 8), (GX - 1, GY, 2.5))
shot(T(7, "Washington") - 0.1, t1, (FX - 40, FY - 70, 34), (FX - 20, FY + 10, 2), (FX - 34, FY - 64, 36), (FX - 16, FY + 10, 2))

# ---------- S8: o ponto cego (satélite sobre Yongbyon) ----------
t0, t1 = S[8]
ts = T(8, "satélite")
visivel(sat, t0, S[9][0])
caminho(sat, t0, S[9][0], lambda u: (YB[0] - 60 + 120 * u, YB[1] - 10 + 10 * u, 75), orientar=False, passo=3)
visivel(scan, ts, S[9][0])
scan.scale = (12, 12, 72); scan.location = (0, 0, 0)
caminho(scan, t0, S[9][0], lambda u: (YB[0] - 60 + 120 * u, YB[1] - 10 + 10 * u, 36.2), orientar=False, passo=3)
tn = T(8, "ampliação")
pop(anexo, tn, 1.0, 0.6)
def satp(t): u = (t - t0) / (S[9][0] - t0); return (YB[0] - 60 + 120 * u, YB[1] - 10 + 10 * u, 75)
shot(t0, ts - 0.1, (satp(t0)[0] - 4, YB[1] - 40, 64), satp(t0), (satp(ts)[0] - 2, YB[1] - 38, 64), satp(ts))
tN = T(8, "Neste") - 0.1
shot(ts - 0.1, tN, (satp(ts)[0] - 18, YB[1] - 58, 92), (satp(ts)[0] + 14, YB[1] + 4, 22), (satp(tN)[0] - 18, YB[1] - 58, 92), (satp(tN)[0] + 14, YB[1] + 4, 22))
shot(T(8, "Neste") - 0.1, t1, (YB[0] + 6, YB[1] - 26, 42), (YB[0] + 6, YB[1] + 4, 2), (YB[0] + 10, YB[1] - 22, 38), (YB[0] + 10, YB[1] + 4, 2))

# ---------- S9-S10: parabéns (visão geral) + CTA + like ----------
t0, _ = S[9]
shot(t0, S[10][0], (-40, -150, 70), (-60, 10, 0), (-20, -140, 90), (-40, 20, 0))
shot(S[10][0], FIM, (FX + 26, FY - 34, 14), (FX - 4, FY, 3), (FX + 34, FY - 44, 22), (FX - 4, FY, 3))
# van volta ao portão no CTA? (fica estacionada no pátio de fora)

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
    emissivo("u235", VERDE, 6.0); emissivo("gas", VERDE, 5.0); emissivo("led", VERMELHO, 6.0); emissivo("xis", VERMELHO, 1.2)
    emissivo("pino", YELLOW, 1.5); emissivo("selo", AZUL_AG, 0.8); emissivo("scan", CIANO, 1.5)
    em = enchim.data.materials[0]; b = em.node_tree.nodes.get("Principled BSDF")
    b.inputs["Emission Strength"].default_value = 2.5
    for t, cor in ((0, VERDE), (t20 + 0.4, AMBAR), (t60 + 0.4, (1.0, 0.45, 0.10, 1)), (t90 + 0.5, VERMELHO)):
        b.inputs["Emission Color"].default_value = _lin(cor); b.inputs["Emission Color"].keyframe_insert("default_value", frame=f(t))
    sc = [m for k, m in _mats.items() if k[1] == "scan"]
    for m in sc:   # cone do satélite translúcido
        m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
        bb = m.node_tree.nodes.get("Principled BSDF"); bb.inputs["Alpha"].default_value = 0.14
        try: m.surface_render_method = "BLENDED"
        except Exception: pass
    # backlog 10: explosões com emissão baixa e laranja mais escuro (não estoura para rosa no AgX)
    for m in bpy.data.materials:
        if tuple(round(c, 3) for c in m.diffuse_color) == tuple(round(c, 3) for c in C["laranja"]):
            b = m.node_tree.nodes.get("Principled BSDF"); b.inputs["Emission Color"].default_value = _lin((1.0, 0.42, 0.06, 1)); b.inputs["Emission Strength"].default_value = 1.2
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
