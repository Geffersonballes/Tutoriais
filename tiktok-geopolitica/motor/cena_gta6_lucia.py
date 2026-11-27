"""Série 2 — 'Por que ninguém quer salvar a Lucia no GTA 6?' (pauta do dono 27/11; estilo C cartoon, Pixel, visual nível 2).
Humor + mecanismo de design: o Pixel pescando de barco enquanto um relógio gira (15h/20h/30h) diante de uma prisão GENÉRICA
(sem nenhuma pessoa, sem arte/personagem/logo da Rockstar). Ciclo curto (joga, espera, puxa, ganha), recompensa variável
(cada puxada traz um prêmio diferente + caixa de Skinner), missão longa x vitória rápida, celular tocando e ônibus no píer,
mapa em miniatura cheio de atividades. CTA PARTIU x SÓ MAIS UMA.
Base: cena_gta6_consoles.py (zonas: cada zona só renderiza no próprio bloco). Anti-borda: mar com ondas, céu com nuvens/sol,
pisos xadrez de contraste alto (backlog gta6-pirata-pc). Uso: blender -b --factory-startup -P cena_gta6_lucia.py -- <pasta> [preview t1,t2 | range a,b]"""
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

def check(nome, loc, s=1.0, cor=VERDE):
    v = vazio(nome, loc); v.scale = (s, s, s)
    a = caixa(_id("chkA"), (0, 0, 0), (0.5, 0.14, 0.16), cor); filho(v, a); a.location = (-0.3, 0, 0.0); a.rotation_euler = (0, math.radians(45), 0)
    b = caixa(_id("chkB"), (0, 0, 0), (1.0, 0.14, 0.16), cor); filho(v, b); b.location = (0.12, 0, 0.18); b.rotation_euler = (0, math.radians(-55), 0)
    return v

def caixa_lacrada(nome, loc, s=1.0, cor=(0.78, 0.58, 0.34, 1)):
    c = caixa(nome, loc, (0.9 * s, 0.9 * s, 0.7 * s), cor); liso(c)
    f1 = caixa(_id("fita"), (0, 0, 0), (0.92 * s, 0.2 * s, 0.72 * s), (0.95, 0.30, 0.25, 1)); filho(c, f1)
    return c

def nuvemzinha(nome, loc, s=1.0):
    b = esfera(nome, loc, 0.9 * s, BRANCO, sub=2); liso(b)
    for dx, dz, r in ((0.9, -0.2, 0.65), (-0.9, -0.25, 0.6), (0.35, 0.5, 0.6)):
        e = esfera(_id("nuvz"), (0, 0, 0), r * s, BRANCO, sub=2); filho(b, e); e.location = (dx * s, 0, dz * s); liso(e)
    return b

def ampulheta(nome, loc, s=1.0):
    v = vazio(nome, loc)
    for dz in (-0.55, 0.55):
        t = cilindro(_id("tampaA"), (0, 0, 0), 0.45 * s, 0.1 * s, (0.45, 0.28, 0.14, 1), seg=14); filho(v, t); t.location = (0, 0, dz * s)
    for dz, r1, r2 in ((-0.25, 0.38, 0.06), (0.25, 0.06, 0.38)):
        c = cilindro(_id("vidro"), (0, 0, 0), r1 * s, 0.5 * s, (0.75, 0.90, 1.0, 1), seg=14, r2=r2 * s); filho(v, c); c.location = (0, 0, dz * s)
    ar = cilindro(_id("areia"), (0, 0, 0), 0.3 * s, 0.2 * s, OURO, seg=14, r2=0.05 * s); filho(v, ar); ar.location = (0, 0, -0.38 * s)
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

def led(nome, loc, cor, r=0.08):
    m = mat(cor, nome); e = esfera(nome, loc, r, cor, sub=1, unico=nome); return e, m

def piscar(m, t0, t1, c1, c2, per=0.4):
    t = t0; k = 0
    while t < t1:
        cor_key(m, t, c1 if k % 2 == 0 else c2, "CONSTANT"); t += per; k += 1

def arvorezinha(nome, loc, s=1.0):
    tr = cilindro(nome, loc, 0.08 * s, 0.4 * s, (0.45, 0.28, 0.14, 1), seg=6)
    cp = cilindro(_id("copaA"), (0, 0, 0), 0.32 * s, 0.7 * s, (0.25, 0.70, 0.30, 1), seg=8, r2=0.0, unico="copaA"); filho(tr, cp); cp.location = (0, 0, 0.5 * s)
    return tr

def cadeado(nome, loc, s=1.0, cor=OURO):
    c = caixa(nome, loc, (0.8 * s, 0.35 * s, 0.65 * s), cor); liso(c)
    a = anel(_id("alca"), (0, 0, 0), 0.28 * s, 0.07 * s, CINZA, seg=20); filho(c, a); a.location = (0, 0, 0.36 * s); a.rotation_euler = (math.radians(90), 0, 0)
    fu = esfera(_id("fur"), (0, 0, 0), 0.08 * s, ESCURO, sub=1); filho(c, fu); fu.location = (0, -0.18 * s, 0.03 * s)
    return c, a

# ---------------------------------------------------------------- modelos genéricos desta cena (sem marca)
MAR = (0.10, 0.55, 0.78, 1); AREIA = (0.95, 0.84, 0.58, 1); MADEIRA = (0.55, 0.36, 0.20, 1); GRAMA = (0.35, 0.75, 0.35, 1)

def peixe(nome, loc, s=1.0, cor=LARANJA):
    c = esfera(nome, loc, 0.45 * s, cor, sub=2); c.scale = (1.5, 0.55, 0.9); liso(c)
    rb = cilindro(_id("rabo"), (0, 0, 0), 0.32 * s, 0.4 * s, cor, seg=3, r2=0.0); filho(c, rb)
    rb.location = (-0.62 * s / 1.5 * 1.5, 0, 0); rb.rotation_euler = (0, math.radians(-90), 0); rb.scale = (1 / 1.5, 1 / 0.55, 1 / 0.9)
    ol = esfera(_id("olhoP"), (0, 0, 0), 0.08 * s, ESCURO, sub=1); filho(c, ol); ol.location = (0.32 * s, -0.42 * s, 0.1 * s); ol.scale = (1 / 1.5, 1 / 0.55, 1 / 0.9)
    return c

