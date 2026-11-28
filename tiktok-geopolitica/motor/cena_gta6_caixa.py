"""Série 2 — 'Por que a caixa do GTA 6 não tem disco?' (notícia 27/11; estilo C cartoon, mascote Pixel, visual nível 2).
Mecanismo: código de resgate. Caixa de jogo GENÉRICA (sem arte/logo) abre e só tem um papel com código; o código
(fila de letras brilhando) vira um envelope que voa até o servidor da loja (torre com cadeado), que confere 2 coisas
(existe? já usado?), carimba USADO e devolve uma chave dourada que entra na 'conta' do Pixel; o jogo baixa da nuvem
para um console genérico. Risco: caixa com código já usado / sem código (sem ensinar truque). Dica: abrir no balcão.
CTA DISCO x DIGITAL. Base: cena_gta6_consoles.py (zonas por bloco; objetos principais já visíveis no corte).
Backlog: salas claras com ladrilho de contraste maior (QC gta6-pirata-pc).
Uso: blender -b --factory-startup -P cena_gta6_caixa.py -- <pasta> [preview t1,t2 | range a,b]"""
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

# ---------------------------------------------------------------- modelos genéricos (sem marca)
def console(nome, loc, s=1.0, cor=BRANCO):
    c = caixa(nome, loc, (0.55 * s, 1.1 * s, 1.5 * s), cor); liso(c)
    fx = caixa(_id("faixaCons"), (0, 0, 0), (0.04 * s, 0.9 * s, 0.08 * s), (0.3, 0.7, 1.0, 1), unico="faixaCons"); filho(c, fx); fx.location = (0.29 * s, 0, 0.5 * s)
    bt = esfera(_id("botCons"), (0, 0, 0), 0.06 * s, VERDE, sub=1); filho(c, bt); bt.location = (0.29 * s, -0.4 * s, -0.55 * s)
    BRILHO.append(mat((0.3, 0.7, 1.0, 1), "faixaCons"))
    c.rotation_euler = (0, 0, math.radians(90))   # frente larga para a câmera
    return c

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

def cadeado(nome, loc, s=1.0, cor=OURO):
    c = caixa(nome, loc, (0.8 * s, 0.35 * s, 0.65 * s), cor); liso(c)
    a = anel(_id("alca"), (0, 0, 0), 0.28 * s, 0.07 * s, CINZA, seg=20); filho(c, a); a.location = (0, 0, 0.36 * s); a.rotation_euler = (math.radians(90), 0, 0)
    fu = esfera(_id("fur"), (0, 0, 0), 0.08 * s, ESCURO, sub=1); filho(c, fu); fu.location = (0, -0.18 * s, 0.03 * s)
    return c, a

def servidor(nome, loc, s=1.0, cor_led=VERDE, unico="ledSrv"):
    r = caixa(nome, loc, (1.2 * s, 1.0 * s, 2.6 * s), (0.14, 0.15, 0.20, 1))
    for j in range(6):
        l = caixa(_id("ledS"), (0, 0, 0), (0.9 * s, 0.04 * s, 0.1 * s), cor_led, unico=unico); filho(r, l); l.location = (0, -0.52 * s, (-1.0 + j * 0.4) * s)
    BRILHO.append(mat(cor_led, unico))
    return r

def nuvemzinha(nome, loc, s=1.0):
    b = esfera(nome, loc, 0.9 * s, BRANCO, sub=2); liso(b)
    for dx, dz, r in ((0.9, -0.2, 0.65), (-0.9, -0.25, 0.6), (0.35, 0.5, 0.6)):
        e = esfera(_id("nuvz"), (0, 0, 0), r * s, BRANCO, sub=2); filho(b, e); e.location = (dx * s, 0, dz * s); liso(e)
    return b

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


def fumaca(nome, loc, t, n=4, cor=(0.32, 0.33, 0.37, 1)):
    """Bolinhas cinza subindo (console 'morrendo')."""
    for k in range(n):
        e = esfera(_id(nome), loc, 0.3, cor, sub=2, unico="fumaca"); liso(e)
        a = t + 0.35 * k; b = a + 1.6; visivel(e, a, b)
        key(e, "location", a, loc); key(e, "location", b, (loc[0] + random.uniform(-0.4, 0.4), loc[1], loc[2] + 1.8))
        e.scale = (0.5,) * 3; e.keyframe_insert("scale", frame=f(a)); e.scale = (1.4,) * 3; e.keyframe_insert("scale", frame=f(b))

def led(nome, loc, cor, r=0.08):
    m = mat(cor, nome); e = esfera(nome, loc, r, cor, sub=1, unico=nome); return e, m

def piscar(m, t0, t1, c1, c2, per=0.4):
    t = t0; k = 0
    while t < t1:
        cor_key(m, t, c1 if k % 2 == 0 else c2, "CONSTANT"); t += per; k += 1

def particulas(nome, n, t0, t1, p0, p1, p2, cor, unico, r=0.12, dur=1.4):
    """Bolinhas que seguem uma curva de p0 a p2 em fila (calor, ar)."""
    BRILHO.append(mat(cor, unico))
    k = 0; t = t0
    while t < t1 and k < n:
        e = esfera(_id(nome), p0, r, cor, sub=1, unico=unico); visivel(e, t, t + dur)
        caminho(e, t, t + dur, lambda u, a=p0, b=p1, c=p2: bez(a, b, c, u), orientar=False, passo=3)
        t += (t1 - t0) / n; k += 1

