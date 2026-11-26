"""Série 2 — 'Por que o GTA 6 pirata de PC foi derrubado?' (estilo C cartoon, mascote Pixel, visual nível 2).
Mecanismo: console x PC (cadeado) -> multidão no chat + caixa lacrada indo de um console a um PC por uma máquina tradutora
-> processador igual, mas a peça quadrada não entra no buraco redondo (sistema e DirectX próprio) -> shaders: lâmpada e
sombra; console com 1 placa x PC com dezenas de placas diferentes; equipe pequena trabalhando com calendário
-> a queda: telão de bolhas de chat e repositório se apagam, cadeado, ampulheta (2 anos) -> envelope de direitos
autorais vai do prédio da empresa ao servidor da plataforma, que tira tudo do ar -> calendário de 2027 com PC embrulhado
e interrogação -> convite (zerei / na fila).
Visual 100 % original: consoles e PC genéricos sem marca, nenhuma arte/personagem/logo/mapa de jogo, nenhum arquivo vazado,
nenhuma tela/servidor de chat real. Anti-borda: piso xadrez texturizado e parede alta com painéis (sem faixa lisa).
Base: cena_var_impedimento.py. Uso: blender -b --factory-startup -P cena_gta6_pirata_pc.py -- <pasta> [preview t1,t2 | range a,b]"""
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
random.seed(61)

AMARELO = (1.0, 0.82, 0.12, 1); VERDE = (0.20, 0.85, 0.40, 1); VERMELHO = (0.95, 0.22, 0.20, 1)
AZUL = (0.20, 0.55, 1.0, 1); BRANCO = (0.97, 0.97, 0.98, 1); CIANO = (0.25, 0.95, 1.0, 1)
ESCURO = (0.10, 0.11, 0.14, 1); CINZA = (0.40, 0.42, 0.48, 1); OURO = (1.0, 0.72, 0.10, 1)
ROXO = (0.55, 0.35, 0.95, 1); ROSA = (1.0, 0.45, 0.70, 1); LARANJA = (1.0, 0.55, 0.15, 1); CHIPV = (0.10, 0.55, 0.30, 1)
BRILHO = []
def brilha(ob): BRILHO.append(ob.data.materials[0]); return ob
def girarZ(ob, graus): ob.rotation_euler = (0, 0, math.radians(graus))

# ---------------------------------------------------------------- cenário (anti-borda)
def piso_xadrez(nome, x, c1, c2, larg=24, y0=-10, y1=4.4, lado=2.0):
    """Piso em ladrilhos de duas cores (textura): nada de chão liso de ponta a ponta na base do quadro."""
    nx = int(larg / lado); ny = int((y1 - y0) / lado)
    for i in range(nx):
        for j in range(ny):
            par = (i + j) % 2 == 0
            caixa(_id(nome + "lad"), (x - larg / 2 + lado / 2 + i * lado, y0 + lado / 2 + j * lado, -0.1), (lado, lado, 0.2),
                  c1 if par else c2, unico=f"{nome}lad{int(par)}")

def parede_alta(nome, x, prof, cor, larg=24):
    """Anti-'borda': prolonga a parede do fundo até o alto do quadro com friso e painéis de luz (sem céu liso)."""
    caixa(nome + "ParedeAlta", (x, prof + 0.05, 10.5), (larg, 0.4, 7.0), tuple(c * 0.85 for c in cor[:3]) + (1,))
    caixa(nome + "Friso", (x, prof - 0.2, 7.05), (larg, 0.15, 0.25), (0.95, 0.75, 0.25, 1))
    for k in range(8):
        caixa(_id(nome + "painel"), (x - 10.5 + k * 3, prof - 0.2, 9.6 + (k % 2) * 1.6), (1.8, 0.08, 0.9), (0.70, 0.88, 1.0, 1), unico="painelLuz")
    BRILHO.append(mat((0.70, 0.88, 1.0, 1), "painelLuz"))

def sala(nome, x, piso1, piso2, parede, prof=4.6):
    sala_fechada(nome, x, piso1, parede, prof=prof, larg=24)
    piso_xadrez(nome, x, piso1, piso2, y1=prof - 0.2)
    parede_alta(nome, x, prof, parede)
    # quadros/prateleiras na parede para quebrar a superfície lisa
    for k in range(4):
        caixa(_id(nome + "prat"), (x - 8.5 + k * 5.6, prof - 0.25, 5.4), (2.2, 0.35, 0.08), (0.98, 0.84, 0.40, 1), unico="prat")
        caixa(_id(nome + "enf"), (x - 9.0 + k * 5.6, prof - 0.3, 5.65), (0.3, 0.25, 0.4), [ROSA, CIANO, VERDE, LARANJA][k], unico=f"enf{k}")

# ---------------------------------------------------------------- modelos genéricos (sem marca)
def console(nome, loc, s=1.0, cor=BRANCO):
    """Console genérico: torre retangular com faixa de luz azul e um controle ao lado (nenhum desenho real)."""
    c = caixa(nome, loc, (0.55 * s, 1.1 * s, 1.5 * s), cor); liso(c)
    fx = caixa(_id("faixaCons"), (0, 0, 0), (0.04 * s, 0.9 * s, 0.08 * s), (0.3, 0.7, 1.0, 1), unico="faixaCons"); filho(c, fx); fx.location = (0.29 * s, 0, 0.5 * s)
    bt = esfera(_id("botCons"), (0, 0, 0), 0.06 * s, VERDE, sub=1); filho(c, bt); bt.location = (0.29 * s, -0.4 * s, -0.55 * s)
    BRILHO.append(mat((0.3, 0.7, 1.0, 1), "faixaCons"))
    return c

