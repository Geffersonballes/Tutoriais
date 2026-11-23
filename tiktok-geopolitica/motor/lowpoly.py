"""Biblioteca low-poly reutilizável para a série (roda dentro do Blender).
Tudo é criado por código: nada de modelos de terceiros, estilo consistente em todo vídeo."""
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion

FPS = 30
C = {  # paleta da série
    "grama": (0.50, 0.82, 0.38, 1), "grama2": (0.40, 0.74, 0.32, 1), "morro": (0.40, 0.68, 0.36, 1),
    "rua": (0.55, 0.57, 0.60, 1), "agua": (0.35, 0.62, 0.90, 1), "arvore": (0.30, 0.66, 0.30, 1),
    "tronco": (0.45, 0.30, 0.18, 1), "nuvem": (0.97, 0.97, 1.0, 1),
    "ameaca": (0.90, 0.18, 0.16, 1), "defesa": (1.0, 0.80, 0.08, 1), "branco": (0.95, 0.95, 0.95, 1),
    "oliva": (0.40, 0.45, 0.25, 1), "cinza": (0.50, 0.52, 0.55, 1), "escuro": (0.12, 0.13, 0.15, 1),
    "pele": (0.93, 0.74, 0.58, 1), "azulmarinho": (0.15, 0.22, 0.40, 1), "tela": (0.05, 0.22, 0.12, 1),
    "verde_ok": (0.20, 0.95, 0.35, 1), "laranja": (1.0, 0.50, 0.10, 1), "ciano": (0.25, 0.90, 1.0, 1),
    "parede": (0.86, 0.86, 0.82, 1), "piso": (0.62, 0.58, 0.52, 1), "madeira": (0.55, 0.38, 0.22, 1),
}
PREDIOS = [(0.96, 0.86, 0.70, 1), (0.84, 0.90, 0.96, 1), (0.96, 0.76, 0.70, 1), (0.82, 0.88, 0.72, 1),
           (0.98, 0.95, 0.86, 1), (0.88, 0.80, 0.92, 1)]

def f(t):  # segundos -> frame
    return int(round(t * FPS)) + 1

_mats = {}
def mat(cor, unico=None):
    key = (tuple(round(c, 3) for c in cor), unico)
    if key in _mats: return _mats[key]
    m = bpy.data.materials.new(f"m{len(_mats)}"); m.diffuse_color = cor
    _mats[key] = m; return m

def _new_obj(nome, bm, cor, unico=None):
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    ob = bpy.data.objects.new(nome, me); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat(cor, unico)); return ob

def caixa(nome, loc, dim, cor, unico=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=Vector(dim), verts=bm.verts)
    ob = _new_obj(nome, bm, cor, unico); ob.location = loc; return ob

