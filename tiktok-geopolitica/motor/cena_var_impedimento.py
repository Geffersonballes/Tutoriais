"""Série 2 (teste de FUTEBOL) — 'Como o VAR decide um impedimento?' (estilo C cartoon, mascote Pixel, visual nível 2).
Mecanismo: gol anulado por um ombro -> 12 câmeras no teto filmando os jogadores -> esqueleto de pontos (braço não conta)
-> chip dentro da bola marca o instante do passe -> passe congelado + duas linhas 3D + alerta -> árbitro de vídeo confere
e o telão mostra a animação -> no Brasil: 28-32 câmeras, sem chip, 47 s em média -> convite (linha ou bandeira).
Visual 100 % original: campo, jogadores-brinquedo genéricos (uniformes LISOS ciano x magenta, sem escudo/número/patrocínio),
bola de gomos inventados. Nada de imagem de transmissão, logo de clube/liga/FIFA/CBF ou rosto real.
Base: cena_matchmaking.py. Uso: blender -b --factory-startup -P cena_var_impedimento.py -- <pasta> [preview t1,t2 | range a,b]"""
import bpy, bmesh, sys, os, json, math, random, re, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowpoly import *
from lowpoly import _id
from cartoon import *

args = sys.argv[sys.argv.index("--") + 1:]
PASTA = args[0]
LEG = json.load(open(os.path.join(PASTA, "legendas.json"), encoding="utf-8"))
FIM = LEG[-1]["e"] + 4.6          # cobre também o pedido de like
NSEG = max(x["seg"] for x in LEG) + 1
def seg_ini(i): return 0.0 if i == 0 else min(x["s"] for x in LEG if x["seg"] == i) - 0.15
def seg_fim(i): return seg_ini(i + 1) if i < NSEG - 1 else FIM
_norm = lambda s: re.sub(r"[^a-z0-9-]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
def T(i, palavra, n=0):
    hits = [x["s"] for x in LEG if x["seg"] == i and _norm(x["w"]) == _norm(palavra)]
    if not hits:
        hits = [x["s"] for x in LEG if x["seg"] == i and palavra.lower() in x["w"].lower()]
    return hits[min(n, len(hits) - 1)] if hits else seg_ini(i) + 0.5
S = [(seg_ini(i), seg_fim(i)) for i in range(NSEG)]

bpy.ops.wm.read_factory_settings(use_empty=True)
configurar_render()
scn = bpy.context.scene
scn.frame_start, scn.frame_end = 1, f(FIM)
random.seed(27)

AMARELO = (1.0, 0.82, 0.12, 1); VERDE = (0.20, 0.85, 0.40, 1); VERMELHO = (0.95, 0.22, 0.20, 1)
AZUL = (0.20, 0.55, 1.0, 1); BRANCO = (0.97, 0.97, 0.98, 1); CIANO = (0.25, 0.95, 1.0, 1)
ESCURO = (0.10, 0.11, 0.14, 1); CINZA = (0.40, 0.42, 0.48, 1); OURO = (1.0, 0.72, 0.10, 1)
TIME_A = (0.10, 0.80, 0.85, 1)     # ataque: ciano liso (cor de fantasia)
TIME_D = (0.90, 0.25, 0.70, 1)     # defesa: magenta liso (cor de fantasia)
GRAMA1 = (0.30, 0.72, 0.32, 1); GRAMA2 = (0.24, 0.62, 0.27, 1); CHIPV = (0.10, 0.55, 0.30, 1)
BRILHO = []
def brilha(ob): BRILHO.append(ob.data.materials[0]); return ob
def girarZ(ob, graus): ob.rotation_euler = (0, 0, math.radians(graus))

# ---------------------------------------------------------------- modelos
def jogador(nome, loc, cor, s=1.0, cabelo=None):
    """Jogador-brinquedo genérico: corpo em cápsula (camisa lisa), short escuro, cabeça redonda com olhinhos e cabelo."""
    raiz = vazio(nome, loc); raiz.scale = (s, s, s)
    corpo = capsula(_id("corpoJ"), (0, 0, 0.85), 0.36, 0.55, cor); filho(raiz, corpo); corpo.location = (0, 0, 0.85)
    short = cilindro(_id("short"), (0, 0, 0), 0.38, 0.3, (0.12, 0.12, 0.16, 1), seg=16); filho(raiz, short); short.location = (0, 0, 0.42)
    for x in (-0.15, 0.15):
        pe = esfera(_id("chut"), (0, 0, 0), 0.13, BRANCO, sub=2); pe.scale = (1, 1.5, 0.6); filho(raiz, pe); pe.location = (x, -0.06, 0.08)
        pr = cilindro(_id("perJ"), (0, 0, 0), 0.09, 0.3, PELE, seg=8); filho(raiz, pr); pr.location = (x, 0, 0.25)
    cab = esfera(_id("cabJ"), (0, 0, 0), 0.34, PELE, sub=3); filho(raiz, cab); cab.location = (0, 0, 1.62); liso(cab)
    for x in (-0.12, 0.12):
        o = esfera(_id("olhoJ"), (0, 0, 0), 0.05, PRETO, sub=2); filho(raiz, o); o.location = (x, -0.31, 1.67)
    cb = esfera(_id("cabeloJ"), (0, 0, 0), 0.35, cabelo or random.choice([CABELO, (0.45, 0.28, 0.12, 1), (0.9, 0.75, 0.35, 1)]), sub=3)
    cb.scale = (1, 1, 0.5); filho(raiz, cb); cb.location = (0, 0.04, 1.8); liso(cb)
    return raiz

def bola(nome, loc, r=0.22):
    """Bola genérica: esfera branca com gomos coloridos inventados (não é a bola oficial de nenhum torneio)."""
    b = esfera(nome, loc, r, BRANCO, sub=3); liso(b)
    for k, (dx, dy, dz) in enumerate([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]):
        g = esfera(_id("gomo"), (0, 0, 0), r * 0.42, (0.15, 0.45, 0.95, 1) if k % 2 else (1.0, 0.55, 0.10, 1), sub=2)
        g.scale = (1 if dx == 0 else 0.35, 1 if dy == 0 else 0.35, 1 if dz == 0 else 0.35)
        filho(b, g); g.location = (dx * r * 0.9, dy * r * 0.9, dz * r * 0.9); liso(g)
    return b

def campo(nome, x, larg=24, prof=16, fundo=(0.20, 0.24, 0.42, 1)):
    """Gramado listrado + linha de fundo + arquibancada em degraus com 'torcida' de blocos coloridos (cena fechada)."""
    for k in range(8):
        caixa(_id(nome + "faixa"), (x, -6 + k * 2.0, -0.1), (larg, 2.0, 0.2), GRAMA1 if k % 2 == 0 else GRAMA2,
              unico="g1" if k % 2 == 0 else "g2")
    for k in range(4):
        caixa(_id(nome + "degrau"), (x, prof * 0.32 + 0.9 + k * 0.9, 0.6 + k * 0.9), (larg, 0.9, 1.2 + k * 1.8), fundo)
    cores = [(0.95, 0.35, 0.30, 1), (1.0, 0.80, 0.25, 1), (0.35, 0.65, 1.0, 1), (0.95, 0.95, 0.95, 1), (0.55, 0.85, 0.45, 1)]
    for k in range(4):
        for j in range(10):
            caixa(_id(nome + "torc"), (x - larg / 2 + 1.2 + j * (larg - 2.4) / 9 + random.uniform(-0.3, 0.3), prof * 0.32 + 0.75 + k * 0.9,
                  1.35 + k * 1.8), (0.9, 0.4, 0.5), cores[(j + k) % 5], unico=f"torc{(j + k) % 5}")
    caixa(_id(nome + "linha"), (x, prof * 0.32 - 0.3, 0.01), (larg, 0.1, 0.02), BRANCO)
    topo_estadio(nome, x, prof * 0.32 + 4.6, larg, fundo)

def topo_estadio(nome, x, y, larg, fundo):
    """Anti-'borda' (Facebook, 26/11): fecha o topo do quadro — anel superior da arquibancada, cobertura com treliça e
    refletores, para não sobrar uma faixa de céu de cor única no alto da tela."""
    sup = tuple(min(1, c * 1.25) for c in fundo[:3]) + (1,)
    caixa(_id(nome + "anelSup"), (x, y + 0.6, 8.6), (larg + 6, 1.2, 5.4), sup)
    cores = [(0.95, 0.35, 0.30, 1), (1.0, 0.80, 0.25, 1), (0.35, 0.65, 1.0, 1), (0.95, 0.95, 0.95, 1), (0.55, 0.85, 0.45, 1)]
    for k in range(3):
        for j in range(12):
            caixa(_id(nome + "torcS"), (x - larg / 2 - 2 + j * (larg + 4) / 11 + random.uniform(-0.3, 0.3), y - 0.05, 6.9 + k * 1.5),
                  (0.9, 0.3, 0.45), cores[(j + 2 * k) % 5], unico=f"torc{(j + 2 * k) % 5}")
    caixa(_id(nome + "cobert"), (x, y - 2.5, 12.2), (larg + 8, 8.0, 0.6), (0.82, 0.84, 0.88, 1))
    for k in range(9):
        caixa(_id(nome + "trelica"), (x - larg / 2 - 3 + k * (larg + 6) / 8, y - 2.5, 11.6), (0.25, 8.0, 0.5), (0.45, 0.47, 0.52, 1))
    for k in range(6):
        rx = x - larg / 2 + 1.5 + k * (larg - 3) / 5
        caixa(_id(nome + "refl"), (rx, y - 5.6, 11.2), (1.6, 0.4, 0.8), (0.25, 0.27, 0.32, 1))
        for j in range(3):
            l = esfera(_id(nome + "lamp"), (rx - 0.5 + j * 0.5, y - 5.85, 11.2), 0.17, (1.0, 0.97, 0.85, 1), sub=2, unico="lampada")
    BRILHO.append(mat((1.0, 0.97, 0.85, 1), "lampada"))

def gol(nome, loc):
    x, y = loc
    for dx in (-1.6, 1.6):
        cilindro(_id("trave"), (x + dx, y, 1.0), 0.07, 2.0, BRANCO, seg=10)
    tr = cilindro(_id("traveS"), (x, y, 2.0), 0.07, 3.27, BRANCO, seg=10); tr.rotation_euler = (0, math.radians(90), 0)
    for k in range(7):   # rede: barras finas cinza claro
        caixa(_id("rede"), (x - 1.5 + k * 0.5, y + 0.9, 1.0), (0.025, 0.025, 2.0), (0.85, 0.87, 0.9, 1))
    for k in range(4):
        caixa(_id("redeH"), (x, y + 0.9, 0.2 + k * 0.6), (3.2, 0.025, 0.025), (0.85, 0.87, 0.9, 1))

def camera_tv(nome, loc, rz=0, s=1.0):
    """Câmera de rastreamento genérica (corpo + lente + luz)."""
    c = caixa(nome, loc, (0.5 * s, 0.75 * s, 0.4 * s), (0.16, 0.17, 0.22, 1)); c.rotation_euler = (math.radians(-25), 0, math.radians(rz))
    l = cilindro(_id("lenteC"), (0, 0, 0), 0.15 * s, 0.2 * s, (0.25, 0.65, 1.0, 1), seg=12, unico="lenteC"); filho(c, l)
    l.rotation_euler = (math.radians(90), 0, 0); l.location = (0, -0.42 * s, 0)
    r = esfera(_id("ledC"), (0, 0, 0), 0.06 * s, VERMELHO, sub=1, unico="ledC"); filho(c, r); r.location = (0.16 * s, -0.2 * s, 0.22 * s)
    return c

def xis(nome, loc, s=0.6, cor=VERMELHO):
    a = caixa(nome, loc, (s, 0.12, s * 0.22), cor); a.rotation_euler = (0, math.radians(45), 0)
    b = caixa(_id("xb"), (0, 0, 0), (s, 0.12, s * 0.22), cor); filho(a, b); b.rotation_euler = (0, math.radians(-90), 0)
    return a

def exclama(nome, loc, s=1.0, cor=VERMELHO):
    e = caixa(nome, loc, (0.22 * s, 0.22 * s, 0.8 * s), cor); liso(e)
    p = esfera(_id("pto"), (0, 0, 0), 0.14 * s, cor, sub=2); filho(e, p); p.location = (0, 0, -0.65 * s)
    return e

def meia_esfera(nome, loc, r, cor, cima=True):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=r)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if (v.co.z < -1e-4 if cima else v.co.z > 1e-4)], context="VERTS")
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(nome, me); bpy.context.collection.objects.link(ob); ob.location = loc
    ob.data.materials.append(mat(cor)); liso(ob)
    tampa = cilindro(_id("tampa"), (0, 0, 0), r * 0.99, 0.04, (0.92, 0.92, 0.94, 1), seg=24); filho(ob, tampa)
    tampa.location = (0, 0, 0.02 if cima else -0.02); return ob

