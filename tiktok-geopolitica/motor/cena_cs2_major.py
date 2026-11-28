"""Série 2 — 'Como funciona o Major de CS2? (sistema suíço)' (28/11; estilo C cartoon, mascote Pixel, visual nível 2).
Mecanismo: arena genérica de torneio (sem marca, sem logo de time/jogo, sem mapa de jogo). Times = fichas coloridas lisas.
Blocos: gancho (ficha perde e não cai) · placar 3 luzes verdes x 3 vermelhas (avança / volta pra casa) · tabuleiro suíço
(0-0 → 1-0 / 0-1, pares com a mesma campanha) · MD1 (1 mapa, zebra) x MD3 · Buchholz (soma da campanha dos adversários) ·
escada de fases (MIBR na 2, FURIA na 3, 2 DEZ — nomes só em texto) · mata-mata de 8 até a final MD5 · CTA PASSA x CAI.
Base: cena_gta6_mocap.py (zonas por bloco, corte seco). Backlog aplicado: objetos de cada bloco já nascem no corte da câmera
(nada de plano vazio no início do bloco — item do matchmaking).
Uso: blender -b --factory-startup -P cena_cs2_major.py -- <pasta> [preview t1,t2 | range a,b]"""
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
random.seed(2811)

AMARELO = (1.0, 0.82, 0.12, 1); VERDE = (0.20, 0.85, 0.40, 1); VERMELHO = (0.95, 0.22, 0.20, 1)
AZUL = (0.20, 0.55, 1.0, 1); BRANCO = (0.97, 0.97, 0.98, 1); CIANO = (0.25, 0.95, 1.0, 1)
ESCURO = (0.10, 0.11, 0.14, 1); CINZA = (0.40, 0.42, 0.48, 1); OURO = (1.0, 0.72, 0.10, 1)
ROXO = (0.55, 0.35, 0.95, 1); ROSA = (1.0, 0.45, 0.70, 1); LARANJA = (1.0, 0.55, 0.15, 1); CHIPV = (0.10, 0.55, 0.30, 1)
PRATA = (0.80, 0.82, 0.86, 1)
BRILHO = []
def brilha(ob): BRILHO.append(ob.data.materials[0]); return ob
def girarZ(ob, graus): ob.rotation_euler = (0, 0, math.radians(graus))

# ---------------------------------------------------------------- zonas (melhoria do backlog: render mais leve)
ZONAS = []
_antes = [set()]
def zona_ini(): _antes[0] = set(bpy.data.objects.keys())
def zona_fim(janelas):
    novos = [bpy.data.objects[n] for n in bpy.data.objects.keys() if n not in _antes[0]]
    ZONAS.append((novos, janelas))

def _tem_hide(o):
    ad = o.animation_data
    return bool(ad and ad.action and any(fc.data_path == "hide_render" for fc in ad.action.fcurves))

def aplicar_zonas():
    """Objeto sem animação de visibilidade: só renderiza nas janelas da sua zona. Objeto que já tem chaves de
    visibilidade (visivel/pop): ganha um 'esconder' depois da última janela, se ainda estiver visível."""
    for obs, jan in ZONAS:
        ult = max(b for a, b in jan)
        for o in obs:
            if o.type not in ("MESH", "CURVE", "FONT"): continue
            if not _tem_hide(o):
                o.hide_render = True; o.keyframe_insert("hide_render", frame=1)
                for a, b in jan:
                    o.hide_render = False; o.keyframe_insert("hide_render", frame=max(1, f(a)))
                    o.hide_render = True; o.keyframe_insert("hide_render", frame=f(b))
                o.hide_render = True
            elif len(jan) == 1:
                fc = next(fc for fc in o.animation_data.action.fcurves if fc.data_path == "hide_render")
                kps = sorted(fc.keyframe_points, key=lambda k: k.co.x)
                if kps and kps[-1].co.y < 0.5 and kps[-1].co.x < f(ult):
                    o.hide_render = True; o.keyframe_insert("hide_render", frame=f(ult))

# ---------------------------------------------------------------- cenário (anti-borda)
def piso_xadrez(nome, x, c1, c2, larg=24, y0=-10, y1=4.4, lado=2.0):
    nx = int(larg / lado); ny = int((y1 - y0) / lado)
    for i in range(nx):
        for j in range(ny):
            par = (i + j) % 2 == 0
            caixa(_id(nome + "lad"), (x - larg / 2 + lado / 2 + i * lado, y0 + lado / 2 + j * lado, -0.1), (lado, lado, 0.2),
                  c1 if par else c2, unico=f"{nome}lad{int(par)}")

def parede_alta(nome, x, prof, cor, larg=24):
    caixa(nome + "ParedeAlta", (x, prof + 0.05, 10.5), (larg, 0.4, 7.0), tuple(c * 0.85 for c in cor[:3]) + (1,))
    caixa(nome + "Friso", (x, prof - 0.2, 7.05), (larg, 0.15, 0.25), (0.95, 0.75, 0.25, 1))
    for k in range(8):
        caixa(_id(nome + "painel"), (x - 10.5 + k * 3, prof - 0.2, 9.6 + (k % 2) * 1.6), (1.8, 0.08, 0.9), (0.70, 0.88, 1.0, 1), unico="painelLuz")
    BRILHO.append(mat((0.70, 0.88, 1.0, 1), "painelLuz"))

