"""Série 2 — 'Como o matchmaking escolhe o seu time?' (estilo C cartoon, mascote Pixel, visual nível 2).
Mecanismo: perdeu 3 seguidas -> nota escondida (MMR) num cofre -> ideia do xadrez (Elo): sobe ao vencer, cai ao perder
-> resultado-surpresa mexe mais -> TrueSkill: habilidade + dúvida (faixa larga no começo) -> dois times de média
parecida numa gangorra equilibrada (50 %) -> fila longa: a faixa de busca abre e a gangorra desequilibra -> convite.
Visual 100 % original: jogadores-brinquedo genéricos (cápsula + cabeça), nenhum personagem, mapa ou logotipo de jogo.
Base: cena_ps5_ia.py (T() com casamento exato, corte seco de câmera entre zonas).
Uso: blender -b --factory-startup -P cena_matchmaking.py -- <pasta_producao> [preview t1,t2,... | range a,b]"""
import bpy, sys, os, json, math, random, re, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lowpoly import *
from lowpoly import _id
from cartoon import *

args = sys.argv[sys.argv.index("--") + 1:]
PASTA = args[0]
LEG = json.load(open(os.path.join(PASTA, "legendas.json"), encoding="utf-8"))
FIM = LEG[-1]["e"] + 4.6          # cobre também o pedido de like (a cena não congela no fim)
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
random.seed(26)

AMARELO = (1.0, 0.82, 0.12, 1); VERDE = (0.20, 0.85, 0.40, 1); VERMELHO = (0.95, 0.22, 0.20, 1)
ROXO = (0.60, 0.34, 0.95, 1); AZUL = (0.20, 0.55, 1.0, 1); BRANCO = (0.97, 0.97, 0.98, 1)
CIANO = (0.25, 0.95, 1.0, 1); ESCURO = (0.10, 0.11, 0.14, 1); CINZA = (0.40, 0.42, 0.48, 1); OURO = (1.0, 0.72, 0.10, 1)
MADEIRA = (0.62, 0.40, 0.24, 1)
BRILHO = []
def brilha(ob): BRILHO.append(ob.data.materials[0]); return ob
def girarZ(ob, graus): ob.rotation_euler = (0, 0, math.radians(graus))

def jogador(nome, loc, cor, s=1.0):
    """Jogador-brinquedo genérico: corpo em cápsula colorida, cabeça redonda com olhinhos (leve, ~6 objetos)."""
    raiz = vazio(nome, loc); raiz.scale = (s, s, s)
    corpo = capsula(_id("corpoJ"), (0, 0, 0.75), 0.36, 0.7, cor); filho(raiz, corpo); corpo.location = (0, 0, 0.75)
    cab = esfera(_id("cabJ"), (0, 0, 0), 0.34, PELE, sub=3); filho(raiz, cab); cab.location = (0, 0, 1.65); liso(cab)
    for x in (-0.12, 0.12):
        o = esfera(_id("olhoJ"), (0, 0, 0), 0.05, PRETO, sub=2); filho(raiz, o); o.location = (x, -0.31, 1.7)
    bone = esfera(_id("boneJ"), (0, 0, 0), 0.35, cor, sub=3); bone.scale = (1, 1, 0.45); filho(raiz, bone); bone.location = (0, 0.02, 1.86); liso(bone)
    return raiz

def xis(nome, loc, s=0.6, cor=VERMELHO):
    """X vermelho de derrota (duas barras cruzadas), de pé virado para a câmera."""
    a = caixa(nome, loc, (s, 0.12, s * 0.22), cor); a.rotation_euler = (0, math.radians(45), 0)
    b = caixa(_id("xb"), (0, 0, 0), (s, 0.12, s * 0.22), cor); filho(a, b); b.rotation_euler = (0, math.radians(-90), 0)
    return a