def cronometro(nome, loc, r=0.9):
    c = cilindro(nome, loc, r, 0.15, BRANCO, seg=28); c.rotation_euler = (math.radians(90), 0, 0)
    a = anel(_id("aroCr"), (0, 0, 0), r + 0.02, 0.08, VERMELHO, seg=28); filho(c, a)
    bt = cilindro(_id("botao"), (0, 0, 0), 0.14, 0.25, VERMELHO, seg=10); filho(c, bt); bt.location = (0, r + 0.15, 0); bt.rotation_euler = (math.radians(90), 0, 0)
    pv = vazio(_id("ponteiroCr"), (0, 0, 0)); filho(c, pv); pv.location = (0, 0, 0.1)   # local +Z = para a câmera
    pp = caixa(_id("pontB"), (0, 0, 0), (0.07, r * 0.8, 0.05), ESCURO); filho(pv, pp); pp.location = (0, r * 0.35, 0)
    return c, pv

def parede_alta(nome, x, prof, cor, larg=22):
    """Anti-'borda': prolonga a parede do fundo até o alto do quadro e põe painéis de luz e faixa clara (sem céu liso)."""
    caixa(nome + "ParedeAlta", (x, prof + 0.05, 10.5), (larg, 0.4, 7.0), tuple(c * 0.85 for c in cor[:3]) + (1,))
    caixa(nome + "Friso", (x, prof - 0.2, 7.05), (larg, 0.15, 0.25), (0.95, 0.75, 0.25, 1))
    for k in range(7):
        pl = caixa(_id(nome + "painel"), (x - 9 + k * 3, prof - 0.2, 9.6 + (k % 2) * 1.6), (1.8, 0.08, 0.9), (0.70, 0.88, 1.0, 1), unico="painelLuz")
    BRILHO.append(mat((0.70, 0.88, 1.0, 1), "painelLuz"))

