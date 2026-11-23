"""Vídeo 01 — 'Você construiu uma defesa antiaérea'. Uso:
blender -b --factory-startup -P cena_defesa.py -- <pasta_producao> [preview t1,t2,...]"""
import bpy, sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
from lowpoly import *

args = sys.argv[sys.argv.index("--") + 1:]
PASTA = args[0]
LEG = json.load(open(os.path.join(PASTA, "legendas.json"), encoding="utf-8"))
FIM = LEG[-1]["e"] + 1.3

def seg_ini(i): return 0.0 if i == 0 else min(x["s"] for x in LEG if x["seg"] == i) - 0.15
def seg_fim(i): return seg_ini(i + 1) if i < 12 else FIM
def T(i, palavra, n=0):
    hits = [x["s"] for x in LEG if x["seg"] == i and palavra.lower() in x["w"].lower()]
    return hits[min(n, len(hits) - 1)]
S = [(seg_ini(i), seg_fim(i)) for i in range(13)]

bpy.ops.wm.read_factory_settings(use_empty=True)
configurar_render()
scn = bpy.context.scene
scn.frame_start, scn.frame_end = 1, f(FIM)
random.seed(7)
W = scn.world
CEU = (0.30, 0.60, 0.95, 1); NOITE = (0.06, 0.09, 0.20, 1)
W.color = CEU[:3]

# =====================================================================
# PALCO A — a cidade (origem)
# =====================================================================
chao = caixa("chao", (0, 0, -0.25), (600, 600, 0.5), C["grama"])
for x in range(-3, 4):
    caixa(f"ruaX{x}", (x * 9, 0, 0.02), (1.6, 66, 0.05), C["rua"]); caixa(f"ruaY{x}", (0, x * 9, 0.02), (66, 1.6, 0.05), C["rua"])
rio = caixa("rio", (0, 48, 0.03), (300, 7, 0.05), C["agua"])
for gx in range(-3, 3):
    for gy in range(-3, 3):
        cx, cy = gx * 9 + 4.5, gy * 9 + 4.5
        if abs(cx) < 5 and abs(cy) < 5: continue  # praça central (comando)
        for _ in range(random.choice([1, 2, 2, 3])):
            w, d = random.uniform(2.5, 4), random.uniform(2.5, 4)
            predio((cx + random.uniform(-2, 2), cy + random.uniform(-2, 2)), w, d, random.uniform(2.5, 9), random.choice(PREDIOS))
for _ in range(110):
    a = random.uniform(0, 2 * math.pi); r = random.uniform(32, 110)
    p = (r * math.cos(a), r * math.sin(a))
    if abs(p[1] - 48) < 5: continue
    arvore(p, random.uniform(0.9, 1.6))
for _ in range(14):
    a = random.uniform(0, 2 * math.pi); r = random.uniform(170, 260)
    m = esfera("morro", (r * math.cos(a), r * math.sin(a), -8), random.uniform(25, 45), C["morro"], sub=1); m.scale = (1.4, 1.4, 0.6)
nuvens = []
for i in range(10):
    n = nuvem((random.uniform(-120, 120), random.uniform(-60, 160), random.uniform(55, 75)), random.uniform(1.5, 2.6))
    n.keyframe_insert("location", frame=1); n.location.x += 25; n.keyframe_insert("location", frame=f(FIM))
    for fc in n.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
    nuvens.append(n)

# instalações fixas da defesa
RADAR_POS = (-24, -12, 0); LANC_POS = (24, -10, 0.9); LASER_POS = (12, 26, 0); CANHAO_POS = (-16, 24, 0)
rad, rad_gir = radar("radarA", (RADAR_POS[0], RADAR_POS[1], 0.75))
rad_gir.rotation_euler = (0, 0, 0); rad_gir.keyframe_insert("rotation_euler", frame=1)
rad_gir.rotation_euler = (0, 0, math.radians(360 * FIM / 3)); rad_gir.keyframe_insert("rotation_euler", frame=f(FIM))
for fc in rad_gir.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
lanc, lanc_t = caminhao("lancA", LANC_POS); lanc.rotation_euler = (0, 0, math.radians(200))
laser = torre_laser("laserA", (LASER_POS[0], LASER_POS[1], 0.6))
canh = canhao("canhaoA", (CANHAO_POS[0], CANHAO_POS[1], 0.5))
hexa = cilindro("comando", (0, 0, 1.0), 3.2, 2.0, C["azulmarinho"], seg=6, unico="hexa")
antena = cilindro("antenaCmd", (0, 0, 2.5), 0.12, 3.0, C["cinza"], seg=5); filho(hexa, antena); antena.location = (0, 0, 2.5)