def controle(nome, loc, s=1.0, cor=(0.15, 0.15, 0.20, 1)):
    c = caixa(nome, loc, (0.7 * s, 0.35 * s, 0.14 * s), cor); liso(c)
    for dx in (-0.32, 0.32):
        g = esfera(_id("pega"), (0, 0, 0), 0.18 * s, cor, sub=2); filho(c, g); g.location = (dx * s, 0.05 * s, -0.05 * s)
    for k, cc in enumerate((VERMELHO, VERDE, AZUL, AMARELO)):
        b = esfera(_id("botao"), (0, 0, 0), 0.04 * s, cc, sub=1); filho(c, b)
        b.location = ((0.18 + 0.06 * (k % 2)) * s, (-0.06 + 0.06 * (k // 2)) * s, 0.08 * s)
    return c

def pc_torre(nome, loc, s=1.0):
    """Gabinete de PC genérico com LED roxo e ventoinhas."""
    p = caixa(nome, loc, (0.7 * s, 1.2 * s, 1.6 * s), (0.12, 0.12, 0.16, 1))
    led = caixa(_id("ledPC"), (0, 0, 0), (0.02 * s, 1.0 * s, 1.4 * s), ROXO, unico="ledPC"); filho(p, led); led.location = (-0.36 * s, 0, 0)
    for k in range(3):
        v = anel(_id("vent"), (0, 0, 0), 0.22 * s, 0.03 * s, CIANO, seg=16, unico="vent"); filho(p, v)
        v.location = (-0.37 * s, 0, (0.5 - k * 0.5) * s); v.rotation_euler = (0, math.radians(90), 0)
    BRILHO.extend([mat(ROXO, "ledPC"), mat(CIANO, "vent")])
    return p

def monitor(nome, loc, cor_tela=(0.30, 0.85, 1.0, 1), w=1.6, h=0.95, unico=None):
    m = caixa(nome, loc, (w, 0.1, h), PRETO)
    t = caixa(_id("telaM"), (0, 0, 0), (w * 0.92, 0.02, h * 0.86), cor_tela, unico=unico or _id("tm")); filho(m, t); t.location = (0, -0.06, 0)
    pe = caixa(_id("peM"), (0, 0, 0), (0.12, 0.12, 0.5), PRETO); filho(m, pe); pe.location = (0, 0.05, -h / 2 - 0.25)
    return m, t

def cadeado(nome, loc, s=1.0, cor=OURO):
    c = caixa(nome, loc, (0.8 * s, 0.35 * s, 0.65 * s), cor); liso(c)
    a = anel(_id("alca"), (0, 0, 0), 0.28 * s, 0.07 * s, CINZA, seg=20); filho(c, a); a.location = (0, 0, 0.36 * s); a.rotation_euler = (math.radians(90), 0, 0)
    fu = esfera(_id("fur"), (0, 0, 0), 0.08 * s, ESCURO, sub=1); filho(c, fu); fu.location = (0, -0.18 * s, 0.03 * s)
    return c

def xis(nome, loc, s=0.6, cor=VERMELHO):
    a = caixa(nome, loc, (s, 0.12, s * 0.22), cor); a.rotation_euler = (0, math.radians(45), 0)
    b = caixa(_id("xb"), (0, 0, 0), (s, 0.12, s * 0.22), cor); filho(a, b); b.rotation_euler = (0, math.radians(-90), 0)
    return a

def interroga(nome, loc, s=1.0, cor=AMARELO):
    """Ponto de interrogação 3D (texto '?' extrudado, convertido em malha para ganhar o contorno do nível 2)."""
    cu = bpy.data.curves.new(_id("qTxt"), "FONT"); cu.body = "?"; cu.extrude = 0.12; cu.size = 1.6 * s
    cu.align_x = "CENTER"; cu.align_y = "CENTER"
    tmp = bpy.data.objects.new(_id("qTmp"), cu); bpy.context.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp); ob = bpy.data.objects.new(nome, me); bpy.context.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler = (math.radians(90), 0, 0)
    ob.data.materials.append(mat(cor, "interroga")); BRILHO.append(mat(cor, "interroga"))
    return ob

def pessoinha(nome, loc, cor, s=1.0):
    """Ícone de usuário genérico: corpo arredondado + cabeça."""
    r = vazio(nome, loc); r.scale = (s, s, s)
    c = capsula(_id("corpoP"), (0, 0, 0), 0.28, 0.3, cor); filho(r, c); c.location = (0, 0, 0.4)
    cb = esfera(_id("cabP"), (0, 0, 0), 0.22, PELE, sub=2); filho(r, cb); cb.location = (0, 0, 0.95); liso(cb)
    return r

def bolha(nome, loc, cor, s=1.0):
    """Balão de chat genérico com três pontinhos."""
    b = caixa(nome, loc, (1.0 * s, 0.15 * s, 0.6 * s), cor); liso(b)
    rb = caixa(_id("rabo"), (0, 0, 0), (0.2 * s, 0.15 * s, 0.2 * s), cor); filho(b, rb); rb.location = (-0.35 * s, 0, -0.33 * s); rb.rotation_euler = (0, math.radians(45), 0)
    for k in range(3):
        p = esfera(_id("pt"), (0, 0, 0), 0.07 * s, BRANCO, sub=1); filho(b, p); p.location = ((-0.22 + k * 0.22) * s, -0.09 * s, 0)
    return b

def caixa_lacrada(nome, loc, s=1.0):
    """Caixa de papelão lacrada com fita (representa 'o arquivo' sem mostrar nada de dentro)."""
    c = caixa(nome, loc, (0.9 * s, 0.9 * s, 0.7 * s), (0.78, 0.58, 0.34, 1)); liso(c)
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

def placa_video(nome, loc, cor, s=1.0):
    """Placa de vídeo genérica: corpo colorido + 2 ventoinhas."""
    p = caixa(nome, loc, (1.3 * s, 0.25 * s, 0.5 * s), cor)
    for dx in (-0.32, 0.32):
        v = cilindro(_id("ventP"), (0, 0, 0), 0.19 * s, 0.05 * s, ESCURO, seg=12); filho(p, v); v.location = (dx * s, -0.14 * s, 0); v.rotation_euler = (math.radians(90), 0, 0)
    pc = caixa(_id("pcb"), (0, 0, 0), (1.3 * s, 0.05 * s, 0.1 * s), CHIPV); filho(p, pc); pc.location = (0, 0, -0.29 * s)
    return p

def ampulheta(nome, loc, s=1.0):
    v = vazio(nome, loc)
    for dz in (-0.55, 0.55):
        t = cilindro(_id("tampaA"), (0, 0, 0), 0.45 * s, 0.1 * s, (0.45, 0.28, 0.14, 1), seg=14); filho(v, t); t.location = (0, 0, dz * s)
    for dz, r1, r2 in ((-0.25, 0.38, 0.06), (0.25, 0.06, 0.38)):
        c = cilindro(_id("vidro"), (0, 0, 0), r1 * s, 0.5 * s, (0.75, 0.90, 1.0, 1), seg=14, r2=r2 * s); filho(v, c); c.location = (0, 0, dz * s)
    ar = cilindro(_id("areia"), (0, 0, 0), 0.3 * s, 0.2 * s, OURO, seg=14, r2=0.05 * s); filho(v, ar); ar.location = (0, 0, -0.38 * s)
    return v

def envelope(nome, loc, s=1.0):
    e = caixa(nome, loc, (0.9 * s, 0.06 * s, 0.6 * s), BRANCO)
    for sg in (-1, 1):
        a = caixa(_id("aba"), (0, 0, 0), (0.55 * s, 0.02 * s, 0.05 * s), (0.75, 0.78, 0.85, 1)); filho(e, a)
        a.location = (sg * 0.2 * s, -0.04 * s, 0.12 * s); a.rotation_euler = (0, math.radians(sg * 32), 0)
    sl = cilindro(_id("selo"), (0, 0, 0), 0.12 * s, 0.03 * s, VERMELHO, seg=12); filho(e, sl); sl.location = (0, -0.05 * s, -0.05 * s); sl.rotation_euler = (math.radians(90), 0, 0)
    return e

def predio_empresa(nome, loc, s=1.0):
    x, y, z = loc
    p = caixa(nome, (x, y, z + 2.0 * s), (2.2 * s, 1.6 * s, 4.0 * s), (0.30, 0.34, 0.48, 1))
    for i in range(3):
        for j in range(5):
            jn = caixa(_id("janela"), (0, 0, 0), (0.45 * s, 0.05 * s, 0.4 * s), (0.70, 0.88, 1.0, 1), unico="janelaE"); filho(p, jn)
            jn.location = ((-0.65 + i * 0.65) * s, -0.82 * s, (-1.4 + j * 0.7) * s)
    BRILHO.append(mat((0.70, 0.88, 1.0, 1), "janelaE"))
    return p

def servidor(nome, loc, s=1.0, cor_led=VERDE, unico="ledSrv"):
    r = caixa(nome, loc, (1.2 * s, 1.0 * s, 2.6 * s), (0.14, 0.15, 0.20, 1))
    for j in range(6):
        l = caixa(_id("ledS"), (0, 0, 0), (0.9 * s, 0.04 * s, 0.1 * s), cor_led, unico=unico); filho(r, l); l.location = (0, -0.52 * s, (-1.0 + j * 0.4) * s)
    return r

def calendario(nome, loc, s=1.0):
    c = caixa(nome, loc, (1.6 * s, 0.12 * s, 1.8 * s), BRANCO)
    tp = caixa(_id("topoCal"), (0, 0, 0), (1.6 * s, 0.14 * s, 0.4 * s), VERMELHO); filho(c, tp); tp.location = (0, -0.01 * s, 0.75 * s)
    for i in range(4):
        for j in range(3):
            q = caixa(_id("dia"), (0, 0, 0), (0.25 * s, 0.03 * s, 0.22 * s), (0.80, 0.82, 0.88, 1)); filho(c, q)
            q.location = ((-0.55 + i * 0.37) * s, -0.07 * s, (0.2 - j * 0.38) * s)
    for dx in (-0.45, 0.45):
        an = anel(_id("argola"), (0, 0, 0), 0.1 * s, 0.03 * s, CINZA, seg=12); filho(c, an); an.location = (dx * s, 0, 0.98 * s)
    return c

def peca_quadrada(nome, loc, s=1.0):
    return caixa(nome, loc, (0.6 * s, 0.6 * s, 0.6 * s), LARANJA)

def presente(nome, loc, s=1.0):
    b = caixa(nome, loc, (1.4 * s, 1.4 * s, 1.4 * s), ROXO); liso(b)
    for rot in (0, 90):
        fi = caixa(_id("laco"), (0, 0, 0), (1.45 * s, 0.25 * s, 1.45 * s), AMARELO); filho(b, fi); fi.rotation_euler = (0, 0, math.radians(rot))
    return b

cam, alvo, cam_key, plano = camera_cartoon(24)

# =====================================================================
# ZONA A (x = 0) — quarto gamer: console (com controle) x PC com cadeado; X vermelho no 'derrubado' (bloco 0 e CTA)
# =====================================================================
t0, t1 = S[0]
sala("A", 0, (0.36, 0.40, 0.62, 1), (0.30, 0.34, 0.54, 1), (0.55, 0.38, 0.85, 1))
tsa = T(0, "saiu"); tps = T(0, "PS5"); txb = T(0, "Xbox"); tga = T(0, "garoto"); tqz = T(0, "quinze"); tro = T(0, "rodar")
tpc = T(0, "PC"); tpq = T(0, "Por"); tde = T(0, "derrubado")
caixa("mesaA", (0.6, 1.6, 1.0), (5.0, 1.3, 0.12), (0.30, 0.22, 0.18, 1))
for dx in (-2.2, 2.2): caixa(_id("peMesaA"), (0.6 + dx, 1.6, 0.48), (0.12, 1.0, 0.96), (0.18, 0.18, 0.22, 1))
c1 = console("consA1", (-1.0, 1.7, 1.82), 0.8); visivel(c1, 0.0); pop(c1, tps - 0.1, 1.0)
c2 = console("consA2", (0.0, 1.7, 1.82), 0.8, cor=(0.15, 0.16, 0.2, 1)); visivel(c2, 0.0); pop(c2, txb - 0.1, 1.0)
ctl = controle("controleA", (-0.5, 1.1, 1.15), 0.9)
pcA = pc_torre("pcA", (2.0, 1.8, 1.9), 0.9)
monA, telaA = monitor("monA", (2.0, 3.6, 2.9), unico="telaA")
mtA = mat((0.30, 0.85, 1.0, 1), "telaA"); BRILHO.append(mtA)
cdA = cadeado("cadeadoA", (2.0, 1.0, 2.2), 0.8); visivel(cdA, tpc - 0.15, t1 + 0.1); pop(cdA, tpc - 0.15, 1.0)
iqA = interroga("interA", (2.0, 1.4, 3.6), 0.9); visivel(iqA, tpq - 0.1, t1 + 0.1); pop(iqA, tpq - 0.1, 1.0)
xA = xis("xA", (2.0, 0.6, 2.3), 1.5); visivel(xA, tde + 0.05, t1 + 0.1); pop(xA, tde + 0.05, 1.0)
cor_key(mtA, tde - 0.05, (0.30, 0.85, 1.0, 1)); cor_key(mtA, tde + 0.2, (0.95, 0.25, 0.22, 1))
px = pixel("pixel", (-2.4, 0.2, 0), escala=0.9); girarZ(px["raiz"], 14); respirar(px, 0, FIM)
espanto(px, tsa - 0.1, 1.2); pensar(px, tga - 0.1, 1.4); apontar(px, tro - 0.1, 1.4, "D", 50); espanto(px, tde - 0.1, 1.2)
plano(0, (0.2, 1.4), "geral", altura=1.9); plano(tga - 0.4, (0.0, 1.4), "geral", altura=1.9)
plano(tga - 0.05, (-1.2, 0.8), "medio", altura=1.9); plano(tro - 0.4, (-1.2, 0.8), "medio", altura=1.9)
plano(tro - 0.05, (1.4, 1.2), "medio", altura=2.2); plano(t1 - 0.05, (1.5, 1.2), "medio", altura=2.4)

# =====================================================================
# ZONA B (x = 40) — telão cheio de bolhas de chat e pessoinhas (180 mil); caixa lacrada vai do console a uma máquina
# tradutora e sai do outro lado no PC (bloco 1)
# =====================================================================
t0, t1 = S[1]
sala("B", 40, (0.95, 0.80, 0.45, 1), (0.88, 0.70, 0.38, 1), (0.25, 0.30, 0.55, 1))
tle = T(1, "Leonida"); tju = T(1, "juntou"); tce = T(1, "cento"); tdi = T(1, "Discord"); tid = T(1, "ideia")
tar = T(1, "arquivo"); tva = T(1, "vazou"); ttr = T(1, "traduzir"); twi = T(1, "Windows")
telB = caixa("telaoB", (40.0, 4.2, 4.6), (9.0, 0.2, 3.6), (0.20, 0.22, 0.36, 1))
cores = [ROSA, CIANO, VERDE, AMARELO, LARANJA, ROXO]
k = 0
for i in range(7):
    for j in range(3):
        b = bolha(_id("bolB"), (36.6 + i * 1.15 + (j % 2) * 0.3, 4.0, 3.5 + j * 1.05), cores[(i + j) % 6], 0.85)
        tt = tju - 0.1 + 0.05 * k; visivel(b, tt, tid); pop(b, tt, 0.85); k += 1
for i in range(14):
    pp = pessoinha(_id("pesB"), (34.6 + i * 0.85, 2.6 + (i % 2) * 0.5, 0), cores[i % 6], 0.8)
    tt = tce - 0.2 + 0.04 * i; visivel(pp, tt, tid); pop(pp, tt, 0.8)
# máquina tradutora: console -> funil/caixa com engrenagens -> PC
cB = console("consB", (36.4, 1.6, 0.75), 1.0); visivel(cB, tid - 0.2); pop(cB, tid - 0.2, 1.0)
maq = caixa("tradutora", (40.0, 1.6, 1.1), (2.0, 1.4, 2.2), (0.35, 0.75, 0.55, 1)); liso(maq)
eng = anel("engrenagem", (0, 0, 0), 0.45, 0.12, AMARELO, seg=12); filho(maq, eng); eng.location = (0, -0.75, 0.3); eng.rotation_euler = (math.radians(90), 0, 0)
setaE = seta3d("setaB1", 1.4, AMARELO); setaE.location = (38.3, 1.4, 1.9); setaE.rotation_euler = (0, math.radians(90), 0); setaE.scale = (0.5, 0.5, 0.5)
setaD = seta3d("setaB2", 1.4, AMARELO); setaD.location = (41.6, 1.4, 1.9); setaD.rotation_euler = (0, math.radians(90), 0); setaD.scale = (0.5, 0.5, 0.5)
pcB = pc_torre("pcB", (43.8, 1.6, 0.8), 1.0)
for k_, ob in enumerate((maq, setaE, setaD, pcB)):
    visivel(ob, tid + 0.1 * k_); pop(ob, tid + 0.1 * k_, 0.5 if ob in (setaE, setaD) else 1.0)
key(eng, "rotation_euler", ttr, (math.radians(90), 0, 0)); key(eng, "rotation_euler", t1 + 0.3, (math.radians(90), math.radians(720), 0))
cx = caixa_lacrada("caixaB", (36.4, 1.4, 2.0), 0.6); visivel(cx, tar - 0.1, t1 + 0.2); pop(cx, tar - 0.1, 1.0)
key(cx, "location", ttr - 0.1, (36.4, 1.4, 2.0)); key(cx, "location", ttr + 0.6, (40.0, 1.4, 2.6))
key(cx, "location", twi - 0.3, (42.0, 1.4, 2.6)); key(cx, "location", twi + 0.4, (43.8, 1.4, 2.0))
gB = pixel("guiaB", (38.5, -0.9, 0), escala=0.85); girarZ(gB["raiz"], 18); respirar(gB, t0, t1 + 0.5)
acenar(gB, tle - 0.2, 1.2); comemorar(gB, tce - 0.1, 1.2); apontar(gB, tar - 0.1, 1.4, "D", 60); apontar(gB, ttr - 0.1, 1.6, "D", 30)
cam_key(t0, (39.6, -7.6, 3.6), (40.0, 3.0, 4.0)); cam_key(tid - 0.4, (40.2, -7.8, 3.6), (40.0, 3.0, 4.0))
cam_key(tid - 0.05, (39.8, -6.6, 2.4), (40.0, 1.6, 1.7)); cam_key(t1 - 0.05, (40.3, -6.8, 2.5), (40.2, 1.6, 1.7))

# =====================================================================
# ZONA C (x = 80) — dois processadores iguais (=) ; mas a peça quadrada não entra no encaixe redondo (sistema/DirectX) (bloco 2)
# =====================================================================
t0, t1 = S[2]
sala("C", 80, (0.62, 0.72, 0.98, 1), (0.52, 0.62, 0.90, 1), (0.30, 0.20, 0.45, 1))
tco = T(2, "copiar"); tpr = T(2, "processador"); tpa = T(2, "parece"); tpb = T(2, "problema"); tre = T(2, "resto")
tcv = T(2, "conversa"); tsi = T(2, "sistema"); tdx = T(2, "DirectX"); tpp = T(2, "próprio")
iqC = interroga("interC", (80.0, 2.0, 4.0), 1.0); visivel(iqC, t0, tpr - 0.1); pop(iqC, t0 + 0.1, 1.0)
chA = chip_cpu("chipC1", (78.2, 2.0, 2.8), 1.1); chB = chip_cpu("chipC2", (81.8, 2.0, 2.8), 1.1)
for ob, d in ((chA, 0), (chB, 0.15)):
    visivel(ob, tpr - 0.1 + d, tpb - 0.1); pop(ob, tpr - 0.1 + d, 1.0)
cons_c = console("consC", (78.2, 2.2, 0.75), 0.8); pcC = pc_torre("pcC", (81.8, 2.2, 0.8), 0.9)
for ob in (cons_c, pcC): visivel(ob, tpr - 0.1, tpb - 0.1); pop(ob, tpr, 0.8 if ob is cons_c else 0.9)
ig1 = caixa("igual1", (80.0, 1.9, 3.0), (0.8, 0.1, 0.14), VERDE); ig2 = caixa("igual2", (80.0, 1.9, 2.6), (0.8, 0.1, 0.14), VERDE)
for ob in (ig1, ig2): brilha(ob); visivel(ob, tpa - 0.1, tpb - 0.1); pop(ob, tpa - 0.1, 1.0)
# o resto: bloco do PC com furo redondo + peça quadrada do console tentando entrar
base = caixa("baseC", (81.0, 2.0, 1.2), (2.6, 1.4, 1.2), (0.30, 0.55, 0.95, 1)); liso(base)
furo = cilindro("furoC", (81.0, 2.0, 1.83), 0.42, 0.06, ESCURO, seg=24)
for ob in (base, furo): visivel(ob, tre - 0.2); pop(ob, tre - 0.2, 1.0)
pq = peca_quadrada("pecaC", (79.0, 2.0, 3.6), 1.4); visivel(pq, tre - 0.1); pop(pq, tre - 0.1, 1.0)
key(pq, "location", tcv - 0.1, (79.0, 2.0, 3.6)); key(pq, "location", tcv + 0.5, (81.0, 2.0, 2.4))
key(pq, "location", tsi + 0.1, (81.0, 2.0, 2.3)); key(pq, "location", tsi + 0.35, (81.0, 2.0, 2.75))
key(pq, "location", tdx - 0.1, (81.0, 2.0, 2.3)); key(pq, "location", tdx + 0.15, (81.0, 2.0, 2.75))
key(pq, "rotation_euler", tsi, (0, 0, 0)); key(pq, "rotation_euler", tpp + 0.3, (0, math.radians(14), math.radians(20)))
xC = xis("xC", (81.0, 1.0, 3.2), 1.3); visivel(xC, tpp - 0.05, t1 + 0.1); pop(xC, tpp - 0.05, 1.0)
# rótulo visual 'sistema' e 'DirectX': dois blocos coloridos que acendem na base
s1 = caixa("blocoSis", (80.3, 1.25, 1.2), (0.7, 0.1, 0.5), ROSA, unico="blocoSis"); s2 = caixa("blocoDX", (81.7, 1.25, 1.2), (0.7, 0.1, 0.5), AMARELO, unico="blocoDX")
visivel(s1, tsi - 0.1); pop(s1, tsi - 0.1, 1.0); visivel(s2, tdx - 0.1); pop(s2, tdx - 0.1, 1.0); brilha(s1); brilha(s2)
gC = pixel("guiaC", (79.1, -0.6, 0), escala=0.85); girarZ(gC["raiz"], 18); respirar(gC, t0, t1 + 0.5)
pensar(gC, t0 + 0.1, 1.6); apontar(gC, tpr - 0.1, 1.4, "D", 70); comemorar(gC, tpa - 0.1, 1.0); apontar(gC, tre - 0.1, 1.4, "D", 40); espanto(gC, tpp - 0.1, 1.3)
plano(t0, (80.0, 2.0), "geral", altura=2.6); plano(tpb - 0.4, (80.0, 2.0), "geral", altura=2.6)
plano(tpb - 0.05, (80.4, 1.6), "medio", altura=2.2); plano(t1 - 0.05, (80.6, 1.6), "medio", altura=2.3)

# =====================================================================
# ZONA D (x = 120) — shaders: lâmpada + esfera com sombra; 1 placa no console x muitas placas no PC; equipe + calendário (bloco 3)
# =====================================================================
t0, t1 = S[3]
sala("D", 120, (0.40, 0.30, 0.55, 1), (0.34, 0.25, 0.48, 1), (0.16, 0.22, 0.40, 1))
tsh = T(3, "shaders"); tlu = T(3, "luz"); tso = T(3, "sombra"); tcn = T(3, "console"); tun = T(3, "única"); tpl = T(3, "placa")
tmi = T(3, "milhares"); tpo = T(3, "port"); tme = T(3, "meses"); tes = T(3, "estúdio")
lamp = esfera("lampD", (118.6, 2.0, 4.2), 0.45, (1.0, 0.95, 0.6, 1), sub=3); liso(lamp); brilha(lamp)
bas = cilindro("basLamp", (118.6, 2.0, 4.75), 0.2, 0.3, CINZA, seg=10)
bolaD = esfera("bolaD", (120.2, 2.0, 1.4), 0.7, (0.95, 0.40, 0.35, 1), sub=3); liso(bolaD)
sombra = cilindro("sombraD", (120.9, 2.2, 0.02), 0.75, 0.02, (0.10, 0.08, 0.16, 1), seg=24); sombra.scale = (1.5, 1, 1)
ped = cilindro("pedD", (120.2, 2.0, 0.35), 0.5, 0.7, BRANCO, seg=16)
for ob, tt in ((lamp, tsh), (bas, tsh), (bolaD, tlu), (ped, tlu), (sombra, tso)):
    visivel(ob, tt - 0.15, tcn - 0.1); pop(ob, tt - 0.15, 1.0 if ob is not sombra else 1.0)
raio = cabo("raioD", (118.6, 2.0, 3.8), (120.0, 2.0, 2.0), 0.04, AMARELO, unico="raioD"); visivel(raio, tlu, tcn - 0.1); BRILHO.append(mat(AMARELO, "raioD"))
# console com UMA placa  x  PC com muitas placas diferentes
cD = console("consD", (117.2, 1.8, 0.9), 1.0); visivel(cD, tcn - 0.15, tpo - 0.1); pop(cD, tcn - 0.15, 1.0)
pv1 = placa_video("placaUnica", (117.2, 1.0, 2.3), VERDE, 1.0); visivel(pv1, tun - 0.15, tpo - 0.1); pop(pv1, tun - 0.15, 1.0)
cores_p = [ROSA, CIANO, AMARELO, LARANJA, ROXO, VERMELHO, AZUL, BRANCO, VERDE]
k = 0
for i in range(4):
    for j in range(4):
        pvx = placa_video(_id("placaPC"), (120.6 + i * 1.15, 2.4, 0.7 + j * 0.85), cores_p[(i * 3 + j) % 9], 0.8)
        tt = tmi - 0.2 + 0.04 * k; visivel(pvx, tt, tpo - 0.1); pop(pvx, tt, 0.8); k += 1
# 'isso é um port': equipe pequena em mesas + calendário passando
calD = calendario("calD", (122.6, 3.8, 3.6), 1.1); visivel(calD, tpo - 0.15); pop(calD, tpo - 0.15, 1.1)
for k in range(4):
    pg = caixa(_id("folha"), (122.6, 3.6, 3.4), (1.6, 0.04, 1.4), BRANCO); visivel(pg, tme + k * 0.3, tme + k * 0.3 + 0.45)
    key(pg, "location", tme + k * 0.3, (122.6, 3.6, 3.4)); key(pg, "location", tme + k * 0.3 + 0.45, (123.4, 2.6, 5.4))
    key(pg, "rotation_euler", tme + k * 0.3, (0, 0, 0)); key(pg, "rotation_euler", tme + k * 0.3 + 0.45, (math.radians(-60), math.radians(30), 0))
for k in range(4):
    mx = 117.6 + k * 1.5
    me_ = caixa(_id("mesaD"), (mx, 1.6, 0.8), (1.2, 0.8, 0.1), (0.30, 0.22, 0.18, 1))
    mn_, _ = monitor(_id("monD"), (mx, 1.9, 1.3), (0.30, 0.85, 1.0, 1), 0.8, 0.5, unico="telaD")
    dev = pessoinha(_id("dev"), (mx, 1.0, 0), cores_p[k], 0.9); girarZ(dev, 180)
    for ob in (me_, mn_, dev): visivel(ob, tpo - 0.05 + 0.08 * k); pop(ob, tpo - 0.05 + 0.08 * k, 0.9 if ob is dev else 1.0)
BRILHO.append(mat((0.30, 0.85, 1.0, 1), "telaD"))
gD = pixel("guiaD", (117.9, -0.6, 0), escala=0.85); girarZ(gD["raiz"], 20); respirar(gD, t0, t1 + 0.5)
apontar(gD, tsh - 0.1, 1.4, "D", 80); apontar(gD, tun - 0.2, 1.4, "D", 50); espanto(gD, tmi - 0.1, 1.3); pensar(gD, tme - 0.1, 1.6)
plano(t0, (119.4, 2.0), "medio", altura=2.6); plano(tcn - 0.4, (119.4, 2.0), "medio", altura=2.6)
plano(tcn - 0.05, (119.6, 1.8), "geral", altura=2.2); plano(tpo - 0.4, (120.0, 1.8), "geral", altura=2.3)
cam_key(tpo - 0.05, (120.0, -7.0, 2.8), (120.0, 2.0, 2.0)); cam_key(t1 - 0.05, (120.4, -6.6, 2.8), (120.2, 2.0, 2.0))

# =====================================================================
# ZONA E (x = 160) — a queda: telão de bolhas e 'repositório' (servidor) apagam; cadeado; ampulheta de 2 anos (bloco 4)
# =====================================================================
t0, t1 = S[4]
sala("E", 160, (0.30, 0.32, 0.42, 1), (0.25, 0.27, 0.36, 1), (0.22, 0.16, 0.30, 1))
tqd = T(4, "queda"); tvq = T(4, "vinte"); tdc = T(4, "Discord"); tgh = T(4, "GitHub"); tsu = T(4, "sumiram")
tgr = T(4, "garoto"); trk = T(4, "Rockstar"); tdo = T(4, "dois"); tba = T(4, "banimento"); tnc = T(4, "comentou")
telE = caixa("telaoE", (158.4, 4.2, 3.6), (5.0, 0.2, 3.2), (0.20, 0.22, 0.36, 1))
BOL = []
for i in range(4):
    for j in range(2):
        b = bolha(_id("bolE"), (156.8 + i * 1.1, 4.0, 3.0 + j * 1.1), cores[(i + 2 * j) % 6], 0.85); BOL.append(b)
        visivel(b, t0, tdc + 0.4 + 0.05 * (i + j)); sumir(b, tdc + 0.1 + 0.05 * (i + j), 0.3)
srvE = servidor("srvE", (163.0, 3.0, 1.3), 1.0, VERDE, "ledSrvE"); mS = mat(VERDE, "ledSrvE"); BRILHO.append(mS)
cor_key(mS, tgh - 0.05, VERDE); cor_key(mS, tgh + 0.25, (0.95, 0.15, 0.15, 1))
off = esfera("offE", (163.0, 2.4, 3.0), 0.3, VERMELHO, sub=3, unico="offE"); liso(off); visivel(off, tsu - 0.1); pop(off, tsu - 0.1, 1.0)
mo = mat(VERMELHO, "offE"); BRILHO.append(mo)
t = tsu; k = 0
while t < tgr:
    cor_key(mo, t, VERMELHO if k % 2 else (1.0, 0.8, 0.8, 1)); t += 0.2; k += 1
# o garoto diz: balão de pensamento + cadeado; ampulheta = 2 anos
cdE = cadeado("cadeadoE", (158.4, 3.6, 3.6), 1.4); visivel(cdE, tsu + 0.1); pop(cdE, tsu + 0.1, 1.4)
amp = ampulheta("ampE", (161.0, 1.6, 1.4), 1.2); visivel(amp, tdo - 0.15); pop(amp, tdo - 0.15, 1.2)
key(amp, "rotation_euler", tba, (0, 0, 0)); key(amp, "rotation_euler", tba + 0.6, (0, math.radians(180), 0))
iqE = interroga("interE", (163.0, 1.4, 4.4), 0.9); visivel(iqE, tnc - 0.2); pop(iqE, tnc - 0.2, 0.9)
pcE = pc_torre("pcE", (156.4, 1.6, 0.8), 1.0)
gE = pixel("guiaE", (158.2, -0.6, 0), escala=0.85); girarZ(gE["raiz"], 10); respirar(gE, t0, t1 + 0.5)
espanto(gE, tqd - 0.1, 1.3); apontar(gE, tdc - 0.1, 1.4, "D", 70); pensar(gE, tgr - 0.1, 1.6); apontar(gE, tdo - 0.1, 1.2, "D", 40); pensar(gE, tnc - 0.2, 1.4)
plano(t0, (159.6, 2.4), "geral", altura=2.6); plano(tgr - 0.4, (159.8, 2.4), "geral", altura=2.6)
plano(tgr - 0.05, (159.6, 1.4), "medio", altura=2.0); plano(t1 - 0.05, (160.0, 1.4), "medio", altura=2.1)

# =====================================================================
# ZONA F (x = 200) — envelope de direitos autorais sai do prédio da empresa e chega ao servidor da plataforma,
# que apaga (tira do ar) os blocos (bloco 5)
# =====================================================================
t0, t1 = S[5]
sala("F", 200, (0.85, 0.88, 0.95, 1), (0.74, 0.78, 0.88, 1), (0.20, 0.45, 0.55, 1))
tem = T(5, "empresa"); tder = T(5, "derruba"); tno = T(5, "notificação"); tdi2 = T(5, "direitos"); tdm = T(5, "DMCA")
ten = T(5, "enviada"); tpla = T(5, "plataforma"); tti = T(5, "tira"); tar2 = T(5, "ar")
emp = predio_empresa("empresaF", (196.6, 2.6, 0), 1.0); visivel(emp, t0); pop(emp, t0 + 0.05, 1.0)
plat = servidor("plataformaF", (203.6, 2.6, 1.3), 1.0, CIANO, "ledPlat"); mP = mat(CIANO, "ledPlat"); BRILHO.append(mP)
visivel(plat, tem - 0.1); pop(plat, tem - 0.1, 1.0)
env = envelope("envF", (196.6, 1.6, 2.4), 1.2); visivel(env, tno - 0.15, tti + 0.2); pop(env, tno - 0.15, 1.2)
key(env, "location", ten - 0.1, (196.6, 1.6, 2.4)); key(env, "location", tpla + 0.2, (203.6, 1.6, 2.8))
key(env, "rotation_euler", ten - 0.1, (0, 0, 0)); key(env, "rotation_euler", tpla + 0.2, (0, math.radians(360), 0))
cp = anel("copy", (0, 0, 0), 0.22, 0.05, VERMELHO, seg=20); filho(env, cp); cp.location = (0.28, -0.07, 0.12); cp.rotation_euler = (math.radians(90), 0, 0)
BLK = []
for i in range(3):
    for j in range(2):
        bl = caixa(_id("blocoF"), (201.8 + i * 0.9, 1.0, 0.4 + j * 0.8), (0.75, 0.75, 0.75), cores[(i + j * 3) % 6]); liso(bl); BLK.append(bl)
        visivel(bl, t0, tar2 + 0.6); sumir(bl, tti + 0.05 * (i + j * 3), 0.3)
cor_key(mP, tti - 0.1, CIANO); cor_key(mP, tti + 0.2, (0.95, 0.15, 0.15, 1))
xF = xis("xF", (202.7, 0.4, 1.4), 1.6); visivel(xF, tar2); pop(xF, tar2, 1.0)
gF = pixel("guiaF", (199.6, -1.2, 0), escala=0.85); girarZ(gF["raiz"], 0); respirar(gF, t0, t1 + 0.5)
pensar(gF, t0 + 0.1, 1.4); apontar(gF, tno - 0.1, 1.4, "E", 50); apontar(gF, tpla - 0.1, 1.4, "D", 50); espanto(gF, tti - 0.1, 1.2)
cam_key(t0, (200.0, -7.4, 3.0), (200.0, 2.0, 2.4)); cam_key(tno - 0.4, (200.0, -7.2, 3.0), (200.0, 2.0, 2.4))
cam_key(tno - 0.05, (198.2, -5.6, 2.8), (198.4, 1.8, 2.4)); cam_key(ten - 0.2, (198.4, -5.6, 2.8), (198.6, 1.8, 2.4))
cam_key(tpla + 0.3, (201.8, -6.0, 2.6), (202.2, 1.8, 1.8)); cam_key(t1 - 0.05, (202.0, -6.2, 2.6), (202.4, 1.8, 1.8))

# =====================================================================
# ZONA G (x = 240) — calendário 2027 (folhas viram), PC embrulhado para presente + interrogação (sem anúncio) (bloco 6)
# =====================================================================
t0, t1 = S[6]
sala("G", 240, (0.45, 0.75, 0.55, 1), (0.38, 0.66, 0.48, 1), (0.95, 0.55, 0.25, 1))
tof = T(6, "oficial"); tgb = T(6, "GamesBeat"); tcm = T(6, "começo"); tdm2 = T(6, "dois"); tan = T(6, "anunciou")
pres = presente("presenteG", (241.6, 1.8, 0.7), 1.0); visivel(pres, tof - 0.15); pop(pres, tof - 0.15, 1.0)
pcG = pc_torre("pcG", (241.6, 1.8, 2.4), 0.8); visivel(pcG, tof - 0.1); pop(pcG, tof - 0.1, 0.8)
calG = calendario("calG", (238.4, 2.6, 2.6), 1.4); visivel(calG, tcm - 0.2); pop(calG, tcm - 0.2, 1.4)
for k in range(5):
    pg = caixa(_id("folhaG"), (238.4, 2.4, 2.4), (2.2, 0.04, 1.9), BRANCO); tt = tcm + k * 0.28
    visivel(pg, tt, tt + 0.45)
    key(pg, "location", tt, (238.4, 2.4, 2.4)); key(pg, "location", tt + 0.45, (239.4, 1.2, 4.8))
    key(pg, "rotation_euler", tt, (0, 0, 0)); key(pg, "rotation_euler", tt + 0.45, (math.radians(-70), math.radians(25), 0))
bri = esfera("brilhoCal", (238.4, 2.3, 2.1), 0.35, AMARELO, sub=2, unico="brCal"); visivel(bri, tdm2, t1 + 0.1); pop(bri, tdm2, 1.0); BRILHO.append(mat(AMARELO, "brCal"))
iqG = interroga("interG", (241.6, 1.8, 4.2), 1.0); visivel(iqG, tan - 0.3); pop(iqG, tan - 0.3, 1.0)
key(iqG, "rotation_euler", tan, (math.radians(90), 0, 0)); key(iqG, "rotation_euler", t1 + 0.3, (math.radians(90), 0, math.radians(200)))
gG = pixel("guiaG", (237.6, -0.6, 0), escala=0.85); girarZ(gG["raiz"], 18); respirar(gG, t0, t1 + 0.5)
pensar(gG, t0 + 0.05, 1.2); apontar(gG, tcm - 0.1, 1.6, "D", 60); comemorar(gG, tdm2 - 0.1, 1.2); pensar(gG, tan - 0.2, 1.4)
plano(t0, (239.6, 2.0), "geral", altura=2.4); plano(tcm - 0.4, (239.6, 2.0), "geral", altura=2.4)
plano(tcm - 0.05, (238.8, 1.6), "medio", altura=2.4); plano(tan - 0.4, (239.0, 1.6), "medio", altura=2.4)
plano(tan - 0.05, (240.6, 1.6), "medio", altura=2.6); plano(t1 - 0.05, (240.8, 1.6), "medio", altura=2.7)

# =====================================================================
# 7 — convite: volta ao quarto do gancho, tela azul de novo; troféu (zerei) x fila de pessoinhas (na fila); like
# =====================================================================
t0 = S[7][0]
tze = T(7, "zerei"); tfi = T(7, "fila"); tjo = T(7, "jogou")
cor_key(mtA, t0 - 0.05, (0.95, 0.25, 0.22, 1)); cor_key(mtA, t0 + 0.1, (0.30, 0.85, 1.0, 1))
tro = vazio("trofeu", (-0.9, 1.0, 2.0))
for nm, loc, r1, r2, h in (("copo", (0, 0, 0.45), 0.35, 0.15, 0.6), ("haste", (0, 0, 0.05), 0.07, 0.07, 0.3), ("pe", (0, 0, -0.15), 0.25, 0.25, 0.12)):
    c = cilindro(_id(nm), (0, 0, 0), r1, h, OURO, seg=14, r2=r2); filho(tro, c); c.location = loc
visivel(tro, tze - 0.15); pop(tro, tze - 0.15, 1.0)
for k in range(4):
    pp = pessoinha(_id("filaCTA"), (0.9 + k * 0.55, 1.0 + k * 0.25, 1.06), cores[k], 0.55)
    visivel(pp, tfi - 0.2 + 0.06 * k); pop(pp, tfi - 0.2 + 0.06 * k, 0.55)
acenar(px, t0 + 0.1, 1.4); apontar(px, tze - 0.1, 1.2, "D", 40); apontar(px, tfi - 0.1, 1.2, "D", 60)
acenar(px, LEG[-1]["e"] + 1.2, 1.6); comemorar(px, LEG[-1]["e"] + 3.0, 1.4)
cam_key(t0, (-0.6, -6.8, 2.6), (-0.6, 1.2, 2.0)); cam_key(FIM, (-0.3, -6.4, 2.6), (-0.3, 1.2, 2.0))

# ---------- corte seco entre zonas ----------
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