def exclama(nome, loc, s=1.0, cor=AMARELO):
    """Ponto de exclamação 3D (surpresa)."""
    e = caixa(nome, loc, (0.22 * s, 0.22 * s, 0.8 * s), cor); liso(e)
    p = esfera(_id("pto"), (0, 0, 0), 0.14 * s, cor, sub=2); filho(e, p); p.location = (0, 0, -0.65 * s)
    return e

def medidor(nome, loc, h0=1.0, cor=VERDE):
    """Coluna de 'nota': base escura + tubo de vidro (anel) + barra que sobe/desce (scale Z). Devolve a barra."""
    x, y = loc
    base = cilindro(nome + "_base", (x, y, 0.15), 0.55, 0.3, ESCURO, seg=20)
    for k in range(5):   # marcas de régua no fundo
        filho(base, caixa(_id("marca"), (0, 0, 0), (0.7, 0.05, 0.05), BRANCO)); base.children[-1].location = (0, 0.42, 0.6 + k * 0.8)
    fundo = caixa(nome + "_fundo", (x, y + 0.42, 2.2), (0.9, 0.06, 4.2), (0.20, 0.22, 0.30, 1))
    b = cilindro(nome, (x, y, 0.3), 0.38, 1.0, cor, seg=16, unico=nome)
    for v in b.data.vertices: v.co.z += 0.5
    b.scale = (1, 1, h0); b.keyframe_insert("scale", frame=1)
    return b
def nivel(b, t, h): b.scale = (1, 1, h); b.keyframe_insert("scale", frame=f(t))

cam, alvo, cam_key, plano = camera_cartoon(24)

# =====================================================================
# ZONA A (x = 0) — quarto gamer: 3 derrotas (X vermelhos), nuvem de chuva sobre o Pixel  (bloco 0 e CTA)
# =====================================================================
t0, t1 = S[0]
QA = quarto_gamer(0)
brilha(QA["tela"])
px = pixel("pixel", (-0.4, 1.0, 0)); respirar(px, 0, FIM)
tpe = T(0, "Perdeu"); ttr = T(0, "três"); tpa = T(0, "partidas"); tse = T(0, "seguidas"); tpi = T(0, "pior")
tca = T(0, "Calma"); tco = T(0, "como"); tti = T(0, "time", 1)
for k, tt in enumerate((ttr, tpa, tse)):
    x = xis(_id("xA"), (-2.2 + k * 1.1, 0.2, 3.3), 0.8); visivel(x, tt - 0.05, tca + 0.2); pop(x, tt - 0.05, 1.0)
nv = nuvem((-0.4, 1.0, 4.3), 0.32); liso(nv);
for o in todos(nv): o.data.materials.clear(); o.data.materials.append(mat((0.45, 0.47, 0.55, 1), unico="nuvemA")) if o.type == "MESH" else None
visivel(nv, tpi - 0.1, tca + 0.1); pop(nv, tpi - 0.1, 1.0)
t = tpi
while t < tca:
    g = esfera(_id("gota"), (0, 0, 0), 0.06, (0.35, 0.65, 1.0, 1), sub=1); visivel(g, t, t + 0.5)
    x0 = random.uniform(-1.1, 0.3)
    caminho(g, t, t + 0.5, lambda u, x0=x0: lerp((x0, 0.9, 3.9), (x0, 0.9, 2.4), u), orientar=False); t += 0.05
espanto(px, tpe - 0.05, 1.2); apontar(px, ttr - 0.1, 1.5, "E", 50); pensar(px, tpi - 0.1, 1.2)
acenar(px, tca - 0.1, 1.0); pensar(px, tco - 0.1, 1.6)
plano(0, (-1.0, 0.6), "medio", altura=2.2); plano(tpi - 0.6, (-1.0, 0.6), "medio", altura=2.2)
plano(tpi - 0.1, (-0.4, 0.8), "medio", altura=2.6); plano(tco - 0.5, (-0.4, 0.8), "medio", altura=2.6)
plano(tco - 0.1, (-0.4, 0.8), "close", altura=2.1)