def bota(nome, loc, s=1.0):
    b = caixa(nome, loc, (0.4 * s, 0.4 * s, 0.9 * s), (0.42, 0.28, 0.16, 1)); liso(b)
    p = caixa(_id("peBota"), (0, 0, 0), (0.75 * s, 0.4 * s, 0.32 * s), (0.42, 0.28, 0.16, 1)); filho(b, p); p.location = (0.18 * s, 0, -0.32 * s)
    return b

def estrela(nome, loc, s=1.0, cor=OURO):
    e = cilindro(nome, loc, 0.6 * s, 0.18 * s, cor, seg=10); e.rotation_euler = (math.radians(90), 0, 0)
    bm = bmesh.new(); bm.from_mesh(e.data)
    for i, v in enumerate(sorted(bm.verts, key=lambda v: math.atan2(v.co.y, v.co.x))):
        pass
    for v in bm.verts:
        ang = math.atan2(v.co.y, v.co.x); k = round((ang + math.pi) / (2 * math.pi / 10))
        if k % 2: v.co.x *= 0.45; v.co.y *= 0.45
    bm.to_mesh(e.data); bm.free()
    BRILHO.append(e.data.materials[0])
    return e

def palmeira(nome, loc, s=1.0):
    tr = cilindro(nome, loc, 0.14 * s, 3.0 * s, (0.55, 0.38, 0.20, 1), seg=6, r2=0.09 * s)
    for k in range(5):
        fo = caixa(_id("folha"), (0, 0, 0), (1.6 * s, 0.45 * s, 0.06 * s), (0.20, 0.68, 0.30, 1), unico="folhaP"); filho(tr, fo)
        a = 2 * math.pi * k / 5; fo.location = (0.7 * s * math.cos(a), 0.7 * s * math.sin(a), 1.5 * s)
        fo.rotation_euler = (0, math.radians(18), a)
    return tr

def ilha(nome, loc, r=4.0):
    i = cilindro(nome, loc, r, 0.8, AREIA, seg=12, r2=r * 0.8); liso(i)
    g = cilindro(_id("ilhaG"), (0, 0, 0), r * 0.62, 0.4, GRAMA, seg=10, r2=r * 0.5); filho(i, g); g.location = (0, 0, 0.5)
    return i

def barco(nome, loc):
    h = caixa(nome, loc, (4.2, 1.7, 0.7), BRANCO); liso(h)
    fx = caixa(_id("faixaB"), (0, 0, 0), (4.24, 1.74, 0.16), AZUL); filho(h, fx); fx.location = (0, 0, -0.18)
    pr = cilindro(_id("proaB"), (0, 0, 0), 0.85, 0.7, BRANCO, seg=3); filho(h, pr); pr.location = (2.1, 0, 0); pr.rotation_euler = (0, 0, 0)
    cb = caixa(_id("cabB"), (0, 0, 0), (1.1, 1.2, 0.9), (0.95, 0.55, 0.20, 1)); filho(h, cb); cb.location = (-1.2, 0.1, 0.8); liso(cb)
    jn = caixa(_id("janB"), (0, 0, 0), (0.7, 0.04, 0.35), (0.55, 0.85, 1.0, 1)); filho(h, jn); jn.location = (-1.2, -0.52, 0.95)
    cx_ = caixa(_id("caixaIsca"), (0, 0, 0), (0.6, 0.45, 0.35), VERMELHO); filho(h, cx_); cx_.location = (0.9, 0.35, 0.52)
    return h

def sol(nome, loc, s=1.0):
    e = esfera(nome, loc, 1.6 * s, (1.0, 0.85, 0.30, 1), sub=3); liso(e); BRILHO.append(e.data.materials[0]); return e

def vara(nome, mao, dirxy, L=2.8, z_agua=0.0, ang=35):
    """Vara de pesca saindo da mão (mundo) na direção dirxy, subindo 'ang' graus; linha vertical até a boia."""
    d = Vector((dirxy[0] * math.cos(math.radians(ang)), dirxy[1] * math.cos(math.radians(ang)), math.sin(math.radians(ang)))).normalized()
    piv = vazio(nome, tuple(mao))
    v = cilindro(_id("varaC"), (0, 0, 0), 0.045, L, (0.25, 0.20, 0.18, 1), seg=6, r2=0.02); filho(piv, v)
    v.location = tuple(d * (L / 2)); v.rotation_euler = Vector((0, 0, 1)).rotation_difference(d).to_euler()
    mol = cilindro(_id("molinete"), (0, 0, 0), 0.12, 0.12, CINZA, seg=10); filho(piv, mol); mol.location = tuple(d * 0.35 + Vector((0, 0, -0.1)))
    ponta = mao + d * L
    hl = ponta.z - z_agua - 0.1
    ln = cilindro(_id("linha"), (0, 0, 0), 0.012, hl, BRANCO, seg=4); filho(piv, ln); ln.location = tuple(d * L + Vector((0, 0, -hl / 2)))
    bo = esfera(_id("boia"), (0, 0, 0), 0.13, VERMELHO, sub=2); filho(piv, bo); bo.location = tuple(d * L + Vector((0, 0, -hl))); liso(bo)
    bb = esfera(_id("boiaB"), (0, 0, 0), 0.1, BRANCO, sub=2); filho(bo, bb); bb.location = (0, 0, 0.09)
    return piv, ponta, bo