def cilindro(nome, loc, r, h, cor, seg=8, r2=None, unico=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    ob = _new_obj(nome, bm, cor, unico); ob.location = loc; return ob

def esfera(nome, loc, r, cor, sub=1, unico=None):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    ob = _new_obj(nome, bm, cor, unico); ob.location = loc; return ob

def anel(nome, loc, R, r, cor, seg=32, unico=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=seg, minor_segments=6, location=loc)
    ob = bpy.context.active_object; ob.name = nome
    for p in ob.data.polygons: p.use_smooth = False
    ob.data.materials.append(mat(cor, unico)); return ob

def vazio(nome, loc=(0, 0, 0)):
    e = bpy.data.objects.new(nome, None); e.location = loc; bpy.context.collection.objects.link(e); return e

def filho(pai, *obs):
    for o in obs:
        o.parent = pai
    return pai

# ---------- animação ----------
def key(ob, path, t, val, interp="BEZIER", idx=-1):
    setattr(ob, path, val) if not isinstance(path, tuple) else None
    ob.keyframe_insert(path, frame=f(t), index=idx)
    ad = ob.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            if fc.data_path == path:
                for kp in fc.keyframe_points:
                    if int(kp.co[0]) == f(t): kp.interpolation = interp

def todos(ob):
    yield ob
    for c in ob.children:
        yield from todos(c)

def visivel(ob, ini, fim=None):
    """Mostra o objeto (e filhos) só entre ini e fim (segundos)."""
    for o in todos(ob):
        o.hide_render = True; o.keyframe_insert("hide_render", frame=1)
        o.hide_render = False; o.keyframe_insert("hide_render", frame=f(ini))
        if fim is not None:
            o.hide_render = True; o.keyframe_insert("hide_render", frame=f(fim))
        o.hide_render = False if fim is None else o.hide_render

def visivel_janelas(ob, janelas):
    for o in todos(ob):
        o.hide_render = True; o.keyframe_insert("hide_render", frame=1)
        for a, b in janelas:
            o.hide_render = False; o.keyframe_insert("hide_render", frame=f(a))
            o.hide_render = True; o.keyframe_insert("hide_render", frame=f(b))

def pop(ob, t, escala=1.0, dur=0.35):
    """Objeto 'nasce' crescendo com leve exagero."""
    s = escala
    ob.scale = (0.001,) * 3; ob.keyframe_insert("scale", frame=max(1, f(t) - 1))
    ob.scale = (s * 1.15,) * 3; ob.keyframe_insert("scale", frame=f(t + dur * 0.7))
    ob.scale = (s,) * 3; ob.keyframe_insert("scale", frame=f(t + dur))

def sumir(ob, t, dur=0.3):
    s = tuple(ob.scale)
    ob.keyframe_insert("scale", frame=f(t))
    ob.scale = (0.001,) * 3; ob.keyframe_insert("scale", frame=f(t + dur))
    ob.scale = s

def caminho(ob, t0, t1, fn, orientar=True, passo=1):
    """Anima o objeto seguindo fn(u) (u de 0 a 1) — chaves densas, frente = +Y local."""
    a, b = f(t0), f(t1); n = max(1, b - a)
    ob.rotation_mode = "QUATERNION"
    prev = None
    for k in range(0, n + 1, passo):
        u = k / n; p = Vector(fn(u))
        ob.location = p; ob.keyframe_insert("location", frame=a + k)
        if orientar:
            q = Vector(fn(min(1, u + 0.01))) - Vector(fn(max(0, u - 0.01)))
            if q.length > 1e-6:
                ob.rotation_quaternion = q.to_track_quat("Y", "Z"); ob.keyframe_insert("rotation_quaternion", frame=a + k)

def cor_key(m, t, cor, interp="BEZIER"):
    m.diffuse_color = cor; m.keyframe_insert("diffuse_color", frame=f(t))

def destacar(m, t, cor_final, dur=1.2):
    """Peça revelada fica amarela e depois volta à cor real (como no vídeo de referência)."""
    cor_key(m, t - 0.05, cor_final); cor_key(m, t, C["defesa"]); cor_key(m, t + dur, C["defesa"]); cor_key(m, t + dur + 0.4, cor_final)

def lerp(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))
def bez(p0, p1, p2, u):
    return tuple((1 - u) ** 2 * a + 2 * (1 - u) * u * b + u ** 2 * c for a, b, c in zip(p0, p1, p2))
def suave(u): return u * u * (3 - 2 * u)

_n = [0]
def _id(p): _n[0] += 1; return f"{p}{_n[0]}"

def explosao(loc, t, r=4.0, n=12):
    random.seed(int(t * 100))
    for i in range(n):
        cor = random.choice([C["laranja"], C["defesa"], C["branco"], C["ameaca"]])
        o = esfera(_id("exp"), loc, random.uniform(0.5, 1.1) * r / 4, cor, sub=0)
        d = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-0.6, 1))).normalized() * r * random.uniform(0.7, 1.3)
        visivel(o, t, t + 0.9)
        o.location = loc; o.keyframe_insert("location", frame=f(t))
        o.location = Vector(loc) + d; o.keyframe_insert("location", frame=f(t + 0.8))
        o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(t))
        o.scale = (0.01,) * 3; o.keyframe_insert("scale", frame=f(t + 0.85))

