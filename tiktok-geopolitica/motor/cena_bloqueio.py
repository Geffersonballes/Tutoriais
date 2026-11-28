"""Vídeo 28/11 — 'Como funciona um bloqueio naval?' (Pacific Archer e o bloqueio aos portos do Irã). Uso:
REALISTA=1 blender -b --factory-startup -P cena_bloqueio.py -- <pasta_producao> [preview t1,t2,... | range a,b]
Palco único: costa genérica ao norte (y > 55) com porto e cidade; mar com ondas (mar_ondulado); linha de bloqueio
com corvetas em y = LY; mar aberto ao sul, de onde chegam os mercantes. Sem bandeiras de países reais."""
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
random.seed(2812)
scn.world.color = (0.30, 0.60, 0.95)

MAR = (0.10, 0.36, 0.55, 1); AREIA = (0.86, 0.74, 0.52, 1); AREIA2 = (0.78, 0.64, 0.44, 1); ROCHA = (0.62, 0.50, 0.38, 1)
AZUL = (0.25, 0.55, 1.0, 1); VERMELHO = (0.92, 0.18, 0.14, 1); AMARELO = (0.98, 0.82, 0.15, 1)
BRANCO = (0.98, 0.98, 0.98, 1); VERDE = (0.20, 0.85, 0.35, 1)
LY = -90.0      # linha do bloqueio
ZN = 0.35       # altura dos cascos na água

def pulsos(loc, t, R, cor, n=3, gap=0.4, dur=1.2, unico=None):
    for k in range(n):
        tt = t + gap * k
        o = anel(_id("pulso"), loc, R, R * 0.025 + 0.2, cor, seg=48, unico=unico)
        visivel(o, tt, tt + dur)
        o.scale = (0.05,) * 3; o.keyframe_insert("scale", frame=f(tt)); o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(tt + dur))

def fumaca_col(nome, loc, t0, t1, altura=26, raio=2.6):
    bs = coluna_fumaca(nome, loc, altura=altura, raio=raio, t0=t0, t_fim=t1, n=18)
    for b in bs: visivel(b, t0, t1)
    return bs

def esteira(fn, t0, t1, r=0.45):
    rastro(fn, t0, t1, (0.95, 0.97, 1.0, 1), r=r, cada=0.16, vida=1.8)

def xis(nome, loc, t, fim, tam=10, cor=VERMELHO):
    a = caixa(nome + "a", loc, (tam, tam * 0.16, 1.0), cor, unico="xis"); a.rotation_euler = (0, 0, math.radians(45))
    b = caixa(nome + "b", (0, 0, 0), (tam, tam * 0.16, 1.0), cor, unico="xis"); filho(a, b); b.rotation_euler = (0, 0, math.radians(90))
    visivel(a, t, fim); pop(a, t); return a

def meia_volta(p0, p_vira, p1):
    """Caminho em U: sobe de p0 até p_vira e volta para p1 (curva de Bézier quadrática)."""
    return lambda u: bez(p0, p_vira, p1, u)

# câmera
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 26; cam_d.clip_end = 6000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def cam_key(t, loc, tgt):
    for ob, v in ((cam, loc), (alvo, tgt)):
        ob.location = v; ob.keyframe_insert("location", frame=f(t))
        for fc in ob.animation_data.action.fcurves:   # chave nova sempre suave (senão herda o CONSTANT do corte)
            for kp in fc.keyframe_points:
                if kp.co[0] == f(t): kp.interpolation = "BEZIER"
def corte(t, loc, tgt):
    for ob in (cam, alvo):
        ad = ob.animation_data
        if ad and ad.action:
            for fc in ad.action.fcurves:
                ant = [kp for kp in fc.keyframe_points if kp.co[0] < f(t)]
                if ant: max(ant, key=lambda kp: kp.co[0]).interpolation = "CONSTANT"
    cam_key(t, loc, tgt)

