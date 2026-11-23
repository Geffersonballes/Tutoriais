import bpy, sys, os, math
sys.path.insert(0, "/home/user/Tutoriais/tiktok-geopolitica/motor")
from lowpoly import *
from cartoon import *
bpy.ops.wm.read_factory_settings(use_empty=True); configurar_render()
s = bpy.context.scene; s.frame_start, s.frame_end = 1, 120
caixa("piso", (0, 0, -0.1), (14, 14, 0.2), (0.80, 0.62, 0.42, 1))
caixa("paredeF", (0, 5, 3), (14, 0.3, 6.2), (0.55, 0.72, 0.95, 1))
caixa("paredeL", (-6, 0, 3), (0.3, 14, 6.2), (0.98, 0.90, 0.70, 1))
caixa("tapete", (0.5, -0.5, 0.02), (5, 4, 0.04), (0.85, 0.25, 0.30, 1))
mesa = caixa("mesa", (1.5, 3.6, 1.5), (4.0, 1.6, 0.15), (0.40, 0.28, 0.20, 1))
for x in (-0.2, 3.2):
    caixa("pe", (x, 3.6, 0.72), (0.15, 1.4, 1.45), (0.25, 0.25, 0.28, 1))
mon = caixa("monitor", (1.5, 4.1, 2.6), (2.6, 0.12, 1.5), (0.08, 0.08, 0.1, 1))
tela = caixa("tela", (1.5, 4.03, 2.6), (2.4, 0.02, 1.32), (0.20, 0.85, 0.95, 1))
caixa("pc", (3.9, 3.8, 1.0), (0.8, 1.4, 2.0), (0.12, 0.12, 0.16, 1))
caixa("ledpc", (3.9, 3.08, 1.0), (0.6, 0.02, 1.6), (0.75, 0.25, 0.95, 1))
cad = capsula("cadeira", (1.5, 2.2, 1.3), 0.5, 0.6, (0.90, 0.20, 0.25, 1))
janela = caixa("janela", (-2.6, 4.84, 3.4), (2.4, 0.05, 1.8), (0.75, 0.90, 1.0, 1))
for k in range(3):
    arvore((-4.5 + k * 1.2, -4.0, 0), 0.8)
P = pixel("pixel", (-0.8, -0.6, 0)); P["raiz"].rotation_euler = (0, 0, math.radians(15))
acenar(P, 0.3, 2.5)
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 32
cam = bpy.data.objects.new("cam", cam_d); s.collection.objects.link(cam); s.camera = cam
cam.location = (2.2, -7.5, 3.4); alvo = vazio("alvo", (0.2, 0.8, 2.0))
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
modo_cartoon(samples=10)
s.frame_set(f(1.2)); s.render.filepath = "/tmp/claude-0/teste_cartoon.jpg"; bpy.ops.render.render(write_still=True)