# quando cada instalação aparece
visivel(rad, S[1][0] + 0.1)
pop(rad, T(1, "Então"))
visivel(lanc, S[4][0])
visivel(canh, S[4][0])
visivel(laser, T(6, "laser") - 0.4); pop(laser, T(6, "laser") - 0.4)
visivel(hexa, T(9, "centro") - 0.6); pop(hexa, T(9, "centro") - 0.6)

def barra_y(nome, r, cor):
    b = cilindro(nome, (0, 0, 0), r, 1, cor, seg=6)
    b.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 0.5)))
    b.data.transform(__import__("mathutils").Matrix.Rotation(math.radians(-90), 4, "X"))
    return b

# câmera
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 24; cam_d.clip_end = 3000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"

def cam_key(t, loc, tgt, interp="BEZIER"):
    for ob, v in ((cam, loc), (alvo, tgt)):
        ob.location = v; ob.keyframe_insert("location", frame=f(t))
        for fc in ob.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                if int(kp.co[0]) == f(t): kp.interpolation = interp

def corte(i, loc, tgt):
    """Corte seco no início da cena i."""
    cam_key(S[i][0], loc, tgt)

# =====================================================================
# 0 — GANCHO: interceptador caro x drone barato
# =====================================================================
t0, t1 = S[0]
dr = drone("drone0", 3.0)
visivel(dr, 0, T(0, "derrubar") + 1.4)
P_HIT = (6, 10, 26)
caminho(dr, 0, T(0, "derrubar") + 1.2, lambda u: lerp((-50, 25, 27), (6, 10, 26), u))
it0 = missil("inter0", C["branco"])
visivel(it0, T(0, "milhões") - 0.2, T(0, "derrubar") + 1.2)
f_it0 = lambda u: bez((LANC_POS[0], LANC_POS[1], 3), (20, -2, 30), P_HIT, suave(u))
caminho(it0, T(0, "milhões") - 0.2, T(0, "derrubar") + 1.2, f_it0)
rastro(f_it0, T(0, "milhões") - 0.2, T(0, "derrubar") + 1.2)
visivel(lanc, 0, S[0][1])  # o lançador já aparece no gancho
explosao(P_HIT, T(0, "derrubar") + 1.2, r=6)
cam_key(0, (36, -26, 30), (4, 8, 24)); cam_key(t1 - 0.05, (28, -18, 32), (5, 10, 25))

# =====================================================================
# 1 — RADAR
# =====================================================================
t0, t1 = S[1]
corte(1, (-2, -50, 14), (10, 10, 14))
cam_key(T(1, "Então"), (-10, -48, 12), (-18, -8, 6))
cam_key(t1 - 0.05, (-38, -36, 14), (-22, -10, 6))
m1 = missil("missil1")
visivel(m1, t0 + 0.2, t1)
caminho(m1, t0 + 0.2, t1, lambda u: lerp((60, 70, 26), (12, 22, 18), u))
for k in range(4):
    tt = T(1, "grita") + k * 0.75
    o = anel(f"onda{k}", (RADAR_POS[0], RADAR_POS[1], 5.0), 70, 0.5, C["ciano"], seg=64)
    visivel(o, tt, tt + 1.4)
    o.scale = (0.02,) * 3; o.keyframe_insert("scale", frame=f(tt)); o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(tt + 1.4))
mpos = Vector(lerp((60, 70, 26), (12, 22, 18), (T(1, "eco") - t0) / (t1 - t0)))
for k in range(3):
    tt = T(1, "eco") + k * 0.35
    o = anel(f"eco{k}", tuple(mpos), 16, 0.5, C["ameaca"], seg=32); o.rotation_euler = (math.radians(80), 0, math.radians(-30))
    visivel(o, tt, tt + 1.0)
    o.scale = (0.05,) * 3; o.keyframe_insert("scale", frame=f(tt)); o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(tt + 1.0))
destacar(rad.data.materials[0], T(1, "Esse"), C["cinza"])

# =====================================================================
# 2 — HORIZONTE / AVIÃO-RADAR (palco B, x=2000)
# =====================================================================
t0, t1 = S[2]
BX = 2000; R = 60
terra = esfera("terra", (BX, 0, 0), R, C["grama"], sub=3)
mar = esfera("terra_mar", (BX, 0, 0), R - 0.4, C["agua"], sub=3)
visivel(terra, t0, t1); visivel(mar, t0, t1)
for k in range(30):
    a = math.radians(random.uniform(-60, 60)); b = math.radians(random.uniform(-25, 25))
    p = Vector((BX + R * math.sin(a) * math.cos(b), R * math.sin(b), R * math.cos(a) * math.cos(b)))
    tr = arvore((0, 0), 1.4); tr.location = p; tr.rotation_euler = (b * -1, a, 0); visivel(tr, t0, t1)