def balao(nome, loc, s=1.0):
    b = esfera(nome, loc, 0.75 * s, BRANCO, sub=2); liso(b); b.scale = (1.25, 0.35, 0.9)
    for dx in (-0.3, 0, 0.3):
        p = esfera(_id("ponto"), (0, 0, 0), 0.09 * s, CINZA, sub=1, unico="pontoB"); filho(b, p); p.location = (dx * s / 1.25, -0.75, 0)
    return b


# ---------------------------------------------------------------- modelos desta cena (genéricos, sem marca)
CORES_CX = [(0.20, 0.70, 0.45, 1), (0.85, 0.30, 0.35, 1), ROXO, LARANJA, (0.25, 0.75, 0.85, 1), (0.90, 0.75, 0.20, 1)]

def codigo(nome, loc, s=1.0, n=6, unico="codigo", cor=CIANO):
    """Fila de 'letras' (cubinhos brilhantes) — o código; nada legível."""
    BRILHO.append(mat(cor, unico)); L = []
    for k in range(n):
        c = caixa(_id(nome), (loc[0] + (k - (n - 1) / 2) * 0.16 * s, loc[1], loc[2] + (0.03 if k % 2 else -0.03) * s),
                  (0.11 * s, 0.04 * s, 0.16 * s), cor, unico=unico); L.append(c)
    return L

def estojo(nome, loc, s=1.0, cor=(0.20, 0.70, 0.45, 1), papel=True):
    """Estojo de jogo genérico (capa colorida lisa, sem arte). Retorna (base, dobradiça, letras)."""
    x, y, z = loc
    base = caixa(nome, (x, y, z), (1.0 * s, 0.10 * s, 1.35 * s), (0.12, 0.13, 0.17, 1)); liso(base)
    letras = []
    if papel:
        caixa(_id("papel"), (x, y - 0.07 * s, z), (0.62 * s, 0.02 * s, 0.85 * s), BRANCO, unico="papel")
        letras = codigo(_id("cod"), (x, y - 0.09 * s, z + 0.1 * s), s)
        for k in range(3):
            caixa(_id("linhaP"), (x, y - 0.085 * s, z - (0.15 + 0.12 * k) * s), (0.45 * s, 0.01 * s, 0.035 * s), (0.70, 0.72, 0.78, 1), unico="linhaP")
    dob = vazio(_id("dob"), (x - 0.5 * s, y - 0.12 * s, z))
    capa = caixa(_id("capaE"), (0, 0, 0), (1.0 * s, 0.05 * s, 1.35 * s), cor); filho(dob, capa); capa.location = (0.5 * s, 0, 0)
    est = esfera(_id("estrela"), (0, 0, 0), 0.22 * s, BRANCO, sub=1); filho(dob, est); est.location = (0.5 * s, -0.04 * s, 0.2 * s); est.scale = (1, 0.3, 1)
    fx = caixa(_id("faixaE"), (0, 0, 0), (0.8 * s, 0.03 * s, 0.12 * s), BRANCO, unico="faixaE"); filho(dob, fx); fx.location = (0.5 * s, -0.04 * s, -0.35 * s)
    return base, dob, letras

def abrir(dob, t, dur=0.5, ang=-155):
    key(dob, "rotation_euler", t, (0, 0, 0)); key(dob, "rotation_euler", t + dur, (0, 0, math.radians(ang)))

def disco(nome, loc, s=1.0):
    d = cilindro(nome, loc, 0.6 * s, 0.04 * s, PRATA, seg=32); d.rotation_euler = (math.radians(90), 0, 0)
    ar = anel(_id("arcoD"), (0, 0, 0), 0.42 * s, 0.07 * s, (0.75, 0.55, 1.0, 1), seg=28, unico="arcoD"); filho(d, ar); ar.location = (0, 0, 0.03 * s)
    fu = cilindro(_id("furoD"), (0, 0, 0), 0.12 * s, 0.06 * s, ESCURO, seg=16); filho(d, fu)
    return d

def controle(nome, loc, s=1.0, cor=ESCURO):
    c = caixa(nome, loc, (1.2 * s, 0.35 * s, 0.5 * s), cor); liso(c)
    for dx in (-0.5, 0.5):
        g = esfera(_id("pega"), (0, 0, 0), 0.3 * s, cor, sub=2); filho(c, g); g.location = (dx * s, 0, -0.2 * s); liso(g)
    for k, cc in enumerate((VERMELHO, VERDE, AZUL, AMARELO)):
        b = esfera(_id("botC"), (0, 0, 0), 0.06 * s, cc, sub=1); filho(c, b)
        b.location = ((0.32 + (0.09 if k == 1 else -0.09 if k == 3 else 0)) * s, -0.19 * s, (0.05 + (0.09 if k == 0 else -0.09 if k == 2 else 0)) * s)
    for dx in (-0.3, 0.12):
        a = cilindro(_id("stick"), (0, 0, 0), 0.08 * s, 0.08 * s, CINZA, seg=10); filho(c, a); a.location = (dx * s, -0.2 * s, -0.08 * s); a.rotation_euler = (math.radians(90), 0, 0)
    return c

