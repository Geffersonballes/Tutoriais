"""Capa do Facebook (1640x624): Pixel acenando à esquerda (games) e uma maquete low-poly à direita (geopolítica).
O texto entra depois, no Pillow (capa_facebook_texto.py). Uso: blender -b --factory-startup -P capa_facebook.py"""
import bpy, sys, os, math
sys.path.insert(0, "/home/user/Tutoriais/tiktok-geopolitica/motor")
from lowpoly import *
from cartoon import *
bpy.ops.wm.read_factory_settings(use_empty=True); configurar_render()
s = bpy.context.scene; s.frame_start, s.frame_end = 1, 120
AZUL = (0.16, 0.42, 0.95, 1)
caixa("fundo", (0, 6, 3), (60, 0.3, 40), AZUL)
caixa("piso", (0, 0, -0.1), (60, 60, 0.2), AZUL)
# esquerda: Pixel
P = pixel("pixel", (-3.1, 0, 0)); P["raiz"].rotation_euler = (0, 0, math.radians(14))
acenar(P, 0.2, 2.5)
# direita: maquete (construída em escala real e depois encolhida)
antes = set(bpy.data.objects)
cilindro("base", (0, 0, 1.5), 17, 3, (0.30, 0.74, 0.35, 1), seg=24)
cilindro("borda", (0, 0, 0.7), 17.6, 1.4, (0.55, 0.36, 0.20, 1), seg=24)
for (x, y, w, h, c) in [(-8, 4, 3.2, 9, (0.95, 0.80, 0.55, 1)), (-4.2, 6, 3, 13, (0.92, 0.55, 0.40, 1)),
                        (-1, 3.5, 2.8, 7, (0.80, 0.84, 0.90, 1)), (-6, 0, 2.6, 6, (0.98, 0.70, 0.30, 1))]:
    b = predio((x, y), w, w, h, c); b.location.z += 3
for (x, y) in [(3, 7), (5.5, 2), (-10, -3), (1.5, -4), (9, 5)]:
    a = arvore((x, y), 1.4); a.location.z += 3
t, _ = torre_transmissao("torre", (9, -2, 3), h=12)
radar("radar", (4, -6, 3.75))
av = aviao("aviao", cor=(0.90, 0.92, 0.95, 1), radome=False)
av.location = (-3, -2, 21); av.rotation_euler = (math.radians(-8), math.radians(-14), math.radians(-115))
sat = satelite("sat", 1.6); sat.location = (5, 2, 23); sat.rotation_euler = (math.radians(20), 0, math.radians(30))
dio = vazio("dio", (3.2, 0.6, 0)); dio.scale = (0.12, 0.12, 0.12)
for o in set(bpy.data.objects) - antes:
    if o.parent is None and o is not dio: o.parent = dio
dio.rotation_euler = (0, 0, math.radians(-20))
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 50
cam = bpy.data.objects.new("cam", cam_d); s.collection.objects.link(cam); s.camera = cam
cam.location = (0, -15.5, 3.0); alvo = vazio("alvo", (0, 0, 1.45))
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
modo_cartoon(samples=int(os.environ.get("AMOSTRAS", "32")), res=(1640, 624), ceu=((0.16, 0.42, 0.95), (0.30, 0.60, 1.0)))
s.frame_set(f(0.9)); s.render.filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capa_facebook_3d.png")
bpy.ops.render.render(write_still=True)
