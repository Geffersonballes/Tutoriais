"""Série 2 — 'O GTA 6 está matando PS5 e Xbox?' (notícia 27/11; estilo C cartoon, mascote Pixel, visual nível 2).
Mecanismo: o caminho do calor dentro de um console GENÉRICO (sem marca): chip esquenta -> metal líquido (prata)
-> dissipador (cobre + alumínio) -> ventoinha joga o ar quente para fora; fonte com raio alimenta tudo. Carga máxima
por horas (termômetro + ampulheta) revela 3 defeitos que já existiam: gota de metal escorre, poeira tampa a grade,
fonte pisca. Console saudável (check) x defeituoso (golpe final). Empresas: 3 balões '...' sem logo. Dicas: espaço em
volta, tirar poeira, assistência (caixa de ferramentas) — nada de abrir console. CTA AGUENTOU x FRITOU.
Base: cena_gta6_212gb.py (zonas: cada zona só renderiza no próprio bloco). Anti-borda: piso xadrez + parede alta com painéis.
Uso: blender -b --factory-startup -P cena_gta6_consoles.py -- <pasta> [preview t1,t2 | range a,b]"""
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

def caixa_lacrada(nome, loc, s=1.0, cor=(0.78, 0.58, 0.34, 1)):
    c = caixa(nome, loc, (0.9 * s, 0.9 * s, 0.7 * s), cor); liso(c)
    f1 = caixa(_id("fita"), (0, 0, 0), (0.92 * s, 0.2 * s, 0.72 * s), (0.95, 0.30, 0.25, 1)); filho(c, f1)
    return c

def chip_cpu(nome, loc, s=1.0, cor=CHIPV):
    c = caixa(nome, loc, (1.0 * s, 0.12 * s, 1.0 * s), cor)
    n = caixa(_id("nucleo"), (0, 0, 0), (0.55 * s, 0.05 * s, 0.55 * s), (0.75, 0.77, 0.80, 1)); filho(c, n); n.location = (0, -0.07 * s, 0)
    for k in range(5):
        for sg in (-1, 1):
            pn = caixa(_id("pino"), (0, 0, 0), (0.06 * s, 0.05 * s, 0.18 * s), OURO); filho(c, pn); pn.location = ((-0.36 + k * 0.18) * s, 0, sg * 0.58 * s)
            pn2 = caixa(_id("pino"), (0, 0, 0), (0.18 * s, 0.05 * s, 0.06 * s), OURO); filho(c, pn2); pn2.location = (sg * 0.58 * s, 0, (-0.36 + k * 0.18) * s)
    return c

def caixa_som(nome, loc, s=1.0):
    b = caixa(nome, loc, (1.2 * s, 0.9 * s, 2.0 * s), (0.16, 0.16, 0.22, 1)); liso(b)
    for dz, r in ((0.45, 0.42), (-0.4, 0.3)):
        cn = cilindro(_id("cone"), (0, 0, 0), r * s, 0.12 * s, CINZA, seg=18); filho(b, cn); cn.location = (0, -0.47 * s, dz * s); cn.rotation_euler = (math.radians(90), 0, 0)
        cc = esfera(_id("ccone"), (0, 0, 0), r * 0.35 * s, LARANJA, sub=2); filho(b, cc); cc.location = (0, -0.52 * s, dz * s)
    return b

def arvorezinha(nome, loc, s=1.0):
    tr = cilindro(nome, loc, 0.08 * s, 0.4 * s, (0.45, 0.28, 0.14, 1), seg=6)
    cp = cilindro(_id("copaA"), (0, 0, 0), 0.32 * s, 0.7 * s, (0.25, 0.70, 0.30, 1), seg=8, r2=0.0, unico="copaA"); filho(tr, cp); cp.location = (0, 0, 0.5 * s)
    return tr

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

def calendario(nome, loc, s=1.0):
    c = caixa(nome, loc, (1.6 * s, 0.12 * s, 1.8 * s), BRANCO)
    tp = caixa(_id("topoCal"), (0, 0, 0), (1.6 * s, 0.14 * s, 0.4 * s), VERMELHO); filho(c, tp); tp.location = (0, -0.01 * s, 0.75 * s)
    for i in range(4):
        for j in range(3):
            q = caixa(_id("dia"), (0, 0, 0), (0.25 * s, 0.03 * s, 0.22 * s), (0.80, 0.82, 0.88, 1)); filho(c, q)
            q.location = ((-0.55 + i * 0.37) * s, -0.07 * s, (0.2 - j * 0.38) * s)
    return c

def ampulheta(nome, loc, s=1.0):
    v = vazio(nome, loc)
    for dz in (-0.55, 0.55):
        t = cilindro(_id("tampaA"), (0, 0, 0), 0.45 * s, 0.1 * s, (0.45, 0.28, 0.14, 1), seg=14); filho(v, t); t.location = (0, 0, dz * s)
    for dz, r1, r2 in ((-0.25, 0.38, 0.06), (0.25, 0.06, 0.38)):
        c = cilindro(_id("vidro"), (0, 0, 0), r1 * s, 0.5 * s, (0.75, 0.90, 1.0, 1), seg=14, r2=r2 * s); filho(v, c); c.location = (0, 0, dz * s)
    ar = cilindro(_id("areia"), (0, 0, 0), 0.3 * s, 0.2 * s, OURO, seg=14, r2=0.05 * s); filho(v, ar); ar.location = (0, 0, -0.38 * s)
    return v