def envelope(nome, loc, s=1.0):
    e = caixa(nome, loc, (1.0 * s, 0.08 * s, 0.65 * s), BRANCO); liso(e)
    ab = caixa(_id("aba"), (0, 0, 0), (0.5 * s, 0.03 * s, 0.5 * s), (0.88, 0.90, 0.95, 1)); filho(e, ab); ab.location = (0, -0.05 * s, 0.12 * s); ab.rotation_euler = (0, math.radians(45), 0); ab.scale = (1, 1, 0.75)
    se = cilindro(_id("selo"), (0, 0, 0), 0.1 * s, 0.04 * s, VERMELHO, seg=14); filho(e, se); se.location = (0, -0.08 * s, -0.05 * s); se.rotation_euler = (math.radians(90), 0, 0)
    return e

def chave(nome, loc, s=1.0):
    BRILHO.append(mat(OURO, "ouroK"))
    v = vazio(nome, loc); v.scale = (s, s, s)
    a = anel(_id("cabK"), (0, 0, 0), 0.25, 0.08, OURO, seg=20, unico="ouroK"); filho(v, a); a.location = (-0.5, 0, 0); a.rotation_euler = (math.radians(90), 0, 0)
    h = caixa(_id("hasteK"), (0, 0, 0), (0.8, 0.1, 0.12), OURO, unico="ouroK"); filho(v, h); h.location = (0.12, 0, 0)
    for dx in (0.3, 0.45):
        d = caixa(_id("denteK"), (0, 0, 0), (0.08, 0.1, 0.18), OURO, unico="ouroK"); filho(v, d); d.location = (dx, 0, -0.12)
    return v

def tela(nome, loc, s=1.0, cor=(0.15, 0.55, 0.95, 1)):
    t = caixa(nome, loc, (2.4 * s, 0.14 * s, 1.4 * s), ESCURO)
    m = caixa(_id("telaM"), (0, 0, 0), (2.2 * s, 0.02 * s, 1.2 * s), cor, unico=nome + "M"); filho(t, m); m.location = (0, -0.08 * s, 0)
    BRILHO.append(mat(cor, nome + "M"))
    p = caixa(_id("peT"), (0, 0, 0), (0.2 * s, 0.2 * s, 0.6 * s), ESCURO); filho(t, p); p.location = (0, 0.05 * s, -0.95 * s)
    return t

def conta(nome, loc, s=1.0):
    """Cartão da 'sua conta': avatar + fenda da licença + LED."""
    c = caixa(nome, loc, (1.5 * s, 0.14 * s, 1.9 * s), BRANCO); liso(c)
    cab = esfera(_id("avC"), (0, 0, 0), 0.25 * s, LARANJA, sub=2); filho(c, cab); cab.location = (0, -0.1 * s, 0.45 * s)
    cor = cilindro(_id("avT"), (0, 0, 0), 0.35 * s, 0.3 * s, LARANJA, seg=16, r2=0.15 * s); filho(c, cor); cor.location = (0, -0.1 * s, 0.05 * s)
    fe = caixa(_id("fenda"), (0, 0, 0), (0.9 * s, 0.04 * s, 0.14 * s), ESCURO); filho(c, fe); fe.location = (0, -0.09 * s, -0.5 * s)
    return c

def carimbo(nome, loc, s=1.0):
    v = vazio(nome, loc)
    b = caixa(_id("baseCar"), (0, 0, 0), (0.9 * s, 0.6 * s, 0.25 * s), VERMELHO); filho(v, b)
    m = cilindro(_id("caboCar"), (0, 0, 0), 0.12 * s, 0.7 * s, (0.45, 0.28, 0.14, 1), seg=10); filho(v, m); m.location = (0, 0, 0.45 * s)
    p = esfera(_id("puxCar"), (0, 0, 0), 0.22 * s, (0.45, 0.28, 0.14, 1), sub=2); filho(v, p); p.location = (0, 0, 0.85 * s)
    return v

def balcao(nome, x, y, larg=5.0):
    b = caixa(nome, (x, y, 0.55), (larg, 1.2, 1.1), (0.85, 0.45, 0.25, 1))
    caixa(_id("tampoB"), (x, y, 1.15), (larg + 0.2, 1.4, 0.1), BRANCO)
    for k in range(4):
        caixa(_id("frisoB"), (x - larg / 2 + 0.6 + k * (larg - 1.2) / 3, y - 0.62, 0.55), (0.12, 0.05, 0.9), AMARELO, unico="frisoB")
    return b

def prateleira_estojos(nome, x, y, z, n=8, s=0.55):
    caixa(nome, (x, y + 0.1, z - 0.42 * s * 1.35 - 0.05), (n * 0.62 * s * 1.6 + 0.4, 0.6, 0.1), (0.98, 0.84, 0.40, 1))
    for k in range(n):
        c = caixa(_id("estP"), (x + (k - (n - 1) / 2) * 0.62 * s * 1.6, y, z), (0.9 * s, 0.4 * s, 1.35 * s), CORES_CX[k % len(CORES_CX)], unico=f"estP{k % len(CORES_CX)}")
        liso(c)