cam, alvo, cam_key, plano = camera_cartoon(24)

# =====================================================================
# ZONA A (x = 0) — gol anulado: bola entra, X vermelho, ombro do atacante brilha (bloco 0 e CTA)
# =====================================================================
t0, t1 = S[0]
campo("A", 0)
gol("golA", (1.2, 3.2))
px = pixel("pixel", (-1.9, 0.6, 0), escala=0.9); girarZ(px["raiz"], 12); respirar(px, 0, FIM)
atk = jogador("atacanteA", (0.9, 1.4, 0), TIME_A, 0.95); girarZ(atk, -10)
dfA = jogador("defensorA", (2.6, 2.2, 0), TIME_D, 0.95); girarZ(dfA, -25)
tgo = T(0, "Gol"); tan = T(0, "anulado"); tom = T(0, "ombro"); tqu = T(0, "Quem"); tol = T(0, "olho"); tju = T(0, "juiz")
tco = T(0, "Como"); tim = T(0, "impedimento")
bA = bola("bolaA", (0.4, 0.2, 0.22))
caminho(bA, 0.0, 0.7, lambda u: bez((0.4, 0.2, 0.22), (1.0, 1.8, 1.4), (1.4, 3.8, 0.9), u), orientar=False)
key(bA, "location", 3.0, (1.4, 3.8, 0.9)); key(bA, "location", 3.4, (1.4, 3.9, 0.22))
xA = xis("xA", (1.2, 2.6, 3.0), 1.4); visivel(xA, tan + 0.1, tqu); pop(xA, tan + 0.1, 1.0)
omb = esfera("ombroBrilho", (0.9 + 0.33, 1.4, 1.2), 0.2, AMARELO, sub=3); liso(omb); brilha(omb)
filho(atk, omb); omb.location = (0.38, 0, 1.15)
visivel(omb, tom - 0.1, t1 + 0.1); pop(omb, tom - 0.1, 1.0)
anO = anel("anelOmbro", (0, 0, 0), 0.35, 0.04, AMARELO, seg=24); filho(atk, anO); anO.location = (0.38, -0.05, 1.15); anO.rotation_euler = (math.radians(90), 0, 0)
visivel(anO, tom, t1 + 0.1); pop(anO, tom, 1.3, 0.5)
# o 'olho' grande do juiz: aparece e fica pequeno diante da pergunta
olho = esfera("olhoJuiz", (-0.6, 1.8, 3.4), 0.55, BRANCO, sub=3); liso(olho)
pup = esfera("pupila", (0, 0, 0), 0.25, PRETO, sub=3); filho(olho, pup); pup.location = (0.05, -0.42, 0); pup.scale = (1, 0.5, 1)
visivel(olho, tol - 0.1, tco + 0.1); pop(olho, tol - 0.1, 1.0)
key(pup, "location", tol + 0.3, (0.05, -0.42, 0)); key(pup, "location", tju + 0.3, (0.25, -0.38, 0.05)); key(pup, "location", tco - 0.1, (-0.2, -0.4, -0.05))
espanto(px, tan - 0.1, 1.2); apontar(px, tom - 0.1, 1.4, "D", 50); pensar(px, tol - 0.1, 1.0); pensar(px, tco - 0.1, 1.8)
plano(0, (0.3, 1.2), "geral", altura=1.9); plano(tom - 0.4, (0.3, 1.2), "geral", altura=1.9)
plano(tom - 0.05, (0.6, 1.2), "medio", altura=1.8); plano(tol - 0.4, (0.6, 1.2), "medio", altura=1.8)
plano(tol - 0.05, (-0.6, 1.0), "medio", altura=2.3); plano(tco - 0.4, (-0.6, 1.0), "medio", altura=2.3)
plano(tco - 0.05, (-1.6, 0.6), "close", altura=2.1); plano(t1 - 0.05, (-1.6, 0.6), "close", altura=2.2)

# =====================================================================
# ZONA B (x = 40) — 12 câmeras sob o teto do estádio filmando os jogadores (bloco 1)
# =====================================================================
t0, t1 = S[1]
campo("B", 40)
tpr = T(1, "Primeiro"); tcam = T(1, "câmeras"); tcopa = T(1, "Copa"); tdo = T(1, "doze"); tte = T(1, "teto")
tfi = T(1, "filmando"); tci = T(1, "cinquenta"); tseg = T(1, "segundo", 1)
teto = caixa("tetoB", (40, 3.2, 7.4), (26, 4.0, 0.5), (0.85, 0.86, 0.90, 1))
for k in range(7):
    caixa(_id("vigaB"), (28.5 + k * 3.8, 3.2, 6.9), (0.3, 4.0, 0.5), (0.55, 0.57, 0.62, 1))
CAMS = []
for k in range(12):
    cx = 33.2 + k * 1.25; cy = 1.6 + (k % 2) * 0.6
    c = camera_tv(_id("camB"), (cx, cy, 6.55), rz=0, s=1.0)
    visivel(c, tdo - 0.25 + 0.06 * k); pop(c, tdo - 0.25 + 0.06 * k, 1.0); CAMS.append(c)
