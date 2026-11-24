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
    b = caixa(_id("pred"), (loc[0], loc[1], h / 2), (w, d, h), cor, unico="predio%d" % PREDIOS.index(cor) if cor in PREDIOS else None)
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

def _lin(c):
    return tuple((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c[:3]) + (1.0,)

def modo_realista(hdri=None, samples=4, res=(540, 960), foco=None, abertura=0.35):
    """Estilo B no Blender: EEVEE, céu HDRI de pôr do sol, sol quente, materiais PBR, quinas arredondadas
    e desfoque tilt-shift (efeito maquete). Chame depois de montar a cena."""
    s = bpy.context.scene
    s.render.engine = "BLENDER_EEVEE_NEXT"
    s.render.resolution_x, s.render.resolution_y = res
    s.eevee.taa_render_samples = samples
    for k, v in (("use_shadows", True), ("use_raytracing", True), ("shadow_ray_count", 1), ("shadow_step_count", 4)):
        try: setattr(s.eevee, k, v)
        except Exception: pass
    s.view_settings.view_transform = "AgX"; s.view_settings.look = "AgX - Punchy"; s.view_settings.exposure = -0.2
    for m in bpy.data.materials:
        m.use_nodes = True
        b = m.node_tree.nodes.get("Principled BSDF")
        if not b: continue
        b.inputs["Base Color"].default_value = _lin(m.diffuse_color)
        b.inputs["Roughness"].default_value = 0.7
        ad = m.animation_data
        if ad and ad.action:
            for fc in ad.action.fcurves:
                if fc.data_path == "diffuse_color" and fc.array_index < 3:
                    for kp in fc.keyframe_points:
                        v = list(b.inputs["Base Color"].default_value); v[fc.array_index] = _lin((kp.co[1],) * 3)[0]
                        b.inputs["Base Color"].default_value = v
                        b.inputs["Base Color"].keyframe_insert("default_value", frame=kp.co[0])
    # fachadas com janelas (prédios)
    for m in bpy.data.materials:
        if not m.name or not any(k[1] and str(k[1]).startswith("predio") for k, v in _mats.items() if v == m): continue
        nt = m.node_tree; b = nt.nodes.get("Principled BSDF"); parede = b.inputs["Base Color"].default_value[:]
        tc = nt.nodes.new("ShaderNodeTexCoord"); sx = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sx.inputs[0])
        ad = nt.nodes.new("ShaderNodeMath"); ad.operation = "ADD"; nt.links.new(sx.outputs[0], ad.inputs[0]); nt.links.new(sx.outputs[1], ad.inputs[1])
        cb = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(ad.outputs[0], cb.inputs[0]); nt.links.new(sx.outputs[2], cb.inputs[1])
        br = nt.nodes.new("ShaderNodeTexBrick"); nt.links.new(cb.outputs[0], br.inputs["Vector"])
        br.inputs["Scale"].default_value = 1.0; br.inputs["Mortar Size"].default_value = 0.32; br.inputs["Brick Width"].default_value = 0.9; br.inputs["Row Height"].default_value = 0.75
        br.inputs["Color1"].default_value = (0.03, 0.05, 0.08, 1); br.inputs["Color2"].default_value = (0.20, 0.25, 0.32, 1); br.inputs["Mortar"].default_value = parede
        geo = nt.nodes.new("ShaderNodeNewGeometry"); sn = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Normal"], sn.inputs[0])
        ab = nt.nodes.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; nt.links.new(sn.outputs[2], ab.inputs[0])
        gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.5; nt.links.new(ab.outputs[0], gt.inputs[0])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; nt.links.new(gt.outputs[0], mx.inputs["Factor"])
        nt.links.new(br.outputs["Color"], mx.inputs[6]); mx.inputs[7].default_value = parede
        nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    # grama com variação de cor
    gm = _mats.get((tuple(round(c, 3) for c in C["grama"]), None))
    if gm:
        nt = gm.node_tree; b = nt.nodes.get("Principled BSDF"); nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.08
        cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = _lin((0.36, 0.62, 0.22, 1)); cr.color_ramp.elements[1].color = _lin((0.62, 0.78, 0.36, 1))
        nt.links.new(nz.outputs["Fac"], cr.inputs[0]); nt.links.new(cr.outputs[0], b.inputs["Base Color"])
    # quinas arredondadas (maquete) nos objetos de caixa
    for o in bpy.data.objects:
        if o.type == "MESH" and len(o.data.polygons) <= 12 and max(o.dimensions) < 40:
            md = o.modifiers.new("bevel", "BEVEL"); md.width = min(0.12, min(o.dimensions) * 0.12 + 0.001); md.segments = 2
    w = s.world; w.use_nodes = True; nt = w.node_tree
    bg = nt.nodes.get("Background")
    if hdri and bg:
        env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(hdri)
        nt.links.new(env.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 1.1
    sol = bpy.data.lights.new("sol", "SUN"); sol.energy = 4.5; sol.angle = math.radians(2.5); sol.color = (1.0, 0.80, 0.58)
    so = bpy.data.objects.new("sol", sol); bpy.context.collection.objects.link(so)
    so.rotation_euler = (math.radians(62), math.radians(0), math.radians(-140))
    cam = s.camera
    if cam is not None:
        cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = abertura
        if foco is not None: cam.data.dof.focus_object = foco
    return bg, sol

# ---------- modelos navais e de economia (vídeo Ormuz) ----------
def petroleiro(nome, cor_casco=(0.55, 0.12, 0.10, 1), escala=1.0):
    """Superpetroleiro: casco com proa afilada, convés com tubulação, castelo branco na popa e chaminé. Frente = +Y."""
    e = escala
    casco = caixa(nome, (0, 0, 0), (1.6 * e, 9.0 * e, 1.0 * e), cor_casco)
    proa = cilindro(_id("proa"), (0, 0, 0), 0.8 * e, 1.0 * e, cor_casco, seg=3); filho(casco, proa)
    proa.location = (0, 4.9 * e, 0); proa.rotation_euler = (0, 0, math.radians(90)); proa.scale = (1, 1.0, 1)
    conves = caixa(_id("conves"), (0, 0, 0), (1.5 * e, 8.6 * e, 0.12 * e), (0.30, 0.42, 0.30, 1)); filho(casco, conves); conves.location = (0, 0, 0.55 * e)
    tubo = caixa(_id("tubo"), (0, 0, 0), (0.12 * e, 6.5 * e, 0.12 * e), (0.85, 0.75, 0.35, 1)); filho(casco, tubo); tubo.location = (0, 0.6 * e, 0.68 * e)
    for k in range(4):
        tq = cilindro(_id("tampa"), (0, 0, 0), 0.22 * e, 0.1 * e, (0.85, 0.75, 0.35, 1), seg=8); filho(casco, tq); tq.location = (0.45 * e, (-1.5 + k * 1.6) * e, 0.66 * e)
    castelo = caixa(_id("castelo"), (0, 0, 0), (1.4 * e, 1.3 * e, 1.3 * e), C["branco"]); filho(casco, castelo); castelo.location = (0, -3.7 * e, 1.2 * e)
    ponte = caixa(_id("ponte"), (0, 0, 0), (1.7 * e, 0.5 * e, 0.3 * e), C["branco"]); filho(casco, ponte); ponte.location = (0, -3.4 * e, 1.9 * e)
    chamine = caixa(_id("chamine"), (0, 0, 0), (0.45 * e, 0.45 * e, 0.8 * e), C["ameaca"]); filho(casco, chamine); chamine.location = (0, -4.1 * e, 2.1 * e)
    linha = caixa(_id("linhaagua"), (0, 0, 0), (1.62 * e, 9.02 * e, 0.12 * e), (0.10, 0.10, 0.12, 1)); filho(casco, linha); linha.location = (0, 0, -0.35 * e)
    return casco

def navio_guerra(nome, escala=1.0):
    """Fragata cinza com canhão na proa, superestrutura escalonada e mastro de radar. Frente = +Y."""
    e = escala; cinza = (0.55, 0.58, 0.62, 1)
    casco = caixa(nome, (0, 0, 0), (1.2 * e, 7.0 * e, 0.8 * e), cinza)
    proa = cilindro(_id("proaG"), (0, 0, 0), 0.6 * e, 0.8 * e, cinza, seg=3); filho(casco, proa); proa.location = (0, 3.8 * e, 0); proa.rotation_euler = (0, 0, math.radians(90))
    s1 = caixa(_id("sup1"), (0, 0, 0), (1.0 * e, 2.6 * e, 0.8 * e), (0.65, 0.68, 0.72, 1)); filho(casco, s1); s1.location = (0, -0.5 * e, 0.8 * e)
    s2 = caixa(_id("sup2"), (0, 0, 0), (0.8 * e, 1.4 * e, 0.6 * e), (0.70, 0.72, 0.76, 1)); filho(casco, s2); s2.location = (0, 0.0, 1.5 * e)
    mastro = cilindro(_id("mastroG"), (0, 0, 0), 0.08 * e, 1.6 * e, C["escuro"], seg=5); filho(casco, mastro); mastro.location = (0, 0.1 * e, 2.4 * e)
    radar_g = caixa(_id("radarG"), (0, 0, 0), (0.9 * e, 0.12 * e, 0.3 * e), C["branco"]); filho(casco, radar_g); radar_g.location = (0, 0.1 * e, 3.1 * e)
    torre = cilindro(_id("torreG"), (0, 0, 0), 0.35 * e, 0.35 * e, cinza, seg=8); filho(casco, torre); torre.location = (0, 2.4 * e, 0.6 * e)
    cano = cilindro(_id("canoG"), (0, 0, 0), 0.07 * e, 1.2 * e, C["escuro"], seg=5); filho(casco, cano); cano.location = (0, 3.0 * e, 0.75 * e); cano.rotation_euler = (math.radians(-80), 0, 0)
    heli = caixa(_id("heli"), (0, 0, 0), (1.1 * e, 1.4 * e, 0.06 * e), (0.35, 0.37, 0.40, 1)); filho(casco, heli); heli.location = (0, -2.9 * e, 0.45 * e)
    return casco

def barco_rapido(nome, escala=1.0):
    e = escala; b = caixa(nome, (0, 0, 0), (0.6 * e, 2.0 * e, 0.35 * e), (0.30, 0.32, 0.30, 1))
    p = cilindro(_id("proaR"), (0, 0, 0), 0.3 * e, 0.35 * e, (0.30, 0.32, 0.30, 1), seg=3); filho(b, p); p.location = (0, 1.15 * e, 0); p.rotation_euler = (0, 0, math.radians(90))
    cab = caixa(_id("cabR"), (0, 0, 0), (0.45 * e, 0.5 * e, 0.35 * e), C["branco"]); filho(b, cab); cab.location = (0, -0.2 * e, 0.35 * e)
    return b

def mina(nome, escala=1.0):
    m = esfera(nome, (0, 0, 0), 0.6 * escala, (0.15, 0.16, 0.17, 1), sub=1)
    for k in range(8):
        a = k * math.pi / 4
        for z in (0.25, -0.25):
            sp = cilindro(_id("espinho"), (0, 0, 0), 0.06 * escala, 0.5 * escala, (0.25, 0.25, 0.25, 1), seg=4); filho(m, sp)
            sp.location = (math.cos(a) * 0.62 * escala, math.sin(a) * 0.62 * escala, z * escala); sp.rotation_euler = (math.radians(90), 0, a + math.pi / 2)
    return m

def barril(nome, escala=1.0, cor=(0.12, 0.30, 0.55, 1)):
    b = cilindro(nome, (0, 0, 0), 1.0 * escala, 2.6 * escala, cor, seg=16)
    for z in (-0.8, 0.0, 0.8):
        filho(b, anel(_id("aro"), (0, 0, z * escala), 1.02 * escala, 0.06 * escala, (0.08, 0.18, 0.35, 1), seg=24))
    tampa = cilindro(_id("tampaB"), (0, 0, 0), 0.2 * escala, 0.1 * escala, (0.8, 0.8, 0.8, 1), seg=8); filho(b, tampa); tampa.location = (0.5 * escala, 0, 1.32 * escala)
    return b

def seta3d(nome, comprimento=4.0, cor=None):
    """Seta para cima (+Z), base na origem."""
    cor = cor or C["ameaca"]
    haste = cilindro(nome, (0, 0, comprimento * 0.35), 0.35, comprimento * 0.7, cor, seg=8)
    ponta = cilindro(_id("pontaS"), (0, 0, comprimento * 0.35 + comprimento * 0.15), 0.8, comprimento * 0.3, cor, seg=8, r2=0.0); filho(haste, ponta)
    ponta.location = (0, 0, comprimento * 0.5)
    return haste

def bomba_combustivel(nome):
    corpo = caixa(nome, (0, 0, 1.5), (1.4, 0.9, 3.0), C["ameaca"])
    visor = caixa(_id("visor"), (0, 0, 0), (1.0, 0.05, 0.7), (0.1, 0.1, 0.1, 1)); filho(corpo, visor); visor.location = (0, -0.47, 0.7)
    topo = caixa(_id("topoB"), (0, 0, 0), (1.6, 1.0, 0.3), C["branco"]); filho(corpo, topo); topo.location = (0, 0, 1.6)
    mang = cilindro(_id("mang"), (0, 0, 0), 0.08, 1.6, C["escuro"], seg=6); filho(corpo, mang); mang.location = (0.8, 0, 0.0)
    return corpo