def rastro(fn, t0, t1, cor=None, r=0.9, cada=0.07, vida=1.3):
    """Fumaça: bolinhas que nascem ao longo do caminho e encolhem."""
    cor = cor or C["branco"]; t = t0
    while t < t1:
        u = (t - t0) / (t1 - t0)
        o = esfera(_id("fum"), fn(u), r, cor, sub=0)
        visivel(o, t, t + vida)
        o.scale = (1,) * 3; o.keyframe_insert("scale", frame=f(t))
        o.scale = (0.01,) * 3; o.keyframe_insert("scale", frame=f(t + vida))
        t += cada

# ---------- modelos ----------
def predio(loc, w, d, h, cor):
    b = caixa(_id("pred"), (loc[0], loc[1], h / 2), (w, d, h), cor)
    t = caixa(_id("teto"), (loc[0], loc[1], h + 0.15), (w * 1.04, d * 1.04, 0.3), tuple(c * 0.8 for c in cor[:3]) + (1,))
    filho(b, t); t.location = (0, 0, h / 2 + 0.15); return b

def arvore(loc, s=1.0):
    tr = cilindro(_id("tronco"), (loc[0], loc[1], 0.6 * s), 0.18 * s, 1.2 * s, C["tronco"], seg=5)
    cp = esfera(_id("copa"), (0, 0, 1.2 * s), 1.0 * s, random.choice([C["arvore"], C["grama2"], (0.38, 0.72, 0.30, 1)]), sub=1)
    filho(tr, cp); return tr

def nuvem(loc, s=1.0):
    base = esfera(_id("nuv"), loc, 2.2 * s, C["nuvem"], sub=1)
    for dx, dz, r in [(2.3, -0.3, 1.6), (-2.2, -0.4, 1.5), (0.8, 1.0, 1.7)]:
        filho(base, esfera(_id("nuv"), (dx * s, 0, dz * s), r * s, C["nuvem"], sub=1))
    base.scale = (1, 0.7, 0.75); return base

def missil(nome, cor=None, escala=1.0, unico=None):
    cor = cor or C["ameaca"]; escala *= 2.4
    corpo = cilindro(nome, (0, 0, 0), 0.28 * escala, 3.0 * escala, cor, seg=8, unico=unico); corpo.rotation_euler = (math.radians(90), 0, 0)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.28 * escala, radius2=0, depth=1.0 * escala)
    bmesh.ops.translate(bm, vec=(0, 0, 2.0 * escala), verts=bm.verts)
    for a in range(4):
        v = bmesh.ops.create_cube(bm, size=1)["verts"]
        bmesh.ops.scale(bm, vec=(0.05, 0.6 * escala, 0.7 * escala), verts=v)
        bmesh.ops.translate(bm, vec=(0.3 * escala, 0, -1.2 * escala), verts=v)
        bmesh.ops.rotate(bm, verts=v, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(a * math.pi / 2, 3, "Z"))
    me = bpy.data.meshes.new(nome + "_p"); bm.to_mesh(me); bm.free()
    p = bpy.data.objects.new(nome + "_p", me); bpy.context.collection.objects.link(p); p.data.materials.append(mat(C["branco"] if cor == C["ameaca"] else C["ameaca"]))
    # corpo deitado ao longo de +Y; ponta e aletas presas a ele
    corpo.data.transform(__import__("mathutils").Matrix.Rotation(math.radians(-90), 4, "X")); corpo.rotation_euler = (0, 0, 0)
    p.data.transform(__import__("mathutils").Matrix.Rotation(math.radians(-90), 4, "X"))
    for poly in p.data.polygons: poly.use_smooth = False
    filho(corpo, p); return corpo