JB = []
for k, (jx, jy, cor) in enumerate([(37.0, 1.8, TIME_A), (39.0, 0.8, TIME_D), (40.6, 2.4, TIME_A), (42.0, 1.2, TIME_D), (43.6, 2.6, TIME_A), (38.4, 3.0, TIME_D)]):
    j = jogador(_id("jB"), (jx, jy, 0), cor, 0.75); JB.append(j)
    caminho(j, t0, t1 + 0.3, lambda u, jx=jx, jy=jy, k=k: (jx + 0.7 * math.sin(u * 5 + k), jy + 0.5 * math.cos(u * 4 + k * 2), 0))
bB = bola("bolaB", (40.2, 1.6, 0.17), 0.17)
caminho(bB, t0, t1 + 0.3, lambda u: (40.2 + 2.0 * math.sin(u * 4), 1.6 + 0.8 * math.sin(u * 6), 0.17), orientar=False)
# feixes: cada câmera 'mira' um jogador (cabo emissivo) a partir de 'filmando'
for k, c in enumerate(CAMS):
    j = JB[k % len(JB)]
    a = (c.location.x, c.location.y - 0.3, c.location.z - 0.25)
    bx = cabo(_id("feixe"), a, (j.location.x, j.location.y, 1.6), 0.025, CIANO, unico="feixe")
    visivel(bx, tfi - 0.1 + 0.04 * k, t1 + 0.1)
BRILHO.append(mat(CIANO, "feixe"))
# 'cinquenta vezes por segundo': as luzes piscam
lm = mat(VERMELHO, "ledC")
t = tci - 0.1; k = 0
while t < t1:
    cor_key(lm, t, VERMELHO if k % 2 else (1.0, 0.9, 0.9, 1)); t += 0.12; k += 1
BRILHO.append(lm)
gB = pixel("guiaB", (36.4, -1.6, 0), escala=0.8); girarZ(gB["raiz"], 15); respirar(gB, t0, t1 + 0.5)
acenar(gB, tpr - 0.1, 1.0); apontar(gB, tdo - 0.2, 1.8, "D", 120); comemorar(gB, tci - 0.1, 1.2)
cam_key(t0, (39.0, -7.2, 2.4), (40.0, 1.6, 2.6)); cam_key(tdo - 0.6, (39.6, -7.6, 2.6), (40.0, 1.6, 3.4))
cam_key(tdo - 0.1, (40.0, -8.4, 3.0), (40.0, 1.6, 4.2)); cam_key(tfi - 0.3, (40.0, -8.4, 3.0), (40.0, 1.6, 4.2))
cam_key(tfi + 0.1, (40.4, -8.6, 3.4), (40.2, 1.6, 3.6)); cam_key(t1 - 0.05, (40.8, -8.6, 3.4), (40.2, 1.6, 3.6))

# =====================================================================
# ZONA C (x = 80) — o 'esqueleto' do atacante: pontos do corpo; os braços apagam (não contam) (bloco 2)
# =====================================================================
t0, t1 = S[2]
campo("C", 80, fundo=(0.30, 0.20, 0.45, 1))
tse = T(2, "Se"); tat = T(2, "atacante"); tes = T(2, "esqueleto"); tvi = T(2, "vinte"); tpo = T(2, "pontos")
tcab = T(2, "cabeça"); tpe = T(2, "pé"); tbr = T(2, "braço"); tnc = T(2, "conta"); tgl = T(2, "gol")
atC = jogador("atacanteC", (81.2, 1.0, 0), TIME_A, 1.6); girarZ(atC, -15)
visivel(atC, t0, tes + 0.4); pop(atC, tat - 0.1, 1.6); sumir(atC, tes + 0.05, 0.3)
# pontos (x, z) de um atacante em corrida, escala ~1.6
OX, OY = 81.2, 1.0
PT = {"cab": (0, 3.05), "pesc": (0, 2.55), "ombE": (-0.55, 2.45), "ombD": (0.55, 2.45), "cotE": (-0.95, 1.95), "cotD": (0.85, 2.0),
      "maoE": (-1.15, 1.45), "maoD": (1.1, 1.55), "peito": (0, 2.1), "quad": (0, 1.45), "quaE": (-0.3, 1.4), "quaD": (0.3, 1.4),
      "joeE": (-0.55, 0.8), "joeD": (0.45, 0.85), "torE": (-0.6, 0.2), "torD": (0.75, 0.35), "peE": (-0.85, 0.08), "peD": (1.05, 0.3)}
LIG = [("cab", "pesc"), ("pesc", "ombE"), ("pesc", "ombD"), ("ombE", "cotE"), ("cotE", "maoE"), ("ombD", "cotD"), ("cotD", "maoD"),
       ("pesc", "peito"), ("peito", "quad"), ("quad", "quaE"), ("quad", "quaD"), ("quaE", "joeE"), ("joeE", "torE"), ("torE", "peE"),
       ("quaD", "joeD"), ("joeD", "torD"), ("torD", "peD")]
BRACO = {"cotE", "cotD", "maoE", "maoD"}
ordem = ["cab", "pesc", "ombE", "ombD", "peito", "cotE", "cotD", "maoE", "maoD", "quad", "quaE", "quaD", "joeE", "joeD", "torE", "torD", "peE", "peD"]
PTS = {}
for k, n in enumerate(ordem):
    x, z = PT[n]; braco = n in BRACO
    p = esfera("pt_" + n, (OX + x, OY - 0.05, z), 0.17 if n != "cab" else 0.3, CIANO, sub=3, unico="ptBraco" if braco else "ptCorpo"); liso(p)
    tp = tes + 0.1 + k * 0.08 if n not in ("cab",) else tes + 0.1
    visivel(p, tp, t1 + 0.1); pop(p, tp, 1.0); PTS[n] = p
for a, b in LIG:
    braco = (a in BRACO or b in BRACO)
    xa, za = PT[a]; xb, zb = PT[b]
    c = cabo(_id("osso"), (OX + xa, OY, za), (OX + xb, OY, zb), 0.06, BRANCO, unico="ossoBraco" if braco else "ossoCorpo")
    visivel(c, tes + 0.5, t1 + 0.1)