import cartoon as _ct
_ct.PLANOS["geral"] = (7.4, 1.2, 0.3)   # plano geral um pouco mais perto (objetos maiores; Pixel ainda inteiro)
cam, alvo, cam_key, plano = camera_cartoon(24)
PX = 0.85   # escala do Pixel (inteiro em quadro nos planos gerais)

# =====================================================================
# ZONA A (x = 0) — loja/quarto: prateleira de estojos; estojo grande abre e só tem papel; disco com X; '200 MIL' (bloco 0) + CTA (bloco 7)
# =====================================================================
zona_ini()
t0, t1 = S[0]
sala("A", 0, (0.36, 0.40, 0.62, 1), (0.26, 0.30, 0.50, 1), (0.55, 0.38, 0.85, 1))
tdi = T(0, "disco"); tfa = T(0, "Famitsu"); tja = T(0, "Japão"); t200 = T(0, "duzentas"); tcx = T(0, "caixas"); tne = T(0, "nenhuma"); tdi2 = T(0, "disco", 1)
prateleira_estojos("pratA", 0.6, 3.6, 3.7, 9, 0.6)
caixa("mesaA", (0.8, 1.7, 1.0), (4.4, 1.3, 0.12), (0.30, 0.22, 0.18, 1))
for dx in (-1.9, 1.9): caixa(_id("peMesaA"), (0.8 + dx, 1.7, 0.48), (0.12, 1.0, 0.96), (0.18, 0.18, 0.22, 1))
bA, dA, lA = estojo("estA", (0.9, 1.7, 1.95), 1.25, CORES_CX[1])
abrir(dA, tne - 0.35, 0.5)
for c in lA: visivel(c, 0.0)
dsA = disco("discoA", (2.2, 1.2, 3.1), 0.8); visivel(dsA, tdi - 0.15, tne - 0.4); pop(dsA, tdi - 0.15, 1.0)
xA = xis("xA", (2.2, 1.0, 3.1), 1.1); visivel(xA, tdi + 0.2, tne - 0.4); pop(xA, tdi + 0.2, 1.0)
iqA = interroga("interA", (0.9, 1.3, 3.6), 0.8, AMARELO); visivel(iqA, 0.0, tfa - 0.2); pop(iqA, 0.05, 1.0)
t2 = texto3d("t200", "+200 MIL", (1.0, 1.4, 4.0), 0.75, AMARELO, 0.16); visivel(t2, t200 - 0.15, tne - 0.4); pop(t2, t200 - 0.15, 1.0)
for k in range(6):
    cx_ = caixa(_id("chegaA"), (0, 0, 0), (0.45, 0.18, 0.6), CORES_CX[k], unico=f"estP{k}")
    tt = tcx - 0.4 + 0.12 * k; visivel(cx_, tt, tne - 0.4)
    key(cx_, "location", tt, (-0.4 + 0.55 * k, 1.0, 6.5)); key(cx_, "location", tt + 0.45, (-0.4 + 0.55 * k, 1.0, 2.9 + 0.15 * (k % 2)))
xA2 = xis("xA2", (2.2, 1.0, 3.0), 1.0); visivel(xA2, tdi2 - 0.2, t1 + 0.3); pop(xA2, tdi2 - 0.2, 1.0)
dsA2 = disco("discoA2", (2.2, 1.2, 3.0), 0.75); visivel(dsA2, tne - 0.1, t1 + 0.3); pop(dsA2, tne - 0.1, 1.0)
# CTA (bloco 7): disco (esquerda) x nuvem digital (direita)
t7 = S[7][0]; tdsc = T(7, "disco", 1); tdig = T(7, "digital", 1)
dC = disco("discoCTA", (-0.6, 1.0, 3.3), 1.0); visivel(dC, tdsc - 0.3); pop(dC, tdsc - 0.3, 1.0)
nC = nuvemzinha("nuvemCTA", (1.8, 1.0, 3.4), 0.6); visivel(nC, tdig - 0.3); pop(nC, tdig - 0.3, 0.6)
for ob in (dC, nC): key(ob, "rotation_euler", t7, tuple(ob.rotation_euler))
px = pixel("pixel", (-1.2, 0.4, 0), escala=PX); girarZ(px["raiz"], 14); respirar(px, 0, FIM)
pensar(px, 0.05, 1.6); apontar(px, tfa - 0.1, 1.2, "D", 50); espanto(px, tne - 0.3, 1.3); apontar(px, tdi2 - 0.1, 1.0, "D", 20)
acenar(px, t7 + 0.1, 1.4); apontar(px, tdsc - 0.2, 1.2, "D", 40); apontar(px, tdig - 0.2, 1.2, "D", 60)
acenar(px, LEG[-1]["e"] + 1.2, 1.6); comemorar(px, LEG[-1]["e"] + 3.0, 1.4)
plano(0, (0.3, 1.8), "geral", altura=2.2); plano(tcx - 0.5, (0.35, 1.8), "geral", altura=2.3)
plano(tne - 0.4, (0.3, 1.8), "geral", altura=2.1); plano(t1 - 0.05, (0.3, 1.8), "geral", altura=2.1)
cam_key(t7, (0.3, -6.0, 3.4), (0.3, 1.6, 2.4)); cam_key(FIM, (0.4, -5.8, 3.4), (0.4, 1.6, 2.4))
zona_fim([(0.0, t1 + 0.3), (t7 - 0.3, FIM + 0.5)])

