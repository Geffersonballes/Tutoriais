"""Série 2 — 'Por que o jogo que você comprou pode morrer?' (estilo C cartoon, mascote Pixel, visual nível 2).
Mecanismo: TV + console + disco; '31/03/2024' e a tela apaga (X vermelho) -> lápide e '?' -> servidor manda bits ao
console (conta, progresso, partidas); servidor desliga, LEDs ficam vermelhos e o console 'fala sozinho' (balão) ->
estante de jogos: um some da biblioteca; placas de protesto ('parem de matar jogos') -> Congresso genérico + documento
'PL 3612', calendário '180 DIAS' e escudo '2 ANOS' -> três pedestais (versão sem internet, servidores da comunidade,
moedas de volta) -> martelo bate, 'R$ 500 MIL' / 'OU 1%', jogos grátis e de assinatura saem do círculo ->
plataformas CÂMARA -> SENADO com o documento caminhando e ampulheta -> convite (SALVA x DESLIGA).
Visual 100 % original: nenhum carro, logo, capa ou arte de The Crew/Ubisoft; objetos genéricos sem marca.
Melhoria do backlog (matchmaking, 'tábua vazia no início do bloco'): o objeto principal de cada zona já está em cena
no corte (nasce em t0 do bloco), e os detalhes entram na palavra.
Base: cena_gta6_212gb.py (zonas só renderizam no próprio bloco; quadros prontos são pulados).
Uso: blender -b --factory-startup -P cena_jogo_comprado.py -- <pasta> [preview t1,t2 | range a,b]"""
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
random.seed(3612)

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

cam, alvo, cam_key, plano = camera_cartoon(24)

# ---------------------------------------------------------------- modelos novos deste vídeo (genéricos)
def disco(nome, loc, s=1.0):
    d = cilindro(nome, loc, 0.5 * s, 0.03 * s, PRATA, seg=32); d.rotation_euler = (math.radians(90), 0, 0)
    fu = cilindro(_id("furoD"), (0, 0, 0), 0.1 * s, 0.035 * s, ESCURO, seg=16); filho(d, fu)
    an = anel(_id("brilhoD"), (0, 0, 0), 0.32 * s, 0.025 * s, (0.75, 0.85, 1.0, 1), seg=32, unico="brilhoD"); filho(d, an)
    an.rotation_euler = (0, 0, 0); an.location = (0, 0, 0.02 * s)
    return d

def tv(nome, loc, s=1.0, cor_tela=CIANO, unico="telaTV"):
    c = caixa(nome, loc, (3.0 * s, 0.15 * s, 1.75 * s), ESCURO); liso(c)
    tl = caixa(_id("telaTV"), (0, 0, 0), (2.8 * s, 0.04 * s, 1.55 * s), cor_tela, unico=unico); filho(c, tl); tl.location = (0, -0.09 * s, 0)
    pe = caixa(_id("peTV"), (0, 0, 0), (0.25 * s, 0.25 * s, 0.5 * s), ESCURO); filho(c, pe); pe.location = (0, 0.05 * s, -1.05 * s)
    return c, mat(cor_tela, unico)

def lapide(nome, loc, s=1.0):
    b = caixa(nome, loc, (1.1 * s, 0.35 * s, 1.1 * s), (0.62, 0.64, 0.70, 1)); liso(b)
    tp = cilindro(_id("topoLap"), (0, 0, 0), 0.55 * s, 0.35 * s, (0.62, 0.64, 0.70, 1), seg=20); filho(b, tp)
    tp.rotation_euler = (math.radians(90), 0, 0); tp.location = (0, 0, 0.55 * s)
    for k in range(3):
        r = caixa(_id("riscoLap"), (0, 0, 0), ((0.7 - 0.15 * k) * s, 0.05 * s, 0.08 * s), (0.42, 0.44, 0.50, 1), unico="riscoLap"); filho(b, r)
        r.location = (0, -0.18 * s, (0.45 - 0.3 * k) * s)
    gr = caixa(_id("gramaLap"), (0, 0, 0), (1.6 * s, 0.8 * s, 0.15 * s), (0.30, 0.65, 0.30, 1)); filho(b, gr); gr.location = (0, 0, -0.55 * s)
    return b

def servidor_anim(nome, loc, s=1.0, unico="ledAnim"):
    """Rack com LEDs de cor animável (sem emissão, que fixaria a cor)."""
    r = caixa(nome, loc, (1.3 * s, 1.0 * s, 2.8 * s), (0.14, 0.15, 0.20, 1)); liso(r)
    for j in range(6):
        l = caixa(_id("ledA"), (0, 0, 0), (1.0 * s, 0.04 * s, 0.12 * s), VERDE, unico=unico); filho(r, l); l.location = (0, -0.52 * s, (-1.05 + j * 0.42) * s)
    return r, mat(VERDE, unico)

def balao(nome, loc, s=1.0):
    b = esfera(nome, loc, 0.7 * s, BRANCO, sub=3); b.scale = (1.4, 0.35, 0.85); liso(b)
    pt = cilindro(_id("pontaBal"), (0, 0, 0), 0.2, 0.5, BRANCO, seg=8, r2=0.0); filho(b, pt); pt.location = (-0.35, 0, -0.75); pt.rotation_euler = (0, math.radians(200), 0)
    for k in range(3):
        d = esfera(_id("ptoBal"), (0, 0, 0), 0.12, ESCURO, sub=1, unico="ptoBal"); filho(b, d); d.location = (-0.42 + 0.42 * k, -0.6, 0); d.scale = (0.7, 2.6, 1.15)
    return b

