"""Série 2 — 'GTA 6: 10 anos para gravar Jason e Lucia?' (notícia 28/11; estilo C cartoon, mascote Pixel, visual nível 2).
Mecanismo: como se grava um personagem — o Pixel de roupa de captura (preta com bolinhas brancas), o 'volume' cercado
de câmeras em tripés e na treliça, raios até as bolinhas, esqueleto digital na tela imitando o aceno; capacete com
câmera no rosto + microfone de vara; por que leva anos (pilha de roteiros, claquete batendo, calendário soltando
folhas); NDA (contrato com cadeado, balão com X, martelo); créditos rolando. SEM foto/rosto dos atores e sem arte,
personagem ou logo da Rockstar: só objetos genéricos. Base: cena_gta6_caixa.py (zonas por bloco).
Uso: blender -b --factory-startup -P cena_gta6_mocap.py -- <pasta> [preview t1,t2 | range a,b]"""
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
random.seed(28)

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
from mathutils import Vector
TRAJE = (0.09, 0.10, 0.13, 1); MARC = (0.96, 0.97, 1.0, 1)
BRILHO.append(mat(MARC, "marcador")); BRILHO.append(mat(VERMELHO, "ledCam")); BRILHO.append(mat(CIANO, "esq"))
BRILHO.append(mat((1.0, 0.35, 0.30, 1), "raio")); BRILHO.append(mat(CIANO, "volume")); BRILHO.append(mat(VERDE, "pontoRosto"))

MARC_POS = [("raiz", (0, -0.38, 1.72)), ("raiz", (-0.26, -0.33, 1.86)), ("raiz", (0.26, -0.33, 1.86)), ("raiz", (0, -0.38, 1.32)),
            ("raiz", (-0.30, -0.30, 1.05)), ("raiz", (0.30, -0.30, 1.05)),
            ("ombroE", (0, -0.14, -0.05)), ("ombroD", (0, -0.14, -0.05)), ("ombroE", (0, -0.15, -0.32)), ("ombroD", (0, -0.15, -0.32)),
            ("cotoveloE", (0, -0.13, 0.0)), ("cotoveloD", (0, -0.13, 0.0)), ("cotoveloE", (0, -0.12, -0.38)), ("cotoveloD", (0, -0.12, -0.38)),
            ("pernaE", (0, -0.21, -0.45)), ("pernaD", (0, -0.21, -0.45)), ("pernaE", (0, -0.24, -0.85)), ("pernaD", (0, -0.24, -0.85)),
            ("cabeca", (0, -0.05, 1.18)), ("cabeca", (-0.5, -0.25, 0.85)), ("cabeca", (0.5, -0.25, 0.85))]

def pixel_mocap(nome, loc, t_marc=None, dt=0.06, escala=0.85):
    """Pixel de roupa de captura (preta) com bolinhas brancas. t_marc: bolinhas nascem uma a uma a partir de t_marc."""
    P = pixel(nome, loc, moletom=TRAJE, calca=TRAJE, escala=escala)
    M = []
    for k, (pai, p) in enumerate(MARC_POS):
        e = esfera(_id("marc"), (0, 0, 0), 0.065, MARC, sub=2, unico="marcador"); filho(P[pai], e); e.location = p; M.append(e)
        if t_marc is not None:
            pop(e, t_marc + dt * k, 1.0, 0.25)
    P["marc"] = M
    return P

def osso(nome, a, b, r, cor, unico):
    a = Vector(a); b = Vector(b); d = b - a
    c = cilindro(nome, tuple((a + b) / 2), r, d.length, cor, seg=8, unico=unico)
    c.rotation_mode = "QUATERNION"; c.rotation_quaternion = d.to_track_quat("Z", "Y")
    return c

def cam_mocap(nome, loc, mirar, h=2.2, tripe=True):
    """Câmera de captura genérica (caixa + lente + anel vermelho) num tripé, girada para 'mirar'."""
    x, y = loc[0], loc[1]; z0 = loc[2] if len(loc) > 2 else 0
    v = vazio(nome, (x, y, z0))
    if tripe:
        for k in range(3):
            a = math.radians(90 + k * 120)
            pe = osso(_id("pe"), (0.45 * math.cos(a), 0.45 * math.sin(a), 0), (0, 0, h * 0.55), 0.035, CINZA, "tripe"); filho(v, pe)
        m = cilindro(_id("mastro"), (0, 0, h * 0.75), 0.04, h * 0.5, CINZA, seg=8, unico="tripe"); filho(v, m); m.location = (0, 0, h * 0.75)
    cab = caixa(_id("camCab"), (0, 0, 0), (0.34, 0.30, 0.26), ESCURO); filho(v, cab); cab.location = (0, 0, h); liso(cab)
    le = cilindro(_id("lente"), (0, 0, 0), 0.09, 0.12, (0.2, 0.22, 0.28, 1), seg=14); filho(v, le); le.location = (0, -0.2, h); le.rotation_euler = (math.radians(90), 0, 0)
    an = anel(_id("anelCam"), (0, 0, 0), 0.13, 0.03, VERMELHO, seg=18, unico="ledCam"); filho(v, an); an.location = (0, -0.27, h); an.rotation_euler = (math.radians(90), 0, 0)
    dx, dy = mirar[0] - x, mirar[1] - y
    v.rotation_euler = (0, 0, math.atan2(dx, -dy))
    return v, (x, y, z0 + h)