# =====================================================================
# ZONA B (x = 40) — estojo grande aberto; o código brilha; '=' controle (o jogo inteiro) (bloco 1)
# =====================================================================
zona_ini()
t0, t1 = S[1]
sala("B", 40, (0.95, 0.80, 0.45, 1), (0.70, 0.52, 0.28, 1), (0.25, 0.30, 0.55, 1))
tpa = T(1, "papel"); tco = T(1, "código"); tva = T(1, "vale"); tji = T(1, "inteiro")
caixa("mesaB", (40.6, 1.8, 0.5), (5.6, 1.6, 1.0), (0.30, 0.22, 0.18, 1))
bB, dB, lB = estojo("estB", (40.2, 1.8, 2.1), 1.3, CORES_CX[1])
key(dB, "rotation_euler", t0 - 0.3, (0, 0, math.radians(-175)))
mC = mat(CIANO, "codigoB")
for k, c in enumerate(lB):
    c.data.materials[0] = mC
BRILHO.append(mC)
cor_key(mC, tco - 0.3, (0.35, 0.45, 0.55, 1)); cor_key(mC, tco + 0.3, (0.25, 1.0, 1.0, 1))
anB = anel("haloB", (40.2, 1.58, 2.25), 0.65, 0.05, AMARELO, seg=28, unico="halo"); anB.rotation_euler = (math.radians(90), 0, 0); BRILHO.append(mat(AMARELO, "halo"))
visivel(anB, tco - 0.1); pop(anB, tco - 0.1, 1.0)
igual = texto3d("igualB", "=", (41.35, 1.6, 2.2), 1.0, AMARELO, 0.16); visivel(igual, tva - 0.15); pop(igual, tva - 0.15, 1.0)
ctl = controle("ctlB", (42.3, 1.6, 2.2), 0.85); visivel(ctl, tji - 0.4); pop(ctl, tji - 0.4, 1.1)
gB = pixel("guiaB", (38.6, 0.3, 0), escala=PX); girarZ(gB["raiz"], 20); respirar(gB, t0, t1 + 0.5)
apontar(gB, tpa - 0.1, 1.3, "D", 40); apontar(gB, tco - 0.1, 1.2, "D", 60); comemorar(gB, tji - 0.2, 1.3)
plano(t0, (40.4, 1.8), "geral", altura=2.0); plano(t1 - 0.05, (40.45, 1.8), "geral", altura=2.0)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA C (x = 80) — Pixel digita (controle + tela com letras); envelope voa até o servidor com cadeado (bloco 2)
# =====================================================================
zona_ini()
t0, t1 = S[2]
sala("C", 80, (0.62, 0.72, 0.98, 1), (0.36, 0.46, 0.80, 1), (0.30, 0.20, 0.45, 1))
tch = T(2, "chave"); tle = T(2, "letras"); tdg = T(2, "digita"); tvi = T(2, "viaja"); tsv = T(2, "servidor"); tlj = T(2, "loja")
caixa("rackC", (79.2, 2.2, 0.45), (3.0, 1.2, 0.9), (0.30, 0.22, 0.18, 1))
tv = tela("telaC", (79.2, 2.4, 2.25), 1.0)
cs = console("consC", (80.3, 2.0, 1.35), 0.55)
chC = chave("chaveC", (79.2, 2.1, 3.5), 1.2); visivel(chC, tch - 0.15, tdg - 0.1); pop(chC, tch - 0.15, 1.2)
letC = codigo("letC", (79.2, 2.28, 2.25), 2.4, 6, "codigo")
for k, c in enumerate(letC):
    tt = tle - 0.1 + 0.15 * k; visivel(c, tt, tvi + 0.1); pop(c, tt, 1.0, 0.2)
srv = servidor("srvC", (82.0, 2.4, 1.3), 1.1); srv2 = servidor("srvC2", (83.3, 3.4, 1.3), 1.1)
cdC, alC = cadeado("cadC", (82.0, 2.0, 3.2), 0.9)
env = envelope("envC", (79.2, 1.9, 2.25), 0.9); visivel(env, tvi - 0.05)
pop(env, tvi - 0.05, 0.9, 0.25)
caminho(env, tvi + 0.2, tsv + 0.6, lambda u: bez((78.6, 1.9, 2.25), (80.4, 1.4, 4.2), (82.0, 1.6, 2.2), u), orientar=False, passo=2)
for k in range(8):
    e = esfera(_id("rastroC"), (0, 0, 0), 0.07, CIANO, sub=1, unico="codigo"); a = tvi + 0.25 + 0.1 * k; visivel(e, a, a + 0.6)
    caminho(e, a, a + 0.6, lambda u: bez((78.6, 1.9, 2.25), (80.4, 1.4, 4.2), (82.0, 1.6, 2.2), u), orientar=False, passo=3)
