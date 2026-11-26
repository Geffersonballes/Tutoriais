"""Vídeo 'Por que os mísseis acabam?' (estoque de mísseis, 26/11). Uso:
REALISTA=1 blender -b --factory-startup -P cena_misseis.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
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
scn.world.color = (0.30, 0.60, 0.95)

CONC = (0.80, 0.79, 0.76, 1); METAL = (0.74, 0.76, 0.78, 1); OLIVA = (0.38, 0.44, 0.26, 1)
VERDE = (0.25, 1.0, 0.35, 1); VERMELHO = (1.0, 0.15, 0.10, 1); AMBAR = (1.0, 0.72, 0.25, 1)
VELHO = (0.55, 0.48, 0.38, 1); AZUL = (0.20, 0.42, 0.85, 1); BRANCO = C["branco"]; AMARELO = (0.95, 0.80, 0.15, 1)

def fumaca(loc, t0, t1, r=0.9, cada=0.45, sobe=10.0, vida=2.4, cor=(0.45, 0.44, 0.44, 1)):
    t = t0
    while t < t1:
        o = esfera(_id("fz"), loc, r * random.uniform(0.7, 1.2), cor, sub=1, unico="fumaca")
        visivel(o, t, t + vida)
        o.location = loc; o.keyframe_insert("location", frame=f(t))
        o.location = (loc[0] + random.uniform(-1.5, 1.5) + sobe * 0.2, loc[1] + random.uniform(-1, 1), loc[2] + sobe); o.keyframe_insert("location", frame=f(t + vida))
        o.scale = (0.4,) * 3; o.keyframe_insert("scale", frame=f(t))
        o.scale = (1.6,) * 3; o.keyframe_insert("scale", frame=f(t + vida * 0.7))
        o.scale = (0.05,) * 3; o.keyframe_insert("scale", frame=f(t + vida))
        t += cada

def xis(loc, R, t0, t1, rot=0.0):
    p = vazio(_id("xis"), loc)
    for a in (45, -45):
        b = caixa(_id("xbar"), (0, 0, 0), (R * 2.4, R * 0.28, R * 0.28), VERMELHO, unico="xis"); b.rotation_euler = (0, math.radians(a), 0); filho(p, b)
    p.rotation_euler = (0, 0, rot); visivel(p, t0, t1); pop(p, t0); return p

def andar(ob, t0, t1, a, b):
    ob.location = a; ob.keyframe_insert("location", frame=f(t0)); ob.location = b; ob.keyframe_insert("location", frame=f(t1))

# =====================================================================
# TERRENO + MAR
# =====================================================================
caixa("chao", (-200, 0, -0.5), (620, 1400, 1.0), C["grama"])
mar = caixa("mar", (560, 0, -0.6), (900, 1400, 1.0), C["agua"])
caixa("areia", (112, 0, -0.45), (12, 1400, 1.0), (0.90, 0.84, 0.66, 1))
caixa("estradaA", (-40, -30, 0.03), (240, 6, 0.06), C["rua"])
caixa("estradaB", (0, 30, 0.03), (6, 120, 0.06), C["rua"])
for _ in range(26):
    m = esfera("morro", (random.uniform(-450, 60), random.uniform(180, 380), -4), random.uniform(18, 40), random.choice([C["morro"], C["grama2"]]), sub=2)
    m.scale = (1.7, 1.0, 0.5)
for _ in range(150):
    x = random.uniform(-200, 100); y = random.uniform(-140, 160)
    if (-30 < x < 30 and -24 < y < 24) or (-130 < x < -50 and -24 < y < 24) or (-30 < x < 50 and 60 < y < 130): continue
    if (-150 < x < -30 and -100 < y < -50) or abs(y + 30) < 6 or abs(x) < 6: continue
    arvore((x, y), random.uniform(0.9, 1.6))

# =====================================================================
# 1) PAIOL (estoque) na origem — galpão em corte com 4 prateleiras
# =====================================================================
caixa("lajePaiol", (0, 0, 0.15), (50, 40, 0.3), (0.70, 0.70, 0.68, 1))
caixa("paredeFundoP", (0, 20, 5), (50, 0.8, 10), CONC)
for sx in (-1, 1): caixa("paredeLadoP", (sx * 25, 0, 3), (0.8, 40, 6), CONC)
caixa("muretaP", (0, -20, 0.8), (50, 0.8, 1.6), CONC)
for sx in (-24.6, 24.6):
    for sy in (-10, 10): caixa("pilarP", (sx, sy, 5.2), (0.6, 0.6, 10.4), (0.40, 0.44, 0.50, 1))
caixa("vigaP", (0, -10, 10.2), (50, 0.6, 0.6), (0.40, 0.44, 0.50, 1)); caixa("vigaP2", (0, 10, 10.2), (50, 0.6, 0.6), (0.40, 0.44, 0.50, 1))
RACK_Y = [-9, -1, 7]; NIVEIS = [1.2, 3.4, 5.6]; COLS = [-17 + k * 4.2 for k in range(8)]
bm = bmesh.new()
for ry in RACK_Y:
    for z in NIVEIS:
        _viga(bm, (COLS[0] - 2.5, ry, z - 0.4), (COLS[-1] + 2.5, ry, z - 0.4), 0.06)
        _viga(bm, (COLS[0] - 2.5, ry + 2.6, z - 0.4), (COLS[-1] + 2.5, ry + 2.6, z - 0.4), 0.06)
    for x in (COLS[0] - 2.5, 0, COLS[-1] + 2.5):
        for dy in (0, 2.6): _viga(bm, (x, ry + dy, 0.3), (x, ry + dy, NIVEIS[-1] + 0.6), 0.1)
_new_obj("prateleiras", bm, (0.55, 0.58, 0.62, 1))
estoque = []
for ry in RACK_Y:
    for z in NIVEIS:
        for x in COLS:
            m = tomahawk(_id("tw"), escala=0.72); m.location = (x, ry + 1.3, z); m.rotation_euler = (0, 0, math.radians(90))
            estoque.append(m)
# canto dos "vencidos": caixotes velhos
velhos = []
for k in range(4):
    cx = caixote_missil(_id("velho"), cor=VELHO, escala=0.9, unico="velho"); cx.location = (-20 + (k % 2) * 1.4, -15.5 + (k // 2) * 0.0, 0.75 + (k // 2) * 1.0)
    cx.rotation_euler = (0, 0, math.radians(90)); velhos.append(cx)
for k in range(3):
    teia = caixa(_id("poeira"), (-19.3, -15.5, 2.4 + k * 0.01), (2.8, 5.6, 0.02), (0.62, 0.58, 0.50, 1)); velhos.append(teia)
scanner_luz = caixa("scanner", (-19.3, -15.5, 1.2), (3.4, 0.08, 2.8), VERDE, unico="scan")
tecnico, bd_t, be_t = boneco("tecnico", (-15, -12, 0.3), camisa=AZUL, capacete=False)
filho(tecnico, esfera(_id("bone"), (0, 0, 2.12), 0.38, BRANCO, sub=1))

# =====================================================================
# 2) FÁBRICA (x ≈ -90) — salão aberto com esteira e 3 fornecedores
# =====================================================================
FX, FY = -90, 0
caixa("lajeFab", (FX, FY, 0.15), (60, 30, 0.3), (0.68, 0.68, 0.66, 1))
caixa("paredeFab", (FX, FY + 15, 5.5), (60, 0.8, 11), (0.84, 0.82, 0.76, 1))
for sx in (-1, 1): caixa("ladoFab", (FX + sx * 30, FY, 2.5), (0.8, 30, 5), (0.84, 0.82, 0.76, 1))
for k in range(5): caixa(_id("shed"), (FX - 24 + k * 12, FY + 12.5, 12.2), (11.6, 5, 0.5), (0.35, 0.45, 0.60, 1))
cham = cilindro("chamFab", (FX + 22, FY + 19, 10), 1.4, 20, CONC, seg=12)
ESTEIRA_Y = FY - 2
caixa("esteira", (FX, ESTEIRA_Y, 1.0), (50, 3.0, 0.4), (0.15, 0.15, 0.16, 1))
for k in range(13): caixa(_id("pesteira"), (FX - 24 + k * 4, ESTEIRA_Y, 0.45), (2.8, 0.3, 0.9), (0.40, 0.42, 0.45, 1))
for k in range(4):
    br = caixa(_id("robo"), (FX - 14 + k * 9, ESTEIRA_Y + 4.0, 2.2), (1.2, 1.2, 4.4), AMARELO); bra = caixa(_id("robob"), (0, -1.6, 2.0), (0.6, 3.6, 0.6), AMARELO); filho(br, bra)
# peças dos fornecedores: motor (cilindro cinza), explosivo (caixa laranja), eletrônica (placa verde)
PEC = {"motor": cilindro("pecaMotor", (0, 0, 0), 0.9, 2.4, (0.45, 0.47, 0.50, 1), seg=12),
       "explosivo": caixa("pecaExpl", (0, 0, 0), (1.6, 1.6, 1.4), C["laranja"]),
       "eletronica": caixa("pecaElet", (0, 0, 0), (1.8, 1.4, 0.2), (0.10, 0.55, 0.25, 1), unico="placa")}
PEC["motor"].rotation_euler = (math.radians(90), 0, 0)
chips = []
for k in range(4):
    ch = caixa(_id("chip"), (-0.5 + (k % 2) * 1.0, -0.35 + (k // 2) * 0.7, 0.15), (0.4, 0.4, 0.1), (0.08, 0.08, 0.10, 1)); filho(PEC["eletronica"], ch)
CAMS = {}
for nome, cor, ini, fimpos in (("motor", (0.20, 0.35, 0.65, 1), (FX - 60, FY - 30, 1.0), (FX - 22, FY - 9, 1.0)),
                               ("explosivo", (0.85, 0.25, 0.15, 1), (FX - 60, FY - 30, 1.0), (FX - 8, FY - 9, 1.0)),
                               ("eletronica", (0.95, 0.95, 0.95, 1), (FX - 60, FY - 30, 1.0), (FX + 6, FY - 9, 1.0))):
    cm, _ = caminhao("cam_" + nome, ini, cor=cor, tubos=False)
    filho(cm, caixa(_id("bau"), (0, -1.0, 1.25), (2.4, 4.6, 1.9), cor))
    CAMS[nome] = (cm, ini, fimpos)
novo = tomahawk("novoMissil", escala=0.9); novo.location = (FX + 16, ESTEIRA_Y, 1.6)
# fábricas extras (guerra das fábricas)
extras = []
for k, (x, y) in enumerate(((-150, -70), (-120, -78), (-90, -74), (-60, -78), (-35, -70))):
    g = caixa(_id("fabX"), (x, y, 4), (18, 12, 8), random.choice([(0.86, 0.84, 0.78, 1), (0.82, 0.86, 0.90, 1), (0.90, 0.82, 0.74, 1)]))
    filho(g, caixa(_id("fabXt"), (0, 0, 4.2), (18.6, 12.6, 0.5), (0.35, 0.45, 0.60, 1)))
    ch = cilindro(_id("fabXc"), (6, 4, 6), 0.9, 12, CONC, seg=10); filho(g, ch)
    extras.append((g, (x + 6, y + 4, 16.5)))
caixa("estradaFab", (-90, -55, 0.03), (150, 5, 0.06), C["rua"])

# =====================================================================
# 3) DEPÓSITO "WASHINGTON" (x≈0, y≈95) com caixotes de Patriot e as duas filas
# =====================================================================
DP = (0, 95)
caixa("lajeDep", (DP[0], DP[1], 0.12), (26, 20, 0.24), (0.66, 0.65, 0.62, 1))
bm = bmesh.new()
for (a, b) in (((-13, -10), (13, -10)), ((13, -10), (13, 10)), ((13, 10), (-13, 10)), ((-13, 10), (-13, -10))):
    _viga(bm, (DP[0] + a[0], DP[1] + a[1], 2.4), (DP[0] + b[0], DP[1] + b[1], 2.4), 0.06)
    for k in range(9):
        u = k / 8; x = a[0] + (b[0] - a[0]) * u; y = a[1] + (b[1] - a[1]) * u
        _viga(bm, (DP[0] + x, DP[1] + y, 0), (DP[0] + x, DP[1] + y, 2.6), 0.08)
_new_obj("cercaDep", bm, (0.45, 0.47, 0.50, 1))
cerca_tela = caixa("telaDep", (DP[0], DP[1] - 10, 1.3), (26, 0.05, 2.4), (0.55, 0.57, 0.60, 1))
cadeado = vazio("cadeado", (DP[0], DP[1] - 10.4, 1.6))
filho(cadeado, caixa(_id("cadC"), (0, 0, 0), (1.4, 0.5, 1.2), AMARELO), anel(_id("cadA"), (0, 0, 0.8), 0.5, 0.12, METAL, seg=16))
for o in cadeado.children:
    if o.name.startswith("cadA"): o.rotation_euler = (math.radians(90), 0, 0)
patriots = []
for k in range(8):
    cx = caixote_missil(_id("pac"), cor=(0.80, 0.80, 0.76, 1), escala=0.9); cx.location = (DP[0] - 7 + (k % 4) * 4.6, DP[1] + (k // 4) * 1.2 - 2, 0.7 + (k // 4) * 1.0)
    patriots.append(cx)
# lado A (tropas americanas, esquerda) e lado B (Ucrânia, direita)
LA = (DP[0] - 45, DP[1] + 10); LB = (DP[0] + 45, DP[1] + 10)
caixa("estradaFilaA", (DP[0] - 25, DP[1], 0.03), (40, 5, 0.06), C["rua"]); caixa("estradaFilaB", (DP[0] + 25, DP[1], 0.03), (40, 5, 0.06), C["rua"])
for k in range(3):
    t_ = caixa(_id("barraca"), (LA[0] - 6 + k * 6, LA[1] + 6, 1.4), (4.6, 5, 2.8), OLIVA)
    filho(t_, caixa(_id("barT"), (0, 0, 1.5), (5, 5.4, 0.3), (0.30, 0.34, 0.20, 1)))
soldados = []
for k in range(4):
    b_, _, _ = boneco(_id("sold"), (LA[0] - 5 + k * 2.2, LA[1] - 2, 0), camisa=OLIVA); soldados.append(b_)
lancA, pivA, _ = lancador_patriot("lancA", (LA[0] + 2, LA[1] - 10, 1.0), cor=(0.42, 0.46, 0.30, 1)); lancA.rotation_euler = (0, 0, math.radians(90))
lancB, pivB, bocasB = lancador_patriot("lancB", (LB[0], LB[1] - 6, 1.0), cor=(0.40, 0.45, 0.32, 1)); lancB.rotation_euler = (0, 0, math.radians(-90))
for k in range(6):
    predio((LB[0] + 14 + (k % 3) * 8, LB[1] + 14 + (k // 3) * 9), 6, 6, random.uniform(8, 16), random.choice(PREDIOS))
cam_entrega, _ = caminhao("camEntrega", (DP[0], DP[1] - 4, 1.0), cor=OLIVA, tubos=False)
caixas_carga = []
for k in range(2):
    cc = caixote_missil(_id("carga"), cor=(0.80, 0.80, 0.76, 1), escala=0.7); filho(cam_entrega, cc); cc.location = (-0.5 + k * 1.0, -1.0, 1.0); caixas_carga.append(cc)
drones = [drone(_id("dr"), escala=2.6) for _ in range(5)]

# =====================================================================
# 4) MAR: destróier que dispara os Tomahawks
# =====================================================================
NV = (300, -10)
navio = navio_guerra("destroier", escala=7.0); navio.location = (NV[0], NV[1], 1.6)
celulas = [(NV[0] + dx, NV[1] + 13 + dy, 4.6) for dx in (-1.6, 1.6) for dy in (0, 2.4, 4.8)]
for c in celulas: caixa(_id("vls"), c, (1.2, 1.2, 0.3), (0.25, 0.27, 0.30, 1))
for k in range(4):
    nv2 = navio_guerra(_id("escolta"), escala=4.0); nv2.location = (NV[0] + 60 + k * 30, NV[1] - 70 + k * 45, 1.2)

def lancar(t, origem, alvo, cor=None, dur=3.2):
    m = tomahawk(_id("vo"), escala=1.7, cor=cor or (0.86, 0.87, 0.88, 1))
    p1 = (origem[0], origem[1], origem[2] + 26); p2 = alvo
    def fn(u):
        if u < 0.25:
            v = u / 0.25; return (origem[0], origem[1], origem[2] + 26 * suave(v))
        v = (u - 0.25) / 0.75; return bez(p1, (p1[0] + (p2[0] - p1[0]) * 0.3, p1[1] + (p2[1] - p1[1]) * 0.3, p1[2] + 16), p2, v)
    visivel(m, t, t + dur); caminho(m, t, t + dur, fn, passo=2)
    rastro(fn, t, t + dur * 0.8, r=1.2, cada=0.1, vida=1.4)
    fl = esfera(_id("flash"), origem, 2.2, C["laranja"], sub=1); visivel(fl, t, t + 0.4)
    fl.scale = (0.3,) * 3; fl.keyframe_insert("scale", frame=f(t)); fl.scale = (1.4,) * 3; fl.keyframe_insert("scale", frame=f(t + 0.2)); fl.scale = (0.05,) * 3; fl.keyframe_insert("scale", frame=f(t + 0.4))
    return m

# =====================================================================
# CÂMERA
# =====================================================================
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 24; cam_d.clip_end = 6000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def shot(t0, t1, loc0, tgt0, loc1=None, tgt1=None):
    for fr, loc, tgt in ((f(t0), loc0, tgt0), (f(t1) - 1, loc1 or loc0, tgt1 or tgt0)):
        for ob, v in ((cam, loc), (alvo, tgt)):
            ob.location = v; ob.keyframe_insert("location", frame=fr)

# ---------- S0: gancho (destróier dispara; Patriots parados; paiol) ----------
t0, t1 = S[0]
tE = T(0, "nesta") - 0.3
for k, tt in enumerate((0.15, 0.9, 1.6, 2.4, 3.3, 4.2, 5.3, 6.2)):
    lancar(tt, celulas[k % len(celulas)], (NV[0] - 260 + k * 8, NV[1] + 300 + k * 30, 30))
shot(t0, 3.0, (NV[0] - 26, NV[1] - 8, 7), (NV[0], NV[1] + 15, 12), (NV[0] - 24, NV[1] - 4, 9), (NV[0], NV[1] + 15, 22))
shot(3.0, tE, (NV[0] - 40, NV[1] - 40, 14), (NV[0], NV[1] + 15, 18), (NV[0] - 55, NV[1] - 30, 20), (NV[0] - 20, NV[1] + 40, 30))
tW = T(0, "Washington"); tPor = T(0, "Por") - 0.15
xis((DP[0], DP[1] - 10.6, 6.0), 2.0, tW - 0.2, tPor)
shot(tE, T(0, "Patriot") - 0.1, (LB[0] + 10, LB[1] - 30, 9), (LB[0], LB[1] - 6, 3.5), (LB[0] + 6, LB[1] - 26, 10), (LB[0], LB[1] - 6, 4))
shot(T(0, "Patriot") - 0.1, tPor, (DP[0] + 6, DP[1] - 30, 9), (DP[0], DP[1] - 4, 2.5), (DP[0] + 3, DP[1] - 25, 10), (DP[0], DP[1] - 4, 3.0))
shot(tPor, t1, (0, -44, 26), (0, 0, 2), (6, -38, 22), (0, 0, 3))

# ---------- S1: o estoque (prateleiras enchem) ----------
t0, t1 = S[1]
tpr = T(1, "prontos")
for k, m in enumerate(estoque):
    tt = t0 + 0.3 + (tpr + 1.4 - t0 - 0.3) * k / len(estoque)
    s_ = tuple(m.scale)
    m.scale = (0.001,) * 3; m.keyframe_insert("scale", frame=1); m.keyframe_insert("scale", frame=max(1, f(tt) - 1))
    m.scale = (1,) * 3; m.keyframe_insert("scale", frame=f(tt + 0.25))
shot(t0, t1, (-16, -17, 4.0), (-6, -7, 2.6), (10, -17, 4.5), (14, -7, 2.6))

# ---------- S2: linha de produção ----------
t0, t1 = S[2]
for nome, palavra in (("motor", "Motor"), ("explosivo", "explosivo"), ("eletronica", "eletrônica")):
    cm, ini, fimpos = CAMS[nome]; tp = T(2, palavra)
    cm.location = ini; cm.keyframe_insert("location", frame=1); cm.keyframe_insert("location", frame=f(tp - 2.2))
    cm.location = fimpos; cm.keyframe_insert("location", frame=f(tp - 0.1)); cm.keyframe_insert("location", frame=f(S[3][0]))
    pc = PEC[nome]; visivel(pc, tp, S[3][0])
    xs = fimpos[0]
    andar(pc, tp, T(2, "meses") + 0.3, (xs, ESTEIRA_Y, 2.2), (FX + 14, ESTEIRA_Y, 2.2))
    pc.keyframe_insert("location", frame=f(S[3][0]))
tl = T(2, "linha")
visivel(novo, T(2, "meses") + 0.3); pop(novo, T(2, "meses") + 0.3, 1.0, 0.6)
destacar(mat((0.86, 0.87, 0.88, 1)), tl, (0.86, 0.87, 0.88, 1), dur=1.0)
shot(t0, T(2, "Motor") - 0.2, (FX - 2, FY - 40, 22), (FX, FY, 2), (FX - 4, FY - 36, 20), (FX - 2, FY, 2))
shot(T(2, "Motor") - 0.2, T(2, "meses") + 0.2, (FX - 30, FY - 22, 9), (FX - 10, ESTEIRA_Y, 2), (FX - 2, FY - 22, 9), (FX + 6, ESTEIRA_Y, 2))
shot(T(2, "meses") + 0.2, t1, (FX + 24, FY - 14, 6), (FX + 15, ESTEIRA_Y, 1.8), (FX + 22, FY - 11, 5), (FX + 16, ESTEIRA_Y, 1.8))

# ---------- S3: o buraco (estoque esvazia em semanas) ----------
t0, t1 = S[3]
tg = T(3, "gasta")
saem = estoque[:]; random.shuffle(saem)
saem = saem[:60]
for k, m in enumerate(saem):
    tt = tg + (T(3, "repor") - tg) * k / len(saem)
    m.scale = (1,) * 3; m.keyframe_insert("scale", frame=f(tt)); m.scale = (0.001,) * 3; m.keyframe_insert("scale", frame=f(tt + 0.2))
volta = saem[-1]
volta.scale = (0.001,) * 3; volta.keyframe_insert("scale", frame=f(T(3, "repor") + 0.4)); volta.scale = (1.0,) * 3; volta.keyframe_insert("scale", frame=f(T(3, "repor") + 0.8))
shot(t0, t1, (0, -36, 18), (0, 0, 2.5), (0, -30, 14), (0, 0, 2.5))

# ---------- S4: prazo de validade ----------
t0, t1 = S[4]
tenc = T(4, "encostado"); trv = T(4, "reavaliados"); tdp = T(4, "disparados")
visivel(tecnico, tenc, S[5][0]); andar(tecnico, tenc, trv, (-15, -12, 0.3), (-17, -15.5, 0.3))
visivel(scanner_luz, trv - 0.1, trv + 1.0)
scanner_luz.location = (-19.3, -18.6, 1.2); scanner_luz.keyframe_insert("location", frame=f(trv - 0.1))
scanner_luz.location = (-19.3, -12.4, 1.2); scanner_luz.keyframe_insert("location", frame=f(trv + 1.0))
mv = [m for k, m in _mats.items() if k[1] == "velho"][0]
cor_key(mv, 0, VELHO); cor_key(mv, trv + 0.3, VELHO); cor_key(mv, trv + 0.9, (0.36, 0.42, 0.26, 1))
for o in velhos:
    if o.name.startswith("poeira"): visivel(o, 0.01, trv + 0.6)
shot(t0, T(4, "chefe") - 0.1, (-8, -30, 8), (-18, -14, 1.5), (-12, -26, 6), (-19, -15, 1.5))
shot(T(4, "chefe") - 0.1, tdp - 0.2, (-13, -21, 3.6), (-19.5, -15.5, 1.3), (-14.5, -20, 3.4), (-19.5, -15.5, 1.3))
lancar(tdp, celulas[0], (NV[0] - 200, NV[1] + 260, 30), cor=VELHO)
lancar(tdp + 1.1, celulas[3], (NV[0] - 210, NV[1] + 280, 30), cor=VELHO)
shot(tdp - 0.2, t1, (NV[0] - 28, NV[1] - 6, 7), (NV[0], NV[1] + 15, 12), (NV[0] - 30, NV[1] - 10, 10), (NV[0], NV[1] + 15, 26))

# ---------- S5: a fila (um estoque para todos) ----------
t0, t1 = S[5]
tpt = T(5, "Pentágono"); ttr = T(5, "tropas"); tkv = T(5, "Kiev") - 0.2; tfl = T(5, "fila")
visivel(cam_entrega, tpt)
cam_entrega.location = (DP[0], DP[1] - 4, 1.0); cam_entrega.keyframe_insert("location", frame=f(ttr - 1.2))
cam_entrega.rotation_euler = (0, 0, math.radians(90)); cam_entrega.keyframe_insert("rotation_euler", frame=f(ttr - 1.2))
cam_entrega.location = (LA[0] + 12, DP[1], 1.0); cam_entrega.keyframe_insert("location", frame=f(ttr + 1.0))
for k, d in enumerate(drones):
    y0 = LB[1] + 120 + k * 8; x0 = LB[0] + 30 - k * 10
    visivel(d, tkv, t1 + 0.5)
    caminho(d, tkv, t1 + 0.5, lambda u, x0=x0, y0=y0: (x0 - 10 * u, y0 - 150 * u, 18 + 3 * math.sin(u * 6)), passo=3)
shot(t0, tpt - 0.1, (DP[0], DP[1] - 60, 34), (DP[0], DP[1] + 5, 1), (DP[0], DP[1] - 54, 30), (DP[0], DP[1] + 5, 1))
shot(tpt - 0.1, tkv, (DP[0] - 18, DP[1] - 26, 10), (DP[0] - 22, DP[1] + 2, 2), (DP[0] - 30, DP[1] - 24, 9), (LA[0] + 10, DP[1] + 2, 2))
shot(tkv, tfl - 0.2, (LB[0] - 8, LB[1] - 34, 8), (LB[0], LB[1] - 4, 8), (LB[0] - 4, LB[1] - 30, 7), (LB[0], LB[1], 12))
shot(tfl - 0.2, t1, (DP[0], DP[1] - 75, 44), (DP[0], DP[1] + 6, 0), (DP[0], DP[1] - 70, 46), (DP[0], DP[1] + 6, 0))

# ---------- S6: a guerra das fábricas ----------
t0, t1 = S[6]
ttp = T(6, "triplicou")
for k, (g, topo) in enumerate(extras):
    visivel(g, ttp - 0.2 + 0.3 * k); pop(g, ttp - 0.2 + 0.3 * k, 1.0, 0.45)
    fumaca(topo, ttp + 0.3 * k, t1 + 0.5, r=1.4, cada=0.6, sobe=9, vida=2.4)
fumaca((FX + 22, FY + 19, 20.5), t0, t1 + 0.5, r=1.6, cada=0.6)
esteira_m = []
for k in range(5):
    m = tomahawk(_id("est"), escala=0.8); visivel(m, t0, t1 + 0.5)
    a = (FX - 24 + k * 10, ESTEIRA_Y, 1.6); b = (FX - 24 + k * 10 + 22, ESTEIRA_Y, 1.6)
    m.rotation_euler = (0, 0, math.radians(-90)); andar(m, t0, t1 + 0.5, a, b)
    for fc in m.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
shot(t0, ttp - 0.2, (FX + 20, FY - 26, 9), (FX - 4, ESTEIRA_Y, 2), (FX + 10, FY - 26, 9), (FX - 10, ESTEIRA_Y, 2))
shot(ttp - 0.2, t1, (-60, -150, 40), (-92, -66, 4), (-110, -150, 44), (-92, -66, 4))

# ---------- S7-S8: parabéns + CTA + like ----------
t0, _ = S[7]
for k, m in enumerate(saem):   # arsenal remontado no "Parabéns"
    tt = t0 + 0.2 + 2.0 * k / len(saem)
    m.scale = (0.001,) * 3; m.keyframe_insert("scale", frame=f(tt)); m.scale = (1.0,) * 3; m.keyframe_insert("scale", frame=f(tt + 0.25))
shot(t0, S[8][0], (-10, -120, 70), (-30, 20, 0), (30, -110, 80), (0, 30, 0))
shot(S[8][0], FIM, (24, -34, 14), (0, 0, 2.5), (34, -26, 18), (0, 2, 2.5))

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
    emissivo("xis", VERMELHO, 1.2); emissivo("scan", VERDE, 4.0); emissivo("placa", (0.10, 0.55, 0.25, 1), 0.6)
    # mar com brilho
    mm = mar.data.materials[0].node_tree.nodes.get("Principled BSDF"); mm.inputs["Roughness"].default_value = 0.15
    # backlog 10: explosões/flash com emissão baixa e laranja mais escuro (não estoura para rosa no AgX)
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
