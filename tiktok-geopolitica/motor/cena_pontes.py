"""Vídeo 03 — 'Por que todo mundo mira nas pontes?' Uso:
REALISTA=1 blender -b --factory-startup -P cena_pontes.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
import bpy, sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowpoly import *
from lowpoly import _id

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
random.seed(5)
scn.world.color = (0.30, 0.60, 0.95)

RIO = (0.18, 0.46, 0.72, 1); CONC = (0.78, 0.78, 0.76, 1); PILAR = (0.62, 0.62, 0.60, 1)
CAIXOTE = (0.55, 0.42, 0.20, 1)

# ---------------- terreno: rio leste-oeste, margem norte (frente) e sul (retaguarda) ----------------
rio = caixa("rio", (0, 0, -0.6), (600, 44, 0.4), RIO)
norte = caixa("margemN", (0, 172, 0.4), (600, 300, 2.0), C["grama"])
sul = caixa("margemS", (0, -172, 0.4), (600, 300, 2.0), C["grama2"])
for y in (34, -34):
    caixa("ruaM", (0, y, 1.45), (600, 5, 0.1), C["rua"])
for _ in range(40):
    x = random.uniform(-150, 150); y = random.choice([1, -1]) * random.uniform(45, 110)
    if abs(x + 30) > 8 and abs(x - 30) > 8 and abs(x) > 6:
        predio((x, y), random.uniform(5, 8), random.uniform(5, 8), random.uniform(5, 20), random.choice(PREDIOS)).location.z += 1.4
for _ in range(30):
    arvore((random.uniform(-160, 160), random.choice([1, -1]) * random.uniform(24, 30)), random.uniform(0.7, 1.1)).location.z += 1.4

def ponte(nome, x, nseg=6):
    segs = []
    L = 56 / nseg
    for k in range(nseg):
        y = -28 + L * (k + 0.5)
        s = caixa(f"{nome}_d{k}", (x, y, 3.2), (9, L + 0.05, 1.0), CONC)
        filho(s, caixa(f"{nome}_g{k}", (4.3, 0, 0.9), (0.4, L, 0.8), PILAR), caixa(f"{nome}_h{k}", (-4.3, 0, 0.9), (0.4, L, 0.8), PILAR))
        segs.append(s)
    for y in (-14, 0, 14):
        cilindro(f"{nome}_p", (x, y, 0.8), 1.6, 4.4, PILAR, seg=10)
    return segs
pA = ponte("ponteA", -30); pB = ponte("ponteB", 30)

def cai(seg, t):  # segmento despenca no rio
    seg.rotation_mode = "XYZ"
    key(seg, "location", t, tuple(seg.location)); key(seg, "rotation_euler", t, (0, 0, 0))
    l = seg.location
    key(seg, "location", t + 0.9, (l[0], l[1], -2.2)); key(seg, "rotation_euler", t + 0.9, (math.radians(25), math.radians(8), 0))

def veiculo(nome, cor, caminhao_=False):
    if caminhao_:
        c, _ = caminhao(nome, (0, 0, 0), cor=cor, tubos=False)
        filho(c, caixa(nome + "_carga", (0, -1.0, 1.2), (2.2, 4.0, 1.6), CAIXOTE))
        return c
    car = caixa(nome, (0, 0, 0), (1.8, 3.6, 1.1), cor)
    filho(car, caixa(nome + "_v", (0, -0.2, 0.8), (1.6, 1.8, 0.6), (0.2, 0.25, 0.3, 1)))
    return car

def travessia(ob, x, t0, t1, dir_=1, z=4.3, ciclos=1):
    caminho(ob, t0, t1, lambda u: (x + (1.8 if dir_ > 0 else -1.8), -dir_ * 34 + dir_ * 68 * ((u * ciclos) % 1), z), passo=2)

def missil_em(alvo_xyz, t_imp, origem=(-200, 220, 90)):
    m = missil(_id("mis"), escala=1.2)
    visivel(m, t_imp - 1.2, t_imp)
    caminho(m, t_imp - 1.2, t_imp, lambda u: bez(origem, ((origem[0] + alvo_xyz[0]) / 2, (origem[1] + alvo_xyz[1]) / 2, origem[2] + 30), alvo_xyz, u), passo=1)
    rastro(lambda u: bez(origem, ((origem[0] + alvo_xyz[0]) / 2, (origem[1] + alvo_xyz[1]) / 2, origem[2] + 30), alvo_xyz, u), t_imp - 1.2, t_imp, (0.9, 0.9, 0.9, 1), r=0.8)
    explosao(alvo_xyz, t_imp, r=8, n=20)

# câmera
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 26; cam_d.clip_end = 3000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def cam_key(t, loc, tgt):
    for ob, v in ((cam, loc), (alvo, tgt)):
        ob.location = v; ob.keyframe_insert("location", frame=f(t))

# =====================================================================
# 0 — GANCHO: duas pontes atingidas na mesma noite (cópias que caem; as pontes "reais" voltam na cena 1)
# =====================================================================
t0, t1 = S[0]
tA = T(0, "pontes") + 0.2; tB = tA + 0.9
for segs in (pA, pB):
    for s in segs: visivel(s, S[1][0])  # as pontes inteiras só aparecem a partir da cena 1
for nome, x, ti in (("gA", -30, tA), ("gB", 30, tB)):
    gs = ponte(nome, x)
    for s in gs: visivel(s, 0, S[1][0])
    missil_em((x, 0, 4), ti)
    cai(gs[2], ti); cai(gs[3], ti + 0.1)
cam_key(t0, (50, -62, 26), (0, 0, 3)); cam_key(t1 - 0.05, (34, -54, 22), (0, 0, 3))

# =====================================================================
# 1 — artérias: tráfego nas duas pontes
# =====================================================================
t0, t1 = S[1]
cores = [C["ameaca"], C["ciano"], C["branco"], C["defesa"], C["azulmarinho"], (0.95, 0.95, 0.95, 1)]
for x in (-30, 30):
    for k in range(6):
        v = veiculo(_id("v"), random.choice(cores), caminhao_=(k % 3 == 0))
        d = 1 if k % 2 else -1
        visivel(v, t0, S[2][0] if x == 30 else S[4][0])
        travessia(v, x, t0 - k * 0.9, S[4][0], d, ciclos=4)
amb = veiculo("ambul", (1, 1, 1, 1)); filho(amb, caixa("cruz", (0, 0, 0.9), (0.4, 1.2, 0.2), C["ameaca"]))
visivel(amb, T(1, "ambulâncias") - 0.5, S[2][0]); travessia(amb, 30, T(1, "ambulâncias") - 1.5, S[2][0], 1, ciclos=2)
cam_key(t0, (-80, -60, 40), (0, 0, 3)); cam_key(T(1, "caminhões"), (55, -40, 14), (30, 0, 4)); cam_key(t1 - 0.05, (60, -30, 12), (30, 0, 4))

# =====================================================================
# 2 — a ponte B cai: fila e desvio
# =====================================================================
t0, t1 = S[2]
tc2 = T(2, "cai")
missil_em((30, 0, 4), tc2)
for k in (2, 3): cai(pB[k], tc2 + 0.05 * k)
for k in range(12):  # fila parada na margem sul
    v = veiculo(_id("fila"), random.choice(cores))
    visivel(v, tc2 + 0.5, S[3][0])
    pos = (32 - 0, -36 - k * 4.4, 2.0) if k < 6 else (36 + (k - 6) * 4.4, -36, 2.0)
    v.location = pos
    if k >= 6: v.rotation_euler = (0, 0, math.radians(90))
    pop(v, tc2 + 0.5 + 0.12 * k)
desvio = seta3d("desvio", 30, C["defesa"]); desvio.rotation_euler = (0, math.radians(-90), 0); desvio.location = (26, -40, 6)
visivel(desvio, T(2, "volta"), S[3][0]); pop(desvio, T(2, "volta"))
cam_key(t0, (60, -30, 12), (30, 0, 4)); cam_key(tc2 + 0.6, (75, -70, 30), (30, -20, 2)); cam_key(t1 - 0.05, (70, -80, 36), (28, -28, 2))

# =====================================================================
# 3 — linha de suprimento: caminhões de munição pela ponte A até a frente (norte)
# =====================================================================
t0, t1 = S[3]
frente = []
for k in range(6):
    b, _, _ = boneco(_id("sold"), (-40 + k * 4, 60, 1.4)); frente.append(b); visivel(b, t0, S[8][0])
for k in range(2):
    cn = canhao(_id("can"), (-50 + k * 40, 66, 2.0)); visivel(cn, t0, S[8][0])
caixotes = []
for k in range(8):
    cx = caixa(_id("cxM"), (-36 + (k % 4) * 3, 52 + (k // 4) * 3, 2.4), (2.2, 2.2, 1.8), CAIXOTE); caixotes.append(cx)
    visivel(cx, T(3, "bala") + 0.3 * k, S[4][1]); pop(cx, T(3, "bala") + 0.3 * k)
comb = []
for k in range(4):
    sup = veiculo(_id("sup"), C["oliva"], caminhao_=True); comb.append(sup)
    visivel(sup, t0, S[4][0] + 1.4)
    caminho(sup, t0 + k * 1.8, S[4][0] + 1.4, lambda u, k=k: (-28.2, -70 + 120 * u, 4.3 if -30 < -70 + 120 * u < 30 else 2.6), passo=2)
cam_key(t0, (-90, -40, 40), (-30, 10, 3)); cam_key(T(3, "combustível"), (-70, 20, 26), (-30, 30, 3)); cam_key(t1 - 0.05, (-60, 30, 30), (-30, 48, 3))

# =====================================================================
# 4 — interdição: cortar a ponte A; a frente fica sem munição
# =====================================================================
t0, t1 = S[4]
tcorte = T(4, "cortar")
missil_em((-30, 0, 4), tcorte)
for k in (2, 3): cai(pA[k], tcorte + 0.05 * k)
for k, cx in enumerate(caixotes):
    sumir(cx, T(4, "munição") + 0.2 * k)
cam_key(t0, (-80, -70, 40), (-30, 0, 3)); cam_key(tcorte + 0.8, (-70, -50, 30), (-30, 10, 3)); cam_key(T(4, "munição"), (-55, 20, 22), (-32, 54, 2)); cam_key(t1 - 0.05, (-50, 26, 20), (-32, 56, 2))

# =====================================================================
# 5 — respostas: ponte flutuante, balsa e defesa antiaérea
# =====================================================================
t0, t1 = S[5]
tfl = T(5, "flutuantes"); tbal = T(5, "balsas"); tdef = T(5, "antiaérea")
for k in range(9):
    pf = caixa(_id("pont"), (0, -20 + k * 5, 0.2), (7, 4.6, 1.0), C["oliva"])
    visivel(pf, tfl - 0.3 + 0.18 * k); pop(pf, tfl - 0.3 + 0.18 * k)
balsa = caixa("balsa", (0, 0, 0.3), (8, 12, 0.8), C["oliva"]); visivel(balsa, tbal - 0.2)
filho(balsa, veiculo("balsaCam", C["oliva"], caminhao_=True)); balsa.children[0].location = (0, 0, 1.2)
caminho(balsa, tbal - 0.2, FIM, lambda u: (-70 + 0 * u, -16 + 32 * ((u * 3) % 1), 0.3), orientar=False, passo=3)
rd = radar("radarP", (-48, -42, 1.4)); rd = rd[0] if isinstance(rd, tuple) else rd; visivel(rd, tdef - 0.3); pop(rd, tdef - 0.3)
for k, x in enumerate((-12, 12)):
    cn = canhao(_id("aa"), (x, -40, 2.0)); visivel(cn, tdef + 0.15 * k); pop(cn, tdef + 0.15 * k)
cam_key(t0, (40, -60, 26), (0, 0, 2)); cam_key(tbal, (-30, -70, 30), (-30, -6, 2)); cam_key(tdef, (10, -80, 30), (-10, -30, 4)); cam_key(t1 - 0.05, (20, -86, 34), (-6, -24, 4))

# =====================================================================
# 6 — ponte da Crimeia: ligação longa sobre o mar (outro cenário, ao leste)
# =====================================================================
t0, t1 = S[6]
mar = caixa("marC", (600, 0, -0.5), (300, 300, 0.4), RIO); visivel(mar, t0, t1)
tL = caixa("terraRu", (480, 0, 0.4), (60, 300, 2.0), C["grama2"]); visivel(tL, t0, t1)
tR = caixa("terraCr", (720, 0, 0.4), (60, 300, 2.0), C["grama"]); visivel(tR, t0, t1)
for k in range(18):
    s = caixa(_id("crm"), (515 + k * 10, 0, 3.0), (10.05, 7, 0.9), CONC); visivel(s, t0, t1)
    if k % 3 == 0:
        p = cilindro(_id("crp"), (515 + k * 10, 0, 0.6), 1.3, 4.6, PILAR, seg=8); visivel(p, t0, t1)
sc = seta3d("setaCr", 160, C["ameaca"]); sc.rotation_euler = (0, math.radians(90), 0); sc.location = (520, -14, 8)
visivel(sc, T(6, "liga") - 0.2, t1); pop(sc, T(6, "liga") - 0.2)
cam_key(t0, (540, -48, 16), (580, 0, 3)); cam_key(t1 - 0.05, (600, -52, 20), (640, 0, 3))

# =====================================================================
# 7/8 — final: visão geral
# =====================================================================
cam_key(S[7][0], (-120, -150, 90), (0, 10, 0)); cam_key(FIM, (-60, -170, 100), (0, 10, 0))

# ---------- render ----------
if os.environ.get("REALISTA"):
    modo_realista(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "hdri", "ceu_parcialmente_nublado_2k.hdr"), foco=alvo)
    m = rio.data.materials[0]; b = m.node_tree.nodes.get("Principled BSDF")
    if b: b.inputs["Roughness"].default_value = 0.25
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