# =====================================================================
# ZONA B (x = 40) — o cofre da nota escondida (MMR): abre, mostra a estrela da nota e fecha de novo  (bloco 1)
# =====================================================================
t0, t1 = S[1]
sala_fechada("B", 40, (0.55, 0.62, 0.85, 1), (0.36, 0.30, 0.62, 1), prof=4.4)
cofre = caixa("cofre", (40.6, 1.6, 1.4), (2.6, 1.6, 2.8), (0.30, 0.33, 0.40, 1)); liso(cofre)
interior = caixa("interior", (40.6, 1.0, 1.4), (2.2, 0.4, 2.4), (0.08, 0.08, 0.10, 1))
estrela = esfera("notaMMR", (40.6, 0.9, 1.5), 0.55, OURO, sub=3); liso(estrela); brilha(estrela)
dobr = vazio("dobradica", (39.3, 0.78, 1.4))
porta = caixa("porta", (0, 0, 0), (2.6, 0.16, 2.8), (0.42, 0.46, 0.55, 1)); filho(dobr, porta); porta.location = (1.3, 0, 0)
roda = cilindro("roda", (0, 0, 0), 0.42, 0.12, AMARELO, seg=20); filho(dobr, roda); roda.rotation_euler = (math.radians(90), 0, 0); roda.location = (1.3, -0.14, 0)
for k in range(3):
    r = caixa(_id("raio"), (0, 0, 0), (0.75, 0.06, 0.08), ESCURO); filho(roda, r); r.location = (0, 0.07, 0); r.rotation_euler = (0, math.radians(60 * k), 0)
cad = caixa("cadeado", (40.6, 0.55, 3.15), (0.6, 0.2, 0.5), VERMELHO)
alca = anel("alca", (40.6, 0.55, 3.45), 0.22, 0.05, CINZA, seg=16); alca.rotation_euler = (math.radians(90), 0, 0)
tes = T(1, "escondido"); tmm = T(1, "MMR"); tha = T(1, "habilidade"); tle = T(1, "League"); toc = T(1, "oculta"); tri = T(1, "Riot")
for ob in (cad, alca):
    visivel(ob, t0, tmm - 0.1);
key(dobr, "rotation_euler", tmm - 0.1, (0, 0, 0)); key(dobr, "rotation_euler", tmm + 0.5, (0, 0, math.radians(-105)))
key(roda, "rotation_euler", tes, (math.radians(90), 0, 0)); key(roda, "rotation_euler", tmm, (math.radians(90), math.radians(360), 0))
pop(estrela, tmm + 0.2, 1.0)
key(estrela, "location", tha - 0.1, (40.6, 0.9, 1.5)); key(estrela, "location", tha + 0.3, (40.6, 0.5, 1.9)); key(estrela, "location", toc - 0.3, (40.6, 0.5, 1.9))
key(estrela, "location", toc, (40.6, 0.9, 1.5))
key(dobr, "rotation_euler", toc - 0.3, (0, 0, math.radians(-105))); key(dobr, "rotation_euler", toc + 0.2, (0, 0, 0))
hudB = hud("hudB", (40.6, 3.2, 4.2), w=3.0, h=1.0); visivel(hudB, tes - 0.2); pop(hudB, tes - 0.2)
gB = pixel("guiaB", (37.6, -0.9, 0), escala=0.85); girarZ(gB["raiz"], 15); respirar(gB, t0, t1 + 0.5)
pensar(gB, t0 + 0.05, 1.2); apontar(gB, tmm - 0.2, 1.6, "D", 30); comemorar(gB, tha - 0.1, 1.1); apontar(gB, toc - 0.2, 1.6, "D", 20)
plano(t0, (39.6, 0.4), "geral", altura=2.4); plano(tmm - 0.6, (39.6, 0.4), "geral", altura=2.4)
plano(tmm - 0.1, (40.2, 0.4), "medio", altura=2.0); plano(tle - 0.3, (40.2, 0.4), "medio", altura=2.0)
plano(tle + 0.1, (39.6, 0.4), "geral", altura=2.4); plano(t1 - 0.05, (39.8, 0.4), "geral", altura=2.4)

