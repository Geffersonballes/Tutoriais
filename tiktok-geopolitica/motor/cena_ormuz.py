"""Vídeo 02 — 'Por que 33 km de mar podem parar o mundo' (Estreito de Ormuz). Uso:
REALISTA=1 blender -b --factory-startup -P cena_ormuz.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
import bpy, sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector, Matrix
from lowpoly import *

args = sys.argv[sys.argv.index("--") + 1:]
PASTA = args[0]
LEG = json.load(open(os.path.join(PASTA, "legendas.json"), encoding="utf-8"))
FIM = LEG[-1]["e"] + 1.3
NSEG = max(x["seg"] for x in LEG) + 1

def seg_ini(i): return 0.0 if i == 0 else min(x["s"] for x in LEG if x["seg"] == i) - 0.15
def seg_fim(i): return seg_ini(i + 1) if i < NSEG - 1 else FIM
def T(i, palavra, n=0):
    hits = [x["s"] for x in LEG if x["seg"] == i and palavra.lower() in x["w"].lower()]
    return hits[min(n, len(hits) - 1)]
S = [(seg_ini(i), seg_fim(i)) for i in range(NSEG)]

bpy.ops.wm.read_factory_settings(use_empty=True)
configurar_render()
scn = bpy.context.scene
scn.frame_start, scn.frame_end = 1, f(FIM)
random.seed(11)
W = scn.world; W.color = (0.30, 0.60, 0.95)

AREIA = (0.86, 0.74, 0.52, 1); AREIA2 = (0.78, 0.64, 0.44, 1); ROCHA = (0.62, 0.50, 0.38, 1)
MAR = (0.16, 0.44, 0.70, 1); FAIXA_IN = (0.30, 0.85, 1.0, 1); FAIXA_OUT = (1.0, 0.85, 0.20, 1)

# =====================================================================
# MAPA: Golfo Pérsico (oeste), Estreito (x≈15), Golfo de Omã (leste)
# =====================================================================
mar = caixa("mar", (0, 0, -0.3), (1400, 1400, 0.4), MAR)
iran = caixa("iran", (0, 240, 0.6), (1400, 430, 1.6), AREIA)              # costa norte em y = 25
arabia = caixa("arabia", (-420, -250, 0.6), (820, 420, 1.6), AREIA2)        # costa sul do Golfo em y = -40 (x < -10)
musandam = caixa("musandam", (15, -226, 0.6), (50, 468, 1.6), ROCHA)         # península: ponta em y = 8
oma = caixa("oma", (400, -290, 0.6), (720, 460, 1.6), AREIA2)              # costa do Golfo de Omã em y = -60 (x > 40)
mar_vermelho = caixa("marVermelho", (-700, -250, 0.85), (60, 420, 0.1), MAR)
for _ in range(45):  # montanhas do Irã e de Omã
    x = random.uniform(-300, 300); y = random.uniform(45, 200)
    m = esfera("serra", (x, y, -2), random.uniform(8, 22), random.choice([ROCHA, AREIA2]), sub=1); m.scale = (1.6, 1.0, 0.45)
for _ in range(14):
    x = random.uniform(-5, 35); y = random.uniform(-38, 0)
    m = esfera("rochaM", (x, y, 0), random.uniform(3, 7), ROCHA, sub=1); m.scale = (1, 1, 0.6)
for _ in range(20):
    x = random.uniform(60, 300); y = random.uniform(-200, -70)
    m = esfera("serraO", (x, y, -2), random.uniform(8, 18), ROCHA, sub=1); m.scale = (1.5, 1.0, 0.4)
# cidades portuárias (blocos pequenos) e porto de embarque
def cidade(cx, cy, n=12, r=6):
    for _ in range(n):
        h = random.uniform(1, 4)
        caixa("casaP", (cx + random.uniform(-r, r), cy + random.uniform(-r, r), 1.4 + h / 2), (1.5, 1.5, h), random.choice(PREDIOS))
cidade(-70, -48); cidade(20, 38, 10, 5); cidade(80, 34, 10, 5); cidade(75, -68, 8, 4); cidade(-160, 34, 10, 6)
porto = caixa("cais", (-70, -39, 1.2), (24, 3, 0.6), (0.5, 0.5, 0.52, 1))
for k in range(4):
    cilindro("tanqueP", (-80 + k * 6, -46, 3), 2.2, 3, (0.92, 0.92, 0.9, 1), seg=14)

# faixas de navegação no estreito (entrada = oeste, saída = leste)
def faixa(nome, y, cor):
    fx = caixa(nome, (20, y, 0.05), (260, 2.2, 0.05), cor, unico=nome); return fx
f_in = faixa("faixaEntrada", 19.5, FAIXA_IN); f_out = faixa("faixaSaida", 13.0, FAIXA_OUT)
regua = caixa("regua33", (15, 16.5, 1.2), (0.6, 17.5, 0.3), C["defesa"])

# câmera
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 24; cam_d.clip_end = 5000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def cam_key(t, loc, tgt):
    for ob, v in ((cam, loc), (alvo, tgt)):
        ob.location = v; ob.keyframe_insert("location", frame=f(t))
def corte(i, loc, tgt): cam_key(S[i][0], loc, tgt)

def navegar(ob, t0, t1, p0, p1):
    caminho(ob, t0, t1, lambda u: lerp(p0, p1, u))
def esteira(ob_fn, t0, t1):  # rastro branco de espuma atrás do barco
    rastro(ob_fn, t0, t1, (0.95, 0.97, 1.0, 1), r=0.35, cada=0.12, vida=1.6)

# frota permanente no estreito (aparece da cena 3 em diante)
frota = []
for k in range(5):
    pt = petroleiro(f"pFrotaIn{k}", escala=0.9); frota.append(pt)
    x0 = 120 - k * 40
    visivel(pt, S[3][0], S[4][1])
    navegar(pt, S[3][0], S[4][1], (x0, 19.5, 0.3), (x0 - 50, 19.5, 0.3))
for k in range(5):
    pt = petroleiro(f"pFrotaOut{k}", escala=0.9, cor_casco=(0.15, 0.22, 0.35, 1)); frota.append(pt)
    x0 = -100 + k * 40
    visivel(pt, S[3][0], S[4][1])
    navegar(pt, S[3][0], S[4][1], (x0, 13.0, 0.3), (x0 + 50, 13.0, 0.3))
visivel(f_in, S[3][0], S[5][0]); visivel(f_out, S[3][0], S[5][0]); pop(f_in, T(3, "faixas")); pop(f_out, T(3, "faixas") + 0.3)
visivel_janelas(f_in, [(T(3, "faixas"), S[5][0]), (S[9][0], S[10][1]), (S[11][0], FIM)])
visivel_janelas(f_out, [(T(3, "faixas") + 0.3, S[5][0]), (S[9][0], S[10][1]), (S[11][0], FIM)])
visivel(regua, T(3, "trinta"), T(3, "faixas") + 1.0); pop(regua, T(3, "trinta"))

# =====================================================================
# 0 — GANCHO: petroleiro atinge uma mina no estreito
# =====================================================================
t0, t1 = S[0]
p0 = petroleiro("pGancho", escala=1.4)
visivel(p0, t0, t1); navegar(p0, t0, t1, (40, 19.5, 0.3), (25, 19.5, 0.3))
p0.rotation_mode = "QUATERNION"
m0 = mina("minaGancho", 1.2); visivel(m0, t0, T(0, "explosões")); m0.location = (27, 21.5, 0.2)
explosao((27, 20.5, 1.5), T(0, "explosões"), r=9, n=22)
rastro(lambda u: (27 + u * 2, 20.5, 2 + u * 14), T(0, "explosões") + 0.2, t1, (0.25, 0.25, 0.27, 1), r=1.6, cada=0.1, vida=2.5)
cam_key(t0, (52, -2, 5), (28, 20, 2)); cam_key(t1 - 0.05, (46, 2, 7), (27, 20, 3))

# =====================================================================
# 1 — SUPERPETROLEIRO
# =====================================================================
t0, t1 = S[1]
p1 = petroleiro("pSuper", escala=1.6)
visivel(p1, t0, t1); navegar(p1, t0, t1, (-120, 0, 0.4), (-95, 0, 0.4))
esteira(lambda u: (-127 + 25 * u, 0, 0.3), t0, t1)
pop(p1, t0 + 0.1, escala=1.0, dur=0.4)
for k in range(6):  # barris "entrando" no navio
    b = barril(f"barrilCarga{k}", 0.5); tt = T(1, "milhões") - 0.6 + 0.15 * k
    visivel(b, tt, tt + 0.9)
    caminho(b, tt, tt + 0.8, lambda u, k=k: ((-108 + k * 1.5 + 3 * u), -8 + 8 * u, 9 - 8 * u), orientar=False)
destacar(p1.data.materials[0] if False else bpy.data.materials[p1.active_material.name], T(1, "Esses"), p1.active_material.diffuse_color[:])
corte(1, (-112, -16, 4), (-104, 0, 1.5))
cam_key(T(1, "enche"), (-100, -18, 5), (-100, 0, 1.5))
cam_key(t1 - 0.05, (-88, -14, 7), (-96, 0, 1.5))

# =====================================================================
# 2 — GOLFO FECHADO → ESTREITO
# =====================================================================
t0, t1 = S[2]
for k in range(3):
    tt = T(2, "corredor") + 0.45 * k
    o = anel(f"pulsoEstreito{k}", (15, 16.5, 1.5), 22, 0.5, C["defesa"], seg=48)
    visivel(o, tt, tt + 1.2); o.scale = (0.05,) * 3; o.keyframe_insert("scale", frame=f(tt)); o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(tt + 1.2))
seta_ir = seta3d("setaIra", 10, C["ameaca"]); seta_ir.location = (15, 45, 2); visivel(seta_ir, T(2, "Irã"), t1); pop(seta_ir, T(2, "Irã"))
seta_om = seta3d("setaOma", 10, (0.25, 0.55, 1.0, 1)); seta_om.location = (15, -15, 2); visivel(seta_om, T(2, "Omã"), t1); pop(seta_om, T(2, "Omã"))
corte(2, (-160, -260, 260), (-120, 0, 0))
cam_key(T(2, "corredor"), (-40, -170, 190), (10, 10, 0))
cam_key(t1 - 0.05, (10, -110, 120), (15, 15, 0))

# =====================================================================
# 3 — 33 KM e DUAS FAIXAS (frota já navegando)
# =====================================================================
t0, t1 = S[3]
corte(3, (15, -45, 55), (15, 16, 0))
cam_key(T(3, "faixas"), (40, -30, 38), (15, 16, 0))
cam_key(T(3, "quinto"), (70, -20, 30), (10, 16, 0))
cam_key(t1 - 0.05, (85, -5, 26), (0, 16, 0))

# =====================================================================
# 4 — NEGAÇÃO DE ÁREA: barcos rápidos, minas, mísseis na costa
# =====================================================================
t0, t1 = S[4]
for k in range(4):
    b = barco_rapido(f"rapido{k}", 1.3); tb = T(4, "barcos") - 0.3 + 0.2 * k
    p_a = (5 + k * 9, 30, 0.3); p_b = (0 + k * 11, 21.5, 0.3)
    visivel(b, tb, t1); caminho(b, tb, tb + 1.6, lambda u, a=p_a, c=p_b: lerp(a, c, suave(u)))
    esteira(lambda u, a=p_a, c=p_b: lerp(a, c, suave(u)), tb, tb + 1.6)
for k in range(7):
    m = mina(f"minaC{k}", 0.9); tm = T(4, "minas") + 0.12 * k
    m.location = (-20 + k * 9, random.choice([19.5, 13.0]) + random.uniform(-0.6, 0.6), 0.25)
    visivel(m, tm, S[5][1]); pop(m, tm)
for k in range(3):
    lc, lt = caminhao(f"lancCosta{k}", (0 + k * 14, 32, 2.3)); lc.rotation_euler = (0, 0, math.radians(180))
    visivel(lc, T(4, "mísseis"), t1); pop(lc, T(4, "mísseis") + 0.15 * k)
corte(4, (20, -8, 12), (18, 26, 2))
cam_key(T(4, "minas"), (10, -2, 14), (12, 18, 0))
cam_key(T(4, "mísseis"), (8, 8, 12), (8, 32, 3))
cam_key(t1 - 0.05, (5, 4, 18), (10, 25, 2))

# =====================================================================
# 5 — SEGURO DE GUERRA: navios parados no porto, custo sobe
# =====================================================================
t0, t1 = S[5]
parados = []
for k in range(3):
    pt = petroleiro(f"pParado{k}", escala=1.0); pt.location = (-82 + k * 12, -33, 0.3); pt.rotation_euler = (0, 0, math.radians(90))
    visivel(pt, t0, t1); parados.append(pt)
moedas = []
for k in range(12):
    mo = cilindro(f"moedaS{k}", (-58, -28, 1.6 + 0.45 * k), 1.6, 0.4, (1.0, 0.78, 0.15, 1), seg=12)
    tt = T(5, "seguro") + 0.12 * k; visivel(mo, tt, t1); pop(mo, tt, dur=0.2)
seta_s = seta3d("setaSeguro", 9, C["ameaca"]); seta_s.location = (-52, -28, 1.5); visivel(seta_s, T(5, "dispara"), t1); pop(seta_s, T(5, "dispara"))
corte(5, (-74, -8, 12), (-66, -32, 3))
cam_key(T(5, "armadores"), (-64, -10, 11), (-62, -30, 4))
cam_key(t1 - 0.05, (-54, -12, 12), (-58, -29, 5))

# =====================================================================
# 6 — PREÇO SOBE: barril gigante e bomba de combustível (palco à parte)
# =====================================================================
t0, t1 = S[6]
PX = 3000
palco = caixa("palcoPreco", (PX, 0, -0.5), (200, 200, 1.0), (0.85, 0.82, 0.76, 1))
bg = barril("barrilGigante", 2.2); bg.location = (PX - 3, 0, 2.9)
bomba = bomba_combustivel("bomba"); bomba.location = (PX + 6, 1, 0)
sp = seta3d("setaPreco", 12, C["ameaca"]); sp.location = (PX + 1.5, -2, 0)
for o in (palco, bg, bomba, sp): visivel(o, t0, t1)
pop(bg, t0 + 0.1); pop(bomba, T(6, "Brasil") - 0.3)
sp.scale = (1, 1, 0.05); sp.keyframe_insert("scale", frame=f(T(6, "preço") - 0.05)); sp.scale = (1, 1, 1); sp.keyframe_insert("scale", frame=f(T(6, "preço") + 0.8))
cam_key(t0, (PX - 4, -20, 6), (PX, 0, 4)); cam_key(t1 - 0.05, (PX + 6, -16, 5), (PX + 2, 0, 4))

# =====================================================================
# 7 — OLEODUTOS DE DESVIO (crescem sobre a Arábia e os Emirados)
# =====================================================================
t0, t1 = S[7]
def duto(nome, a, b, t):
    d = cilindro(nome, (0, 0, 0), 3.2, 1, (0.92, 0.92, 0.96, 1), seg=10, unico=nome)
    d.data.transform(Matrix.Translation((0, 0, 0.5))); d.data.transform(Matrix.Rotation(math.radians(-90), 4, "X"))
    va = Vector(a); vb = Vector(b); dv = vb - va
    d.location = va; d.rotation_mode = "QUATERNION"; d.rotation_quaternion = dv.to_track_quat("Y", "Z")
    d.scale = (1, 0.001, 1); d.keyframe_insert("scale", frame=f(t)); d.scale = (1, dv.length, 1); d.keyframe_insert("scale", frame=f(t + 1.6))
    return d
d_sa = duto("dutoSaudita", (-80, -50, 2.6), (-670, -120, 2.6), T(7, "Arábia"))
d_ea = duto("dutoEmirados", (-25, -48, 2.6), (75, -62, 2.6), T(7, "Emirados"))
for d in (d_sa, d_ea):
    visivel_janelas(d, [(S[7][0], S[8][1]), (S[11][0], FIM)])
destacar(d_sa.data.materials[0], T(7, "Esses"), (0.92, 0.92, 0.96, 1)); destacar(d_ea.data.materials[0], T(7, "Esses"), (0.92, 0.92, 0.96, 1))
corte(7, (-250, -260, 170), (-260, -90, 0))
cam_key(T(7, "Emirados"), (-10, -150, 90), (15, -55, 0))
cam_key(t1 - 0.05, (-110, -260, 170), (-150, -75, 0))

# =====================================================================
# 8 — SÓ UMA PEQUENA PARTE: fila de petroleiros x duto fino
# =====================================================================
t0, t1 = S[8]
for k in range(14):
    pt = petroleiro(f"pFila{k}", escala=0.9); pt.location = (-30 - (k % 7) * 11, 4 + (k // 7) * 8, 0.3); pt.rotation_euler = (0, 0, math.radians(-90))
    visivel(pt, t0, t1)
corte(8, (-40, -60, 45), (-55, 2, 0))
cam_key(t1 - 0.05, (-20, -55, 35), (-50, 0, 0))

# =====================================================================
# 9 — COMBOIO e CAÇA-MINAS
# =====================================================================
t0, t1 = S[9]
comb = []
for k in range(3):
    pt = petroleiro(f"pComboio{k}", escala=1.0); comb.append(pt)
    visivel(pt, t0, t1); navegar(pt, t0, t1, (-40 - k * 14, 13.0, 0.3), (10 - k * 14, 13.0, 0.3))
    esteira(lambda u, k=k: (-46 - k * 14 + 50 * u, 13.0, 0.3), t0, t1)
for k, dy in enumerate((-3.5, 3.5)):
    ng = navio_guerra(f"fragata{k}", 1.0)
    visivel(ng, T(9, "escoltam") - 0.2, t1); navegar(ng, t0, t1, (-46, 13.0 + dy, 0.3), (4, 13.0 + dy, 0.3))
    esteira(lambda u, dy=dy: (-50 + 50 * u, 13.0 + dy, 0.3), T(9, "escoltam"), t1)
cm = navio_guerra("cacaMinas", 0.6); visivel(cm, T(9, "caça") - 0.3, t1); navegar(cm, t0, t1, (-15, 13.0, 0.3), (32, 13.0, 0.3))
mc = mina("minaComboio", 0.9); mc.location = (22, 13.2, 0.25); visivel(mc, t0, T(9, "caminho") + 0.4)
explosao((22, 13.2, 1.0), T(9, "caminho") + 0.4, r=6, n=14)
corte(9, (-24, -3, 5), (-18, 13, 1))
cam_key(T(9, "caça"), (2, -2, 6), (14, 13, 1))
cam_key(t1 - 0.05, (14, 0, 7), (8, 13, 1))

# =====================================================================
# 10 — DISSUASÃO: o petroleiro do próprio Irã também precisa passar
# =====================================================================
t0, t1 = S[10]
pir = petroleiro("pIra", escala=1.2, cor_casco=(0.20, 0.45, 0.30, 1))
visivel(pir, t0, t1); navegar(pir, t0, T(10, "Fechar"), (-60, 13.0, 0.3), (-8, 13.0, 0.3))
pir.keyframe_insert("location", frame=f(t1))
barreira = caixa("barreira", (15, 16.5, 1.5), (1.5, 18, 3.0), C["ameaca"], unico="barreira")
visivel(barreira, T(10, "Fechar"), T(10, "ameaça")); pop(barreira, T(10, "Fechar"))
for k in range(3):
    tt = T(10, "ameaça") + 0.4 * k
    o = anel(f"pulsoDiss{k}", (15, 16.5, 1.5), 30, 0.5, C["ameaca"], seg=48)
    visivel(o, tt, tt + 1.2); o.scale = (0.05,) * 3; o.keyframe_insert("scale", frame=f(tt)); o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(tt + 1.2))
corte(10, (-30, -30, 26), (-10, 14, 0))
cam_key(T(10, "Fechar"), (-5, -28, 22), (5, 15, 0))
cam_key(t1 - 0.05, (10, -40, 40), (12, 16, 0))

# =====================================================================
# 11/12 — FINAL: o mapa inteiro com tráfego e dutos
# =====================================================================
t0 = S[11][0]; tF = FIM
for k in range(6):
    pt = petroleiro(f"pFinal{k}", escala=0.9, cor_casco=random.choice([(0.55, 0.12, 0.10, 1), (0.15, 0.22, 0.35, 1)]))
    y = 19.5 if k % 2 else 13.0; d = -1 if k % 2 else 1
    x0 = -60 + k * 25
    visivel(pt, t0, tF); navegar(pt, t0, tF, (x0, y, 0.3), (x0 + d * 30, y, 0.3))
cam_key(t0, (-60, -170, 140), (0, 0, 0)); cam_key(S[12][0], (20, -150, 120), (10, 5, 0)); cam_key(tF, (70, -120, 100), (15, 10, 0))

# ---------- render ----------
if os.environ.get("REALISTA"):
    modo_realista(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "hdri", "ceu_parcialmente_nublado_2k.hdr"), foco=alvo)
    # mar com variação de cor e leve brilho
    mm = mar.data.materials[0]; b = mm.node_tree.nodes.get("Principled BSDF")
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
