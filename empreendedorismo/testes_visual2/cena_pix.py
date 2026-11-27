"""Teste visual 2.0: render de produto (EEVEE) — maquininha x Pix. Roda: blender -b -P cena_pix.py"""
import bpy, math, os
from mathutils import Vector
A = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
def lin(c): return tuple(((x/255)/12.92) if x/255 <= 0.04045 else (((x/255)+0.055)/1.055)**2.4 for x in c) + (1,)
def mat(nome, cor, rough=0.4, metal=0.0, emis=None, img=None, emis_str=1.0):
    m = bpy.data.materials.new(nome); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(cor); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if img:
        tx = m.node_tree.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(os.path.join(A, img))
        m.node_tree.links.new(tx.outputs["Color"], b.inputs["Base Color"]); m.node_tree.links.new(tx.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emis_str
    return m
def caixa(nome, loc, dim, m, bevel=0.08, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot); o = bpy.context.object; o.name = nome
    o.scale = (dim[0]/2, dim[1]/2, dim[2]/2); bpy.ops.object.transform_apply(scale=True)
    md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 4; o.data.materials.append(m)
    bpy.ops.object.shade_smooth(); return o
def plano_img(nome, loc, dim, m, rot):
    bpy.ops.mesh.primitive_plane_add(location=loc, rotation=rot); o = bpy.context.object; o.name = nome
    o.scale = (dim[0]/2, dim[1]/2, 1); o.data.materials.append(m); return o

# chão infinito escuro com leve reflexo
bpy.ops.mesh.primitive_plane_add(size=60); chao = bpy.context.object; chao.data.materials.append(mat("chao", (16, 20, 26), 0.35))
# MAQUININHA (esquerda), inclinada
grp = []
corpo = caixa("maq", (-1.6, 0, 0.35), (2.0, 3.6, 0.5), mat("maq", (28, 30, 36), 0.45), 0.2)
tela = plano_img("tela", (-1.6, 0.75, 0.61), (1.5, 0.95), mat("tela", (255, 255, 255), img="tex_tela.png", emis_str=1.4), (0, 0, 0))
mt = mat("tecla", (210, 214, 220), 0.5)
for i in range(3):
    for j in range(4):
        caixa(f"t{i}{j}", (-2.05 + i*0.45, -0.25 - j*0.38, 0.62), (0.34, 0.26, 0.08), mt, 0.03)
caixa("ok", (-1.15, -1.40, 0.62), (0.34, 0.26, 0.08), mat("verde", (43, 213, 118), 0.4), 0.03)
for o in list(bpy.data.objects):
    if o.name.startswith(("maq", "tela", "t", "ok")) and o.name != "tela" or o.name == "tela":
        if o is not chao: o.rotation_euler[2] += math.radians(12); o.location.rotate(__import__("mathutils").Euler((0, 0, math.radians(12))))
# CELULAR com Pix (direita)
cel = caixa("cel", (1.7, 0.2, 0.12), (1.65, 3.3, 0.16), mat("cel", (12, 12, 14), 0.25, 0.6), 0.22)
qr = plano_img("qr", (1.7, 0.2, 0.205), (1.45, 3.0), mat("qr", (255, 255, 255), img="tex_pix.png", emis_str=1.2), (0, 0, 0))
for o in (cel, qr): o.rotation_euler[2] = math.radians(-10)
qr.parent = None
# MOEDAS (frente)
mo = mat("moeda", (230, 180, 60), 0.25, 1.0)
for k in range(9):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.42, depth=0.09, location=(0.1 + (k % 3)*0.02, -2.4, 0.05 + k*0.095)); bpy.context.object.data.materials.append(mo); bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.42, depth=0.09, location=(0.95, -2.7, 0.3), rotation=(math.radians(70), 0, math.radians(30))); bpy.context.object.data.materials.append(mo); bpy.ops.object.shade_smooth()
# LUZES de estúdio: chave suave, recorte verde e recorte âmbar
def area(nome, loc, energia, cor, tam):
    l = bpy.data.lights.new(nome, "AREA"); l.energy = energia; l.color = cor; l.size = tam
    o = bpy.data.objects.new(nome, l); s.collection.objects.link(o); o.location = loc
    d = Vector((0, -0.5, 0.3)) - o.location; o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
area("chave", (0, -6, 9), 1400, (1, 0.97, 0.92), 6)
area("verde", (6, 5, 3), 900, (0.3, 1.0, 0.55), 3)
area("ambar", (-6, 5, 3), 900, (1.0, 0.7, 0.25), 3)
s.world = bpy.data.worlds.new("W"); s.world.use_nodes = True; s.world.node_tree.nodes["Background"].inputs[0].default_value = (0.006, 0.008, 0.012, 1)
# câmera vertical, de cima em ângulo
cd = bpy.data.cameras.new("cam"); cd.lens = 42; cam = bpy.data.objects.new("cam", cd); s.collection.objects.link(cam)
cam.location = (0, -7.8, 9.0); cam.rotation_euler = (Vector((0, -0.3, 0.4)) - cam.location).to_track_quat("-Z", "Y").to_euler(); s.camera = cam
cd.dof.use_dof = True; cd.dof.focus_distance = (cam.location - Vector((0, -0.4, 0.4))).length; cd.dof.aperture_fstop = 2.2
s.render.engine = "BLENDER_EEVEE_NEXT"; s.eevee.taa_render_samples = 24
for k, v in (("use_shadows", True), ("use_raytracing", True)):
    try: setattr(s.eevee, k, v)
    except Exception: pass
s.view_settings.view_transform = "AgX"; s.view_settings.look = "AgX - Medium High Contrast"
s.render.resolution_x, s.render.resolution_y = 1080, 1920
s.render.filepath = os.path.join(A, "render_pix.png"); bpy.ops.render.render(write_still=True)