def drone(nome, escala=1.0):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in [(0, 2.0, 0), (-2.2, -1.2, 0), (0, -0.6, 0.35), (2.2, -1.2, 0), (0, -0.6, -0.1)]]
    for fa in [(0, 1, 2), (0, 2, 3), (0, 4, 1), (0, 3, 4), (1, 4, 2), (2, 4, 3)]:
        bm.faces.new([vs[i] for i in fa])
    bmesh.ops.scale(bm, vec=(escala,) * 3, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _new_obj(nome, bm, C["ameaca"])

def aviao(nome, cor=None, radome=True):
    cor = cor or C["cinza"]
    corpo = cilindro(nome, (0, 0, 0), 0.7, 9, cor, seg=8)
    corpo.data.transform(__import__("mathutils").Matrix.Rotation(math.radians(-90), 4, "X"))
    asa = caixa(_id("asa"), (0, 0.3, 0), (11, 2.2, 0.25), cor); filho(corpo, asa); asa.location = (0, 0.3, 0)
    cauda = caixa(_id("cauda"), (0, -4.0, 1.0), (0.25, 1.6, 2.0), cor); filho(corpo, cauda); cauda.location = (0, -4.0, 1.0)
    est = caixa(_id("estab"), (0, -4.0, 0.2), (4, 1.2, 0.2), cor); filho(corpo, est); est.location = (0, -4.0, 0.2)
    nariz = esfera(_id("nariz"), (0, 4.6, 0), 0.7, cor, sub=1); filho(corpo, nariz); nariz.location = (0, 4.6, 0)
    if radome:
        d = cilindro(_id("radome"), (0, 0, 0), 2.2, 0.45, C["branco"], seg=12); filho(corpo, d); d.location = (0, -1.0, 1.7)
        mast = caixa(_id("mast"), (0, 0, 0), (0.3, 0.6, 1.2), cor); filho(corpo, mast); mast.location = (0, -1.0, 1.0)
    return corpo

def radar(nome, loc, cor_base=None):
    cor_base = cor_base or C["cinza"]
    base = cilindro(nome, loc, 1.2, 1.5, cor_base, seg=8, unico=nome)
    mastro = cilindro(_id("mastro"), (0, 0, 1.6), 0.25, 2.0, cor_base, seg=6, unico=nome); filho(base, mastro)
    gir = vazio(nome + "_gir", (0, 0, 2.7)); filho(base, gir)
    prato = caixa(_id("prato"), (0, 0.3, 0.6), (3.6, 0.25, 2.0), C["branco"], unico=nome + "p"); filho(gir, prato)
    prato.rotation_euler = (math.radians(-15), 0, 0)
    return base, gir

def caminhao(nome, loc, cor=None, tubos=True):
    cor = cor or C["oliva"]
    chassi = caixa(nome, loc, (2.4, 7, 0.8), C["escuro"])
    cab = caixa(_id("cab"), (0, 2.6, 1.2), (2.4, 1.8, 1.6), cor); filho(chassi, cab)
    for x in (-1.25, 1.25):
        for y in (-2.3, 0.0, 2.6):
            r = cilindro(_id("roda"), (x, y, -0.4), 0.55, 0.4, C["escuro"], seg=8); r.rotation_euler = (0, math.radians(90), 0); filho(chassi, r)
    lanc = None
    if tubos:
        lanc = vazio(nome + "_lanc", (0, -1.2, 0.6)); filho(chassi, lanc)
        caixa_t = caixa(_id("tubos"), (0, -0.2, 0.9), (2.2, 4.2, 1.6), cor); filho(lanc, caixa_t)
        lanc.rotation_euler = (math.radians(35), 0, 0)
    return chassi, lanc

def canhao(nome, loc):
    base = cilindro(nome, loc, 1.4, 1.0, C["oliva"], seg=8)
    torre = caixa(_id("torre"), (0, 0, 1.0), (1.6, 1.8, 1.0), C["oliva"]); filho(base, torre)
    cano = cilindro(_id("cano"), (0, 1.6, 1.4), 0.15, 3.2, C["escuro"], seg=6); cano.rotation_euler = (math.radians(-60), 0, 0); filho(base, cano)
    return base

def torre_laser(nome, loc):
    base = cilindro(nome, loc, 1.3, 1.2, C["branco"], seg=8)
    cab = esfera(_id("lcab"), (0, 0, 1.5), 1.0, C["cinza"], sub=1); filho(base, cab)
    lente = cilindro(_id("lente"), (0, 0, 2.4), 0.45, 0.6, C["ciano"], seg=8); filho(base, lente)
    return base

def boneco(nome, loc, camisa=None, capacete=True):
    camisa = camisa or C["oliva"]
    pai = vazio(nome, loc)
    for x in (-0.22, 0.22):
        filho(pai, caixa(_id("perna"), (x, 0, 0.45), (0.32, 0.34, 0.9), C["azulmarinho"]))
    filho(pai, caixa(_id("tronco"), (0, 0, 1.25), (0.8, 0.45, 0.8), camisa))
    bd = caixa(_id("bracoD"), (0, 0, 0), (0.22, 0.25, 0.75), camisa)
    piv_d = vazio(nome + "_ombroD", (0.52, 0, 1.6)); filho(pai, piv_d); filho(piv_d, bd); bd.location = (0, 0, -0.35)
    be = caixa(_id("bracoE"), (0, 0, 0), (0.22, 0.25, 0.75), camisa)
    piv_e = vazio(nome + "_ombroE", (-0.52, 0, 1.6)); filho(pai, piv_e); filho(piv_e, be); be.location = (0, 0, -0.35)
    filho(pai, esfera(_id("cabeca"), (0, 0, 2.0), 0.36, C["pele"], sub=2))
    if capacete:
        filho(pai, esfera(_id("capac"), (0, 0, 2.12), 0.38, C["oliva"], sub=1))
        fone = anel(_id("fone"), (0, 0, 2.0), 0.4, 0.06, C["escuro"], seg=12); fone.rotation_euler = (0, math.radians(90), 0); filho(pai, fone)
    return pai, piv_d, piv_e

def configurar_render(res_x=720, res_y=1280):
    s = bpy.context.scene
    s.render.engine = "BLENDER_WORKBENCH"
    s.render.resolution_x, s.render.resolution_y = res_x, res_y
    s.render.fps = FPS
    s.display.render_aa = "8"
    sh = s.display.shading
    sh.light = "STUDIO"; sh.color_type = "MATERIAL"
    sh.show_shadows = True; sh.shadow_intensity = 0.25
    sh.show_cavity = True; sh.cavity_type = "BOTH"; sh.curvature_ridge_factor = 0.6; sh.curvature_valley_factor = 0.8
    sh.show_specular_highlight = False
    s.display.light_direction = (0.45, -0.35, 0.82)
    s.display.shadow_shift = 0.1
    s.render.image_settings.file_format = "JPEG"; s.render.image_settings.quality = 95
    s.view_settings.view_transform = "Standard"; s.view_settings.exposure = 0.45; s.view_settings.look = "None"
    if s.world is None: s.world = bpy.data.worlds.new("W")

def modo_realista(hdri=None, samples=16):
    """EEVEE com luz realista: materiais PBR, céu HDRI, sombras suaves, AgX. Chame depois de montar a cena."""
    s = bpy.context.scene
    s.render.engine = "BLENDER_EEVEE_NEXT"
    s.eevee.taa_render_samples = samples
    try:
        s.eevee.use_shadows = True; s.eevee.use_raytracing = True
        s.eevee.ray_tracing_options.resolution_scale = "2"
    except Exception: pass
    s.view_settings.view_transform = "AgX"; s.view_settings.look = "AgX - Medium High Contrast"; s.view_settings.exposure = 0.3
    for m in bpy.data.materials:
        m.use_nodes = True
        b = m.node_tree.nodes.get("Principled BSDF")
        if b:
            b.inputs["Base Color"].default_value = m.diffuse_color
            b.inputs["Roughness"].default_value = 0.55
            # anima a cor base junto com diffuse_color (destaques amarelos)
            ad = m.animation_data
            if ad and ad.action:
                for fc in ad.action.fcurves:
                    if fc.data_path == "diffuse_color":
                        for kp in fc.keyframe_points:
                            b.inputs["Base Color"].default_value[fc.array_index] = kp.co[1]
                            b.inputs["Base Color"].keyframe_insert("default_value", index=fc.array_index, frame=kp.co[0])
    w = s.world; w.use_nodes = True; nt = w.node_tree
    bg = nt.nodes.get("Background")
    if hdri and bg:
        env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(hdri)
        nt.links.new(env.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 1.0
    sol = bpy.data.lights.new("sol", "SUN"); sol.energy = 3.5; sol.angle = math.radians(3)
    so = bpy.data.objects.new("sol", sol); bpy.context.collection.objects.link(so)
    so.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