def roteador(nome, loc, s=1.0):
    r = caixa(nome, loc, (1.6 * s, 0.9 * s, 0.35 * s), ESCURO); liso(r)
    for dx in (-0.55, 0.55):
        a = cilindro(_id("antena"), (0, 0, 0), 0.05 * s, 0.9 * s, ESCURO, seg=6); filho(r, a); a.location = (dx * s, 0.3 * s, 0.6 * s)
    for k in range(4):
        l = esfera(_id("ledR"), (0, 0, 0), 0.05 * s, VERDE, sub=1, unico="ledR"); filho(r, l); l.location = ((-0.45 + k * 0.3) * s, -0.46 * s, 0)
    BRILHO.append(mat(VERDE, "ledR"))
    return r

def lixeira(nome, loc, s=1.0):
    b = cilindro(nome, loc, 0.55 * s, 1.2 * s, (0.30, 0.55, 0.95, 1), seg=16, r2=0.65 * s)
    tp = cilindro(_id("tampaL"), (0, 0, 0), 0.7 * s, 0.1 * s, (0.22, 0.42, 0.80, 1), seg=16); filho(b, tp); tp.location = (0, 0, 0.66 * s)
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

def chama(nome, loc, s=1.0):
    b = cilindro(nome, loc, 0.5 * s, 1.3 * s, LARANJA, seg=10, r2=0.0, unico="chamaF")
    i = cilindro(_id("chamaI"), (0, 0, 0), 0.3 * s, 0.9 * s, AMARELO, seg=10, r2=0.0, unico="chamaI"); filho(b, i); i.location = (0, -0.15 * s, -0.1 * s)
    BRILHO.extend([mat(LARANJA, "chamaF"), mat(AMARELO, "chamaI")])
    return b

def particulas(nome, n, t0, t1, p0, p1, p2, cor, unico, r=0.12, dur=1.4):
    """Bolinhas que seguem uma curva de p0 a p2 em fila (calor, ar)."""
    BRILHO.append(mat(cor, unico))
    k = 0; t = t0
    while t < t1 and k < n:
        e = esfera(_id(nome), p0, r, cor, sub=1, unico=unico); visivel(e, t, t + dur)
        caminho(e, t, t + dur, lambda u, a=p0, b=p1, c=p2: bez(a, b, c, u), orientar=False, passo=3)
        t += (t1 - t0) / n; k += 1

def dissipador(nome, loc, s=1.0):
    base = caixa(nome, loc, (1.8 * s, 1.2 * s, 0.18 * s), (0.85, 0.50, 0.25, 1))
    for k in range(9):
        a = caixa(_id("aleta"), (0, 0, 0), (0.07 * s, 1.1 * s, 0.9 * s), (0.80, 0.83, 0.88, 1), unico="aleta"); filho(base, a)
        a.location = ((-0.8 + k * 0.2) * s, 0, 0.55 * s)
    for dx in (-0.45, 0.45):
        tb = cilindro(_id("tuboCu"), (0, 0, 0), 0.07 * s, 1.0 * s, (0.90, 0.52, 0.25, 1), seg=8, unico="tuboCu"); filho(base, tb)
        tb.location = (dx * s, -0.62 * s, 0.5 * s)
    return base

def ventoinha(nome, loc, s=1.0):
    """Moldura + rotor de 7 pás no plano XZ (de frente para a câmera); o rotor gira em Y."""
    mold = caixa(nome, loc, (2.4 * s, 0.4 * s, 2.4 * s), (0.20, 0.21, 0.26, 1))
    furo = cilindro(_id("furoV"), (0, 0, 0), 1.05 * s, 0.42 * s, (0.08, 0.08, 0.10, 1), seg=28); filho(mold, furo); furo.rotation_euler = (math.radians(90), 0, 0)
    rot = vazio(_id("rotorV"), (loc[0], loc[1] - 0.25 * s, loc[2]))
    hub = cilindro(_id("hubV"), (0, 0, 0), 0.32 * s, 0.2 * s, CIANO, seg=16); filho(rot, hub); hub.rotation_euler = (math.radians(90), 0, 0)
    for k in range(7):
        p = caixa(_id("paV"), (0, 0, 0), (0.32 * s, 0.06 * s, 0.85 * s), (0.85, 0.88, 0.95, 1), unico="paV"); filho(rot, p)
        ang = 2 * math.pi * k / 7; p.location = (0.6 * s * math.sin(ang), 0, 0.6 * s * math.cos(ang)); p.rotation_euler = (0, -ang, math.radians(20))
    return mold, rot

