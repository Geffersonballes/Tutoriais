"""Vídeo refinaria — "Por que mirar numa refinaria?" (Jazan, 27/11/2026). Uso:
REALISTA=1 blender -b --factory-startup -P cena_refinaria.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
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
random.seed(2712)

VERMELHO = (1.0, 0.15, 0.10, 1); AMARELO = (0.98, 0.82, 0.15, 1); LARANJA = (0.95, 0.50, 0.12, 1)
AZUL = (0.25, 0.55, 0.90, 1); BRANCO = C["branco"]; OLIVA = C["oliva"]
AREIA = (0.86, 0.74, 0.52, 1); AREIA2 = (0.80, 0.66, 0.44, 1); ASFALTO = (0.30, 0.30, 0.32, 1)
PRETO = (0.06, 0.06, 0.07, 1)
def andar(ob, t0, t1, a, b):
    ob.location = a; ob.keyframe_insert("location", frame=f(t0)); ob.location = b; ob.keyframe_insert("location", frame=f(t1))
def rumo(ob, t, graus):
    ob.rotation_euler = (0, 0, math.radians(graus)); ob.keyframe_insert("rotation_euler", frame=f(t), index=2)
def texto3d(nome, txt, tam, cor, chave):
    cd = bpy.data.curves.new(nome, "FONT"); cd.body = txt; cd.extrude = 0.4; cd.size = tam; cd.align_x = "CENTER"; cd.bevel_depth = 0.05
    o = bpy.data.objects.new(nome, cd); scn.collection.objects.link(o); o.data.materials.append(mat(cor, chave)); return o
def pulsar(ob, t0, t1, s0=0.85, s1=1.15, per=0.35):
    t = t0; k = 0
    while t < t1:
        ob.scale = ((s0 if k % 2 == 0 else s1),) * 3; ob.keyframe_insert("scale", frame=f(t)); t += per; k += 1

# =====================================================================
# TERRENO: deserto costeiro; mar a oeste (x < -70)
# =====================================================================
caixa("chao", (300, 0, -0.5), (1400, 1600, 1.0), AREIA)
MAR = mar_ondulado("mar", (-470, 0, 0.15), (800, 1600), (0.18, 0.45, 0.62, 1), res=90, altura=0.5, escala_onda=8.0, t_fim=FIM + 1)
caixa("praia", (-72, 0, 0.02), (8, 1600, 0.1), (0.93, 0.85, 0.66, 1))
for _ in range(30):
    d = esfera("duna", (random.uniform(120, 700), random.uniform(260, 520), -3), random.uniform(18, 40), random.choice([AREIA, AREIA2]), sub=2)
    d.scale = (1.8, 1.0, 0.35)

# =====================================================================
# 1) REFINARIA (Jazan) em R
# =====================================================================
R = (0, 0)
caixa("pisoRef", (R[0], R[1], 0.03), (84, 70, 0.06), (0.62, 0.60, 0.56, 1))
TORRES = []
for k, (x, h) in enumerate(((-14, 24), (-6, 19), (2, 15))):
    t_, saidas = torre_destilacao(_id("torre"), (R[0] + x, R[1] + 12), h=h, r=1.6 if k == 0 else 1.3)
    TORRES.append((t_, saidas, h))
# rack de tubos (vigas + 4 tubos coloridos)
for x in range(-30, 34, 6):
    caixa(_id("rackPe"), (x, R[1] + 2, 2.2), (0.3, 0.3, 4.4), (0.30, 0.32, 0.34, 1), unico="tdPlat")
caixa("rackViga", (R[0] + 2, R[1] + 2, 4.5), (66, 1.6, 0.25), (0.30, 0.32, 0.34, 1), unico="tdPlat")
TUBOS = []
for j, cor in enumerate((AMARELO, LARANJA, AZUL, (0.40, 0.40, 0.42, 1))):
    tb = cilindro(_id("tubo"), (0, 0, 0), 0.28, 64, cor, seg=10, unico="tubo%d" % j)
    tb.data.transform(__import__("mathutils").Matrix.Rotation(math.radians(90), 4, "Y")); tb.location = (R[0] + 2, R[1] + 1.4 + j * 0.45, 4.9 + (j % 2) * 0.1)
    TUBOS.append(tb)
# parque de tanques
TANQUES = []
for row, y in enumerate((-14, -27)):
    for k in range(4):
        x = -24 + k * 13
        faixa = (0.80, 0.20, 0.15, 1) if (row + k) % 2 == 0 else (0.20, 0.45, 0.75, 1)
        TANQUES.append(tanque_armazenamento(_id("tanque"), (R[0] + x, R[1] + y), r=5.0, h=6.0, faixa=faixa))
ALVO_T = TANQUES[5]          # tanque atingido (fileira de trás, 2º)
AT = Vector((ALVO_T.location[0], ALVO_T.location[1], 6.5))
# tocha (flare) com chama
tocha = cilindro("tocha", (R[0] + 30, R[1] + 22, 13), 0.5, 26, (0.75, 0.30, 0.20, 1), seg=10)
for z in (4, 10, 16, 22):
    filho(tocha, anel(_id("tochaAro"), (0, 0, z - 13), 0.6, 0.06, BRANCO, seg=12))
CHAMA = esfera("chama", (R[0] + 30, R[1] + 22, 27.2), 1.3, (1.0, 0.55, 0.10, 1), sub=2, unico="fogo"); CHAMA.scale = (1, 1, 1.6)
# prédios administrativos e caminhão-tanque estacionado
for k in range(4):
    predio((R[0] + 28 + (k % 2) * 9, R[1] - 12 - (k // 2) * 10), 7, 6, random.uniform(4, 7), PREDIOS[k])
cerca = []
for k in range(36):
    a = k * 10
    cilindro(_id("cerca"), (R[0] + 46 * math.cos(math.radians(a)), R[1] + 40 * math.sin(math.radians(a)), 1.0), 0.1, 2.0, (0.6, 0.6, 0.6, 1), seg=5)
# fogo + fumaça do tanque atingido
FOGO = []
for k in range(7):
    a = k * 360 / 7
    fo = esfera(_id("fogoT"), (AT[0] + 2.6 * math.cos(math.radians(a)), AT[1] + 2.6 * math.sin(math.radians(a)), 6.4), random.uniform(1.4, 2.2), (1.0, 0.45 + 0.1 * (k % 3), 0.08, 1), sub=2, unico="fogo")
    pulsar(fo, 0, FIM, 0.8, 1.2, 0.25 + 0.04 * k); FOGO.append(fo)
FUMACA = coluna_fumaca("fumTanque", (AT[0], AT[1], 7.0), altura=34, raio=3.6, t0=0, t_fim=FIM, n=28, deriva=(0.35, 0.18))
# anel de "ponto fraco"
ANEL_PF = anel("anelPF", (R[0], R[1] - 2, 0.6), 46, 0.8, VERMELHO, seg=96, unico="alerta")

# =====================================================================
# 2) CAMPO DE PETRÓLEO (cavalos de pau + barris de óleo cru) em OF
# =====================================================================
OF = (95, 75)
CDP = []
for k in range(6):
    b_, p_ = cavalo_de_pau(_id("cdp"), (OF[0] - 24 + (k % 3) * 16, OF[1] + (k // 3) * 18))
    b_.rotation_euler = (0, 0, math.radians(90 + random.uniform(-15, 15)))
    per = random.uniform(1.6, 2.2); t = 0; s = 1
    while t < FIM:
        p_.rotation_euler = (math.radians(14 * s), 0, 0); p_.keyframe_insert("rotation_euler", frame=f(t), index=0); t += per / 2; s = -s
    CDP.append(b_)
BARRIS = []
for k in range(8):
    b = barril(_id("barrilCru"), escala=0.9, cor=PRETO); b.location = (OF[0] - 12 + (k % 4) * 2.4, OF[1] - 14 - (k // 4) * 2.4, 1.2); BARRIS.append(b)
caixa("dutoOF", (OF[0] / 2 + 15, OF[1] / 2 + 6, 0.5), (4, 4, 4), (0.4, 0.4, 0.42, 1))
duto = cilindro("duto", (0, 0, 0), 0.5, 112, (0.25, 0.25, 0.27, 1), seg=10)
duto.data.transform(__import__("mathutils").Matrix.Rotation(math.radians(90), 4, "Y"))
duto.location = ((OF[0] + 30) / 2 - 5, (OF[1] + 12) / 2, 0.6); duto.rotation_euler = (0, 0, math.atan2(OF[1] - 12, OF[0] - 30))

# =====================================================================
# 3) DISTRIBUIÇÃO: estrada leste, posto, aeroporto, quartel
# =====================================================================
caixa("estradaL", (100, -45, 0.04), (140, 7, 0.08), ASFALTO)
caixa("estradaQ", (110, -70, 0.04), (7, 50, 0.08), ASFALTO)
caixa("estradaSai", (36, -35, 0.04), (7, 20, 0.08), ASFALTO)
for x in range(34, 170, 8):
    caixa(_id("faixaEst"), (x, -45, 0.09), (3, 0.3, 0.02), BRANCO, unico="faixaEst")
PO = (70, -56); AE = (150, -20); QU = (110, -100)
caixa("pisoPosto", (PO[0], PO[1], 0.05), (22, 12, 0.1), (0.75, 0.75, 0.74, 1))
for k in range(3):
    bc = bomba_combustivel(_id("bomba")); bc.location = (PO[0] - 6 + k * 6, PO[1], 1.5)
cobertura = caixa("cobPosto", (PO[0], PO[1], 6.0), (22, 10, 0.6), BRANCO)
for x in (-9, 9):
    caixa(_id("pilar"), (PO[0] + x, PO[1], 3), (0.6, 0.6, 6), BRANCO)
filho(cobertura, caixa("faixaPosto", (0, 0, 0), (22.1, 10.1, 0.25), LARANJA))
caixa("pista", (AE[0], AE[1], 0.05), (90, 10, 0.1), ASFALTO)
for x in range(-40, 44, 8):
    caixa(_id("faixaPista"), (AE[0] + x, AE[1], 0.11), (4, 0.5, 0.02), BRANCO, unico="faixaEst")
AV = aviao("aviaoAero", cor=BRANCO, radome=False); AV.location = (AE[0] - 10, AE[1] + 14, 1.6); AV.rotation_euler = (0, 0, math.radians(-90)); AV.scale = (1.4,) * 3
predio((AE[0] + 20, AE[1] + 18), 18, 8, 6, PREDIOS[1])
caixa("pisoQuartel", (QU[0], QU[1], 0.05), (40, 26, 0.1), (0.66, 0.62, 0.50, 1))
predio((QU[0] - 10, QU[1] - 6), 14, 8, 5, (0.62, 0.64, 0.50, 1))
s_ = sacos_areia("sacosQ", comprimento=12, fiadas=2); s_.location = (QU[0], QU[1] + 12, 0)
for k in range(3):
    cm, _ = caminhao(_id("milQ"), (QU[0] + 6 + k * 4, QU[1] - 4, 1.0), cor=OLIVA, tubos=False)
    filho(cm, caixa(_id("lona"), (0, -1.0, 1.4), (2.4, 4.4, 1.8), (0.36, 0.40, 0.24, 1)))
CT = [caminhao_tanque(_id("ctq"), (0, 0, 1.0)) for _ in range(3)]

# =====================================================================
# 4) HODEIDA (lançador) — sul, do outro lado do mar
# =====================================================================
HD = (-40, -330)
caixa("pisoHD", (HD[0], HD[1], 0.03), (30, 24, 0.06), AREIA2)
LANC, LANC_T = caminhao("lancHD", (HD[0], HD[1], 1.0), cor=(0.55, 0.50, 0.36, 1), tubos=True)
LANC.rotation_euler = (0, 0, math.radians(180 + 10))
for k in range(6):
    predio((HD[0] - 20 + (k % 3) * 9, HD[1] - 22 - (k // 3) * 9), 6, 6, random.uniform(3, 6), PREDIOS[(k + 2) % 6])
interrog = texto3d("interrog", "?", 7.0, AMARELO, "interrog"); interrog.rotation_euler = (math.radians(90), 0, 0)
piv_q = vazio("pivQ", (HD[0], HD[1], 9.0)); filho(piv_q, interrog); interrog.location = (0, 0, 0)
# rota do projétil (pontilhado) HD -> refinaria
def arco(u):
    return bez((HD[0], HD[1], 3), ((HD[0] + AT[0]) / 2, (HD[1] + AT[1]) / 2, 120), tuple(AT), u)
ROTA = [esfera(_id("rota"), arco(k / 40), 2.2, VERMELHO, sub=1, unico="alerta") for k in range(1, 40)]

# =====================================================================
# 5) ABQAIQ (2019) — planta grande + 10 barris "dominó"
# =====================================================================
AB = (330, 230)
caixa("pisoAB", (AB[0], AB[1], 0.03), (110, 80, 0.06), (0.62, 0.60, 0.56, 1))
for k in range(5):
    torre_destilacao(_id("torreAB"), (AB[0] - 40 + k * 9, AB[1] + 22), h=random.uniform(16, 24), r=1.4)
for k in range(8):
    esf = esfera(_id("esfAB"), (AB[0] - 36 + (k % 4) * 11, AB[1] + 2 - (k // 4) * 12, 5.2), 4.6, (0.92, 0.92, 0.90, 1), sub=3, unico="tanqueArm")
    for pl in esf.data.polygons: pl.use_smooth = True
    for dx in (-3, 3):
        cilindro(_id("perAB"), (esf.location[0] + dx, esf.location[1], 2.0), 0.25, 4.0, (0.3, 0.3, 0.32, 1), seg=6)
for k in range(5):
    tanque_armazenamento(_id("tanqueAB"), (AB[0] + 20 + (k % 3) * 12, AB[1] + 8 - (k // 3) * 12), r=5, h=6)
DOM = []
DX = (AB[0] - 30, AB[1] - 28)
for k in range(10):
    pv = vazio(_id("domPiv"), (DX[0] + k * 4.2 + 1.0, DX[1], 0))
    b = barril(_id("dom"), escala=1.0, cor=PRETO); filho(pv, b); b.location = (-1.0, 0, 1.3)
    DOM.append(pv)
FOGO_AB = []
for k in range(6):
    fo = esfera(_id("fogoAB"), (AB[0] - 36 + (k % 4) * 11, AB[1] + 2 - (k // 4) * 12, 9.0), 2.0, (1.0, 0.45, 0.08, 1), sub=2, unico="fogo")
    FOGO_AB.append(fo)
FUM_AB = coluna_fumaca("fumAB", (AB[0] - 25, AB[1] - 4, 8), altura=40, raio=4.5, t0=0, t_fim=FIM, n=24)

# =====================================================================
# câmera
# =====================================================================
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 24; cam_d.clip_end = 6000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def shot(t0, t1, loc0, tgt0, loc1=None, tgt1=None):
    for fr, loc, tgt in ((f(t0), loc0, tgt0), (f(t1) - 1, loc1 or loc0, tgt1 or tgt0)):
        for ob, v in ((cam, loc), (alvo, tgt)):
            ob.location = v; ob.keyframe_insert("location", frame=fr)

# janelas de fogo: gancho (depois do impacto) e a partir do impacto da cena 5
T_HIT0 = 1.5
T_HIT5 = T(5, "atingiu") + 0.25
JAN_FOGO = [(T_HIT0, S[1][0]), (T_HIT5, FIM)]
for o in FOGO: visivel_janelas(o, JAN_FOGO)
for o in FUMACA: visivel_janelas(o, JAN_FOGO)
for o in FOGO_AB + FUM_AB: visivel(o, T(7, "ataque"), S[8][0])

# míssil (gancho e cena 5)
MIS = missil("missil", escala=1.4)
def voo(ob, t0, t1, p0, p1, alt):
    caminho(ob, t0, t1, lambda u: bez(p0, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, alt), p1, u))
P_ENTRADA = (AT[0] - 70, AT[1] - 160, 60)
voo(MIS, 0.0, T_HIT0, P_ENTRADA, tuple(AT), 70)
visivel_janelas(MIS, [(0.0, T_HIT0)])
rastro(lambda u: bez(P_ENTRADA, ((P_ENTRADA[0] + AT[0]) / 2, (P_ENTRADA[1] + AT[1]) / 2, 70), tuple(AT), u), 0.0, T_HIT0 - 0.05, r=1.1, cada=0.05, vida=1.0)
explosao(tuple(AT), T_HIT0, r=12, n=16); explosao(tuple(AT), T_HIT0 + 0.25, r=8, n=10)

# ---------- S0: gancho ----------
t0, t1 = S[0]
tm = T(0, "mirar"); tp = T(0, "Peça")
shot(t0, T_HIT0 + 0.6, (AT[0] + 40, AT[1] - 60, 22), (AT[0], AT[1], 8), (AT[0] + 34, AT[1] - 52, 20), (AT[0], AT[1], 9))
shot(T_HIT0 + 0.6, tm - 0.1, (AT[0] + 30, AT[1] - 50, 18), (AT[0], AT[1], 12), (AT[0] + 14, AT[1] - 70, 46), (R[0], R[1], 6))
shot(tm - 0.1, t1, (R[0] + 40, R[1] - 110, 70), (R[0], R[1], 4), (R[0] + 10, R[1] - 120, 80), (R[0], R[1] + 4, 4))

# ---------- S1: petróleo cru (campo) ----------
t0, t1 = S[1]
tpe = T(1, "petróleo"); tcr = T(1, "cru")
for k, b in enumerate(BARRIS): pop(b, tpe + 0.12 * k, 0.9, 0.3); visivel(b, tpe + 0.12 * k)
shot(t0, tpe, (OF[0] - 40, OF[1] - 40, 20), (OF[0], OF[1] + 6, 3), (OF[0] - 30, OF[1] - 36, 16), (OF[0], OF[1] + 6, 3))
shot(tpe, t1, (OF[0] - 18, OF[1] - 30, 7), (OF[0] - 6, OF[1] - 16, 2), (OF[0] - 12, OF[1] - 30, 7), (OF[0] - 6, OF[1] - 16, 2))

# ---------- S2: a torre separa (gotas coloridas saem pelos tubos) ----------
t0, t1 = S[2]
tq = T(2, "aquece"); tg = T(2, "gasolina"); td = T(2, "diesel"); tk = T(2, "querosene"); te = T(2, "Essa")
TP, SAI, HP = TORRES[0]
# "calor" na base da torre principal
for k in range(5):
    cl = esfera(_id("calor"), (TP.location[0] + random.uniform(-1, 1), TP.location[1] - 2.2, 0.6), 0.6, (1.0, 0.45, 0.08, 1), sub=1, unico="fogo")
    visivel(cl, tq, S[3][0]); pulsar(cl, tq, S[3][0], 0.7, 1.2, 0.2)
for j, (tt, cor) in enumerate(((tg, AMARELO), (td, LARANJA), (tk, AZUL))):
    sx, sy, sz = SAI[j]
    base = Vector(TP.location) + Vector((sx, sy, sz))
    for k in range(6):
        g = esfera(_id("gota"), tuple(base), 0.55, cor, sub=2, unico="gota%d" % j)
        ts = tt + 0.18 * k
        visivel(g, ts, S[3][0])
        andar(g, ts, ts + 1.6, tuple(base), tuple(base + Vector((-12, -2 + k * 0.1, -sz + 0.6))))
shot(t0, tg - 0.2, (TP.location[0] + 22, TP.location[1] + 34, 10), (TP.location[0], TP.location[1], 10), (TP.location[0] + 16, TP.location[1] + 30, 14), (TP.location[0], TP.location[1], 12))
shot(tg - 0.2, t1, (TP.location[0] - 14, TP.location[1] + 30, 12), (TP.location[0] - 7, TP.location[1], 10), (TP.location[0] - 20, TP.location[1] + 28, 11), (TP.location[0] - 9, TP.location[1], 8))

# ---------- S3: abastecimento (caminhões-tanque saem para posto, aeroporto e quartel) ----------
t0, t1 = S[3]
tc3 = T(3, "caminhões"); tpo = T(3, "postos"); tae = T(3, "aeroportos"); tqu = T(3, "quartéis")
destinos = [((36, -30, 1.0), (36, -45, 1.0), (PO[0] - 6, -45, 1.0)),
            ((40, -30, 1.0), (40, -45, 1.0), (AE[0] - 40, -45, 1.0)),
            ((44, -30, 1.0), (44, -45, 1.0), (110, -45, 1.0))]
for k, (ct, (a, b, c)) in enumerate(zip(CT, destinos)):
    rumo(ct, 0, 0); ct.location = a; ct.keyframe_insert("location", frame=1)
    ts = tc3 + 0.25 * k
    andar(ct, ts, ts + 0.8, a, b); rumo(ct, ts + 0.8, -90); ct.keyframe_insert("location", frame=f(ts + 0.8))
    andar(ct, ts + 0.9, t1, b, c)
    visivel(ct, 0, S[5][0])
shot(t0, tpo - 0.1, (20, -80, 26), (45, -40, 2), (26, -84, 24), (55, -44, 2))
shot(tpo - 0.1, tae - 0.1, (PO[0] - 16, PO[1] - 24, 9), (PO[0], PO[1], 2.5), (PO[0] - 10, PO[1] - 24, 9), (PO[0] + 2, PO[1], 2.5))
shot(tae - 0.1, tqu - 0.1, (AE[0] - 36, AE[1] - 30, 12), (AE[0] - 10, AE[1] + 10, 2), (AE[0] - 30, AE[1] - 32, 12), (AE[0] - 6, AE[1] + 10, 2))
shot(tqu - 0.1, t1, (QU[0] - 26, QU[1] - 30, 14), (QU[0], QU[1], 2), (QU[0] - 20, QU[1] - 34, 16), (QU[0] + 2, QU[1], 2))

# ---------- S4: ponto fraco (anel vermelho; câmera sobe) ----------
t0, t1 = S[4]
tl = T(4, "lugar"); tco = T(4, "combustível"); tes = T(4, "esconder")
visivel(ANEL_PF, tl, S[5][0]); pop(ANEL_PF, tl, 1.0, 0.5)
for k, tq_ in enumerate(TANQUES):
    m_ = esfera(_id("pfMarca"), (tq_.location[0], tq_.location[1], 9.5), 1.0, VERMELHO, sub=2, unico="alerta")
    visivel(m_, tco + 0.08 * k, S[5][0]); pop(m_, tco + 0.08 * k, 1.0, 0.25)
shot(t0, tes - 0.2, (R[0] + 20, R[1] - 70, 26), (R[0], R[1] - 6, 4), (R[0] + 30, R[1] - 90, 60), (R[0], R[1] - 4, 2))
shot(tes - 0.2, t1, (R[0] + 10, R[1] - 50, 150), (R[0], R[1] - 2, 0), (R[0] + 6, R[1] - 40, 170), (R[0], R[1], 0))

# ---------- S5: o golpe em Jazan (míssil, impacto, incêndio, tocha apaga) ----------
t0, t1 = S[5]
tg5 = T(5, "guerra"); tpj = T(5, "projétil"); tin = T(5, "incêndio"); tpa = T(5, "parou"); te5 = T(5, "Esse")
MIS2 = missil("missil2", escala=1.4)
voo(MIS2, tpj - 0.9, T_HIT5, P_ENTRADA, tuple(AT), 70); visivel_janelas(MIS2, [(tpj - 0.9, T_HIT5)])
rastro(lambda u: bez(P_ENTRADA, ((P_ENTRADA[0] + AT[0]) / 2, (P_ENTRADA[1] + AT[1]) / 2, 70), tuple(AT), u), tpj - 0.9, T_HIT5 - 0.05, r=1.1, cada=0.05, vida=1.0)
explosao(tuple(AT), T_HIT5, r=13, n=16); explosao(tuple(AT), T_HIT5 + 0.3, r=9, n=10)
# tocha apaga quando "parte das operações parou"; cavalos de pau não importam aqui
CHAMA.keyframe_insert("scale", frame=f(tpa - 0.05)); CHAMA.scale = (0.01,) * 3; CHAMA.keyframe_insert("scale", frame=f(tpa + 0.4))
shot(t0, tpj - 0.2, (R[0] - 40, R[1] - 90, 40), (R[0], R[1], 4), (R[0] - 30, R[1] - 84, 36), (R[0], R[1], 4))
shot(tpj - 0.2, tin, (AT[0] + 36, AT[1] - 56, 20), (AT[0], AT[1], 8), (AT[0] + 30, AT[1] - 50, 18), (AT[0], AT[1], 10))
shot(tin, tpa - 0.3, (AT[0] - 26, AT[1] - 40, 12), (AT[0], AT[1], 10), (AT[0] - 18, AT[1] - 44, 16), (AT[0], AT[1], 14))
shot(tpa - 0.3, t1, (R[0] + 50, R[1] - 46, 30), (R[0] + 24, R[1] + 16, 18), (R[0] + 46, R[1] - 52, 34), (R[0] + 18, R[1] + 10, 14))

# ---------- S6: o atirador (rota pontilhada, lançador em Hodeida, "?") ----------
t0, t1 = S[6]
tcu = T(6, "culpa"); tde = T(6, "destruído"); tho2 = T(6, "houthis", 1); te6 = T(6, "Esse")
for k, r_ in enumerate(ROTA):
    tt = tcu + 0.03 * k; visivel(r_, tt, S[7][0]); pop(r_, tt, 1.0, 0.2)
for k in range(3): explosao((HD[0], HD[1], 2.0), tde + 0.2 + 0.35 * k, r=9, n=12)
LANC.keyframe_insert("scale", frame=f(tde + 0.3)); LANC.scale = (0.001,) * 3; LANC.keyframe_insert("scale", frame=f(tde + 0.6))
destroco = []
for k in range(8):
    d_ = caixa(_id("destroco"), (HD[0] + random.uniform(-4, 4), HD[1] + random.uniform(-4, 4), 0.3), (random.uniform(0.6, 1.6), random.uniform(0.6, 1.6), 0.5), (0.25, 0.24, 0.22, 1))
    d_.rotation_euler = (0, 0, random.uniform(0, 3)); visivel(d_, tde + 0.5, S[7][0])
fum_hd = coluna_fumaca("fumHD", (HD[0], HD[1], 1.0), altura=18, raio=2.4, t0=tde, t_fim=S[7][0], n=12)
for o in fum_hd: visivel(o, tde + 0.4, S[7][0])
visivel(interrog, tho2 - 0.1, S[7][0]); pop(interrog, tho2 - 0.1, 1.0, 0.4)
piv_q.rotation_euler = (0, 0, 0); piv_q.keyframe_insert("rotation_euler", frame=f(tho2), index=2)
piv_q.rotation_euler = (0, 0, math.radians(360)); piv_q.keyframe_insert("rotation_euler", frame=f(S[7][0]), index=2)
shot(t0, tde - 0.6, (30, -420, 110), (-20, -200, 0), (20, -410, 120), (-20, -190, 0))
shot(tde - 0.6, t1, (HD[0] + 26, HD[1] - 34, 16), (HD[0], HD[1], 4), (HD[0] + 22, HD[1] - 28, 15), (HD[0], HD[1], 5))

# ---------- S7: Abqaiq 2019 — barris caem em dominó (6 de 10) ----------
t0, t1 = S[7]
tcin = T(7, "cinco"); tme = T(7, "metade"); tdo = T(7, "dominó")
for k, pv in enumerate(DOM[:6]):
    tt = tcin + 0.18 * k
    pv.rotation_euler = (0, 0, 0); pv.keyframe_insert("rotation_euler", frame=f(tt), index=1)
    pv.rotation_euler = (0, math.radians(88), 0); pv.keyframe_insert("rotation_euler", frame=f(tt + 0.35), index=1)
MARC_DOM = []
for k, pv in enumerate(DOM):
    m_ = esfera(_id("domMarca"), (pv.location[0] - 1.0, pv.location[1], 4.2), 0.5, VERMELHO if k < 6 else (0.25, 0.90, 0.40, 1), sub=2, unico="alerta" if k < 6 else "ok")
    visivel(m_, tme, S[8][0]); pop(m_, tme + 0.05 * k, 1.0, 0.2)
shot(t0, tcin - 0.3, (AB[0] + 30, AB[1] - 90, 60), (AB[0], AB[1], 4), (AB[0] + 20, AB[1] - 84, 50), (AB[0] - 6, AB[1] - 10, 4))
shot(tcin - 0.3, t1, (DX[0] + 20, DX[1] - 22, 8), (DX[0] + 18, DX[1], 1.5), (DX[0] + 22, DX[1] - 26, 10), (DX[0] + 18, DX[1], 1.5))

# ---------- S8-S9: parabéns (visão geral) + CTA + like ----------
t0, _ = S[8]
shot(t0, S[9][0], (R[0] + 46, R[1] - 96, 50), (R[0] + 14, R[1] - 4, 4), (R[0] + 30, R[1] - 104, 56), (R[0] + 8, R[1] - 4, 4))
shot(S[9][0], FIM, (AT[0] + 40, AT[1] - 50, 18), (AT[0], AT[1], 10), (AT[0] + 50, AT[1] - 40, 22), (AT[0], AT[1], 12))

for ob in (cam, alvo, piv_q):
    for fc in ob.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

for o in bpy.data.objects:   # fumaça não projeta sombra (manchas escuras no chão na prévia)
    if o.name.startswith(("fum", "rota")):
        o.visible_shadow = False
if os.environ.get("REALISTA"):
    HD_ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "hdri")
    bg, sol = modo_realista(os.path.join(HD_, "ceu_por_do_sol_2k.hdr"), samples=int(os.environ.get("AMOSTRAS", "4")), foco=alvo)
    def emissivo(chave, cor, forca):
        for m in bpy.data.materials:
            if any(v == m and k[1] == chave for k, v in _mats.items()):
                b = m.node_tree.nodes.get("Principled BSDF"); b.inputs["Emission Color"].default_value = _lin(cor); b.inputs["Emission Strength"].default_value = forca
    emissivo("fogo", (1.0, 0.45, 0.08, 1), 7.0); emissivo("alerta", VERMELHO, 2.5); emissivo("interrog", AMARELO, 1.4); emissivo("ok", (0.25, 0.90, 0.40, 1), 1.5)
    for j, cor in enumerate((AMARELO, LARANJA, AZUL)): emissivo("gota%d" % j, cor, 1.6)
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
