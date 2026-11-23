"""Série 2, vídeo 01 — 'Por que o GTA 6 se pagou em um único dia?' Miniaturas ORIGINAIS (nenhuma arte do jogo).
Uso: REALISTA=1 blender -b --factory-startup -P cena_gta.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
import bpy, sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
from lowpoly import *

args = sys.argv[sys.argv.index("--") + 1:]
PASTA = args[0]
LEG = json.load(open(os.path.join(PASTA, "legendas.json"), encoding="utf-8"))
FIM = LEG[-1]["e"] + 1.3
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
random.seed(7)
scn.world.color = (0.30, 0.60, 0.95)

OURO = (1.0, 0.74, 0.12, 1); OURO2 = (0.92, 0.62, 0.08, 1); COFRE = (0.36, 0.40, 0.46, 1)
CAIXA_J = (0.10, 0.11, 0.16, 1); FAIXA_J = (0.95, 0.30, 0.55, 1); ESTEIRA = (0.20, 0.21, 0.24, 1)

# ---------------- chão: quarteirão em miniatura ----------------
chao = caixa("chao", (0, 0, -0.25), (400, 400, 0.5), C["grama"])
for y in (-4, 22, 48):
    caixa("ruaH", (0, y, 0.02), (140, 5, 0.06), C["rua"])
for x in (-34, 0, 34):
    caixa("ruaV", (x, 22, 0.03), (5, 60, 0.06), C["rua"])
for _ in range(26):
    arvore((random.uniform(-70, 70), random.uniform(-40, -20) if random.random() < 0.4 else random.uniform(55, 80)), random.uniform(0.8, 1.3))

# ---------------- cofre central (fica o vídeo todo) ----------------
cofre = caixa("cofre", (0, -16, 4), (12, 8, 8), COFRE)
porta = cilindro("portaCofre", (0, -20.1, 4), 3.0, 0.4, OURO2, seg=24); porta.rotation_euler = (math.radians(90), 0, 0)
for k in range(4):
    r = caixa("raio", (0, -20.4, 4), (0.4, 0.3, 5.0), (0.75, 0.75, 0.78, 1)); r.rotation_euler = (0, math.radians(45 * k), 0)
pilha = cilindro("pilhaOuro", (0, -16, 8.0), 4.2, 0.01, OURO, seg=24, unico="pilhaOuro")  # cresce no topo do cofre
pilha.location = (0, -16, 8.0)

def moeda(nome, loc, r=1.3):
    m = cilindro(nome, loc, r, 0.22, OURO, seg=16, unico="moeda"); m.rotation_euler = (math.radians(90), 0, 0); return m

def chuva_moedas(t0, t1, n, origem, alvo_pos, alt=14, dur=0.9):
    for k in range(n):
        ta = t0 + (t1 - t0) * k / n
        o = tuple(v + random.uniform(-4, 4) for v in origem)
        m = moeda(f"moeda{k}_{int(t0*10)}", o)
        visivel(m, ta, ta + dur)
        meio = ((o[0] + alvo_pos[0]) / 2, (o[1] + alvo_pos[1]) / 2, max(o[2], alvo_pos[2]) + alt)
        caminho(m, ta, ta + dur, lambda u, o=o, meio=meio: bez(o, meio, alvo_pos, suave(u)), orientar=False, passo=2)
        m.rotation_mode = "XYZ"
        key(m, "rotation_euler", ta, (math.radians(90), 0, 0)); key(m, "rotation_euler", ta + dur, (math.radians(90), math.radians(540), 0))

def altura_pilha(t, h):
    pilha.scale = (1, 1, max(0.01, h) / 0.01); pilha.keyframe_insert("scale", frame=f(t))
    pilha.location = (0, -16, 8.0 + h / 2); pilha.keyframe_insert("location", frame=f(t))

# câmera
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 26; cam_d.clip_end = 3000
cam = bpy.data.objects.new("cam", cam_d); scn.collection.objects.link(cam); scn.camera = cam
alvo = vazio("alvo")
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def cam_key(t, loc, tgt):
    for ob, v in ((cam, loc), (alvo, tgt)):
        ob.location = v; ob.keyframe_insert("location", frame=f(t))

# =====================================================================
# 0 — GANCHO: o cofre recebe uma avalanche de moedas
# =====================================================================
t0, t1 = S[0]
altura_pilha(0, 0.01); altura_pilha(T(0, "pagou"), 0.01); altura_pilha(t1, 3.0)
chuva_moedas(0.2, t1 - 0.6, 36, (0, 10, 12), (0, -16, 9.5), alt=8, dur=1.0)
cam_key(t0, (14, -42, 12), (0, -16, 7)); cam_key(t1 - 0.05, (9, -36, 10), (0, -16, 8))

# =====================================================================
# 1 — a cidade e o "exército" de desenvolvedores
# =====================================================================
t0, t1 = S[1]
tc_ = T(1, "cidade"); td = T(1, "desenvolvedores"); ta = T(1, "Analistas")
lotes = [(x, y) for x in (-50, -42, -26, -18, -8, 8, 18, 26, 42, 50) for y in (6, 14, 30, 38)]
random.shuffle(lotes)
for k, (x, y) in enumerate(lotes):
    h = random.uniform(5, 22) if abs(x) < 30 else random.uniform(4, 12)
    p = predio((x, y), random.uniform(5, 7), random.uniform(5, 7), h, random.choice(PREDIOS))
    tp = tc_ + 0.12 * k if k < 30 else tc_ + 3.6
    visivel(p, tp); pop(p, tp, dur=0.3)
carros = []
for k in range(10):
    cor = random.choice([C["ameaca"], C["ciano"], C["branco"], C["defesa"], C["azulmarinho"]])
    car = caixa(f"carro{k}", (0, 0, 0.6), (1.6, 3.2, 1.0), cor)
    filho(car, caixa(f"vidro{k}", (0, -0.2, 0.75), (1.4, 1.6, 0.6), (0.2, 0.25, 0.3, 1)))
    carros.append(car)
    y = (-4, 22, 48)[k % 3] + (1.2 if k % 2 else -1.2); d = 1 if k % 2 else -1
    x0 = -70 + k * 14
    visivel(car, tc_ + 1.0)
    caminho(car, tc_ + 1.0, FIM, lambda u, x0=x0, y=y, d=d: (((x0 + d * u * 400 + 70) % 140) - 70, y, 0.6), passo=3)
# estúdio: mesas com telas e devs (bonecos sem capacete)
devs = []
for i in range(5):
    for j in range(3):
        x, y = -10 + i * 5, -34 - j * 4
        mesa = caixa(f"mesa{i}{j}", (x, y, 0.8), (3.2, 1.6, 0.2), C["madeira"])
        tela = caixa(f"tela{i}{j}", (x, y + 0.5, 1.7), (2.4, 0.15, 1.4), C["tela"]); filho(mesa, tela); tela.location = (0, 0.5, 0.9)
        b, _, _ = boneco(f"dev{i}{j}", (x, y - 1.3, 0), camisa=random.choice(PREDIOS[:4] + [C["ameaca"], C["ciano"]]), capacete=False)
        b.rotation_euler = (0, 0, math.radians(180)); b.rotation_euler = (0, 0, 0)
        for ob in (mesa, b):
            visivel(ob, td - 0.4 + 0.05 * (i * 3 + j)); pop(ob, td - 0.4 + 0.05 * (i * 3 + j))
        devs.append(b)
altura_pilha(t0, 3.0)
cam_key(t0, (-60, -30, 45), (0, 22, 0)); cam_key(td - 0.6, (-30, 10, 60), (0, 22, 4))
cam_key(td - 0.2, (0, -52, 9), (0, -36, 1)); cam_key(ta - 0.1, (6, -48, 8), (0, -36, 1.5))
cam_key(ta, (34, -58, 18), (8, -34, 4)); cam_key(t1 - 0.05, (30, -52, 22), (4, -26, 6))
# etiqueta de custo: pilha de notas verdes que cresce ao lado do estúdio
custo = caixa("custo", (16, -36, 0.01), (4, 4, 0.02), (0.30, 0.68, 0.30, 1), unico="custo")
visivel(custo, ta)
for t_, h in ((ta, 0.02), (ta + 1.2, 9.0)):
    custo.scale = (1, 1, h / 0.02); custo.keyframe_insert("scale", frame=f(t_))
    custo.location = (16, -36, h / 2); custo.keyframe_insert("location", frame=f(t_))

# =====================================================================
# 2 — pré-venda: caixinhas na esteira até o cofre
# =====================================================================
t0, t1 = S[2]
tpv = T(2, "pré"); t32 = T(2, "trinta")
est = caixa("esteira", (-30, -16, 0.6), (40, 3.2, 1.2), ESTEIRA)
visivel(est, t0)
for k in range(28):
    cx = caixa(f"jogo{k}", (0, 0, 0), (2.4, 0.45, 3.2), CAIXA_J)
    filho(cx, caixa(f"jogoF{k}", (0, -0.17, 0.5), (2.3, 0.06, 0.7), FAIXA_J))
    ta_ = tpv - 1.0 + k * 0.55; tb = ta_ + 4.0
    visivel(cx, ta_, tb)
    caminho(cx, ta_, tb, lambda u: (-50 + 44 * u, -16, 2.85), orientar=False, passo=2)
contador = caixa("contador", (-14, -24, 0.01), (3, 3, 0.02), FAIXA_J, unico="contador")
visivel(contador, t32)
for t_, h in ((t32, 0.02), (t32 + 1.5, 14.0)):
    contador.scale = (1, 1, h / 0.02); contador.keyframe_insert("scale", frame=f(t_))
    contador.location = (-14, -24, h / 2); contador.keyframe_insert("location", frame=f(t_))
altura_pilha(t1, 5.0)
cam_key(t0, (-42, -32, 8), (-30, -16, 2.5)); cam_key(tpv, (-34, -30, 7), (-24, -16, 3))
cam_key(t32, (-26, -42, 12), (-14, -20, 6)); cam_key(t1 - 0.05, (-20, -50, 16), (-8, -18, 7))

# =====================================================================
# 3 — o cofre enche de uma vez (US$ 3,79 bilhões no 1º dia)
# =====================================================================
t0, t1 = S[3]
tcf = T(3, "cofre"); t379 = T(3, "três")
chuva_moedas(tcf - 0.3, t1 - 0.5, 70, (0, 20, 30), (0, -16, 12), alt=10, dur=1.1)
altura_pilha(tcf, 5.0); altura_pilha(t379 + 1.5, 13.0); altura_pilha(t1, 14.0)
explosao((0, -16, 22), t379, r=5, n=14)
cam_key(t0, (22, -50, 18), (0, -16, 8)); cam_key(t379, (14, -42, 14), (0, -16, 14)); cam_key(t1 - 0.05, (10, -46, 30), (0, -16, 16))

# =====================================================================
# 4 — comparação: GTA 5 (2013) x GTA 6 no 1º dia (barras)
# =====================================================================
t0, t1 = S[4]
t5 = T(4, "GTA"); t800 = T(4, "oitocentos"); tx = T(4, "cinco")
base_cmp = caixa("palco", (40, -16, 0.3), (22, 12, 0.6), (0.94, 0.94, 0.94, 1)); visivel(base_cmp, t0, t1)
def barra(nome, x, cor, t_, h):
    b = caixa(nome, (x, -16, 0.6), (5, 5, 0.02), cor, unico=nome); visivel(b, t0, t1)
    for tt, hh in ((t_, 0.02), (t_ + 1.0, h)):
        b.scale = (1, 1, hh / 0.02); b.keyframe_insert("scale", frame=f(tt))
        b.location = (x, -16, 0.6 + hh / 2); b.keyframe_insert("location", frame=f(tt))
barra("barra5", 34, (0.62, 0.64, 0.68, 1), t800, 4.0)
barra("barra6", 46, OURO, tx - 0.6, 19.0)
cam_key(t0, (40, -52, 10), (40, -16, 5)); cam_key(tx, (40, -56, 14), (40, -16, 9)); cam_key(t1 - 0.05, (38, -58, 16), (40, -16, 10))

# =====================================================================
# 5 — digital: a fábrica de discos e o caminhão somem
# =====================================================================
t0, t1 = S[5]
tdg = T(5, "digital"); tcod = T(5, "código"); tdc = T(5, "disco"); tcf5 = T(5, "cofre")
fab = caixa("fabrica", (-30, -34, 4), (12, 9, 8), (0.80, 0.78, 0.74, 1)); visivel(fab, t0, tdc + 0.4)
cham = cilindro("chamine", (-26, -32, 10), 1.0, 6, (0.55, 0.52, 0.5, 1)); filho(fab, cham); cham.location = (4, 2, 6)
cam_, _ = caminhao("caminhaoDiscos", (-18, -26, 1.0), cor=C["branco"], tubos=False); visivel(cam_, t0, tdc + 0.4)
cam_.rotation_euler = (0, 0, math.radians(90))
sumir(fab, tdc); sumir(cam_, tdc)
seta = seta3d("setaDigital", 10, C["verde_ok"]); visivel(seta, tcf5 - 0.6, t1)
seta.location = (-18, -16, 3.2); seta.rotation_euler = (0, math.radians(90), 0); pop(seta, tcf5 - 0.6)
cx5 = caixa("caixaCodigo", (-26, -16, 2.6), (2.4, 0.5, 3.0), CAIXA_J); visivel(cx5, tcod - 0.3, t1); pop(cx5, tcod - 0.3, 1.4)
cam_key(t0, (-50, -52, 22), (-24, -26, 3)); cam_key(tdc + 0.5, (-44, -48, 18), (-20, -20, 3)); cam_key(t1 - 0.05, (-30, -46, 14), (-12, -16, 4))

# =====================================================================
# 6 — o lançamento é só o começo: edição especial e atualizações
# =====================================================================
t0, t1 = S[6]
ted = T(6, "edição"); tat = T(6, "atualizações")
esp = caixa("edicaoEsp", (-8, -26, 2.2), (2.6, 0.5, 3.2), OURO2); visivel(esp, ted - 0.2, t1); pop(esp, ted - 0.2, 1.3)
filho(esp, caixa("edicaoF", (0, -0.28, 0.7), (2.4, 0.05, 0.7), CAIXA_J))
for k in range(5):
    s3 = seta3d(f"setaAtt{k}", 5, C["ciano"]); s3.location = (-10 + k * 5, -8, 8 + (k % 2) * 2)
    visivel(s3, tat + 0.15 * k, t1); pop(s3, tat + 0.15 * k)
altura_pilha(t1, 16.0)
for k in range(16):  # esteira continua
    cx = caixa(f"jogoB{k}", (0, 0, 0), (2.4, 0.45, 3.2), CAIXA_J)
    filho(cx, caixa(f"jogoBF{k}", (0, -0.17, 0.5), (2.3, 0.06, 0.7), FAIXA_J))
    ta_ = t0 - 2 + k * 0.6; visivel(cx, ta_, ta_ + 4)
    caminho(cx, ta_, ta_ + 4, lambda u: (-50 + 44 * u, -16, 2.85), orientar=False, passo=2)
cam_key(t0, (-26, -44, 12), (-8, -20, 4)); cam_key(tat, (-6, -48, 20), (-4, -14, 8)); cam_key(t1 - 0.05, (8, -50, 26), (0, -14, 10))

# =====================================================================
# 7 — final: cidade inteira + cofre cheio (CTA)
# =====================================================================
t0 = S[7][0]
cam_key(t0, (-70, -90, 60), (0, 5, 4)); cam_key(FIM, (-30, -100, 70), (0, 8, 4))

# ---------- render ----------
if os.environ.get("REALISTA"):
    modo_realista(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "hdri", "ceu_parcialmente_nublado_2k.hdr"), foco=alvo)
    for nome in ("moeda", "pilhaOuro"):
        m = bpy.data.materials.get(nome)
        b = m and m.node_tree and m.node_tree.nodes.get("Principled BSDF")
        if b: b.inputs["Metallic"].default_value = 0.85; b.inputs["Roughness"].default_value = 0.3
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