def capacete(P):
    """Capacete com câmera na frente do rosto (preso ao pivô da cabeça) + pontinhos verdes no rosto."""
    c = P["cabeca"]; L = []
    h = esfera(_id("capacete"), (0, 0, 0), 0.64, (0.20, 0.22, 0.28, 1), sub=3); filho(c, h); h.location = (0, 0.04, 0.82); h.scale = (1.02, 1.0, 0.62); liso(h); L.append(h)
    braco = caixa(_id("hasteHMC"), (0, 0, 0), (0.06, 0.62, 0.06), CINZA); filho(c, braco); braco.location = (0, -0.62, 1.12); L.append(braco)
    desce = caixa(_id("hasteHMC2"), (0, 0, 0), (0.06, 0.06, 0.32), CINZA); filho(c, desce); desce.location = (0, -0.92, 0.98); L.append(desce)
    cm = caixa(_id("camHMC"), (0, 0, 0), (0.2, 0.14, 0.14), ESCURO); filho(c, cm); cm.location = (0, -0.92, 0.80); L.append(cm)
    led_ = esfera(_id("ledHMC"), (0, 0, 0), 0.04, VERMELHO, sub=1, unico="ledCam"); filho(c, led_); led_.location = (0.07, -0.99, 0.84); L.append(led_)
    for p in ((-0.3, -0.48, 0.42), (0.3, -0.48, 0.42), (-0.18, -0.55, 0.30), (0.18, -0.55, 0.30), (0, -0.56, 0.74), (-0.36, -0.44, 0.62), (0.36, -0.44, 0.62)):
        d = esfera(_id("ptR"), (0, 0, 0), 0.032, VERDE, sub=1, unico="pontoRosto"); filho(c, d); d.location = p; L.append(d)
    return L

def boneco(nome, base, s=1.0):
    """Esqueleto digital (bolinhas + ossos ciano) em pé no plano XZ; braço direito num pivô animável."""
    bx, by, bz = base; R = 0.035 * s
    J = {"cab": (0, 1.75), "pes": (0, 1.5), "pel": (0, 0.95), "omE": (-0.28, 1.45), "omD": (0.28, 1.45), "coE": (-0.42, 1.12),
         "maE": (-0.48, 0.82), "joE": (-0.16, 0.5), "joD": (0.16, 0.5), "peE": (-0.18, 0.05), "peD": (0.18, 0.05), "quE": (-0.14, 0.95), "quD": (0.14, 0.95)}
    W = lambda k: (bx + J[k][0] * s, by, bz + J[k][1] * s)
    root = vazio(nome, (bx, by, bz)); obs = []
    for a, b in (("pes", "pel"), ("omE", "omD"), ("omE", "coE"), ("coE", "maE"), ("quE", "quD"), ("quE", "joE"), ("joE", "peE"), ("quD", "joD"), ("joD", "peD")):
        obs.append(osso(_id("osso"), W(a), W(b), R, CIANO, "esq"))
    for k in J:
        if k != "cab": obs.append(esfera(_id("junta"), W(k), R * 2.0, CIANO, sub=1, unico="esq"))
    obs.append(esfera(_id("cabEsq"), W("cab"), 0.17 * s, CIANO, sub=2, unico="esq"))
    piv = vazio(_id("pivEsq"), W("omD")); obs2 = []
    o1 = osso(_id("osso"), W("omD"), (W("omD")[0] + 0.14 * s, by, W("omD")[2] - 0.33 * s), R, CIANO, "esq")
    o2 = osso(_id("osso"), (W("omD")[0] + 0.14 * s, by, W("omD")[2] - 0.33 * s), (W("omD")[0] + 0.2 * s, by, W("omD")[2] - 0.63 * s), R, CIANO, "esq")
    j1 = esfera(_id("junta"), (W("omD")[0] + 0.14 * s, by, W("omD")[2] - 0.33 * s), R * 2, CIANO, sub=1, unico="esq")
    j2 = esfera(_id("junta"), (W("omD")[0] + 0.2 * s, by, W("omD")[2] - 0.63 * s), R * 2, CIANO, sub=1, unico="esq")
    for o in (o1, o2, j1, j2):
        o.parent = piv; o.location = tuple(Vector(o.location) - Vector(piv.location))
    for o in obs + [piv]:
        o.parent = root; o.location = tuple(Vector(o.location) - Vector(root.location))
    return root, piv

