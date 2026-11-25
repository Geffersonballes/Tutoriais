"""Foto de perfil do canal: mascote Pixel acenando, fundo laranja liso (lê bem em círculo pequeno)."""
import bpy, sys, os, math
sys.path.insert(0, "/home/user/Tutoriais/tiktok-geopolitica/motor")
from lowpoly import *
from cartoon import *
bpy.ops.wm.read_factory_settings(use_empty=True); configurar_render()
s = bpy.context.scene; s.frame_start, s.frame_end = 1, 120
caixa("fundo", (0, 4, 3), (40, 0.3, 40), (0.16, 0.42, 0.95, 1))
caixa("piso", (0, 0, -0.1), (40, 40, 0.2), (0.16, 0.42, 0.95, 1))
P = pixel("pixel", (0, 0, 0)); P["raiz"].rotation_euler = (0, 0, math.radians(8))
acenar(P, 0.2, 2.5)
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 50
cam = bpy.data.objects.new("cam", cam_d); s.collection.objects.link(cam); s.camera = cam
cam.location = (0.5, -6.2, 2.5); alvo = vazio("alvo", (0.05, 0, float(os.environ.get("ALVO_Z", "2.15"))))
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
modo_cartoon(samples=32, res=(1080, 1080), ceu=((0.16, 0.42, 0.95), (0.30, 0.60, 1.0)))
s.frame_set(f(float(os.environ.get("T", "0.9")))); s.render.filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "foto_perfil.jpg"); bpy.ops.render.render(write_still=True)