def sala(nome, x, piso1, piso2, parede, prof=4.6):
    sala_fechada(nome, x, piso1, parede, prof=prof, larg=24)
    piso_xadrez(nome, x, piso1, piso2, y1=prof - 0.2)
    parede_alta(nome, x, prof, parede)
    for k in range(4):
        caixa(_id(nome + "prat"), (x - 8.5 + k * 5.6, prof - 0.25, 5.4), (2.2, 0.35, 0.08), (0.98, 0.84, 0.40, 1), unico="prat")
        caixa(_id(nome + "enf"), (x - 9.0 + k * 5.6, prof - 0.3, 5.65), (0.3, 0.25, 0.4), [ROSA, CIANO, VERDE, LARANJA][k], unico=f"enf{k}")

from mathutils import Vector
def texto3d(nome, body, loc, s=1.0, cor=AMARELO, extr=0.12):
    """Texto extrudado convertido em malha (ganha o contorno do nível 2)."""
    cu = bpy.data.curves.new(_id("txt"), "FONT"); cu.body = body; cu.extrude = extr; cu.size = 1.0 * s
    cu.align_x = "CENTER"; cu.align_y = "CENTER"
    tmp = bpy.data.objects.new(_id("txtTmp"), cu); bpy.context.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp); ob = bpy.data.objects.new(nome, me); bpy.context.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler = (math.radians(90), 0, 0)
    m = mat(cor, "txt" + nome); ob.data.materials.append(m); BRILHO.append(m)
    return ob

def interroga(nome, loc, s=1.0, cor=AMARELO):
    return texto3d(nome, "?", loc, 1.6 * s, cor)

def xis(nome, loc, s=0.6, cor=VERMELHO):
    a = caixa(nome, loc, (s, 0.12, s * 0.22), cor); a.rotation_euler = (0, math.radians(45), 0)
    b = caixa(_id("xb"), (0, 0, 0), (s, 0.12, s * 0.22), cor); filho(a, b); b.rotation_euler = (0, math.radians(-90), 0)
    return a

def check(nome, loc, s=1.0, cor=VERDE):
    v = vazio(nome, loc); v.scale = (s, s, s)
    a = caixa(_id("chkA"), (0, 0, 0), (0.5, 0.14, 0.16), cor); filho(v, a); a.location = (-0.3, 0, 0.0); a.rotation_euler = (0, math.radians(45), 0)
    b = caixa(_id("chkB"), (0, 0, 0), (1.0, 0.14, 0.16), cor); filho(v, b); b.location = (0.12, 0, 0.18); b.rotation_euler = (0, math.radians(-55), 0)
    return v


def barra(nome, x, y, z0, h, w=0.7, cor=VERDE, moldura=ESCURO):
    """Medidor vertical: moldura + enchimento (escala Z animável a partir da base)."""
    m = caixa(nome + "Mold", (x, y + 0.08, z0 + h / 2), (w + 0.2, 0.15, h + 0.2), moldura)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.translate(bm, vec=Vector((0, 0, 0.5)), verts=bm.verts)
    bmesh.ops.scale(bm, vec=Vector((w, 0.2, h)), verts=bm.verts)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(nome, me); bpy.context.collection.objects.link(ob); ob.location = (x, y - 0.05, z0)
    mm = mat(cor, nome); ob.data.materials.append(mm)   # cor animada: sem emissão (fixaria a cor)
    return m, ob, mm

def encher(ob, t0, t1, u0=0.0, u1=1.0):
    ob.scale = (1, 1, max(0.001, u0)); ob.keyframe_insert("scale", frame=f(t0))
    ob.scale = (1, 1, max(0.001, u1)); ob.keyframe_insert("scale", frame=f(t1))


def calendario(nome, loc, s=1.0, cor=VERMELHO):
    x, y, z = loc
    b = caixa(nome, (x, y, z), (1.2 * s, 0.12 * s, 1.3 * s), BRANCO); liso(b)
    caixa(_id("topoCal"), (x, y - 0.02, z + 0.55 * s), (1.22 * s, 0.14 * s, 0.3 * s), cor)
    for i in range(3):
        for j in range(3):
            caixa(_id("diaCal"), (x + (i - 1) * 0.32 * s, y - 0.07 * s, z + (0.12 - j * 0.28) * s), (0.2 * s, 0.01 * s, 0.16 * s), (0.75, 0.77, 0.82, 1), unico="diaCal")
    return b


# ---------------------------------------------------------------- modelos desta cena (genéricos, sem marca)
TOKEN_CORES = [(0.20, 0.55, 1.0, 1), (0.95, 0.30, 0.25, 1), (0.25, 0.80, 0.45, 1), (1.0, 0.75, 0.15, 1),
               (0.65, 0.40, 0.95, 1), (1.0, 0.50, 0.75, 1), (0.25, 0.85, 0.90, 1), (1.0, 0.55, 0.20, 1)]
def escurecer(c, k=0.6): return (c[0] * k, c[1] * k, c[2] * k, 1)

def ficha(nome, loc, cor, s=1.0, listras=False):
    """'Time' genérico: disco em pé virado para a câmera, aro branco e miolo mais escuro (sem logo)."""
    v = vazio(nome, loc); v.scale = (s, s, s)
    d = cilindro(_id("disco"), (0, 0, 0), 0.5, 0.18, cor, seg=28); filho(v, d); d.location = (0, 0, 0); d.rotation_euler = (math.radians(90), 0, 0); liso(d)
    a = anel(_id("aro"), (0, 0, 0), 0.5, 0.05, BRANCO, seg=28, unico="aroFicha"); filho(v, a); a.location = (0, -0.02, 0); a.rotation_euler = (math.radians(90), 0, 0)
    m = cilindro(_id("miolo"), (0, 0, 0), 0.24, 0.08, escurecer(cor) if not listras else BRANCO, seg=20); filho(v, m); m.location = (0, -0.1, 0); m.rotation_euler = (math.radians(90), 0, 0)
    if listras:
        for k, dz in enumerate((-0.3, -0.1, 0.1, 0.3)):
            l = caixa(_id("listraZ"), (0, 0, 0), (0.9 - abs(dz) * 1.2, 0.02, 0.08), ESCURO, unico="listraZebra"); filho(v, l); l.location = (0, -0.11, dz)
    return v