# =====================================================================
# CENÁRIO: mar com ondas, costa com porto, cidade e montanhas
# =====================================================================
mar = mar_ondulado("mar", (0, -150, 0), (900, 700), MAR, res=110, altura=0.45, escala_onda=7.0, t_fim=FIM)
fundo_mar = caixa("fundoMar", (0, -150, -1.2), (3000, 3000, 0.4), (0.06, 0.24, 0.38, 1))
costa = caixa("costa", (0, 260, 0.2), (1400, 400, 2.4), AREIA)
praia = caixa("praia", (0, 61, 0.1), (1400, 6, 1.6), (0.92, 0.84, 0.64, 1))
for _ in range(40):
    x = random.uniform(-500, 500); y = random.uniform(150, 420)
    m = esfera(_id("serra"), (x, y, -2), random.uniform(14, 34), random.choice([ROCHA, AREIA2]), sub=1); m.scale = (1.7, 1.0, 0.5)
# porto: cais, guindastes, armazéns, quebra-mar com a "boca" do porto em x ∈ [-14, 14]
cais = caixa("cais", (0, 66, 1.4), (120, 10, 1.6), (0.60, 0.60, 0.62, 1))
for k, x in enumerate((-40, -14, 14, 40)):
    guindaste_porto(f"guind{k}", (x, 68), h=10.0, cor=(0.85, 0.20, 0.15, 1) if k % 2 == 0 else (0.20, 0.45, 0.80, 1))
for k in range(6):
    caixa(_id("armazem"), (-50 + k * 20, 80, 3.4), (16, 8, 5.2), random.choice([(0.85, 0.85, 0.82, 1), (0.70, 0.72, 0.75, 1)]))
for k in range(14):  # pilhas de contêineres
    cor = random.choice([(0.85, 0.25, 0.18, 1), (0.20, 0.45, 0.75, 1), (0.95, 0.70, 0.15, 1), (0.25, 0.60, 0.35, 1)])
    caixa(_id("cont"), (-55 + k * 8, 92, 2.0 + random.randint(0, 2) * 1.2), (6, 2.4, 2.4), cor, unico="cont%d" % (k % 4))
qm_o = caixa("quebraMarO", (-45, 28, 0.8), (62, 4, 2.0), ROCHA)
qm_l = caixa("quebraMarL", (45, 28, 0.8), (62, 4, 2.0), ROCHA)
for _ in range(110):  # cidade atrás do porto
    x = random.uniform(-150, 150); y = random.uniform(100, 170)
    if abs(x) < 60 and y < 100: continue
    predio((x, y), random.uniform(5, 9), random.uniform(5, 9), random.uniform(4, 16), random.choice(PREDIOS))
for _ in range(5): nuvem((random.uniform(-200, 200), random.uniform(60, 260), random.uniform(130, 150)), random.uniform(3.0, 4.0))
# navios atracados no cais (presos durante o bloqueio)
atracados = []
for k, x in enumerate((-30, 0, 30)):
    g = graneleiro(f"atracado{k}", escala=2.2, cor_casco=[(0.16, 0.24, 0.36, 1), (0.22, 0.30, 0.22, 1), (0.30, 0.18, 0.18, 1)][k])
    g.location = (x, 55, ZN); g.rotation_euler = (0, 0, math.radians(90)); atracados.append(g)

# linha do bloqueio: 5 corvetas patrulhando de um lado a outro
CORV_X = [-120, -60, 0, 60, 120]
corvetas = []
for k, x in enumerate(CORV_X):
    c = corveta(f"corveta{k}", escala=3.0); corvetas.append(c)
    sentido = 1 if k % 2 == 0 else -1
    def fn(u, x=x, s=sentido): return (x + s * 14 * math.sin(u * 2 * math.pi * 3.0), LY + 3 * math.sin(u * 2 * math.pi * 1.5 + x), ZN)
    caminho(c, 0.0, FIM, fn, passo=6)