rB, _ = radar("radarB", (0, 0, 0)); rB.location = (BX - 18, 0, math.sqrt(R ** 2 - 18 ** 2)); rB.rotation_euler = (0, math.radians(-17.5), 0)
visivel(rB, t0, t1)
feixe = cilindro("feixe", (0, 0, 0), 0.25, 1, C["defesa"], seg=6)
feixe.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 0.5)))
feixe.location = (rB.location.x, 0, rB.location.z + 3)
feixe.rotation_euler = (0, math.radians(107.5), 0); feixe.scale = (1, 1, 140)
visivel(feixe, t0 + 0.6, T(2, "Então"))
def f_m2(u):
    a = math.radians(lerp((40,), (8,), u)[0]); r = R + 2.5
    return (BX + r * math.sin(a), 0, r * math.cos(a))
m2 = missil("missil2"); visivel(m2, t0, t1)
caminho(m2, t0, t1, lambda u: f_m2(u))
m2.scale = (1.3,) * 3
awacs = aviao("awacs")
visivel(awacs, T(2, "Então"), t1)
caminho(awacs, T(2, "Então"), t1, lambda u: (BX - 30 + 45 * u, -6, R + 28 + 2 * u))
awacs.scale = (2.6,) * 3
feixe2 = barra_y("feixe2", 0.25, C["defesa"])
feixe2.parent = None
st = feixe2.constraints.new("COPY_LOCATION"); st.target = awacs
st2 = feixe2.constraints.new("STRETCH_TO"); st2.target = m2; st2.rest_length = 1.0; st2.keep_axis = "PLANE_X"; st2.volume = "NO_VOLUME"
visivel(feixe2, T(2, "dentro"), t1)
corte(2, (BX - 5, -150, 60), (BX + 5, 0, 52))
cam_key(T(2, "Então"), (BX + 5, -135, 75), (BX + 5, 0, 62))
cam_key(t1 - 0.05, (BX + 15, -115, 80), (BX + 10, 0, 66))

# =====================================================================
# 3 — IFF (palco C: sala de controle, x=-2000)
# =====================================================================
t0, t1 = S[3]
CX = -2000
sala = [caixa("piso", (CX, 0, -0.1), (16, 16, 0.2), C["piso"]), caixa("paredeF", (CX, 6, 4), (16, 0.3, 8.5), C["parede"]),
        caixa("paredeE", (CX - 7, 0, 4), (0.3, 16, 8.5), C["parede"]), caixa("paredeD", (CX + 7, 0, 4), (0.3, 16, 8.5), C["parede"]),
        caixa("mesa", (CX, 2.5, 1.0), (7, 1.6, 0.2), C["madeira"]), caixa("pemesa", (CX, 2.5, 0.5), (6.6, 1.2, 1.0), C["madeira"])]
tela = caixa("tela", (CX, 5.8, 4.4), (9, 0.2, 5), C["tela"]); sala.append(tela)
moldura = caixa("moldura", (CX, 5.9, 4.4), (9.5, 0.1, 5.5), C["escuro"]); sala.append(moldura)
for k in range(4):
    sala.append(anel(f"grade{k}", (CX, 5.65, 4.4), 0.6 + k * 0.6, 0.03, (0.15, 0.6, 0.3, 1), seg=32))
    sala[-1].rotation_euler = (math.radians(90), 0, 0)
op, op_bd, op_be = boneco("operador", (CX, -0.2, 0.0))
op.rotation_euler = (0, 0, 0)
cad = caixa("cadeira", (CX, -0.6, 0.6), (1.2, 1.2, 0.2), C["escuro"]); sala.append(cad)
for o in sala + [op]: visivel(o, t0, t1)
random.seed(3)
pontos = []
for k in range(6):
    m = mat((0.6, 1.0, 0.6, 1), unico=f"ponto{k}")
    p = cilindro(f"ponto{k}", (0, 0, 0), 0.22, 0.1, (0.6, 1.0, 0.6, 1), seg=8, unico=f"ponto{k}")
    p.rotation_euler = (math.radians(90), 0, 0)
    x0, z0 = random.uniform(-3.8, 3.8), random.uniform(2.4, 6.4)
    visivel(p, t0 + 0.2 + k * 0.15, t1)
    caminho(p, t0, t1, lambda u, x0=x0, z0=z0, k=k: (CX + x0 + 0.6 * u * (1 if k % 2 else -1), 5.6, z0 + 0.3 * math.sin(u * 6 + k)), orientar=False)
    pontos.append((p, p.data.materials[0]))