def caixinha_jogo(nome, loc, cor, s=1.0, unico=None):
    c = caixa(nome, loc, (0.42 * s, 0.3 * s, 0.6 * s), cor, unico=unico)
    cp = caixa(_id("capaJ"), (0, 0, 0), (0.3 * s, 0.02 * s, 0.32 * s), BRANCO, unico="capaJ"); filho(c, cp); cp.location = (0, -0.16 * s, 0.05 * s)
    return c

def placa(nome, loc, cor, s=1.0):
    h = cilindro(nome, loc, 0.05 * s, 1.6 * s, (0.55, 0.38, 0.22, 1), seg=6)
    p = caixa(_id("placaP"), (0, 0, 0), (1.1 * s, 0.08 * s, 0.75 * s), cor); filho(h, p); p.location = (0, -0.06 * s, 0.95 * s)
    for k in range(2):
        r = caixa(_id("letraP"), (0, 0, 0), ((0.8 - 0.25 * k) * s, 0.03 * s, 0.1 * s), BRANCO, unico="letraP"); filho(p, r); r.location = (0, -0.05 * s, (0.15 - 0.3 * k) * s)
    return h

def megafone(nome, loc, s=1.0):
    m = cilindro(nome, loc, 0.12 * s, 0.9 * s, VERMELHO, seg=14, r2=0.42 * s); m.rotation_euler = (0, math.radians(90), 0); return m

def congresso(nome, x, y, s=1.0, cor=(0.93, 0.93, 0.96, 1)):
    """Prédio legislativo genérico: torres gêmeas, laje, cúpula e 'tigela' invertida."""
    base = caixa(nome, (x, y, 0.25 * s), (9.0 * s, 2.2 * s, 0.5 * s), cor)
    for dx in (-0.45, 0.45):
        t = caixa(_id("torreC"), (0, 0, 0), (0.7 * s, 0.7 * s, 5.0 * s), cor); filho(base, t); t.location = (dx * s, 0.3 * s, 2.7 * s)
        for k in range(10):
            j = caixa(_id("janC"), (0, 0, 0), (0.55 * s, 0.05 * s, 0.12 * s), (0.45, 0.70, 0.95, 1), unico="janC"); filho(t, j); j.location = (0, -0.36 * s, (-2.1 + k * 0.45) * s)
    cu = esfera(_id("cupula"), (0, 0, 0), 1.0 * s, cor, sub=3); filho(base, cu); cu.location = (-2.8 * s, 0, 0.3 * s); cu.scale = (1, 1, 0.6); liso(cu)
    tg = cilindro(_id("tigela"), (0, 0, 0), 0.5 * s, 0.8 * s, cor, seg=24, r2=1.5 * s); filho(base, tg); tg.location = (2.8 * s, 0, 0.65 * s)
    return base

def bandeira_br(nome, loc, s=1.0):
    h = cilindro(nome, loc, 0.04 * s, 2.4 * s, CINZA, seg=6)
    b = caixa(_id("bandV"), (0, 0, 0), (1.2 * s, 0.05 * s, 0.8 * s), (0.10, 0.60, 0.25, 1)); filho(h, b); b.location = (0.62 * s, 0, 0.8 * s)
    l = caixa(_id("bandL"), (0, 0, 0), (0.55 * s, 0.06 * s, 0.55 * s), (1.0, 0.85, 0.10, 1)); filho(b, l); l.rotation_euler = (0, math.radians(45), 0)
    c = cilindro(_id("bandC"), (0, 0, 0), 0.2 * s, 0.07 * s, (0.10, 0.25, 0.70, 1), seg=16); filho(b, c); c.rotation_euler = (math.radians(90), 0, 0)
    return h

def documento(nome, loc, s=1.0, txt="PL 3612"):
    d = caixa(nome, loc, (1.5 * s, 0.06 * s, 2.0 * s), BRANCO); liso(d)
    for k in range(5):
        r = caixa(_id("linhaDoc"), (0, 0, 0), ((1.1 - 0.12 * (k % 2)) * s, 0.02 * s, 0.07 * s), (0.55, 0.58, 0.65, 1), unico="linhaDoc"); filho(d, r)
        r.location = (0, -0.04 * s, (-0.1 - 0.22 * k) * s)
    tx = texto3d(_id("txDoc"), txt, (0, 0, 0), 0.38 * s, (0.15, 0.30, 0.75, 1), 0.04); filho(d, tx); tx.location = (0, -0.06 * s, 0.55 * s)
    return d

def escudo(nome, loc, s=1.0, cor=VERDE):
    e = cilindro(nome, loc, 0.8 * s, 0.2 * s, cor, seg=6); e.rotation_euler = (math.radians(90), 0, 0); e.scale = (1, 1.25, 1); liso(e)
    return e

def moeda(nome, loc, s=1.0):
    m = cilindro(nome, loc, 0.32 * s, 0.1 * s, OURO, seg=20, unico="moeda"); return m