def mover(ob, t0, t1, p1, p0=None):
    if p0 is not None: key(ob, "location", t0, p0)
    else: ob.keyframe_insert("location", frame=f(t0))
    key(ob, "location", t1, p1)

def luz(nome, loc, cor_off, r=0.17):
    e = esfera(nome, loc, r, cor_off, sub=2, unico=nome); liso(e)
    m = e.data.materials[0]; cor_key(m, 0, cor_off, "CONSTANT")
    return e, m

def osso(nome, a, b, r, cor, unico):
    a = Vector(a); b = Vector(b); d = b - a
    c = cilindro(nome, tuple((a + b) / 2), r, d.length, cor, seg=8, unico=unico)
    c.rotation_mode = "QUATERNION"; c.rotation_quaternion = d.to_track_quat("Z", "Y")
    return c

def trofeu(nome, loc, s=1.0):
    x, y, z = loc
    b = caixa(nome, (x, y, z), (0.7, 0.5, 0.25), (0.30, 0.20, 0.12, 1)); liso(b); b.scale = (s, s, s)
    h = cilindro(_id("haste"), (0, 0, 0), 0.08, 0.45, OURO, seg=12); filho(b, h); h.location = (0, 0, 0.35 / 1)
    c = cilindro(_id("taca"), (0, 0, 0), 0.18, 0.6, OURO, seg=20, r2=0.45); filho(b, c); c.location = (0, 0, 0.85); liso(c)
    for sx in (-1, 1):
        a = anel(_id("alcaT"), (0, 0, 0), 0.17, 0.04, OURO, seg=16, unico="alcaT"); filho(b, a); a.location = (sx * 0.45, 0, 0.9); a.rotation_euler = (math.radians(90), 0, 0)
    BRILHO.append(mat(OURO))
    return b

def tile_mapa(nome, loc, s=1.0, cores=((0.45, 0.75, 0.35, 1), (0.95, 0.82, 0.55, 1))):
    """Quadro de 'mapa' genérico: moldura escura com blocos coloridos (nada de mapa real de jogo)."""
    v = vazio(nome, loc); v.scale = (s, s, s)
    fr = caixa(_id("molduraM"), (0, 0, 0), (1.5, 0.1, 1.5), ESCURO); filho(v, fr); fr.location = (0, 0, 0)
    for i in range(3):
        for j in range(3):
            c = caixa(_id("blocoM"), (0, 0, 0), (0.42, 0.06, 0.42), cores[(i + j) % 2], unico=f"blocoM{(i + j) % 2}"); filho(v, c); c.location = ((i - 1) * 0.45, -0.06, (j - 1) * 0.45)
    return v

def degrau(nome, x, y, topo, larg=1.3, cor=AZUL):
    d = caixa(nome, (x, y, topo / 2), (larg, 1.2, topo), cor); liso(d); return d

import cartoon as _ct
_ct.PLANOS["geral"] = (7.4, 1.2, 0.3)
cam, alvo, cam_key, plano = camera_cartoon(24)
PX = 0.85
PISO_A = ((0.30, 0.32, 0.55, 1), (0.22, 0.24, 0.44, 1))