# =====================================================================
# ZONA C (x = 80) — tabuleiro de xadrez + coluna da nota: sobe quando vence, cai quando perde  (bloco 2)
# =====================================================================
t0, t1 = S[2]
sala_fechada("C", 80, (0.62, 0.82, 0.55, 1), (0.98, 0.78, 0.45, 1), prof=4.6)
mesa = caixa("mesaC", (78.6, 1.2, 0.5), (3.4, 2.6, 1.0), MADEIRA)
tab = vazio("tabuleiro", (78.6, 1.2, 1.02))
for i in range(6):
    for j in range(6):
        q = caixa(_id("casa"), (0, 0, 0), (0.48, 0.38, 0.06), BRANCO if (i + j) % 2 == 0 else ESCURO, unico="casaB" if (i + j) % 2 == 0 else "casaP")
        filho(tab, q); q.location = (-1.2 + i * 0.48 + 0.24, -0.95 + j * 0.38 + 0.19, 0)
def peao(nome, loc, cor):
    p = cilindro(nome, loc, 0.16, 0.12, cor, seg=14)
    c = cilindro(_id("pc"), (0, 0, 0), 0.09, 0.3, cor, seg=12, r2=0.06); filho(p, c); c.location = (0, 0, 0.2)
    h = esfera(_id("ph"), (0, 0, 0), 0.11, cor, sub=2); filho(p, h); h.location = (0, 0, 0.42); return p
pb = peao("peaoB", (78.3, 1.0, 1.12), BRANCO); pp = peao("peaoP", (79.0, 1.6, 1.12), (0.18, 0.18, 0.22, 1))
txa = T(2, "xadrez"); tse = T(2, "sessenta"); tel = T(2, "Elo"); tcr = T(2, "criou"); tso = T(2, "sobe"); tve = T(2, "vence")
tcai = T(2, "cai"); tpe = T(2, "perde")
pop(pb, txa - 0.1); pop(pp, txa + 0.1)
key(pb, "location", tso - 0.3, (78.3, 1.0, 1.12)); key(pb, "location", tso + 0.2, (78.78, 1.38, 1.12))
key(pp, "location", tso + 0.1, (79.0, 1.6, 1.12)); key(pp, "location", tso + 0.5, (80.4, 0.4, 1.0))
bC = medidor("notaC", (82.4, 1.6), 1.2, VERDE)
nivel(bC, tcr, 1.2); nivel(bC, tso + 0.1, 3.0); nivel(bC, tcai - 0.2, 3.0); nivel(bC, tcai + 0.4, 1.4)
cor_key(bC.data.materials[0], tcai - 0.2, VERDE); cor_key(bC.data.materials[0], tcai + 0.2, VERMELHO)
sC1 = seta3d("setaC1", 1.4, VERDE); sC1.location = (83.6, 1.0, 2.0); visivel(sC1, tso, tcai - 0.1); pop(sC1, tso)
sC2 = seta3d("setaC2", 1.4, VERMELHO); sC2.location = (83.6, 1.0, 3.6); sC2.rotation_euler = (math.radians(180), 0, 0); visivel(sC2, tcai, t1 + 0.1); pop(sC2, tcai)
gC = pixel("guiaC", (80.6, -1.2, 0), escala=0.85); respirar(gC, t0, t1 + 0.5)
apontar(gC, txa - 0.2, 1.4, "E", 30); pensar(gC, tse - 0.1, 1.4); comemorar(gC, tso - 0.1, 1.2); espanto(gC, tcai - 0.1, 1.2)
plano(t0, (80.0, 0.6), "geral", altura=2.2); plano(tel - 0.6, (80.0, 0.6), "geral", altura=2.2)
plano(tel - 0.1, (80.8, 0.6), "geral", altura=2.6); plano(t1 - 0.05, (81.0, 0.6), "geral", altura=2.6)