m_pc = mat(CIANO, "ptCorpo"); m_pb = mat(CIANO, "ptBraco"); m_ob = mat(BRANCO, "ossoBraco")
BRILHO.extend([m_pc, m_pb])
for n, tt in (("cab", tcab), ("peE", tpe), ("peD", tpe)):
    p = PTS[n]; s0 = 1.0
    key(p, "scale", tt - 0.05, (s0,) * 3); key(p, "scale", tt + 0.15, (1.7,) * 3); key(p, "scale", tt + 0.45, (s0,) * 3)
cor_key(m_pb, tbr - 0.1, CIANO); cor_key(m_pb, tbr + 0.2, (0.35, 0.35, 0.40, 1))
cor_key(m_ob, tbr - 0.1, BRANCO); cor_key(m_ob, tbr + 0.2, (0.45, 0.45, 0.50, 1))
for nm, (x, z) in (("xBE", PT["cotE"]), ("xBD", PT["cotD"])):
    xx = xis(nm, (OX + x, OY - 0.4, z), 0.7); visivel(xx, tbr + 0.1, t1 + 0.1); pop(xx, tbr + 0.1, 1.0)
gC = pixel("guiaC", (78.2, -1.2, 0), escala=0.85); girarZ(gC["raiz"], 18); respirar(gC, t0, t1 + 0.5)
apontar(gC, tat - 0.2, 1.4, "D", 40); espanto(gC, tes - 0.1, 1.2); apontar(gC, tvi - 0.1, 2.0, "D", 70); pensar(gC, tbr - 0.2, 1.6); comemorar(gC, tgl - 0.3, 1.0)
plano(t0, (80.4, 0.8), "geral", altura=2.0); plano(tes - 0.4, (80.4, 0.8), "geral", altura=2.0)
plano(tes, (80.8, 0.8), "geral", altura=2.2); plano(tbr - 0.4, (80.8, 0.8), "geral", altura=2.2)
plano(tbr - 0.1, (80.9, 0.8), "medio", altura=2.2); plano(t1 - 0.05, (80.9, 0.8), "medio", altura=2.3)

# =====================================================================
# ZONA D (x = 120) — a bola se abre: chip no centro manda pulsos 500x/s e marca o instante do passe (bloco 3)
# =====================================================================
t0, t1 = S[3]
sala_fechada("D", 120, (0.30, 0.62, 0.35, 1), (0.16, 0.22, 0.40, 1), prof=4.6)
parede_alta("D", 120, 4.6, (0.16, 0.22, 0.40, 1))
tchip = T(3, "chip"); tden = T(3, "Dentro"); tsen = T(3, "sensor"); tqui = T(3, "quinhentas"); tins = T(3, "instante"); tpas = T(3, "passe")
BX, BY, BZ, BR = 120.8, 1.2, 2.2, 1.25
base = cilindro("pedestalD", (BX, BY, 0.45), 0.7, 0.9, (0.85, 0.86, 0.90, 1), seg=20)
cimaD = meia_esfera("bolaCima", (BX, BY, BZ), BR, BRANCO, True); baixoD = meia_esfera("bolaBaixo", (BX, BY, BZ), BR, BRANCO, False)
for k, ang in enumerate((0, 72, 144, 216, 288)):
    for metade, zz in ((cimaD, 0.55), (baixoD, -0.55)):
        g = esfera(_id("gomoD"), (0, 0, 0), 0.42, (0.15, 0.45, 0.95, 1) if k % 2 else (1.0, 0.55, 0.10, 1), sub=2)
        a = math.radians(ang + (36 if zz < 0 else 0)); r = BR * 0.84
        g.scale = (1, 1, 0.35); filho(metade, g); g.location = (math.cos(a) * r, math.sin(a) * r, zz * 1.3)
        g.rotation_euler = (0, math.radians(55 if zz > 0 else -55), a); liso(g)
key(cimaD, "location", tden - 0.15, (BX, BY, BZ)); key(cimaD, "location", tden + 0.45, (BX, BY, BZ + 1.7))
key(baixoD, "location", tden - 0.15, (BX, BY, BZ)); key(baixoD, "location", tden + 0.45, (BX, BY, BZ - 0.25))
chip = caixa("chip", (BX, BY - 0.1, BZ), (0.8, 0.8, 0.14), CHIPV); chip.rotation_euler = (math.radians(70), 0, 0)
nucleo = caixa("nucleoChip", (0, 0, 0), (0.4, 0.4, 0.06), (0.10, 0.10, 0.12, 1)); filho(chip, nucleo); nucleo.location = (0, 0, 0.09)
for k in range(4):
    for s_ in (-1, 1):
        pn = caixa(_id("pino"), (0, 0, 0), (0.06, 0.16, 0.04), OURO); filho(chip, pn); pn.location = (-0.27 + k * 0.18, s_ * 0.46, 0)
led = esfera("ledChip", (0, 0, 0), 0.07, VERDE, sub=2); filho(chip, led); led.location = (0.28, 0.28, 0.1); brilha(led)
visivel(chip, tden + 0.15); pop(chip, tden + 0.15, 1.0)
for k in range(8):   # pulsos 'quinhentas vezes por segundo'
    tt = tqui - 0.1 + k * 0.32
    r_ = anel(_id("pulso"), (BX, BY - 0.2, BZ), 0.6, 0.05, VERDE, seg=32, unico="pulso"); r_.rotation_euler = (math.radians(90), 0, 0)
    visivel(r_, tt, tt + 0.6); key(r_, "scale", tt, (0.5,) * 3); key(r_, "scale", tt + 0.6, (3.0,) * 3)
BRILHO.append(mat(VERDE, "pulso"))
crD, pvD = cronometro("cronD", (123.6, 2.6, 3.9), 0.6)
visivel(crD, tins - 0.2); pop(crD, tins - 0.2, 1.0)
key(pvD, "rotation_euler", tins, (0, 0, 0)); key(pvD, "rotation_euler", tpas + 0.1, (0, 0, math.radians(-300)))
key(crD, "scale", tpas - 0.05, (1, 1, 1)); key(crD, "scale", tpas + 0.15, (1.35, 1.35, 1.35)); key(crD, "scale", tpas + 0.45, (1, 1, 1))
gD = pixel("guiaD", (118.7, -0.9, 0), escala=0.85); girarZ(gD["raiz"], 20); respirar(gD, t0, t1 + 0.5)
pensar(gD, tchip - 0.2, 1.0); espanto(gD, tden + 0.1, 1.2); apontar(gD, tqui - 0.1, 1.6, "D", 40); apontar(gD, tins - 0.1, 1.6, "D", 90)
plano(t0, (120.0, 0.8), "geral", altura=2.2); plano(tden - 0.3, (120.0, 0.8), "geral", altura=2.2)
plano(tden + 0.05, (120.6, 1.0), "medio", altura=2.4); plano(tins - 0.4, (120.6, 1.0), "medio", altura=2.4)
plano(tins - 0.05, (121.4, 1.2), "geral", altura=2.7); plano(t1 - 0.05, (121.4, 1.2), "geral", altura=2.7)