# =====================================================================
# 0 — GANCHO: mercantes chegam e dão meia-volta; um já arde (inutilizado); câmera sobe para o plano geral
# =====================================================================
t0, t1 = S[0]
T_GERAL = T(0, "Como")
mercantes = []
rotas_volta = [(-90, -320, -100, -150, -140, -330), (-40, -330, -40, -140, 10, -330), (40, -320, 30, -145, 80, -320),
               (95, -330, 110, -150, 150, -320), (-150, -300, -165, -155, -200, -300), (160, -300, 175, -150, 210, -310)]
for k, (x0, y0, xv, yv, x1, y1) in enumerate(rotas_volta):
    m = petroleiro(f"mercante{k}", cor_casco=random.choice([(0.55, 0.12, 0.10, 1), (0.16, 0.30, 0.46, 1), (0.22, 0.34, 0.24, 1)]), escala=2.6) if k % 2 else graneleiro(f"mercante{k}", escala=2.6)
    tt0 = -1.5 + 0.35 * k; tt1 = tt0 + 9.0
    fn = meia_volta((x0, y0, ZN), (xv, yv + 70, ZN), (x1, y1, ZN))
    caminho(m, max(0, tt0), tt1, lambda u, fn=fn, tt0=tt0, tt1=tt1: fn(min(1, (u * (tt1 - max(0, tt0)) + max(0, tt0) - tt0) / (tt1 - tt0))), passo=2)
    visivel(m, 0, T_GERAL + 3.5); mercantes.append(m)
# navio já inutilizado, parado, com fumaça desde o 1º quadro; segundo é atingido aos ~2,2 s
inut = graneleiro("inutilizado0", escala=2.8); inut.location = (-25, -128, ZN - 0.2); inut.rotation_euler = (math.radians(3), math.radians(-4), math.radians(70))
visivel(inut, 0, t1); fumaca_col("fumInut0", (-25 + 9, -128 - 3, 2.0), 0.0, t1, altura=30, raio=2.8)
inut2 = petroleiro("inutilizado1", escala=2.8); inut2.location = (28, -120, ZN); inut2.rotation_euler = (0, 0, math.radians(-60))
visivel(inut2, 0, t1); explosao((28 - 8, -120 - 5, 3.0), 2.2, r=9, n=16); explosao((28 - 8, -120 - 5, 3.0), 3.4, r=7, n=10)
fumaca_col("fumInut1", (28 - 8, -120 - 5, 2.0), 2.3, t1, altura=26, raio=2.4)
xs_inut = []
for k, (x, y) in enumerate(((-25, -128), (28, -120))):
    xs_inut.append(xis(f"xisInut{k}", (x, y, 14), T(0, "inutilizados"), T_GERAL, tam=10))
cam_key(t0, (0, -40, 16), (0, -140, 6)); cam_key(T(0, "Seis"), (0, -55, 20), (0, -130, 4))
cam_key(T_GERAL, (0, -60, 60), (0, -120, 0)); cam_key(t1 - 0.05, (0, -150, 230), (0, -40, 0))

# =====================================================================
# 1 — O BLOQUEIO: o porto e os navios presos; boias vermelhas fecham a boca do porto
# =====================================================================
t0, t1 = S[1]
boias = []
for k in range(9):
    b = cilindro(_id("boia"), (-16 + k * 4, 28, 1.0), 0.9, 1.8, VERMELHO, seg=10, unico="boia")
    filho(b, esfera(_id("boiaTopo"), (0, 0, 1.2), 0.6, BRANCO, sub=1))
    tt = T(1, "fecha") + 0.08 * k; visivel(b, tt, S[2][1]); pop(b, tt); boias.append(b)
corrente = caixa("corrente", (0, 28, 1.2), (36, 0.3, 0.3), (0.2, 0.2, 0.22, 1)); visivel(corrente, T(1, "portos"), S[2][1])
pulsos((0, 28, 1.5), T(1, "mar"), 30, VERMELHO, n=2, unico="pulsoAlerta")
corte(t0, (40, -40, 34), (0, 60, 2))
cam_key(T(1, "fecha"), (14, -10, 22), (0, 40, 1)); cam_key(t1 - 0.05, (6, -4, 20), (0, 36, 0))