def martelo(nome, loc, s=1.0):
    """Martelo de juiz: pivô no cabo."""
    pv = vazio(nome, loc)
    cb = cilindro(_id("caboM"), (0, 0, 0), 0.07 * s, 1.6 * s, (0.55, 0.32, 0.16, 1), seg=8); filho(pv, cb); cb.rotation_euler = (0, math.radians(90), 0); cb.location = (-0.8 * s, 0, 0)
    cab = cilindro(_id("cabM"), (0, 0, 0), 0.28 * s, 0.9 * s, (0.45, 0.25, 0.12, 1), seg=14); filho(pv, cab); cab.location = (-1.6 * s, 0, 0)
    for dz in (-0.35, 0.35):
        an = cilindro(_id("aroM"), (0, 0, 0), 0.3 * s, 0.08 * s, OURO, seg=14); filho(cab, an); an.location = (0, 0, dz * s)
    return pv

def botao_power(nome, loc, s=1.0):
    b = cilindro(nome, loc, 0.6 * s, 0.25 * s, VERMELHO, seg=24); b.rotation_euler = (math.radians(90), 0, 0); liso(b)
    a = anel(_id("anelPw"), (0, 0, 0), 0.32 * s, 0.05 * s, BRANCO, seg=24, unico="brPw"); filho(b, a); a.location = (0, 0, 0.14 * s)
    r = caixa(_id("hastePw"), (0, 0, 0), (0.1 * s, 0.3 * s, 0.08 * s), BRANCO, unico="brPw"); filho(b, r); r.location = (0, 0.32 * s, 0.17 * s)
    return b

def plataforma(nome, x, y, cor, rot, s=1.0):
    p = cilindro(nome, (x, y, 0.3), 1.6 * s, 0.6, cor, seg=24); liso(p)
    t = texto3d(_id("txPlat"), rot, (x, y - 1.6 * s - 0.1, 0.95), 0.36 * s, BRANCO, 0.08)
    return p, t

# =====================================================================
# ZONA A (x = 0) — TV + console + disco; '31/03/2024'; tela apaga; lápide e '?' (bloco 0) + CTA (bloco 7)
# =====================================================================
zona_ini()
t0, t1 = S[0]
sala("A", 0, (0.36, 0.40, 0.62, 1), (0.26, 0.30, 0.50, 1), (0.55, 0.38, 0.85, 1))
tma = T(0, "março"); tcr = T(0, "Crew"); tpa = T(0, "parou"); tdi = T(0, "disco"); tcm = T(0, "Como"); tmo = T(0, "morrer")
caixa("mesaA", (0.4, 2.2, 0.5), (5.6, 1.4, 1.0), (0.30, 0.22, 0.18, 1))
tvA, mTela = tv("tvA", (0.6, 2.7, 2.15), 1.0)
cor_key(mTela, 0.0, CIANO); cor_key(mTela, tpa - 0.05, CIANO); cor_key(mTela, tpa + 0.35, (0.08, 0.08, 0.10, 1))
cor_key(mTela, S[7][0] - 0.1, (0.08, 0.08, 0.10, 1)); cor_key(mTela, S[7][0] + 0.3, CIANO)
cA = console("consA", (-1.6, 1.9, 1.75), 0.8)
dA = disco("discoA", (-1.6, 1.2, 3.2), 1.1); visivel(dA, 0.0, tdi + 0.6); pop(dA, 0.02, 1.0, 0.4)
key(dA, "location", 0.4, (-1.6, 1.2, 3.2)); key(dA, "location", tdi - 0.2, (-1.6, 1.2, 3.0)); key(dA, "location", tdi + 0.5, (-1.6, 1.5, 1.9))
txD = texto3d("tData", "31/03/2024", (1.2, 1.4, 4.1), 0.62, AMARELO, 0.12); visivel(txD, 0.0, tcm); pop(txD, 0.02, 1.0, 0.45)
xA = xis("xA", (0.6, 2.5, 2.15), 1.6); visivel(xA, tpa, tcm + 0.2); pop(xA, tpa, 1.0)
lpA = lapide("lapideA", (2.9, 1.2, 0.65), 1.0); visivel(lpA, tcm - 0.15, t1 + 0.1); pop(lpA, tcm - 0.15, 1.0)
iqA = interroga("interA", (2.9, 1.0, 2.6), 0.6); visivel(iqA, tmo - 0.3, t1 + 0.1); pop(iqA, tmo - 0.3, 1.0)
# CTA (bloco 7): check verde (salva) e botão de desligar (desliga)
tsa = T(7, "salva"); tdl = T(7, "desliga"); t7 = S[7][0]
ckA = check("checkA", (-1.6, 1.0, 3.3), 1.2); visivel(ckA, tsa - 0.2); pop(ckA, tsa - 0.2, 1.2)
pwA = botao_power("powerA", (2.8, 1.0, 1.7), 1.0); visivel(pwA, tdl - 0.6); pop(pwA, tdl - 0.6, 1.0)
key(pwA, "location", tdl - 0.05, (2.8, 1.0, 1.7)); key(pwA, "location", tdl + 0.15, (2.8, 1.15, 1.7)); key(pwA, "location", tdl + 0.4, (2.8, 1.0, 1.7))
px = pixel("pixel", (-2.5, 0.2, 0), escala=0.9); girarZ(px["raiz"], 14); respirar(px, 0, FIM)
apontar(px, 0.1, 1.4, "D", 60); espanto(px, tpa - 0.05, 1.3); pensar(px, tcm - 0.1, 1.6)
acenar(px, t7 + 0.1, 1.4); apontar(px, tsa - 0.2, 1.2, "D", 70); apontar(px, tdl - 0.2, 1.2, "D", 30)
acenar(px, LEG[-1]["e"] + 1.2, 1.6); comemorar(px, LEG[-1]["e"] + 3.0, 1.4)
plano(0, (-0.2, 1.8), "geral", altura=2.4); plano(tpa - 0.3, (0.0, 1.8), "geral", altura=2.4)
plano(tpa + 0.1, (0.3, 1.8), "medio", altura=2.3); plano(tcm - 0.25, (0.5, 1.8), "medio", altura=2.3)
plano(tcm - 0.05, (1.0, 1.6), "geral", altura=2.2); plano(t1 - 0.05, (1.2, 1.6), "geral", altura=2.2)
cam_key(t7, (-0.2, -7.4, 2.8), (-0.2, 1.4, 2.2)); cam_key(FIM, (0.1, -7.0, 2.8), (0.1, 1.4, 2.2))
zona_fim([(0.0, t1 + 0.3), (t7 - 0.3, FIM + 0.5)])