ctlC = controle("ctlC", (0, 0, 0), 0.5)
gC = pixel("guiaC", (78.0, 0.3, 0), escala=PX); girarZ(gC["raiz"], 20); respirar(gC, t0, t1 + 0.5)
filho(gC["raiz"], ctlC); ctlC.location = (0.35, -0.45, 1.25)
apontar(gC, tch - 0.1, 1.2, "D", 60); pensar(gC, tdg - 0.1, 1.3); apontar(gC, tvi - 0.1, 1.4, "D", 40); comemorar(gC, tlj - 0.2, 1.2)
plano(t0, (79.8, 2.0), "geral", altura=2.2); plano(tvi - 0.3, (79.85, 2.0), "geral", altura=2.2); plano(t1 - 0.05, (79.9, 2.0), "geral", altura=2.3)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA D (x = 120) — servidor confere 2 coisas (lâmpadas com check), carimbo USADO, chave dourada entra na conta (bloco 3)
# =====================================================================
zona_ini()
t0, t1 = S[3]
sala("D", 120, (0.40, 0.30, 0.55, 1), (0.28, 0.20, 0.42, 1), (0.16, 0.22, 0.40, 1))
tdu = T(3, "duas"); tex = T(3, "existe"); tni = T(3, "ninguém"); tai = T(3, "ainda"); tce = T(3, "certo"); tca = T(3, "carimba")
tus = T(3, "usada"); tgr = T(3, "grava"); tli = T(3, "licença"); tct = T(3, "conta")
servidor("srvD", (122.0, 2.8, 1.4), 1.3); cadeado("cadD", (122.0, 2.4, 3.6), 0.9)
caixa("mesaD", (120.9, 1.6, 0.5), (2.6, 1.4, 1.0), (0.55, 0.60, 0.70, 1))
envD = envelope("envD", (120.9, 1.5, 1.05), 1.0); envD.rotation_euler = (math.radians(-80), 0, 0)
for k, (tt, z) in enumerate(((tex, 3.9), (tai, 3.1))):
    ld, ml = led(f"ledD{k}", (122.0, 1.95, z - 0.9), CINZA, 0.22); BRILHO.append(ml)
    cor_key(ml, t0, (0.45, 0.47, 0.52, 1), "CONSTANT"); cor_key(ml, tt, VERDE, "CONSTANT")
    ck = check(_id("ckD"), (122.9, 1.8, z - 0.95), 0.55); visivel(ck, tt); pop(ck, tt, 0.55)