def onda_braco(piv, t, dur=1.4):
    """Braço do esqueleto sobe e acena (gira em Y = plano da tela)."""
    key(piv, "rotation_euler", t, (0, 0, 0)); key(piv, "rotation_euler", t + 0.25, (0, math.radians(-150), 0))
    for k in range(3):
        key(piv, "rotation_euler", t + 0.4 + 0.3 * k, (0, math.radians(-125), 0)); key(piv, "rotation_euler", t + 0.55 + 0.3 * k, (0, math.radians(-170), 0))
    key(piv, "rotation_euler", t + dur, (0, 0, 0))

def claquete(nome, loc, s=1.0):
    x, y, z = loc
    b = caixa(nome, (x, y, z), (1.2 * s, 0.1 * s, 0.8 * s), ESCURO)
    for k in range(3):
        caixa(_id("linCl"), (x, y - 0.06 * s, z - 0.15 * s + 0.2 * s * (k - 1)), (0.9 * s, 0.01 * s, 0.05 * s), BRANCO, unico="linCl")
    dob = vazio(_id("dobCl"), (x - 0.6 * s, y, z + 0.42 * s))
    tp = caixa(_id("topoCl"), (0, 0, 0), (1.2 * s, 0.1 * s, 0.18 * s), BRANCO); filho(dob, tp); tp.location = (0.6 * s, 0, 0.09 * s)
    for k in range(4):
        st = caixa(_id("listra"), (0, 0, 0), (0.14 * s, 0.11 * s, 0.19 * s), ESCURO, unico="listraCl"); filho(dob, st); st.location = ((0.15 + 0.3 * k) * s, 0, 0.09 * s); st.rotation_euler = (0, math.radians(30), 0)
    return b, dob

def bater(dob, t):
    key(dob, "rotation_euler", t, (0, math.radians(-30), 0)); key(dob, "rotation_euler", t + 0.12, (0, 0, 0), "CONSTANT")

def calendario(nome, loc, s=1.0, cor=VERMELHO):
    x, y, z = loc
    b = caixa(nome, (x, y, z), (1.2 * s, 0.12 * s, 1.3 * s), BRANCO); liso(b)
    caixa(_id("topoCal"), (x, y - 0.02, z + 0.55 * s), (1.22 * s, 0.14 * s, 0.3 * s), cor)
    for i in range(3):
        for j in range(3):
            caixa(_id("diaCal"), (x + (i - 1) * 0.32 * s, y - 0.07 * s, z + (0.12 - j * 0.28) * s), (0.2 * s, 0.01 * s, 0.16 * s), (0.75, 0.77, 0.82, 1), unico="diaCal")
    return b

def folhas_voando(nome, loc, t0, n, intervalo=0.25, s=1.0):
    x, y, z = loc
    for k in range(n):
        fl = caixa(_id(nome), (x, y - 0.1, z), (1.1 * s, 0.03, 1.0 * s), BRANCO, unico="folhaCal")
        a = t0 + intervalo * k; visivel(fl, a, a + 1.0)
        key(fl, "location", a, (x, y - 0.1, z)); key(fl, "location", a + 1.0, (x + random.uniform(-1.6, 1.6), y - 0.8, z + 1.8))
        key(fl, "rotation_euler", a, (0, 0, 0)); key(fl, "rotation_euler", a + 1.0, (random.uniform(-1, 1), random.uniform(-2, 2), random.uniform(-1, 1)))

def tela_creditos(nome, x, y, z, w=3.2, h=2.2, t0=0.0, t1=10.0, ouro=(), n=12):
    """Tela escura com 'linhas de créditos' (barras) subindo; índices em 'ouro' ficam dourados."""
    caixa(nome, (x, y, z), (w + 0.2, 0.15, h + 0.2), (0.25, 0.25, 0.30, 1))
    caixa(_id("telaCred"), (x, y - 0.09, z), (w, 0.02, h), (0.04, 0.04, 0.07, 1))
    BRILHO.append(mat(OURO, "credOuro")); BRILHO.append(mat((0.85, 0.87, 0.92, 1), "credLin"))
    vel = (h + 1.0) / max(0.5, (t1 - t0)) * 0.9
    for k in range(n):
        larg = random.uniform(0.9, 1.9) if k not in ouro else 2.2
        ob = caixa(_id("cred"), (x, y - 0.12, z), (larg, 0.02, 0.1), OURO if k in ouro else (0.85, 0.87, 0.92, 1), unico="credOuro" if k in ouro else "credLin")
        za = z - h / 2 - 0.1 - 0.32 * k; zb = za + vel * (t1 - t0)
        # só aparece dentro da tela
        ent = t0 + max(0.0, (z - h / 2 - za) / vel); sai = t0 + max(0.0, (z + h / 2 - za) / vel)
        if ent >= t1: bpy.data.objects.remove(ob); continue
        key(ob, "location", t0, (x, y - 0.12, za), "LINEAR"); key(ob, "location", t1, (x, y - 0.12, zb), "LINEAR")
        visivel(ob, ent, min(sai, t1 + 0.4))