# =====================================================================
# ZONA B (x = 40) — servidor -> bits -> console; conta, progresso, partidas; servidor desliga; balão '...' (bloco 1)
# =====================================================================
zona_ini()
t0, t1 = S[1]
sala("B", 40, (0.62, 0.72, 0.98, 1), (0.50, 0.60, 0.90, 1), (0.20, 0.24, 0.42, 1))
tsv = T(1, "servidor"); tcn = T(1, "conectados"); tct = T(1, "conta"); tpg = T(1, "progresso"); tpt = T(1, "partidas")
tdg = T(1, "Desligou"); tfa = T(1, "falando")
srvB, mLed = servidor_anim("srvB", (37.5, 2.4, 1.4), 1.1)
cor_key(mLed, t0, VERDE); cor_key(mLed, tdg - 0.05, VERDE); cor_key(mLed, tdg + 0.25, VERMELHO)
caixa("mesinhaB", (42.9, 1.8, 0.5), (2.4, 1.3, 1.0), (0.30, 0.22, 0.18, 1))
cB = console("consB", (42.9, 1.8, 1.75), 0.9)
caboB = caixa("caboB", (40.2, 2.0, 0.08), (5.0, 0.12, 0.08), ESCURO)
pulsoB = []
k = 0
while True:
    a = tcn - 0.3 + 0.45 * k
    if a > tdg - 0.6: break
    bt = caixa(_id("bitB"), (37.4, 2.0, 1.2), (0.26, 0.26, 0.26), CIANO, unico="bitB")
    visivel(bt, a, a + 1.1)
    caminho(bt, a, a + 1.1, lambda u: bez((38.2, 1.8, 1.4), (40.4, 1.6, 3.2), (42.5, 1.8, 1.9), u), orientar=False, passo=2)
    k += 1
BRILHO.append(mat(CIANO, "bitB"))
# ícones: conta (crachá), progresso (barra), partidas (duas bolinhas frente a frente)
icC = caixa("cracha", (38.4, 1.6, 3.9), (0.9, 0.08, 1.1), AZUL); liso(icC)
cab_ = esfera(_id("cabCr"), (0, 0, 0), 0.2, BRANCO, sub=2); filho(icC, cab_); cab_.location = (0, -0.06, 0.18)
lin_ = caixa(_id("linCr"), (0, 0, 0), (0.6, 0.03, 0.1), BRANCO); filho(icC, lin_); lin_.location = (0, -0.06, -0.3)
visivel(icC, tct - 0.15, tdg + 0.3); pop(icC, tct - 0.15, 1.0)
mbB, fbB, mfB = barra("progB", 40.2, 1.6, 3.3, 1.3, 0.5, VERDE)
for o in (mbB, fbB): visivel(o, tpg - 0.15, tdg + 0.3)
pop(mbB, tpg - 0.15, 1.0); encher(fbB, tpg - 0.1, tpg + 0.8, 0.05, 1.0)
pa1 = esfera("partA", (41.7, 1.6, 3.9), 0.32, VERMELHO, sub=2); pa2 = esfera("partB", (42.5, 1.6, 3.9), 0.32, AZUL, sub=2)
for o in (pa1, pa2): visivel(o, tpt - 0.15, tdg + 0.3); pop(o, tpt - 0.15, 1.0)
xB = xis("xB", (40.1, 1.5, 2.6), 1.3); visivel(xB, tdg); pop(xB, tdg, 1.0)
for o in (icC, mbB, pa1, pa2):
    o.keyframe_insert("scale", frame=f(tdg - 0.05)); sc = tuple(o.scale); o.scale = (0.001,) * 3; o.keyframe_insert("scale", frame=f(tdg + 0.25)); o.scale = sc