for k, (p, m) in enumerate(pontos):
    if k == 4:
        cor_key(m, T(3, "responde") + 0.8, (0.6, 1.0, 0.6, 1)); cor_key(m, T(3, "responde") + 1.2, C["ameaca"])
        p.scale = (1,) * 3; p.keyframe_insert("scale", frame=f(T(3, "responde") + 1.2)); p.scale = (2.2,) * 3; p.keyframe_insert("scale", frame=f(T(3, "responde") + 1.6))
    else:
        tt = T(3, "responde") + 0.15 * k
        cor_key(m, tt, (0.6, 1.0, 0.6, 1)); cor_key(m, tt + 0.2, (0.15, 0.55, 1.0, 1))
corte(3, (CX + 2.5, -5.5, 3.6), (CX, 4, 3.4))
cam_key(T(3, "Então"), (CX + 1.2, -3.0, 3.4), (CX, 5, 4.2))
cam_key(t1 - 0.05, (CX + 0.3, -0.2, 4.0), (CX, 6, 4.4))

# =====================================================================
# 4 — INTERCEPTADOR
# =====================================================================
t0, t1 = S[4]
alvo4 = aviao("alvo4", C["ameaca"], radome=False); alvo4.scale = (2.2,) * 3
visivel(alvo4, t0, T(4, "Esse") - 0.2)
P4 = lambda u: lerp((-70, 70, 34), (-26, 40, 30), u)
caminho(alvo4, t0, t1, P4)
bala = esfera("bala", (0, 0, 0), 0.9, C["escuro"], sub=1)
tb0, tb1 = T(4, "Uma"), T(4, "Então") - 0.1
visivel(bala, tb0, tb1 + 0.2)
fb = lambda u: bez((CANHAO_POS[0], CANHAO_POS[1] + 1.6, 3.0), (-20, 32, 22), (-22, 40, 0.5), u)
caminho(bala, tb0, tb1, fb, orientar=False); rastro(fb, tb0, tb1, C["cinza"], r=0.25, cada=0.1, vida=0.6)
explosao((-22, 40, 0.5), tb1, r=3)
ti0, ti1 = T(4, "lança") + 0.2, T(4, "Esse") - 0.2
hit4 = P4((ti1 - t0) / (t1 - t0))
it4 = missil("inter4", C["branco"])
fi4 = lambda u: bez((LANC_POS[0], LANC_POS[1], 3), (10, 20, 50), hit4, suave(u))
visivel(it4, ti0, ti1); caminho(it4, ti0, ti1, fi4); rastro(fi4, ti0, ti1)
explosao(hit4, ti1, r=6)
corte(4, (-44, -12, 8), (-18, 30, 16))
cam_key(T(4, "Então"), (-30, -22, 12), (0, 28, 22))
cam_key(t1 - 0.05, (-20, -24, 16), (-14, 34, 28))

# =====================================================================
# 5 — BALÍSTICO: mirar no futuro
# =====================================================================
t0, t1 = S[5]
ALTO = (-90, 150, 150); IMPACTO = (2, 2, 0)
fbal = lambda u: lerp(ALTO, IMPACTO, u)
tb_hit = T(5, "acertar") + 0.3
ub_hit = 0.72
fbal_t = lambda t: fbal(ub_hit * (t - t0) / (tb_hit - t0))
bal = missil("balistico", escala=2.2)
visivel(bal, t0, tb_hit)
caminho(bal, t0, tb_hit, lambda u: fbal(ub_hit * u))
rastro(lambda u: fbal(ub_hit * u), t0, tb_hit, (0.85, 0.85, 0.85, 1), r=0.9, cada=0.12, vida=2.0)
# tiro errado: mira onde ele ESTÁ
te0, te1 = T(5, "mira"), T(5, "erra") + 0.4
p_atual = fbal_t(te0)
erro = missil("interErro", C["branco"])
fe = lambda u: bez((LANC_POS[0], LANC_POS[1], 3), (0, 40, 90), (p_atual[0] + 5, p_atual[1] - 8, p_atual[2] - 10), u)
visivel(erro, te0, te1); caminho(erro, te0, te1, fe); rastro(fe, te0, te1)
# trajetória prevista pontilhada + X
tp = T(5, "computador")
for k in range(12):
    u = ub_hit * 0.55 + (ub_hit - ub_hit * 0.55) * k / 11
    d = esfera(f"prev{k}", fbal(u), 0.6, C["defesa"], sub=0)
    visivel(d, tp + 0.08 * k, tb_hit); pop(d, tp + 0.08 * k, dur=0.2)
