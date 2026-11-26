"""Vídeo 26/11 — 'Como a guerra da Ucrânia chegou à África?' (drones navais em Benghazi, Líbia). Uso:
REALISTA=1 blender -b --factory-startup -P cena_libia.py -- <pasta_producao> [preview t1,t2,... | range a,b]
Palcos: PORTO (origem, Benghazi em miniatura, mar com ondas), MAPA (x=3000, Mediterrâneo + Mar Negro)."""
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
random.seed(2626)
scn.world.color = (0.30, 0.60, 0.95)

AREIA = (0.86, 0.74, 0.52, 1); AREIA2 = (0.80, 0.68, 0.48, 1); CONC = (0.78, 0.77, 0.74, 1)
MAR = (0.10, 0.36, 0.55, 1); VERDE_EU = (0.52, 0.70, 0.40, 1); AZUL = (0.25, 0.50, 0.95, 1)
VERMELHO = (0.92, 0.18, 0.14, 1); LARANJA_LNA = (0.95, 0.55, 0.20, 1); AMARELO = (0.98, 0.82, 0.15, 1)

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

def pulsos(loc, t, R, cor, n=3, gap=0.4, dur=1.2, unico=None):
    for k in range(n):
        tt = t + gap * k
        o = anel(_id("pulso"), loc, R, R * 0.025 + 0.2, cor, seg=48, unico=unico)
        visivel(o, tt, tt + dur)
        o.scale = (0.05,) * 3; o.keyframe_insert("scale", frame=f(tt)); o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(tt + dur))

def esteira(fn, t0, t1, r=0.35, cada=0.14):
    rastro(fn, t0, t1, (0.95, 0.97, 1.0, 1), r=r, cada=cada, vida=1.4)

# câmera
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 26; cam_d.clip_end = 6000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def cam_key(t, loc, tgt):
    for ob, v in ((cam, loc), (alvo, tgt)):
        ob.location = v; ob.keyframe_insert("location", frame=f(t))
def corte(t, loc, tgt):  # corte seco: a chave anterior vira CONSTANT (segura o plano e salta em t)
    for ob in (cam, alvo):
        ad = ob.animation_data
        if ad and ad.action:
            for fc in ad.action.fcurves:
                ant = [kp for kp in fc.keyframe_points if kp.co[0] < f(t)]
                if ant: max(ant, key=lambda kp: kp.co[0]).interpolation = "CONSTANT"
    cam_key(t, loc, tgt)

# =====================================================================
# PALCO 1 — PORTO DE BENGHAZI (miniatura). Mar em y < -4, cais e cidade em y > -4.
# =====================================================================
mar = mar_ondulado("mar", (0, -160, 0.0), (700, 320), MAR, res=220, altura=0.45, escala_onda=5.0, t_fim=FIM)
terra = caixa("terra", (0, 110, 0.6), (700, 220, 1.6), AREIA)
cais = caixa("cais", (0, -2.0, 0.7), (90, 4.0, 1.4), CONC)
molhe = caixa("molhe", (-46, -22, 0.7), (4, 44, 1.4), CONC)
for k in range(10):   # cabeços de amarração
    cilindro(_id("cabeco"), (-40 + k * 9, -3.6, 1.6), 0.25, 0.4, C["escuro"], seg=8)
for k in range(3):    # guindastes do porto
    gx = -25 + k * 22
    caixa(_id("guiP"), (gx, 2.5, 6), (0.8, 0.8, 10), AMARELO)
    caixa(_id("guiB"), (gx, -1.0, 11), (0.6, 9, 0.6), AMARELO)
for k in range(4):    # armazéns
    caixa(_id("armz"), (-30 + k * 16, 9, 2.8), (12, 6, 3), random.choice([(0.82, 0.80, 0.74, 1), (0.70, 0.74, 0.78, 1)]))
for _ in range(60):   # cidade
    x = random.uniform(-90, 90); y = random.uniform(16, 70)
    predio((x, y), random.uniform(3, 6), random.uniform(3, 6), random.uniform(3, 12) + 1.4, random.choice(PREDIOS))
for _ in range(16):
    tr = arvore((random.uniform(-80, 80), random.uniform(13, 15)), 0.9); tr.location.z += 1.4