# =====================================================================
# ZONA A (x = 0) — palco do torneio: duas fichas; uma perde (X), cai e volta ('?'); 'SEGUE VIVO' (bloco 0) + CTA (bloco 7)
# =====================================================================
zona_ini()
t0, t1 = S[0]
sala("A", 0, PISO_A[0], PISO_A[1], (0.55, 0.38, 0.85, 1))
tpe = T(0, "perdeu"); tca = T(0, "caiu"); tfo = T(0, "fora"); tma = T(0, "Major"); tsi = T(0, "Singapura"); tpr = T(0, "perder"); tel = T(0, "elimina")
telaA = caixa("telaA", (1.0, 4.1, 4.4), (4.6, 0.15, 2.6), ESCURO)
telaAm = caixa("telaAm", (1.0, 4.0, 4.4), (4.3, 0.05, 2.3), (0.15, 0.55, 0.95, 1), unico="telaAm"); BRILHO.append(mat((0.15, 0.55, 0.95, 1), "telaAm"))
trA = trofeu("trofA", (1.2, 3.2, 1.5), 1.1)
pedA = caixa("pedA", (1.2, 3.2, 0.7), (1.0, 0.9, 1.4), (0.85, 0.85, 0.90, 1)); liso(pedA)
fa = ficha("fichaA1", (0.2, 1.4, 3.2), TOKEN_CORES[0], 0.9); pop(fa, 0.0, 0.9, 0.3)
fb = ficha("fichaA2", (2.2, 1.4, 3.2), TOKEN_CORES[1], 0.9); pop(fb, 0.0, 0.9, 0.3)
for o in (fa, fb): visivel(o, 0.0, t1 + 0.3)
vsA = texto3d("vsA", "VS", (1.2, 1.3, 3.2), 0.5, AMARELO, 0.14); visivel(vsA, 0.0, tpe); pop(vsA, 0.05, 1.0)
xA = xis("xA", (2.2, 1.1, 3.2), 0.9); visivel(xA, tpe - 0.1, tca + 0.6); pop(xA, tpe - 0.1, 1.0)
mover(fb, tca - 0.1, tca + 0.4, (2.2, 1.4, 1.9))
key(fb, "location", tfo + 0.4, (2.2, 1.4, 3.4)); key(fb, "location", tfo + 0.6, (2.2, 1.4, 3.2))
iqA = interroga("iqA", (2.2, 1.2, 4.1), 0.45, AMARELO); visivel(iqA, tfo - 0.05, tma - 0.1); pop(iqA, tfo - 0.05, 1.0)
majA = texto3d("majA", "MAJOR", (1.2, 1.3, 4.05), 0.5, AMARELO, 0.14); visivel(majA, tma - 0.1, tpr - 0.1); pop(majA, tma - 0.1, 1.0)
d1A = texto3d("d1A", "1 DERROTA", (1.2, 1.3, 4.05), 0.42, VERMELHO, 0.14); visivel(d1A, tpr - 0.1, tel - 0.1); pop(d1A, tpr - 0.1, 1.0)
svA = texto3d("svA", "SEGUE VIVO", (1.2, 1.3, 4.05), 0.42, VERDE, 0.14); visivel(svA, tel - 0.1, t1 + 0.3); pop(svA, tel - 0.1, 1.0)
ckF = check("ckF", (2.2, 1.1, 3.2), 0.7); visivel(ckF, tel - 0.1, t1 + 0.3); pop(ckF, tel - 0.1, 0.7)
# CTA (bloco 7): ficha FURIA? -> check (PASSA) x X (CAI)
t7 = S[7][0]; tpa = T(7, "passa", 1); tcai = T(7, "cai", 1)
fC = ficha("fichaCTA", (1.2, 1.4, 3.0), (0.25, 0.25, 0.30, 1), 0.9); visivel(fC, t7 - 0.3); pop(fC, t7 - 0.3, 0.9)
iqC = interroga("iqC", (1.2, 1.2, 4.1), 0.45, AMARELO); visivel(iqC, t7 - 0.3, tpa - 0.3); pop(iqC, t7 - 0.2, 1.0)
ckC = check("ckCTA", (0.1, 1.2, 3.8), 1.0); visivel(ckC, tpa - 0.3); pop(ckC, tpa - 0.3, 1.0)
xC = xis("xCTA", (2.3, 1.2, 3.8), 1.0); visivel(xC, tcai - 0.3); pop(xC, tcai - 0.3, 1.0)
px = pixel("pixelA", (-1.1, 0.4, 0), escala=PX); girarZ(px["raiz"], 14); respirar(px, 0, t1 + 0.3); respirar(px, t7 - 0.3, FIM)
espanto(px, tpe - 0.1, 1.2); pensar(px, tfo, 1.4); apontar(px, tel - 0.1, 1.2, "D", 40)
acenar(px, t7 + 0.1, 1.4); apontar(px, tpa - 0.2, 1.2, "D", 70); apontar(px, tcai - 0.2, 1.2, "D", 40)
acenar(px, LEG[-1]["e"] + 1.2, 1.6); comemorar(px, LEG[-1]["e"] + 3.0, 1.4)
plano(0, (0.5, 1.8), "geral", altura=2.3); plano(tma - 0.2, (0.55, 1.8), "geral", altura=2.35); plano(t1 - 0.05, (0.5, 1.8), "geral", altura=2.3)
plano(t7, (0.5, 1.8), "geral", altura=2.3); plano(FIM, (0.55, 1.6), "geral", altura=2.3)
zona_fim([(0.0, t1 + 0.3), (t7 - 0.3, FIM + 0.5)])

# =====================================================================
# ZONA B (x = 40) — placar: '3 x 16'; ficha verde enche 3 luzes e sobe (avança); ficha vermelha enche 3 e cai (bloco 1)
# =====================================================================
zona_ini()
t0, t1 = S[1]; X = 40
sala("B", X, (0.95, 0.80, 0.45, 1), (0.68, 0.50, 0.26, 1), (0.25, 0.30, 0.55, 1))
ttr = T(1, "três"); tde = T(1, "dezesseis"); tqu = T(1, "Quem"); tvi = T(1, "vitórias"); tav = T(1, "avança"); tqu2 = T(1, "Quem", 1); tdr = T(1, "derrotas"); tvo = T(1, "volta"); tcs = T(1, "casa")
painel = caixa("painelB", (X + 1.4, 2.6, 3.2), (4.4, 0.15, 2.9), ESCURO); liso(painel)
for k in range(3):
    n = texto3d(_id("nFase"), str(k + 1), (X + 0.3 + 1.1 * k, 1.4, 4.0), 0.6, [CIANO, ROSA, AMARELO][k], 0.14)
    visivel(n, t0 - 0.3, tqu - 0.1); pop(n, ttr - 0.1 + 0.12 * k, 1.0)