fbB.scale = (1, 1, 1.0); fbB.keyframe_insert("scale", frame=f(tdg - 0.05)); fbB.scale = (1, 1, 0.001); fbB.keyframe_insert("scale", frame=f(tdg + 0.25))
blB = balao("balaoB", (43.0, 1.3, 3.2), 0.9); visivel(blB, tfa - 0.2); pop(blB, tfa - 0.2, 1.0)
gB = pixel("guiaB", (39.4, -0.4, 0), escala=0.85); girarZ(gB["raiz"], 8); respirar(gB, t0, t1 + 0.5)
apontar(gB, tsv - 0.15, 1.4, "E", 50); apontar(gB, tcn - 0.1, 1.4, "D", 40); comemorar(gB, tpt - 0.1, 1.0)
espanto(gB, tdg - 0.05, 1.3); pensar(gB, tfa - 0.1, 1.3)
plano(t0, (38.8, 2.0), "medio", altura=2.2); plano(tcn - 0.4, (39.4, 2.0), "medio", altura=2.3)
plano(tcn - 0.1, (40.2, 2.0), "geral", altura=2.5); plano(tdg - 0.1, (40.2, 2.0), "geral", altura=2.5)
plano(tdg + 0.3, (40.3, 1.9), "geral", altura=2.4); plano(t1 - 0.05, (40.5, 1.9), "geral", altura=2.4)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA C (x = 80) — estante 'biblioteca'; um jogo some; calendário; placas de protesto + megafone (bloco 2)
# =====================================================================
zona_ini()
t0, t1 = S[2]
sala("C", 80, (0.95, 0.80, 0.45, 1), (0.82, 0.62, 0.32, 1), (0.25, 0.30, 0.55, 1))
# anti-borda (QC 26/11): faixa de pôsteres coloridos acima do friso — nos closes da estante o topo ficava liso (desvio 1,7)
for k in range(17):
    caixa(_id("posterC"), (80 - 9.6 + k * 1.2, 4.38, 7.7 + (k % 3) * 0.35), (0.9, 0.06, 0.6), [ROSA, CIANO, AMARELO, VERDE, LARANJA][k % 5], unico=f"posterC{k % 5}")
tsm = T(2, "semanas"); tjg = T(2, "jogadores"); tsu = T(2, "sumiu"); tbi = T(2, "biblioteca"); tfo = T(2, "força")
tmv = T(2, "movimento"); tst = T(2, "Stop"); tpm = T(2, "parem"); tmt = T(2, "matar")
for k in range(3):
    caixa(_id("pratC"), (79.4, 3.4, 1.0 + k * 1.05), (4.6, 0.9, 0.1), (0.55, 0.36, 0.20, 1), unico="pratC")
for dx in (-2.35, 2.35): caixa(_id("ladoC"), (79.4 + dx, 3.4, 2.1), (0.12, 0.9, 2.4), (0.50, 0.32, 0.18, 1), unico="ladoC")
coresJ = [ROSA, CIANO, VERDE, AMARELO, LARANJA, ROXO, AZUL]
alvoJ = None
for k in range(3):
    for i in range(7):
        if k == 1 and i == 3:
            alvoJ = caixinha_jogo("jogoAlvo", (79.4 - 1.8 + i * 0.6, 3.25, 1.37 + k * 1.05), VERMELHO, 1.0); continue
        caixinha_jogo(_id("jogoC"), (79.4 - 1.8 + i * 0.6, 3.25, 1.37 + k * 1.05), coresJ[(i + 2 * k) % 7], 1.0, unico=f"jogoC{(i + 2 * k) % 7}")
destaque = anel("anelAlvo", (79.4, 2.7, 2.42), 0.55, 0.05, AMARELO, seg=24, unico="anelAlvo"); destaque.rotation_euler = (math.radians(90), 0, 0)
visivel(destaque, tjg - 0.2, tsu + 0.5); pop(destaque, tjg - 0.2, 1.0); BRILHO.append(mat(AMARELO, "anelAlvo"))
key(alvoJ, "location", tsu - 0.05, alvoJ.location.copy()); key(alvoJ, "location", tsu + 0.35, (79.4, 2.2, 2.42))
sumir(alvoJ, tsu + 0.35, 0.35)
iqC = interroga("interC", (79.4, 2.6, 2.4), 0.45); visivel(iqC, tbi - 0.1, tfo); pop(iqC, tbi - 0.1, 1.0)
calC = calendario("calC", (83.4, 3.6, 3.6), 0.8); visivel(calC, t0); pop(calC, t0 + 0.05, 1.0)
for k in range(4):
    pg = caixa(_id("folhaC"), (83.4, 3.45, 3.45), (1.2, 0.04, 1.05), BRANCO); tt = tsm + k * 0.2
    visivel(pg, tt, tt + 0.4)
    key(pg, "location", tt, (83.4, 3.45, 3.45)); key(pg, "location", tt + 0.4, (84.0, 2.6, 4.8))
coresP = [AMARELO, ROSA, CIANO, VERDE, LARANJA]
for k in range(5):
    pl = placa(_id("placaC"), (77.0 + k * 1.25, 0.9 - (k % 2) * 0.4, 0.8), coresP[k], 1.0)
    tt = tmv - 0.2 + 0.12 * k; visivel(pl, tt); pop(pl, tt, 1.0)
    for j in range(3):
        key(pl, "rotation_euler", tpm - 0.2 + 0.35 * j + 0.05 * k, (0, math.radians(8 if (j + k) % 2 else -8), 0))
mgC = megafone("megaC", (76.0, 0.6, 1.9), 1.0); visivel(mgC, tst - 0.2); pop(mgC, tst - 0.2, 1.0)
for k in range(3):
    w = anel(_id("ondaC"), (76.7, 0.6, 1.9), 0.4, 0.04, BRANCO, seg=20, unico="ondaC"); w.rotation_euler = (0, math.radians(90), 0)
    tt = tpm + k * 0.35; visivel(w, tt, tt + 0.8)
    w.scale = (0.5, 0.5, 0.5); w.keyframe_insert("scale", frame=f(tt)); w.scale = (2.0, 2.0, 2.0); w.keyframe_insert("scale", frame=f(tt + 0.8))
