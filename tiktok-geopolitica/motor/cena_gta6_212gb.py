"""Série 2 — 'Por que o GTA 6 pesa 212 GB?' (estilo C cartoon, mascote Pixel, visual nível 2).
Mecanismo: console + barra de armazenamento enchendo e '212 GB' gigante -> três pedestais (textura, som, cópias);
painel de 'pele' que passa de 4 ladrilhos borrados a 36 nítidos e barras de ouro empilhando -> caixa de som com ondas
e coluna de 12 blocos (9 laranja = áudio) + processador sem o pacote para descompactar -> HD mecânico (prato girando,
braço leitor) com árvores copiadas em vários cantos -> torre de blocos que encolhe de 154 para 23 (-85 %) ->
nuvem/servidor manda caixas ao console com cadeado que abre no lançamento -> roteador, barra de progresso e ampulheta
(~5 h) -> convite (CABE x APAGUEI).
Visual 100 % original: consoles, HD, roteador genéricos sem marca; nenhuma arte/personagem/logo/mapa de jogo.
Anti-borda: piso xadrez e parede alta com painéis. Melhoria do backlog (render NPCs): cada zona só fica 'renderizável'
durante o próprio bloco (zona_janela), o EEVEE não sincroniza as outras zonas.
Base: cena_gta6_pirata_pc.py. Uso: blender -b --factory-startup -P cena_gta6_212gb.py -- <pasta> [preview t1,t2 | range a,b]"""
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
random.seed(212)

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

# =====================================================================
# ZONA A (x = 0) — console + barra de espaço que enche até o vermelho + '212 GB' gigante (bloco 0 e CTA)
# =====================================================================
zona_ini()
t0, t1 = S[0]
sala("A", 0, (0.36, 0.40, 0.62, 1), (0.30, 0.34, 0.54, 1), (0.55, 0.38, 0.85, 1))
tdz = T(0, "doze"); tes = T(0, "espaço"); trk = T(0, "Rockstar"); tco = T(0, "console"); tpq = T(0, "Por"); tpe = T(0, "pesado")
caixa("mesaA", (0.4, 1.6, 1.0), (5.4, 1.3, 0.12), (0.30, 0.22, 0.18, 1))
for dx in (-2.4, 2.4): caixa(_id("peMesaA"), (0.4 + dx, 1.6, 0.48), (0.12, 1.0, 0.96), (0.18, 0.18, 0.22, 1))
cA = console("consA", (0.0, 1.7, 1.82), 0.9)
txA = texto3d("t212", "212 GB", (0.3, 1.2, 3.9), 1.25, AMARELO, 0.18); visivel(txA, 0.0); pop(txA, 0.02, 1.0, 0.45)
key(txA, "location", 0.5, (0.3, 1.2, 3.9)); key(txA, "location", tpe, (0.3, 1.2, 4.1))
mbA, fbA, mfA = barra("barraA", 2.2, 1.7, 1.15, 2.4, 0.6, VERDE)
encher(fbA, 0.0, 0.05, 0.05, 0.05); encher(fbA, tes - 0.1, tco + 0.3, 0.05, 1.0)
cor_key(mfA, tes - 0.1, VERDE); cor_key(mfA, tco + 0.3, VERMELHO)
iqA = interroga("interA", (-1.3, 1.4, 3.6), 0.8); visivel(iqA, tpq - 0.1, t1 + 0.1); pop(iqA, tpq - 0.1, 1.0)
# CTA (bloco 7): check verde (cabe) e lixeira (apaguei) com uma caixinha caindo dentro
tcb = T(7, "cabe"); tap = T(7, "apaguei"); tvc = T(7, "você"); t7 = S[7][0]
ckA = check("checkA", (-1.2, 1.1, 2.6), 1.2); visivel(ckA, tcb - 0.15); pop(ckA, tcb - 0.15, 1.2)
lxA = lixeira("lixeiraA", (2.4, 1.0, 1.65), 0.8); visivel(lxA, tap - 0.5); pop(lxA, tap - 0.5, 1.0)
cxA = caixa_lacrada("caixaA", (2.4, 1.0, 3.6), 0.5, (0.55, 0.65, 0.95, 1)); visivel(cxA, tap - 0.2, tap + 0.9); pop(cxA, tap - 0.2, 1.0)
key(cxA, "location", tap + 0.1, (2.4, 1.0, 3.6)); key(cxA, "location", tap + 0.75, (2.4, 1.0, 1.9))
encher(fbA, t7 - 0.1, t7, 1.0, 0.55); cor_key(mfA, t7 - 0.1, VERMELHO); cor_key(mfA, t7, AMARELO)
encher(fbA, tap + 0.6, tap + 1.0, 0.55, 0.3); cor_key(mfA, tap + 1.0, VERDE)
txA.scale = (1, 1, 1); sumir(txA, t1 - 0.2, 0.2)
px = pixel("pixel", (-2.4, 0.2, 0), escala=0.9); girarZ(px["raiz"], 14); respirar(px, 0, FIM)
espanto(px, 0.05, 1.3); apontar(px, tes - 0.1, 1.4, "D", 50); pensar(px, tpq - 0.1, 1.6)
acenar(px, t7 + 0.1, 1.4); apontar(px, tcb - 0.1, 1.2, "E", 40); apontar(px, tap - 0.1, 1.2, "D", 50)
acenar(px, LEG[-1]["e"] + 1.2, 1.6); comemorar(px, LEG[-1]["e"] + 3.0, 1.4)
plano(0, (0.2, 1.6), "geral", altura=2.4); plano(tes - 0.4, (0.2, 1.6), "geral", altura=2.4)
plano(tes - 0.05, (0.4, 1.5), "geral", altura=2.6); plano(t1 - 0.05, (0.6, 1.5), "geral", altura=2.6)
cam_key(t7, (0.0, -7.2, 2.8), (0.0, 1.4, 2.2)); cam_key(FIM, (0.3, -6.8, 2.8), (0.3, 1.4, 2.2))
zona_fim([(0.0, t1 + 0.3), (t7 - 0.3, FIM + 0.5)])

