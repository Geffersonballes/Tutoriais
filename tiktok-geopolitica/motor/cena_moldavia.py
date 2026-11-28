"""Vídeo 28/11 — 'Por que a Moldávia?' (sete drones no céu de um país neutro). Uso:
REALISTA=1 blender -b --factory-startup -P cena_moldavia.py -- <pasta_producao> [preview t1,t2,... | range a,b]
Palcos: CAPITAL (origem, miniatura de Chișinău genérica), VILA (x=600, vilarejo com campos),
MAPA (x=3000, contornos reais por lon/lat — backlog do mapa abstrato da Líbia)."""
import bpy, sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
from lowpoly import *
from lowpoly import _id, _lin, _mats

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
random.seed(2811)
scn.world.color = (0.30, 0.60, 0.95)

MAR = (0.10, 0.36, 0.55, 1); NEUTRO = (0.60, 0.68, 0.50, 1); AZUL = (0.30, 0.52, 0.92, 1)
VERMELHO = (0.92, 0.18, 0.14, 1); AMARELO = (0.98, 0.82, 0.15, 1); ROXO = (0.62, 0.52, 0.80, 1)
MOLD = (0.95, 0.62, 0.25, 1); LARANJA_TR = (0.85, 0.30, 0.20, 1); CAMPO = (0.80, 0.72, 0.40, 1)

def pulsos(loc, t, R, cor, n=3, gap=0.4, dur=1.2, unico=None):
    for k in range(n):
        tt = t + gap * k
        o = anel(_id("pulso"), loc, R, R * 0.025 + 0.2, cor, seg=48, unico=unico)
        visivel(o, tt, tt + dur)
        o.scale = (0.05,) * 3; o.keyframe_insert("scale", frame=f(tt)); o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(tt + dur))

def fumaca(loc, t0, t1, r=0.9, cada=0.45, sobe=10.0, vida=2.4, cor=(0.30, 0.30, 0.31, 1)):
    t = t0
    while t < t1:
        o = esfera(_id("fz"), loc, r * random.uniform(0.7, 1.2), cor, sub=1, unico="fumaca")
        visivel(o, t, t + vida)
        o.location = loc; o.keyframe_insert("location", frame=f(t))
        o.location = (loc[0] + random.uniform(-1.5, 1.5) + sobe * 0.2, loc[1] + random.uniform(-1, 1), loc[2] + sobe); o.keyframe_insert("location", frame=f(t + vida))
        o.scale = (0.4,) * 3; o.keyframe_insert("scale", frame=f(t))
        o.scale = (1.6,) * 3; o.keyframe_insert("scale", frame=f(t + vida * 0.7))
        t += cada

def voo(nome, t0, t1, fn, escala=1.0, fim=None):
    d = drone_delta(nome, escala); visivel(d, t0, fim if fim is not None else t1)
    caminho(d, t0, t1, fn, passo=2); girar_helice(d, t0, t1); return d

# câmera
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 26; cam_d.clip_end = 6000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def cam_key(t, loc, tgt):
    for ob, v in ((cam, loc), (alvo, tgt)):
        ob.location = v; ob.keyframe_insert("location", frame=f(t))
def corte(t, loc, tgt):
    for ob in (cam, alvo):
        ad = ob.animation_data
        if ad and ad.action:
            for fc in ad.action.fcurves:
                ant = [kp for kp in fc.keyframe_points if kp.co[0] < f(t)]
                if ant: max(ant, key=lambda kp: kp.co[0]).interpolation = "CONSTANT"
    cam_key(t, loc, tgt)

# =====================================================================
# PALCO 1 — CAPITAL (miniatura genérica): praça central, avenidas, prédios, parque
# =====================================================================
chao = caixa("chaoCidade", (0, 0, -0.2), (500, 500, 0.4), C["grama"])
for k in (-1, 0, 1):
    caixa(_id("aveX"), (0, k * 28, 0.02), (300, 6, 0.1), C["rua"], unico="rua")
    caixa(_id("aveY"), (k * 28, 0, 0.02), (6, 300, 0.1), C["rua"], unico="rua")
