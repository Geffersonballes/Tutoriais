"""Série 2 — 'Como os pedestres (NPCs) do GTA 6 funcionam?' (estilo C cartoon, mascote Pixel).
Mecanismo peça por peça: 600 mil animações (x 55 mil do GTA 5) -> time só de pedestres -> a mesma animação
se ajusta a corpos diferentes -> temperamento decide se foge ou enfrenta -> testemunha -> descrição para a
polícia (roupa, carro, dupla) -> trocar de roupa / separar a dupla faz a descrição não bater.
Visual 100 % original: bonequinhos genéricos, cidade genérica, nenhum personagem, mapa, logotipo ou arte de jogo.
Melhoria do backlog #3: placas de HUD dentro do cenário (o número vai por cima, no grafismo 2D).
Uso: blender -b --factory-startup -P cena_gta_npcs.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
import bpy, sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowpoly import *
from lowpoly import _id
from cartoon import *

args = sys.argv[sys.argv.index("--") + 1:]
PASTA = args[0]
LEG = json.load(open(os.path.join(PASTA, "legendas.json"), encoding="utf-8"))
FIM = LEG[-1]["e"] + 4.6          # cobre também o pedido de like (a cena não congela no fim)
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
random.seed(23)

AMARELO = (1.0, 0.82, 0.12, 1); VERDE = (0.20, 0.85, 0.40, 1); VERMELHO = (0.95, 0.22, 0.20, 1)
ROXO = (0.60, 0.34, 0.95, 1); AZUL = (0.20, 0.55, 1.0, 1); BRANCO = (0.97, 0.97, 0.98, 1)
CIANO = (0.25, 0.95, 1.0, 1); ESCURO = (0.10, 0.11, 0.14, 1); CINZA = (0.40, 0.42, 0.48, 1)
MARINHO = (0.10, 0.18, 0.45, 1); ASFALTO = (0.30, 0.31, 0.36, 1); CALCADA = (0.80, 0.80, 0.84, 1)
CORES = [(0.98, 0.45, 0.35, 1), (0.30, 0.70, 1.0, 1), (0.98, 0.80, 0.25, 1), (0.45, 0.85, 0.45, 1), (0.75, 0.50, 0.95, 1), (1.0, 0.60, 0.80, 1)]
PELES = [PELE, (0.75, 0.52, 0.38, 1), (0.50, 0.33, 0.22, 1), (0.98, 0.84, 0.70, 1)]
CABELOS = [(0.16, 0.10, 0.08, 1), (0.45, 0.28, 0.12, 1), (0.92, 0.78, 0.35, 1), (0.75, 0.25, 0.15, 1), (0.85, 0.85, 0.88, 1)]
BRILHO = []

def girar(ob, graus): ob.rotation_euler = (0, 0, math.radians(graus))
def brilha(ob): BRILHO.append(ob.data.materials[0]); return ob
def rotk(ob, t, rx=0, ry=0, rz=0, interp="BEZIER"):
    ob.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz)); key(ob, "rotation_euler", t, ob.rotation_euler, interp)
def lock(ob, t, v): key(ob, "location", t, v, "LINEAR")

# ---------- pedestre genérico articulado (original) ----------
def pedestre(nome, loc, camisa, calca=(0.22, 0.26, 0.36, 1), h=1.0, w=1.0, pele=None, cabelo=None, unico=None, chapeu=None):
    """Bonequinho com quadris e ombros articulados (anda). h/w mudam o tipo de corpo; a cabeça não deforma."""
    pele = pele or random.choice(PELES); cabelo = cabelo or random.choice(CABELOS)
    raiz = vazio(nome, loc); raiz.scale = (w, w, h); raiz.rotation_mode = "XYZ"
    P = {"raiz": raiz, "h": h, "w": w}
    for lado, x in (("E", -0.17), ("D", 0.17)):
        q = vazio(_id("quad"), (x, 0, 0.9)); filho(raiz, q)
        pr = capsula(_id("pernaP"), (0, 0, 0), 0.14, 0.5, calca); filho(q, pr); pr.location = (0, 0, -0.42)
        sp = esfera(_id("sap"), (0, 0, 0), 0.17, (0.95, 0.95, 0.95, 1), sub=2); sp.scale = (1, 1.4, 0.6); filho(q, sp); sp.location = (0, -0.06, -0.82); liso(sp)
        P["perna" + lado] = q
    tr = capsula(_id("troncoP"), (0, 0, 0), 0.33, 0.42, camisa, unico=unico); filho(raiz, tr); tr.location = (0, 0, 1.32); tr.scale = (1, 0.76, 1)
    P["tronco"] = tr; P["mat"] = tr.data.materials[0]
    for lado, x in (("E", -0.44), ("D", 0.44)):
        o = vazio(_id("ombP"), (x, 0, 1.6)); filho(raiz, o)
        b = capsula(_id("bracoP"), (0, 0, 0), 0.10, 0.36, camisa, unico=unico); filho(o, b); b.location = (0, 0, -0.26)
        m = esfera(_id("maoP"), (0, 0, 0), 0.12, pele, sub=2); filho(o, m); m.location = (0, 0, -0.58); liso(m)
        o.rotation_euler = (0, math.radians(-7 if lado == "D" else 7), 0); P["braco" + lado] = o
    pc = vazio(_id("pescP"), (0, 0, 1.78)); filho(raiz, pc); k = 1.0 / max(w, h) ** 0.35
    pc.scale = (k / w, k / w, k / h); P["cabeca"] = pc
    cb = esfera(_id("cabP"), (0, 0, 0), 0.40, pele, sub=3); filho(pc, cb); cb.location = (0, 0, 0.38); liso(cb)
    for x in (-0.14, 0.14):
        o = esfera(_id("olhoP"), (0, 0, 0), 0.055, PRETO, sub=2); o.scale = (1, 0.6, 1.3); filho(pc, o); o.location = (x, -0.36, 0.42)
    if chapeu is None:
        cp = esfera(_id("cabeloP"), (0, 0, 0), 0.41, cabelo, sub=3); cp.scale = (1.03, 1.0, 0.6); filho(pc, cp); cp.location = (0, 0.05, 0.58); liso(cp)
    else:   # quepe genérico (policial sem insígnia real)
        q1 = cilindro(_id("quepe"), (0, 0, 0), 0.42, 0.22, chapeu, seg=18); filho(pc, q1); q1.location = (0, 0, 0.74); liso(q1)
        ab = caixa(_id("aba"), (0, 0, 0), (0.6, 0.34, 0.06), ESCURO); filho(pc, ab); ab.location = (0, -0.42, 0.64)
        ds = caixa(_id("dist"), (0, 0, 0), (0.16, 0.04, 0.18), AMARELO); filho(tr, ds); ds.location = (0.14, -0.27, 0.12)
    return P

def andar(P, t0, t1, per=0.56, amp=32):
    """Ciclo de caminhada: pernas e braços alternados."""
    k = 0; t = t0
    for nm in ("pernaE", "pernaD", "bracoE", "bracoD"): rotk(P[nm], t0 - 0.02, 0, 7 if nm == "bracoE" else (-7 if nm == "bracoD" else 0))
    while t < t1:
        s = amp if k % 2 else -amp
        rotk(P["pernaE"], t, s); rotk(P["pernaD"], t, -s); rotk(P["bracoE"], t, -s * 0.8, 7); rotk(P["bracoD"], t, s * 0.8, -7)
        t += per / 2; k += 1
    for nm in ("pernaE", "pernaD"): rotk(P[nm], t1, 0)
    rotk(P["bracoE"], t1, 0, 7); rotk(P["bracoD"], t1, 0, -7)

def ir(P, t0, t1, a, b, per=0.56):
    """Anda de a até b (x, y) virado para o destino."""
    r = P["raiz"]; z = r.location.z
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) + 90
    rotk(r, t0 - 0.25, 0, 0, math.degrees(r.rotation_euler.z)); rotk(r, t0, 0, 0, ang)
    lock(r, t0, (a[0], a[1], z)); lock(r, t1, (b[0], b[1], z)); andar(P, t0, t1, per)

def passeio(P, janelas, x0, vel, a, b, y, z=0.0):
    """Anda em linha reta em X com volta ao começo (wrap) nas janelas de tempo dadas."""
    r = P["raiz"]; L = b - a; girar(r, 90 if vel > 0 else -90)
    for (ta, tb) in janelas:
        for fr in range(f(ta), f(tb) + 1):
            t = (fr - 1) / 30.0; r.location = (a + ((x0 - a) + vel * t) % L, y, z); r.keyframe_insert("location", frame=fr)
        andar(P, ta, tb, per=0.56 / max(0.6, abs(vel) / 1.6))

def bracos(P, t, dur, rx=-150, ry=0):
    """Levanta os dois braços (susto / bronca) e volta."""
    for lado, s in (("E", 1), ("D", -1)):
        rotk(P["braco" + lado], t - 0.02, 0, 7 * s); rotk(P["braco" + lado], t + 0.2, rx, ry * s); rotk(P["braco" + lado], t + dur - 0.2, rx, ry * s); rotk(P["braco" + lado], t + dur, 0, 7 * s)

def carrinho(nome, cor, s=1.0, unico=None):
    """Carro genérico de brinquedo (sem marca). Frente = +X local."""
    r = vazio(nome); r.scale = (s,) * 3
    c = caixa(_id("carroc"), (0, 0, 0), (2.4, 1.1, 0.55), cor, unico=unico); filho(r, c); c.location = (0, 0, 0.55)
    cb = caixa(_id("cabine"), (0, 0, 0), (1.2, 0.96, 0.5), (0.78, 0.92, 1.0, 1)); filho(r, cb); cb.location = (-0.15, 0, 1.05)
    for x in (-0.75, 0.75):
        for y in (-0.52, 0.52):
            rd = cilindro(_id("roda"), (0, 0, 0), 0.28, 0.2, ESCURO, seg=14); rd.rotation_euler = (math.radians(90), 0, 0); filho(r, rd); rd.location = (x, y, 0.28)
    fr = caixa(_id("farol"), (0, 0, 0), (0.06, 0.8, 0.14), (1.0, 0.95, 0.6, 1)); filho(r, fr); fr.location = (1.21, 0, 0.6)
    return r

def fachada(x, y, w, h, cor, porta=False):
    """Prédio de fundo com janelas (cidade genérica)."""
    caixa(_id("fach"), (x, y, h / 2), (w, 1.2, h), cor)
    nx = max(2, int(w / 1.3)); nz = max(2, int(h / 1.6))
    for i in range(nx):
        for j in range(nz):
            if porta and j == 0: continue
            caixa(_id("jan"), (x - w / 2 + (i + 0.5) * w / nx, y - 0.62, 1.5 + j * 1.6), (0.62, 0.06, 0.8), (0.70, 0.90, 1.0, 1) if (i + j) % 3 else (1.0, 0.92, 0.55, 1))
    if porta:
        caixa(_id("porta"), (x, y - 0.62, 1.0), (1.2, 0.08, 2.0), (0.35, 0.22, 0.16, 1))
        caixa(_id("toldo"), (x, y - 1.0, 2.5), (w * 0.9, 0.9, 0.16), (0.98, 0.40, 0.36, 1))

def rua(x, larg=30, predios=True):
    """Calçada + rua + prédios coloridos ao fundo."""
    caixa(_id("calc"), (x, -1.0, -0.1), (larg, 10, 0.2), CALCADA)
    caixa(_id("asf"), (x, 6.0, -0.12), (larg, 4.4, 0.2), ASFALTO)
    for k in range(int(larg / 3)):
        caixa(_id("faixa"), (x - larg / 2 + 1.5 + k * 3, 6.0, -0.01), (1.4, 0.16, 0.02), BRANCO)
    caixa(_id("meio"), (x, 3.9, 0.02), (larg, 0.22, 0.2), (0.62, 0.62, 0.68, 1))
    if predios:
        px = x - larg / 2 + 2
        k = 0
        while px < x + larg / 2:
            w = 3.2 + (k % 3) * 0.7; fachada(px, 9.4, w, 6.5 + ((k * 7) % 5) * 1.6, PREDIOS[k % len(PREDIOS)] if k % 2 else CORES[k % 6]); px += w + 0.25; k += 1
        caixa(_id("ceuF"), (x, 11.0, 9), (larg, 0.4, 22), (0.62, 0.80, 1.0, 1))

def balao(P, cor, t):
    """'Humor' do pedestre: bolinha colorida flutuando sobre a cabeça."""
    r = P["raiz"]; b = esfera(_id("balao"), (0, 0, 0), 0.36, cor, sub=3, unico=_id("bl")); liso(b); brilha(b)
    b.location = (r.location.x, r.location.y, 2.75 * P["h"] + 0.35); visivel(b, t - 0.05); pop(b, t - 0.05)
    return b

def prancheta(nome, loc, s=1.0):
    """Quadro de 'descrição' com 3 ícones: roupa, carro, dupla. Retorna dict."""
    r = vazio(nome, loc); r.scale = (s,) * 3
    q = caixa(_id("quadro"), (0, 0, 0), (4.6, 0.14, 2.0), (0.22, 0.24, 0.32, 1)); filho(r, q)
    D = {"raiz": r}
    for i, nm in enumerate(("roupa", "carro", "dupla")):
        cx = -1.5 + i * 1.5
        sl = caixa(_id("slot"), (0, 0, 0), (1.3, 0.05, 1.6), BRANCO); filho(r, sl); sl.location = (cx, -0.09, 0)
        g = vazio(_id("ic"), (0, 0, 0)); filho(r, g); g.location = (cx, -0.2, 0)
        if nm == "roupa":
            c = caixa(_id("cam"), (0, 0, 0), (0.62, 0.08, 0.78), VERMELHO); filho(g, c); c.location = (0, 0, -0.05)
            for sx in (-1, 1):
                m = caixa(_id("manga"), (0, 0, 0), (0.36, 0.08, 0.3), VERMELHO); filho(g, m); m.location = (sx * 0.42, 0, 0.22); m.rotation_euler = (0, math.radians(sx * 25), 0)
        elif nm == "carro":
            c = carrinho(_id("icar"), AMARELO, 0.42); filho(g, c); c.location = (0, 0, -0.3)
        else:
            for sx, cor in ((-0.26, VERMELHO), (0.26, ROXO)):
                cp = capsula(_id("icp"), (0, 0, 0), 0.17, 0.3, cor); filho(g, cp); cp.location = (sx, 0, -0.22)
                hd = esfera(_id("ich"), (0, 0, 0), 0.19, PELE, sub=2); filho(g, hd); hd.location = (sx, 0, 0.32); liso(hd)
        D[nm] = g
    return D

def xis(nome, loc, s=1.0):
    r = vazio(nome, loc); r.scale = (s,) * 3
    for a in (-42, 42):
        b = caixa(_id("xb"), (0, 0, 0), (2.2, 0.12, 0.34), VERMELHO, unico="xis"); filho(r, b); b.rotation_euler = (0, math.radians(a), 0)
    return r

cam, alvo, cam_key, plano = camera_cartoon(24)

# =====================================================================
# ZONA H (x = -40) — rua cheia de pedestres andando  (bloco 0 gancho e bloco 6 CTA)
# =====================================================================
t0, t1 = S[0]
rua(-40)
JAN = [(0.0, S[0][1] + 0.2), (S[6][0] - 0.2, FIM)]
multidao = []
TIPOS = [(1.0, 1.0), (1.25, 0.9), (0.75, 1.05), (1.05, 1.35), (0.9, 0.95), (1.15, 1.1)]
for k in range(16):
    h, w = TIPOS[k % 6]
    p = pedestre(_id("ped"), (0, 0, 0), CORES[k % 6], calca=random.choice([(0.22, 0.26, 0.36, 1), (0.35, 0.30, 0.25, 1), (0.15, 0.35, 0.45, 1)]), h=h * 1.05, w=w * 1.05)
    y = (1.5, 2.5, 3.3)[k % 3] + random.uniform(-0.2, 0.2)
    vel = random.choice([1, -1]) * random.uniform(1.3, 2.2)
    passeio(p, JAN, -49 + k * 1.15 + random.uniform(0, 0.5), vel, -49.5, -30.5, y)
    multidao.append(p)
for k, (cor, vel, y) in enumerate(((AMARELO, 4.2, 5.2), (CIANO, -3.6, 6.9), ((0.98, 0.45, 0.35, 1), 3.4, 5.2))):
    c = carrinho(_id("car"), cor); girar(c, 0 if vel > 0 else 180)
    for (ta, tb) in JAN:
        for fr in range(f(ta), f(tb) + 1):
            t = (fr - 1) / 30.0; c.location = (-52 + ((k * 9) + vel * t) % 24, y, 0); c.keyframe_insert("location", frame=fr)
eu0 = pixel("eu0", (-40.3, -0.6, 0)); girar(eu0["raiz"], 8); respirar(eu0, 0, FIM)
espanto(eu0, 0.15, 1.5); apontar(eu0, T(0, "pedestres") - 0.25, 1.6, "D", 60); pensar(eu0, T(0, "Como") - 0.1, 1.9)
cam_key(0, (-40.0, -7.4, 3.4), (-40.0, 3.0, 3.0)); cam_key(T(0, "pedestres"), (-39.6, -7.0, 3.2), (-39.8, 3.0, 2.7))
cam_key(T(0, "Como") - 0.15, (-40.2, -5.0, 2.7), (-40.3, 0.5, 2.6)); cam_key(t1 - 0.05, (-40.3, -4.6, 2.7), (-40.3, 0.5, 2.7))

# =====================================================================
# ZONA A (x = 0) — duas pilhas de 'cartões de animação': 55 mil x 600 mil  (bloco 1, 1ª parte)
# =====================================================================
t0, t1 = S[1]; ttime = T(1, "time") - 0.45
sala_fechada("A", 0, (0.36, 0.78, 0.74, 1), (0.42, 0.30, 0.70, 1), prof=3.6)
caixa("Aalto", (0, 3.6, 11), (22, 0.4, 10), (0.42, 0.30, 0.70, 1))
for x in (-0.5, 1.9):
    cilindro(_id("baseP"), (x, 1.6, 0.12), 0.95, 0.24, (0.20, 0.20, 0.28, 1), seg=24)
def cartao(x, k, t):
    c = caixa(_id("cartao"), (x, 1.6, 0.34 + k * 0.165), (1.25, 0.95, 0.13), CORES[k % 6])
    c.rotation_euler = (0, 0, math.radians((k * 37) % 16 - 8)); visivel(c, t); pop(c, t, dur=0.2); return c
for k in range(3): cartao(-0.5, k, T(1, "cinquenta") - 0.2 + k * 0.15)
ta = T(1, "Agora") - 0.1; tb = T(1, "isso") + 0.2
for k in range(33): cartao(1.9, k, ta + (tb - ta) * k / 32)
# placas de HUD no cenário (backlog #3): o número entra por cima como pílula
h1 = hud("hud55", (-0.5, 1.5, 1.75), w=1.9, h=0.8); visivel(h1, T(1, "cinquenta") - 0.1); pop(h1, T(1, "cinquenta") - 0.1)
h2 = hud("hud600", (1.9, 1.5, 6.65), w=2.3, h=0.95); visivel(h2, T(1, "dez") - 0.1); pop(h2, T(1, "dez") - 0.1)
gA = pixel("guiaA", (-2.1, -1.0, 0), escala=0.95); girar(gA["raiz"], 14); respirar(gA, t0, ttime + 0.5)
apontar(gA, T(1, "cinquenta") - 0.3, 1.5, "D", 35); espanto(gA, T(1, "Agora") + 0.1, 1.5); apontar(gA, T(1, "dez") + 0.1, 2.0, "D", 95)
cam_key(t0, (-0.6, -7.6, 2.4), (-0.6, 1.5, 2.2)); cam_key(T(1, "Agora") - 0.1, (-0.6, -7.6, 2.4), (-0.6, 1.5, 2.2))
cam_key(T(1, "dez") + 0.2, (-0.2, -9.0, 3.9), (-0.1, 1.5, 3.7)); cam_key(ttime - 0.05, (-0.2, -8.8, 3.9), (-0.1, 1.5, 3.8))

# =====================================================================
# ZONA B (x = 40) — o estúdio: um time que só cuida dos pedestres  (bloco 1, 2ª parte)
# =====================================================================
sala_fechada("B", 40, (0.95, 0.80, 0.58, 1), (0.30, 0.62, 0.72, 1), prof=4.4)
caixa("Balto", (40, 4.4, 11), (22, 0.4, 10), (0.30, 0.62, 0.72, 1))
ped = cilindro("pedestalB", (40.9, 1.2, 0.75), 1.0, 1.5, (0.92, 0.92, 0.96, 1), seg=28)
modelo = pedestre("modeloB", (40.9, 1.2, 1.5), (0.98, 0.45, 0.35, 1), h=1.15, w=1.1, cabelo=CABELOS[2])
ordem = [modelo["pernaE"], modelo["pernaD"], modelo["tronco"], modelo["bracoE"], modelo["bracoD"], modelo["cabeca"]]
for k, parte in enumerate(ordem):
    tp = ttime + 0.3 + k * 0.2; visivel(parte, tp); 
    s0 = tuple(parte.scale); parte.scale = (0.001,) * 3; parte.keyframe_insert("scale", frame=max(1, f(tp) - 1)); parte.scale = tuple(v * 1.15 for v in s0); parte.keyframe_insert("scale", frame=f(tp + 0.2)); parte.scale = s0; parte.keyframe_insert("scale", frame=f(tp + 0.3))
rotk(modelo["raiz"], T(1, "cuida") - 0.2, 0, 0, 0); rotk(modelo["raiz"], t1, 0, 0, 360)
for k, (x, y, cor) in enumerate(((38.6, 2.6, AZUL), (43.0, 2.7, VERDE), (41.0, 3.4, ROXO))):
    caixa(_id("mesaB"), (x, y - 0.5, 0.75), (1.5, 0.7, 0.1), (0.55, 0.36, 0.24, 1)); caixa(_id("peB"), (x, y - 0.5, 0.36), (0.12, 0.5, 0.72), (0.25, 0.25, 0.30, 1))
    mn = caixa(_id("monB"), (x + 0.2, y - 0.45, 1.25), (0.8, 0.08, 0.55), PRETO); tl = caixa(_id("telaB"), (0, 0, 0), (0.7, 0.02, 0.45), CIANO); filho(mn, tl); tl.location = (0, -0.05, 0); mn.rotation_euler = (0, 0, math.radians(180))
    a = pedestre(_id("artista"), (x, y, 0), cor, h=1.0, w=1.0); girar(a["raiz"], (-25, 25, 0)[k])
    t = ttime; j = 0
    while t < t1:   # 'trabalhando': braço sobe e desce
        rotk(a["bracoD"], t, -70 if j % 2 else -35, -7); rotk(a["bracoE"], t, -35 if j % 2 else -70, 7); t += 0.3; j += 1
gB = pixel("guiaB", (38.3, -1.2, 0), escala=0.95); girar(gB["raiz"], 16); respirar(gB, ttime, t1 + 0.5)
acenar(gB, ttime + 0.05, 1.0); apontar(gB, T(1, "Los") - 0.1, 1.2, "D", 50); comemorar(gB, T(1, "cuida") + 0.2, 1.1)
cam_key(ttime, (40.0, -7.4, 2.6), (40.2, 1.2, 2.3)); cam_key(t1 - 0.05, (40.3, -6.6, 2.6), (40.5, 1.2, 2.3))

# =====================================================================
# ZONA C (x = 80) — a mesma animação se ajusta ao alto, ao baixo e ao forte  (bloco 2)
# =====================================================================
t0, t1 = S[2]
sala_fechada("C", 80, (0.70, 0.74, 0.86, 1), (0.98, 0.70, 0.52, 1), prof=4.0)
caixa("Calto", (80, 4.0, 11), (22, 0.4, 10), (0.98, 0.70, 0.52, 1))
CORPOS = [("alto", 79.0, 1.42, 0.82, AZUL), ("baixo", 80.6, 0.72, 1.0, VERDE), ("forte", 82.2, 1.08, 1.5, ROXO)]
tcorpo = T(2, "corpo") - 0.3; taj = T(2, "ajusta")
peds2 = []
for k, (nm, x, h, w, cor) in enumerate(CORPOS):
    pd = cilindro(_id("pedC"), (x, 1.5, 0.2), 0.78, 0.4, (0.92, 0.92, 0.96, 1), seg=24, unico="pd" + nm)
    p = pedestre("corpo_" + nm, (x, 1.5, 0.4), cor, h=h, w=w)
    visivel(p["raiz"], tcorpo + k * 0.22)
    rz = p["raiz"]; s0 = tuple(rz.scale); rz.scale = (0.001,) * 3; rz.keyframe_insert("scale", frame=max(1, f(tcorpo + k * 0.22) - 1)); rz.scale = s0; rz.keyframe_insert("scale", frame=f(tcorpo + k * 0.22 + 0.25))
    peds2.append((p, pd, x))
# o cartão de animação (um só) aparece no alto e manda uma cópia para cada corpo
tcard = T(2, "truque") - 0.1
def cartao_anim(nome, loc, s=1.0):
    c = caixa(nome, loc, (1.5 * s, 0.14 * s, 1.0 * s), AMARELO, unico=_id("ca")); brilha(c)
    tri = cilindro(_id("playC"), (0, 0, 0), 0.3 * s, 0.06 * s, BRANCO, seg=3); filho(c, tri); tri.rotation_euler = (math.radians(90), math.radians(90), 0); tri.location = (0, -0.1 * s, 0)
    for sx in (-1, 1):
        for j in range(3):
            fz = caixa(_id("furo"), (0, 0, 0), (0.12 * s, 0.03 * s, 0.14 * s), ESCURO); filho(c, fz); fz.location = (sx * 0.62 * s, -0.08 * s, (-0.3 + j * 0.3) * s)
    return c
mestre = cartao_anim("cartaoMestre", (80.6, 1.3, 5.9), 1.25); visivel(mestre, tcard); pop(mestre, tcard, 1.0)
for k, (p, pd, x) in enumerate(peds2):
    tc = taj + k * 0.12
    c = cartao_anim(_id("copia"), (80.6, 1.3, 5.9), 0.6); visivel(c, tc, tc + 0.6)
    caminho(c, tc, tc + 0.55, lambda u, x=x, p=p: bez((80.6, 1.3, 5.6), ((80.6 + x) / 2, 1.0, 5.0), (x, 1.4, 0.4 + 1.5 * p["h"]), suave(u)), orientar=False)
    andar(p, tc + 0.55, t1 + 0.3, per=0.62, amp=36)     # todos no MESMO ciclo
for (nm, x, h, w, cor), (p, pd, _) in zip(CORPOS, peds2):
    m = pd.data.materials[0]; tn = T(2, nm)
    cor_key(m, tn - 0.08, (0.92, 0.92, 0.96, 1)); cor_key(m, tn + 0.05, AMARELO); cor_key(m, tn + 0.75, AMARELO); cor_key(m, tn + 1.0, (0.92, 0.92, 0.96, 1))
gC = pixel("guiaC", (77.9, -1.3, 0), escala=0.9); girar(gC["raiz"], 16); respirar(gC, t0, t1 + 0.5)
pensar(gC, t0 + 0.1, 1.5); espanto(gC, T(2, "impossível") - 0.2, 1.3); apontar(gC, tcard, 1.6, "D", 95); comemorar(gC, taj + 0.5, 1.1); apontar(gC, T(2, "baixo") - 0.1, 1.4, "D", 45)
cam_key(t0, (79.2, -7.2, 2.5), (79.6, 1.5, 2.2)); cam_key(tcard - 0.4, (79.3, -7.2, 2.5), (79.7, 1.5, 2.3))
cam_key(tcard + 0.3, (79.6, -8.6, 3.5), (79.9, 1.5, 3.2)); cam_key(taj + 0.8, (79.7, -8.0, 3.0), (79.9, 1.5, 2.6)); cam_key(t1 - 0.05, (79.8, -7.6, 2.9), (80.0, 1.5, 2.5))

# =====================================================================
# ZONA D (x = 120) — temperamento: calmo, medroso, esquentado; um foge, o outro parte para cima  (bloco 3)
# =====================================================================
t0, t1 = S[3]
rua(120)
calmo = pedestre("calmo", (119.6, 1.5, 0), (0.45, 0.85, 0.45, 1), h=1.1, w=1.05, cabelo=CABELOS[1])
bravo = pedestre("bravo", (121.0, 1.7, 0), (0.98, 0.45, 0.35, 1), h=1.15, w=1.35, cabelo=CABELOS[0])
medroso = pedestre("medroso", (122.4, 1.5, 0), (0.98, 0.80, 0.25, 1), h=1.0, w=0.9, cabelo=CABELOS[2])
tand = T(3, "andar"); ttemp = T(3, "temperamento")
for p in (calmo, bravo, medroso): andar(p, t0, ttemp - 0.2, per=0.6, amp=22)   # 'andar não basta': marcham no lugar
bC = balao(calmo, VERDE, T(3, "calmo")); bM = balao(medroso, AMARELO, T(3, "medroso")); bB = balao(bravo, VERMELHO, T(3, "esquentado"))
gD = pixel("guiaD", (117.7, -0.9, 0), escala=0.95); girar(gD["raiz"], 18); respirar(gD, t0, t1 + 0.5)
tmx = T(3, "Mexeu"); tfg = T(3, "foge") - 0.25; tpc = T(3, "parte") - 0.2
pensar(gD, t0 + 0.2, 1.4); apontar(gD, T(3, "calmo") - 0.1, 2.4, "D", 60)
# 'Mexeu com eles?': o Pixel dá um passo e cutuca
rD = gD["raiz"]; lock(rD, tmx - 0.1, (117.7, -0.9, 0)); lock(rD, tmx + 0.3, (118.5, -0.4, 0)); apontar(gD, tmx, 1.4, "D", 70)
# medroso: susto e corre para fora
bracos(medroso, tmx + 0.35, 0.7, -160); ir(medroso, tfg, tfg + 1.3, (122.4, 1.5), (129.5, 2.4), per=0.3)
visivel(bM, T(3, "medroso") - 0.05, tfg + 0.1)
# calmo: só olha (vira a cabeça)
rotk(calmo["cabeca"], tmx, 0, 0, 0); rotk(calmo["cabeca"], tmx + 0.4, 0, 0, -35); rotk(calmo["cabeca"], tfg, 0, 0, -35); rotk(calmo["cabeca"], tfg + 0.5, 0, 0, 40); rotk(calmo["cabeca"], t1, 0, 0, 25)
# esquentado: parte para cima do Pixel, braços erguidos; o Pixel recua assustado
ir(bravo, tpc, tpc + 0.9, (121.0, 1.7), (119.6, 0.0), per=0.36)
bB.keyframe_insert("location", frame=f(tpc)); bB.location = (119.6, 0.0, bB.location.z); bB.keyframe_insert("location", frame=f(tpc + 0.9))
bracos(bravo, tpc + 0.85, t1 - tpc, -150, 20)
lock(rD, tpc + 0.4, (118.5, -0.4, 0)); lock(rD, tpc + 1.0, (117.4, -1.2, 0)); espanto(gD, tpc + 0.35, t1 - tpc)
cam_key(t0, (120.0, -6.6, 2.5), (120.3, 1.5, 2.3)); cam_key(ttemp, (120.1, -6.9, 2.7), (120.4, 1.5, 2.5))
cam_key(tmx - 0.1, (120.4, -7.2, 2.7), (120.6, 1.2, 2.4)); cam_key(tfg + 0.6, (120.6, -7.4, 2.7), (120.9, 1.2, 2.4))
cam_key(tpc + 0.5, (119.4, -6.2, 2.6), (119.4, 0.4, 2.3)); cam_key(t1 - 0.05, (119.3, -6.0, 2.6), (119.3, 0.4, 2.3))

# =====================================================================
# ZONA E (x = 160) — o crime e a testemunha  (bloco 4, 1ª parte)
# =====================================================================
t0, t1 = S[4]; tpol = T(4, "polícia") - 0.35
caixa("Ecalc", (160, -1.0, -0.1), (30, 10, 0.2), CALCADA)
fachada(159.0, 4.6, 6.0, 9.0, (0.98, 0.84, 0.40, 1), porta=True); fachada(164.6, 4.6, 5.0, 12.0, (0.55, 0.78, 1.0, 1)); fachada(153.8, 4.6, 4.2, 11.0, (0.96, 0.76, 0.70, 1))
caixa("Eceu", (160, 6.0, 12), (30, 0.4, 26), (0.62, 0.80, 1.0, 1))
alarme = esfera("alarme", (159.0, 3.5, 3.3), 0.3, (0.5, 0.12, 0.12, 1), sub=3, unico="alarme"); liso(alarme); brilha(alarme)
tcr = T(4, "crime") - 0.2
k = 0; t = tcr
while t < tpol: cor_key(alarme.data.materials[0], t, VERMELHO if k % 2 == 0 else (0.45, 0.10, 0.10, 1)); t += 0.3; k += 1
carroE = carrinho("carroFuga", AMARELO, 1.0); carroE.location = (156.9, 2.3, 0)
jog = pedestre("jogador", (159.0, 2.9, 0), VERMELHO, h=1.12, w=1.05, cabelo=CABELOS[0], unico="camJog")
par = pedestre("parceira", (158.0, 1.9, 0), ROXO, h=1.05, w=0.95, cabelo=CABELOS[3]); girar(par["raiz"], 90)
saco = esfera("saco", (0, 0, 0), 0.3, (0.35, 0.75, 0.40, 1), sub=3); liso(saco); filho(jog["bracoD"], saco); saco.location = (0, -0.05, -0.85)
no = cilindro("noSaco", (0, 0, 0), 0.09, 0.2, (0.25, 0.55, 0.30, 1), seg=8); filho(saco, no); no.location = (0, 0, 0.3)
ir(jog, tcr, tcr + 1.0, (159.0, 2.9), (158.2, 1.2), per=0.34)    # sai correndo da loja com o saco
tes = pedestre("testemunha", (162.3, 1.0, 0), (0.30, 0.70, 1.0, 1), h=1.1, w=1.0, cabelo=CABELOS[4]); girar(tes["raiz"], -70)
tq = T(4, "quem") - 0.1
for k in range(5):   # linha de visão (tracinhos amarelos) da testemunha até o jogador
    u = (k + 0.5) / 5; d = caixa(_id("visao"), (161.8 - 3.2 * u, 1.0 + 0.15 * u, 2.25), (0.4, 0.1, 0.1), AMARELO); visivel(d, tq + k * 0.07, tpol); brilha(d)
excl = cilindro("excl", (162.3, 1.0, 3.45), 0.13, 0.55, AMARELO, seg=10, r2=0.07, unico="excl"); excl.rotation_euler = (math.radians(180), 0, 0)
pt = esfera("exclP", (162.3, 1.0, 2.98), 0.1, AMARELO, sub=2, unico="excl"); brilha(excl)
for o in (excl, pt): visivel(o, T(4, "testemunha") - 0.1, tpol); pop(o, T(4, "testemunha") - 0.1)
bracos(tes, T(4, "testemunha"), 0.9, -140, 15)
gE = pixel("guiaE", (157.6, -1.7, 0), escala=0.85); girar(gE["raiz"], 22); respirar(gE, t0, tpol + 0.5)
apontar(gE, tcr, 1.3, "D", 60); espanto(gE, tq, 1.6)
cam_key(t0, (159.2, -6.8, 2.9), (159.2, 2.0, 2.4)); cam_key(tq - 0.2, (159.8, -7.0, 2.9), (159.8, 1.6, 2.4))
cam_key(T(4, "testemunha"), (159.9, -6.9, 2.9), (159.9, 1.2, 2.4)); cam_key(tpol - 0.05, (159.9, -6.7, 2.9), (159.9, 1.2, 2.4))

# =====================================================================
# ZONA F (x = 200) — a polícia recebe a descrição: roupa, carro, dupla  (bloco 4, 2ª parte)
# =====================================================================
sala_fechada("F", 200, (0.62, 0.72, 0.98, 1), (0.20, 0.24, 0.42, 1), prof=3.4)
caixa("Falto", (200, 3.4, 11), (22, 0.4, 10), (0.20, 0.24, 0.42, 1))
PR = prancheta("prancheta", (200.2, 3.0, 4.5), 1.3)
for nm in ("roupa", "carro", "dupla"):
    tn = T(4, nm) - 0.1; visivel(PR[nm], tn); pop(PR[nm], tn)
pol = pedestre("policial", (198.9, 0.9, 0), MARINHO, calca=(0.08, 0.10, 0.22, 1), h=1.15, w=1.1, chapeu=MARINHO, pele=PELES[1]); girar(pol["raiz"], 20)
rotk(pol["bracoD"], tpol, 0, -7); rotk(pol["bracoE"], tpol, 0, 7); rotk(pol["bracoE"], T(4, "descrição"), -165, 20); rotk(pol["bracoE"], t1, -165, 20)
lamp = esfera("giro", (197.2, 3.0, 5.9), 0.26, AZUL, sub=3, unico="giro"); liso(lamp); brilha(lamp)
k = 0; t = tpol
while t < t1: cor_key(lamp.data.materials[0], t, AZUL if k % 2 == 0 else VERMELHO); t += 0.35; k += 1
gF = pixel("guiaF", (201.9, -1.2, 0), escala=0.9); girar(gF["raiz"], -14); respirar(gF, tpol, t1 + 0.5)
apontar(gF, T(4, "roupa") - 0.2, 1.0, "E", 80); apontar(gF, T(4, "carro") - 0.2, 0.9, "E", 85); apontar(gF, T(4, "dupla") - 0.25, 1.2, "E", 90)
cam_key(tpol, (200.3, -7.0, 3.2), (200.3, 2.0, 3.0)); cam_key(t1 - 0.05, (200.4, -6.5, 3.2), (200.4, 2.0, 3.0))

# =====================================================================
# ZONA G (x = 240) — a descrição não bate mais: trocou de roupa, separou da dupla  (bloco 5)
# =====================================================================
t0, t1 = S[5]
rua(240)
PG = prancheta("pranchetaG", (238.6, 2.4, 4.3), 0.62)
caixa("posteG", (238.6, 2.5, 1.9), (0.14, 0.14, 3.8), (0.25, 0.25, 0.30, 1))
visivel(PG["carro"], 0, 0.05)   # aqui a descrição mostra só a roupa e a dupla
polG = pedestre("policialG", (238.4, 1.0, 0), MARINHO, calca=(0.08, 0.10, 0.22, 1), h=1.15, w=1.1, chapeu=MARINHO, pele=PELES[1]); girar(polG["raiz"], 20)
jogG = pedestre("jogadorG", (241.0, 1.3, 0), VERMELHO, h=1.12, w=1.05, cabelo=CABELOS[0], unico="camJogG"); girar(jogG["raiz"], -15)
parG = pedestre("parceiraG", (242.0, 1.5, 0), ROXO, h=1.05, w=0.95, cabelo=CABELOS[3]); girar(parG["raiz"], -10)
ttr = T(5, "Trocou"); tsp = T(5, "separou") - 0.1; tnb = T(5, "bate") - 0.25; tdf = T(5, "difícil") - 0.3
# policial procura: cabeça de um lado para o outro
k = 0; t = t0
while t < t1: rotk(polG["cabeca"], t, 0, 0, 35 if k % 2 else -30); t += 0.9; k += 1
# troca de roupa: pulinho + camisa muda de vermelho para verde
mj = jogG["mat"]; cor_key(mj, ttr + 0.25, VERMELHO); cor_key(mj, ttr + 0.4, (0.25, 0.80, 0.45, 1))
rj = jogG["raiz"]
for dt, dz in ((0.1, 0), (0.3, 0.45), (0.5, 0)): lock(rj, ttr + dt, (241.0, 1.3, dz))
giro = anel("giroTroca", (241.0, 1.3, 1.5), 0.75, 0.07, AMARELO, unico="gt"); brilha(giro); visivel(giro, ttr + 0.1, ttr + 0.75)
key(giro, "scale", ttr + 0.1, (0.3, 0.3, 0.3)); key(giro, "scale", ttr + 0.7, (1.5, 1.5, 1.5))
# a parceira vai embora para o outro lado
ir(parG, tsp, tsp + 1.5, (242.0, 1.5), (249.0, 2.6), per=0.42)
# X vermelho em cima da prancheta
X = xis("xisG", (238.6, 2.1, 4.3), 0.85); visivel(X, tnb); pop(X, tnb, 0.85)
rotk(polG["bracoD"], tnb, 0, -7); rotk(polG["bracoD"], tnb + 0.3, -150, -25); rotk(polG["bracoD"], t1, -150, -25)   # coça a cabeça
# o jogador passa tranquilo pela frente do policial e some
ir(jogG, tdf, t1 + 0.4, (241.0, 1.3), (234.0, 0.2), per=0.6)
gG = pixel("guiaG", (242.4, -1.4, 0), escala=0.9); girar(gG["raiz"], -16); respirar(gG, t0, t1 + 0.5)
pensar(gG, t0 + 0.15, 1.6); apontar(gG, ttr - 0.1, 1.2, "E", 55); apontar(gG, tsp, 1.2, "D", 60); comemorar(gG, tnb + 0.2, 1.2); acenar(gG, tdf + 0.3, 1.3)
cam_key(t0, (240.2, -7.4, 3.0), (240.2, 1.4, 2.7)); cam_key(ttr - 0.2, (240.8, -6.6, 2.8), (240.9, 1.3, 2.5))
cam_key(tsp + 0.9, (241.0, -6.8, 2.8), (241.1, 1.3, 2.5)); cam_key(tnb, (240.2, -7.4, 3.1), (240.2, 1.4, 2.8)); cam_key(t1 - 0.05, (240.2, -7.2, 3.1), (240.2, 1.4, 2.8))

# =====================================================================
# 6 — CTA de volta à rua cheia (câmera aberta: o CTA não encosta na cabeça — backlog #9)
# =====================================================================
t0 = S[6][0]
acenar(eu0, t0 + 0.15, 1.4); comemorar(eu0, T(6, "zerei") - 0.1, 1.2); pensar(eu0, T(6, "Ainda") - 0.1, 1.2); apontar(eu0, T(6, "fila") - 0.2, 1.3, "D", 60)
tl = LEG[-1]["e"] + 0.5
acenar(eu0, tl, 1.4); comemorar(eu0, tl + 1.6, 1.3); acenar(eu0, tl + 3.0, 1.2)
cam_key(t0, (-40.1, -8.2, 3.0), (-40.3, 0.5, 2.7)); cam_key(FIM, (-40.2, -7.6, 3.0), (-40.3, 0.5, 2.7))

# ---------- render ----------
modo_cartoon(samples=int(os.environ.get("AMOSTRAS", "8")))
for m in set(BRILHO):
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Emission Color"].default_value = b.inputs["Base Color"].default_value
        b.inputs["Emission Strength"].default_value = 0.8
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