for k in range(6):    # contêineres coloridos no cais
    caixa(_id("cont"), (20 + (k % 3) * 3.0, 1.0 + (k // 3) * 1.4, 2.0), (2.6, 1.2, 1.2), random.choice([VERMELHO, AZUL, (0.2, 0.6, 0.3, 1), LARANJA_LNA]))

# corveta atracada (a do gancho afunda; a "intacta" aparece no 'porto amigo')
corvA = corveta("corvetaA", 1.4); corvA.location = (0, -6.6, 0.55); corvA.rotation_mode = "XYZ"; corvA.rotation_euler = (0, 0, math.radians(-90))
corvB = corveta("corvetaB", 1.4); corvB.location = (0, -6.6, 0.55); corvB.rotation_euler = (0, 0, math.radians(-90))
carga = petroleiro("cargueiro", cor_casco=(0.20, 0.30, 0.45, 1), escala=1.2); carga.location = (-28, -8.5, 0.4); carga.rotation_euler = (0, 0, math.radians(-90))

# =====================================================================
# PALCO 2 — MAPA (x = MX). 8 unidades por grau.
# =====================================================================
MX = 3000
def M(lon, lat, z=0.0): return (MX + (lon - 22) * 8, (lat - 38) * 8, z)
def terra_ll(nome, lon0, lon1, lat0, lat1, cor, z=0.6, h=1.6, unico=None):
    a = M(lon0, lat0); b = M(lon1, lat1)
    return caixa(nome, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z), (b[0] - a[0], b[1] - a[1], h), cor, unico=unico)
mapa = [caixa("marMapa", (MX + 40, 0, -0.3), (700, 520, 0.4), MAR, unico="marMapa")]
mapa += [terra_ll("africa", 0, 50, 10, 31.3, AREIA), terra_ll("cirenaica", 19.5, 24.5, 31.0, 32.8, AREIA),
         terra_ll("tunisia", 8, 11, 31, 37.2, AREIA), terra_ll("levante", 34.6, 50, 29, 37.2, AREIA2),
         terra_ll("anatolia", 26.2, 50, 36.6, 41.2, AREIA2), terra_ll("grecia", 20.0, 26.0, 37.0, 42.0, VERDE_EU),
         terra_ll("balcas", 16.8, 30, 42.0, 46.5, VERDE_EU), terra_ll("europa", -5, 50, 45, 62, VERDE_EU),
         terra_ll("franca", -5, 7.5, 43.2, 46, VERDE_EU), terra_ll("sardenha", 8.2, 9.8, 38.9, 41.2, VERDE_EU),
         terra_ll("espanha", -5, 3, 36.5, 43.5, VERDE_EU), terra_ll("argelia_n", 0, 8, 31, 36.8, AREIA)]
negro = terra_ll("marNegro", 27.6, 41.6, 41.0, 46.6, MAR, z=0.75, h=1.6, unico="marNegro"); mapa.append(negro)
crimeia = terra_ll("crimeia", 32.6, 36.4, 44.4, 46.0, VERDE_EU, z=0.8, h=1.6); mapa.append(crimeia)
# Itália: norte + bota inclinada + Sicília (material próprio para destacar)
ita_n = terra_ll("italiaN", 7.0, 13.6, 43.6, 46.2, VERDE_EU, z=0.7, unico="italia")
bota_a = Vector(M(11.8, 44.0)); bota_b = Vector(M(16.4, 38.3)); dv = bota_b - bota_a
bota = caixa("italiaBota", tuple((bota_a + bota_b) / 2) [:2] + (0.7,), (2.3 * 8, dv.length, 1.6), VERDE_EU, unico="italia")
bota.rotation_euler = (0, 0, math.atan2(dv.y, dv.x) - math.pi / 2)
sicilia = terra_ll("sicilia", 12.4, 15.6, 36.7, 38.2, VERDE_EU, z=0.7, unico="italia")
mapa += [ita_n, bota, sicilia]
ucr = terra_ll("ucrania", 22.2, 40.2, 46.6, 52.3, AZUL, z=0.75, h=1.6, unico="ucrania"); mapa.append(ucr)
lna = terra_ll("libiaLeste", 19.5, 25.0, 22.0, 32.85, AREIA, z=0.75, h=1.6, unico="libiaLeste"); mapa.append(lna)
siria = terra_ll("siria", 35.7, 42.0, 32.5, 37.2, AREIA2, z=0.75, h=1.6, unico="siria"); mapa.append(siria)
def pino(nome, lon, lat, cor):
    p = cilindro(nome, M(lon, lat, 6.0), 0.9, 9.0, C["escuro"], seg=6)
    filho(p, esfera(_id("pinoC"), (0, 0, 5.8), 5.0, cor, sub=1)); return p
def cm(lon, lat, alt): x, y, _ = M(lon, lat); return (x, y - alt * 0.30, alt), (x, y, 0)
def cam_mapa(t, lon, lat, alt, seco=False): (corte if seco else cam_key)(t, *cm(lon, lat, alt))
p_bgz = pino("pinoBenghazi", 20.1, 32.1, VERMELHO); p_ods = pino("pinoOdesa", 30.7, 46.5, AZUL)
p_tar = pino("pinoTartus", 35.9, 34.9, VERMELHO); p_rom = pino("pinoRoma", 12.5, 41.9, AMARELO)

def trilha(nome, pts_ll, t0, dur, cor, r=1.5, n=36, fim=None, z=2.2):
    """Linha pontilhada que se desenha ao longo de pontos (lon, lat)."""
    P = [Vector(M(lo, la, z)) for lo, la in pts_ll]
    seg_l = [(P[i + 1] - P[i]).length for i in range(len(P) - 1)]; tot = sum(seg_l)
    obs = []
    for k in range(n):
        d = tot * k / (n - 1); i = 0
        while i < len(seg_l) - 1 and d > seg_l[i]: d -= seg_l[i]; i += 1
        p = P[i].lerp(P[i + 1], min(1, d / seg_l[i]))
        o = esfera(_id(nome), tuple(p), r, cor, sub=1, unico=nome)
        tt = t0 + dur * k / n; visivel(o, tt, fim); pop(o, tt, dur=0.2); obs.append(o)
    return obs

def xis(nome, loc, t, fim, tam=10, cor=VERMELHO):
    a = caixa(nome + "a", loc, (tam, 1.6, 1.0), cor, unico="xis"); a.rotation_euler = (0, 0, math.radians(45))
    b = caixa(nome + "b", (0, 0, 0), (tam, 1.6, 1.0), cor, unico="xis"); filho(a, b); b.rotation_euler = (0, 0, math.radians(90))
    visivel(a, t, fim); pop(a, t); return a

# =====================================================================
# 0 — GANCHO: 7 drones navais atingem a corveta; ela tomba. Depois, o mapa: 2.000 km.
# =====================================================================
t0, t1 = S[0]
T_MAPA = T(0, "dois") - 0.25
visivel_janelas(corvA, [(t0, T_MAPA), (S[4][0], S[4][1])])
visivel_janelas(corvB, [(S[2][0], S[3][1])])
visivel_janelas(carga, [(t0, T_MAPA), (S[2][0], S[4][1]), (S[7][0], FIM)])
impactos = [1.15, 1.45, 1.75, 2.05, 2.35, 2.6, 2.85]
for k in range(7):
    dn = drone_naval(f"dnGancho{k}", 1.3)
    x0 = -26 + k * 8.5; p_a = (x0, -70 + random.uniform(-6, 6), 0.35); p_b = (-9 + k * 3.0, -8.6, 0.35)
    ti = impactos[k]
    visivel(dn, t0, ti)
    caminho(dn, t0, ti, lambda u, a=p_a, c=p_b: lerp(a, c, u))
    esteira(lambda u, a=p_a, c=p_b: lerp(a, c, u), t0, ti)
    explosao((p_b[0], -8.0, 1.5), ti, r=6, n=14)
# tomba e afunda (rolagem pelo eixo do comprimento)
corvA.keyframe_insert("rotation_euler", frame=f(3.0)); corvA.keyframe_insert("location", frame=f(3.0))
corvA.rotation_euler = (0, math.radians(68), math.radians(-90)); corvA.keyframe_insert("rotation_euler", frame=f(8.0))
corvA.location = (0, -7.6, -0.9); corvA.keyframe_insert("location", frame=f(8.0))
fumaca((0, -6.8, 3.0), 1.3, T_MAPA, r=1.5, cada=0.35, sobe=14)
fumaca((-4, -7.2, 2.0), 2.2, T_MAPA, r=1.0, cada=0.5, sobe=10)
cam_key(t0, (-13, -32, 4.5), (0, -7, 2)); cam_key(2.9, (-10, -26, 5.5), (0, -7, 2))
cam_key(T(0, "Líbia"), (-20, -36, 14), (0, -2, 1)); cam_key(T_MAPA - 0.05, (-30, -48, 22), (0, 0, 0))
# mapa: Ucrânia → Benghazi
visivel_janelas(p_bgz, [(T_MAPA, S[0][1]), (S[2][0], S[3][1]), (S[5][0], S[6][1])])
visivel_janelas(p_ods, [(T_MAPA, S[0][1]), (S[3][0], S[3][1]), (S[5][0], S[6][1])])
trilha("trilhaFrente", [(37.8, 48.0), (33.5, 44.0), (29.0, 41.2), (25.5, 37.0), (20.1, 32.4)], T_MAPA + 0.2, 2.0, AMARELO, fim=t1)
pulsos(M(20.1, 32.1, 1.8), T(0, "frente"), 22, VERMELHO)
cam_mapa(T_MAPA, 30, 41, 200, seco=True); cam_mapa(T(0, "Como"), 29, 40, 225); cam_mapa(t1 - 0.05, 28, 39.5, 245)

# =====================================================================
# 1 — DRONE NAVAL: um barco sem ninguém, close no mar aberto (x ≈ 220)
# =====================================================================
t0, t1 = S[1]
DX, DY = 220, -150
heroi = drone_naval("dnHeroi", 2.2)
visivel(heroi, t0, t1)
fn_h = lambda u: (DX, DY - 30 + 60 * u, 0.5)
caminho(heroi, t0, t1, fn_h); esteira(lambda u: (DX, DY - 34 + 60 * u, 0.4), t0, t1, r=0.5)
for k, dx in enumerate((-9, 9, -18, 18)):
    d = drone_naval(f"dnForm{k}", 1.6); tt = T(1, "Esse") - 0.6 + 0.15 * k
    visivel(d, tt, t1); fn = lambda u, dx=dx: (DX + dx, DY - 30 - abs(dx) * 0.6 + 60 * u, 0.45)
    caminho(d, t0, t1, fn); esteira(lambda u, dx=dx: (DX + dx, DY - 34 - abs(dx) * 0.6 + 60 * u, 0.4), tt, t1)
for k in range(3):  # "carregados de explosivos": anel amarelo na tampa de carga
    tt = T(1, "explosivos") + 0.35 * k
    o = anel(_id("pulsoCarga"), (0, 0, 0), 2.2, 0.15, AMARELO, seg=32); filho(heroi, o); o.location = (0, -0.7, 0.9)
    visivel(o, tt, tt + 0.9); o.scale = (0.1,) * 3; o.keyframe_insert("scale", frame=f(tt)); o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(tt + 0.9))
# câmera acompanha o drone com chaves densas (offset interpolado entre poses)
poses = [(t0, (10, 9, 3.2), (0, 0, 0.8)), (T(1, "barcos"), (8, 7, 2.6), (0, 0, 0.8)),
         (T(1, "explosivos"), (-6, 6, 6.0), (0, 0, 0.8)), (t1 - 0.05, (-20, -14, 12), (0, 4, 0.5))]
def pose(t):
    for (ta, oa, ga), (tb, ob, gb) in zip(poses, poses[1:]):
        if t <= tb: u = suave(max(0, (t - ta) / (tb - ta))); return lerp(oa, ob, u), lerp(ga, gb, u)
    return poses[-1][1], poses[-1][2]
tt = t0; primeiro = True
while tt < t1:
    off, tg = pose(tt); p = fn_h((tt - t0) / (t1 - t0))
    loc = (p[0] + off[0], p[1] + off[1], off[2]); tgt = (p[0] + tg[0], p[1] + tg[1], tg[2])
    (corte if primeiro else cam_key)(tt, loc, tgt); primeiro = False; tt += 0.2

# =====================================================================
# 2 — PORTO AMIGO: Mar Negro → queda de Assad (Síria) → Líbia; leste aliado da Rússia
# =====================================================================
t0, t1 = S[2]
t_porto = T(2, "Esse") - 0.1
navNegro = navio_guerra("navioNegro", 4.0); navNegro.location = M(34.5, 43.6, 1.6); navNegro.rotation_euler = (0, 0, math.radians(-120))
visivel(navNegro, t0, T(2, "Assad")); pop(navNegro, t0 + 0.1, 1.0)
caminho_negro = lambda u: lerp(M(34.5, 43.6, 1.6), M(29.3, 41.3, 1.6), suave(u))
caminho(navNegro, T(2, "alvo"), T(2, "Assad"), caminho_negro)
visivel(p_tar, T(2, "Assad") - 0.3, t_porto)
xis("xisSiria", M(37.5, 35.0, 4.0), T(2, "Assad") + 0.15, t_porto, tam=26)
destacar(siria.data.materials[0], T(2, "Síria"), AREIA2)
trilha("trilhaSiria", [(35.9, 34.9), (30.0, 33.8), (24.5, 33.2), (20.1, 32.4)], T(2, "Moscou"), 1.2, VERMELHO, fim=t_porto, r=1.8, n=26)
m_lna = lna.data.materials[0]
cor_key(m_lna, T(2, "leste") - 0.05, AREIA); cor_key(m_lna, T(2, "leste") + 0.3, LARANJA_LNA)
cor_key(m_lna, S[3][0] + 0.1, LARANJA_LNA); cor_key(m_lna, S[3][0] + 0.5, AREIA)
cam_mapa(t0, 33, 42, 170, seco=True); cam_mapa(T(2, "Assad"), 32, 37.5, 200)
cam_mapa(T(2, "Líbia"), 26, 35, 200); cam_mapa(t_porto - 0.05, 22.5, 33.5, 165)
# porto amigo: corveta intacta atracada, cargueiro, guindaste trabalhando
corte(t_porto, (24, -34, 12), (0, -5, 2))
cam_key(t1 - 0.05, (30, -26, 9), (-4, -5, 2))
for k in range(3):
    cx = caixa(_id("caixaSup"), (0, 0, 0), (1.2, 1.2, 1.0), (0.55, 0.45, 0.30, 1))
    tt = t_porto + 0.3 + 0.5 * k; visivel(cx, tt, t1)
    caminho(cx, tt, tt + 0.6, lambda u, k=k: lerp((-3 + k * 2, 1.0, 8.0), (-3 + k * 2, -6.0, 2.6 + 0.0 * u), suave(u)), orientar=False)

# =====================================================================
# 3 — ALCANCE: a rota de casa é longa demais; os drones partem de perto (navio-mãe)
# =====================================================================
t0, t1 = S[3]
t_rel = T(3, "Segundo") - 0.1
visivel(p_bgz, t0, t1)
rota = trilha("trilhaCasa", [(30.7, 46.3), (29.3, 42.5), (28.8, 41.0), (26.2, 40.1), (25.5, 37.0), (22.5, 34.2), (20.1, 32.4)], t0 + 0.15, 1.6, (0.85, 0.85, 0.85, 1), fim=t_rel, r=1.3, n=40)
xis("xisCasa", M(26.0, 39.0, 4.0), T(3, "casa"), t_rel, tam=22)
cam_mapa(t0, 26, 40, 225, seco=True); cam_mapa(t_rel - 0.05, 25.5, 39.5, 240)
mae = petroleiro("naviomae", cor_casco=(0.30, 0.32, 0.34, 1), escala=1.1); mae.location = (-10, -62, 0.4); mae.rotation_euler = (0, 0, math.radians(15))
visivel(mae, t_rel, t1)
for k in range(5):
    d = drone_naval(f"dnMae{k}", 1.1); tt = T(3, "drones") + 0.18 * k
    a = (-10 + random.uniform(-1, 1), -60, 0.35); b = (-22 + k * 7, -22, 0.35)
    visivel(d, tt, t1); caminho(d, tt, t1, lambda u, a=a, b=b: lerp(a, b, u)); esteira(lambda u, a=a, b=b: lerp(a, b, u), tt, t1)
regua = caixa("reguaPerto", (-8, -35, 1.4), (0.6, 50, 0.3), AMARELO, unico="regua"); regua.rotation_euler = (0, 0, math.radians(8))
visivel(regua, T(3, "perto"), t1); pop(regua, T(3, "perto"))
corte(t_rel, (26, -84, 20), (-8, -44, 0))
cam_key(t1 - 0.05, (24, -66, 26), (-6, -30, 0))

# =====================================================================
# 4 — EFEITO COLATERAL: navio tombado no porto da Líbia, dois oficiais líbios mortos, promessa de retaliar
# =====================================================================
t0, t1 = S[4]
fumaca((0, -6.8, 1.6), t0, t1, r=1.4, cada=0.5, sobe=12)
for k in range(2):
    b = barco_rapido(f"patrulhaLibia{k}", 2.0); b.location = (14 + k * 7, -6.0, 0.4); b.rotation_euler = (0, 0, math.radians(-90))
    visivel(b, t0, t1)
for k in range(2):   # duas boias de luto (marcadores sóbrios, sem corpos)
    m = cilindro(_id("marcador"), (10 + k * 3, -2.0, 2.6), 0.5, 2.4, (0.12, 0.12, 0.14, 1), seg=10)
    filho(m, esfera(_id("marcadorT"), (0, 0, 1.5), 0.6, (0.95, 0.95, 0.95, 1), sub=1))
    tt = T(4, "dois") + 0.25 * k; visivel(m, tt, t1); pop(m, tt)
for k in range(4):
    lc, _ = caminhao(f"caminhaoLNA{k}", (-10 + k * 8, 6.5, 2.4), cor=(0.62, 0.55, 0.40, 1), tubos=False)
    lc.rotation_euler = (0, 0, math.radians(180)); tt = T(4, "retaliar") - 0.2 + 0.15 * k
    visivel(lc, tt, t1); pop(lc, tt)
pulsos((2, 0, 2.2), T(4, "retaliar"), 40, VERMELHO, n=3)
corte(t0, (-22, -30, 9), (0, -6, 1))
cam_key(T(4, "forças"), (-10, -26, 13), (6, -3, 1.5))
cam_key(T(4, "retaliar"), (6, -34, 22), (4, 2, 1.5))
cam_key(t1 - 0.05, (12, -42, 30), (2, 0, 1))

# =====================================================================
# 5 — DIPLOMACIA: Itália (300 km, petróleo da Líbia) diz que Kiev errou; Kiev: alvos legítimos
# =====================================================================
t0, t1 = S[5]
visivel(p_rom, T(5, "Itália"), t1)
m_ita = ita_n.data.materials[0]
cor_key(m_ita, T(5, "Itália") - 0.05, VERDE_EU); cor_key(m_ita, T(5, "Itália") + 0.3, AMARELO)
cor_key(m_ita, T(5, "Ucrânia") - 0.2, AMARELO); cor_key(m_ita, T(5, "Ucrânia") + 0.3, VERDE_EU)
r300 = caixa("regua300", (0, 0, 0), (0.9, 1, 0.4), AMARELO, unico="regua")
a3, b3 = Vector(M(14.3, 36.6, 2.0)), Vector(M(14.3, 33.0, 2.0)); r300.location = (a3 + b3) / 2; r300.scale = (1, (a3 - b3).length, 1)
visivel(r300, T(5, "trezentos"), t1)
for k in range(6):
    br = barril(f"barrilIta{k}", 0.9); tt = T(5, "petróleo") - 0.2 + 0.25 * k
    visivel(br, tt, tt + 1.6)
    caminho(br, tt, tt + 1.5, lambda u, k=k: lerp(M(19.0 + 0.3 * k, 31.5, 2.5), M(14.5 + 0.2 * k, 37.0, 3.5), suave(u)), orientar=False)
pulsos(M(12.5, 41.9, 2.0), T(5, "Kiev"), 26, VERMELHO, n=3)
pulsos(M(30.5, 50.4, 2.0), T(5, "Ucrânia"), 26, AZUL, n=3)
destacar(ucr.data.materials[0], T(5, "Ucrânia"), AZUL)
cam_mapa(t0, 14.5, 39, 170, seco=True); cam_mapa(T(5, "petróleo"), 16, 35.5, 150)
cam_mapa(T(5, "Ucrânia") - 0.3, 22, 43, 270); cam_mapa(T(5, "legítimos"), 29, 48, 190); cam_mapa(t1 - 0.05, 28, 47.5, 205)

# =====================================================================
# 6 — NOVO FRONT: navios russos sob alerta no Mar Negro e no Mediterrâneo
# =====================================================================
t0, t1 = S[6]
alvos = [(33.5, 44.2), (37.5, 44.6), (30.5, 43.0), (20.6, 33.1), (25.0, 34.4), (16.0, 35.0)]
for k, (lo, la) in enumerate(alvos):
    ng = navio_guerra(f"frota{k}", 4.0); ng.location = M(lo, la, 1.8 if la > 40 else 1.4); ng.rotation_euler = (0, 0, math.radians(random.uniform(0, 360)))
    tt = T(6, "frota") + 0.12 * k; visivel(ng, tt, t1); pop(ng, tt)
    pulsos(M(lo, la, 2.0), T(6, "segura") + 0.1 * k, 20, VERMELHO, n=2, gap=0.5, unico="pulsoFront")
    for j in range(2):
        d = drone_naval(f"dnFront{k}_{j}", 2.6); ang0 = random.uniform(0, 6.28)
        fn = lambda u, lo=lo, la=la, ang0=ang0, j=j: (M(lo, la)[0] + math.cos(ang0 + u * 5 + j * 3.1) * 16, M(lo, la)[1] + math.sin(ang0 + u * 5 + j * 3.1) * 16, 1.6 if la > 40 else 1.2)
        visivel(d, T(6, "segura"), t1); caminho(d, T(6, "segura"), t1, fn, passo=2)
cam_mapa(t0, 27, 39.5, 250, seco=True); cam_mapa(t1 - 0.05, 27, 39.5, 290)

# =====================================================================
# 7/8 — FINAL: o porto ao entardecer, drones patrulhando, câmera sobe
# =====================================================================
t0 = S[7][0]; tF = FIM
corvC = corveta("corvetaC", 1.4); corvC.location = (0, -6.6, 0.55); corvC.rotation_euler = (0, 0, math.radians(-90))
visivel(corvC, t0, tF)
for k in range(4):
    d = drone_naval(f"dnFinal{k}", 1.3); R = 34 + k * 6; ang0 = k * 1.4
    fn = lambda u, R=R, ang0=ang0: (math.cos(ang0 + u * 1.6) * R, -40 + math.sin(ang0 + u * 1.6) * R * 0.5, 0.35)
    visivel(d, t0, tF); caminho(d, t0, tF, fn, passo=2); esteira(fn, t0, tF, cada=0.3)
corte(t0, (-30, -44, 11), (0, -8, 2))
cam_key(S[8][0], (-6, -58, 20), (0, -12, 1))
cam_key(tF, (20, -78, 38), (0, -16, 0))

# ---------- render ----------
if os.environ.get("REALISTA"):
    HD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "hdri")
    bg, sol = modo_realista(os.path.join(HD, "ceu_parcialmente_nublado_2k.hdr"), samples=int(os.environ.get("AMOSTRAS", "4")), foco=alvo)
    mm = mar.data.materials[0].node_tree.nodes.get("Principled BSDF"); mm.inputs["Roughness"].default_value = 0.12
    mm2 = bpy.data.materials.get(mapa[0].data.materials[0].name).node_tree.nodes.get("Principled BSDF"); mm2.inputs["Roughness"].default_value = 0.3
    for m in bpy.data.materials:   # explosões com emissão baixa (backlog 10)
        if tuple(round(c, 3) for c in m.diffuse_color) == tuple(round(c, 3) for c in C["laranja"]):
            b = m.node_tree.nodes.get("Principled BSDF"); b.inputs["Emission Color"].default_value = _lin((1.0, 0.42, 0.06, 1)); b.inputs["Emission Strength"].default_value = 1.2
    # pinos e pulsos brilham levemente
    for chave in ("pulsoFront",):
        for k, v in _mats.items():
            if k[1] == chave:
                b = v.node_tree.nodes.get("Principled BSDF"); b.inputs["Emission Color"].default_value = _lin(VERMELHO); b.inputs["Emission Strength"].default_value = 1.0
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