praca = caixa("praca", (0, 0, 0.05), (18, 18, 0.12), (0.82, 0.80, 0.74, 1))
arco = caixa("arcoPraca", (0, 6, 3.5), (6, 1.2, 7), (0.90, 0.88, 0.80, 1))
filho(arco, caixa(_id("arcoTopo"), (0, 0, 3.8), (7, 1.6, 0.8), (0.80, 0.78, 0.70, 1)))
for _ in range(110):
    x = random.uniform(-110, 110); y = random.uniform(-110, 110)
    if abs(x) < 12 and abs(y) < 12: continue
    if -60 < x < 0 and -110 < y < -20: continue   # corredor da câmera do gancho
    if min(abs(x - k * 28) for k in (-1, 0, 1)) < 6 or min(abs(y - k * 28) for k in (-1, 0, 1)) < 6: continue
    predio((x, y), random.uniform(5, 9), random.uniform(5, 9), random.uniform(5, 22), random.choice(PREDIOS))
for _ in range(40):
    arvore((random.uniform(-40, -14), random.uniform(-40, -14)), random.uniform(0.9, 1.4))
for k in range(8):
    arvore((-9 + (k % 4) * 6, -9 + (k // 4) * 18), 1.0)
radar_tel, gir_tel = radar("radarTelhado", (36, -36, 18.0)); predio((36, -36), 8, 8, 17, PREDIOS[1])
girar(gir_tel, 0.0, rps=0.4)
for _ in range(6): nuvem((random.uniform(-120, 120), random.uniform(40, 160), random.uniform(55, 75)), random.uniform(2.0, 3.2))

# =====================================================================
# PALCO 2 — VILA (x = VX): casas, campos arados, estrada de terra
# =====================================================================
VX = 600
caixa("chaoVila", (VX, 0, -0.2), (400, 400, 0.4), C["grama"])
for i in range(6):
    for j in range(3):
        caixa(_id("campo"), (VX - 75 + i * 30, 40 + j * 24, 0.03), (27, 21, 0.1), random.choice([CAMPO, (0.62, 0.50, 0.32, 1), C["grama2"]]), unico="campo%d" % ((i + j) % 3))
caixa("estradaVila", (VX, 0, 0.02), (240, 5, 0.1), (0.66, 0.56, 0.42, 1))
casas = []
for k in range(16):
    x = VX - 70 + (k % 8) * 20 + random.uniform(-3, 3); y = -14 if k < 8 else 14
    casas.append(casa_vila(_id("casa"), (x, y + random.uniform(-2, 2)), rot=math.radians(0 if k < 8 else 180) + random.uniform(-0.15, 0.15),
                           teto=random.choice([(0.72, 0.30, 0.20, 1), (0.30, 0.42, 0.55, 1), (0.55, 0.55, 0.58, 1)])))
for _ in range(50):
    arvore((VX + random.uniform(-110, 110), random.choice([-1, 1]) * random.uniform(24, 34) if random.random() < 0.5 else random.uniform(-80, -40)), random.uniform(0.9, 1.5))
igreja = caixa("igrejaVila", (VX + 95, -62, 4), (6, 9, 8), (0.95, 0.94, 0.90, 1))
filho(igreja, cilindro(_id("torreIgreja"), (0, -3, 7), 1.6, 6, (0.95, 0.94, 0.90, 1), seg=8))
filho(igreja, cilindro(_id("cupula"), (0, -3, 11), 1.6, 2.4, (0.85, 0.70, 0.25, 1), seg=8, r2=0.1))

# =====================================================================
# PALCO 3 — MAPA (x = MX). 8 unidades por grau, centro em 28.5 E / 47 N
# =====================================================================
MX = 3000
def M(lon, lat, z=0.0): return (MX + (lon - 28.5) * 8, (lat - 47.0) * 8, z)
mapa = [caixa("marMapa", (MX, 0, -0.3), (2400, 2000, 0.4), MAR, unico="marMapa")]
mapa.append(caixa("terraBase", (MX, 60, 0.4), (1400, 700, 0.8), NEUTRO, unico="terraBase"))
NEGRO = [(28.6, 43.75), (27.9, 43.2), (27.6, 42.5), (28.0, 41.6), (29.1, 41.2), (31.4, 41.1), (33.5, 42.0), (35.2, 42.0),
         (36.5, 41.3), (38.5, 40.9), (41.5, 41.4), (41.6, 42.6), (40.0, 43.4), (38.5, 44.4), (37.4, 44.7), (36.6, 45.2),
         (35.5, 45.1), (34.4, 44.5), (33.5, 44.5), (32.6, 45.3), (33.6, 46.0), (32.0, 46.5), (30.7, 46.4), (29.7, 45.2),
         (29.6, 44.8), (28.8, 44.5)]
mapa.append(prisma_ll("marNegro", NEGRO, M, z=0.45, h=0.86, cor=MAR, unico="marNegro"))
AZOV = [(35.0, 46.3), (35.5, 45.4), (36.6, 45.4), (38.2, 46.3), (39.3, 47.2), (38.2, 47.1), (35.0, 46.6)]
mapa.append(prisma_ll("marAzov", AZOV, M, z=0.45, h=0.86, cor=MAR, unico="marNegro"))
MOLDAVIA = [(26.62, 48.26), (27.6, 48.47), (28.1, 48.24), (28.6, 48.15), (29.2, 47.98), (29.2, 47.45), (29.55, 47.3),
            (29.6, 46.9), (30.1, 46.45), (29.7, 46.2), (28.95, 46.47), (28.95, 46.0), (28.6, 45.5), (28.2, 45.47),
            (28.1, 45.6), (28.15, 46.2), (27.6, 47.0), (27.2, 47.6)]
TRANSN = [(28.4, 48.1), (28.75, 48.12), (29.2, 47.98), (29.2, 47.45), (29.55, 47.3), (29.6, 46.9), (30.05, 46.5),
          (29.75, 46.4), (29.4, 46.6), (29.15, 46.95), (28.9, 47.3), (28.6, 47.7)]
ROMENIA = [(22.0, 47.9), (23.5, 48.0), (24.9, 47.75), (26.62, 48.26), (27.2, 47.6), (27.6, 47.0), (28.15, 46.2),
           (28.1, 45.6), (28.2, 45.47), (29.7, 45.2), (28.7, 44.35), (28.6, 43.75), (27.0, 44.15), (25.4, 43.65),
           (22.7, 43.9), (22.0, 44.6), (20.3, 46.15), (21.0, 46.4)]
UCRANIA = [(22.15, 48.4), (22.9, 48.0), (24.9, 47.75), (26.62, 48.26), (27.6, 48.47), (28.1, 48.24), (28.6, 48.15),
           (29.2, 47.98), (29.2, 47.45), (29.55, 47.3), (29.6, 46.9), (30.1, 46.45), (29.7, 46.2), (28.95, 46.47),
           (28.95, 46.0), (28.6, 45.5), (28.2, 45.47), (29.7, 45.2), (30.7, 46.4), (31.7, 46.6), (33.0, 46.1),
           (35.0, 46.6), (38.2, 47.1), (40.0, 48.0), (40.2, 49.6), (38.0, 50.0), (35.4, 50.6), (34.0, 52.3),
           (32.0, 52.1), (30.5, 51.3), (28.0, 51.6), (25.0, 51.9), (23.6, 51.5), (24.0, 50.5), (22.6, 49.1)]
ucr = prisma_ll("ucrania", UCRANIA, M, z=0.7, h=1.6, cor=AZUL, unico="ucrania"); mapa.append(ucr)
rom = prisma_ll("romenia", ROMENIA, M, z=0.7, h=1.6, cor=ROXO, unico="romenia"); mapa.append(rom)
mol = prisma_ll("moldavia", MOLDAVIA, M, z=0.9, h=2.0, cor=MOLD, unico="moldavia"); mapa.append(mol)
trn = prisma_ll("transnistria", TRANSN, M, z=1.0, h=2.2, cor=MOLD, unico="transnistria"); mapa.append(trn)
BRANCO = (0.98, 0.98, 0.98, 1)
txt_ucr = texto3d("txtUcrania", "UCRÂNIA", M(32.5, 49.3, 2.2), tam=9, cor=BRANCO, unico="txtMapa")
txt_rom = texto3d("txtRomenia", "ROMÊNIA", M(24.6, 45.9, 2.2), tam=9, cor=BRANCO, unico="txtMapa")
txt_mol = texto3d("txtMoldavia", "MOLDÁVIA", M(28.0, 47.25, 2.6), tam=4.2, cor=(0.10, 0.10, 0.12, 1), unico="txtMold")
txt_mar = texto3d("txtMarNegro", "MAR NEGRO", M(33.0, 43.6, 1.4), tam=7, cor=(0.80, 0.90, 1.0, 1), unico="txtMar")
def pino(nome, lon, lat, cor, alt=5.0):
    p = cilindro(nome, M(lon, lat, 1.9 + alt / 2), 0.35, alt, C["escuro"], seg=6)
    filho(p, esfera(_id("pinoC"), (0, 0, alt / 2 + 1.0), 1.4, cor, sub=1)); return p
p_chi = pino("pinoChisinau", 28.86, 47.01, BRANCO)
p_ods = pino("pinoOdesa", 30.73, 46.48, AZUL)
def cm(lon, lat, alt):
    alt = alt * 0.5 if alt >= 100 else alt   # prévia 28/11: mapa pequeno demais no quadro
    x, y, _ = M(lon, lat); return (x, y - alt * 0.32, alt), (x, y, 0)
def cam_mapa(t, lon, lat, alt, seco=False): (corte if seco else cam_key)(t, *cm(lon, lat, alt))
def xis(nome, loc, t, fim, tam=10, cor=VERMELHO):
    a = caixa(nome + "a", loc, (tam, tam * 0.16, 1.0), cor, unico="xis"); a.rotation_euler = (0, 0, math.radians(45))
    b = caixa(nome + "b", (0, 0, 0), (tam, tam * 0.16, 1.0), cor, unico="xis"); filho(a, b); b.rotation_euler = (0, 0, math.radians(90))
    visivel(a, t, fim); pop(a, t); return a
def trilha_ll(nome, pts, t0, dur, cor, r=0.5, n=30, fim=None, z=3.0):
    P = [Vector(M(lo, la, z)) for lo, la in pts]
    sl = [(P[i + 1] - P[i]).length for i in range(len(P) - 1)]; tot = sum(sl)
    for k in range(n):
        d = tot * k / (n - 1); i = 0
        while i < len(sl) - 1 and d > sl[i]: d -= sl[i]; i += 1
        p = P[i].lerp(P[i + 1], min(1, d / sl[i]))
        o = esfera(_id(nome), tuple(p), r, cor, sub=1, unico=nome); tt = t0 + dur * k / n; visivel(o, tt, fim); pop(o, tt, dur=0.2)
# bolha de neutralidade (anel branco grosso em volta da Moldávia)
bolha = anel("bolhaNeutra", M(28.4, 46.95, 2.6), 17, 0.7, BRANCO, seg=64, unico="bolha"); bolha.scale = (0.85, 1.25, 1)

# =====================================================================
# 0 — GANCHO: 7 drones cruzam o céu da capital; um passa sobre a praça. Depois, o mapa.
# =====================================================================
t0, t1 = S[0]
T_MAPA = T(0, "Por") - 0.1
for k in range(7):
    tt0 = 0.0 + k * 0.3
    a = (-46 + k * 13, 110, 30 + k * 1.2); b = (-20 + k * 7, -150, 22 + k)
    voo(f"dGancho{k}", tt0, tt0 + 4.2, lambda u, a=a, b=b: lerp(a, b, u), escala=2.6, fim=T_MAPA)
heroi_fn = lambda u: lerp((16, 60, 16), (-24, -90, 12), u)
d_heroi = voo("dHeroi", 3.0, 6.5, heroi_fn, escala=2.4, fim=T_MAPA)
pulsos((0, 0, 0.4), T(0, "capital"), 30, VERMELHO, n=3, unico="pulsoAlerta")
cam_key(t0, (-30, -70, 10), (0, 20, 26)); cam_key(T(0, "Um"), (-24, -54, 10), (0, 0, 16))
cam_key(T(0, "capital"), (-16, -34, 10), (0, 0, 10)); cam_key(T(0, "guerra"), (-26, -44, 30), (0, 0, 4))
# mapa: Moldávia acende
cam_mapa(T_MAPA, 28.5, 47.0, 220, seco=True); cam_mapa(T(0, "Peça"), 28.5, 47.0, 150); cam_mapa(t1 - 0.05, 28.5, 47.0, 135)
destacar(mol.data.materials[0], T(0, "Moldávia") + 0.1, MOLD)
visivel(txt_mol, T_MAPA, S[7][1]); visivel(txt_mar, T_MAPA, S[7][1])
visivel_janelas(p_chi, [(T_MAPA, t1), (S[6][0], S[7][1])])

# =====================================================================
# 1 — GEOGRAFIA: espremida entre Ucrânia e Romênia
# =====================================================================
t0, t1 = S[1]
visivel_janelas(txt_ucr, [(T(1, "Ucrânia") - 0.1, S[1][1]), (S[4][0], S[4][1])])
visivel_janelas(txt_rom, [(T(1, "Romênia") - 0.1, S[1][1])])
pop(txt_ucr, T(1, "Ucrânia") - 0.1); pop(txt_rom, T(1, "Romênia") - 0.1)
destacar(ucr.data.materials[0], T(1, "Ucrânia"), AZUL)
destacar(rom.data.materials[0], T(1, "Romênia"), ROXO)
# "espremido": duas setas empurrando dos lados
for nome, lon, ang in (("setaO", 25.2, 90), ("setaL", 31.8, -90)):
    s = seta3d(nome, 14, AMARELO); s.location = M(lon, 47.0, 4.0); s.rotation_euler = (0, math.radians(ang), 0)
    visivel(s, T(1, "espremido"), T(1, "Essa")); pop(s, T(1, "espremido"))
destacar(mol.data.materials[0], T(1, "Moldávia"), MOLD)
cam_mapa(t0, 28.0, 47.2, 330, seco=True); cam_mapa(T(1, "Ucrânia"), 30.0, 48.0, 380)
cam_mapa(T(1, "Romênia"), 26.0, 46.6, 380); cam_mapa(T(1, "Essa"), 28.4, 47.0, 170); cam_mapa(t1 - 0.05, 28.4, 47.0, 160)

# =====================================================================
# 2 — NEUTRALIDADE: a Constituição de 1994 + bolha; tropas estrangeiras barradas
# =====================================================================
t0, t1 = S[2]
doc, selo = documento("constituicao", (0, 0), w=4.5, d=6.0)
doc.location = M(28.4, 46.7, 2.0); selo.location = (doc.location.x + 1.1, doc.location.y - 2.0, doc.location.z + 1.66)
visivel(doc, T(2, "Constituição"), T(2, "estrangeiras")); visivel(selo, T(2, "neutro"), T(2, "estrangeiras"))
pop(doc, T(2, "Constituição")); pop(selo, T(2, "neutro"))
visivel_janelas(bolha, [(T(2, "neutro"), S[2][1]), (S[7][0], S[7][1])]); pop(bolha, T(2, "neutro"), escala=1.0)
for k, (lo, la, ang) in enumerate(((31.0, 47.6, 120), (31.2, 46.6, 70))):
    c, _ = caminhao(f"tropa{k}", M(lo, la, 3.0), cor=(0.40, 0.45, 0.25, 1), tubos=False); c.scale = (1.4,) * 3
    c.rotation_euler = (0, 0, math.radians(ang)); tt = T(2, "tropas")
    visivel(c, tt - 0.2, t1)
    caminho(c, tt - 0.2, tt + 1.0, lambda u, lo=lo, la=la, k=k: lerp(M(lo, la, 3.0), M(lo - 0.9, la - 0.1 * (k - 0.5), 3.0), suave(u)), orientar=False)
    xis(f"xisTropa{k}", M(lo - 1.0, la - 0.1 * (k - 0.5), 5.0), T(2, "estrangeiras"), t1, tam=9)
cam_mapa(t0, 28.6, 46.9, 120, seco=True); cam_mapa(T(2, "neutro"), 28.8, 47.0, 165); cam_mapa(t1 - 0.05, 29.4, 47.0, 175)

# =====================================================================
# 3 — O ESPINHO: Transnístria (faixa no leste) com soldados russos
# =====================================================================
t0, t1 = S[3]
m_tr = trn.data.materials[0]
cor_key(m_tr, T(3, "região") - 0.05, MOLD); cor_key(m_tr, T(3, "separatista") + 0.2, LARANJA_TR)
cor_key(m_tr, S[4][1] - 0.2, LARANJA_TR); cor_key(m_tr, S[4][1] + 0.3, MOLD)
txt_tr = texto3d("txtTransn", "TRANSNÍSTRIA", M(30.6, 47.75, 3.4), tam=2.6, cor=BRANCO, unico="txtMapa")
txt_tr.rotation_euler = (0, 0, math.radians(-55)); visivel(txt_tr, T(3, "Transnístria"), t1); pop(txt_tr, T(3, "Transnístria"))
for k in range(6):
    lo = 29.0 + 0.16 * k; la = 47.55 - 0.18 * k
    sd, _, _ = boneco(f"soldado{k}", M(lo, la, 3.2), camisa=(0.40, 0.45, 0.25, 1)); sd.scale = (0.9,) * 3
    tt = T(3, "soldados") + 0.12 * k; visivel(sd, tt, t1); pop(sd, tt, escala=0.9)
for k in range(2):
    c, _ = caminhao(f"blindTr{k}", M(29.25 + 0.4 * k, 47.05 - 0.3 * k, 3.6), cor=(0.40, 0.45, 0.25, 1), tubos=False); c.scale = (0.6,) * 3
    c.rotation_euler = (0, 0, math.radians(-30)); tt = T(3, "russos"); visivel(c, tt, t1); pop(c, tt, escala=0.6)
pulsos(M(29.3, 47.0, 3.4), T(3, "Esse"), 12, VERMELHO, n=2, unico="pulsoAlerta")
cam_mapa(t0, 29.0, 47.1, 120, seco=True); cam_mapa(T(3, "Transnístria"), 29.3, 47.0, 70); cam_mapa(T(3, "soldados"), 29.3, 47.1, 42)
cam_mapa(t1 - 0.05, 29.4, 47.0, 55)

# =====================================================================
# 4 — TRANSBORDAMENTO: drones rumo à Ucrânia (Odesa) cortam o céu moldavo
# =====================================================================
t0, t1 = S[4]
rotas = [[(36.5, 44.0), (32.5, 45.6), (30.75, 46.5)],
         [(37.0, 44.4), (32.0, 46.0), (30.2, 46.2), (29.6, 46.1), (28.7, 46.3), (29.0, 47.0), (30.6, 46.6)],
         [(37.5, 45.0), (33.0, 46.5), (30.0, 46.0), (28.5, 45.9), (28.3, 46.6), (29.8, 47.1)],
         [(36.0, 43.6), (31.5, 45.4), (30.8, 46.3)]]
for k, rota in enumerate(rotas):
    P = [Vector(M(lo, la, 6.0)) for lo, la in rota]
    def fn(u, P=P):
        n = len(P) - 1; x = u * n; i = min(int(x), n - 1); return tuple(P[i].lerp(P[i + 1], x - i))
    tt0 = t0 + 0.4 + 0.5 * k; tt1 = min(t1, tt0 + 5.0)
    voo(f"dRota{k}", tt0, tt1, fn, escala=3.2, fim=t1)
    trilha_ll(f"trilhaRota{k}", rota, tt0, tt1 - tt0, VERMELHO if k in (1, 2) else (0.85, 0.85, 0.85, 1), n=34, fim=t1, z=3.0)
    if k in (0, 3): explosao(M(rota[-1][0], rota[-1][1], 4.0), tt1, r=8, n=12)
visivel(p_ods, t0, t1)
pulsos(M(28.5, 46.6, 3.0), T(4, "céu"), 26, VERMELHO, n=3, unico="pulsoAlerta")
cam_mapa(t0, 31.0, 46.3, 330, seco=True); cam_mapa(T(4, "Drones"), 30.2, 46.5, 300); cam_mapa(t1 - 0.05, 29.3, 46.7, 230)

# =====================================================================
# 5 — O ALERTA (17/11): vila, drones caem perto das casas; céu fechado (avião em espera)
# =====================================================================
t0, t1 = S[5]
quedas = [(VX - 50, 30), (VX - 15, 44), (VX + 20, 32), (VX + 50, 46), (VX + 80, -34)]
ts_q = [T(5, "cinco") + 0.25 * k for k in range(5)]
for k, ((qx, qy), tq) in enumerate(zip(quedas, ts_q)):
    a = (qx - 70, qy - 90, 40); b = (qx, qy, 0.8)
    voo(f"dQueda{k}", T(5, "sete") - 0.3 + 0.15 * k, tq, lambda u, a=a, b=b: lerp(a, b, u ** 1.3), escala=1.4)
    explosao((qx, qy, 1.5), tq, r=7, n=14)
    fumaca((qx, qy, 1.0), tq, t1, r=1.3, cada=0.6, sobe=12)
for k in range(2):  # os outros dois seguem viagem
    a = (VX - 160, -120 + k * 30, 46); b = (VX + 160, 140 + k * 20, 50)
    voo(f"dPassa{k}", T(5, "sete"), T(5, "sete") + 6.0, lambda u, a=a, b=b: lerp(a, b, u), escala=1.4)
av = aviao("aviaoEspera", cor=(0.95, 0.95, 0.96, 1)); av.scale = (1.6,) * 3
visivel(av, T(5, "céu"), t1)
caminho(av, T(5, "céu"), t1, lambda u: (VX + math.cos(u * 3.4) * 70, 20 + math.sin(u * 3.4) * 50, 70), passo=2)
fechado = anel("anelFechado", (VX, 30, 60), 95, 1.2, VERMELHO, seg=64, unico="pulsoAlerta")
visivel(fechado, T(5, "fechado") - 0.2, t1); pop(fechado, T(5, "fechado") - 0.2)
corte(t0, (VX - 30, -110, 40), (VX, 40, 10))
cam_key(T(5, "cinco"), (VX - 5, -48, 22), (VX + 5, 30, 3))
cam_key(T(5, "céu"), (VX - 40, -100, 52), (VX, 40, 30))
cam_key(t1 - 0.05, (VX - 60, -130, 70), (VX, 40, 34))

# =====================================================================
# 6 — O IMPASSE: destroços no campo; Chișinău acusa, Moscou nega (seta azul x seta vermelha)
# =====================================================================
t0, t1 = S[6]
destroco = drone_delta("destroco", 2.6); destroco.location = (VX + 20, 32, 0.6); destroco.rotation_euler = (math.radians(18), math.radians(-25), math.radians(40))
visivel(destroco, t0, T(6, "Moscou"))
cratera = cilindro("cratera", (VX + 20, 32, 0.06), 5.5, 0.12, (0.25, 0.20, 0.16, 1), seg=16); visivel(cratera, t0, T(6, "Moscou"))
fita = anel("fita", (VX + 20, 32, 1.0), 9, 0.12, AMARELO, seg=24); visivel(fita, t0, T(6, "Moscou"))
for k in range(3):
    pe, bd, _ = boneco(f"perito{k}", (VX + 20 + math.cos(k * 2.1) * 7, 32 + math.sin(k * 2.1) * 7, 0.0), camisa=(0.20, 0.30, 0.55, 1), capacete=False)
    pe.rotation_euler = (0, 0, k * 2.1 + math.pi / 2); visivel(pe, t0, T(6, "Moscou"))
radar_vazio = cilindro("plataformaVazia", (VX + 40, 22, 0.6), 2.4, 1.2, C["cinza"], seg=10)
visivel(radar_vazio, T(6, "defesa"), T(6, "Moscou")); pop(radar_vazio, T(6, "defesa"))
xis("xisDefesa", (VX + 40, 22, 4.0), T(6, "drones"), T(6, "Moscou"), tam=6)
corte(t0, (VX + 0, 0, 14), (VX + 20, 32, 1.5))
cam_key(T(6, "defesa") - 0.2, (VX + 7, -2, 18), (VX + 27, 28, 2))
# mapa: acusação (seta azul de Chișinău) x rejeição (seta vermelha do leste)
seta_az = seta3d("setaAcusa", 30, (0.25, 0.55, 1.0, 1)); seta_az.location = M(29.2, 47.0, 4.0); seta_az.rotation_euler = (0, math.radians(90), 0)
visivel(seta_az, T(6, "culpa"), t1)
seta_vm = seta3d("setaNega", 30, VERMELHO); seta_vm.location = M(35.0, 48.2, 4.0); seta_vm.rotation_euler = (0, math.radians(-90), 0)
visivel(seta_vm, T(6, "Moscou"), t1); pop(seta_vm, T(6, "Moscou"))
interrog = texto3d("txtInterrog", "?", M(32.1, 47.6, 6.0), tam=14, cor=AMARELO, espessura=1.2, unico="txtInterrog")
visivel(interrog, T(6, "prova"), t1); pop(interrog, T(6, "prova"))
cam_mapa(T(6, "Moscou") - 0.05, 31.6, 47.4, 280, seco=True); cam_mapa(t1 - 0.05, 31.8, 47.4, 300)

# =====================================================================
# 7 — O DILEMA: radares chegam de parceiros, a bolha neutra continua
# =====================================================================
t0, t1 = S[7]
for k, (lo, la) in enumerate(((28.0, 47.6), (28.6, 46.6), (28.35, 47.15))):
    rb, rg = radar(f"radarParc{k}", M(lo, la, 2.6)); rb.scale = (1.6,) * 3; girar(rg, t0, rps=0.6)
    a = M(lo - 4.0, la - 0.4, 14.0); b = M(lo, la, 2.6); tt = T(7, "ajuda") + 0.35 * k
    visivel(rb, tt - 0.6, t1); caminho(rb, tt - 0.6, tt + 0.6, lambda u, a=a, b=b: lerp(a, b, suave(u)), orientar=False)
pulsos(M(28.4, 46.95, 3.0), T(7, "neutra"), 20, BRANCO, n=2, unico="pulsoBranco")
cam_mapa(t0, 27.4, 46.9, 190, seco=True); cam_mapa(T(7, "parceiros"), 28.0, 46.95, 170); cam_mapa(t1 - 0.05, 28.4, 47.0, 150)

# =====================================================================
# 8/9 — FINAL: a capital ao entardecer, radar girando no telhado, câmera sobe
# =====================================================================
t0 = S[8][0]; tF = FIM
corte(t0, (-40, -70, 16), (0, 0, 6))
cam_key(S[9][0], (-20, -90, 40), (0, 0, 2))
cam_key(tF, (30, -120, 80), (0, 10, 0))

# ---------- render ----------
if os.environ.get("REALISTA"):
    HD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "hdri")
    bg, sol = modo_realista(os.path.join(HD, "ceu_parcialmente_nublado_2k.hdr"), samples=int(os.environ.get("AMOSTRAS", "4")), foco=alvo)
    for nome in ("marMapa", "marNegro"):
        for k, v in _mats.items():
            if k[1] == nome:
                b = v.node_tree.nodes.get("Principled BSDF"); b.inputs["Roughness"].default_value = 0.25
    for m in bpy.data.materials:   # explosões com emissão baixa (backlog 10)
        if tuple(round(c, 3) for c in m.diffuse_color) == tuple(round(c, 3) for c in C["laranja"]):
            b = m.node_tree.nodes.get("Principled BSDF"); b.inputs["Emission Color"].default_value = _lin((1.0, 0.42, 0.06, 1)); b.inputs["Emission Strength"].default_value = 1.2
    for chave, cor in (("pulsoAlerta", VERMELHO), ("pulsoBranco", BRANCO), ("txtMapa", BRANCO), ("bolha", BRANCO)):
        for k, v in _mats.items():
            if k[1] == chave:
                b = v.node_tree.nodes.get("Principled BSDF"); b.inputs["Emission Color"].default_value = _lin(cor); b.inputs["Emission Strength"].default_value = 0.8
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