x16 = texto3d("x16", "16 CADA", (X + 1.4, 1.4, 3.0), 0.45, BRANCO, 0.12); visivel(x16, tde - 0.1, tqu - 0.1); pop(x16, tde - 0.1, 1.0)
fV = ficha("fichaV", (X + 0.4, 1.4, 3.5), TOKEN_CORES[2], 0.85); visivel(fV, tqu - 0.15); pop(fV, tqu - 0.15, 0.85)
fR = ficha("fichaR", (X + 2.4, 1.4, 3.5), TOKEN_CORES[1], 0.85); visivel(fR, tqu - 0.15); pop(fR, tqu - 0.15, 0.85)
LV = [luz(_id("luzV"), (X - 0.05 + 0.45 * k, 1.5, 2.3), (0.20, 0.24, 0.22, 1)) for k in range(3)]
LR = [luz(_id("luzR"), (X + 1.95 + 0.45 * k, 1.5, 2.3), (0.24, 0.20, 0.20, 1)) for k in range(3)]
for e, m in LV + LR: visivel(e, tqu - 0.15)
for k, (e, m) in enumerate(LV):
    tt = tqu + 0.25 + (tav - 0.1 - tqu - 0.25) * k / 2; cor_key(m, tt - 0.01, (0.20, 0.24, 0.22, 1), "CONSTANT"); cor_key(m, tt, (0.20, 1.0, 0.35, 1), "CONSTANT")
for k, (e, m) in enumerate(LR):
    tt = tqu2 + 0.2 + (tvo - 0.1 - tqu2 - 0.2) * k / 2; cor_key(m, tt - 0.01, (0.24, 0.20, 0.20, 1), "CONSTANT"); cor_key(m, tt, (1.0, 0.18, 0.15, 1), "CONSTANT")
mover(fV, tav - 0.05, tav + 0.5, (X + 0.4, 1.4, 4.0))
ckB = check("ckB", (X + 1.15, 1.1, 3.95), 0.5); visivel(ckB, tav + 0.4); pop(ckB, tav + 0.4, 0.5)
mover(fR, tvo - 0.05, tcs + 0.3, (X + 2.4, 1.4, -1.0))
xB = xis("xB", (X + 2.4, 1.2, 3.4), 0.8); visivel(xB, tvo - 0.05); pop(xB, tvo - 0.05, 1.0)
pxB = pixel("pixelB", (X - 1.0, 0.4, 0), escala=PX); girarZ(pxB["raiz"], 16); respirar(pxB, t0 - 0.3, t1 + 0.3)
acenar(pxB, t0 + 0.05, 1.2); apontar(pxB, tav - 0.2, 1.2, "D", 70); espanto(pxB, tvo - 0.1, 1.2)
plano(t0, (X + 0.6, 1.8), "geral", altura=2.3); plano(t1 - 0.05, (X + 0.7, 1.8), "geral", altura=2.4)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA C (x = 80) — tabuleiro suíço: 4 fichas por ranking (1..4) em 0-0; vencedores vão para 1-0, perdedores para 0-1 (bloco 2)
# =====================================================================
zona_ini()
t0, t1 = S[2]; X = 80
sala("C", X, (0.45, 0.80, 0.70, 1), (0.30, 0.62, 0.55, 1), (0.85, 0.45, 0.35, 1))
tra = T(2, "ranking"); tdp = T(2, "Depois"); tmc = T(2, "campanha"); tc1 = T(2, "contra", 1); tc2 = T(2, "contra", 2)
for xx in (0.0, 1.9):
    caixa(_id("colC"), (X + xx, 2.4, 3.1), (1.4, 0.12, 3.4), (0.95, 0.93, 0.88, 1), unico="colC")
l00 = texto3d("l00", "0-0", (X + 0.0, 1.4, 4.2), 0.38, BRANCO, 0.12); visivel(l00, t0 - 0.3, tdp); pop(l00, t0, 1.0)
ZC = (3.7, 3.15, 2.6, 2.05)
FC = []; NUM = []
for k in range(4):
    fk = ficha(_id("fichaC"), (X + 0.0, 1.5, ZC[k]), TOKEN_CORES[k + 3], 0.5); FC.append(fk)
    nk = texto3d(_id("rk"), str(k + 1), (X + 0.48, 1.4, ZC[k]), 0.32, AMARELO, 0.1); visivel(nk, tra - 0.2, tdp); pop(nk, tra - 0.2 + 0.1 * k, 1.0)
# pares por ranking (1x4, 2x3): setas = traços
for a_, b_ in ((0, 3), (1, 2)):
    tr = caixa(_id("parC"), (X + 0.78 + 0.12 * a_, 1.45, (ZC[a_] + ZC[b_]) / 2), (0.06, 0.06, abs(ZC[a_] - ZC[b_])), AMARELO, unico="parC")
    visivel(tr, tra + 0.2, tdp); pop(tr, tra + 0.2, 1.0)
# vencedores (1 e 2) -> 1-0 ; perdedores (3 e 4) -> 0-1
dest = {0: (X + 1.9, 1.5, 3.75), 1: (X + 1.9, 1.5, 3.2), 2: (X + 1.9, 1.5, 2.45), 3: (X + 1.9, 1.5, 1.9)}
for k in range(4):
    mover(FC[k], tdp - 0.05 + 0.1 * k, tdp + 0.6 + 0.1 * k, dest[k])