gC = pixel("guiaC", (82.6, -0.2, 0), escala=0.85); girarZ(gC["raiz"], -18); respirar(gC, t0, t1 + 0.5)
pensar(gC, t0 + 0.1, 1.2); apontar(gC, tjg - 0.1, 1.4, "E", 60); espanto(gC, tsu - 0.05, 1.3); comemorar(gC, tmv - 0.1, 1.4); acenar(gC, tpm, 1.2)
plano(t0, (80.6, 2.6), "medio", altura=2.4); plano(tjg - 0.3, (80.0, 2.6), "medio", altura=2.4)
plano(tjg - 0.05, (79.4, 2.4), "close", altura=2.3); plano(tfo - 0.2, (79.4, 2.4), "close", altura=2.3)
plano(tfo + 0.05, (79.2, 1.4), "geral", altura=2.0); plano(t1 - 0.05, (79.6, 1.4), "geral", altura=2.0)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA D (x = 120) — Congresso genérico + bandeira; documento 'PL 3612'; calendário '180 DIAS'; escudo '2 ANOS' (bloco 3)
# =====================================================================
zona_ini()
t0, t1 = S[3]
sala("D", 120, (0.45, 0.75, 0.55, 1), (0.36, 0.64, 0.46, 1), (0.30, 0.55, 0.85, 1))
tbr = T(3, "Brasil"); tpj = T(3, "projeto"); tav = T(3, "aviso"); tce = T(3, "cento"); tdia = T(3, "dias"); tdo = T(3, "dois"); tsp = T(3, "suporte")
cgD = congresso("congD", 120.0, 3.4, 0.55); visivel(cgD, t0); pop(cgD, t0 + 0.02, 0.55 / 0.55, 0.4)
bdD = bandeira_br("bandD", (116.4, 2.6, 1.2), 1.0); visivel(bdD, t0); pop(bdD, tbr - 0.2, 1.0)
docD = documento("docD", (120.0, 1.4, 2.0), 1.0); visivel(docD, tpj - 0.2); pop(docD, tpj - 0.2, 1.0)
key(docD, "location", tav - 0.2, (120.0, 1.4, 2.0)); key(docD, "location", tav + 0.3, (118.2, 1.4, 2.0))
calD = calendario("calD", (121.6, 1.4, 3.4), 0.8); visivel(calD, tav - 0.1); pop(calD, tav - 0.1, 1.0)
tx180 = texto3d("t180", "180 DIAS", (121.6, 1.2, 2.2), 0.42, AMARELO, 0.1); visivel(tx180, tce - 0.1); pop(tx180, tce - 0.1, 1.0)
esD = escudo("escD", (123.6, 1.4, 1.7), 0.9); visivel(esD, tdo - 0.2); pop(esD, tdo - 0.2, 1.0)
tx2a = texto3d("t2anos", "2 ANOS", (123.6, 1.15, 1.7), 0.36, BRANCO, 0.08); visivel(tx2a, tdo - 0.1); pop(tx2a, tdo - 0.1, 1.0)
gD = pixel("guiaD", (117.2, -0.6, 0), escala=0.85); girarZ(gD["raiz"], 16); respirar(gD, t0, t1 + 0.5)
comemorar(gD, tbr - 0.3, 1.3); apontar(gD, tpj - 0.1, 1.4, "D", 50); apontar(gD, tce - 0.1, 1.4, "D", 60); apontar(gD, tdo - 0.1, 1.4, "D", 40)
plano(t0, (120.0, 2.6), "geral", altura=3.0); plano(tpj - 0.3, (120.0, 2.4), "geral", altura=2.9)
plano(tpj + 0.05, (119.8, 1.6), "medio", altura=2.3); plano(tav - 0.1, (120.4, 1.6), "medio", altura=2.3)
plano(tav + 0.35, (120.9, 1.6), "geral", altura=2.2); plano(t1 - 0.05, (121.1, 1.6), "geral", altura=2.2)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA E (x = 160) — três pedestais: sem internet / servidores da comunidade / dinheiro de volta (bloco 4)
# =====================================================================
zona_ini()
t0, t1 = S[4]
sala("E", 160, (0.30, 0.32, 0.42, 1), (0.42, 0.44, 0.56, 1), (0.22, 0.16, 0.30, 1))
tes = T(4, "escolher"); tvs = T(4, "versão"); tin = T(4, "internet"); tfe = T(4, "ferramentas"); tcm4 = T(4, "comunidade")
tsv4 = T(4, "servidores"); tdv = T(4, "devolver"); tdn = T(4, "dinheiro")
PX = (157.2, 160.0, 162.8)
for k, cx_ in enumerate(PX):
    pd = cilindro(_id("pedE"), (cx_, 2.2, 0.5), 1.05, 1.0, [CIANO, VERDE, OURO][k], seg=24, unico=f"pedE{k}"); liso(pd)
    visivel(pd, t0); pop(pd, t0 + 0.05 + 0.1 * k, 1.0)
    tn = texto3d(_id("numE"), str(k + 1), (cx_, 1.1, 0.55), 0.5, BRANCO, 0.06); visivel(tn, t0); pop(tn, t0 + 0.1 + 0.1 * k, 1.0)
# 1) versão sem internet: console + roteador riscado
cE = console("consE", (157.2, 2.2, 1.75), 0.7); visivel(cE, tvs - 0.2); pop(cE, tvs - 0.2, 1.0)
rtE = roteador("rotE", (157.2, 1.4, 2.9), 0.6); visivel(rtE, tin - 0.25); pop(rtE, tin - 0.25, 1.0)
xE = xis("xE", (157.2, 1.1, 2.9), 0.9); visivel(xE, tin + 0.05); pop(xE, tin + 0.05, 1.0)
# 2) servidores da comunidade: 3 racks pequenos + chave inglesa (ferramenta) simplificada
for k in range(3):
    s_ = servidor(_id("srvE"), (159.3 + k * 0.7, 2.2, 1.55), 0.42, VERDE, "ledSrvE")
    tt = tsv4 - 0.2 + 0.1 * k; visivel(s_, tt); pop(s_, tt, 1.0)