car = carimbo("carD", (120.9, 1.5, 3.4), 1.0)
key(car, "location", t0, (120.9, 1.5, 3.4)); key(car, "location", tca - 0.15, (120.9, 1.5, 3.4)); key(car, "location", tca + 0.15, (120.9, 1.5, 1.25))
key(car, "location", tca + 0.6, (120.9, 1.5, 1.25)); key(car, "location", tus + 0.6, (121.3, 1.5, 3.8))
usd = texto3d("usadoD", "USADO", (120.9, 0.85, 1.35), 0.42, VERMELHO, 0.06); visivel(usd, tca + 0.15); pop(usd, tca + 0.15, 1.0, 0.2)
ctD = conta("contaD", (118.0, 2.3, 3.05), 1.0)
chD = chave("chaveD", (120.9, 1.4, 2.0), 1.0); visivel(chD, tgr - 0.3)
key(chD, "location", tgr - 0.3, (121.0, 1.4, 2.6)); key(chD, "location", tct, (118.5, 2.1, 2.6)); key(chD, "location", tct + 0.4, (118.2, 2.15, 2.6))
mFen = mat(VERDE, "brilhoConta"); BRILHO.append(mFen)
fen = caixa("fendaLuz", (118.0, 2.18, 2.55), (1.0, 0.02, 0.22), VERDE, unico="brilhoConta"); visivel(fen, tct + 0.3); pop(fen, tct + 0.3, 1.0, 0.2)
ckC = check("ckConta", (119.3, 1.9, 3.6), 0.7); visivel(ckC, tct + 0.3); pop(ckC, tct + 0.3, 0.7)
gD = pixel("guiaD", (119.2, 0.3, 0), escala=PX); girarZ(gD["raiz"], 20); respirar(gD, t0, t1 + 0.5)
apontar(gD, tdu - 0.1, 1.3, "D", 60); apontar(gD, tni - 0.1, 1.2, "D", 70); espanto(gD, tca - 0.1, 1.1); comemorar(gD, tct, 1.3)
plano(t0, (120.25, 2.0), "geral", altura=2.2); plano(t1 - 0.05, (120.15, 2.0), "geral", altura=2.2)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA E (x = 160) — nuvem -> download para o console (barra enche); disco com X; barras 90% digital x disco (bloco 4)
# =====================================================================
zona_ini()
t0, t1 = S[4]
sala("E", 160, (0.85, 0.88, 0.95, 1), (0.50, 0.56, 0.72, 1), (0.20, 0.45, 0.55, 1))
tba = T(4, "baixa"); tin = T(4, "internet"); tds = T(4, "disco"); tch5 = T(4, "chefe"); tme = T(4, "mercado"); t90 = T(4, "noventa"); tdgt = T(4, "digital")
nuv = nuvemzinha("nuvemE", (158.4, 2.4, 4.6), 1.0)
caixa("rackE", (158.4, 2.2, 0.45), (2.6, 1.2, 0.9), (0.30, 0.22, 0.18, 1))
cE = console("consE", (158.4, 2.0, 1.65), 0.8)
particulas("downE", 14, t0, tds, (158.4, 1.8, 4.0), (158.0, 1.7, 3.0), (158.4, 1.6, 2.1), CIANO, "codigo", r=0.1, dur=0.9)
mbE, prog, mpE = barra("progE", 157.2, 1.4, 0.95, 0.9, 0.18, VERDE)
prog.rotation_euler = (0, math.radians(90), 0); mbE.rotation_euler = (0, math.radians(90), 0)
mbE.location = (158.4, 1.45, 1.0); prog.location = (157.95, 1.38, 1.0)
encher(prog, t0, tba - 0.1, 0.02, 0.02); encher(prog, tba - 0.1, tds - 0.2, 0.02, 1.0)
dsE = disco("discoE", (160.2, 1.6, 2.4), 0.7); visivel(dsE, tds - 0.4, tch5 - 0.2); pop(dsE, tds - 0.4, 1.0)
xE = xis("xE", (160.2, 1.4, 2.4), 1.0); visivel(xE, tds - 0.1, tch5 - 0.2); pop(xE, tds - 0.1, 1.0)
mbD, bDig, mDig = barra("barDig", 160.0, 2.2, 0.3, 3.4, 0.8, CIANO)
mbF, bFis, mFis = barra("barFis", 161.2, 2.2, 0.3, 3.4, 0.8, CINZA)
for ob in (mbD, bDig, mbF, bFis): visivel(ob, tch5 - 0.2)
encher(bDig, tme - 0.2, t90 + 0.4, 0.01, 0.92); encher(bFis, tme - 0.2, t90 + 0.4, 0.01, 0.08)
nuP = nuvemzinha("nuvP", (160.0, 1.9, 4.3), 0.35); visivel(nuP, tch5 - 0.2)
dsP = disco("discoP", (161.2, 1.9, 4.3), 0.4); visivel(dsP, tch5 - 0.2)
t90x = texto3d("t90", "90%", (160.0, 1.5, 2.2), 0.6, BRANCO, 0.14); visivel(t90x, t90 - 0.1); pop(t90x, t90 - 0.1, 1.0)
gE = pixel("guiaE", (157.4, 0.3, 0), escala=PX); girarZ(gE["raiz"], 14); respirar(gE, t0, t1 + 0.5)
apontar(gE, tba - 0.1, 1.3, "D", 70); apontar(gE, tds - 0.2, 1.2, "D", 40); pensar(gE, tch5 - 0.1, 1.4); comemorar(gE, t90 - 0.1, 1.3)
plano(t0, (159.0, 2.0), "geral", altura=2.4); plano(t1 - 0.05, (159.05, 2.0), "geral", altura=2.4)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA F (x = 200) — risco: 2 envelopes correm, o 1º leva a chave e o 2º leva X; 3 estojos: aberto com '!', vazio '?', USADO; balão '...' (bloco 5)
# =====================================================================
zona_ini()
t0, t1 = S[5]
sala("F", 200, (0.42, 0.46, 0.62, 1), (0.28, 0.32, 0.46, 1), (0.40, 0.28, 0.58, 1))
tri = T(5, "risco"); tso = T(5, "sozinho"); tre = T(5, "resgata"); tpr = T(5, "primeiro"); tle5 = T(5, "leva"); tcp = T(5, "Compradores")
tvs = T(5, "visível"); tou = T(5, "outras"); tus5 = T(5, "usado"); trk = T(5, "Rockstar"); tcm = T(5, "comentou")
servidor("srvF", (202.4, 2.7, 1.4), 1.2)
excF = texto3d("excF", "!", (200.0, 1.4, 4.2), 1.4, VERMELHO, 0.2); visivel(excF, t0); pop(excF, t0 + 0.05, 1.0)
for k, (cor, dz) in enumerate(((VERDE, 0.6), (VERMELHO, -0.6))):
    e = envelope(_id("envF"), (198.9, 1.6, 2.4 + dz), 0.7); visivel(e, t0, tcp - 0.3)
    ini = tre - 0.2 + 0.7 * k; fim = ini + 1.0
    key(e, "location", ini, (198.9, 1.6, 2.4 + dz)); key(e, "location", fim, (201.5, 1.6, 2.4 + dz))
    if k == 0:
        chF = chave("chaveF", (202.0, 1.3, 3.0), 0.8); visivel(chF, tle5 - 0.1, tcp - 0.3); pop(chF, tle5 - 0.1, 0.9)
    else:
        xF = xis("xF", (202.0, 1.3, 1.8), 0.8); visivel(xF, tle5 + 0.3, tcp - 0.3); pop(xF, tle5 + 0.3, 1.0)
# três estojos: (1) fechado com '!' acima, (2) aberto sem papel '?', (3) aberto com papel USADO
caixa("mesaF", (200.2, 1.8, 0.5), (6.2, 1.5, 1.0), (0.30, 0.22, 0.18, 1))
E1 = estojo("estF1", (199.2, 1.8, 1.75), 0.85, CORES_CX[2], papel=True)
E2 = estojo("estF2", (200.6, 1.8, 1.75), 0.85, CORES_CX[3], papel=False)
E3 = estojo("estF3", (202.0, 1.8, 1.75), 0.85, CORES_CX[4], papel=True)
for E, tt in ((E2, tou), (E3, tus5 - 0.4)): abrir(E[1], tt - 0.3, 0.45)
key(E1[1], "rotation_euler", t0, (0, 0, 0))
ESTF = []
for E in (E1, E2, E3):
    ESTF.append(E[0])