# =====================================================================
# 2 — A DECLARAÇÃO: documento, costa destacada, bandeiras de todas as cores
# =====================================================================
t0, t1 = S[2]
doc, selo = documento("declaracao", (0, 0), w=6.0, d=8.0); doc.scale = (1.6,) * 3
doc.location = (-45, 40, 0.6); selo.location = (doc.location.x + 2.4, doc.location.y - 4.8, doc.location.z + 2.66); selo.scale = (1.6,) * 3
visivel(doc, t0, S[3][0] + 2.0); visivel(selo, T(2, "mundo"), S[3][0] + 2.0); pop(doc, t0 + 0.05, escala=1.6); pop(selo, T(2, "mundo"), escala=1.6)
faixa_costa = caixa("faixaCosta", (0, 61, 1.5), (300, 2.4, 0.3), AMARELO, unico="faixaCosta")
visivel(faixa_costa, T(2, "costa"), T(2, "bandeiras")); pop(faixa_costa, T(2, "costa"))
relogio = cilindro("relogio", (-45, 46, 12), 3.2, 0.5, BRANCO, seg=24); relogio.rotation_euler = (math.radians(90), 0, 0)
ponteiro = caixa("ponteiro", (0, 0, 0), (0.3, 0.2, 2.4), C["escuro"]); filho(relogio, ponteiro); ponteiro.location = (0, -0.4, 0.9)
visivel(relogio, T(2, "desde"), T(2, "vale")); pop(relogio, T(2, "desde"))
cores_band = [(0.90, 0.20, 0.20, 1), (0.20, 0.45, 0.90, 1), (0.95, 0.80, 0.15, 1), (0.20, 0.70, 0.35, 1), (0.95, 0.55, 0.15, 1), (0.60, 0.35, 0.80, 1), (0.95, 0.95, 0.95, 1)]
bands = []
for k, cor in enumerate(cores_band):
    bd = bandeira(_id("band"), (-36 + k * 12, 10, 0.5), cor, h=7.0, larg=3.2, alt=2.0, fase=k * 0.7)
    tt = T(2, "todas") + 0.12 * k; visivel(bd, tt, t1); pop(bd, tt); bands.append(bd)
corte(t0, (-45, 4, 22), (-45, 42, 3))
cam_key(T(2, "costa") - 0.1, (-40, -30, 40), (-20, 50, 2))
cam_key(T(2, "todas") - 0.2, (0, -36, 16), (0, 10, 5)); cam_key(t1 - 0.05, (0, -30, 14), (0, 10, 5))

# =====================================================================
# 3 — O CERCO: o papel não basta; corvetas e avião vigiando a linha
# =====================================================================
t0, t1 = S[3]
xis("xisPapel", (-45, 40, 14), T(3, "basta"), T(3, "regras") + 0.3, tam=9)
for k, c in enumerate(corvetas):
    pulsos((CORV_X[k], LY, 1.0), T(3, "navios") + 0.15 * k, 34, AZUL, n=2, gap=0.6, dur=1.6, unico="pulsoAzul")
vig = aviao("aviaoVigia", cor=(0.80, 0.82, 0.84, 1), radome=True); vig.scale = (2.0,) * 3
visivel(vig, T(3, "vigiando") - 1.0, S[4][1])
caminho(vig, T(3, "vigiando") - 1.0, S[4][1], lambda u: (math.cos(u * 4.0 + 2.6) * 150, LY - 40 + math.sin(u * 4.0 + 2.6) * 60, 55), passo=2)
corte(t0, (-60, 6, 26), (-45, 40, 3))
cam_key(T(3, "regras") - 0.1, (-95, -55, 20), (-55, LY, 1))
cam_key(T(3, "vigiando"), (-80, -40, 34), (0, LY - 10, 8)); cam_key(t1 - 0.05, (-40, -36, 40), (30, LY - 20, 8))