P5 = fbal(ub_hit)
xa = caixa("xA", P5, (0.6, 0.6, 9), C["defesa"]); xa.rotation_euler = (0, math.radians(45), math.radians(30))
xb = caixa("xB", P5, (0.6, 0.6, 9), C["defesa"]); xb.rotation_euler = (0, math.radians(-45), math.radians(30))
for o in (xa, xb): visivel(o, T(5, "vai"), tb_hit); pop(o, T(5, "vai"))
ti0 = T(5, "manda")
it5 = missil("inter5", C["branco"], escala=1.4)
fi5 = lambda u: bez((LANC_POS[0], LANC_POS[1], 3), (20, 20, 70), P5, suave(u))
visivel(it5, ti0, tb_hit); caminho(it5, ti0, tb_hit, fi5); rastro(fi5, ti0, tb_hit)
explosao(P5, tb_hit, r=12, n=18)
corte(5, (45, -55, 30), (-20, 35, 55))
cam_key(tp, (40, -60, 38), (-25, 45, 60))
cam_key(t1 - 0.05, (30, -55, 45), (-25, 45, 62))

# =====================================================================
# 6 — CAMADAS: custo
# =====================================================================
t0, t1 = S[6]
moedas = []
for k in range(14):
    mo = cilindro(f"moeda{k}", (LANC_POS[0] + 6, LANC_POS[1] - 6, 0.25 + 0.4 * k), 1.4, 0.35, (1.0, 0.78, 0.15, 1), seg=10)
    moedas.append(mo); visivel(mo, t0, t0 + (T(6, "dele") + 0.6 - t0) * (1 - k / 14) + 0.0)
drones = []
random.seed(11)
tdr0 = T(6, "enxames") - 0.4; tdr1 = T(6, "laser") + 1.2
for k in range(12):
    d = drone(f"drone6_{k}", 2.4)
    a = math.radians(70 + k * 5); st0 = (130 * math.cos(a) + random.uniform(-15, 15), 130 * math.sin(a), random.uniform(14, 28))
    en = (random.uniform(-15, 15), random.uniform(10, 30), random.uniform(10, 18))
    morte = tdr0 + 3.5 + k * 0.55
    visivel(d, tdr0, morte); caminho(d, tdr0, morte, lambda u, s=st0, e=en: lerp(s, e, u * 0.8))
    drones.append((d, morte, lerp(st0, en, 0.8)))
    if k < 5:  # derrubados com míssil caro (antes das camadas)
        ti = morte - 1.0; pe = lerp(st0, en, 0.8)
        it = missil(f"inter6_{k}", C["branco"]); fi = lambda u, pe=pe: bez((LANC_POS[0], LANC_POS[1], 3), (15, 10, 30), pe, suave(u))
        visivel(it, ti, morte); caminho(it, ti, morte, fi); rastro(fi, ti, morte, vida=0.8, cada=0.1)
    elif k < 9:  # canhão
        for j in range(4):
            tj = morte - 0.6 + j * 0.12
            tr = esfera(f"traco{k}{j}", (0, 0, 0), 0.25, C["defesa"], sub=0)
            pe = lerp(st0, en, 0.8)
            visivel(tr, tj, tj + 0.5); caminho(tr, tj, tj + 0.5, lambda u, pe=pe: lerp((CANHAO_POS[0], CANHAO_POS[1], 3), pe, u), orientar=False)
    else:  # laser
        pe = lerp(st0, en, 0.8)
        lz = cilindro(f"laserFx{k}", (0, 0, 0), 0.18, 1, C["ciano"], seg=6)
        lz.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 0.5)))
        lz.location = (LASER_POS[0], LASER_POS[1], 3.0)
        dv = Vector(pe) - Vector(lz.location); lz.rotation_mode = "QUATERNION"; lz.rotation_quaternion = dv.to_track_quat("Z", "Y"); lz.scale = (1, 1, dv.length)
        visivel(lz, morte - 0.7, morte)
    explosao(lerp(st0, en, 0.8), morte, r=3, n=8)
for k, (R_, cor, tt) in enumerate([(44, C["ameaca"], T(6, "Míssil", 1)), (30, C["laranja"], T(6, "canhão")), (18, C["ciano"], T(6, "laser"))]):
    a6 = anel(f"camada{k}", (0, 0, 0.3), R_, 0.5, cor, seg=48)
    visivel(a6, tt, S[11][1]); pop(a6, tt, dur=0.5)
    a6.hide_render = True  # some nas cenas de outros palcos (re-ligado abaixo)