# =====================================================================
# ZONA D (x = 120) — o Pixel contra um rival grandão (ganha: nota dispara) e contra um baixinho (perde: despenca)  (bloco 3)
# =====================================================================
t0, t1 = S[3]
sala_fechada("D", 120, (0.95, 0.70, 0.55, 1), (0.40, 0.70, 0.98, 1), prof=4.6)
tga = T(3, "ganha"); tfo = T(3, "forte"); tsob = T(3, "sobe"); tmu = T(3, "muito"); tpe = T(3, "perde"); tfr = T(3, "fraco")
tcai = T(3, "cai"); tmu2 = T(3, "muito", 1); tqu = T(3, "Quem"); tsu = T(3, "surpresa")
pD = pixel("guiaD", (118.4, 0.6, 0), escala=0.9); girarZ(pD["raiz"], 20); respirar(pD, t0, t1 + 0.5)
forte = jogador("forte", (121.0, 1.0, 0), VERMELHO, 1.7); girarZ(forte, -20); visivel(forte, t0, tpe - 0.1); pop(forte, tga - 0.2, 1.0)
fraco = jogador("fraco", (121.0, 0.8, 0), (0.55, 0.85, 0.35, 1), 0.65); girarZ(fraco, -20); visivel(fraco, tpe - 0.1, t1 + 0.1); pop(fraco, tpe - 0.1, 1.0)
key(forte, "rotation_euler", tsob - 0.1, (0, 0, math.radians(-20))); key(forte, "rotation_euler", tsob + 0.3, (math.radians(70), 0, math.radians(-20)))
bD = medidor("notaD", (123.6, 1.6), 1.6, VERDE)
nivel(bD, tsob - 0.1, 1.6); nivel(bD, tmu + 0.3, 4.0); nivel(bD, tcai - 0.1, 4.0); nivel(bD, tmu2 + 0.3, 0.5)
cor_key(bD.data.materials[0], tcai - 0.1, VERDE); cor_key(bD.data.materials[0], tcai + 0.3, VERMELHO)
comemorar(pD, tsob - 0.1, 1.4); espanto(pD, tcai - 0.1, 1.4); pensar(pD, tqu - 0.1, 1.6)
for k, dx in enumerate((-1.2, 0.0, 1.2)):
    e = exclama(_id("excl"), (120.6 + dx, 0.6, 4.3), 1.0); visivel(e, tsu - 0.2 + 0.12 * k); pop(e, tsu - 0.2 + 0.12 * k, 1.0)
plano(t0, (120.6, 0.6), "geral", altura=2.6); plano(tmu - 0.4, (120.6, 0.6), "geral", altura=2.6)
plano(tmu, (121.2, 0.8), "geral", altura=3.0); plano(tpe - 0.5, (121.2, 0.8), "geral", altura=3.0)
plano(tpe - 0.1, (120.4, 0.6), "medio", altura=1.8); plano(tcai - 0.3, (120.4, 0.6), "medio", altura=1.8)
plano(tcai + 0.1, (121.2, 0.8), "geral", altura=2.8); plano(tqu - 0.2, (121.2, 0.8), "geral", altura=2.8)
plano(tsu - 0.4, (121.0, 0.6), "geral", altura=3.2); plano(t1 - 0.05, (121.0, 0.6), "geral", altura=3.2)

# =====================================================================
# ZONA E (x = 160) — 'dois números': marcador da habilidade numa régua + faixa da dúvida (larga no começo)  (bloco 4)
# =====================================================================
t0, t1 = S[4]
sala_fechada("E", 160, (0.78, 0.78, 0.92, 1), (0.22, 0.26, 0.44, 1), prof=4.8)
tpu = T(4, "pulo"); tmi = T(4, "Microsoft"); tdo = T(4, "dois"); thab = T(4, "habilidade"); tdu = T(4, "dúvida")
tpr = T(4, "primeiras"); tgr = T(4, "grande"); tpul = T(4, "pula"); tta = T(4, "tanto")
regua = caixa("regua", (160.0, 1.4, 2.2), (6.0, 0.3, 0.22), BRANCO)
for k in range(11):
    m = caixa(_id("tick"), (0, 0, 0), (0.06, 0.32, 0.5 if k % 5 == 0 else 0.3), ESCURO); filho(regua, m); m.location = (-2.8 + k * 0.56, 0, 0.1)