# =====================================================================
# ZONA E (x = 160) — passe congelado: linha 3D no último defensor e no atacante; atacante passou -> alerta (bloco 4)
# =====================================================================
t0, t1 = S[4]
campo("E", 160)
gol("golE", (160.0, 5.6))
tpu = T(4, "pulo"); tpa = T(4, "passe"); tcg = T(4, "congelado"); tcmp = T(4, "computador"); tli = T(4, "linha")
tde = T(4, "defensor"); tou = T(4, "outra"); tatk = T(4, "atacante"); tps = T(4, "passou"); tdi = T(4, "dispara"); tal = T(4, "alerta")
pas = jogador("passador", (157.0, -1.6, 0), TIME_A, 0.9); girarZ(pas, 160)
DEF = []
for k, (dx, dy) in enumerate([(-2.6, 2.3), (-0.6, 2.0), (1.6, 2.3), (3.0, 1.6)]):
    d = jogador(_id("defE"), (160 + dx, dy, 0), TIME_D, 0.9); girarZ(d, 180); DEF.append(d)
ATK = jogador("atacanteE", (160.8, 2.75, 0), TIME_A, 0.9); girarZ(ATK, 170)
# todo mundo corre um pouquinho e para no 'congelado'
for ob in DEF + [ATK, pas]:
    x0, y0 = ob.location.x, ob.location.y
    key(ob, "location", t0, (x0, y0 - 0.9, 0)); key(ob, "location", tcg, (x0, y0, 0))
bE = bola("bolaE", (157.3, -1.1, 0.2), 0.2)
key(bE, "location", t0, (157.3, -1.1, 0.2)); key(bE, "location", tpa, (157.3, -1.1, 0.2)); key(bE, "location", tcg, (157.9, -0.4, 0.2))
pausa = vazio("pausa", (160.0, 1.0, 3.8))
for dx in (-0.25, 0.25):
    pb_ = caixa(_id("barraPausa"), (0, 0, 0), (0.28, 0.1, 1.0), (0.35, 0.75, 1.0, 1), unico="pausa"); filho(pausa, pb_); pb_.location = (dx, 0, 0); liso(pb_)
visivel(pausa, tcg, tcmp + 0.4); pop(pausa, tcg, 1.0); BRILHO.append(mat((0.35, 0.75, 1.0, 1), "pausa"))
def linha3d(nome, y, cor, t):
    ln = caixa(nome, (160.0, y, 0.03), (14.0, 0.08, 0.04), cor, unico=nome); brilha(ln)
    visivel(ln, t); ln.scale = (0.001, 1, 1); ln.keyframe_insert("scale", frame=f(t)); ln.scale = (1, 1, 1); ln.keyframe_insert("scale", frame=f(t + 0.5))
    for k in range(8):   # 'cortina' de hastes: mostra que a linha é um plano 3D
        h = caixa(_id(nome + "h"), (153.4 + k * 1.9, y, 1.0), (0.04, 0.04, 2.0), cor, unico=nome)
        visivel(h, t + 0.3 + 0.04 * k); pop(h, t + 0.3 + 0.04 * k, 1.0)
    return ln
linha3d("linhaDef", 2.3 + 0.18, AMARELO, tde - 0.2)
linha3d("linhaAtk", 2.75 + 0.18, VERMELHO, tatk - 0.2)
bv = esfera("pontoAtk", (0, 0, 0), 0.16, VERMELHO, sub=3); filho(ATK, bv); bv.location = (0.0, -0.2, 1.1); visivel(bv, tatk - 0.1); pop(bv, tatk - 0.1, 1.0); brilha(bv)
ex = exclama("alertaE", (160.8, 2.9, 4.3), 1.3); visivel(ex, tal - 0.15); pop(ex, tal - 0.15, 1.0)
sir = esfera("sirene", (159.2, 2.9, 3.9), 0.35, VERMELHO, sub=3, unico="sirene"); liso(sir); visivel(sir, tal - 0.1); pop(sir, tal - 0.1, 1.0)
ms = mat(VERMELHO, "sirene"); BRILHO.append(ms)
t = tal; k = 0
while t < t1 + 0.2:
    cor_key(ms, t, VERMELHO if k % 2 else (1.0, 0.85, 0.3, 1)); t += 0.18; k += 1
gE = pixel("guiaE", (156.6, -2.6, 0), escala=0.8); girarZ(gE["raiz"], 25); respirar(gE, t0, t1 + 0.5)
comemorar(gE, tpu - 0.1, 1.0); apontar(gE, tli - 0.1, 1.5, "D", 30); apontar(gE, tatk - 0.2, 1.4, "D", 45); espanto(gE, tal - 0.1, 1.4)
cam_key(t0, (159.0, -8.4, 3.2), (159.6, 1.2, 1.4)); cam_key(tcg - 0.2, (159.2, -8.2, 3.4), (159.6, 1.2, 1.4))
cam_key(tcg + 0.2, (159.8, -4.6, 4.3), (160.2, 2.4, 0.9)); cam_key(tps - 0.3, (160.0, -4.3, 4.1), (160.3, 2.5, 0.9))
cam_key(tps + 0.05, (162.2, -3.2, 2.4), (160.6, 2.6, 1.4)); cam_key(t1 - 0.05, (162.4, -3.4, 2.6), (160.6, 2.6, 1.6))

# =====================================================================
# ZONA F (x = 200) — não é robô: sala do VAR, árbitro de vídeo confere, avisa o juiz em campo, telão com a animação (bloco 5)
# =====================================================================
t0, t1 = S[5]
sala_fechada("F", 200, (0.42, 0.44, 0.56, 1), (0.22, 0.24, 0.36, 1), prof=4.8)
parede_alta("F", 200, 4.8, (0.22, 0.24, 0.36, 1))
trb = T(5, "robô"); tap = T(5, "apita"); tarb = T(5, "árbitro"); tcf = T(5, "confere"); tav = T(5, "avisa"); tjz = T(5, "juiz")
ttor = T(5, "torcida"); tani = T(5, "animação"); ttl = T(5, "telão")
caixa("mesaF", (198.6, 1.6, 1.0), (3.6, 1.2, 0.12), (0.30, 0.22, 0.18, 1))
caixa("peMesaF", (198.6, 1.6, 0.5), (3.2, 0.9, 0.9), (0.18, 0.18, 0.22, 1))
TELAS = []
for k, dx in enumerate((-1.2, 0.0, 1.2)):
    mn = caixa(_id("monF"), (198.6 + dx, 2.0, 1.7), (1.1, 0.08, 0.7), PRETO)
    tl = caixa(_id("telaF"), (0, 0, 0), (1.0, 0.02, 0.6), (0.25, 0.70, 0.35, 1), unico="telaF"); filho(mn, tl); tl.location = (0, -0.06, 0)
    ln = caixa(_id("linTela"), (0, 0, 0), (0.03, 0.02, 0.55), AMARELO); filho(mn, ln); ln.location = (-0.1 + 0.1 * k, -0.08, 0)
    TELAS.append(mn)