# =====================================================================
# 4 — A INTERCEPTAÇÃO: um mercante obedece e volta; outro insiste, é abordado e escoltado
# =====================================================================
t0, t1 = S[4]
m1 = graneleiro("obediente", escala=2.6, cor_casco=(0.22, 0.30, 0.22, 1))
fn1a = lambda u: lerp((-40, -230, ZN), (-40, -130, ZN), suave(u))
fn1b = meia_volta((-40, -130, ZN), (-40, -105, ZN), (-80, -230, ZN))
visivel(m1, t0, t1); caminho(m1, t0, T(4, "mudar"), fn1a, passo=2); caminho(m1, T(4, "mudar") + 0.05, t1, fn1b, passo=2)
pulsos((-40, -125, 2), T(4, "ordem"), 14, AMARELO, n=3, unico="pulsoAmarelo")
m2 = petroleiro("teimoso", escala=2.6)
fn2a = lambda u: lerp((30, -250, ZN), (30, -118, ZN), u)
fn2b = lambda u: bez((30, -118, ZN), (34, -100, ZN), (75, -150, ZN), suave(u))
visivel(m2, t0, t1); caminho(m2, t0, T(4, "desviado"), fn2a, passo=2); caminho(m2, T(4, "desviado") + 0.05, t1, fn2b, passo=2)
lancha = barco_rapido("lanchaAbordagem", escala=3.0)
fnl = lambda u: bez((0, LY + 4, ZN), (10, -110, ZN), (24, -116, ZN), suave(u))
visivel(lancha, T(4, "insistir"), T(4, "desviado")); caminho(lancha, T(4, "insistir"), T(4, "abordado") + 0.3, fnl, passo=1)
for k in range(3):
    sd, _, _ = boneco(f"marinheiro{k}", (30 + (k - 1) * 1.6, -118 + 2 + k * 1.5, ZN + 1.0), camisa=(0.20, 0.30, 0.55, 1))
    sd.scale = (0.8,) * 3; visivel(sd, T(4, "abordado") + 0.2, T(4, "desviado")); pop(sd, T(4, "abordado") + 0.2 + 0.1 * k, escala=0.8)
seta_desv = seta3d("setaDesvio", 18, AMARELO); seta_desv.location = (40, -112, 6); seta_desv.rotation_euler = (math.radians(90), 0, math.radians(55))
visivel(seta_desv, T(4, "desviado"), T(4, "capturado") + 0.4); pop(seta_desv, T(4, "desviado"))
escolta = corveta("escolta", escala=3.0)
visivel(escolta, T(4, "capturado") - 0.6, t1)
caminho(escolta, T(4, "capturado") - 0.6, t1, lambda u: bez((60, LY - 6, ZN), (62, -110, ZN), (90, -140, ZN), suave(u)), passo=2)
corte(t0, (-90, -60, 40), (-10, -150, 2))
cam_key(T(4, "insistir"), (-30, -60, 34), (20, -125, 2))
cam_key(T(4, "abordado"), (0, -80, 20), (30, -118, 2)); cam_key(t1 - 0.05, (10, -80, 34), (55, -135, 2))