corte(6, (34, -30, 8), (24, -12, 4))
cam_key(T(6, "enxames"), (40, -55, 30), (0, 20, 12))
cam_key(T(6, "camadas"), (10, -70, 55), (0, 5, 0))
cam_key(t1 - 0.05, (-35, -62, 55), (0, 5, 0))

# =====================================================================
# 7 — TRIAGEM
# =====================================================================
t0, t1 = S[7]
random.seed(21)
alvos = [(-50, 30), (60, -40), (70, 50), (-70, -50), (-40, 75), (80, 5), (-85, 10), (5, 8), (-10, -6), (12, -12)]
tr0 = T(7, "chegam")
for k, (ax, ay) in enumerate(alvos):
    cidade = abs(ax) < 25 and abs(ay) < 25
    orig = (ax * 0.3 + random.uniform(-20, 20), 260, 0)
    queda = T(7, "deixa") + 0.8 + k * 0.12 if not cidade else T(7, "gente") + 0.2
    fr = lambda u, o=orig, a=(ax, ay, 0): bez(o, ((o[0] + a[0]) / 2, (o[1] + a[1]) / 2, 110), a, u)
    tot = queda - tr0
    fog = missil(f"fog{k}", escala=1.2)
    if cidade:
        u_hit = (T(7, "gente") + 0.2 - tr0) / (T(7, "deixa") + 3.5 - tr0)
        fr2 = lambda u, fr=fr, uh=u_hit: fr(u * uh)
        visivel(fog, tr0, queda); caminho(fog, tr0, queda, fr2); rastro(fr2, tr0, queda, (0.85, 0.85, 0.85, 1), cada=0.15, vida=1.2)
        ph = fr(u_hit)
        ti = T(7, "atira") - 0.2
        it = missil(f"inter7_{k}", C["branco"]); fi = lambda u, ph=ph, k=k: bez((LANC_POS[0], LANC_POS[1], 3), (0, 0, 60), ph, suave(u))
        visivel(it, ti, queda); caminho(it, ti, queda, fi); rastro(fi, ti, queda, vida=0.8)
        explosao(ph, queda, r=6)
    else:
        visivel(fog, tr0, queda); caminho(fog, tr0, queda, fr); rastro(fr, tr0, queda, (0.85, 0.85, 0.85, 1), cada=0.15, vida=1.2)
        explosao((ax, ay, 0.5), queda, r=4, n=8)
    mk = cilindro(f"marca{k}", (ax, ay, 0.15), 4.5, 0.2, C["ameaca"], seg=16, unico=f"marca{k}")
    tm = T(7, "calcula") + 0.15 * k
    visivel(mk, tm, queda + 0.3); pop(mk, tm)
    if not cidade:
        cor_key(mk.data.materials[0], T(7, "campo") - 0.05, C["ameaca"]); cor_key(mk.data.materials[0], T(7, "campo") + 0.3, C["cinza"])
corte(7, (15, -85, 75), (0, 25, 10))
cam_key(T(7, "Só"), (-5, -75, 70), (0, 15, 5))
cam_key(t1 - 0.05, (-20, -70, 68), (0, 12, 5))

# =====================================================================
# 8 — NOITE: radar = lanterna; mobilidade e isca (palco E, y=2000)
# =====================================================================
t0, t1 = S[8]
EY = 2000
cor_key_w = lambda t, c: (W.__setattr__("color", c[:3]), W.keyframe_insert("color", frame=f(t)))
cor_key_w(t0 - 0.05, CEU); cor_key_w(t0, NOITE); cor_key_w(t1 - 0.05, NOITE); cor_key_w(t1, CEU)
for fc in W.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
chaoE = caixa("chaoE", (0, EY, -0.2), (400, 400, 0.4), (0.16, 0.30, 0.18, 1)); visivel(chaoE, t0, t1)
for k in range(30):
    a = arvore((random.uniform(-80, 80), EY + random.uniform(10, 90)), 1.3); visivel(a, t0, t1)
cam8, _ = caminhao("radarMovel", (0, EY, 0.9), tubos=False)
rM, rM_gir = radar("radarM", (0, 0, 0)); filho(cam8, rM); rM.location = (0, -1.5, 0.9); rM.scale = (0.8,) * 3
visivel(cam8, t0, t1)
cone = cilindro("luz", (0, 0, 0), 0.5, 1, (1.0, 0.95, 0.55, 1), seg=10, r2=12)
cone.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 0.5)))
cone.location = (0, EY - 1.5, 4.5); cone.rotation_euler = (math.radians(-70), 0, 0); cone.scale = (1, 1, 60)
tl = T(8, "liga")
visivel(cone, tl, T(8, "caminhões"))
cone.rotation_mode = "XYZ"
for k, tt in enumerate([tl, tl + 1.5, tl + 3, tl + 4.5, T(8, "caminhões")]):
    cone.rotation_euler = (math.radians(-70), 0, math.radians(-40 + 25 * (k % 2) * 2)); cone.keyframe_insert("rotation_euler", frame=f(tt))
