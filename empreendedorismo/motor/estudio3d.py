"""Estúdio 3D da série "Negócio Peça por Peça" (roda DENTRO do Blender 4.2).
Visual aprovado pelo dono em 27/11: fundo grafite, luz de estúdio com recorte âmbar e verde, EEVEE, profundidade de campo.
Objetos genéricos (sem marca): maquininha, celular, cartão, nota, moeda, calendário. Texturas de tela vêm de PNGs feitos com PIL.
Uso: import estudio3d as E; E.limpar(); E.estudio(); m = E.maquininha(...); E.camera(...); E.config_render(...)"""
import bpy, math, os
from mathutils import Vector, Euler

FPS = 30
def fr(t): return int(round(t * FPS)) + 1

def lin(c):
    return tuple(((x / 255) / 12.92) if x / 255 <= 0.04045 else (((x / 255) + 0.055) / 1.055) ** 2.4 for x in c) + (1,)

def limpar():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene; s.render.fps = FPS
    return s

_mats = {}
def mat(nome, cor, rough=0.4, metal=0.0, img=None, emis=0.0, alpha=False):
    if nome in _mats: return _mats[nome]
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(cor); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if img:
        tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(img); tx.extension = "CLIP"
        nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
        if emis:
            nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = emis
        if alpha:
            nt.links.new(tx.outputs["Alpha"], b.inputs["Alpha"]); m.blend_method = "HASHED" if hasattr(m, "blend_method") else None
    _mats[nome] = m; return m

def _ativo(): return bpy.context.object

def caixa(nome, loc, dim, m, bevel=0.06, pai=None):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = _ativo(); o.name = nome
    o.scale = (dim[0] / 2, dim[1] / 2, dim[2] / 2); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 4
    o.data.materials.append(m); bpy.ops.object.shade_smooth()
    if pai: o.parent = pai
    return o

def plano(nome, loc, dim, m, pai=None):
    bpy.ops.mesh.primitive_plane_add(location=loc); o = _ativo(); o.name = nome
    o.scale = (dim[0] / 2, dim[1] / 2, 1); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(m)
    if pai: o.parent = pai
    return o

def vazio(nome, loc=(0, 0, 0)):
    o = bpy.data.objects.new(nome, None); bpy.context.collection.objects.link(o); o.location = loc; return o

# ---------------- cenário ----------------
def estudio(chave=1400, recortes=900):
    s = bpy.context.scene
    bpy.ops.mesh.primitive_plane_add(size=80); chao = _ativo(); chao.name = "chao"
    chao.data.materials.append(mat("chao", (16, 20, 26), 0.35))
    def area(nome, loc, energia, cor, tam, alvo=(0, 0, 0.3)):
        l = bpy.data.lights.new(nome, "AREA"); l.energy = energia; l.color = cor; l.size = tam
        o = bpy.data.objects.new(nome, l); s.collection.objects.link(o); o.location = loc
        o.rotation_euler = (Vector(alvo) - o.location).to_track_quat("-Z", "Y").to_euler(); return o
    area("chave", (0, -6, 9), chave, (1, 0.97, 0.92), 6)
    area("verde", (6, 5, 3), recortes, (0.3, 1.0, 0.55), 3)
    area("ambar", (-6, 5, 3), recortes, (1.0, 0.7, 0.25), 3)
    s.world = bpy.data.worlds.new("W"); s.world.use_nodes = True
    s.world.node_tree.nodes["Background"].inputs[0].default_value = (0.006, 0.008, 0.012, 1)
    return chao

# ---------------- objetos ----------------
def maquininha(nome, loc, telas, rot_z=0.0):
    """telas: {chave: caminho_png}. Devolve (raiz, {chave: plano_da_tela}). Todas as telas ficam no mesmo lugar;
    use mostrar_tela() para trocar."""
    raiz = vazio(nome, loc)
    caixa(nome + "_corpo", (0, 0, 0.25), (2.0, 3.6, 0.5), mat("maq", (28, 30, 36), 0.45), 0.2, raiz)
    pl = {}
    for k, png in telas.items():
        pl[k] = plano(f"{nome}_tela_{k}", (0, 0.75, 0.512), (1.5, 0.95), mat("tela_" + k, (255, 255, 255), img=png, emis=1.4), raiz)
    mt = mat("tecla", (210, 214, 220), 0.5)
    for i in range(3):
        for j in range(4):
            caixa(f"{nome}_t{i}{j}", (-0.45 + i * 0.45, -0.25 - j * 0.38, 0.52), (0.34, 0.26, 0.08), mt, 0.03, raiz)
    caixa(nome + "_ok", (0.45, -1.40, 0.52), (0.34, 0.26, 0.08), mat("ok", (43, 213, 118), 0.4), 0.03, raiz)
    caixa(nome + "_fenda", (0, 1.82, 0.30), (1.3, 0.06, 0.08), mat("preto", (5, 5, 6), 0.6), 0.01, raiz)
    raiz.rotation_euler[2] = rot_z
    return raiz, pl

def celular(nome, loc, telas, rot_z=0.0):
    raiz = vazio(nome, loc)
    caixa(nome + "_corpo", (0, 0, 0.08), (1.65, 3.3, 0.16), mat("cel", (12, 12, 14), 0.25, 0.6), 0.22, raiz)
    pl = {}
    for k, png in telas.items():
        pl[k] = plano(f"{nome}_tela_{k}", (0, 0, 0.165), (1.45, 3.0), mat("cel_" + k, (255, 255, 255), img=png, emis=1.2), raiz)
    raiz.rotation_euler[2] = rot_z
    return raiz, pl