mt = mat((0.25, 0.70, 0.35, 1), "telaF"); BRILHO.append(mt)
arb = jogador("arbitroVideo", (200.7, 1.3, 0), (0.15, 0.15, 0.18, 1), 1.0); girarZ(arb, 35)
fone = anel("foneArb", (0, 0, 0), 0.36, 0.05, FONE, seg=24); filho(arb, fone); fone.location = (0, 0, 1.68); fone.rotation_euler = (0, math.radians(90), 0)
rob = vazio("robo", (196.0, 0.6, 0))
for nm, loc, dim, cor in (("rbCorpo", (0, 0, 1.0), (0.9, 0.6, 1.0), CINZA), ("rbCab", (0, 0, 1.85), (0.7, 0.55, 0.55), (0.55, 0.57, 0.62, 1)),
                          ("rbOlhoE", (-0.15, -0.29, 1.9), (0.14, 0.04, 0.1), CIANO), ("rbOlhoD", (0.15, -0.29, 1.9), (0.14, 0.04, 0.1), CIANO),
                          ("rbPerna", (0, 0, 0.25), (0.6, 0.4, 0.5), ESCURO)):
    o = caixa(_id(nm), (0, 0, 0), dim, cor); filho(rob, o); o.location = loc
ap = cilindro(_id("apito"), (0, 0, 0), 0.12, 0.3, OURO, seg=10); filho(rob, ap); ap.location = (0.3, -0.35, 1.6); ap.rotation_euler = (math.radians(90), 0, 0)
visivel(rob, trb - 0.15, tarb); pop(rob, trb - 0.15, 1.0); sumir(rob, tarb - 0.35, 0.3)
xR = xis("xRobo", (196.0, 0.1, 1.3), 1.3); visivel(xR, tap, tarb); pop(xR, tap, 1.0)
# confere: telas piscam
t = tcf - 0.1; k = 0
while t < tav:
    cor_key(mt, t, (0.25, 0.70, 0.35, 1) if k % 2 else (0.75, 1.0, 0.8, 1)); t += 0.2; k += 1
# avisa o juiz em campo: ondas de rádio até o juiz (à direita, num pedaço de gramado)
caixa("gramaF", (203.4, 1.0, 0.02), (3.0, 3.0, 0.06), GRAMA1)
jz = jogador("juizCampo", (203.4, 1.0, 0), (0.15, 0.15, 0.18, 1), 1.0); girarZ(jz, -30)
apJ = cilindro(_id("apitoJ"), (0, 0, 0), 0.08, 0.2, OURO, seg=10); filho(jz, apJ); apJ.location = (0.25, -0.3, 1.5); apJ.rotation_euler = (math.radians(90), 0, 0)
for k in range(5):
    tt = tav - 0.1 + k * 0.22
    w = anel(_id("onda"), (0, 0, 0), 0.3, 0.04, AMARELO, seg=20, unico="onda"); w.rotation_euler = (0, math.radians(90), 0)
    visivel(w, tt, tt + 0.8)
    caminho(w, tt, tt + 0.8, lambda u: lerp((199.4, 2.4, 2.2), (203.2, 1.0, 2.0), u), orientar=False)
    key(w, "scale", tt, (0.6,) * 3); key(w, "scale", tt + 0.8, (1.6,) * 3)
BRILHO.append(mat(AMARELO, "onda"))
# telão na parede com a animação 3D (figurinhas + linha)
tela = caixa("telao", (199.6, 4.5, 4.6), (6.2, 0.2, 3.0), PRETO)
fundoT = caixa("fundoTelao", (199.6, 4.36, 4.6), (5.8, 0.04, 2.6), (0.20, 0.55, 0.28, 1), unico="fundoT"); BRILHO.append(mat((0.20, 0.55, 0.28, 1), "fundoT"))
ANI = []
for dx, cor in ((-1.6, TIME_D), (-0.2, TIME_A), (1.2, TIME_D)):
    fg = jogador(_id("figT"), (199.6 + dx, 4.2, 3.4), cor, 0.55); ANI.append(fg)
lt = caixa("linhaTelao", (199.6 + 0.55, 4.2, 4.5), (0.08, 0.06, 2.4), AMARELO, unico="linhaT"); ANI.append(lt); BRILHO.append(mat(AMARELO, "linhaT"))
for k, ob in enumerate(ANI):
    visivel(ob, tani - 0.1 + 0.08 * k); pop(ob, tani - 0.1 + 0.08 * k, 0.55 if k < 3 else 1.0)
for k in range(10):   # torcida olhando o telão (de costas)
    tc = jogador(_id("torcF"), (196.0 + k * 0.85, 3.4 + (k % 2) * 0.3, 0), random.choice([AMARELO, AZUL, VERMELHO, BRANCO]), 0.5); girarZ(tc, 180)
    visivel(tc, ttor - 0.2); pop(tc, ttor - 0.2 + 0.04 * k, 0.5)
gF = pixel("guiaF", (201.9, -1.2, 0), escala=0.8); girarZ(gF["raiz"], -20); respirar(gF, t0, t1 + 0.5)
pensar(gF, trb - 0.1, 1.0); apontar(gF, tarb - 0.1, 1.4, "E", 40); apontar(gF, tav - 0.1, 1.2, "D", 30); comemorar(gF, ttl - 0.2, 1.2)
plano(t0, (198.6, 1.0), "geral", altura=2.0); plano(tcf + 0.3, (198.6, 1.0), "geral", altura=2.0)
plano(tav - 0.1, (200.8, 1.0), "geral", altura=2.0); plano(ttor - 0.5, (200.8, 1.0), "geral", altura=2.0)
cam_key(ttor - 0.1, (199.6, -5.0, 3.2), (199.6, 4.0, 3.9)); cam_key(t1 - 0.05, (199.6, -4.6, 3.3), (199.6, 4.0, 3.9))