tm0 = T(8, "inimigo"); tm1 = T(8, "isca") + 0.5
m8 = missil("missil8", escala=1.5)
f8 = lambda u: bez((-30, EY + 160, 60), (-10, EY + 60, 40), (0, EY, 2.5), u)
visivel(m8, tm0, tm1); caminho(m8, tm0, tm1, f8); rastro(f8, tm0, tm1, (0.6, 0.6, 0.65, 1), cada=0.12, vida=1.2)
# caminhão foge
cam8.keyframe_insert("location", frame=f(T(8, "caminhões") - 0.3))
cam8.location = (38, EY - 25, 0.9); cam8.keyframe_insert("location", frame=f(T(8, "dispara") + 1.2))
cam8.rotation_euler = (0, 0, 0); cam8.keyframe_insert("rotation_euler", frame=f(T(8, "caminhões") - 0.3))
cam8.rotation_euler = (0, 0, math.radians(-60)); cam8.keyframe_insert("rotation_euler", frame=f(T(8, "dispara")))
isca, _ = radar("isca", (0, EY, 0.75), cor_base=(0.75, 0.75, 0.80, 1))
visivel(isca, T(8, "espalha") - 0.2, tm1 + 0.05); pop(isca, T(8, "espalha") - 0.2)
explosao((0, EY, 2.5), tm1, r=8, n=16)
corte(8, (-18, EY - 42, 10), (0, EY + 10, 6))
cam_key(T(8, "inimigo"), (-30, EY - 40, 16), (-5, EY + 30, 15))
cam_key(T(8, "caminhões"), (-12, EY - 50, 18), (10, EY - 5, 2))
cam_key(t1 - 0.05, (-20, EY - 45, 18), (5, EY, 3))

# =====================================================================
# 9 — COMANDO E CONTROLE (rede)
# =====================================================================
t0, t1 = S[9]
aw9 = aviao("awacs9"); aw9.scale = (2.0,) * 3
visivel(aw9, t0, S[12][1])
caminho(aw9, t0, S[12][1], lambda u: (55 * math.cos(u * 6 + 1), 55 * math.sin(u * 6 + 1), 40))
nos = [("radar", (RADAR_POS[0], RADAR_POS[1], 4), T(9, "radar")), ("avião", None, T(9, "avião")),
       ("lançador", (LANC_POS[0], LANC_POS[1], 3), T(9, "lançador")), ("laser", (LASER_POS[0], LASER_POS[1], 3), T(9, "laser"))]
for k, (nome, p, tt) in enumerate(nos):
    alvo_obj = {"radar": rad, "avião": aw9, "lançador": lanc, "laser": laser}[nome]
    pulso = anel(f"pulso{k}", (0, 0, 0), 4.5, 0.35, C["defesa"], seg=24)
    pc = pulso.constraints.new("COPY_LOCATION"); pc.target = alvo_obj
    visivel(pulso, tt, tt + 0.9); pop(pulso, tt, 1.0)
    linha = barra_y(f"linha{k}", 0.25, C["defesa"])
    lc = linha.constraints.new("COPY_LOCATION"); lc.target = hexa
    ls = linha.constraints.new("STRETCH_TO"); ls.target = alvo_obj; ls.rest_length = 1.0; ls.keep_axis = "PLANE_X"; ls.volume = "NO_VOLUME"
    tl9 = T(9, "rede") + 0.15 * k
    visivel_janelas(linha, [(tl9, S[9][1]), (S[11][0], S[12][1])])
for k in range(3):
    tt = T(9, "decide") + 0.4 * k
    o = anel(f"cmdPulso{k}", (0, 0, 4), 70, 0.6, C["defesa"], seg=64)
    visivel(o, tt, tt + 1.2); o.scale = (0.04,) * 3; o.keyframe_insert("scale", frame=f(tt)); o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(tt + 1.2))
destacar(hexa.data.materials[0], T(9, "Esse"), C["azulmarinho"])
corte(9, (0, -70, 80), (0, 5, 0))
cam_key(T(9, "rede"), (15, -65, 75), (0, 5, 0))
cam_key(t1 - 0.05, (35, -60, 80), (0, 0, 4))