l10 = texto3d("l10", "1-0", (X + 2.85, 1.4, 3.48), 0.34, VERDE, 0.12); visivel(l10, tdp + 0.5); pop(l10, tdp + 0.5, 1.0)
l01 = texto3d("l01", "0-1", (X + 2.85, 1.4, 2.18), 0.34, VERMELHO, 0.12); visivel(l01, tdp + 0.7); pop(l01, tdp + 0.7, 1.0)
v1 = texto3d("vsC1", "VS", (X + 0.95, 1.3, 3.48), 0.3, AMARELO, 0.1); visivel(v1, tc1 - 0.2); pop(v1, tc1 - 0.2, 1.0)
v2 = texto3d("vsC2", "VS", (X + 0.95, 1.3, 2.18), 0.3, AMARELO, 0.1); visivel(v2, tc2 - 0.2); pop(v2, tc2 - 0.2, 1.0)
pxC = pixel("pixelC", (X - 0.7, 0.4, 0), escala=PX); girarZ(pxC["raiz"], 16); respirar(pxC, t0 - 0.3, t1 + 0.3)
pensar(pxC, t0 + 0.05, 1.4); apontar(pxC, tra - 0.2, 1.2, "D", 60); apontar(pxC, tc1 - 0.2, 1.3, "D", 70); apontar(pxC, tc2 - 0.2, 1.3, "D", 40)
plano(t0, (X + 0.9, 1.8), "geral", altura=2.3); plano(tdp, (X + 0.9, 1.8), "geral", altura=2.35); plano(t1 - 0.05, (X + 0.95, 1.8), "geral", altura=2.35)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA D (x = 120) — MD1: 1 mapa, a ficha-zebra derruba a grandona; MD3: 3 mapas (bloco 3)
# =====================================================================
zona_ini()
t0, t1 = S[3]; X = 120
sala("D", X, (0.60, 0.50, 0.90, 1), (0.45, 0.36, 0.72, 1), (0.95, 0.60, 0.30, 1))
tmp_ = T(3, "mapa"); tze = T(3, "zebra"); tac = T(3, "acontece"); tmas = T(3, "mas"); tcl = T(3, "classifica"); ttr3 = T(3, "três")
md1 = texto3d("md1", "MD1", (X + 0.9, 1.3, 4.1), 0.42, AMARELO, 0.14); visivel(md1, t0 - 0.3, tmas - 0.1); pop(md1, t0, 1.0)
mapa1 = tile_mapa("mapa1", (X + 0.9, 2.2, 2.9), 1.0); pop(mapa1, t0 - 0.05, 1.0)
for o in todos(mapa1): visivel(o, t0 - 0.3, tmas)
grande = ficha("fichaGrande", (X + 1.9, 1.2, 3.0), TOKEN_CORES[0], 1.15)
zeb = ficha("fichaZebra", (X + 0.15, 1.0, 2.9), BRANCO, 0.75, listras=True)
for o in (grande, zeb): visivel(o, t0 - 0.3, tmas)
mover(zeb, tze - 0.35, tze, (X + 1.3, 1.0, 2.9))
key(grande, "location", tze, (X + 1.9, 1.2, 3.0)); key(grande, "location", tze + 0.7, (X + 4.5, 1.2, 5.5))
key(grande, "rotation_euler", tze, (0, 0, 0)); key(grande, "rotation_euler", tze + 0.7, (0, math.radians(200), 0))
ckZ = check("ckZ", (X + 1.25, 1.0, 3.8), 0.55); visivel(ckZ, tac - 0.1, tmas); pop(ckZ, tac - 0.1, 0.55)
MAPS = [tile_mapa(_id("mapa3"), (X + 0.0 + 1.15 * k, 2.0, 3.0), 0.72, cores=[((0.45, 0.75, 0.35, 1), (0.95, 0.82, 0.55, 1)), ((0.40, 0.65, 0.95, 1), (0.90, 0.90, 0.95, 1)), ((0.95, 0.55, 0.35, 1), (0.98, 0.85, 0.40, 1))][k]) for k in range(3)]
for k, mp in enumerate(MAPS):
    for o in todos(mp): visivel(o, tmas - 0.05)
    pop(mp, tmas + 0.15 * k, 0.72)
md3 = texto3d("md3", "MD3", (X + 1.0, 1.3, 4.1), 0.42, VERDE, 0.14); visivel(md3, tmas - 0.1); pop(md3, tmas - 0.1, 1.0)
pxD = pixel("pixelD", (X - 0.7, 0.4, 0), escala=PX); girarZ(pxD["raiz"], 16); respirar(pxD, t0 - 0.3, t1 + 0.3)
apontar(pxD, tmp_ - 0.2, 1.2, "D", 50); espanto(pxD, tze, 1.2); comemorar(pxD, ttr3 - 0.3, 1.2)
plano(t0, (X + 0.9, 1.8), "geral", altura=2.3); plano(tmas - 0.1, (X + 0.9, 1.8), "geral", altura=2.3); plano(t1 - 0.05, (X + 0.95, 1.8), "geral", altura=2.35)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA E (x = 160) — Buchholz: ficha azul liga 3 adversários (2, 1 e 3 vitórias) e a soma vira '= 6' (bloco 4)
# =====================================================================
zona_ini()
t0, t1 = S[4]; X = 160
sala("E", X, (0.98, 0.70, 0.55, 1), (0.85, 0.52, 0.40, 1), (0.30, 0.55, 0.60, 1))
tgr = T(4, "grupo"); tbu = T(4, "Buchholz"); tso = T(4, "soma"); tad = T(4, "adversários"); ten = T(4, "enfrentou"); tor = T(4, "organiza")
quadro = caixa("quadroE", (X + 1.2, 2.8, 3.3), (4.4, 0.12, 2.9), (0.96, 0.96, 0.92, 1))
fE = ficha("fichaE", (X + 0.2, 1.5, 3.2), TOKEN_CORES[0], 0.75); pop(fE, t0 - 0.05, 0.75)
fE2 = ficha("fichaE2", (X + 0.2, 1.5, 2.0), TOKEN_CORES[3], 0.55); visivel(fE2, t0 - 0.3, tbu); pop(fE2, t0, 0.55)
igu = texto3d("iguE", "=", (X + 0.2, 1.4, 2.6), 0.4, ESCURO, 0.1); visivel(igu, t0 - 0.3, tbu); pop(igu, t0 + 0.1, 1.0)
OPZ = (3.9, 3.1, 2.3); OPW = ("2", "1", "3"); OPC = (TOKEN_CORES[1], TOKEN_CORES[4], TOKEN_CORES[6])
for k in range(3):
    fo = ficha(_id("fichaOp"), (X + 2.2, 1.5, OPZ[k]), OPC[k], 0.5); visivel(fo, tbu - 0.2); pop(fo, tbu - 0.2 + 0.12 * k, 0.5)
    ln = osso(_id("linhaE"), (X + 0.55, 1.6, 3.2), (X + 1.9, 1.6, OPZ[k]), 0.035, ESCURO, "linhaE"); visivel(ln, tad - 0.1); pop(ln, tad - 0.1 + 0.1 * k, 1.0)
    nw = texto3d(_id("nwE"), OPW[k], (X + 2.85, 1.4, OPZ[k]), 0.36, VERDE, 0.1); visivel(nw, tso - 0.1, ten + 0.4); pop(nw, tso - 0.1 + 0.12 * k, 1.0)
    # o número 'voa' para a soma
    nv = texto3d(_id("nvE"), OPW[k], (X + 2.85, 1.4, OPZ[k]), 0.36, VERDE, 0.1); visivel(nv, ten + 0.4, ten + 1.2)
    mover(nv, ten + 0.4, ten + 1.1, (X + 0.9, 1.3, 4.1), (X + 2.85, 1.4, OPZ[k]))
