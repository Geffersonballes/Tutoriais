"""Cena 3D animada — Pix x maquininha. Uso:
  blender -b -P cena.py -- teste 3.0 12.5 ...   (quadros de teste em teste3d_<t>.png)
  blender -b -P cena.py -- render [ini fim]     (quadros em frames/, retoma de onde parou)"""
import bpy, sys, os, json, math, re
A = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(A, "..", "..", "motor"))
import estudio3d as E
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["teste", "3"]
LEG = json.load(open(f"{A}/legendas.json", encoding="utf-8"))
NSEG = max(x["seg"] for x in LEG) + 1
INI = {k: min(x["s"] for x in LEG if x["seg"] == k) for k in range(NSEG)}
FIM_NARR = max(x["e"] for x in LEG)
DUR = FIM_NARR + 1.5
def norm(w): return re.sub(r"[^\wÀ-ÿ]", "", w.lower())
def tw(seg, p, n=0):
    h = [x["s"] for x in LEG if x["seg"] == seg and norm(x["w"]) == p]
    return h[min(n, len(h) - 1)] if h else INI[seg]
# prévia rápida: RES=540x960 (padrão 1080x1920); PREVIA=1 grava em frames_previa/ com passo 2
RES = tuple(int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
PREVIA = os.environ.get("PREVIA") == "1"
T = lambda n: f"{A}/tex/{n}.png"

s = E.limpar(); s.frame_start = 1; s.frame_end = E.fr(DUR)
E.estudio()
MX, CX = -1.9, 1.9
maq, tel_m = E.maquininha("maq", (MX, 0, 0), {k: T("maq_" + k) for k in ("inicio", "pix", "debito", "credito", "12x")}, math.radians(10))
cel, tel_c = E.celular("cel", (CX, 0.3, 0), {"pix": T("cel_pix")}, math.radians(-8))
nota = E.nota("nota", (0, -2.0, 2.2), T("nota"))
cartao = E.cartao("cartao", (MX, 0.5, 3.5), T("cartao"))
cal, pag = E.calendario("cal", (0, 5.0, 0), {"30": T("cal_30"), "hoje": T("cal_hoje")})

# telas da maquininha conforme a fala
E.mostrar_tela(tel_m, [(0, "inicio"), (INI[2], "pix"), (INI[3], "debito"), (INI[4], "credito"), (INI[6], "12x"), (INI[7], "inicio")], DUR + 1)
E.mostrar_tela(pag, [(INI[5] - 0.3, "30"), (tw(5, "hora"), "hoje")], INI[6])
E.visivel(cal, [(INI[5] - 0.3, INI[6])])
for k, p in pag.items(): pass

# nota: gira flutuando na abertura e sai voando para cima
for i, t in enumerate([0, 3, 6, 9]):
    E.key(nota, "rotation_euler", t, math.radians(25) + i * 0.0, 0); E.key(nota, "rotation_euler", t, i * math.radians(80), 2)
E.key(nota, "location", 0, 2.2, 2); E.key(nota, "location", 4.5, 2.5, 2); E.key(nota, "location", INI[1] - 0.6, 2.3, 2); E.key(nota, "location", INI[1] + 0.4, 9, 2)
E.visivel(nota, [(0, INI[1] + 0.5)])

# cartão: desce e encosta na maquininha no débito, volta no crédito, some depois
c0 = (MX + 0.2, 1.3, 3.6); c1 = (MX + 0.05, 0.75, 0.75)
for t, p, rx in ((INI[3] - 0.2, c0, 0.5), (INI[3] + 1.0, c1, 0.15), (INI[3] + 2.6, c0, 0.5), (INI[4] + 0.3, c0, 0.5), (INI[4] + 1.4, c1, 0.15), (INI[4] + 3.0, c0, 0.5)):
    for i in range(3): E.key(cartao, "location", t, p[i], i)
    E.key(cartao, "rotation_euler", t, rx, 0)
E.visivel(cartao, [(INI[3] - 0.2, INI[5])])

# moedas que caem no Pix da maquininha (poucas: custa quase nada)
for k in range(3):
    m = E.moeda(f"mp{k}", (MX + 0.9 + k * 0.05, -2.3, 0.05 + k * 0.1), 0.3)
    E.key(m, "location", INI[2] + 0.8 + k * 0.4, 4.0, 2); E.key(m, "location", INI[2] + 1.3 + k * 0.4, 0.05 + k * 0.1, 2, "BOUNCE")
    E.visivel(m, [(INI[2] + 0.8 + k * 0.4, INI[3])])

# 12 parcelas: grade 3x4, uma moeda por mês, num canto separado do estúdio
GX, GY = 0.0, -9.0
t_lin = tw(6, "sem")
for k in range(12):
    i, j = k % 3, k // 3
    x, y = GX + (i - 1) * 1.15, GY + (1.5 - j) * 1.15; t = t_lin + k * 0.32
    m = E.moeda(f"m12_{k}", (x, y, 0.05), 0.42)
    E.key(m, "location", t, 3.0, 2); E.key(m, "location", t + 0.35, 0.05, 2, "BOUNCE")
    E.visivel(m, [(t, INI[7])])
# câmera: um plano por cena, com movimento lento dentro do plano
cam, alvo = E.camera(40)
def plano(t0, t1, p0, m0, p1, m1):
    E.plano_camera(cam, alvo, t0, p0, m0); E.plano_camera(cam, alvo, t1, p1, m1)
W0 = ((0, -8.6, 9.6), (0, 0.6, 0.6))
plano(0, INI[1] - 0.5, (0.8, -7.0, 7.4), (0, 0.4, 1.0), (-0.4, -8.4, 8.8), (0, 0.6, 0.8))
plano(INI[1], INI[2] - 0.5, (CX + 0.6, -3.8, 4.6), (CX, 0.9, 0.2), (CX - 0.2, -3.2, 4.0), (CX, 0.9, 0.2))
plano(INI[2], INI[3] - 0.5, (MX + 1.6, -3.9, 4.4), (MX + 0.3, 0.2, 0.4), (MX + 0.9, -3.5, 4.0), (MX + 0.2, 0.3, 0.4))
plano(INI[3], INI[5] - 0.5, (MX - 0.6, -4.2, 5.0), (MX, 0.6, 0.6), (MX + 0.6, -4.6, 5.4), (MX, 0.6, 0.6))
plano(INI[5], INI[6] - 0.5, (0.7, -0.4, 2.4), (0, 5.0, 1.0), (-0.3, 0.4, 2.0), (0, 5.0, 1.0))
plano(INI[6], t_lin - 0.3, (MX + 0.4, -4.0, 4.8), (MX, 0.6, 0.6), (MX + 0.1, -3.6, 4.4), (MX, 0.6, 0.6))
plano(t_lin, INI[7] - 0.5, (GX + 0.4, GY - 3.2, 8.6), (GX, GY + 0.3, 0.0), (GX - 0.3, GY - 2.6, 7.6), (GX, GY + 0.3, 0.0))
plano(INI[7], INI[8] - 0.5, (1.5, -10.5, 11.5), (0, 0.6, 0.6), (-1.0, -9.5, 10.5), (0, 0.6, 0.6))
plano(INI[8], DUR, (MX + 2.2, -4.6, 4.2), (MX, 0.3, 0.5), (MX - 0.8, -4.0, 4.6), (MX, 0.3, 0.5))
# cortes secos entre planos: deixa a interpolação da câmera constante nas trocas
for ob in (cam, alvo):
    for fc in ob.animation_data.action.fcurves:
        kps = list(fc.keyframe_points)
        for i, kp in enumerate(kps):
            if i % 2 == 1: kp.interpolation = "CONSTANT"

if ARGS[0] == "teste":
    E.config_render(amostras=int(os.environ.get("AMOSTRAS", "16")), res=RES)
    for t in ARGS[1:]:
        s.frame_set(E.fr(float(t))); s.render.filepath = f"{A}/teste3d_{t}.png"; bpy.ops.render.render(write_still=True)
else:
    E.config_render(amostras=int(os.environ.get("AMOSTRAS", "24")), res=RES)
    if PREVIA: E.renderizar(f"{A}/frames_previa", int(ARGS[1]) if len(ARGS) > 1 else 1, int(ARGS[2]) if len(ARGS) > 2 else s.frame_end, int(ARGS[3]) if len(ARGS) > 3 else 2); sys.exit(0)
    ini = int(ARGS[1]) if len(ARGS) > 1 else 1; fim = int(ARGS[2]) if len(ARGS) > 2 else s.frame_end
    passo = int(ARGS[3]) if len(ARGS) > 3 else 1
    E.renderizar(f"{A}/frames", ini, fim, passo)