faixa = caixa("faixaDuvida", (160.0, 1.3, 2.2), (1.0, 0.36, 0.9), (0.98, 0.55, 0.25, 1), unico="faixa")
marc = esfera("marcHab", (160.0, 1.1, 2.2), 0.36, CIANO, sub=3); liso(marc); brilha(marc)
hab = hud("hudHab", (158.5, 3.2, 3.9), w=2.4, h=0.9); dvd = hud("hudDuv", (161.5, 3.2, 3.9), w=2.6, h=0.9, cor=(0.30, 0.14, 0.06, 1))
visivel(hab, tdo - 0.1); pop(hab, tdo - 0.1); visivel(dvd, tdo + 0.2); pop(dvd, tdo + 0.2)
visivel(marc, thab - 0.15); pop(marc, thab - 0.15, 1.0)
visivel(faixa, tdu - 0.15); faixa.scale = (0.3, 1, 1); faixa.keyframe_insert("scale", frame=f(tdu - 0.15))
faixa.scale = (4.6, 1, 1); faixa.keyframe_insert("scale", frame=f(tdu + 0.4))
# primeiras partidas: o marcador pula de um lado para o outro dentro da faixa larga
xs = [160.0, 158.0, 161.9, 158.4, 162.0, 159.0, 161.2]
t = tpr - 0.1; k = 0
while t < tta + 0.5:
    key(marc, "location", t, (xs[k % len(xs)], 1.1, 2.2)); t += 0.55; k += 1
# depois: a dúvida encolhe e o marcador se acalma
faixa.keyframe_insert("scale", frame=f(tta + 0.4)); faixa.scale = (1.4, 1, 1); faixa.keyframe_insert("scale", frame=f(t1 + 0.1))
key(marc, "location", t1 + 0.1, (160.4, 1.1, 2.2))
gE = pixel("guiaE", (158.6, -1.1, 0), escala=0.7); girarZ(gE["raiz"], 12); respirar(gE, t0, t1 + 0.5)
comemorar(gE, tpu - 0.1, 1.2); apontar(gE, tdo - 0.1, 1.4, "D", 60); apontar(gE, tdu - 0.2, 1.5, "D", 20); espanto(gE, tpul - 0.1, 1.3)
plano(t0, (159.6, 0.6), "medio", altura=2.6); plano(tdo - 0.5, (159.6, 0.6), "medio", altura=2.6)
plano(tdo - 0.1, (160.0, 1.0), "medio", altura=3.1); plano(thab - 0.4, (160.0, 1.0), "medio", altura=3.1)
plano(thab - 0.1, (160.0, 0.8), "medio", altura=2.4); plano(t1 - 0.05, (160.0, 0.8), "medio", altura=2.4)

# =====================================================================
# ZONA F (x = 200) — gangorra: 5 azuis x 5 vermelhos chegam um a um; com média parecida ela fica reta  (bloco 5)
# =====================================================================
t0, t1 = S[5]
sala_fechada("F", 200, (0.55, 0.85, 0.80, 1), (0.98, 0.70, 0.80, 1), prof=4.6)
def gangorra(nome, x, y=1.2, larg=8.4):
    apoio = cilindro(nome + "_apoio", (x, y, 0.65), 0.75, 1.3, (0.30, 0.30, 0.38, 1), seg=3)
    apoio.rotation_euler = (math.radians(90), 0, 0)
    piv = vazio(nome, (x, y, 1.35))
    tb = caixa(_id("tabua"), (0, 0, 0), (larg, 1.1, 0.18), MADEIRA); filho(piv, tb)
    return piv