# =====================================================================
# ZONA B (x = 40) — três pedestais (textura, som, cópias); painel 'pele' de 4 ladrilhos -> 36 nítidos; ouro empilha (bloco 1)
# =====================================================================
zona_ini()
t0, t1 = S[1]
sala("B", 40, (0.95, 0.80, 0.45, 1), (0.88, 0.70, 0.38, 1), (0.25, 0.30, 0.55, 1))
ttr = T(1, "Três"); tpr = T(1, "Primeiro"); ttx = T(1, "texturas"); tpl = T(1, "peles"); tru = T(1, "ruas"); tca = T(1, "carros")
tqu = T(1, "Quanto"); tni = T(1, "nítidas"); tep = T(1, "espaço"); toc = T(1, "ocupam")
cores = [ROSA, CIANO, VERDE, AMARELO, LARANJA, ROXO]
# pedestais (plano geral)
PED = []
for k, cx_ in enumerate((37.4, 40.0, 42.6)):
    pd = cilindro(_id("pedB"), (cx_, 2.6, 0.5), 0.8, 1.0, BRANCO, seg=20); PED.append(pd)
    visivel(pd, t0); pop(pd, ttr - 0.1 + 0.15 * k, 1.0)
ic1 = caixa("icTex", (37.4, 2.6, 1.6), (0.9, 0.1, 0.9), ROSA)
for i in range(3):
    for j in range(3):
        if (i + j) % 2: q = caixa(_id("icTexQ"), (0, 0, 0), (0.3, 0.12, 0.3), BRANCO); filho(ic1, q); q.location = (-0.3 + i * 0.3, -0.01, -0.3 + j * 0.3)
ic2 = caixa_som("icSom", (40.0, 2.6, 1.75), 0.55)
ic3 = vazio("icCop", (42.6, 2.6, 1.05))
for k in range(3):
    a_ = arvorezinha(_id("icArv"), (0, 0, 0), 0.9); filho(ic3, a_); a_.location = (-0.45 + k * 0.45, 0, 0.2)
for k, ob in enumerate((ic1, ic2, ic3)):
    visivel(ob, ttr - 0.05 + 0.15 * k, tpr + 0.5); pop(ob, ttr - 0.05 + 0.15 * k, 1.0 if ob is not ic2 else 0.55)