# =====================================================================
# 5 — O RECADO: o cargueiro sai do porto, ignora avisos, é atingido na popa por um avião; tripulação a salvo
# =====================================================================
t0, t1 = S[5]
pa = graneleiro("pacificArcher", escala=3.2, cor_casco=(0.18, 0.22, 0.30, 1))
pa_fn = lambda u: lerp((0, 52, ZN), (0, -60, ZN), u)
T_HIT = T(5, "atingido") + 0.25
u_hit = 0.86
visivel(pa, t0, S[6][1])
caminho(pa, t0, T_HIT, lambda u: pa_fn(u * u_hit), passo=2)
caminho(pa, T_HIT + 0.05, t1, lambda u: pa_fn(u_hit + 0.03 * (1 - (1 - u) ** 3)), passo=3)
esteira(lambda u: (0, 52 - (112 * u_hit) * u + 14, 0.6), t0, T_HIT)
pulsos((0, -30, 3), T(5, "avisos"), 15, AMARELO, n=2, gap=0.3, dur=0.9, unico="pulsoAmarelo")
jato = aviao("jatoBloqueio", cor=(0.55, 0.58, 0.62, 1), radome=False); jato.scale = (1.4,) * 3
visivel(jato, T_HIT - 1.8, T_HIT + 2.2)
popa = lambda: Vector(pa_fn(u_hit)) + Vector((0, 15, 3))
caminho(jato, T_HIT - 1.8, T_HIT + 2.2, lambda u: lerp((-180, -40, 45), (180, -10, 60), u), passo=1)
pp = tuple(popa())
mis = missil("municao", escala=0.5); visivel(mis, T_HIT - 0.55, T_HIT)
caminho(mis, T_HIT - 0.55, T_HIT, lambda u: lerp((-40, pp[1] - 6, 30), pp, u), passo=1)
explosao(pp, T_HIT, r=9, n=18); explosao(pp, T_HIT + 0.3, r=6, n=10)
fumaca_col("fumPopa", pp, T_HIT + 0.1, S[6][1], altura=28, raio=2.4)
for k in range(3):  # tripulação no convés de proa, a salvo
    tp, _, _ = boneco(f"tripulante{k}", (0, 0, 0), camisa=(0.95, 0.55, 0.12, 1), capacete=True); tp.scale = (0.9,) * 3
    filho(pa, tp); tp.location = ((k - 1) * 0.5, 3.2, 1.0); tp.scale = (0.28,) * 3
    visivel(tp, T(5, "tripulação") - 0.2, t1)
pulsos(tuple(Vector(pa_fn(u_hit)) + Vector((0, -10, 2))), T(5, "ilesa"), 9, VERDE, n=2, unico="pulsoVerde")
corte(t0, (40, 0, 26), (0, 40, 2))
cam_key(T(5, "Irã"), (36, -40, 28), (0, -10, 2))
cam_key(T(5, "avisos"), (44, -30, 30), (0, -32, 3))
cam_key(T_HIT, (40, -6, 24), (0, -38, 3))
cam_key(T(5, "tripulação"), (22, -80, 16), (0, -55, 2)); cam_key(t1 - 0.05, (30, -100, 30), (0, -45, 4))

# =====================================================================
# 6 — O IMPASSE: lanchas saem do porto rumo à linha; corvetas encaram; "?" no meio
# =====================================================================
t0, t1 = S[6]
lanchas = []
for k in range(5):
    lb = barco_rapido(f"lanchaPorto{k}", escala=5.0); x = -40 + k * 20
    visivel(lb, t0, t1); caminho(lb, t0, T(6, "Washington"), lambda u, x=x: lerp((x * 0.3, 40, ZN), (x, -40, ZN), suave(u)), passo=2)
    lanchas.append(lb)
seta_vm = seta3d("setaRomper", 24, VERMELHO); seta_vm.location = (0, -22, 10); seta_vm.scale = (2.2, 2.2, 1.0); seta_vm.rotation_euler = (math.radians(90), 0, 0)
visivel(seta_vm, T(6, "promete"), t1)
seta_az = seta3d("setaBloquear", 24, AZUL); seta_az.location = (0, LY - 4, 10); seta_az.scale = (2.2, 2.2, 1.0); seta_az.rotation_euler = (math.radians(-90), 0, 0)
visivel(seta_az, T(6, "Washington"), t1)
interrog = texto3d("txtInterrog", "?", (14, -62, 14), tam=22, cor=AMARELO, espessura=1.4, unico="txtInterrog")
interrog.rotation_euler = (math.radians(70), 0, 0)
visivel(interrog, T(6, "impasse") - 0.2, t1); pop(interrog, T(6, "impasse") - 0.2)
corte(t0, (45, -15, 26), (0, -32, 2))
cam_key(T(6, "Washington"), (55, -85, 32), (0, -55, 4)); cam_key(t1 - 0.05, (60, -105, 40), (0, -58, 6))