soma = texto3d("somaE", "= 6", (X + 0.9, 1.3, 4.1), 0.45, AMARELO, 0.14); visivel(soma, ten + 1.1); pop(soma, ten + 1.1, 1.0)
pxE = pixel("pixelE", (X - 0.8, 0.4, 0), escala=PX); girarZ(pxE["raiz"], 16); respirar(pxE, t0 - 0.3, t1 + 0.3)
pensar(pxE, tgr - 0.3, 1.5); apontar(pxE, tso - 0.2, 1.3, "D", 60); comemorar(pxE, tor - 0.2, 1.3)
plano(t0, (X + 0.8, 1.8), "geral", altura=2.3); plano(t1 - 0.05, (X + 0.85, 1.8), "geral", altura=2.4)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA F (x = 200) — escada das fases: ficha pula direto ao degrau 3; MIBR no 2 ('hoje'); FURIA no 3; calendário 2 DEZ (bloco 5)
# =====================================================================
zona_ini()
t0, t1 = S[5]; X = 200
sala("F", X, (0.55, 0.72, 0.98, 1), (0.40, 0.56, 0.85, 1), (0.95, 0.75, 0.40, 1))
tpu = T(5, "pula"); tmi = T(5, "MIBR"); tho = T(5, "hoje"); tfu = T(5, "FURIA"); tdz = T(5, "dezembro"); tmd = T(5, "melhor")
D1 = degrau("deg1", X + 0.1, 1.6, 1.4, 1.3, (0.35, 0.80, 0.90, 1)); D2 = degrau("deg2", X + 1.4, 1.6, 2.1, 1.3, (1.0, 0.50, 0.75, 1)); D3 = degrau("deg3", X + 2.7, 1.6, 2.8, 1.3, (1.0, 0.78, 0.20, 1))
for k, (xx, zz) in enumerate(((X + 0.1, 0.8), (X + 1.4, 1.15), (X + 2.7, 1.5))):
    texto3d(_id("nDeg"), str(k + 1), (xx, 0.95, zz + 0.5), 0.5, BRANCO, 0.1)
fp = ficha("fichaPula", (X + 0.1, 1.5, 1.85), TOKEN_CORES[4], 0.55); visivel(fp, t0 - 0.3, tmi - 0.1); pop(fp, t0, 0.55)
key(fp, "location", tpu - 0.1, (X + 0.1, 1.5, 1.85)); key(fp, "location", tpu + 0.25, (X + 1.4, 1.5, 4.2)); key(fp, "location", tpu + 0.55, (X + 2.7, 1.5, 3.25))
fM = ficha("fichaMIBR", (X + 1.4, 1.5, 2.55), (0.30, 0.32, 0.38, 1), 0.6); visivel(fM, tmi - 0.15); pop(fM, tmi - 0.15, 0.6)
tM = texto3d("txtMIBR", "MIBR", (X + 1.4, 1.4, 3.35), 0.34, BRANCO, 0.1); visivel(tM, tmi - 0.15); pop(tM, tmi - 0.15, 1.0)
fF = ficha("fichaFURIA", (X + 2.7, 1.5, 3.25), (0.12, 0.12, 0.14, 1), 0.6); visivel(fF, tfu - 0.15); pop(fF, tfu - 0.15, 0.6)
tF = texto3d("txtFURIA", "FURIA", (X + 2.7, 1.4, 3.98), 0.34, BRANCO, 0.1); visivel(tF, tfu - 0.15); pop(tF, tfu - 0.15, 1.0)
calF = calendario("calF", (X + 0.1, 2.2, 3.35), 0.8, VERMELHO); visivel(calF, tdz - 0.3); pop(calF, tdz - 0.3, 1.0)
for o in bpy.data.objects:
    if o.name.startswith(("topoCal", "diaCal")) and abs(o.location.x - (X + 0.1)) < 1: visivel(o, tdz - 0.3)