em1 = texto3d("excF1", "!", (199.2, 1.6, 3.2), 0.9, AMARELO, 0.14); visivel(em1, tvs - 0.2); pop(em1, tvs - 0.2, 1.0)
for c in E1[2]:
    mV = mat(CIANO, "codVis"); c.data.materials[0] = mV
BRILHO.append(mat(CIANO, "codVis"))
iq2 = interroga("interF2", (200.6, 1.6, 3.2), 0.55, AMARELO); visivel(iq2, tou); pop(iq2, tou, 1.0)
usF = texto3d("usadoF", "USADO", (202.0, 1.6, 1.75), 0.26, VERMELHO, 0.05); visivel(usF, tus5 - 0.1); pop(usF, tus5 - 0.1, 1.0, 0.2)
bal = balao("balaoF", (201.6, 1.0, 4.1), 0.7); visivel(bal, trk - 0.1)
bal.scale = (0.001,) * 3; bal.keyframe_insert("scale", frame=f(trk - 0.1)); bal.scale = (1.25, 0.35, 0.9); bal.keyframe_insert("scale", frame=f(trk + 0.25))
gF = pixel("guiaF", (198.3, 0.3, 0), escala=PX); girarZ(gF["raiz"], 14); respirar(gF, t0, t1 + 0.5)
espanto(gF, tri - 0.1, 1.2); apontar(gF, tre - 0.1, 1.4, "D", 40); apontar(gF, tvs - 0.2, 1.2, "D", 30)
apontar(gF, tou - 0.1, 1.2, "D", 40); espanto(gF, tus5 - 0.1, 1.2); pensar(gF, trk - 0.1, 2.0)
for o in [E1[0], E2[0], E3[0], bpy.data.objects["mesaF"]]:
    visivel(o, tcp - 0.35)
for E in (E1, E2, E3):
    for o in list(todos(E[1])) + E[2]: visivel(o, tcp - 0.35)
for o in bpy.data.objects:
    if o.name.startswith(("papel", "linhaP")) and abs(o.location.x - 200) < 4 and o.location.y > 1.5: visivel(o, tcp - 0.35)
plano(t0, (200.1, 2.0), "geral", altura=2.4); plano(tcp - 0.4, (200.1, 2.0), "geral", altura=2.4)
plano(tcp - 0.3, (200.15, 1.8), "geral", altura=2.2); plano(t1 - 0.05, (200.2, 1.8), "geral", altura=2.3)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA G (x = 240) — balcão da loja: Pixel abre o estojo ali mesmo e confere o código (check) (bloco 6)
# =====================================================================
zona_ini()
t0, t1 = S[6]
sala("G", 240, (0.45, 0.75, 0.55, 1), (0.30, 0.56, 0.40, 1), (0.95, 0.55, 0.25, 1))
tdc = T(6, "dica"); tab = T(6, "abra"); tlj6 = T(6, "loja"); tcf = T(6, "confira"); tho = T(6, "hora")
prateleira_estojos("pratG", 240.4, 3.8, 3.9, 9, 0.6)
balcao("balcaoG", 240.8, 1.9, 5.0)
reg = caixa("caixaReg", (242.6, 2.0, 1.55), (1.0, 0.8, 0.7), (0.30, 0.32, 0.38, 1)); liso(reg)
telaR = caixa("telaReg", (242.6, 1.7, 2.1), (0.8, 0.08, 0.45), (0.2, 0.9, 0.6, 1), unico="telaReg"); BRILHO.append(mat((0.2, 0.9, 0.6, 1), "telaReg"))
bG, dG, lG = estojo("estG", (240.4, 1.8, 1.95), 1.0, CORES_CX[0])
abrir(dG, tab - 0.1, 0.5)
anG = anel("haloG", (240.4, 1.6, 2.05), 0.6, 0.05, AMARELO, seg=28, unico="halo"); anG.rotation_euler = (math.radians(90), 0, 0)
visivel(anG, tcf - 0.1); pop(anG, tcf - 0.1, 1.0)
ckG = check("checkG", (240.4, 1.5, 3.4), 1.0); visivel(ckG, tho - 0.2); pop(ckG, tho - 0.2, 1.0)
lpG = interroga("lupaG", (239.4, 1.5, 3.4), 0.5, BRANCO); visivel(lpG, tdc - 0.1, tab); pop(lpG, tdc - 0.1, 1.0)
gG = pixel("guiaG", (238.5, 0.3, 0), escala=PX); girarZ(gG["raiz"], 10); respirar(gG, t0, t1 + 0.5)
acenar(gG, tdc - 0.2, 1.0); apontar(gG, tab - 0.1, 1.2, "D", 30); apontar(gG, tcf - 0.1, 1.2, "D", 40); comemorar(gG, tho, 1.2)
plano(t0, (240.2, 1.9), "geral", altura=2.2); plano(t1 - 0.05, (240.25, 1.9), "geral", altura=2.2)
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