# =====================================================================
# 7 — O FREIO: corvetas abrem passagem para um navio de ajuda com sacos de alimento; gente esperando no cais
# =====================================================================
t0, t1 = S[7]
ajuda = graneleiro("navioAjuda", escala=3.0, cor_casco=(0.95, 0.95, 0.93, 1), cor_conves=(0.30, 0.60, 0.35, 1))
fna = lambda u: lerp((-5, -175, ZN), (-5, -10, ZN), u)
visivel(ajuda, t0, FIM); caminho(ajuda, t0, t1 + 3, fna, passo=2)
for k in range(8):
    sc = caixa(_id("sacoAjuda"), (0, 0, 0), (0.55, 0.38, 0.22), (0.92, 0.86, 0.66, 1), unico="sacoAjuda"); filho(ajuda, sc)
    sc.location = ((k % 2 - 0.5) * 0.6, 2.9 - (k // 2) * 1.3, 0.9)
faixa_v = caixa("faixaAjuda", (0, 0, 0), (1.62, 0.6, 0.2), (0.25, 0.65, 0.35, 1)); filho(ajuda, faixa_v); faixa_v.location = (0, 1.5, 0.35)
civis = []
for k in range(10):
    cv, _, _ = boneco(f"civil{k}", (-20 + k * 4.4, 63, 2.2), camisa=random.choice(PREDIOS), capacete=False); cv.scale = (1.3,) * 3
    cv.rotation_euler = (0, 0, math.radians(180)); visivel(cv, t0, FIM); civis.append(cv)
pulsos((-5, LY, 1.0), T(7, "limite"), 26, BRANCO, n=2, unico="pulsoBranco")
corte(t0, (-55, -215, 26), (-5, -165, 2))
cam_key(T(7, "bloqueio"), (-50, -170, 30), (-5, -120, 2)); cam_key(T(7, "fome"), (-40, -110, 26), (-5, -70, 2))
cam_key(t1 - 0.05, (-30, -30, 26), (-5, 20, 2))

# =====================================================================
# 8/9 — FINAL: plano geral ao entardecer, câmera sobe sobre a linha
# =====================================================================
t0 = S[8][0]; tF = FIM
corte(t0, (-120, -200, 60), (0, -60, 0))
cam_key(S[9][0], (-40, -240, 120), (0, -40, 0))
cam_key(tF, (40, -260, 200), (0, -20, 0))

# ---------- render ----------
if os.environ.get("REALISTA"):
    HD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "hdri")
    bg, sol = modo_realista(os.path.join(HD, "ceu_parcialmente_nublado_2k.hdr"), samples=int(os.environ.get("AMOSTRAS", "4")), foco=alvo)
    for nome in ("mar",):
        m = bpy.data.objects[nome].data.materials[0]
        if m.node_tree:
            b = m.node_tree.nodes.get("Principled BSDF")
            if b: b.inputs["Roughness"].default_value = 0.18
    for m in bpy.data.materials:   # explosões com emissão baixa (backlog 10)
        if tuple(round(c, 3) for c in m.diffuse_color) == tuple(round(c, 3) for c in C["laranja"]):
            b = m.node_tree.nodes.get("Principled BSDF"); b.inputs["Emission Color"].default_value = _lin((1.0, 0.42, 0.06, 1)); b.inputs["Emission Strength"].default_value = 1.2
    for chave, cor in (("pulsoAlerta", VERMELHO), ("pulsoAzul", AZUL), ("pulsoAmarelo", AMARELO), ("pulsoVerde", VERDE), ("pulsoBranco", BRANCO), ("faixaCosta", AMARELO), ("xis", VERMELHO)):
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