chv = vazio("chaveE", (160.0, 1.3, 3.1))
cb = caixa(_id("caboCh"), (0, 0, 0), (0.18, 0.1, 1.0), CINZA); filho(chv, cb)
bc = anel(_id("bocaCh"), (0, 0, 0), 0.22, 0.08, CINZA, seg=12); filho(chv, bc); bc.location = (0, 0, 0.6); bc.rotation_euler = (math.radians(90), 0, 0)
chv.rotation_euler = (0, math.radians(35), 0); visivel(chv, tfe - 0.15); pop(chv, tfe - 0.15, 1.0)
key(chv, "rotation_euler", tcm4, (0, math.radians(35), 0)); key(chv, "rotation_euler", tcm4 + 0.4, (0, math.radians(-25), 0)); key(chv, "rotation_euler", tcm4 + 0.8, (0, math.radians(35), 0))
# 3) dinheiro de volta: moedas caindo e empilhando
for k in range(8):
    mo = moeda(_id("moedaE"), (162.8, 2.0, 1.05 + 0.11 * k), 1.0)
    tt = tdv - 0.1 + 0.12 * k; visivel(mo, tt)
    key(mo, "location", tt, (162.8 + (k % 2) * 0.05, 2.0, 4.0)); key(mo, "location", tt + 0.35, (162.8, 2.0, 1.05 + 0.11 * k))
BRILHO.append(mat(OURO, "moeda"))
gE = pixel("guiaE", (154.6, -0.6, 0), escala=0.85); girarZ(gE["raiz"], 22); respirar(gE, t0, t1 + 0.5)
pensar(gE, tes - 0.2, 1.4); apontar(gE, tvs - 0.1, 1.4, "D", 40); apontar(gE, tfe - 0.1, 1.4, "D", 60); apontar(gE, tdv - 0.1, 1.4, "D", 50)
plano(t0, (160.0, 2.0), "geral", altura=2.4); plano(tvs - 0.3, (159.6, 2.0), "geral", altura=2.4)
plano(tvs - 0.05, (157.6, 1.8), "medio", altura=2.2); plano(tfe - 0.4, (157.8, 1.8), "medio", altura=2.2)
plano(tfe - 0.05, (160.0, 1.8), "medio", altura=2.2); plano(tdv - 0.4, (160.2, 1.8), "medio", altura=2.2)
plano(tdv - 0.05, (161.6, 1.8), "medio", altura=2.2); plano(t1 - 0.05, (161.4, 1.9), "geral", altura=2.3)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA F (x = 200) — martelo bate; 'R$ 500 MIL' / 'OU 1%'; pilha de moedas; grátis e assinatura saem do círculo (bloco 5)
# =====================================================================
zona_ini()
t0, t1 = S[5]
sala("F", 200, (0.85, 0.55, 0.40, 1), (0.72, 0.44, 0.32, 1), (0.30, 0.20, 0.45, 1))
tqm = T(5, "Quem"); tml = T(5, "multa"); tqh = T(5, "quinhentos"); tum = T(5, "um"); tfat = T(5, "faturamento")
tgr = T(5, "gratuito"); tass = T(5, "assinatura"); tfr = T(5, "fora")
baseF = cilindro("baseMart", (196.6, 1.8, 1.15), 0.6, 0.25, (0.45, 0.25, 0.12, 1), seg=18)
caixa("mesaF", (198.0, 1.8, 0.5), (5.0, 1.4, 1.0), (0.30, 0.22, 0.18, 1))
mtF = martelo("martF", (198.3, 1.8, 1.9), 1.0)
key(mtF, "rotation_euler", t0, (0, math.radians(-40), 0))
for k, tb in enumerate((tml, tqh + 0.6)):
    key(mtF, "rotation_euler", tb - 0.35, (0, math.radians(-40), 0)); key(mtF, "rotation_euler", tb, (0, math.radians(10), 0), interp="LINEAR")
    key(mtF, "rotation_euler", tb + 0.3, (0, math.radians(-30), 0))