def girarY(ob, t0, rps=1.2):
    ob.rotation_euler = (0, 0, 0); ob.keyframe_insert("rotation_euler", frame=f(t0), index=1)
    ob.rotation_euler = (0, 2 * math.pi * rps, 0); ob.keyframe_insert("rotation_euler", frame=f(t0 + 1.0), index=1)
    for fc in ob.animation_data.action.fcurves:
        if fc.data_path == "rotation_euler":
            for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
            fc.extrapolation = "LINEAR"

def fonte_energia(nome, loc, s=1.0):
    b = caixa(nome, loc, (1.4 * s, 1.0 * s, 1.0 * s), (0.30, 0.32, 0.38, 1)); liso(b)
    for k, (dx, dz, rz) in enumerate(((0.08, 0.22, -25), (-0.05, 0.0, 30), (0.08, -0.22, -25))):
        r = caixa(_id("raio"), (0, 0, 0), (0.12 * s, 0.05 * s, 0.32 * s), AMARELO, unico="raio"); filho(b, r)
        r.location = (dx * s, -0.52 * s, dz * s); r.rotation_euler = (0, math.radians(rz), 0)
    BRILHO.append(mat(AMARELO, "raio"))
    return b

def grade(nome, loc, s=1.0):
    g = caixa(nome, loc, (1.8 * s, 0.2 * s, 1.4 * s), (0.14, 0.15, 0.18, 1))
    for k in range(6):
        l = caixa(_id("ripa"), (0, 0, 0), (1.6 * s, 0.1 * s, 0.08 * s), (0.45, 0.47, 0.52, 1), unico="ripa"); filho(g, l); l.location = (0, -0.1 * s, (-0.55 + k * 0.22) * s)
    return g

def poeira(nome, loc, s=1.0):
    e = esfera(nome, loc, 0.32 * s, (0.62, 0.58, 0.52, 1), sub=2, unico="poeira"); liso(e)
    for dx, dz, r in ((0.3, 0.1, 0.22), (-0.28, 0.05, 0.2), (0.05, 0.25, 0.2)):
        q = esfera(_id("poeiraB"), (0, 0, 0), r * s, (0.66, 0.62, 0.56, 1), sub=2, unico="poeiraB"); filho(e, q); q.location = (dx * s, -0.05, dz * s)
    return e

def balao(nome, loc, s=1.0):
    b = esfera(nome, loc, 0.75 * s, BRANCO, sub=2); liso(b); b.scale = (1.25, 0.35, 0.9)
    for dx in (-0.3, 0, 0.3):
        p = esfera(_id("ponto"), (0, 0, 0), 0.09 * s, CINZA, sub=1, unico="pontoB"); filho(b, p); p.location = (dx * s / 1.25, -0.75, 0)
    return b

def ferramentas(nome, loc, s=1.0):
    cx_ = caixa(nome, loc, (1.4 * s, 0.7 * s, 0.7 * s), VERMELHO); liso(cx_)
    al = anel(_id("alcaF"), (0, 0, 0), 0.3 * s, 0.06 * s, CINZA, seg=16); filho(cx_, al); al.location = (0, 0, 0.42 * s); al.rotation_euler = (math.radians(90), 0, 0)
    ch = caixa(_id("chaveF"), (0, 0, 0), (0.15 * s, 0.1 * s, 1.1 * s), PRATA); filho(cx_, ch); ch.location = (0.5 * s, -0.1 * s, 0.75 * s); ch.rotation_euler = (0, math.radians(30), 0)
    cb = anel(_id("bocaF"), (0, 0, 0), 0.16 * s, 0.05 * s, PRATA, seg=12); filho(cx_, cb); cb.location = (0.78 * s, -0.1 * s, 1.22 * s); cb.rotation_euler = (math.radians(90), 0, 0)
    return cx_

def console_preto(nome, loc, s=1.0):
    """Console genérico 'caixa' escura, sem marca (para contrastar com o branco)."""
    c = caixa(nome, loc, (1.0 * s, 1.0 * s, 1.4 * s), (0.12, 0.13, 0.16, 1)); liso(c)
    tp = cilindro(_id("topoP"), (0, 0, 0), 0.38 * s, 0.06 * s, (0.25, 0.27, 0.32, 1), seg=20); filho(c, tp); tp.location = (0, 0, 0.71 * s)
    return c

cam, alvo, cam_key, plano = camera_cartoon(24)