def contrato(nome, loc, s=1.0):
    x, y, z = loc
    p = caixa(nome, (x, y, z), (1.5 * s, 0.06 * s, 2.0 * s), BRANCO)
    for k in range(6):
        caixa(_id("linCt"), (x, y - 0.04 * s, z + (0.25 - 0.2 * k) * s), (1.1 * s, 0.01, 0.05 * s), (0.6, 0.62, 0.68, 1), unico="linCt")
    caixa(_id("assin"), (x + 0.3 * s, y - 0.04 * s, z - 0.8 * s), (0.6 * s, 0.01, 0.04 * s), AZUL)
    return p

def martelo(nome, loc, s=1.0):
    x, y, z = loc
    base = cilindro(_id("baseMart"), (x + 0.5 * s, y, z - 0.05), 0.35 * s, 0.12 * s, (0.45, 0.28, 0.14, 1), seg=16)
    piv = vazio(nome, (x - 0.5 * s, y, z + 0.2 * s))
    cabo = caixa(_id("caboMart"), (0, 0, 0), (1.0 * s, 0.08 * s, 0.08 * s), (0.55, 0.35, 0.18, 1)); filho(piv, cabo); cabo.location = (0.5 * s, 0, 0)
    cab = cilindro(_id("cabMart"), (0, 0, 0), 0.15 * s, 0.5 * s, (0.45, 0.28, 0.14, 1), seg=14); filho(piv, cab); cab.location = (1.0 * s, 0, 0)
    return piv, base

def microfone_vara(nome, x, y, s=1.0):
    pe = cilindro(nome, (x, y + 0.6, 1.6 * s), 0.04, 3.2 * s, CINZA, seg=8)
    vara = osso(_id("vara"), (x, y + 0.6, 3.2 * s), (x - 1.4 * s, y - 0.1, 3.4 * s), 0.035, CINZA, "tripe")
    mic = cilindro(_id("micV"), (x - 1.5 * s, y - 0.2, 3.25 * s), 0.11 * s, 0.5 * s, ESCURO, seg=12); mic.rotation_euler = (math.radians(70), 0, 0)
    esp = esfera(_id("espuma"), (x - 1.5 * s, y - 0.35, 3.2 * s), 0.16 * s, (0.35, 0.36, 0.42, 1), sub=2); esp.scale = (1, 1.6, 1); liso(esp)
    return pe, mic

def tela(nome, loc, s=1.0, cor=(0.15, 0.55, 0.95, 1)):
    t = caixa(nome, loc, (2.4 * s, 0.14 * s, 1.4 * s), ESCURO)
    m = caixa(_id("telaM"), (0, 0, 0), (2.2 * s, 0.02 * s, 1.2 * s), cor, unico=nome + "M"); filho(t, m); m.location = (0, -0.08 * s, 0)
    BRILHO.append(mat(cor, nome + "M"))
    p = caixa(_id("peT"), (0, 0, 0), (0.2 * s, 0.2 * s, 0.6 * s), ESCURO); filho(t, p); p.location = (0, 0.05 * s, -0.95 * s)
    return t

def volume_piso(nome, x, y, lado=3.6):
    for dx, dy, w, d in ((0, -lado / 2, lado, 0.06), (0, lado / 2, lado, 0.06), (-lado / 2, 0, 0.06, lado), (lado / 2, 0, 0.06, lado)):
        caixa(_id(nome), (x + dx, y + dy, 0.02), (w, d, 0.04), CIANO, unico="volume")

import cartoon as _ct
_ct.PLANOS["geral"] = (7.4, 1.2, 0.3)
cam, alvo, cam_key, plano = camera_cartoon(24)
PX = 0.85

# =====================================================================
# ZONA A (x = 0) — estúdio: Pixel de roupa de captura; '?'; '10 ANOS?'; calendário 2016; tela de créditos (bloco 0) + CTA (bloco 7)
# =====================================================================
zona_ini()
t0, t1 = S[0]
sala("A", 0, (0.36, 0.40, 0.62, 1), (0.24, 0.28, 0.48, 1), (0.55, 0.38, 0.85, 1))
tan = T(0, "anos"); tgt = T(0, "GTA"); tcr = T(0, "créditos"); tdy = T(0, "Dylan"); tma = T(0, "Manni"); tpo = T(0, "post"); t16 = T(0, "dois"); tte = T(0, "teriam")
tela_creditos("credA", 1.0, 3.9, 3.0, 3.4, 2.4, tcr - 0.3, t1 + 0.3, ouro=(2, 5), n=16)
volume_piso("volA", 0.6, 1.2, 3.4)
dA = []
for k, (cx, cy) in enumerate(((-1.9, 2.8), (2.9, 2.8))):
    v, _ = cam_mocap(_id("camA"), (cx, cy, 0), (0.0, 1.0), 2.4); dA.append(v)