POSE_PESCA = {"ombroD": (-48, 0, 0), "cotoveloD": (-25, 0, 0)}
def pescador(nome, loc, rot_z, escala=0.85, z_agua=0.0, L=2.8):
    """Pixel parado segurando a vara (braço direito fixo; os gestos usam o braço esquerdo e a cabeça)."""
    P = pixel(nome, loc, escala=escala); girarZ(P["raiz"], rot_z)
    for k, v in POSE_PESCA.items(): P[k].rotation_euler = tuple(math.radians(a) for a in v)
    bpy.context.view_layer.update()
    mao = next(o for o in P["cotoveloD"].children if o.name.startswith("mao")).matrix_world.translation.copy()
    th = math.radians(rot_z); dirxy = (math.sin(th), -math.cos(th))
    piv, ponta, bo = vara(_id("vara"), mao, dirxy, L, z_agua)
    return P, piv, bo

def fixa_pose(P):
    """Gestos prontos chamam repouso() no braço direito; aqui toda chave dele volta para a pose de pesca."""
    for k, v in POSE_PESCA.items():
        ob = P[k]; ad = ob.animation_data
        frames = set()
        if ad and ad.action:
            for fc in ad.action.fcurves:
                if fc.data_path == "rotation_euler": frames |= {int(kp.co.x) for kp in fc.keyframe_points}
        ob.rotation_euler = tuple(math.radians(a) for a in v)
        for fr in sorted(frames): ob.keyframe_insert("rotation_euler", frame=fr)

def fisgar(piv, t, eixo=(0, 1, 0)):
    """Puxão na vara (gira o pivô ~14 graus e volta)."""
    piv.rotation_euler = (0, 0, 0); piv.keyframe_insert("rotation_euler", frame=f(t - 0.05))
    piv.rotation_euler = tuple(math.radians(-14) * e for e in eixo); piv.keyframe_insert("rotation_euler", frame=f(t + 0.18))
    piv.rotation_euler = (0, 0, 0); piv.keyframe_insert("rotation_euler", frame=f(t + 0.6))

def pular(P, t, n=2):
    raiz = P["raiz"]; z0 = raiz.location.z
    for k, dz in enumerate([0, 0.35, 0, 0.25, 0][: 2 * n + 1]):
        raiz.location.z = z0 + dz; raiz.keyframe_insert("location", index=2, frame=f(t + k * 0.16))

def salto_peixe(nome, a, b, p0, p2, cor=LARANJA, s=0.7, alto=2.4):
    px_ = peixe(nome, p0, s, cor); visivel(px_, a, b)
    p1 = ((p0[0] + p2[0]) / 2, (p0[1] + p2[1]) / 2, max(p0[2], p2[2]) + alto)
    caminho(px_, a, b, lambda u: bez(p0, p1, p2, u), orientar=False, passo=2)
    key(px_, "rotation_euler", a, (0, math.radians(40), 0)); key(px_, "rotation_euler", b, (0, math.radians(-50), 0))
    return px_

def bolhas(nome, x, y, t0, t1, n=8):
    for k in range(n):
        a = t0 + (t1 - t0) * k / n; e = esfera(_id(nome), (x, y, 0), 0.1 + 0.04 * (k % 3), (0.85, 0.97, 1.0, 1), sub=2, unico="bolha"); liso(e)
        visivel(e, a, a + 1.2); key(e, "location", a, (x + 0.2 * math.sin(k), y, -0.1)); key(e, "location", a + 1.2, (x + 0.3 * math.cos(k), y, 1.6))
    BRILHO.append(mat((0.85, 0.97, 1.0, 1), "bolha"))

def ponteiro_relogio(nome, loc, R=1.3, cor=BRANCO):
    face = cilindro(nome, loc, R, 0.2, cor, seg=32); face.rotation_euler = (math.radians(90), 0, 0)
    aro = anel(_id("aroR"), (0, 0, 0), R, 0.1, VERMELHO, seg=32); filho(face, aro)
    for k in range(12):
        a = 2 * math.pi * k / 12; m_ = caixa(_id("marca"), (0, 0, 0), (0.08, 0.2, 0.06), ESCURO, unico="marcaR"); filho(face, m_)
        m_.location = (0.82 * R * math.sin(a), 0.82 * R * math.cos(a), -0.12)
    piv = vazio(_id("pivR"), (loc[0], loc[1] - 0.16, loc[2]))
    hg = caixa(_id("ponteiroG"), (0, 0, 0), (0.08, 0.06, 0.95 * R), ESCURO); filho(piv, hg); hg.location = (0, 0, 0.42 * R)
    piv2 = vazio(_id("pivR2"), (loc[0], loc[1] - 0.18, loc[2]))
    hp = caixa(_id("ponteiroP"), (0, 0, 0), (0.12, 0.06, 0.6 * R), VERMELHO); filho(piv2, hp); hp.location = (0, 0, 0.27 * R)
    return face, piv, piv2

def girar_y(ob, t0, t1, voltas):
    ob.rotation_euler = (0, 0, 0); ob.keyframe_insert("rotation_euler", frame=f(t0), index=1)
    ob.rotation_euler = (0, 2 * math.pi * voltas, 0); ob.keyframe_insert("rotation_euler", frame=f(t1), index=1)

def celular(nome, loc, s=1.0):
    c = caixa(nome, loc, (1.1 * s, 0.16 * s, 2.0 * s), ESCURO); liso(c)
    tela = caixa(_id("telaCel"), (0, 0, 0), (0.95 * s, 0.04 * s, 1.75 * s), (0.25, 0.85, 0.45, 1), unico="telaCel"); filho(c, tela); tela.location = (0, -0.09 * s, 0)
    for dx, cor in ((-0.25, VERMELHO), (0.25, VERDE)):
        b_ = esfera(_id("botCel"), (0, 0, 0), 0.14 * s, cor, sub=2); filho(c, b_); b_.location = (dx * s, -0.13 * s, -0.6 * s)
    BRILHO.append(mat((0.25, 0.85, 0.45, 1), "telaCel"))
    return c