gF = gangorra("gangF", 200.0)
tmo = T(5, "monta"); ttim = T(5, "times"); tme = T(5, "média"); tpar = T(5, "parecida"); tci = T(5, "cinquenta"); tve = T(5, "vencer")
JF = []
for lado, cor in ((-1, AZUL), (1, VERMELHO)):
    for k in range(5):
        j = jogador(_id("jF"), (0, 0, 0), cor, 0.62); filho(gF, j)
        j.location = (lado * (0.9 + k * 0.7), 0, 0.09); girarZ(j, 0)
        tp = tmo - 0.1 + 0.12 * (2 * k + (0 if lado < 0 else 1))
        visivel(j, tp); pop(j, tp, 0.62); JF.append(j)
# chegando um a um, a gangorra balança; em "parecida" ela fica reta
for t, ang in ((t0, 0), (tmo, -8), (tmo + 0.6, 7), (tmo + 1.1, -5), (ttim + 0.3, 4), (tme, -2), (tpar + 0.2, 0)):
    key(gF, "rotation_euler", t, (0, math.radians(ang), 0))
gFg = pixel("guiaF", (200.0, -1.4, 0), escala=0.75); respirar(gFg, t0, t1 + 0.5)
apontar(gFg, tmo - 0.1, 1.4, "E", 40); apontar(gFg, ttim, 1.2, "D", 40); comemorar(gFg, tci - 0.1, 1.4)
hF = hud("hudF", (200.0, 3.4, 4.6), w=3.6, h=1.0); visivel(hF, tci - 0.2); pop(hF, tci - 0.2)
plano(t0, (200.0, 0.6), "geral", altura=2.6); plano(tpar - 0.6, (200.0, 0.6), "geral", altura=2.6)
plano(tpar, (200.0, 0.8), "geral", altura=3.0); plano(t1 - 0.05, (200.0, 0.8), "geral", altura=3.0)

# =====================================================================
# ZONA G (x = 240) — a fila: relógio gira, a faixa de busca abre, e a gangorra desequilibra  (bloco 6)
# =====================================================================
t0, t1 = S[6]
sala_fechada("G", 240, (0.40, 0.38, 0.50, 1), (0.85, 0.45, 0.35, 1), prof=4.6)
tpre = T(6, "preço"); tes = T(6, "espera"); tfi = T(6, "fila"); taf = T(6, "afasta"); tpa = T(6, "partida")
tFi = T(6, "Fila", 1); tlo = T(6, "longa"); tde = T(6, "desequilibrado")
for k in range(6):
    j = jogador(_id("filaG"), (236.0 + k * 0.9, 2.4, 0), [AZUL, VERDE, ROXO, AMARELO][k % 4], 0.6)
    visivel(j, t0); pop(j, t0 + 0.08 * k, 0.6)
rel = cilindro("relogio", (243.6, 3.0, 3.8), 0.9, 0.15, BRANCO, seg=28); rel.rotation_euler = (math.radians(90), 0, 0)
aro = anel("aroRel", (243.6, 2.9, 3.8), 0.92, 0.08, VERMELHO, seg=28); aro.rotation_euler = (math.radians(90), 0, 0)
pont = vazio("ponteiro", (243.6, 2.85, 3.8))
pp = caixa("ponteiroB", (0, 0, 0), (0.08, 0.05, 0.75), ESCURO); filho(pont, pp); pp.location = (0, 0, 0.3)
key(pont, "rotation_euler", tes - 0.2, (0, 0, 0)); key(pont, "rotation_euler", tfi + 1.2, (0, math.radians(720), 0))
key(pont, "rotation_euler", t1, (0, math.radians(1500), 0))
# faixa de busca em volta da nota do Pixel: abre ('se afasta da sua nota')
reguaG = caixa("reguaG", (240.0, 1.2, 1.4), (6.0, 0.3, 0.2), BRANCO)
faixaG = caixa("faixaG", (240.0, 1.1, 1.4), (1.0, 0.34, 0.7), (0.98, 0.55, 0.25, 1), unico="faixaG")
marcG = esfera("marcG", (240.0, 0.95, 1.4), 0.3, CIANO, sub=3); liso(marcG); brilha(marcG)
faixaG.scale = (0.8, 1, 1); faixaG.keyframe_insert("scale", frame=f(taf - 0.2)); faixaG.scale = (5.6, 1, 1); faixaG.keyframe_insert("scale", frame=f(tpa + 0.2))
cor_key(faixaG.data.materials[0], taf - 0.2, (0.98, 0.55, 0.25, 1)); cor_key(faixaG.data.materials[0], tpa + 0.2, VERMELHO)
# gangorra desequilibrada: 5 grandões vermelhos x 5 baixinhos azuis
gG = gangorra("gangG", 240.0, 1.0, 7.6)
for lado, cor, s in ((-1, AZUL, 0.42), (1, VERMELHO, 0.75)):
    for k in range(5):
        j = jogador(_id("jG"), (0, 0, 0), cor, s); filho(gG, j); j.location = (lado * (0.8 + k * 0.62), 0, 0.09)