iqA = interroga("interA", (1.3, 1.4, 4.4), 0.7, AMARELO); visivel(iqA, 0.0, tan - 0.05); pop(iqA, 0.05, 1.0)
t10 = texto3d("t10", "10 ANOS?", (1.2, 1.4, 4.4), 0.62, AMARELO, 0.16); visivel(t10, tan - 0.05, tcr - 0.3); pop(t10, tan - 0.05, 1.0)
calA = calendario("calA", (1.6, 1.6, 2.1), 1.0); visivel(calA, tte - 0.3, t1 + 0.3); pop(calA, tte - 0.3, 1.0)
for o in bpy.data.objects:
    if o.name.startswith(("topoCal", "diaCal")) and abs(o.location.x - 1.6) < 1 and o.location.y < 2: visivel(o, tte - 0.3, t1 + 0.3)
t2016 = texto3d("t2016", "2016?", (1.5, 1.3, 3.3), 0.45, VERMELHO, 0.12); visivel(t2016, t16 - 0.3, t1 + 0.3); pop(t2016, t16 - 0.3, 1.0)
# CTA (bloco 7): check verde (SIM) x X vermelho (NÃO)
t7 = S[7][0]; tsim = T(7, "sim"); tnao = T(7, "não")
ckA = check("ckCTA", (0.2, 1.2, 3.6), 1.1); visivel(ckA, tsim - 0.3); pop(ckA, tsim - 0.3, 1.1)
xCTA = xis("xCTA", (2.0, 1.2, 3.6), 1.1); visivel(xCTA, tnao - 0.3); pop(xCTA, tnao - 0.3, 1.0)
px = pixel_mocap("pixel", (-1.0, 0.4, 0), escala=PX); girarZ(px["raiz"], 14); respirar(px, 0, FIM)
pensar(px, 0.05, 1.6); apontar(px, tcr - 0.1, 1.4, "D", 50); apontar(px, tma - 0.1, 1.2, "D", 40); espanto(px, t16 - 0.3, 1.3)
acenar(px, t7 + 0.1, 1.4); apontar(px, tsim - 0.2, 1.2, "D", 40); apontar(px, tnao - 0.2, 1.2, "D", 60)
acenar(px, LEG[-1]["e"] + 1.2, 1.6); comemorar(px, LEG[-1]["e"] + 3.0, 1.4)
plano(0, (0.4, 1.8), "geral", altura=2.3); plano(tcr - 0.4, (0.45, 1.8), "geral", altura=2.4)
plano(tpo - 0.3, (0.4, 1.8), "geral", altura=2.2); plano(t1 - 0.05, (0.4, 1.8), "geral", altura=2.2)
cam_key(t7, (0.4, -6.0, 3.4), (0.4, 1.6, 2.4)); cam_key(FIM, (0.5, -5.8, 3.4), (0.5, 1.6, 2.4))
zona_fim([(0.0, t1 + 0.3), (t7 - 0.3, FIM + 0.5)])

# =====================================================================
# ZONA B (x = 40) — camarim: arara com roupas de captura; Pixel de moletom troca para a roupa; bolinhas nascem uma a uma (bloco 1)
# =====================================================================
zona_ini()
t0, t1 = S[1]
sala("B", 40, (0.95, 0.80, 0.45, 1), (0.68, 0.50, 0.26, 1), (0.25, 0.30, 0.55, 1))
tgr = T(1, "grava"); tpe = T(1, "personagem"); tve = T(1, "veste"); tro = T(1, "roupa"); tbo = T(1, "bolinhas"); tbr = T(1, "brilhantes")
caixa("araraB", (42.0, 2.6, 3.2), (2.6, 0.08, 0.08), CINZA)
for dx in (-1.25, 1.25): caixa(_id("peArara"), (42.0 + dx, 2.6, 1.6), (0.08, 0.08, 3.2), CINZA)
for k in range(3):
    r = caixa(_id("roupaB"), (41.2 + 0.8 * k, 2.6, 2.3), (0.6, 0.15, 1.6), TRAJE); liso(r)
    for j in range(4):
        esfera(_id("marcB"), (41.2 + 0.8 * k + (0.18 if j % 2 else -0.18), 2.48, 2.7 - 0.35 * j), 0.05, MARC, sub=1, unico="marcador")