# =====================================================================
# 10 — SIRENE E ABRIGO
# =====================================================================
t0, t1 = S[10]
poste = cilindro("poste", (6, -22, 4), 0.2, 8, C["cinza"], seg=6)
sir = cilindro("sirene", (0, 0, 4.2), 0.8, 1.2, C["ameaca"], seg=8, r2=0.3); filho(poste, sir); sir.location = (0, 0, 4.2)
abrigo = caixa("abrigo", (-4, -24, 0.6), (4, 3, 1.2), C["cinza"]); porta = caixa("porta", (0, -1.52, -0.05), (2, 0.1, 1.0), C["escuro"]); filho(abrigo, porta)
for o in (poste, abrigo): visivel(o, t0, t1)
for k in range(3):
    tt = T(10, "sirene") + 0.5 * k
    o = anel(f"som{k}", (6, -22, 8.2), 6, 0.15, C["ameaca"], seg=32)
    visivel(o, tt, tt + 0.9); o.scale = (0.15,) * 3; o.keyframe_insert("scale", frame=f(tt)); o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(tt + 0.9))
random.seed(5)
for k in range(6):
    b, bd, be = boneco(f"pessoa{k}", (0, 0, 0), camisa=random.choice(PREDIOS), capacete=False)
    st = (random.uniform(4, 14), random.uniform(-30, -16), 0)
    ta = T(10, "corre") - 0.6 + k * 0.15
    visivel(b, t0, ta + 1.5)
    caminho(b, ta, ta + 1.4, lambda u, st=st: lerp(st, (-4, -26, 0), u), orientar=False)
    b.rotation_euler = (0, 0, math.atan2(-26 - st[1], -4 - st[0]) - math.pi / 2)
    b.keyframe_insert("scale", frame=f(ta + 1.1)); b.scale = (0.01,) * 3; b.keyframe_insert("scale", frame=f(ta + 1.4)); b.scale = (1,) * 3
fx = missil("fura", escala=1.5)
ff = lambda u: bez((-90, 110, 70), (-50, 30, 55), (-28, 12, 1), u)
tf0, tf1 = t0 + 0.2, T(10, "tudo") + 0.6
visivel(fx, tf0, tf1); caminho(fx, tf0, tf1, ff); rastro(ff, tf0, tf1, (0.8, 0.8, 0.8, 1), cada=0.12)
explosao((-28, 12, 1), tf1, r=7)
corte(10, (16, -48, 5), (-6, 0, 10))
cam_key(T(10, "sirene"), (14, -40, 4), (0, -22, 4))
cam_key(t1 - 0.05, (10, -36, 4), (-4, -24, 2))

# =====================================================================
# 11/12 — PARABÉNS + CTA
# =====================================================================
t0 = S[11][0]; tF = S[12][1]
fin, fin_bd, fin_be = boneco("operadorFinal", (10, -34, 0))
fin.rotation_euler = (0, 0, math.radians(200)); fin.scale = (2.2,) * 3
visivel(fin, t0, tF)
fin_bd.rotation_euler = (0, 0, 0); fin_bd.keyframe_insert("rotation_euler", frame=f(t0 + 0.3))
fin_bd.rotation_euler = (0, math.radians(-150), 0); fin_bd.keyframe_insert("rotation_euler", frame=f(t0 + 0.8))
corte(11, (24, -62, 14), (0, 0, 8))
cam_key(S[12][0], (40, -55, 28), (0, 0, 6))
cam_key(tF, (55, -35, 40), (0, 0, 4))

# camadas (anéis) aparecem também no final e no comando
for o in bpy.data.objects:
    if o.name.startswith("camada"):
        o.animation_data_clear()
        tt6 = [T(6, "Míssil", 1), T(6, "canhão"), T(6, "laser")][int(o.name[-1])]
        pop(o, tt6, dur=0.5)
        visivel_janelas(o, [(tt6, S[6][1]), (S[9][0], S[12][1])])

# ---------- render ----------
if os.environ.get("REALISTA"):
    modo_realista(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "hdri", "ceu_parcialmente_nublado_2k.hdr"))

saida = os.path.join(PASTA, "frames")
os.makedirs(saida, exist_ok=True)
if len(args) > 1 and args[1] == "preview":
    scn.render.resolution_percentage = 50
    for t in [float(x) for x in args[2].split(",")]:
        scn.frame_set(f(t)); scn.render.filepath = os.path.join(PASTA, "preview", f"p_{t:06.2f}.jpg"); bpy.ops.render.render(write_still=True)
elif len(args) > 1 and args[1] == "range":
    a, b = [int(x) for x in args[2].split(",")]
    scn.frame_start, scn.frame_end = a, b
    scn.render.filepath = os.path.join(saida, "f_")
    bpy.ops.render.render(animation=True)
else:
    print("FRAMES", scn.frame_end)