# =====================================================================
# ZONA G (x = 240) — no Brasil: 28 a 32 câmeras em volta, bola SEM chip, imagens marcam o toque, cronômetro 47 s (bloco 6)
# =====================================================================
t0, t1 = S[6]
campo("G", 240, fundo=(0.95, 0.78, 0.15, 1))
tbra = T(6, "Brasil"); tcbf = T(6, "CBF"); tvin = T(6, "vinte"); tcm = T(6, "câmeras"); tch = T(6, "chip")
ttq = T(6, "toque"); tim2 = T(6, "imagens"); test = T(6, "estreia"); tqua = T(6, "quarenta"); tsg = T(6, "segundos"); tme = T(6, "média")
CG = []
for k in range(30):   # 28 a 32 câmeras: fileira em postes atrás do campo, em dois andares
    cx = 232.2 + (k // 2) * 1.11; cz = 2.4 + 1.5 * (k % 2); cy = 4.6
    if k % 2 == 0:
        cilindro(_id("poste"), (cx, cy + 0.1, 1.6), 0.05, 3.2, CINZA, seg=6)
    c = camera_tv(_id("camG"), (cx, cy, cz), rz=(cx - 240) * 3, s=0.75)
    tt = tvin - 0.1 + k * 0.045; visivel(c, tt); pop(c, tt, 1.0); CG.append(c)
bG = bola("bolaG", (240.0, 1.6, 0.6), 0.6)
atG = jogador("atacanteG", (238.9, 1.9, 0), TIME_A, 1.1); girarZ(atG, -20)
chG = caixa("chipG", (240.0, 1.3, 2.2), (0.6, 0.6, 0.1), CHIPV); chG.rotation_euler = (math.radians(70), 0, 0)
xG = xis("xChip", (240.0, 1.1, 2.2), 1.0)
for ob, d in ((chG, 0.0), (xG, 0.2)):
    visivel(ob, tch - 0.15 + d, ttq + 0.2); pop(ob, tch - 0.15 + d, 1.0)
for k in range(10):   # as imagens: feixes das câmeras até a bola
    c = CG[k * 3]
    fx = cabo(_id("feixeG"), (c.location.x, c.location.y - 0.2, c.location.z - 0.2), (240.0, 1.6, 0.7), 0.03, CIANO, unico="feixeG")
    visivel(fx, tim2 - 0.4 + 0.05 * k, test + 0.3)
BRILHO.append(mat(CIANO, "feixeG"))
flG = esfera("toqueG", (240.0, 1.4, 0.7), 0.3, AMARELO, sub=2, unico="toqueG"); visivel(flG, ttq, ttq + 0.6); key(flG, "scale", ttq, (0.5,) * 3); key(flG, "scale", ttq + 0.6, (2.6,) * 3)
BRILHO.append(mat(AMARELO, "toqueG"))
crG, pvG = cronometro("cronG", (242.6, 1.4, 3.0), 1.0)
visivel(crG, test - 0.1); pop(crG, test - 0.1, 1.0)
key(pvG, "rotation_euler", test + 0.2, (0, 0, 0)); key(pvG, "rotation_euler", tsg, (0, 0, math.radians(-282)))
gG = pixel("guiaG", (237.3, -0.8, 0), escala=0.85); girarZ(gG["raiz"], 18); respirar(gG, t0, t1 + 0.5)
acenar(gG, tbra - 0.2, 1.2); apontar(gG, tvin - 0.1, 1.6, "D", 100); espanto(gG, tch - 0.1, 1.2); apontar(gG, tim2 - 0.2, 1.2, "D", 60); comemorar(gG, tqua - 0.1, 1.4)
cam_key(t0, (239.2, -7.6, 2.6), (239.6, 1.6, 2.4)); cam_key(tvin - 0.5, (239.4, -7.6, 2.6), (239.6, 1.6, 2.4))
cam_key(tvin - 0.1, (240.0, -9.6, 3.6), (240.0, 1.8, 3.2)); cam_key(tch - 0.4, (240.0, -9.4, 3.6), (240.0, 1.8, 3.2))
cam_key(tch - 0.1, (239.6, -6.0, 2.4), (240.0, 1.4, 1.8)); cam_key(test - 0.4, (239.8, -6.2, 2.4), (240.0, 1.4, 1.8))
cam_key(test - 0.1, (240.8, -6.4, 2.6), (241.0, 1.4, 2.2)); cam_key(t1 - 0.05, (241.0, -6.6, 2.6), (241.0, 1.4, 2.2))

# =====================================================================
# 7 — convite: volta ao campo do gancho; linha 3D brilhando x bandeirinha com a bandeira; Pixel acena e pede o like
# =====================================================================
t0 = S[7][0]
tlin = T(7, "linha"); tban = T(7, "bandeirinha"); tc1 = T(7, "Comenta"); tc2 = T(7, "comenta", 1)
lA = caixa("linhaCTA", (0.5, 2.2, 0.03), (12, 0.08, 0.04), AMARELO, unico="linhaCTA"); brilha(lA)
visivel(lA, tlin - 0.1); lA.scale = (0.001, 1, 1); lA.keyframe_insert("scale", frame=f(tlin - 0.1)); lA.scale = (1, 1, 1); lA.keyframe_insert("scale", frame=f(tlin + 0.4))
band = jogador("bandeirinha", (2.9, 0.4, 0), (0.15, 0.15, 0.18, 1), 0.9); girarZ(band, -35)
mastro = cilindro(_id("mastro"), (0, 0, 0), 0.03, 1.4, BRANCO, seg=6); filho(band, mastro); mastro.location = (0.45, -0.1, 1.7)
pano = caixa(_id("pano"), (0, 0, 0), (0.5, 0.03, 0.36), (1.0, 0.85, 0.10, 1)); filho(band, pano); pano.location = (0.72, -0.1, 2.2)
visivel(band, tban - 0.2); pop(band, tban - 0.2, 0.9)
key(band, "rotation_euler", tban + 0.4, (0, 0, math.radians(-35))); key(band, "rotation_euler", tban + 0.8, (0, math.radians(-12), math.radians(-35)))
acenar(px, t0 + 0.15, 1.4); apontar(px, tc1 - 0.1, 1.2, "E", 30); apontar(px, tc2 - 0.1, 1.2, "D", 40)
acenar(px, LEG[-1]["e"] + 1.2, 1.6); comemorar(px, LEG[-1]["e"] + 3.0, 1.4)
cam_key(t0, (0.4, -7.6, 2.6), (0.4, 1.4, 2.0)); cam_key(FIM, (0.6, -7.0, 2.6), (0.6, 1.4, 2.0))

# ---------- corte seco entre zonas (backlog: levado para cartoon.corte_seco) ----------
corte_seco(cam, alvo)

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