def onibus(nome, loc, s=1.0):
    b = caixa(nome, loc, (4.4 * s, 1.5 * s, 1.6 * s), AMARELO); liso(b)
    for k in range(5):
        j = caixa(_id("janOn"), (0, 0, 0), (0.6 * s, 0.04 * s, 0.55 * s), (0.55, 0.85, 1.0, 1), unico="janOn"); filho(b, j); j.location = ((-1.7 + k * 0.85) * s, -0.76 * s, 0.3 * s)
    for dx in (-1.4, 1.4):
        r = cilindro(_id("rodaOn"), (0, 0, 0), 0.38 * s, 0.3 * s, ESCURO, seg=14); filho(b, r); r.location = (dx * s, -0.7 * s, -0.8 * s); r.rotation_euler = (math.radians(90), 0, 0)
    return b

def bandeirinha(nome, loc, cor, h=1.6):
    m = cilindro(nome, loc, 0.05, h, CINZA, seg=6)
    p = caixa(_id("pano"), (0, 0, 0), (0.6, 0.05, 0.4), cor); filho(m, p); p.location = (0.3, 0, h / 2 - 0.25)
    return m

def pino(nome, loc, cor, s=1.0):
    p = cilindro(nome, loc, 0.22 * s, 0.6 * s, cor, seg=10, r2=0.0); p.rotation_euler = (math.radians(180), 0, 0)
    b = esfera(_id("pinoB"), (0, 0, 0), 0.26 * s, cor, sub=2); filho(p, b); b.location = (0, 0, -0.38 * s); liso(b)
    return p

def caixa_skinner(nome, loc, s=1.0):
    c = caixa(nome, loc, (1.8 * s, 1.2 * s, 1.4 * s), (0.92, 0.93, 0.96, 1)); liso(c)
    al = caixa(_id("alavanca"), (0, 0, 0), (0.5 * s, 0.3 * s, 0.1 * s), CINZA); filho(c, al); al.location = (-0.35 * s, -0.7 * s, -0.1 * s)
    lp = esfera(_id("lampada"), (0, 0, 0), 0.16 * s, AMARELO, sub=2, unico="lampSk"); filho(c, lp); lp.location = (0.4 * s, -0.62 * s, 0.35 * s)
    bc = caixa(_id("bocal"), (0, 0, 0), (0.4 * s, 0.1 * s, 0.25 * s), ESCURO); filho(c, bc); bc.location = (0.4 * s, -0.62 * s, -0.35 * s)
    return c

cam, alvo, cam_key, plano = camera_cartoon(24)
nuv = lambda x, n=4: [nuvemzinha(_id("nuv"), (x - 9 + k * 6, 30, 9 + (k % 2) * 2.5), 1.6) for k in range(n)]