t2d = texto3d("t2dez", "2 DEZ", (X + 0.1, 1.9, 4.15), 0.36, VERMELHO, 0.12); visivel(t2d, tdz - 0.3); pop(t2d, tdz - 0.3, 1.0)
pxF = pixel("pixelF", (X - 0.75, 0.4, 0), escala=PX); girarZ(pxF["raiz"], 16); respirar(pxF, t0 - 0.3, t1 + 0.3)
apontar(pxF, tpu - 0.2, 1.2, "D", 70); apontar(pxF, tmi - 0.2, 1.3, "D", 50); comemorar(pxF, tfu - 0.1, 1.3); apontar(pxF, tdz - 0.2, 1.2, "D", 30)
plano(t0, (X + 0.85, 1.8), "geral", altura=2.3); plano(tfu - 0.3, (X + 0.9, 1.8), "geral", altura=2.4); plano(t1 - 0.05, (X + 0.9, 1.8), "geral", altura=2.4)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA G (x = 240) — mata-mata: 8 fichas -> 4 -> 2 -> 1 até o troféu; 'MD5' na final (bloco 6)
# =====================================================================
zona_ini()
t0, t1 = S[6]; X = 240
sala("G", X, (0.40, 0.42, 0.62, 1), (0.28, 0.30, 0.48, 1), (0.85, 0.35, 0.45, 1))
toi = T(6, "oito"); tse = T(6, "segunda"); tmm = T(6, "mata-mata"); tfi = T(6, "final"); tci = T(6, "cinco")
fundo = caixa("chaveG", (X + 2.25, 2.6, 3.0), (4.4, 0.12, 2.6), (0.95, 0.95, 0.98, 1))
ZQ = (3.9, 3.3, 2.7, 2.1); ZS = ((3.9 + 3.3) / 2, (2.7 + 2.1) / 2); ZF = 3.0
def lh(x0, x1, z): caixa(_id("linG"), ((x0 + x1) / 2, 2.5, z), (abs(x1 - x0), 0.05, 0.05), ESCURO, unico="linG")
def lv(x, z0, z1): caixa(_id("linG"), (x, 2.5, (z0 + z1) / 2), (0.05, 0.05, abs(z1 - z0)), ESCURO, unico="linG")
LADOS = {-1: (X + 0.6, X + 1.4, X + 1.95), 1: (X + 3.9, X + 3.1, X + 2.55)}   # (quartas, semi, final)
for sd, (xq, xs, xf) in LADOS.items():
    xm = (xq + xs) / 2
    for a_, b_ in ((0, 1), (2, 3)):
        lh(xq, xm, ZQ[a_]); lh(xq, xm, ZQ[b_]); lv(xm, ZQ[a_], ZQ[b_]); lh(xm, xs, (ZQ[a_] + ZQ[b_]) / 2)
    xm2 = (xs + xf) / 2
    lh(xs, xm2, ZS[0]); lh(xs, xm2, ZS[1]); lv(xm2, ZS[0], ZS[1]); lh(xm2, xf, ZF)
trG = trofeu("trofG", (X + 2.25, 2.0, 1.75), 0.75); visivel(trG, tfi - 0.2); pop(trG, tfi - 0.2, 0.75)
F8 = {}
k = 0
for sd, (xq, xs, xf) in LADOS.items():
    for i_ in range(4):
        fk = ficha(_id("fichaG"), (xq, 2.0, ZQ[i_]), TOKEN_CORES[k], 0.42); pop(fk, t0 - 0.05 + 0.05 * k, 0.42); F8[(sd, i_)] = fk; k += 1
# quartas: vencem 0 e 3 de cada lado; semi: vence o 0 da esquerda e o 3 da direita; final: direita
for sd, (xq, xs, xf) in LADOS.items():
    mover(F8[(sd, 0)], tmm - 0.1, tmm + 0.35, (xs, 2.0, ZS[0])); mover(F8[(sd, 3)], tmm - 0.1, tmm + 0.35, (xs, 2.0, ZS[1]))
    sumir(F8[(sd, 1)], tmm + 0.1); sumir(F8[(sd, 2)], tmm + 0.1)
vL, vR = F8[(-1, 0)], F8[(1, 3)]
mover(vL, tmm + 0.45, tmm + 0.8, (LADOS[-1][2], 2.0, ZF)); mover(vR, tmm + 0.45, tmm + 0.8, (LADOS[1][2], 2.0, ZF))
sumir(F8[(-1, 3)], tmm + 0.6); sumir(F8[(1, 0)], tmm + 0.6)
mover(vR, tfi - 0.2, tfi + 0.2, (X + 2.25, 2.0, 3.75))
sumir(vL, tfi)
md5 = texto3d("md5", "MD5", (X + 2.25, 1.9, 4.3), 0.3, AMARELO, 0.1); visivel(md5, tci - 0.2); pop(md5, tci - 0.2, 1.0)
pxG = pixel("pixelG", (X - 0.1, 0.4, 0), escala=PX); girarZ(pxG["raiz"], 16); respirar(pxG, t0 - 0.3, t1 + 0.3)
apontar(pxG, toi - 0.2, 1.2, "D", 60); espanto(pxG, tse - 0.1, 1.1); comemorar(pxG, tfi - 0.1, 1.3)
plano(t0, (X + 1.5, 1.8), "geral", altura=2.3); plano(t1 - 0.05, (X + 1.55, 1.8), "geral", altura=2.4)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# ---------- corte seco entre zonas + visibilidade por zona ----------
corte_seco(cam, alvo)
aplicar_zonas()

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
    scn.render.use_overwrite = False   # retomada: quadros já prontos são pulados
    bpy.ops.render.render(animation=True)
else:
    print("FRAMES", scn.frame_end)