caixa("caixaBol", (42.0, 1.4, 0.35), (1.0, 0.7, 0.7), (0.85, 0.45, 0.25, 1))
for k in range(8):
    esfera(_id("bolCaixa"), (41.7 + 0.1 * (k % 4) * 2, 1.3 + 0.12 * (k // 4), 0.75), 0.07, MARC, sub=1, unico="marcador")
iqB = interroga("interB", (40.8, 1.4, 4.3), 0.6, AMARELO); visivel(iqB, t0, tve - 0.2); pop(iqB, t0 + 0.05, 1.0)
gB0 = pixel("guiaB0", (39.0, 0.3, 0), escala=PX); girarZ(gB0["raiz"], 20); respirar(gB0, t0, tve)
pensar(gB0, tgr - 0.2, 1.4); visivel(gB0["raiz"], t0 - 0.3, tve)
gB = pixel_mocap("guiaB", (39.0, 0.3, 0), t_marc=tbo - 0.35, dt=0.05, escala=PX); girarZ(gB["raiz"], 20); respirar(gB, tve, t1 + 0.5)
visivel(gB["raiz"], tve)
anB = anel("haloB", (39.0, 0.25, 1.4), 1.1, 0.05, AMARELO, seg=28, unico="halo"); BRILHO.append(mat(AMARELO, "halo"))
visivel(anB, tve, tve + 0.6); pop(anB, tve, 1.0, 0.25)
espanto(gB, tro, 1.0); comemorar(gB, tbr - 0.1, 1.3)
plano(t0, (40.4, 1.8), "geral", altura=2.2); plano(t1 - 0.05, (40.45, 1.8), "geral", altura=2.2)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA C (x = 80) — o volume: quadrado no chão, câmeras em tripés e na treliça; raios até as bolinhas; esqueleto na tela imita o aceno (bloco 2)
# =====================================================================
zona_ini()
t0, t1 = S[2]
sala("C", 80, (0.30, 0.32, 0.42, 1), (0.20, 0.22, 0.30, 1), (0.16, 0.20, 0.34, 1))
tvo = T(2, "volta"); tcm = T(2, "câmeras"); tvl = T(2, "volume"); tar = T(2, "área"); ten = T(2, "enxergam"); tco = T(2, "computador"); tmv = T(2, "movimento"); tes = T(2, "esqueleto")
PXC = (79.0, 0.9)
volume_piso("volC", 79.0, 1.0, 3.6)
caixa("trelica", (80.0, 2.6, 5.3), (6.4, 0.25, 0.25), CINZA)
CAMS = []
for k, (cx, cy, h, tri) in enumerate(((76.7, 2.4, 2.3, True), (81.3, 2.6, 2.3, True), (77.6, 3.0, 1.4, True), (80.6, 3.1, 1.4, True))):
    v, pos = cam_mocap(_id("camC"), (cx, cy, 0), PXC, h, tri); CAMS.append((v, pos))
for k, cx in enumerate((77.2, 78.6, 80.0, 81.4)):
    v, pos = cam_mocap(_id("camT"), (cx, 2.5, 4.6), PXC, 0.5, False); CAMS.append((v, pos))
for k, (v, pos) in enumerate(CAMS):
    tt = tcm - 0.3 + 0.1 * k; visivel(v, tt); pop(v, tt, 1.0, 0.3)
# raios das câmeras até o peito do Pixel
for k, (v, pos) in enumerate(CAMS):
    r = osso(_id("raioC"), pos, (PXC[0], PXC[1] - 0.2, 1.5), 0.018, (1.0, 0.35, 0.30, 1), "raio"); visivel(r, ten - 0.1 + 0.05 * k, tco - 0.2)
# tela com esqueleto (à direita)
tvC = tela("telaC", (81.6, 1.9, 2.4), 0.95, (0.05, 0.08, 0.16, 1))
skC, pivC = boneco("esqC", (81.6, 1.74, 1.55), 0.95)
visivel(skC, tco - 0.2); pop(skC, tco - 0.2, 1.0)
onda_braco(pivC, tmv - 0.05, 1.6)
gC = pixel_mocap("guiaC", (PXC[0], PXC[1], 0), escala=PX); girarZ(gC["raiz"], 10); respirar(gC, t0, t1 + 0.5)
apontar(gC, tvo, 1.2, "D", 60); espanto(gC, tvl - 0.1, 1.0); acenar(gC, tmv - 0.05, 1.6); comemorar(gC, tes + 0.2, 1.2)
plano(t0, (79.6, 1.8), "geral", altura=2.4); plano(tco - 0.4, (79.9, 1.8), "geral", altura=2.3); plano(t1 - 0.05, (79.95, 1.8), "geral", altura=2.3)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA D (x = 120) — capacete com câmera no rosto (pontinhos verdes) + tela com o rosto em pontos; microfone de vara (bloco 3)
# =====================================================================
zona_ini()
t0, t1 = S[3]
sala("D", 120, (0.40, 0.30, 0.55, 1), (0.26, 0.18, 0.40, 1), (0.16, 0.22, 0.40, 1))
tro3 = T(3, "rosto"); tcap = T(3, "capacete"); tpi = T(3, "piscada"); tso = T(3, "sorriso"); tvz = T(3, "voz"); tju = T(3, "junto"); tce = T(3, "cena")
gD = pixel_mocap("guiaD", (119.0, 0.6, 0), escala=PX); girarZ(gD["raiz"], 12); respirar(gD, t0, t1 + 0.5)
HMC = capacete(gD)
for o in HMC: visivel(o, tcap - 0.3)
anD = anel("haloD", (119.0, 0.55, 2.2), 0.9, 0.04, AMARELO, seg=28, unico="halo"); anD.rotation_euler = (math.radians(90), 0, 0)
anD.location = (119.0 - 0.0, 0.0, 2.3); visivel(anD, tcap - 0.2, tcap + 0.8); pop(anD, tcap - 0.2, 1.0)
# tela com 'rosto em pontos' (pontos verdes que piscam/sorriem)
tvD = tela("telaD", (121.4, 2.2, 2.6), 0.95, (0.05, 0.08, 0.16, 1))
BRILHO.append(mat(VERDE, "ptTela"))
olhos = []
for x in (-0.35, 0.35):
    o = caixa(_id("olhoT"), (121.4 + x, 2.06, 2.95), (0.28, 0.02, 0.14), VERDE, unico="ptTela"); olhos.append(o)
for k in range(7):
    a = math.radians(200 + k * 140 / 6)
    caixa(_id("bocaT"), (121.4 + 0.5 * math.cos(a), 2.06, 2.45 + 0.25 * math.sin(a)), (0.1, 0.02, 0.1), VERDE, unico="ptTela")
for o in olhos:
    for tt in (tpi - 0.05, tpi + 0.5):
        key(o, "scale", tt, (1, 1, 1)); key(o, "scale", tt + 0.1, (1, 1, 0.15)); key(o, "scale", tt + 0.2, (1, 1, 1))
for o in bpy.data.objects:
    if o.name.startswith(("olhoT", "bocaT")): visivel(o, tcap)
pe, micD = microfone_vara("microD", 121.0, 0.9, 1.0); visivel(pe, tvz - 0.5); visivel(micD, tvz - 0.5)
for o in bpy.data.objects:
    if o.name.startswith(("vara", "espuma")) and abs(o.location.x - 120) < 4: visivel(o, tvz - 0.5)
pop(micD, tvz - 0.5, 1.0)
apontar(gD, tro3 - 0.1, 1.2, "D", 70); comemorar(gD, tso - 0.2, 1.2); apontar(gD, tvz - 0.1, 1.4, "D", 80); acenar(gD, tce - 0.3, 1.0)
plano(t0, (120.1, 1.8), "geral", altura=2.6); plano(t1 - 0.05, (120.15, 1.8), "geral", altura=2.6)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA E (x = 160) — por que leva anos: pilha de roteiros cresce com X, claquete batendo, calendário soltando folhas (bloco 4)
# =====================================================================
zona_ini()
t0, t1 = S[4]
sala("E", 160, (0.85, 0.88, 0.95, 1), (0.48, 0.54, 0.70, 1), (0.20, 0.45, 0.55, 1))
tle = T(4, "leva"); trt = T(4, "roteiro"); tms = T(4, "missões"); tcn = T(4, "cenas"); trg = T(4, "regravadas"); tsg = T(4, "Segundo"); tdo = T(4, "dois"); tan4 = T(4, "anos"); tna = T(4, "nascer")
caixa("mesaE", (160.4, 1.8, 0.5), (4.6, 1.5, 1.0), (0.30, 0.22, 0.18, 1))
for k in range(9):
    pp = caixa(_id("roteiroE"), (159.4, 1.8, 1.06 + 0.11 * k), (1.0, 0.75, 0.1), BRANCO if k % 2 else (0.95, 0.92, 0.80, 1))
    tt = trt - 0.2 + 0.22 * k; visivel(pp, tt); pop(pp, tt, 1.0, 0.2)
xE = xis("xE", (159.4, 1.2, 2.6), 0.8); visivel(xE, tms - 0.1, tcn - 0.1); pop(xE, tms - 0.1, 1.0)
clB, clD = claquete("claqE", (161.4, 1.6, 1.5), 1.0)
for k in range(4): bater(clD, tcn - 0.2 + 0.45 * k)
calE = calendario("calE", (160.4, 2.8, 3.6), 1.1, VERMELHO)
folhas_voando("folhaE", (160.4, 2.7, 3.6), tsg - 0.2, 10, 0.3, 1.0)
gE = pixel_mocap("guiaE", (158.0, 0.4, 0), escala=PX); girarZ(gE["raiz"], 14); respirar(gE, t0, t1 + 0.5)
pensar(gE, t0 + 0.05, 1.4); apontar(gE, trt - 0.1, 1.3, "D", 50); espanto(gE, trg - 0.2, 1.1); apontar(gE, tan4 - 0.2, 1.4, "D", 80)
plano(t0, (159.5, 1.9), "geral", altura=2.4); plano(t1 - 0.05, (159.55, 1.9), "geral", altura=2.4)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA F (x = 200) — NDA: contrato com cadeado; balão com X ('não pode contar'); martelo (processo); créditos (bloco 5)
# =====================================================================
zona_ini()
t0, t1 = S[5]
sala("F", 200, (0.42, 0.46, 0.62, 1), (0.27, 0.31, 0.45, 1), (0.40, 0.28, 0.58, 1))
tnd = T(5, "NDA"); tsi = T(5, "sigilo"); tct = T(5, "contrato"); tpb = T(5, "proíbe"); tcnt = T(5, "contar"); tqb = T(5, "Quebrar"); tpc = T(5, "processo"); tno = T(5, "nomes"); tcr5 = T(5, "créditos")
caixa("mesaF", (200.6, 1.8, 0.5), (5.0, 1.5, 1.0), (0.30, 0.22, 0.18, 1))
ctF = contrato("contratoF", (200.0, 2.2, 2.3), 1.0)
tNDA = texto3d("tNDA", "NDA", (200.0, 2.1, 2.95), 0.42, ESCURO, 0.06); visivel(tNDA, tnd - 0.2); pop(tNDA, tnd - 0.2, 1.0)
cdF, alF = cadeado("cadF", (200.0, 1.9, 1.75), 0.9)
key(cdF, "location", t0, (200.0, 1.9, 5.5)); key(cdF, "location", tsi - 0.3, (200.0, 1.9, 5.5)); key(cdF, "location", tsi + 0.1, (200.0, 1.9, 1.75))
balF = balao("balaoF", (199.0, 1.4, 4.3), 0.7); visivel(balF, tcnt - 0.5, tno - 0.3)
balF.scale = (0.001,) * 3; balF.keyframe_insert("scale", frame=f(tcnt - 0.5)); balF.scale = (1.25, 0.35, 0.9); balF.keyframe_insert("scale", frame=f(tcnt - 0.2))
xF = xis("xF", (199.0, 1.1, 4.3), 0.9); visivel(xF, tcnt, tno - 0.3); pop(xF, tcnt, 1.0)
mpiv, mbase = martelo("martF", (201.6, 1.4, 1.1), 1.0); visivel(mpiv, tqb - 0.4); visivel(mbase, tqb - 0.4); pop(mpiv, tqb - 0.4, 1.0)
key(mpiv, "rotation_euler", tqb - 0.1, (0, math.radians(-60), 0)); key(mpiv, "rotation_euler", tpc, (0, math.radians(10), 0), "CONSTANT")
key(mpiv, "rotation_euler", tpc + 0.35, (0, math.radians(-50), 0)); key(mpiv, "rotation_euler", tpc + 0.6, (0, math.radians(10), 0), "CONSTANT")
excF = texto3d("excF", "!", (201.9, 1.3, 3.2), 0.9, VERMELHO, 0.14); visivel(excF, tpc, tno - 0.3); pop(excF, tpc, 1.0)
gF = pixel_mocap("guiaF", (198.3, 0.4, 0), escala=PX); girarZ(gF["raiz"], 14); respirar(gF, t0, t1 + 0.5)
pensar(gF, t0 + 0.05, 1.4); apontar(gF, tct - 0.1, 1.3, "D", 40); espanto(gF, tcnt - 0.2, 1.2); espanto(gF, tpc - 0.1, 1.0)
# créditos no fim do bloco (mesma sala, à direita do contrato)
tela_creditos("credF", 200.6, 3.6, 3.9, 2.8, 1.6, tno - 0.4, t1 + 0.3, ouro=(1, 3), n=8)
apontar(gF, tcr5 - 0.2, 1.2, "D", 75)
plano(t0, (199.9, 1.8), "geral", altura=2.5); plano(t1 - 0.05, (199.95, 1.8), "geral", altura=2.6)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA G (x = 240) — créditos rolando (2 linhas douradas); '?' no ano exato; calendário soltando folhas: 'foram anos' (bloco 6)
# =====================================================================
zona_ini()
t0, t1 = S[6]
sala("G", 240, (0.45, 0.75, 0.55, 1), (0.28, 0.54, 0.38, 1), (0.95, 0.55, 0.25, 1))
tdz = T(6, "dez"); tex = T(6, "exato"); tcf = T(6, "confirmou"); tfa = T(6, "anos", 1)
tela_creditos("credG", 240.9, 3.9, 3.0, 3.4, 2.4, t0 - 0.3, t1 + 0.3, ouro=(2, 4), n=12)
iqG = interroga("interG", (239.6, 1.4, 4.3), 0.6, AMARELO); visivel(iqG, tex - 0.3, tfa - 0.4); pop(iqG, tex - 0.3, 1.0)
calG = calendario("calG", (241.8, 1.6, 2.0), 0.9, VERMELHO)
folhas_voando("folhaG", (241.8, 1.5, 2.0), tfa - 0.7, 6, 0.18, 0.9)
gG = pixel_mocap("guiaG", (238.6, 0.4, 0), escala=PX); girarZ(gG["raiz"], 12); respirar(gG, t0, t1 + 0.5)
pensar(gG, tdz - 0.2, 1.3); apontar(gG, tex - 0.1, 1.2, "D", 50); comemorar(gG, tfa - 0.3, 1.3)
plano(t0, (240.3, 1.9), "geral", altura=2.3); plano(t1 - 0.05, (240.35, 1.9), "geral", altura=2.3)
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