# =====================================================================
# ZONA A (x = 0) — dois consoles genéricos na mesa; LED fica vermelho, fumaça; caixas chegando (bloco 0) + CTA (bloco 7)
# =====================================================================
zona_ini()
t0, t1 = S[0]
sala("A", 0, (0.36, 0.40, 0.62, 1), (0.30, 0.34, 0.54, 1), (0.55, 0.38, 0.85, 1))
tma = T(0, "matando"); txb = T(0, "Xbox"); tsg = T(0, "Segundo"); tpo = T(0, "Polônia"); tch = T(0, "chegaram"); tdl = T(0, "desligam"); tli = T(0, "ligam")
caixa("mesaA", (0.4, 1.6, 1.0), (5.4, 1.3, 0.12), (0.30, 0.22, 0.18, 1))
for dx in (-2.4, 2.4): caixa(_id("peMesaA"), (0.4 + dx, 1.6, 0.48), (0.12, 1.0, 0.96), (0.18, 0.18, 0.22, 1))
cA = console("consA", (-0.5, 1.7, 1.93), 1.05)
cB = console_preto("consB", (1.5, 1.7, 1.83), 1.05)
lA, mlA = led("ledA", (-0.6, 1.15, 1.25), VERDE); lB, mlB = led("ledB", (1.4, 1.2, 1.25), VERDE)
for m in (mlA, mlB): cor_key(m, 0.0, VERDE, "CONSTANT"); piscar(m, tdl - 0.1, t1 + 0.3, VERMELHO, ESCURO, 0.35)
fumaca("fumA", (-0.6, 1.7, 2.7), tdl, 4); fumaca("fumB", (1.4, 1.7, 2.5), tdl + 0.2, 4)
iqA = interroga("interA", (0.4, 1.4, 3.7), 0.9, VERMELHO); visivel(iqA, 0.0, tsg + 0.2); pop(iqA, 0.05, 1.0)
for k in range(5):
    cx_ = caixa_lacrada(_id("chegaA"), (3.6, 1.2, 6.0), 0.55, (0.78, 0.58, 0.34, 1))
    tt = tch - 0.3 + 0.25 * k; visivel(cx_, tt, t1 + 0.3)
    key(cx_, "location", tt, (3.2 + (k % 2) * 0.7, 1.0 + (k // 2) * 0.3, 6.0)); key(cx_, "location", tt + 0.45, (3.2 + (k % 2) * 0.7, 1.0 + (k // 2) * 0.3, 1.33 + 0.5 * (k // 2)))
# CTA (bloco 7): check verde (aguentou) e chama (fritou)
tag = T(7, "aguentou", 1); tfr = T(7, "fritou"); t7 = S[7][0]
ckA = check("checkA", (-1.6, 1.1, 2.9), 1.2); visivel(ckA, tag - 0.15); pop(ckA, tag - 0.15, 1.2)
chA = chama("chamaA", (2.6, 1.1, 2.6), 0.9); visivel(chA, tfr - 0.3); pop(chA, tfr - 0.3, 1.0)
px = pixel("pixel", (-1.9, 0.5, 0), escala=0.9); girarZ(px["raiz"], 14); respirar(px, 0, FIM)
espanto(px, 0.05, 1.3); apontar(px, tsg - 0.1, 1.2, "D", 40); apontar(px, tch - 0.1, 1.2, "D", 60); espanto(px, tdl - 0.1, 1.3)
acenar(px, t7 + 0.1, 1.4); apontar(px, tag - 0.1, 1.2, "E", 40); apontar(px, tfr - 0.1, 1.2, "D", 50)
acenar(px, LEG[-1]["e"] + 1.2, 1.6); comemorar(px, LEG[-1]["e"] + 3.0, 1.4)
plano(0, (0.4, 1.6), "geral", altura=2.4); plano(tch - 0.4, (0.6, 1.6), "geral", altura=2.5)
plano(tch - 0.05, (1.2, 1.5), "geral", altura=2.6); plano(t1 - 0.05, (1.0, 1.5), "geral", altura=2.6)
cam_key(t7, (0.0, -7.2, 2.8), (0.0, 1.4, 2.2)); cam_key(FIM, (0.3, -6.8, 2.8), (0.3, 1.4, 2.2))
zona_fim([(0.0, t1 + 0.3), (t7 - 0.3, FIM + 0.5)])

# =====================================================================
# ZONA B (x = 40) — bancada com 10 consoles; 2 escuros pulam (2 de cada 10); lupa/jornal 'site' (bloco 1)
# =====================================================================
zona_ini()
t0, t1 = S[1]
sala("B", 40, (0.95, 0.80, 0.45, 1), (0.88, 0.70, 0.38, 1), (0.25, 0.30, 0.55, 1))
tdo = T(1, "dois"); tdz = T(1, "dez"); tban = T(1, "bancada"); txb1 = T(1, "Xbox"); tpa = T(1, "país"); tme = T(1, "menos"); tsi = T(1, "site")
caixa("bancadaB", (40.4, 1.9, 1.0), (7.4, 1.6, 0.14), (0.55, 0.36, 0.22, 1))
for dx in (-3.4, 3.4): caixa(_id("peBanc"), (40.4 + dx, 1.9, 0.48), (0.14, 1.4, 0.96), (0.18, 0.18, 0.22, 1))
CON = []
for k in range(10):
    x_ = 37.6 + k * 0.62; esc = k in (3, 7)
    c_ = caixa(_id("miniB"), (x_, 2.0, 1.43), (0.42, 0.7, 0.72), (0.12, 0.13, 0.16, 1) if esc else BRANCO, unico="miniE" if esc else "miniW"); liso(c_)
    tt = tdz - 0.6 + 0.07 * k; visivel(c_, t0 if k < 2 else tt); pop(c_, t0 + 0.05 if k < 2 else tt, 1.0, 0.25); CON.append(c_)
for k in (3, 7):
    c_ = CON[k]
    key(c_, "location", txb1 - 0.1, (c_.location.x, 2.0, 1.43)); key(c_, "location", txb1 + 0.25, (c_.location.x, 1.6, 2.2)); key(c_, "location", t1, (c_.location.x, 1.6, 2.2))
    an = anel(_id("halo"), (c_.location.x, 1.55, 2.2), 0.62, 0.06, AMARELO, seg=24, unico="halo"); an.rotation_euler = (math.radians(90), 0, 0)
    visivel(an, txb1 + 0.25); pop(an, txb1 + 0.25, 1.0)
BRILHO.append(mat(AMARELO, "halo"))
tx2 = texto3d("t2de10", "2 / 10", (40.4, 2.6, 4.1), 0.9, AMARELO, 0.16); visivel(tx2, tdo - 0.1); pop(tx2, tdo - 0.1, 1.0)
lupa = anel("lupaB", (43.8, 1.0, 2.7), 0.45, 0.08, CIANO, seg=24); lupa.rotation_euler = (math.radians(90), 0, 0)
cab_ = caixa(_id("caboLupa"), (0, 0, 0), (0.12, 0.12, 0.7), (0.45, 0.28, 0.14, 1)); filho(lupa, cab_); cab_.location = (0.5, 0.5, 0); cab_.rotation_euler = (0, 0, 0)
visivel(lupa, tsi - 0.2); pop(lupa, tsi - 0.2, 1.0)
gB = pixel("guiaB", (37.2, 0.3, 0), escala=0.85); girarZ(gB["raiz"], 20); respirar(gB, t0, t1 + 0.5)
apontar(gB, tdo - 0.1, 1.4, "D", 60); espanto(gB, txb1 - 0.1, 1.3); pensar(gB, tpa - 0.1, 1.6); apontar(gB, tsi - 0.1, 1.3, "D", 40)
plano(t0, (40.4, 2.0), "geral", altura=2.4); plano(txb1 - 0.3, (40.4, 2.0), "geral", altura=2.5)
plano(txb1, (40.2, 1.8), "geral", altura=2.6); plano(t1 - 0.05, (40.6, 1.8), "geral", altura=2.7)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA C (x = 80) — caminho do calor: chip (esquenta) -> metal líquido (prata) -> dissipador (cobre + alumínio) (bloco 2)
# =====================================================================
zona_ini()
t0, t1 = S[2]
sala("C", 80, (0.62, 0.72, 0.98, 1), (0.52, 0.62, 0.90, 1), (0.30, 0.20, 0.45, 1))
tsiga = T(2, "siga"); tcal = T(2, "calor"); tchip = T(2, "chip"); tesq = T(2, "esquenta"); tps = T(2, "PS5"); tmet = T(2, "metal"); trap = T(2, "rápido"); tdis = T(2, "dissipador")
placa = caixa("placaC", (80.4, 2.0, 0.55), (5.0, 3.2, 0.14), (0.10, 0.45, 0.25, 1))
for k in range(6):
    caixa(_id("trilhaC"), (78.4 + k * 0.8, 1.6, 0.63), (0.08, 2.2, 0.03), OURO, unico="trilhaC")
caixa("pedC", (80.4, 2.0, 0.25), (5.2, 3.4, 0.5), (0.25, 0.25, 0.30, 1))
chipC = caixa("chipC", (80.4, 2.0, 0.85), (1.5, 1.5, 0.4), (0.16, 0.17, 0.20, 1)); liso(chipC)
mN = mat((0.75, 0.77, 0.80, 1), "nucleoC")
nuc = caixa("nucleoC", (80.4, 2.0, 1.07), (0.9, 0.9, 0.06), (0.75, 0.77, 0.80, 1), unico="nucleoC")
cor_key(mN, tesq - 0.2, (0.75, 0.77, 0.80, 1)); cor_key(mN, tesq + 0.6, (1.0, 0.35, 0.10, 1))
for ob in (placa, chipC, nuc): visivel(ob, t0)
metal = caixa("metalC", (80.4, 2.0, 1.15), (0.95, 0.95, 0.08), (0.86, 0.88, 0.92, 1), unico="metalC")
visivel(metal, tmet - 0.15); pop(metal, tmet - 0.15, 1.0); BRILHO.append(mat((0.86, 0.88, 0.92, 1), "metalC"))
for k in range(4):
    g = esfera(_id("gotaC"), (80.4 + random.uniform(-0.35, 0.35), 2.0 + random.uniform(-0.35, 0.35), 1.22), 0.09, (0.90, 0.92, 0.96, 1), sub=2, unico="metalC")
    visivel(g, tmet - 0.1 + 0.08 * k); pop(g, tmet - 0.1 + 0.08 * k, 1.0, 0.2)
dsp = dissipador("dissC", (80.4, 2.0, 2.9), 1.2)
key(dsp, "location", t0, (80.4, 2.0, 2.9)); tlev = T(2, "leva"); key(dsp, "location", tlev - 0.1, (80.4, 2.0, 2.9)); key(dsp, "location", tdis + 0.2, (80.4, 2.0, 1.3))
visivel(dsp, tlev - 0.2); pop(dsp, tlev - 0.2, 1.0)
particulas("calorC", 16, tcal, t1 + 0.2, (80.4, 1.5, 1.1), (80.0, 1.4, 2.2), (80.6, 1.5, 3.4), (1.0, 0.45, 0.10, 1), "calorC", r=0.11, dur=1.3)
gC = pixel("guiaC", (78.0, 0.2, 0), escala=0.8); girarZ(gC["raiz"], 20); respirar(gC, t0, t1 + 0.5)
apontar(gC, tsiga - 0.1, 1.3, "D", 40); apontar(gC, tchip - 0.1, 1.3, "D", 20); espanto(gC, tesq - 0.1, 1.2); apontar(gC, tmet - 0.1, 1.4, "D", 30); comemorar(gC, tdis - 0.1, 1.3)
plano(t0, (79.4, 2.0), "medio", altura=1.6); plano(tmet - 0.4, (79.5, 2.0), "medio", altura=1.5)
plano(tmet - 0.1, (79.6, 2.0), "medio", altura=1.5); plano(t1 - 0.05, (79.7, 2.0), "medio", altura=1.8)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA D (x = 120) — ventoinha gira, ar azul entra, calor laranja sai; fonte com raio manda energia (bloco 3)
# =====================================================================
zona_ini()
t0, t1 = S[3]
sala("D", 120, (0.40, 0.30, 0.55, 1), (0.34, 0.25, 0.48, 1), (0.16, 0.22, 0.40, 1))
tpu = T(3, "puxa"); tar = T(3, "ar"); tfo = T(3, "fora"); tfn = T(3, "fonte"); ten = T(3, "energia")
fan, rotor = ventoinha("fanD", (119.6, 2.0, 2.2), 1.0); girarY(rotor, t0, 1.5)
particulas("arD", 10, t0, t1 + 0.2, (116.6, 1.4, 2.2), (118.0, 1.2, 2.6), (119.6, 1.6, 2.2), (0.35, 0.80, 1.0, 1), "arD", r=0.1, dur=1.0)
particulas("calD", 10, tfo - 0.6, t1 + 0.2, (119.8, 1.6, 2.2), (121.4, 1.2, 2.6), (123.4, 1.0, 3.6), (1.0, 0.45, 0.10, 1), "calorC", r=0.12, dur=1.1)
fnt = fonte_energia("fonteD", (121.5, 1.6, 0.6), 0.9); visivel(fnt, tfn - 0.2); pop(fnt, tfn - 0.2, 1.0)
for k in range(6):
    e = esfera(_id("energD"), (121.2, 1.1, 0.9), 0.09, AMARELO, sub=1, unico="raio"); a = ten - 0.1 + 0.25 * k; visivel(e, a, a + 0.8)
    caminho(e, a, a + 0.8, lambda u: bez((121.2, 1.1, 0.9), (120.8, 1.2, 1.4), (120.2, 1.6, 1.3), u), orientar=False, passo=3)
gD = pixel("guiaD", (118.0, 0.2, 0), escala=0.85); girarZ(gD["raiz"], 20); respirar(gD, t0, t1 + 0.5)
apontar(gD, tpu - 0.1, 1.3, "D", 50); apontar(gD, tfo - 0.1, 1.2, "D", 70); apontar(gD, tfn - 0.1, 1.4, "D", 10)
plano(t0, (119.6, 2.0), "medio", altura=1.9); plano(t1 - 0.05, (120.2, 2.0), "medio", altura=1.9)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA E (x = 160) — termômetro enche; 3 defeitos: gota de metal escorre, poeira tampa a grade, fonte pisca; '!' (bloco 4)
# =====================================================================
zona_ini()
t0, t1 = S[4]
sala("E", 160, (0.42, 0.46, 0.62, 1), (0.36, 0.40, 0.55, 1), (0.40, 0.28, 0.58, 1))
tho = T(4, "horas"); tcg = T(4, "carga"); tmx = T(4, "máxima"); tme4 = T(4, "metal"); tesc = T(4, "escorrendo"); tpoe = T(4, "poeira")
tsa = T(4, "saída"); tfn4 = T(4, "fonte"); tfr4 = T(4, "fraca"); tdef = T(4, "defeito"); tap = T(4, "aparece")
mbE, termo, mtE = barra("termoE", 157.6, 3.2, 0.4, 4.2, 0.6, VERDE)
encher(termo, t0, t0 + 0.05, 0.1, 0.1); encher(termo, tcg - 0.2, tmx + 0.6, 0.1, 1.0)
cor_key(mtE, tcg - 0.2, VERDE); cor_key(mtE, tmx + 0.6, VERMELHO)
amp = ampulheta("ampE", (158.6, 2.6, 4.3), 0.7); visivel(amp, tho - 0.2); pop(amp, tho - 0.2, 0.7)
for k in range(3): key(amp, "rotation_euler", tho + 0.6 * k, (0, math.radians(180 * k), 0))
# 1) chip com metal líquido + gota escorrendo pela borda
caixa("chipE", (159.0, 2.0, 1.0), (1.2, 1.2, 0.35), (0.16, 0.17, 0.20, 1))
caixa("metalE", (159.0, 2.0, 1.2), (0.8, 0.8, 0.06), (0.86, 0.88, 0.92, 1), unico="metalC")
gota = esfera("gotaE", (159.4, 1.5, 1.22), 0.13, (0.90, 0.92, 0.96, 1), sub=2, unico="metalC"); visivel(gota, tme4 - 0.1)
key(gota, "location", tesc - 0.2, (159.4, 1.5, 1.22)); key(gota, "location", tesc + 0.5, (159.65, 1.38, 1.0)); key(gota, "location", tesc + 1.2, (159.7, 1.35, 0.3))
# 2) grade de saída de ar + bolas de poeira tampando
grade("gradeE", (160.6, 2.2, 2.0), 1.0)
for k in range(5):
    pz = poeira(_id("poE"), (160.0 + (k % 3) * 0.55, 2.0, 1.6 + (k // 3) * 0.5), 0.9); tt = tpoe - 0.1 + 0.12 * k; visivel(pz, tt); pop(pz, tt, 0.9, 0.25)
# 3) fonte cansada, LED piscando vermelho
fE = fonte_energia("fonteE", (161.9, 1.8, 0.55), 0.9)
lE, mlE = led("ledE", (162.35, 1.33, 0.9), VERDE, 0.09); cor_key(mlE, t0, VERDE, "CONSTANT"); piscar(mlE, tfn4 - 0.1, t1 + 0.3, VERMELHO, ESCURO, 0.3)
exc = texto3d("excE", "!", (160.2, 1.2, 4.0), 2.0, VERMELHO, 0.2); visivel(exc, tdef - 0.15); pop(exc, tdef - 0.15, 1.0)
gE = pixel("guiaE", (157.2, 0.3, 0), escala=0.85); girarZ(gE["raiz"], 10); respirar(gE, t0, t1 + 0.5)
pensar(gE, tho - 0.1, 1.4); apontar(gE, tesc - 0.2, 1.2, "D", 20); apontar(gE, tpoe - 0.1, 1.2, "D", 40); apontar(gE, tfn4 - 0.1, 1.2, "D", 10); espanto(gE, tdef - 0.1, 1.3)
plano(t0, (158.2, 2.2), "medio", altura=2.4); plano(tme4 - 0.4, (158.4, 2.2), "medio", altura=2.4)
plano(tme4 - 0.1, (159.6, 2.0), "geral", altura=2.0); plano(t1 - 0.05, (159.8, 2.0), "geral", altura=2.2)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA F (x = 200) — console saudável (check) x console com defeito (rachadura); martelinho 'golpe final'; 3 balões '...' (bloco 5)
# =====================================================================
zona_ini()
t0, t1 = S[5]
sala("F", 200, (0.85, 0.88, 0.95, 1), (0.74, 0.78, 0.88, 1), (0.20, 0.45, 0.55, 1))
ttec = T(5, "técnicos"); tlim = T(5, "limites"); tgol = T(5, "golpe"); tpro = T(5, "problema"); tso = T(5, "Sony"); tms = T(5, "Microsoft"); trk = T(5, "Rockstar"); tcom = T(5, "comentaram")
for dx in (-1.8, 1.8): cilindro(_id("pedF"), (200.0 + dx, 2.0, 0.45), 0.9, 0.9, BRANCO, seg=20)
cS = console("consS", (198.2, 2.0, 1.6), 0.8)
cD = console("consD", (201.8, 2.0, 1.6), 0.8, (0.85, 0.85, 0.88, 1))
for k, (dx, dz, ry) in enumerate(((0.0, 0.3, 30), (0.12, 0.0, -35), (0.0, -0.3, 30))):
    r = caixa(_id("rachaF"), (201.8 + dx - 0.05, 1.5, 1.7 + dz), (0.06, 0.04, 0.36), ESCURO, unico="racha"); visivel(r, tlim)
ckF = check("checkF", (198.2, 1.4, 3.1), 0.9); visivel(ckF, tlim - 0.1); pop(ckF, tlim - 0.1, 0.9)
mart = vazio("martF", (202.6, 1.6, 3.2))
cabo_ = cilindro(_id("caboM"), (0, 0, 0), 0.08, 1.4, (0.55, 0.36, 0.20, 1), seg=8); filho(mart, cabo_); cabo_.location = (0.7, 0, 0); cabo_.rotation_euler = (0, math.radians(90), 0)
cab2 = caixa(_id("cabecaM"), (0, 0, 0), (0.4, 0.5, 0.7), CINZA); filho(mart, cab2); cab2.location = (0.0, 0, 0)
visivel(mart, tgol - 0.6, t1 + 0.3)
key(mart, "rotation_euler", tgol - 0.5, (0, math.radians(-60), 0)); key(mart, "rotation_euler", tgol + 0.05, (0, math.radians(15), 0)); key(mart, "rotation_euler", tgol + 0.6, (0, math.radians(-30), 0))
key(cD, "rotation_euler", tgol, (0, 0, math.radians(90))); key(cD, "rotation_euler", tgol + 0.3, (0, math.radians(-12), math.radians(90)))
fumaca("fumF", (201.8, 2.0, 2.3), tgol + 0.1, 4)
xF = xis("xF", (201.8, 1.4, 3.1), 0.9); visivel(xF, tpro - 0.1); pop(xF, tpro - 0.1, 1.0)
for k, tt in enumerate((tso, tms, trk)):
    b = balao(_id("balaoF"), (197.8 + k * 2.2, 1.0, 4.4), 0.8); visivel(b, tt - 0.1); b.scale = (1.25, 0.35, 0.9)
    b.scale = (0.001,) * 3; b.keyframe_insert("scale", frame=f(tt - 0.1)); b.scale = (1.25, 0.35, 0.9); b.keyframe_insert("scale", frame=f(tt + 0.25))
gF = pixel("guiaF", (196.0, 0.2, 0), escala=0.85); girarZ(gF["raiz"], 14); respirar(gF, t0, t1 + 0.5)
apontar(gF, ttec - 0.1, 1.3, "D", 40); apontar(gF, tgol - 0.3, 1.2, "D", 30); pensar(gF, tso - 0.1, 2.0)
plano(t0, (200.0, 2.0), "geral", altura=2.2); plano(tso - 0.4, (200.0, 2.0), "geral", altura=2.3)
plano(tso - 0.1, (200.0, 2.0), "geral", altura=3.0); plano(t1 - 0.05, (200.2, 2.0), "geral", altura=3.1)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA G (x = 240) — console na estante com espaço em volta (setas de ar); poeira voa; caixa de ferramentas (assistência) (bloco 6)
# =====================================================================
zona_ini()
t0, t1 = S[6]
sala("G", 240, (0.45, 0.75, 0.55, 1), (0.38, 0.66, 0.48, 1), (0.95, 0.55, 0.25, 1))
tprt = T(6, "proteger"); tesp = T(6, "espaço"); tvol = T(6, "volta"); tti = T(6, "tire"); tpoe6 = T(6, "poeira"); tdes = T(6, "desligar"); tass = T(6, "assistência")
caixa("rackG", (240.4, 2.2, 0.55), (3.6, 1.4, 1.1), (0.30, 0.22, 0.18, 1))
cG = console("consG", (240.4, 2.2, 2.05), 1.05)
for k, (dx, dz, rot) in enumerate(((-1.4, 2.0, 90), (1.4, 2.0, -90), (0.0, 3.4, 0))):
    s_ = seta3d(_id("setaG"), 1.2, CIANO); s_.location = (240.4 + dx, 1.6, dz); s_.rotation_euler = (0, math.radians(rot), 0)
    if k == 0: s_.rotation_euler = (0, math.radians(-90), 0)
    if k == 1: s_.rotation_euler = (0, math.radians(90), 0)
    tt = tesp - 0.1 + 0.15 * k; visivel(s_, tt, tti); pop(s_, tt, 0.5)
POE = []
for k in range(6):
    pz = poeira(_id("poG"), (239.6 + (k % 3) * 0.55, 1.6, 2.4 + (k // 3) * 0.45), 0.7); visivel(pz, t0, tpoe6 + 1.4); POE.append(pz)
    key(pz, "location", tpoe6 - 0.1 + 0.05 * k, tuple(pz.location)); key(pz, "location", tpoe6 + 1.2, (244.5 + k * 0.3, 0.8, 4.2 + 0.3 * k))
for k in range(5):
    w = esfera(_id("sopro"), (238.2, 1.4, 2.3), 0.1, (0.85, 0.95, 1.0, 1), sub=1, unico="sopro"); a = tpoe6 - 0.2 + 0.18 * k; visivel(w, a, a + 0.7)
    key(w, "location", a, (238.2, 1.4, 2.3)); key(w, "location", a + 0.7, (240.8, 1.5, 2.6))
fer = ferramentas("ferrG", (243.4, 1.4, 1.45), 0.9); visivel(fer, tass - 0.2); pop(fer, tass - 0.2, 0.9)
caixa("mesinhaG", (243.4, 1.4, 0.55), (1.8, 1.1, 1.1), (0.30, 0.22, 0.18, 1))
ckG = check("checkG", (243.4, 1.0, 3.3), 0.8); visivel(ckG, tass + 0.2); pop(ckG, tass + 0.2, 0.8)
gG = pixel("guiaG", (237.9, 0.3, 0), escala=0.85); girarZ(gG["raiz"], -10); respirar(gG, t0, t1 + 0.5)
acenar(gG, tprt - 0.2, 1.2); apontar(gG, tesp - 0.1, 1.3, "D", 40); apontar(gG, tpoe6 - 0.2, 1.2, "D", 60); apontar(gG, tass - 0.1, 1.3, "D", 20); comemorar(gG, tass + 0.4, 1.2)
plano(t0, (240.2, 1.8), "geral", altura=2.2); plano(t1 - 0.05, (240.6, 1.8), "geral", altura=2.3)
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