# =====================================================================
# ZONA A (x = 0) — prisão GENÉRICA (muro, grades, guarita), sem nenhuma pessoa; relógio girando 15h, 20h, 30h (bloco 0)
# =====================================================================
zona_ini()
t0, t1 = S[0]
piso_xadrez("A", 0, (0.55, 0.78, 0.42, 1), (0.36, 0.60, 0.30, 1), larg=30, y0=-12, y1=8)
tsal = T(0, "salvar"); tjog = T(0, "Jogadores"); tpr = T(0, "presa"); t15 = T(0, "quinze"); t20 = T(0, "vinte"); t30 = T(0, "trinta"); tho = T(0, "horas")
muro = caixa("muroA", (1.0, 6.5, 2.2), (16, 1.0, 4.4), (0.62, 0.62, 0.66, 1))
for k in range(9): caixa(_id("ameia"), (-6.6 + k * 1.9, 6.5, 4.65), (0.9, 1.05, 0.5), (0.55, 0.55, 0.60, 1), unico="ameia")
for k in range(10): caixa(_id("tijolo"), (-6.2 + (k % 5) * 3.0 + (k // 5) * 1.5, 5.95, 1.0 + (k // 5) * 1.6), (1.2, 0.08, 0.45), (0.52, 0.52, 0.57, 1), unico="tijolo")
gu = cilindro("guaritaA", (6.6, 6.0, 3.6), 1.0, 7.2, (0.58, 0.58, 0.63, 1), seg=10)
caixa("guaritaTopo", (6.6, 6.0, 7.5), (2.6, 2.6, 0.9), (0.40, 0.42, 0.50, 1))
caixa("guaritaTeto", (6.6, 6.0, 8.15), (3.0, 3.0, 0.3), VERMELHO)
por = caixa("portaoA", (1.0, 5.85, 1.6), (3.2, 0.3, 3.2), (0.22, 0.24, 0.30, 1))
for k in range(7): cilindro(_id("grade"), (-0.3 + k * 0.43, 5.6, 1.6), 0.06, 3.1, CINZA, seg=6, unico="gradeA")
jan = caixa("janelaA", (-4.4, 5.9, 2.9), (1.6, 0.2, 1.2), ESCURO)
for k in range(4): cilindro(_id("gradeJ"), (-5.0 + k * 0.4, 5.75, 2.9), 0.05, 1.2, CINZA, seg=6, unico="gradeA")
cad, alca = cadeado("cadA", (1.0, 5.5, 1.4), 0.7) if "cadeado" in globals() else (None, None)
face, pg, pp = ponteiro_relogio("relA", (2.9, 3.4, 3.4), 1.0)
girar_y(pg, t0, t1, 9); girar_y(pp, t0, t1, 0.75)
for k, (tt, txt) in enumerate(((t15, "15 H"), (t20, "20 H"), (t30, "30 H"))):
    tx = texto3d(_id("horas"), txt, (2.6, 3.0, 5.2), 0.75, [AMARELO, LARANJA, VERMELHO][k], 0.16)
    fim_ = [t20, t30, t1 + 0.3][k]; visivel(tx, tt - 0.1, fim_ - 0.1); pop(tx, tt - 0.1, 1.0)
for k in range(5): arvorezinha(_id("arvA"), (-7.5 + k * 3.6, 9.5, 0.3), 1.6) if "arvorezinha" in globals() else None
nuv(0)
pA = pixel("pixelA", (-1.4, 0.8, 0), escala=0.95); girarZ(pA["raiz"], 15); respirar(pA, 0, t1 + 0.5)
espanto(pA, 0.05, 1.2); apontar(pA, tpr - 0.1, 1.2, "D", 30); apontar(pA, t15 - 0.15, 1.6, "D", 60); espanto(pA, t30 - 0.1, 1.2)
plano(0, (0.6, 2.6), "geral", altura=2.6); plano(t15 - 0.3, (0.8, 2.6), "geral", altura=2.7)
plano(t15, (1.3, 2.6), "geral", altura=2.8); plano(t1 - 0.05, (1.0, 2.6), "geral", altura=2.9)
zona_fim([(0.0, t1 + 0.3)])

# =====================================================================
# ZONA B (x = 40) — o Pixel pescando de barco no mar, ilha com coqueiros (bloco 1) + CTA (bloco 7)
# =====================================================================
zona_ini()
t0, t1 = S[1]; t7 = S[7][0]
mar_ondulado("marB", (40, 12, 0.0), (70, 50), MAR, res=110, altura=0.3, escala_onda=4.0, t_fim=FIM)
ilha("ilhaB", (46.5, 15, 0.1), 4.2)
for k, (dx, dy) in enumerate(((-1.5, 0.5), (0.8, -0.6), (2.0, 1.4))): palmeira(_id("palmB"), (46.5 + dx, 15 + dy, 2.0), 1.1)
ilha("ilhaB2", (31, 22, 0.1), 3.0); palmeira("palmB4", (31, 22, 1.9), 1.0)
sol("solB", (52, 34, 9.5), 1.4); nuv(40)
bt = barco("barcoB", (40.0, 2.0, 0.15))
key(bt, "rotation_euler", 0, (0, 0, 0))
for k in range(int(FIM / 1.6) + 1): key(bt, "rotation_euler", k * 1.6, (math.radians(2.5 if k % 2 else -2.5), 0, 0))
tpes = T(1, "pesca"); tbar = T(1, "barco"); tmer = T(1, "mergulha"); texp = T(1, "explora"); tsit = T(1, "sites"); trel = T(1, "relatos")
pB, varaB, boiaB = pescador("pixelB", (39.2, 1.9, 0.5), 55, 0.85)
respirar(pB, 0, FIM)
fisgar(varaB, tpes - 0.1); salto_peixe("pxB1", tpes, tpes + 1.2, (41.7, 0.2, 0.0), (43.0, 1.2, -0.3), LARANJA)
bolhas("bolB", 37.0, 0.6, tmer - 0.1, tmer + 1.6, 8)
mask = anel("mascB", (37.0, 0.6, 0.15), 0.35, 0.08, AMARELO, seg=20); mask.rotation_euler = (math.radians(90), 0, 0); visivel(mask, tmer - 0.1, tmer + 1.8); pop(mask, tmer - 0.1, 1.0)
pinB = pino("pinoB", (46.5, 15, 3.6), VERMELHO, 1.6); visivel(pinB, texp - 0.15); pop(pinB, texp - 0.15, 1.6)
apontar(pB, texp - 0.1, 1.3, "E", 40); apontar(pB, tsit - 0.1, 1.2, "E", 60)
# CTA (bloco 7): check verde (partiu) e peixe pulando (só mais uma)
tbu = T(7, "buscar"); tpa = T(7, "partiu"); tpe7 = T(7, "pescar"); tum = T(7, "uma")
ckB = check("checkB", (37.3, 0.6, 4.2), 1.1); visivel(ckB, tpa - 0.15); pop(ckB, tpa - 0.15, 1.1)
salto_peixe("pxB2", tpe7 - 0.1, tpe7 + 1.1, (41.7, 0.2, 0.0), (42.6, 1.4, -0.3), OURO)
salto_peixe("pxB3", tum - 0.3, tum + 0.9, (42.4, 0.6, 0.0), (43.6, 1.6, -0.3), ROSA)
fisgar(varaB, tpe7 - 0.15); fisgar(varaB, tum - 0.35)
mais1 = texto3d("mais1B", "+1", (42.3, 0.6, 4.0), 1.1, AMARELO, 0.16); visivel(mais1, tum - 0.1); pop(mais1, tum - 0.1, 1.0)
apontar(pB, tbu - 0.1, 1.2, "E", 50); apontar(pB, tpa - 0.1, 1.0, "E", 70); pular(pB, LEG[-1]["e"] + 1.2); pular(pB, LEG[-1]["e"] + 3.0)
fixa_pose(pB)
plano(t0, (40.0, 1.6), "medio", altura=1.9); plano(tmer - 0.3, (40.0, 1.6), "medio", altura=1.9)
plano(tmer, (40.6, 2.6), "geral", altura=2.4); plano(t1 - 0.05, (41.4, 3.2), "geral", altura=2.6)
cam_key(t7, (40.2, -4.6, 2.3), (40.2, 1.8, 2.0)); cam_key(FIM, (40.6, -4.2, 2.3), (40.6, 1.8, 2.0))
zona_fim([(t0 - 0.3, t1 + 0.3), (t7 - 0.3, FIM + 0.5)])

# =====================================================================
# ZONA C (x = 80) — o ciclo curto: argola grande na parede; JOGA (vara) -> ESPERA (ampulheta) -> PUXA (peixe) -> GANHA (estrela) (bloco 2)
# =====================================================================
zona_ini()
t0, t1 = S[2]
sala("C", 80, (0.98, 0.80, 0.35, 1), (0.62, 0.40, 0.22, 1), (0.25, 0.40, 0.70, 1))
tpre = T(2, "preguiça"); tdes = T(2, "design"); tcic = T(2, "ciclo"); tjo = T(2, "joga"); tesp = T(2, "espera"); tpux = T(2, "puxa"); tgan = T(2, "ganha"); tmin = T(2, "minutos")
CX, CZ, R = 80.6, 3.0, 1.9
aro = anel("cicloC", (CX, 3.6, CZ), R, 0.12, BRANCO, seg=48); aro.rotation_euler = (math.radians(90), 0, 0)
for k in range(4):
    a = math.pi / 2 - k * math.pi / 2 - math.pi / 4
    sp = cilindro(_id("setaC"), (CX + R * math.cos(a), 3.5, CZ + R * math.sin(a)), 0.28, 0.45, CIANO, seg=3, unico="setaC")
    sp.rotation_euler = (0, -a + math.pi, 0); sp.rotation_euler = (math.radians(90), 0, 0); sp.rotation_euler = (0, math.pi - a, 0)
BRILHO.append(mat(CIANO, "setaC"))
# estações (topo, direita, baixo, esquerda)
est = {}
vC = cilindro("varaC0", (CX, 3.3, CZ + R + 0.2), 0.06, 1.4, (0.25, 0.20, 0.18, 1), seg=6); vC.rotation_euler = (0, math.radians(50), 0)
bC = esfera("boiaC0", (CX + 0.6, 3.2, CZ + R - 0.35), 0.18, VERMELHO, sub=2); liso(bC)
amC = ampulheta("ampC", (CX + R + 0.1, 3.2, CZ), 0.8)
pxC = peixe("peixeC", (CX, 3.2, CZ - R - 0.1), 0.9, LARANJA)
stC = estrela("estrelaC", (CX - R - 0.1, 3.2, CZ), 0.95)
for ob, tt in ((vC, tjo), (bC, tjo), (amC, tesp), (pxC, tpux), (stC, tgan)):
    visivel(ob, min(tt, t0 + 0.0) if False else t0); pop(ob, tt - 0.1, 1.0 if ob is not amC else 0.8)
for ob in (vC, bC): pass
# bolinha de luz que roda o ciclo cada vez mais rápido
bola = esfera("bolaC", (CX, 3.1, CZ + R), 0.22, AMARELO, sub=2, unico="bolaC"); liso(bola); BRILHO.append(mat(AMARELO, "bolaC"))
visivel(bola, tcic - 0.1, t1 + 0.3)
caminho(bola, tcic - 0.1, t1 + 0.3, lambda u: (CX + R * math.sin(2 * math.pi * (u * 3 + 1.6 * u * u)), 3.1, CZ + R * math.cos(2 * math.pi * (u * 3 + 1.6 * u * u))), orientar=False, passo=2)
pC = pixel("guiaC", (78.0, 0.4, 0), escala=0.8); girarZ(pC["raiz"], 22); respirar(pC, t0, t1 + 0.5)
pensar(pC, t0 + 0.05, 1.2); comemorar(pC, tdes - 0.15, 1.0); apontar(pC, tjo - 0.1, 1.0, "D", 70); apontar(pC, tesp - 0.1, 0.7, "D", 40)
apontar(pC, tpux - 0.1, 0.7, "D", 10); apontar(pC, tgan - 0.1, 1.0, "D", 40); acenar(pC, tmin - 0.3, 1.2)
plano(t0, (79.6, 2.4), "geral", altura=2.6); plano(tcic - 0.3, (79.8, 2.4), "geral", altura=2.7)
plano(tcic, (80.0, 2.6), "geral", altura=2.8); plano(t1 - 0.05, (80.2, 2.6), "geral", altura=2.8)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA D (x = 120) — recompensa variável: lago redondo, cada puxada traz um prêmio diferente (peixe, bota, baú, peixe dourado); caixa de Skinner (bloco 3)
# =====================================================================
zona_ini()
t0, t1 = S[3]
sala("D", 120, (0.30, 0.62, 0.40, 1), (0.18, 0.42, 0.26, 1), (0.95, 0.55, 0.30, 1))
tpm = T(3, "prêmio"); tmu = T(3, "muda"); tns = T(3, "nunca"); tanz = T(3, "anzol"); trec = T(3, "recompensa"); tsk = T(3, "Skinner"); tinc = T(3, "incerto"); tten = T(3, "tentar")
lago = cilindro("lagoD", (120.6, 2.0, 0.25), 1.8, 0.5, (0.55, 0.42, 0.30, 1), seg=24); liso(lago)
agua = cilindro("aguaD", (120.6, 2.0, 0.42), 1.6, 0.22, MAR, seg=24)
iq = interroga("interD", (120.6, 1.6, 4.4), 1.0, AMARELO); visivel(iq, t0); pop(iq, t0 + 0.05, 1.0)
key(iq, "rotation_euler", tns, (math.radians(90), 0, 0)); key(iq, "rotation_euler", tanz + 0.4, (math.radians(90), 0, math.radians(360)))
premios = [(lambda n, p: peixe(n, p, 0.8, AZUL)), (lambda n, p: bota(n, p, 0.9)), (lambda n, p: caixa_lacrada(n, p, 0.9, OURO)),
           (lambda n, p: peixe(n, p, 1.1, OURO)), (lambda n, p: peixe(n, p, 0.6, ROSA)), (lambda n, p: bota(n, p, 0.8))]
tempos = [t0 + 0.1, tmu - 0.1, tns + 0.1, tanz, tinc - 0.1, tten - 0.1]
for k, (fn, tt) in enumerate(zip(premios, tempos)):
    ob = fn(_id("premio"), (120.6, 2.0, 0.6)); fim_ = tempos[k + 1] if k + 1 < len(tempos) else t1 + 0.3
    visivel(ob, tt, fim_); key(ob, "location", tt, (120.6, 2.0, 0.5)); key(ob, "location", tt + 0.4, (120.6, 1.6, 2.6))
    pop(ob, tt, 1.0, 0.3)
sk = caixa_skinner("skinnerD", (122.9, 1.2, 0.6), 0.75); visivel(sk, t0); pop(sk, tsk - 0.15, 1.0)
lpm = mat(AMARELO, "lampSk"); BRILHO.append(lpm)
piscar(lpm, t0, t1 + 0.3, AMARELO, (0.35, 0.30, 0.10, 1), 0.5)
pD = pixel("guiaD", (118.3, 0.4, 0), escala=0.8); girarZ(pD["raiz"], 20); respirar(pD, t0, t1 + 0.5)
apontar(pD, tmu - 0.1, 1.0, "D", 30); espanto(pD, tns - 0.05, 1.0); pensar(pD, trec - 0.1, 1.3); apontar(pD, tsk - 0.1, 1.2, "D", 20); comemorar(pD, tten - 0.2, 1.1)
plano(t0, (120.4, 2.0), "geral", altura=2.2); plano(tsk - 0.4, (120.6, 2.0), "geral", altura=2.3)
plano(tsk - 0.1, (121.2, 2.0), "geral", altura=2.3); plano(t1 - 0.05, (121.0, 2.0), "geral", altura=2.4)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA E (x = 160) — missão principal = estrada longa com 6 bandeirinhas + relógio; ao lado, ciclo curto com peixe e estrela (bloco 4)
# =====================================================================
zona_ini()
t0, t1 = S[4]
piso_xadrez("E", 160, (0.62, 0.50, 0.85, 1), (0.40, 0.30, 0.62, 1), larg=30, y0=-12, y1=26)
parede_alta("E", 160, 26, (0.30, 0.45, 0.80, 1), larg=30)
caixa("fundoE", (160, 26.2, 3.5), (30, 0.4, 7.0), (0.30, 0.45, 0.80, 1))
tlon = T(4, "Longa"); tet = T(4, "etapas"); thm = T(4, "marcada"); tdu = T(4, "duas"); tvr = T(4, "vitória"); tfa = T(4, "famoso"); tpsc = T(4, "pescaria")
estr = caixa("estradaE", (162.6, 11.0, 0.03), (1.6, 24, 0.06), (0.25, 0.26, 0.30, 1))
for k in range(8): caixa(_id("faixaE"), (162.6, 0.0 + k * 3.0, 0.08), (0.15, 1.2, 0.02), BRANCO, unico="faixaE")
for k in range(6):
    b_ = bandeirinha(_id("bandE"), (163.6, 1.0 + k * 3.6, 0.8), [VERMELHO, LARANJA, AMARELO, VERDE, AZUL, ROXO][k], 1.6)
    tt = tet - 0.1 + 0.12 * k; visivel(b_, t0); pop(b_, tt, 1.0)
rf, rpg, rpp = ponteiro_relogio("relE", (162.6, 22.0, 3.6), 1.6); girar_y(rpg, t0, t1, 4)
aroE = anel("cicloE", (157.6, 1.6, 0.12), 1.2, 0.12, CIANO, seg=32); BRILHO.append(aroE.data.materials[0])
bolaE = esfera("bolaE", (157.6, 1.6, 0.4), 0.18, AMARELO, sub=2, unico="bolaC"); liso(bolaE)
caminho(bolaE, t0, t1 + 0.3, lambda u: (157.6 + 1.2 * math.cos(2 * math.pi * u * 7), 1.6 + 1.2 * math.sin(2 * math.pi * u * 7), 0.35), orientar=False, passo=2)
pxE = peixe("peixeE", (157.6, 1.6, 1.0), 0.7, LARANJA); visivel(pxE, t0)
stE = estrela("estrelaE", (157.6, 1.2, 2.6), 0.8); visivel(stE, tvr - 0.1); pop(stE, tvr - 0.1, 0.8)
salto_peixe("pxE2", tpsc - 0.4, tpsc + 0.8, (156.6, 1.6, 0.3), (158.6, 1.6, 0.3), OURO, 0.6, 1.8)
m1 = texto3d("mais1E", "+1", (157.6, 1.0, 4.0), 0.9, AMARELO, 0.16); visivel(m1, tpsc - 0.1); pop(m1, tpsc - 0.1, 1.0)
pE = pixel("guiaE", (160.2, 0.0, 0), escala=0.9); girarZ(pE["raiz"], 0); respirar(pE, t0, t1 + 0.5)
apontar(pE, tlon - 0.1, 1.6, "D", 30); pensar(pE, tdu - 0.2, 1.2); apontar(pE, tvr - 0.15, 1.2, "E", 40); comemorar(pE, tfa - 0.1, 1.4)
plano(t0, (160.6, 2.0), "geral", altura=2.6); plano(tdu - 0.3, (160.4, 2.0), "geral", altura=2.6)
plano(tdu, (159.4, 1.6), "medio", altura=2.2); plano(t1 - 0.05, (159.2, 1.6), "medio", altura=2.2)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA F (x = 200) — píer: o Pixel pescando; celular gigante tocando ("a Lucia liga"), ônibus passa na estrada da praia; mar (bloco 5)
# =====================================================================
zona_ini()
t0, t1 = S[5]
mar_ondulado("marF", (200, 4, 0.0), (60, 24), MAR, res=100, altura=0.3, escala_onda=4.0, t_fim=FIM)
caixa("praiaF", (200, 20, 0.2), (60, 12, 0.6), AREIA)
caixa("ruaF", (200, 18.5, 0.55), (60, 3.0, 0.1), (0.25, 0.26, 0.30, 1))
for k in range(8): caixa(_id("faixaF"), (184 + k * 4.5, 18.5, 0.62), (1.6, 0.15, 0.02), BRANCO, unico="faixaE")
for k in range(6): palmeira(_id("palmF"), (186 + k * 5.6, 22.5, 2.0), 1.2)
sol("solF", (212, 40, 10), 1.4); nuv(200)
caixa("pierF", (199.0, 7.0, 0.45), (2.6, 14, 0.25), MADEIRA)
for k in range(7): caixa(_id("tabuaF"), (199.0, 0.5 + k * 2.0, 0.6), (2.7, 0.12, 0.06), (0.42, 0.26, 0.14, 1), unico="tabuaF")
for k in range(5):
    for dx in (-1.2, 1.2): cilindro(_id("estacaF"), (199.0 + dx, 0.6 + k * 3.0, 0.1), 0.13, 1.4, (0.42, 0.26, 0.14, 1), seg=6, unico="estacaF")
tlib = T(5, "liberdade"); thi = T(5, "história"); tseg = T(5, "Segundo"); tli = T(5, "liga"); tame = T(5, "ameaça"); ton = T(5, "ônibus"); tmar = T(5, "mar"); tcont = T(5, "continua")
pF, varaF, boiaF = pescador("pixelF", (199.0, 1.4, 0.58), 60, 0.85)
respirar(pF, t0, t1 + 0.5)
cel = celular("celF", (197.6, 0.9, 1.75), 0.6); visivel(cel, t0); pop(cel, tli - 0.25, 0.6)
for k in range(int((t1 - tli) / 0.12)):
    key(cel, "rotation_euler", tli + 0.12 * k, (0, math.radians(8 if k % 2 else -8), 0))
for k in range(4):
    an_ = anel(_id("toqueF"), (197.6, 0.85, 1.75), 0.55, 0.04, VERDE, seg=24, unico="toqueF"); an_.rotation_euler = (math.radians(90), 0, 0)
    a = tli + 0.4 * k; visivel(an_, a, a + 0.8); an_.scale = (0.6,) * 3; an_.keyframe_insert("scale", frame=f(a)); an_.scale = (1.6,) * 3; an_.keyframe_insert("scale", frame=f(a + 0.8))
BRILHO.append(mat(VERDE, "toqueF"))
on = onibus("onibusF", (186, 18.5, 1.45), 1.0); visivel(on, t0)
key(on, "location", t0, (184, 18.5, 1.45)); key(on, "location", ton - 0.6, (184, 18.5, 1.45)); key(on, "location", t1 + 0.3, (215, 18.5, 1.45))
apontar(pF, tli - 0.1, 1.3, "E", 30); apontar(pF, ton - 0.1, 1.3, "E", 60)
fisgar(varaF, tcont - 0.2)
fixa_pose(pF)
plano(t0, (199.0, 2.4), "geral", altura=2.4); plano(tmar - 0.4, (199.2, 2.6), "geral", altura=2.5)
plano(tmar - 0.1, (200.6, 3.4), "geral", altura=2.6); plano(t1 - 0.05, (201.2, 3.6), "geral", altura=2.8)
zona_fim([(t0 - 0.3, t1 + 0.3)])

# =====================================================================
# ZONA G (x = 240) — mapa em miniatura: ilha na mesa, cheia de pinos e atividades pequenas; barra da história quase parada (bloco 6)
# =====================================================================
zona_ini()
t0, t1 = S[6]
sala("G", 240, (0.95, 0.62, 0.42, 1), (0.70, 0.38, 0.25, 1), (0.30, 0.25, 0.55, 1))
test = T(6, "estúdios"); tma = T(6, "mapa"); tat = T(6, "atividades"); tseg6 = T(6, "seguram"); tav = T(6, "avançar")
caixa("mesaG", (240.4, 2.2, 0.55), (5.2, 3.6, 1.1), (0.30, 0.22, 0.18, 1))
caixa("marMesaG", (240.4, 2.2, 1.14), (4.9, 3.2, 0.08), MAR)
il = cilindro("ilhaG", (240.4, 2.2, 1.25), 2.1, 0.2, AREIA, seg=9); il.scale = (1.25, 0.7, 1.0)
ig = cilindro("ilhaGG", (240.4, 2.25, 1.38), 1.7, 0.12, GRAMA, seg=9); ig.scale = (1.2, 0.62, 1.0)
cores = [VERMELHO, AZUL, OURO, VERDE, ROSA, LARANJA, CIANO, ROXO, VERMELHO, AZUL, OURO, VERDE]
for k in range(12):
    x_ = 238.6 + (k % 6) * 0.72; y_ = 1.8 + (k // 6) * 0.8 + 0.2 * math.sin(k)
    p_ = pino(_id("pinoG"), (x_, y_, 1.95), cores[k], 0.8); tt = tma + 0.12 * k; visivel(p_, t0 if k < 3 else tt); pop(p_, t0 + 0.05 if k < 3 else tt, 0.8, 0.25)
for k, (dx, fn) in enumerate(((-2.0, lambda n, p: peixe(n, p, 0.5, LARANJA)), (-1.3, lambda n, p: estrela(n, p, 0.45)), (2.0, lambda n, p: bota(n, p, 0.5)))):
    ob = fn(_id("iconeG"), (240.4 + dx, 1.4, 1.6)); visivel(ob, tat - 0.1 + 0.15 * k); pop(ob, tat - 0.1 + 0.15 * k, 1.0)
mb, br, mm = barra("progG", 242.9, 3.9, 2.6, 2.6, 0.5, VERDE);
encher(br, t0, t0 + 0.05, 0.08, 0.08); encher(br, tav - 0.2, tav + 0.6, 0.08, 0.1)
hq = texto3d("historiaG", "HISTÓRIA", (242.9, 3.7, 5.6), 0.3, BRANCO, 0.08)
pG = pixel("guiaG", (238.4, 0.9, 0), escala=0.8); girarZ(pG["raiz"], 20); respirar(pG, t0, t1 + 0.5)
apontar(pG, test - 0.1, 1.2, "D", 40); apontar(pG, tat - 0.1, 1.2, "D", 20); comemorar(pG, tseg6 - 0.1, 1.2); pensar(pG, tav - 0.2, 1.2)
plano(t0, (240.2, 2.0), "geral", altura=2.5); plano(t1 - 0.05, (240.8, 2.0), "geral", altura=2.6)
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