for pd in PED: pd.scale = (1, 1, 1); sumir(pd, tpr + 0.3, 0.2)
# painel 'pele' sobre uma parede de 'rua' (carrinho genérico na frente)
pele_grossa = []
for i in range(2):
    for j in range(2):
        q = caixa(_id("peleG"), (37.6 + i * 1.6, 3.6, 1.6 + j * 1.6), (1.55, 0.1, 1.55), [(0.55, 0.55, 0.6, 1), (0.65, 0.62, 0.58, 1)][(i + j) % 2])
        visivel(q, ttx - 0.1, tni + 0.1); pop(q, ttx - 0.1 + 0.05 * (i + j), 1.0); pele_grossa.append(q)
for i in range(6):
    for j in range(6):
        q = caixa(_id("peleF"), (36.9 + i * 0.535, 3.55, 0.92 + j * 0.535), (0.5, 0.1, 0.5), cores[(i * 2 + j) % 6], unico=f"peleF{(i * 2 + j) % 6}")
        tt = tni + 0.02 * (i + j); visivel(q, tt); pop(q, tt, 1.0, 0.25)
carro = caixa("carroB", (39.2, 1.8, 0.55), (2.2, 1.0, 0.6), VERMELHO); liso(carro)
cab = caixa(_id("cabCarro"), (0, 0, 0), (1.1, 0.9, 0.5), (0.85, 0.15, 0.15, 1)); filho(carro, cab); cab.location = (-0.1, 0, 0.5)
for dx in (-0.7, 0.7):
    rd = cilindro(_id("roda"), (0, 0, 0), 0.28, 0.2, ESCURO, seg=12); filho(carro, rd); rd.location = (dx, -0.5, -0.3); rd.rotation_euler = (math.radians(90), 0, 0)