tx500 = texto3d("t500", "R$ 500 MIL", (200.6, 1.4, 4.4), 0.62, OURO, 0.12); visivel(tx500, tqh - 0.1); pop(tx500, tqh - 0.1, 1.0)
tx1 = texto3d("t1pc", "OU 1%", (200.6, 1.4, 3.5), 0.62, AMARELO, 0.12); visivel(tx1, tum - 0.1); pop(tx1, tum - 0.1, 1.0)
for k in range(10):
    mo = moeda(_id("moedaF"), (199.8 + (k // 5) * 0.75, 1.8, 1.05 + 0.11 * (k % 5)), 1.0)
    tt = tqh - 0.15 + 0.08 * k; visivel(mo, tt); pop(mo, tt, 1.0, 0.2)
# círculo da lei no chão + dois jogos (grátis, assinatura) que saem dele
cir = anel("circF", (203.2, 1.4, 0.05), 1.5, 0.08, AMARELO, seg=40, unico="circF"); BRILHO.append(mat(AMARELO, "circF"))
visivel(cir, t0); pop(cir, t0 + 0.05, 1.0)
jg1 = caixinha_jogo("jogoGratis", (202.7, 1.4, 0.45), VERDE, 1.4); jg2 = caixinha_jogo("jogoAss", (203.7, 1.4, 0.45), ROXO, 1.4)
for j_ in (jg1, jg2): visivel(j_, t0); pop(j_, t0 + 0.1, 1.0)
tg1 = texto3d("tGratis", "GRÁTIS", (202.4, 1.1, 1.35), 0.26, BRANCO, 0.05); tg2 = texto3d("tAss", "ASSINATURA", (204.0, 1.1, 1.35), 0.22, BRANCO, 0.05)
visivel(tg1, tgr - 0.1); pop(tg1, tgr - 0.1, 1.0); visivel(tg2, tass - 0.1); pop(tg2, tass - 0.1, 1.0)
for ob, de, para in ((jg1, (202.7, 1.4, 0.45), (200.9, 0.9, 0.45)), (jg2, (203.7, 1.4, 0.45), (205.5, 0.9, 0.45)),
                     (tg1, (202.4, 1.1, 1.35), (200.6, 0.6, 1.35)), (tg2, (204.0, 1.1, 1.35), (205.8, 0.6, 1.35))):
    key(ob, "location", tfr - 0.3, de); key(ob, "location", tfr + 0.3, para)
gF = pixel("guiaF", (195.0, -0.4, 0), escala=0.85); girarZ(gF["raiz"], 18); respirar(gF, t0, t1 + 0.5)
apontar(gF, tml - 0.1, 1.2, "D", 40); espanto(gF, tqh - 0.05, 1.3); apontar(gF, tgr - 0.1, 1.6, "D", 30)
plano(t0, (198.4, 2.0), "medio", altura=2.4); plano(tml + 0.2, (198.6, 2.0), "medio", altura=2.6)
plano(tqh - 0.05, (199.6, 1.8), "geral", altura=2.6); plano(tgr - 0.4, (200.2, 1.8), "geral", altura=2.6)
plano(tgr - 0.1, (202.8, 1.4), "medio", altura=1.6); plano(t1 - 0.05, (203.0, 1.4), "medio", altura=1.6)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA G (x = 240) — plataformas CÂMARA -> SENADO; documento caminha; sirene de urgência; ampulheta (bloco 6)
# =====================================================================
zona_ini()
t0, t1 = S[6]
sala("G", 240, (0.62, 0.72, 0.98, 1), (0.50, 0.60, 0.90, 1), (0.95, 0.55, 0.25, 1))
tcl = T(6, "calma"); tle = T(6, "lei"); ttr = T(6, "tramita"); tur = T(6, "urgência"); tcam = T(6, "Câmara"); tps = T(6, "passar"); tsn = T(6, "Senado")
p1, l1 = plataforma("platCam", 237.8, 2.4, AZUL, "CÂMARA", 0.8); p2, l2 = plataforma("platSen", 242.2, 2.4, ROXO, "SENADO", 0.8)
for o in (p1, l1, p2, l2): visivel(o, t0); pop(o, t0 + 0.05, 1.0)
ponte = caixa("ponteG", (240.0, 2.4, 0.45), (2.0, 0.9, 0.12), (0.95, 0.85, 0.55, 1)); visivel(ponte, t0)
docG = documento("docG", (237.8, 2.4, 1.6), 0.75); visivel(docG, t0); pop(docG, t0 + 0.1, 1.0)
key(docG, "location", ttr - 0.1, (237.8, 2.4, 1.6)); key(docG, "location", tcam + 0.2, (237.8, 2.4, 1.6))
caminho(docG, tps - 0.2, tsn + 0.5, lambda u: bez((237.8, 2.4, 1.6), (240.0, 2.4, 2.8), (242.2, 2.4, 1.6), u), orientar=False, passo=2)
sir = esfera("sireneG", (237.4, 2.0, 2.45), 0.2, VERMELHO, sub=2)
filho(docG, sir); sir.location = (0, 0, 1.0)
visivel(sir, tur - 0.1); pop(sir, tur - 0.1, 1.0)
for k in range(6):
    sir.scale = (1.4, 1.4, 1.4) if k % 2 == 0 else (1.0, 1.0, 1.0); sir.keyframe_insert("scale", frame=f(tur + 0.3 + 0.25 * k))
ampG = ampulheta("ampG", (240.0, 2.0, 3.9), 1.3); visivel(ampG, tcl - 0.2); pop(ampG, tcl - 0.2, 1.0)
for k in range(3):
    key(ampG, "rotation_euler", tcl + 0.9 * k, (0, math.radians(180 * k), 0))
cdG, alG = cadeado("cadG", (242.2, 1.6, 2.7), 0.8); visivel(cdG, tle - 0.1, tsn + 0.2); pop(cdG, tle - 0.1, 1.0)
gG = pixel("guiaG", (237.0, -0.9, 0), escala=0.8); girarZ(gG["raiz"], 14); respirar(gG, t0, t1 + 0.5)
acenar(gG, tcl - 0.1, 1.2); apontar(gG, tcam - 0.2, 1.2, "D", 30); apontar(gG, tsn - 0.2, 1.4, "D", 50)
plano(t0, (240.0, 2.2), "geral", altura=2.6); plano(tps - 0.3, (239.8, 2.2), "geral", altura=2.6)
plano(t1 - 0.05, (240.6, 2.2), "geral", altura=2.6)
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