def cartao(nome, loc, png):
    raiz = vazio(nome, loc)
    caixa(nome + "_c", (0, 0, 0), (1.1, 1.75, 0.03), mat("cartao", (40, 70, 140), 0.35, 0.3), 0.04, raiz)
    plano(nome + "_f", (0, 0, 0.017), (1.08, 1.72), mat("cartao_f", (255, 255, 255), img=png, emis=0.3), raiz)
    return raiz

def nota(nome, loc, png):
    raiz = vazio(nome, loc)
    caixa(nome + "_n", (0, 0, 0), (3.1, 1.45, 0.01), mat("nota_b", (230, 235, 230), 0.6), 0.0, raiz)
    plano(nome + "_f", (0, 0, 0.006), (3.1, 1.45), mat("nota_f", (255, 255, 255), img=png, emis=0.15), raiz)
    plano(nome + "_v", (0, 0, -0.006), (3.1, 1.45), mat("nota_f", (255, 255, 255)), raiz).rotation_euler[0] = math.pi
    return raiz

def moeda(nome, loc, r=0.42):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=0.09, location=loc); o = _ativo(); o.name = nome
    o.data.materials.append(mat("moeda", (230, 180, 60), 0.25, 1.0)); bpy.ops.object.shade_smooth()
    md = o.modifiers.new("b", "BEVEL"); md.width = 0.02; md.segments = 2
    return o

def calendario(nome, loc, paginas):
    """paginas: {chave: png}. Bloco com argolas; troque a página com mostrar_tela()."""
    raiz = vazio(nome, loc)
    caixa(nome + "_b", (0, 0, 0.9), (2.0, 0.3, 1.8), mat("cal_b", (245, 245, 240), 0.6), 0.05, raiz)
    caixa(nome + "_topo", (0, 0, 1.9), (2.0, 0.34, 0.35), mat("cal_t", (200, 50, 45), 0.4), 0.05, raiz)
    pl = {}
    for k, png in paginas.items():
        p = plano(f"{nome}_p_{k}", (0, -0.152, 0.85), (1.9, 1.6), mat("cal_" + k, (255, 255, 255), img=png, emis=0.25), raiz)
        p.rotation_euler[0] = math.pi / 2; pl[k] = p
    return raiz, pl

# ---------------- animação ----------------
def key(ob, path, t, val, idx=-1, interp="BEZIER"):
    setattr(ob, path, val) if idx < 0 else getattr(ob, path).__setitem__(idx, val)
    ob.keyframe_insert(path, frame=fr(t), index=idx)
    if ob.animation_data and ob.animation_data.action:
        for fc in ob.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                if int(kp.co[0]) == fr(t): kp.interpolation = interp

def visivel(ob, janelas):
    """janelas: [(t0, t1)] em que o objeto (e filhos) aparece no render."""
    obs = [ob] + list(ob.children_recursive)
    for o in obs:
        o.hide_render = True; o.keyframe_insert("hide_render", frame=1)
        for t0, t1 in janelas:
            o.hide_render = False; o.keyframe_insert("hide_render", frame=fr(t0))
            o.hide_render = True; o.keyframe_insert("hide_render", frame=fr(t1))
        if o.animation_data and o.animation_data.action:
            for fc in o.animation_data.action.fcurves:
                if fc.data_path == "hide_render":
                    for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"

def mostrar_tela(planos, agenda, fim):
    """agenda: [(t, chave)] em ordem; cada tela fica visível do seu t até o próximo."""
    for k, p in planos.items():
        jan = [(t, (agenda[i + 1][0] if i + 1 < len(agenda) else fim)) for i, (t, kk) in enumerate(agenda) if kk == k]
        visivel(p, jan)

def camera(lente=42):
    s = bpy.context.scene
    cd = bpy.data.cameras.new("cam"); cd.lens = lente; cam = bpy.data.objects.new("cam", cd); s.collection.objects.link(cam)
    alvo = vazio("alvo"); tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    cd.dof.use_dof = True; cd.dof.focus_object = alvo; cd.dof.aperture_fstop = 2.4
    s.camera = cam
    return cam, alvo

def plano_camera(cam, alvo, t, pos, mira, ease=True):
    """Keyframe de câmera: posição e ponto de mira no instante t."""
    for i in range(3):
        key(cam, "location", t, pos[i], i); key(alvo, "location", t, mira[i], i)

def config_render(amostras=16, raytracing=False, res=(1080, 1920)):
    s = bpy.context.scene
    try: s.render.engine = "BLENDER_EEVEE_NEXT"  # Blender 4.2 a 4.x
    except TypeError: s.render.engine = "BLENDER_EEVEE"  # Blender 5 (Steam) voltou ao nome antigo
    s.eevee.taa_render_samples = amostras
    for k, v in (("use_shadows", True), ("use_raytracing", raytracing)):
        try: setattr(s.eevee, k, v)
        except Exception: pass
    s.view_settings.view_transform = "AgX"; s.view_settings.look = "AgX - Medium High Contrast"
    s.render.resolution_x, s.render.resolution_y = res
    s.render.image_settings.file_format = "PNG"; s.render.image_settings.color_mode = "RGB"

def renderizar(pasta, ini, fim, passo=1):
    """Renderiza quadro a quadro, pulando os que já existem (retoma se a máquina reiniciar)."""
    s = bpy.context.scene; os.makedirs(pasta, exist_ok=True)
    for f in range(ini, fim + 1, passo):
        out = os.path.join(pasta, f"{f:05d}.png")
        if os.path.exists(out) and os.path.getsize(out) > 1000: continue
        s.frame_set(f); s.render.filepath = out + ".tmp.png"; bpy.ops.render.render(write_still=True)
        os.replace(out + ".tmp.png", out)