visivel(carro, tca - 0.15); pop(carro, tca - 0.15, 1.0)
# barras de ouro empilhando (espaço ocupado)
for k in range(8):
    ob = caixa(_id("ouroB"), (43.4 + (k % 2) * 0.9, 2.4, 0.25 + (k // 2) * 0.5), (0.85, 0.5, 0.45), OURO, unico="ouroB")
    tt = tep - 0.2 + 0.1 * k; visivel(ob, tt); pop(ob, tt, 1.0, 0.25)
BRILHO.append(mat(OURO, "ouroB"))
gB = pixel("guiaB", (41.4, 0.6, 0), escala=0.85); girarZ(gB["raiz"], -20); respirar(gB, t0, t1 + 0.5)
key(gB["raiz"], "location", t0, (44.2, 0.6, 0), interp="CONSTANT"); key(gB["raiz"], "location", tpr + 0.15, (41.4, 0.6, 0), interp="CONSTANT")
apontar(gB, ttx - 0.1, 1.4, "E", 60); espanto(gB, tni - 0.1, 1.2); apontar(gB, tep - 0.1, 1.4, "D", 30)
plano(t0, (40.0, 2.2), "geral", altura=2.2); plano(tpr - 0.2, (40.0, 2.2), "geral", altura=2.2)
plano(tpr + 0.15, (39.0, 2.0), "medio", altura=2.2); plano(tep - 0.5, (39.4, 2.0), "medio", altura=2.3)
plano(tep - 0.15, (41.6, 2.0), "geral", altura=2.0); plano(t1 - 0.05, (41.8, 2.0), "geral", altura=2.0)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA C (x = 80) — caixa de som com ondas; coluna de 12 blocos (9 laranja = 35 de 48); processador sem descompactar (bloco 2)
# =====================================================================
zona_ini()
t0, t1 = S[2]
sala("C", 80, (0.62, 0.72, 0.98, 1), (0.52, 0.62, 0.90, 1), (0.30, 0.20, 0.45, 1))
tso = T(2, "som"); tqo = T(2, "quarenta"); tpc = T(2, "PC"); ttc = T(2, "trinta"); tau = T(2, "áudio"); tsc = T(2, "compressão")
tmo = T(2, "motivo"); tna = T(2, "não"); tpro = T(2, "processador"); tde = T(2, "descompactando")
som = caixa_som("somC", (77.6, 2.2, 1.0), 1.0); visivel(som, t0); pop(som, tso - 0.1, 1.0)
for k in range(5):
    w = anel(_id("onda"), (77.6, 1.4, 1.45), 0.5, 0.05, CIANO, seg=24, unico="onda"); w.rotation_euler = (math.radians(90), 0, 0)
    tt = tso + k * 0.5; visivel(w, tt, tt + 1.2)
    w.scale = (0.4, 0.4, 0.4); w.keyframe_insert("scale", frame=f(tt)); w.scale = (2.2, 2.2, 2.2); w.keyframe_insert("scale", frame=f(tt + 1.2))
BRILHO.append(mat(CIANO, "onda"))
for k in range(12):
    cor = LARANJA if k >= 3 else CINZA
    ob = caixa(_id("blocoC"), (81.0, 2.2, 0.22 + k * 0.42), (1.1, 0.9, 0.38), cor, unico="bAud" if k >= 3 else "bRes")
    tt = (tqo - 0.1 + 0.06 * k) if k < 3 else (ttc - 0.2 + 0.07 * (k - 3)); visivel(ob, tqo - 0.1 + 0.06 * k); pop(ob, tqo - 0.1 + 0.06 * k, 1.0, 0.25)
mA = mat(LARANJA, "bAud"); cor_key(mA, ttc - 0.25, CINZA); cor_key(mA, ttc + 0.4, LARANJA)
chC = chip_cpu("chipC", (83.6, 2.0, 2.4), 1.2); visivel(chC, tmo - 0.15); pop(chC, tmo - 0.15, 1.0)
pkC = caixa_lacrada("pacoteC", (83.6, 1.4, 4.0), 0.6); visivel(pkC, tmo, tde + 0.8); pop(pkC, tmo, 1.0)
key(pkC, "location", tna - 0.1, (83.6, 1.4, 4.0)); key(pkC, "location", tde + 0.3, (84.2, 1.2, 3.6))
xC = xis("xC", (83.6, 1.1, 4.0), 1.2); visivel(xC, tna); pop(xC, tna, 1.0)
gC = pixel("guiaC", (79.0, -0.6, 0), escala=0.85); girarZ(gC["raiz"], 12); respirar(gC, t0, t1 + 0.5)
apontar(gC, tso - 0.1, 1.4, "E", 50); apontar(gC, tqo - 0.1, 1.4, "D", 70); espanto(gC, ttc - 0.1, 1.3); pensar(gC, tmo - 0.1, 1.4); apontar(gC, tpro - 0.1, 1.2, "D", 60)
plano(t0, (78.8, 1.8), "medio", altura=2.2); plano(tqo - 0.4, (79.0, 1.8), "medio", altura=2.2)
plano(tqo - 0.05, (80.2, 1.8), "geral", altura=2.6); plano(tmo - 0.4, (80.6, 1.8), "geral", altura=2.6)
plano(tmo - 0.05, (82.6, 1.6), "medio", altura=2.6); plano(t1 - 0.05, (82.8, 1.6), "medio", altura=2.6)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA D (x = 120) — HD mecânico: prato girando, braço leitor; árvores copiadas em vários cantos (bloco 3)
# =====================================================================
zona_ini()
t0, t1 = S[3]
sala("D", 120, (0.40, 0.30, 0.55, 1), (0.34, 0.25, 0.48, 1), (0.16, 0.22, 0.40, 1))
ttq = T(3, "truque"); tgu = T(3, "guardar"); tcp = T(3, "cópias"); thd = T(3, "HD"); tle = T(3, "leitor"); tme = T(3, "menos")
tar = T(3, "árvore"); tvr = T(3, "vários"); tdi = T(3, "disco")
caseD = caixa("caseHD", (120.0, 2.4, 0.15), (5.2, 4.0, 0.3), (0.55, 0.58, 0.64, 1))
prato = cilindro("pratoD", (120.0, 2.0, 0.42), 1.6, 0.08, PRATA, seg=40)
eixo = cilindro("eixoD", (120.0, 2.0, 0.5), 0.25, 0.1, CINZA, seg=16)
for k in range(3):
    tr_ = anel(_id("trilha"), (120.0, 2.0, 0.47), 0.6 + k * 0.32, 0.015, (0.6, 0.62, 0.68, 1), seg=40, unico="trilha")
    filho(prato, tr_); tr_.location = (0, 0, 0.05)
girar(prato, t0, 0.8)
braco = vazio("bracoPiv", (122.3, 3.6, 0.6))
bh = caixa(_id("braco"), (0, 0, 0), (0.18, 2.6, 0.08), AMARELO); filho(braco, bh); bh.location = (0, -1.3, 0)
cb_ = cilindro(_id("cabeca"), (0, 0, 0), 0.14, 0.12, VERMELHO, seg=10); filho(braco, cb_); cb_.location = (0, -2.55, -0.06)
girarZ(braco, -15)
for ob in (caseD, prato, eixo): visivel(ob, thd - 0.2); pop(ob, thd - 0.2, 1.0)
visivel(braco, thd - 0.2); pop(braco, thd - 0.1, 1.0)
# leitor: primeiro pulando longe (antes das cópias), depois quase parado
for k, ang in enumerate((-15, 25, -20, 30)):
    key(braco, "rotation_euler", tle - 0.2 + 0.25 * k, (0, 0, math.radians(ang)))
key(braco, "rotation_euler", tme + 0.1, (0, 0, math.radians(5))); key(braco, "rotation_euler", tdi + 0.5, (0, 0, math.radians(8)))
# arquivos 'caixa' do mesmo arquivo copiados (gancho do 'guardar cópias')
CP = []
for k in range(4):
    cx2 = caixa_lacrada(_id("copiaD"), (117.0 + k * 0.9, 1.6, 3.4), 0.55, (0.45, 0.80, 0.55, 1))
    tt = tcp - 0.1 + 0.12 * k; visivel(cx2, tt, thd - 0.1); pop(cx2, tt, 1.0); CP.append(cx2)
# árvores em vários cantos do disco
for k in range(6):
    ang = math.radians(30 + k * 60); r = 1.15
    a_ = arvorezinha(_id("arvD"), (120.0 + r * math.cos(ang), 2.0 + r * math.sin(ang), 0.68), 0.8)
    filho(prato, a_); a_.location = (r * math.cos(ang), r * math.sin(ang), 0.26)
    tt = tvr - 0.2 + 0.08 * k if k else tar - 0.05; visivel(a_, tt); pop(a_, tt, 0.8, 0.25)
gD = pixel("guiaD", (117.0, -0.6, 0), escala=0.85); girarZ(gD["raiz"], 20); respirar(gD, t0, t1 + 0.5)
pensar(gD, ttq - 0.1, 1.4); apontar(gD, tcp - 0.1, 1.4, "D", 60); apontar(gD, tle - 0.1, 1.4, "D", 30); comemorar(gD, tme, 1.2); apontar(gD, tvr - 0.1, 1.4, "D", 20)
plano(t0, (118.6, 2.2), "geral", altura=2.6); plano(thd - 0.4, (118.8, 2.2), "geral", altura=2.6)
cam_key(thd - 0.05, (119.6, -3.2, 4.2), (120.2, 2.2, 0.6)); cam_key(t1 - 0.05, (119.9, -2.9, 4.0), (120.2, 2.2, 0.6))
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA E (x = 160) — torre de blocos encolhe de 154 para 23 (cópias somem); '-85%' (bloco 4)
# =====================================================================
zona_ini()
t0, t1 = S[4]
sala("E", 160, (0.30, 0.32, 0.42, 1), (0.25, 0.27, 0.36, 1), (0.22, 0.16, 0.30, 1))
tqd = T(4, "Quando"); tti = T(4, "tirou"); tcai = T(4, "caiu"); tct = T(4, "cento"); tvt = T(4, "vinte"); tgg = T(4, "gigas"); toi = T(4, "Oitenta")
mbE, torre, mtE = barra("torreE", 159.0, 2.4, 0.0, 6.0, 1.6, ROXO, moldura=(0.18, 0.18, 0.24, 1))
encher(torre, t0, t0 + 0.05, 1.0, 1.0); encher(torre, tvt - 0.1, tvt + 0.7, 1.0, 23 / 154)
cor_key(mtE, tvt - 0.1, ROXO); cor_key(mtE, tvt + 0.7, VERDE)
ARV = []
for k in range(10):
    a_ = arvorezinha(_id("arvE"), (157.8 + (k % 5) * 0.6, 1.4, 0.6 + (k // 5) * 2.2), 0.9); ARV.append(a_)
    visivel(a_, t0, tti + 0.6 + 0.05 * k); sumir(a_, tti + 0.2 + 0.05 * k, 0.3)
mini = arvorezinha("arvUnica", (161.6, 1.6, 0.25), 1.2); visivel(mini, tti + 0.4); pop(mini, tti + 0.4, 1.2)
tx85 = texto3d("t85", "-85%", (159.4, 1.2, 3.3), 1.0, VERDE, 0.18); visivel(tx85, toi - 0.1); pop(tx85, toi - 0.1, 1.0)
gE = pixel("guiaE", (156.4, -0.6, 0), escala=0.85); girarZ(gE["raiz"], 12); respirar(gE, t0, t1 + 0.5)
apontar(gE, tqd - 0.1, 1.4, "D", 70); espanto(gE, tct - 0.1, 1.2); apontar(gE, tvt - 0.1, 1.4, "D", 30); comemorar(gE, toi - 0.1, 1.4)
plano(t0, (159.2, 2.2), "geral", altura=3.2); plano(tvt - 0.4, (159.2, 2.2), "geral", altura=3.0)
plano(tvt + 0.6, (159.8, 1.8), "medio", altura=2.2); plano(t1 - 0.05, (160.2, 1.8), "medio", altura=2.3)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA F (x = 200) — nuvem/servidor manda caixas ao console; calendário; cadeado que abre no lançamento (bloco 5)
# =====================================================================
zona_ini()
t0, t1 = S[5]
sala("F", 200, (0.85, 0.88, 0.95, 1), (0.74, 0.78, 0.88, 1), (0.20, 0.45, 0.55, 1))
tba = T(5, "baixar"); tpc5 = T(5, "pré-carga"); tdz5 = T(5, "dez"); tno = T(5, "nove"); tst = T(5, "estreia"); tch = T(5, "chega")
ttk = T(5, "trancado"); tla = T(5, "lançamento")
nv = nuvemzinha("nuvemF", (196.4, 2.6, 4.4), 1.0); visivel(nv, t0); pop(nv, t0 + 0.05, 1.0)
srvF = servidor("srvF", (196.4, 2.6, 1.3), 1.0, CIANO, "ledSrvF")
cF = console("consF", (203.6, 2.0, 0.85), 1.1)
for k in range(7):
    bx = caixa_lacrada(_id("pctF"), (196.4, 1.6, 2.6), 0.45, [AMARELO, ROSA, CIANO, VERDE][k % 4])
    a, b = tba - 0.1 + 0.55 * k, tba - 0.1 + 0.55 * k + 1.1
    visivel(bx, a, b)
    caminho(bx, a, b, lambda u: bez((196.4, 1.6, 2.6), (200.0, 1.4, 4.2), (203.6, 1.4, 1.9), u), orientar=False, passo=2)
calF = calendario("calF", (200.0, 3.6, 4.6), 1.0); visivel(calF, tdz5 - 0.2); pop(calF, tdz5 - 0.2, 1.0)
for k in range(4):
    pg = caixa(_id("folhaF"), (200.0, 3.45, 4.4), (1.5, 0.04, 1.3), BRANCO); tt = tno + k * 0.22
    visivel(pg, tt, tt + 0.4)
    key(pg, "location", tt, (200.0, 3.45, 4.4)); key(pg, "location", tt + 0.4, (200.8, 2.6, 6.0))
cdF, alF = cadeado("cadeadoF", (203.6, 1.0, 2.1), 0.9); visivel(cdF, ttk - 0.2, tla + 1.0); pop(cdF, ttk - 0.2, 1.0)
key(alF, "location", tla - 0.05, (0, 0, 0.32)); key(alF, "location", tla + 0.3, (0, 0, 0.62))
key(cdF, "location", tla + 0.4, (203.6, 1.0, 2.1)); key(cdF, "location", tla + 1.0, (204.6, 0.6, 0.3))
ckF = check("checkF", (203.6, 1.0, 3.0), 1.0); visivel(ckF, tla + 0.3); pop(ckF, tla + 0.3, 1.0)
gF = pixel("guiaF", (199.6, -1.2, 0), escala=0.85); girarZ(gF["raiz"], 0); respirar(gF, t0, t1 + 0.5)
pensar(gF, tba - 0.1, 1.2); apontar(gF, tpc5 - 0.1, 1.4, "E", 50); apontar(gF, tdz5 - 0.1, 1.2, "D", 70); apontar(gF, tch - 0.1, 1.2, "D", 40); comemorar(gF, tla, 1.4)
plano(t0, (200.0, 2.4), "geral", altura=2.8); plano(ttk - 0.6, (200.0, 2.4), "geral", altura=2.8)
plano(ttk - 0.25, (202.6, 1.6), "medio", altura=2.0); plano(t1 - 0.05, (202.8, 1.6), "medio", altura=2.1)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA G (x = 240) — roteador -> console; barra de progresso; ampulheta virando; '~5 H' (bloco 6)
# =====================================================================
zona_ini()
t0, t1 = S[6]
sala("G", 240, (0.45, 0.75, 0.55, 1), (0.38, 0.66, 0.48, 1), (0.95, 0.55, 0.25, 1))
tin = T(6, "internet"); tcem = T(6, "cem"); tdu = T(6, "duzentos"); tqs = T(6, "quase"); tcin = T(6, "cinco"); tcr = T(6, "cair")
rt = roteador("roteadorG", (237.0, 1.6, 1.3), 1.0)
caixa("mesinhaG", (237.0, 1.6, 0.55), (2.0, 1.2, 1.1), (0.30, 0.22, 0.18, 1))
cG = console("consG", (243.0, 1.8, 0.85), 1.1)
for k in range(10):
    sx = caixa(_id("bitG"), (237.8, 1.6, 1.5), (0.22, 0.22, 0.22), CIANO, unico="bitG")
    a = t0 + 0.4 * k; b = a + 1.0; visivel(sx, a, b)
    key(sx, "location", a, (237.8, 1.6, 1.5)); key(sx, "location", b, (242.4, 1.6, 1.4), interp="LINEAR")
BRILHO.append(mat(CIANO, "bitG"))
pb_m = caixa("progMold", (240.0, 2.6, 3.6), (4.6, 0.15, 0.6), ESCURO)
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.translate(bm, vec=Vector((0.5, 0, 0)), verts=bm.verts)
bmesh.ops.scale(bm, vec=Vector((4.4, 0.2, 0.44)), verts=bm.verts)
me = bpy.data.meshes.new("progG"); bm.to_mesh(me); bm.free()
prog = bpy.data.objects.new("progG", me); bpy.context.collection.objects.link(prog); prog.location = (237.8, 2.45, 3.6)
mP = mat(VERDE, "progG"); prog.data.materials.append(mP); BRILHO.append(mP)
prog.scale = (0.02, 1, 1); prog.keyframe_insert("scale", frame=f(tcem - 0.1))
prog.scale = (1.0, 1, 1); prog.keyframe_insert("scale", frame=f(tcr + 0.2))
amp = ampulheta("ampG", (244.2, 1.2, 3.4), 0.9); visivel(amp, tdu - 0.2); pop(amp, tdu - 0.2, 0.9)
for k in range(3):
    key(amp, "rotation_euler", tdu + 0.9 * k, (0, math.radians(180 * k), 0))
tx5 = texto3d("t5h", "~5 H", (240.0, 1.6, 5.0), 1.2, AMARELO, 0.18); visivel(tx5, tcin - 0.1); pop(tx5, tcin - 0.1, 1.0)
gG = pixel("guiaG", (235.0, -0.6, 0), escala=0.85); girarZ(gG["raiz"], 18); respirar(gG, t0, t1 + 0.5)
apontar(gG, tin - 0.1, 1.4, "D", 40); pensar(gG, tdu - 0.1, 1.4); espanto(gG, tcin - 0.1, 1.2)
plano(t0, (239.6, 2.2), "geral", altura=2.8); plano(t1 - 0.05, (240.0, 2.2), "geral", altura=3.0)
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
