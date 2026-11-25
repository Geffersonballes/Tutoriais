"""Série 2 — 'Como a sua LIVE chega em milhões de celulares ao mesmo tempo?' (estilo C cartoon, mascote Pixel).
Mecanismo peça por peça: aperta 'Iniciar LIVE' -> o celular comprime o vídeo para caber no 4G -> servidor de
entrada (ingest) -> transcodificação em alta/média/baixa -> cada espectador recebe a versão da sua internet ->
CDN: cópias perto de quem assiste (o celular manda um vídeo só) -> chat e presentes por outro caminho, mais rápido
-> convite para a primeira LIVE.
Visual 100 % original: nenhuma tela, ícone ou logotipo real de plataforma; nenhum rosto real (o Pixel faz o streamer).
Base técnica/visual: cena_gta_twitch.py. Melhoria do backlog: TE() com casamento EXATO de palavra (sem pegar substring).
Uso: blender -b --factory-startup -P cena_live.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
import bpy, sys, os, json, math, random, re, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowpoly import *
from lowpoly import _id
from cartoon import *

args = sys.argv[sys.argv.index("--") + 1:]
PASTA = args[0]
LEG = json.load(open(os.path.join(PASTA, "legendas.json"), encoding="utf-8"))
FIM = LEG[-1]["e"] + 1.3
NSEG = max(x["seg"] for x in LEG) + 1
def seg_ini(i): return 0.0 if i == 0 else min(x["s"] for x in LEG if x["seg"] == i) - 0.15
def seg_fim(i): return seg_ini(i + 1) if i < NSEG - 1 else FIM
_norm = lambda s: re.sub(r"[^a-z0-9-]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
def T(i, palavra, n=0):
    """Tempo da n-ésima ocorrência EXATA da palavra (sem pontuação/acentos) no bloco i (backlog: 'No' casava 'nova?')."""
    hits = [x["s"] for x in LEG if x["seg"] == i and _norm(x["w"]) == _norm(palavra)]
    if not hits:   # fallback: substring, como nas cenas antigas
        hits = [x["s"] for x in LEG if x["seg"] == i and palavra.lower() in x["w"].lower()]
    return hits[min(n, len(hits) - 1)] if hits else seg_ini(i) + 0.5
S = [(seg_ini(i), seg_fim(i)) for i in range(NSEG)]

bpy.ops.wm.read_factory_settings(use_empty=True)
configurar_render()
scn = bpy.context.scene
scn.frame_start, scn.frame_end = 1, f(FIM)
random.seed(25)

AMARELO = (1.0, 0.82, 0.12, 1); VERDE = (0.20, 0.85, 0.40, 1); VERMELHO = (0.95, 0.22, 0.20, 1)
ROSA = (1.0, 0.45, 0.65, 1); ROXO = (0.60, 0.34, 0.95, 1); AZUL = (0.20, 0.55, 1.0, 1); BRANCO = (0.97, 0.97, 0.98, 1)
CIANO = (0.25, 0.95, 1.0, 1); ESCURO = (0.10, 0.11, 0.14, 1); CINZA = (0.40, 0.42, 0.48, 1)
CORES = [(0.98, 0.45, 0.35, 1), (0.30, 0.70, 1.0, 1), (0.98, 0.80, 0.25, 1), (0.45, 0.85, 0.45, 1), (0.75, 0.50, 0.95, 1), (1.0, 0.60, 0.20, 1)]
QALTA, QMEDIA, QBAIXA = VERDE, AMARELO, (1.0, 0.45, 0.30, 1)
BRILHO = []

def girar(ob, graus): ob.rotation_euler = (0, 0, math.radians(graus))
def brilha(ob): BRILHO.append(ob.data.materials[0]); return ob
def linear(ob):
    for fc in ob.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

def espectador(loc, cor, tel=True):
    corpo = cilindro(_id("esp"), loc, 0.16, 0.36, cor, seg=10)
    cab = esfera(_id("cabE"), (0, 0, 0), 0.17, random.choice([PELE, (0.75, 0.52, 0.38, 1), (0.50, 0.33, 0.22, 1)]), sub=2)
    filho(corpo, cab); cab.location = (0, 0, 0.36)
    if tel:
        t = caixa(_id("cel"), (0, 0, 0), (0.16, 0.03, 0.24), CIANO); filho(corpo, t); t.location = (0.05, -0.22, 0.14)
        t.rotation_euler = (math.radians(-25), 0, 0)
    return corpo

def pacote(nome, loc, s=0.45, cor=CIANO):
    """'Pacote de vídeo': cubo colorido com triângulo de play branco."""
    c = caixa(nome, loc, (s, s, s), cor)
    tri = cilindro(_id("play"), (0, 0, 0), s * 0.28, s * 0.06, BRANCO, seg=3); filho(c, tri)
    tri.rotation_euler = (math.radians(90), math.radians(90), 0); tri.location = (0, -s * 0.52, 0)
    return c

def celular(nome, loc, esc=1.0, tela=(0.30, 0.85, 1.0, 1)):
    """Celular genérico de pé (interface própria: tela lisa + botão redondo vermelho). Frente para -Y."""
    corpo = caixa(nome, loc, (1.15 * esc, 0.14 * esc, 2.3 * esc), ESCURO)
    tl = caixa(_id("telaCel"), (0, 0, 0), (1.0 * esc, 0.02 * esc, 2.0 * esc), tela, unico=_id("tc")); filho(corpo, tl); tl.location = (0, -0.075 * esc, 0.02 * esc)
    bt = cilindro(_id("botao"), (0, 0, 0), 0.26 * esc, 0.06 * esc, VERMELHO, seg=20, unico=_id("bt")); filho(corpo, bt)
    bt.rotation_euler = (math.radians(90), 0, 0); bt.location = (0, -0.11 * esc, -0.6 * esc)
    anelB = anel(_id("anelBt"), (0, 0, 0), 0.33 * esc, 0.03 * esc, BRANCO); filho(corpo, anelB)
    anelB.rotation_euler = (math.radians(90), 0, 0); anelB.location = (0, -0.11 * esc, -0.6 * esc)
    cam_ = cilindro(_id("camCel"), (0, 0, 0), 0.05 * esc, 0.03 * esc, (0.2, 0.2, 0.25, 1), seg=10); filho(corpo, cam_)
    cam_.rotation_euler = (math.radians(90), 0, 0); cam_.location = (0, -0.09 * esc, 1.05 * esc)
    return {"corpo": corpo, "tela": tl, "botao": bt}

def presente(nome, loc, s=0.4):
    """Caixinha de presente: rosa com fita amarela e laço."""
    c = caixa(nome, loc, (s, s, s), ROSA)
    f1 = caixa(_id("fita"), (0, 0, 0), (s * 1.03, s * 0.16, s * 1.03), AMARELO); filho(c, f1)
    f2 = caixa(_id("fita"), (0, 0, 0), (s * 0.16, s * 1.03, s * 1.03), AMARELO); filho(c, f2)
    laco = esfera(_id("laco"), (0, 0, 0), s * 0.2, AMARELO, sub=2); filho(c, laco); laco.location = (0, 0, s * 0.55)
    return c

def balao(nome, loc, L=0.7, cor=BRANCO):
    """Balão de mensagem do chat: plaquinha branca com 'rabicho' e avatar colorido."""
    b = caixa(nome, loc, (L, 0.12, 0.34), cor)
    r = cilindro(_id("rab"), (0, 0, 0), 0.09, 0.1, cor, seg=3); filho(b, r); r.rotation_euler = (math.radians(90), 0, 0); r.location = (-L * 0.35, 0, -0.2)
    av = esfera(_id("avB"), (0, 0, 0), 0.11, random.choice(CORES), sub=2); filho(b, av); av.location = (-L / 2 - 0.12, 0, 0)
    return b

def torre(nome, loc, h=1.4):
    """Servidor de borda: torrinha com lâmpada no topo. Retorna (torre, material da lâmpada)."""
    b = caixa(nome, (loc[0], loc[1], h / 2), (0.5, 0.5, h), (0.22, 0.24, 0.32, 1))
    for j in range(3):
        l = caixa(_id("ledT"), (0, 0, 0), (0.36, 0.02, 0.06), VERDE); filho(b, l); l.location = (0, -0.26, -h * 0.3 + j * 0.22)
    lamp = esfera(_id("lampT"), (0, 0, 0), 0.24, CINZA, sub=2, unico=_id("lt")); filho(b, lamp); lamp.location = (0, 0, h / 2 + 0.22)
    return b, lamp.data.materials[0]

def antena(nome, loc, h=5.0):
    """Antena de celular (4G) genérica: mastro + 3 painéis + ondas que pulsam."""
    m = cilindro(nome, (loc[0], loc[1], h / 2), 0.16, h, (0.92, 0.32, 0.26, 1), seg=8)
    for k in range(3):
        a = k / 3 * math.tau
        p = caixa(_id("painel"), (0, 0, 0), (0.22, 0.12, 0.9), BRANCO); filho(m, p)
        p.location = (0.28 * math.cos(a), 0.28 * math.sin(a), h / 2 - 0.6); p.rotation_euler = (0, 0, a)
    return m

def ondas(loc, t0, t1, cor=CIANO, R=1.4, cada=0.5, rot=(90, 0, 0)):
    """Anéis que crescem e somem (sinal saindo)."""
    t = t0
    while t < t1:
        o = anel(_id("onda"), loc, R * 0.3, 0.05, cor); o.rotation_euler = tuple(math.radians(v) for v in rot)
        visivel(o, t, t + 0.9)
        key(o, "scale", t, (0.4, 0.4, 0.4)); key(o, "scale", t + 0.9, (1.6, 1.6, 1.6)); t += cada

def tubo(nome, a, b, r, cor):
    from mathutils import Vector
    a, b = Vector(a), Vector(b); d = b - a
    c = cilindro(nome, (a + b) / 2, r, d.length, cor, seg=10)
    c.rotation_mode = "QUATERNION"; c.rotation_quaternion = d.to_track_quat("Z", "Y"); return c

BRILHO.append(mat(CIANO))
cam, alvo, cam_key, plano = camera_cartoon(24)

# =====================================================================
# ZONA A (x = 0) — quarto do streamer: o Pixel aperta 'Iniciar LIVE'  (bloco 0 e bloco 6)
# =====================================================================
t0, t1 = S[0]
QA = quarto_gamer(0)
brilha(QA["tela"])
st = pixel("streamer", (0, 1.0, 0)); respirar(st, 0, FIM)
# celular gigante (de pé, ao lado do Pixel) — é o 'celular' do streamer em escala de explicação
CA = celular("celA", (-1.7, 0.4, 1.45), esc=1.05); girar(CA["corpo"], 18)
brilha(CA["tela"]); BRILHO.append(CA["botao"].data.materials[0])
tap = T(0, "aperta"); tini = T(0, "LIVE")
# o botão afunda e a lâmpada 'ao vivo' começa a piscar
for tt, sy in ((tini - 0.15, 1.0), (tini, 0.35), (tini + 0.25, 1.0)):
    key(CA["botao"], "scale", tt, (1, sy, 1))
cor_key(CA["tela"].data.materials[0], tini - 0.05, (0.30, 0.85, 1.0, 1)); cor_key(CA["tela"].data.materials[0], tini + 0.1, (1.0, 0.35, 0.45, 1))
cor_key(CA["tela"].data.materials[0], tini + 0.8, (0.30, 0.85, 1.0, 1))
mlive = QA["live"].data.materials[0]
cor_key(mlive, 0, (0.30, 0.10, 0.12, 1)); cor_key(mlive, tini, (0.30, 0.10, 0.12, 1))
k = 0; t = tini + 0.1
while t < FIM:
    cor_key(mlive, t, (0.95, 0.15, 0.18, 1) if k % 2 == 0 else (0.55, 0.10, 0.12, 1)); t += 0.6; k += 1
ondas((-1.7, 0.2, 2.9), tini + 0.1, T(0, "outro") - 0.2, cor=VERMELHO, R=1.0, cada=0.45)
apontar(st, tap - 0.25, 1.5, "E", 35)
plano(0, (-0.8, 0.8), "medio", altura=2.0); plano(tini + 0.3, (-1.1, 0.6), "close", altura=2.0)

# ZONA G (x = -60) — mapa do país em miniatura: o sinal atravessa até um celular longe  (bloco 0, 2ª parte)
tout = T(0, "outro"); tcom = T(0, "Como")
caixa("Gfundo", (-60, 10, 3), (34, 0.4, 14), (0.55, 0.78, 1.0, 1))
caixa("Gmar", (-60, 2, -0.15), (34, 22, 0.2), (0.35, 0.65, 0.98, 1))
pais = cilindro("pais", (-60, 2.5, 0.0), 8.5, 0.3, (0.48, 0.80, 0.42, 1), seg=9)
pais.scale = (1.35, 0.8, 1)
for i in range(14):
    a = random.uniform(0, math.tau); r = random.uniform(1.0, 8.5)
    x, y = -60 + r * math.cos(a) * 1.25, 2.5 + r * math.sin(a) * 0.7
    if abs(x + 60) > 9: continue
    arvore((x, y, 0.15), 0.5)
casaA = predio((-62.0, -3.0, 0.15), 1.2, 1.2, 1.2, PREDIOS[0]); casaB = predio((-57.0, 8.6, 0.15), 1.6, 1.6, 1.6, PREDIOS[2])
celLonge = celular("celLonge", (-57.0, 6.8, 2.2), esc=0.9); girar(celLonge["corpo"], -8)
mL = celLonge["tela"].data.materials[0]; brilha(celLonge["tela"])
cor_key(mL, tout, (0.15, 0.18, 0.25, 1)); cor_key(mL, tout + 1.1, (0.15, 0.18, 0.25, 1)); cor_key(mL, tout + 1.3, (1.0, 0.35, 0.45, 1))
pkG = pacote("pacoteG", (-62.0, -3.0, 1.6), 0.5, VERMELHO)
visivel(pkG, tout - 0.2, tout + 1.3)
caminho(pkG, tout - 0.1, tout + 1.2, lambda u: bez((-62.0, -3.0, 1.6), (-59.5, 2.0, 6.0), (-57.0, 6.6, 2.4), suave(u)), orientar=False)
rastro(lambda u: bez((-62.0, -3.0, 1.6), (-59.5, 2.0, 6.0), (-57.0, 6.6, 2.4), suave(u)), tout - 0.1, tout + 1.2, cor=(1.0, 0.6, 0.6, 1), r=0.18, cada=0.06, vida=0.7)
espV = espectador((-55.6, 6.4, 0.18), CORES[1]); espV.scale = (2.2, 2.2, 2.2)
gG = pixel("guiaG", (-63.6, -4.4, 0.15), escala=0.75); girar(gG["raiz"], 20); respirar(gG, tout - 0.3, t1 + 0.5)
pensar(gG, tcom - 0.1, 1.6)
cam_key(tout - 0.12, (-60.8, -8.6, 4.0), (-59.4, 2.0, 2.2)); cam_key(tout + 1.0, (-59.8, -6.4, 3.8), (-58.0, 4.0, 2.2))
cam_key(t1 - 0.05, (-59.8, -6.0, 3.6), (-58.2, 4.0, 2.0))

# =====================================================================
# ZONA B (x = 40) — o celular comprime o vídeo para caber no 4G  (bloco 1)
# =====================================================================
t0, t1 = S[1]
sala_fechada("B", 40, (0.98, 0.84, 0.52, 1), (0.55, 0.80, 0.98, 1), prof=4.2)
CB = celular("celB", (38.2, 1.6, 2.6), esc=1.9); brilha(CB["tela"])
tcru = T(1, "cru"); tpes = T(1, "pesado"); tcmp = T(1, "comprime"); tcab = T(1, "caber"); t4g = T(1, "quatro")
# o 'vídeo cru': cubão pesado que faz o chão afundar (balança)
cru = pacote("cru", (41.0, 0.6, 1.0), 2.0, (0.85, 0.40, 0.95, 1))
visivel(cru, tcru - 0.3, tcmp + 0.6); pop(cru, tcru - 0.3, 1.0, 0.45)
key(cru, "location", tpes - 0.1, (41.0, 0.6, 1.0)); key(cru, "location", tpes + 0.15, (41.0, 0.6, 0.85)); key(cru, "location", tpes + 0.4, (41.0, 0.6, 1.0))
# prensa: placa desce e o cubão encolhe; sai um pacote pequeno e leve
prensa = caixa("prensa", (41.0, 0.6, 6.5), (2.6, 2.2, 0.35), (0.35, 0.38, 0.48, 1))
haste = caixa("hasteP", (0, 0, 0), (0.3, 0.3, 3.0), CINZA); filho(prensa, haste); haste.location = (0, 0, 1.6)
key(prensa, "location", tcmp - 0.3, (41.0, 0.6, 6.5)); key(prensa, "location", tcmp + 0.5, (41.0, 0.6, 2.35)); key(prensa, "location", tcmp + 1.1, (41.0, 0.6, 6.5))
key(cru, "scale", tcmp, (1, 1, 1)); key(cru, "scale", tcmp + 0.5, (0.25, 0.25, 0.25))
key(cru, "location", tcmp, (41.0, 0.6, 1.0)); key(cru, "location", tcmp + 0.5, (41.0, 0.6, 0.25))
leve = pacote("leve", (41.0, 0.6, 0.3), 0.5, CIANO)
visivel(leve, tcmp + 0.55, t1 + 0.1); pop(leve, tcmp + 0.55, 1.6)
mast = antena("antenaB", (45.2, 2.2), 5.2)
caminho(leve, tcab - 0.1, t4g + 0.6, lambda u: bez((41.0, 0.6, 0.3), (43.0, 0.4, 4.5), (45.2, 2.2, 4.9), suave(u)), orientar=False)
ondas((45.2, 2.2, 4.9), t4g, t1 + 0.2, cor=VERDE, R=1.6, cada=0.4, rot=(0, 0, 0))
# barra de 'peso' ao lado: alta e vermelha -> baixa e verde
caixa("pesoTubo", (36.0, 3.6, 2.2), (0.6, 0.25, 3.6), (0.18, 0.18, 0.24, 1))
peso = cilindro("pesoBarra", (36.0, 3.42, 0.5), 0.22, 1.0, VERMELHO, seg=16, unico="peso")
for v in peso.data.vertices: v.co.z += 0.5
def nivel(b, t, h): b.scale = (1, 1, h); b.keyframe_insert("scale", frame=f(t))
nivel(peso, t0, 0.05); nivel(peso, tcru, 0.05); nivel(peso, tpes + 0.2, 3.2); nivel(peso, tcmp + 0.3, 3.2); nivel(peso, tcmp + 0.8, 0.7)
cor_key(peso.data.materials[0], tcmp + 0.3, VERMELHO); cor_key(peso.data.materials[0], tcmp + 0.8, VERDE)
gB = pixel("guiaB", (39.0, -1.4, 0), escala=0.85); girar(gB["raiz"], 12); respirar(gB, t0, t1 + 0.5)
acenar(gB, t0 + 0.05, 1.0); espanto(gB, tpes - 0.1, 1.2); apontar(gB, tcmp - 0.2, 1.5, "D", 30); comemorar(gB, t4g - 0.1, 1.2)
plano(t0, (38.8, 0.4), "medio", altura=2.6); plano(tcru - 0.2, (40.4, 0.2), "geral", altura=2.6)
plano(tcab - 0.2, (43.2, 1.0), "medio", altura=3.4); plano(t1 - 0.05, (43.8, 1.2), "medio", altura=3.8)

# =====================================================================
# ZONA C (x = 80) — servidor de entrada (ingest) + máquina de transcodificação  (bloco 2)
# =====================================================================
t0, t1 = S[2]
data_center(80)
ing = caixa("ingest", (77.0, 1.8, 2.3), (2.6, 1.8, 4.6), (0.20, 0.30, 0.60, 1), unico="ing")
for j in range(5):
    l = caixa(_id("ledI"), (0, 0, 0), (2.0, 0.04, 0.14), VERDE); filho(ing, l); l.location = (0, -0.92, -1.9 + j * 0.3)
porta = anel("porta", (77.0, 0.86, 3.2), 0.7, 0.13, CINZA, unico="porta"); porta.rotation_euler = (math.radians(90), 0, 0)
cilindro("fundoPorta", (77.0, 0.88, 3.2), 0.6, 0.04, (0.05, 0.10, 0.25, 1), seg=24).rotation_euler = (math.radians(90), 0, 0)
tch = T(2, "chega"); tsv = T(2, "servidor"); tig = T(2, "ingest"); tvs = T(2, "versões"); ttr = T(2, "transcodificação")
pk2 = pacote("pacote2", (72.0, 0.6, 3.2), 0.5)
visivel(pk2, t0, tch + 1.0)
caminho(pk2, t0 + 0.1, tch + 0.6, lambda u: (72.0 + 5.0 * u, 0.6, 3.2), orientar=False)
key(pk2, "scale", tch + 0.5, (1, 1, 1)); key(pk2, "scale", tch + 0.9, (0.05, 0.05, 0.05))
mp = porta.data.materials[0]
cor_key(mp, tch, CINZA); cor_key(mp, tch + 0.4, CIANO); cor_key(mp, tig - 0.1, CIANO); cor_key(mp, tig + 0.15, AMARELO); cor_key(mp, tig + 0.6, CIANO)
destacar(ing.data.materials[0], tsv, (0.20, 0.30, 0.60, 1), 1.4)
# cano do ingest para a máquina
tubo("canoIM", (78.3, 1.0, 3.6), (80.3, 1.0, 3.6), 0.14, (0.25, 0.25, 0.30, 1))
maq = caixa("maquina", (81.4, 1.4, 2.7), (2.0, 1.6, 5.4), (0.55, 0.36, 0.95, 1), unico="maq")
engr = cilindro("engrenagem", (81.4, 0.58, 3.8), 0.5, 0.12, AMARELO, seg=10); engr.rotation_mode = "XYZ"
key(engr, "rotation_euler", t0, (math.radians(90), 0, 0)); key(engr, "rotation_euler", t1, (math.radians(90), math.radians(900), 0)); linear(engr)
SAIDAS = [(4.6, 0.50, QALTA, T(2, "alta")), (3.1, 0.36, QMEDIA, T(2, "média")), (1.6, 0.22, QBAIXA, T(2, "baixa"))]
for z, s, cor, ta in SAIDAS:
    tr = caixa(_id("trilho"), (84.2, 1.0, z - s / 2 - 0.08), (3.6, 0.7, 0.1), (0.22, 0.24, 0.30, 1))
    visivel(tr, ta - 0.2); pop(tr, ta - 0.2)
    t = ta
    while t < t1 + 0.3:
        p = pacote(_id("q"), (82.5, 1.0, z), s, cor); visivel(p, t, t + 1.5)
        caminho(p, t, t + 1.5, lambda u, z=z: (82.5 + 3.4 * u, 1.0, z), orientar=False); t += 0.3
gC = pixel("guiaC", (79.0, -1.3, 0), escala=0.85); girar(gC["raiz"], 10); respirar(gC, t0, t1 + 0.5)
apontar(gC, tsv - 0.2, 1.5, "E", 40); comemorar(gC, tig - 0.05, 1.0); apontar(gC, tvs - 0.2, 1.6, "D", 60); pensar(gC, ttr - 0.1, 1.4)
destacar(maq.data.materials[0], ttr, (0.55, 0.36, 0.95, 1), 1.2)
plano(t0, (75.8, 0.4), "medio", altura=2.8); plano(tsv - 0.25, (77.0, 0.6), "medio", altura=3.0)
plano(tvs - 0.3, (81.8, 0.6), "geral", altura=3.2); plano(t1 - 0.05, (82.6, 0.6), "geral", altura=3.2)

# =====================================================================
# ZONA D (x = 120) — wi-fi recebe a alta, sinal fraco recebe a leve, e a live não para  (bloco 3)
# =====================================================================
t0, t1 = S[3]
caixa("Dpiso", (120, 0, -0.1), (24, 18, 0.2), (0.62, 0.86, 0.55, 1))
caixa("Dfundo", (120, 4.6, 3.5), (24, 0.4, 7.0), (0.58, 0.80, 1.0, 1))
caixa("divisoria", (120, 1.6, 1.8), (0.2, 6.0, 3.6), (0.96, 0.92, 0.84, 1))
# lado esquerdo: sala com roteador wi-fi e TV
caixa("salaPiso", (116.5, 1.6, 0.0), (6.8, 6.0, 0.1), (0.78, 0.60, 0.44, 1))
tvD = caixa("tvD", (116.5, 4.0, 2.1), (3.0, 0.2, 1.8), ESCURO)
telaTV = caixa("telaTV", (0, 0, 0), (2.8, 0.04, 1.6), CIANO, unico="ttv"); filho(tvD, telaTV); telaTV.location = (0, -0.12, 0); brilha(telaTV)
rot = caixa("roteador", (118.6, 3.8, 1.0), (0.8, 0.5, 0.25), BRANCO)
caixa("mesinha", (118.6, 3.8, 0.45), (1.0, 0.7, 0.9), (0.55, 0.36, 0.24, 1))
for dx in (-0.28, 0.28):
    an = cilindro(_id("antR"), (0, 0, 0), 0.04, 0.55, ESCURO, seg=6); filho(rot, an); an.location = (dx, 0.1, 0.38)
espW = espectador((116.0, 1.2, 0.18), CORES[3]); espW.scale = (2.0, 2.0, 2.0)
# lado direito: rua com sinal fraco (antena longe, barrinhas apagadas)
caixa("banco", (123.6, 1.4, 0.45), (2.2, 0.7, 0.18), (0.55, 0.36, 0.24, 1))
arvore((126.6, 3.2, 0), 1.3); arvore((121.6, 3.6, 0), 0.9)
espF = espectador((123.4, 1.2, 0.6), CORES[0]); espF.scale = (2.0, 2.0, 2.0)
celF = celular("celF", (124.9, 1.0, 2.6), esc=0.6); girar(celF["corpo"], -12); brilha(celF["tela"])
barras = []
for k in range(4):
    b = caixa(_id("barra"), (125.9 + k * 0.32, 1.0, 1.9 + k * 0.15), (0.22, 0.1, 0.3 + k * 0.3), CINZA, unico=_id("bar")); barras.append(b)
tint = T(3, "internet"); twf = T(3, "wi-fi"); tsn = T(3, "sinal"); tlv = T(3, "leve"); tpr = T(3, "para")
for b in barras: visivel(b, tsn - 0.3)
cor_key(barras[0].data.materials[0], tsn - 0.3, VERMELHO)
ondas((118.6, 3.4, 1.4), twf - 0.3, t1 + 0.2, cor=AZUL, R=1.2, cada=0.45, rot=(90, 0, 0))
# pacotes grandes (alta) entrando na TV; pacotes pequenos (leve) chegando ao celular da rua
t = twf - 0.2
while t < t1 + 0.2:
    p = pacote(_id("pa"), (116.5, 6.0, 4.6), 0.5, QALTA); visivel(p, t, t + 1.0)
    caminho(p, t, t + 1.0, lambda u: (116.5, 6.0 - 2.0 * u, 4.6 - 2.4 * u), orientar=False); t += 0.5
t = tsn
while t < t1 + 0.2:
    p = pacote(_id("pb"), (128.0, 6.0, 4.6), 0.22, QBAIXA); visivel(p, t, t + 1.0)
    caminho(p, t, t + 1.0, lambda u: (128.0 - 3.1 * u, 6.0 - 5.0 * u, 4.6 - 2.0 * u), orientar=False); t += 0.5
gD = pixel("guiaD", (120.0, -1.6, 0), escala=0.85); respirar(gD, t0, t1 + 0.5)
pensar(gD, t0 + 0.05, 1.5); apontar(gD, twf - 0.2, 1.6, "E", 50); apontar(gD, tsn - 0.2, 1.6, "D", 50); comemorar(gD, tpr - 0.4, 1.2)
plano(t0, (120.0, 0.2), "medio", altura=2.2); plano(tint - 0.1, (120.0, 0.6), "geral", altura=2.6)
plano(twf - 0.3, (117.0, 1.0), "medio", altura=2.2); plano(tsn - 0.3, (124.4, 1.0), "medio", altura=2.2)
plano(tpr - 0.6, (120.6, 0.8), "geral", altura=2.6); plano(t1 - 0.05, (120.6, 0.8), "geral", altura=2.6)

# =====================================================================
# ZONA E (x = 160) — mapa em miniatura: o celular manda UM vídeo; a CDN espalha cópias  (bloco 4)
# =====================================================================
t0, t1 = S[4]
caixa("Efundo", (160, 9, 3), (30, 0.4, 12), (0.55, 0.78, 1.0, 1))
caixa("mapaE", (160, 2.5, -0.1), (30, 20, 0.2), (0.48, 0.80, 0.42, 1))
for (x, y, w, d) in ((156.0, 5.6, 3.2, 2.2), (164.6, -1.0, 2.4, 3.0)):
    caixa(_id("lago"), (x, y, 0.01), (w, d, 0.04), (0.35, 0.65, 0.98, 1))
orig = caixa("origem", (160, 4.0, 1.6), (1.6, 1.4, 3.2), (0.20, 0.30, 0.60, 1), unico="orig")
for j in range(4):
    l = caixa(_id("ledO"), (0, 0, 0), (1.2, 0.04, 0.12), VERDE); filho(orig, l); l.location = (0, -0.72, -1.0 + j * 0.45)
celE = celular("celE", (152.0, 5.4, 1.0), esc=0.8); girar(celE["corpo"], 20); brilha(celE["tela"])
CIDADES = [(156.6, 1.6), (163.4, 2.4), (157.4, -2.4), (162.6, -3.6), (160.2, -0.6)]
tmil = T(4, "mil"); tum = T(4, "manda", 1); tcop = T(4, "Cópias"); tcdn = T(4, "C-D-N"); tsen = T(4, "sente")
# 'mil pessoas' aparecem pelo mapa
for k in range(40):
    a = random.uniform(0, math.tau); r = random.uniform(3.0, 7.0)
    e = espectador((160 + r * 1.3 * math.cos(a), 1.0 + r * 0.75 * math.sin(a), 0.18), random.choice(CORES))
    tp = tmil + 0.03 * k; visivel(e, tp); pop(e, tp)
# um vídeo só: do celular até a origem
pkE = pacote("pacoteE", (152.0, 5.0, 1.2), 0.45)
visivel(pkE, tum - 0.1, tcop + 0.2)
caminho(pkE, tum - 0.05, tum + 0.9, lambda u: bez((152.0, 5.0, 1.2), (156.0, 4.8, 4.0), (160, 4.0, 3.4), suave(u)), orientar=False)
mcel = celE["tela"].data.materials[0]; cor_key(mcel, tum - 0.1, CIANO); cor_key(mcel, tum + 0.1, VERDE); cor_key(mcel, tum + 0.6, CIANO)
torres = []
for i, (cx, cy) in enumerate(CIDADES):
    for k in range(4):
        predio((cx + (k % 2) * 0.9 - 1.1, cy + (k // 2) * 0.9 + 0.2, 0), 0.6, 0.6, 0.6 + ((i + k) % 3) * 0.4, PREDIOS[(i + k) % 6])
    tw, ml = torre(_id("edge"), (cx + 0.8, cy - 0.5)); torres.append((tw, ml, cx + 0.8, cy - 0.5))
    tlig = tcop + 0.2 * i
    visivel(tw, tlig - 0.1); pop(tw, tlig - 0.1)
for i, (tw, ml, tx, ty) in enumerate(torres):
    ta = tcop + 0.18 * i
    for r in range(3):
        p = pacote(_id("cp"), (160, 4.0, 3.4), 0.32); visivel(p, ta + r * 1.3, ta + r * 1.3 + 0.95)
        caminho(p, ta + r * 1.3, ta + r * 1.3 + 0.9, lambda u, tx=tx, ty=ty: bez((160, 4.0, 3.4), ((160 + tx) / 2, (4 + ty) / 2, 5.0), (tx, ty, 1.8), u), orientar=False)
    cor_key(ml, ta + 0.85, CINZA); cor_key(ml, ta + 0.95, CIANO)
    for k in range(4):
        a = k / 4 * math.tau + i
        fl = tubo(_id("fioV"), (tx + 1.0 * math.cos(a), ty + 0.9 * math.sin(a), 0.5), (tx, ty, 1.0), 0.025, CIANO); visivel(fl, tcdn + 0.1 + 0.05 * k)
gE = pixel("guiaE", (152.6, 1.2, 0), escala=0.9); girar(gE["raiz"], 18); respirar(gE, t0, t1 + 0.5)
espanto(gE, tmil - 0.1, 1.4); apontar(gE, tum - 0.2, 1.6, "E", 40); apontar(gE, tcop - 0.2, 1.8, "D", 50); comemorar(gE, tsen - 0.3, 1.4)
cam_key(t0, (160.0, -10.6, 8.4), (160.0, 1.0, 0.6)); cam_key(tum - 0.3, (156.0, -6.4, 5.4), (156.0, 3.4, 1.4))
cam_key(tcop - 0.1, (160.0, -10.8, 8.6), (160.0, 0.6, 0.6)); cam_key(tcdn, (159.4, -10.2, 7.6), (159.8, 0.0, 0.8))
cam_key(tsen - 0.5, (153.6, -4.4, 3.4), (153.0, 2.8, 1.4)); cam_key(t1 - 0.05, (153.6, -4.2, 3.3), (153.0, 2.8, 1.4))

# =====================================================================
# ZONA F (x = 200) — dois caminhos: o vídeo (tubo largo, devagar) e o chat/presentes (tubo fino, rápido)  (bloco 5)
# =====================================================================
t0, t1 = S[5]
sala_fechada("F", 200, (0.30, 0.30, 0.42, 1), (0.98, 0.70, 0.52, 1), prof=4.6)
celF1 = celular("celF1", (196.4, 2.0, 3.8), esc=1.0); brilha(celF1["tela"])
celF2 = celular("celF2", (203.6, 2.0, 3.8), esc=1.0); brilha(celF2["tela"])
tuboV = tubo("tuboVideo", (197.0, 2.0, 3.0), (203.0, 2.0, 3.0), 0.45, (0.70, 0.85, 1.0, 1))
tuboC = tubo("tuboChat", (203.0, 2.0, 4.7), (197.0, 2.0, 4.7), 0.24, (1.0, 0.85, 0.95, 1))
tmsg = T(5, "Mensagens"); tpre = T(5, "presentes"); tcam = T(5, "caminho"); tsep = T(5, "separado"); trap = T(5, "rápido"); tconv = T(5, "conversa")
# vídeo: pacotes devagar, por baixo
t = t0
while t < t1 + 0.3:
    p = pacote(_id("pv"), (197.0, 1.0, 3.0), 0.55); visivel(p, t, t + 2.4)
    caminho(p, t, t + 2.4, lambda u: (197.0 + 6.0 * u, 1.0, 3.0), orientar=False); t += 0.8
# chat e presentes: rápidos, por cima, no sentido contrário (de quem assiste para o streamer)
t = tmsg - 0.2; k = 0
while t < t1 + 0.3:
    if t >= tpre - 0.2 and k % 2: ob = presente(_id("gift"), (203.0, 1.3, 4.7), 0.42)
    else: ob = balao(_id("msgF"), (203.0, 1.3, 4.7), random.uniform(0.6, 0.95))
    visivel(ob, t, t + 0.7)
    caminho(ob, t, t + 0.7, lambda u: (203.0 - 6.0 * u, 1.3, 4.7 + 0.12 * math.sin(u * 9)), orientar=False); t += 0.28; k += 1
destacar(tuboC.data.materials[0], tcam, (1.0, 0.85, 0.95, 1), 1.0)
destacar(tuboV.data.materials[0], tsep, (0.70, 0.85, 1.0, 1), 1.0)
gF = pixel("guiaF", (200.0, -1.4, 0), escala=0.75); respirar(gF, t0, t1 + 0.5)
pensar(gF, t0 + 0.05, 1.2); apontar(gF, tmsg - 0.1, 1.4, "D", 70); comemorar(gF, tpre - 0.1, 1.0)
apontar(gF, tsep - 0.1, 1.4, "E", 10); espanto(gF, trap - 0.2, 1.0); acenar(gF, tconv - 0.1, 1.4)
plano(t0, (200.0, 0.6), "geral", altura=3.0); plano(tmsg - 0.25, (200.0, 0.9), "geral", altura=3.3)
plano(tconv - 0.3, (200.0, 0.8), "geral", altura=3.1); plano(t1 - 0.05, (200.0, 0.8), "geral", altura=3.1)

# =====================================================================
# 6 — convite: de volta ao quarto, a lâmpada 'ao vivo' pisca, o Pixel acena (câmera aberta: CTA não encosta na cabeça)
# =====================================================================
t0 = S[6][0]
acenar(st, t0 + 0.15, 1.6); apontar(st, T(6, "primeira") - 0.3, 1.6, "E", 35); comemorar(st, T(6, "Conta") - 0.1, 1.4)
for tt, sy in ((T(6, "primeira") - 0.1, 1.0), (T(6, "primeira") + 0.05, 0.35), (T(6, "primeira") + 0.3, 1.0)):
    key(CA["botao"], "scale", tt, (1, sy, 1))
cam_key(t0, (-0.6, -6.6, 2.9), (-0.6, 1.0, 2.6)); cam_key(FIM, (-0.5, -6.1, 2.9), (-0.5, 1.0, 2.6))

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