for ob in [gG, bpy.data.objects["gangG_apoio"]] + [c for c in gG.children]:
    visivel(ob, tFi - 0.2)
visivel(reguaG, t0, tFi - 0.2); visivel(faixaG, t0, tFi - 0.2); visivel(marcG, t0, tFi - 0.2)
key(gG, "rotation_euler", tFi - 0.2, (0, 0, 0)); key(gG, "rotation_euler", tde + 0.3, (0, math.radians(14), 0))
gGg = pixel("guiaG", (243.0, -1.0, 0), escala=0.8); girarZ(gGg["raiz"], -12); respirar(gGg, t0, t1 + 0.5)
pensar(gGg, tpre - 0.1, 1.2); apontar(gGg, tes - 0.1, 1.5, "D", 70); apontar(gGg, taf - 0.2, 1.5, "E", 20); espanto(gGg, tde - 0.1, 1.4)
plano(t0, (240.6, 1.2), "geral", altura=2.8); plano(taf - 0.6, (240.6, 1.2), "geral", altura=2.8)
plano(taf - 0.1, (240.4, 0.6), "geral", altura=2.2); plano(tFi - 0.5, (240.4, 0.6), "geral", altura=2.2)
plano(tFi - 0.15, (240.0, 0.6), "geral", altura=2.6); plano(t1 - 0.05, (240.0, 0.6), "geral", altura=2.6)

# =====================================================================
# 7 — convite: de volta ao quarto, o Pixel acena (câmera aberta para o CTA) e segue animado no pedido de like
# =====================================================================
t0 = S[7][0]
acenar(px, t0 + 0.15, 1.6); apontar(px, T(7, "time", 1) - 0.2, 1.4, "E", 35); comemorar(px, T(7, "fila", 1) - 0.1, 1.4)
acenar(px, LEG[-1]["e"] + 1.2, 1.6); comemorar(px, LEG[-1]["e"] + 3.0, 1.4)
cam_key(t0, (-0.8, -6.6, 2.9), (-0.8, 1.0, 2.6)); cam_key(FIM, (-0.7, -6.0, 2.9), (-0.7, 1.0, 2.6))

# ---------- corte seco entre zonas: sem isso o Bezier da câmera 'atropela' a zona seguinte ----------
for ob in (cam, alvo):
    fcs = [fc for fc in ob.animation_data.action.fcurves if fc.data_path == "location"]
    fx = [fc for fc in fcs if fc.array_index == 0][0]
    cortes = set()
    kps = list(fx.keyframe_points)
    for a, b in zip(kps, kps[1:]):
        if abs(b.co.y - a.co.y) > 12: cortes.add(round(a.co.x))
    for fc in fcs:
        for kp in fc.keyframe_points:
            if round(kp.co.x) in cortes: kp.interpolation = "CONSTANT"
        ks = list(fc.keyframe_points)
        for a, b in zip(ks, ks[1:]):
            if round(a.co.x) in cortes: b.handle_left_type = "VECTOR"; b.handle_right_type = "VECTOR"
        fc.update()

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
