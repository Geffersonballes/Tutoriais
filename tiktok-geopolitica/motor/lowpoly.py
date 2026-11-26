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

def drone(nome, escala=1.0, cor=None):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in [(0, 2.0, 0), (-2.2, -1.2, 0), (0, -0.6, 0.35), (2.2, -1.2, 0), (0, -0.6, -0.1)]]
    for fa in [(0, 1, 2), (0, 2, 3), (0, 4, 1), (0, 3, 4), (1, 4, 2), (2, 4, 3)]:
        bm.faces.new([vs[i] for i in fa])
    bmesh.ops.scale(bm, vec=(escala,) * 3, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _new_obj(nome, bm, cor or C["ameaca"])

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
                        b.inputs["Base Color"].keyframe_insert("default_value", frame=kp.co[0], index=fc.array_index)   # só o canal desta curva (antes gravava os 3 e misturava as cores)
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

# ---------- modelos de energia (vídeo rede elétrica, 25/11) ----------
from mathutils import Matrix as _Mx

def _viga(bm, a, b, r, seg=4):
    """Barra reta entre dois pontos dentro de um bmesh (para treliças num único objeto)."""
    va, vb = Vector(a), Vector(b); dv = vb - va
    vs = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=dv.length)["verts"]
    bmesh.ops.transform(bm, matrix=_Mx.Translation((va + vb) / 2) @ dv.to_track_quat("Z", "Y").to_matrix().to_4x4(), verts=vs)

def cabo(nome, a, b, r=0.08, cor=None, unico=None):
    """Cabo/viga reta entre dois pontos (objeto próprio, dá para animar a cor)."""
    bm = bmesh.new(); _viga(bm, a, b, r, seg=5)
    return _new_obj(nome, bm, cor or C["escuro"], unico)

def torre_transmissao(nome, loc, h=16.0, cor=(0.74, 0.76, 0.78, 1)):
    """Torre treliçada de alta tensão (linha ao longo de X, braços ao longo de Y). Devolve (torre, pontos de fixação dos cabos)."""
    bm = bmesh.new(); base = h * 0.13; topo = h * 0.045
    niveis = [0.0, 0.22, 0.44, 0.62, 0.76, 0.92]
    def larg(u): return base + (topo - base) * min(1.0, u / 0.76)
    aneis = [[(sx * larg(u), sy * larg(u), u * h) for sx, sy in ((1, 1), (1, -1), (-1, -1), (-1, 1))] for u in niveis]
    for k in range(len(aneis) - 1):
        for i in range(4):
            _viga(bm, aneis[k][i], aneis[k + 1][i], 0.13)
            _viga(bm, aneis[k + 1][i], aneis[k + 1][(i + 1) % 4], 0.08)
            _viga(bm, aneis[k][i], aneis[k + 1][(i + 1) % 4], 0.06)
            _viga(bm, aneis[k][(i + 1) % 4], aneis[k + 1][i], 0.06)
    _viga(bm, (0, 0, 0.92 * h), (0, 0, h), 0.10)
    bracos = ((0.70, h * 0.24), (0.88, h * 0.17))
    for u, w in bracos:
        for s in (-1, 1):
            _viga(bm, (0, 0, u * h - 0.25), (0, s * w, u * h), 0.11); _viga(bm, (0, 0, u * h + h * 0.07), (0, s * w, u * h), 0.07)
    for sx, sy in ((1, 1), (1, -1), (-1, -1), (-1, 1)):   # sapatas de concreto
        v = bmesh.ops.create_cube(bm, size=1)["verts"]; bmesh.ops.scale(bm, vec=(0.8, 0.8, 0.5), verts=v); bmesh.ops.translate(bm, vec=(sx * base, sy * base, 0.1), verts=v)
    t = _new_obj(nome, bm, cor); t.location = loc
    bm2 = bmesh.new(); pts = []
    for u, w in bracos:
        for s in (-1, 1):
            for k in range(4):   # cadeia de isoladores (discos)
                vs = bmesh.ops.create_cone(bm2, cap_ends=True, segments=8, radius1=0.24, radius2=0.12, depth=0.2)["verts"]
                bmesh.ops.translate(bm2, vec=(0, s * w, u * h - 0.15 - 0.24 * k), verts=vs)
            pts.append((loc[0], loc[1] + s * w, loc[2] + u * h - 1.1))
    iso = _new_obj(nome + "_iso", bm2, (0.45, 0.70, 0.66, 1)); filho(t, iso)
    return t, pts

def transformador(nome, escala=1.0, cor=(0.47, 0.56, 0.55, 1)):
    """Transformador de potência: tanque, radiadores, conservador de óleo e buchas de porcelana.
    Devolve (pai, tanque, topos das 3 buchas de alta em coordenadas locais). Lado comprido ao longo de X."""
    e = escala; pai = vazio(nome)
    base = caixa(nome + "_base", (0, 0, 0.2 * e), (5.0 * e, 3.4 * e, 0.4 * e), (0.70, 0.70, 0.68, 1))
    tanque = caixa(nome + "_tanque", (0, 0, 1.9 * e), (4.2 * e, 2.4 * e, 3.0 * e), cor, unico=nome)
    tampa = caixa(nome + "_tampa", (0, 0, 3.47 * e), (4.4 * e, 2.6 * e, 0.14 * e), tuple(c * 0.8 for c in cor[:3]) + (1,))
    bm = bmesh.new()
    for s in (-1, 1):
        for k in range(9):
            v = bmesh.ops.create_cube(bm, size=1)["verts"]; bmesh.ops.scale(bm, vec=(0.10 * e, 0.75 * e, 2.3 * e), verts=v)
            bmesh.ops.translate(bm, vec=((-1.8 + k * 0.45) * e, s * 1.62 * e, 1.85 * e), verts=v)
        v = bmesh.ops.create_cube(bm, size=1)["verts"]; bmesh.ops.scale(bm, vec=(3.9 * e, 0.12 * e, 0.12 * e), verts=v); bmesh.ops.translate(bm, vec=(0, s * 1.3 * e, 3.05 * e), verts=v)
    rad = _new_obj(nome + "_rad", bm, (0.66, 0.70, 0.70, 1))
    cons = cilindro(nome + "_cons", (0, 0, 0), 0.42 * e, 3.0 * e, (0.60, 0.66, 0.65, 1), seg=12)
    cons.rotation_euler = (0, math.radians(90), 0); cons.location = (0.3 * e, 0.75 * e, 4.35 * e)
    sup = caixa(nome + "_sup", (0.3 * e, 0.75 * e, 3.75 * e), (2.2 * e, 0.15 * e, 0.6 * e), (0.35, 0.38, 0.38, 1))
    bm = bmesh.new(); topos = []
    for x in (-1.35, 0.0, 1.35):       # buchas de alta tensão (com saias)
        vs = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.24 * e, radius2=0.10 * e, depth=1.9 * e)["verts"]
        bmesh.ops.translate(bm, vec=(x * e, -0.55 * e, 4.45 * e), verts=vs)
        for k in range(5):
            vs = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=(0.42 - 0.04 * k) * e, radius2=(0.24 - 0.02 * k) * e, depth=0.14 * e)["verts"]
            bmesh.ops.translate(bm, vec=(x * e, -0.55 * e, (3.75 + 0.3 * k) * e), verts=vs)
        topos.append((x * e, -0.55 * e, 5.45 * e))
    for x in (-1.0, 0.0, 1.0):          # buchas de baixa
        vs = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.18 * e, radius2=0.09 * e, depth=0.8 * e)["verts"]
        bmesh.ops.translate(bm, vec=(x * e - 0.9 * e, 0.0, 3.9 * e), verts=vs)
    buchas = _new_obj(nome + "_buchas", bm, (0.50, 0.24, 0.15, 1))
    bm = bmesh.new()
    for x, y, z in topos:
        vs = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.07 * e, radius2=0.07 * e, depth=0.3 * e)["verts"]; bmesh.ops.translate(bm, vec=(x, y, z + 0.1 * e), verts=vs)
    pontas = _new_obj(nome + "_pontas", bm, (0.80, 0.80, 0.82, 1))
    painel = caixa(nome + "_painel", (-2.16 * e, 0, 1.5 * e), (0.15 * e, 0.9 * e, 1.2 * e), (0.80, 0.80, 0.78, 1))
    filho(pai, base, tanque, tampa, rad, cons, sup, buchas, pontas, painel)
    return pai, tanque, topos

def sacos_areia(nome, comprimento=6.0, fiadas=3, cor=(0.76, 0.66, 0.46, 1)):
    """Parede de sacos de areia empilhados em amarração (ao longo de X, base em z = 0)."""
    bm = bmesh.new(); n = max(2, int(comprimento / 0.95))
    for r in range(fiadas):
        for k in range(n - (r % 2)):
            vs = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.5)["verts"]
            bmesh.ops.scale(bm, vec=(1.0, 0.62, 0.36), verts=vs)
            bmesh.ops.translate(bm, vec=(-comprimento / 2 + 0.5 + k * 0.95 + (0.47 if r % 2 else 0), random.uniform(-0.04, 0.04), 0.18 + r * 0.30), verts=vs)
    o = _new_obj(nome, bm, cor)
    for p in o.data.polygons: p.use_smooth = True
    return o

def gerador(nome, cor=(0.95, 0.70, 0.10, 1)):
    """Gerador a diesel de emergência (carenagem amarela, grade, escapamento e painel)."""
    pai = vazio(nome)
    filho(pai, caixa(nome + "_skid", (0, 0, 0.15), (3.3, 1.6, 0.3), C["escuro"]),
          caixa(nome + "_corpo", (0, 0, 1.1), (3.0, 1.4, 1.6), cor),
          caixa(nome + "_grade", (1.52, 0, 1.1), (0.06, 1.1, 1.1), C["escuro"]),
          caixa(nome + "_painel", (-0.8, -0.72, 1.3), (0.7, 0.06, 0.6), C["escuro"]),
          caixa(nome + "_faixa", (0.4, -0.72, 0.6), (1.4, 0.05, 0.18), C["escuro"]),
          cilindro(nome + "_escape", (-1.0, 0.3, 2.3), 0.10, 0.9, C["cinza"], seg=8),
          caixa(nome + "_tanque", (0, 0, 0.42), (2.6, 1.2, 0.25), (0.30, 0.32, 0.34, 1)))
    return pai

def usina(nome):
    """Usina termelétrica: galpão das turbinas, casa de caldeiras, 2 chaminés listradas e torre de resfriamento.
    Devolve (pai, [topos locais de onde sai vapor/fumaça])."""
    pai = vazio(nome); par = (0.82, 0.82, 0.80, 1); conc = (0.86, 0.85, 0.82, 1)
    pecas = [caixa(nome + "_hall", (0, 0, 5), (26, 14, 10), par),
             caixa(nome + "_teto", (0, 0, 10.3), (27, 15, 0.6), (0.42, 0.46, 0.52, 1)),
             caixa(nome + "_vidro", (0, -7.06, 7.2), (22, 0.2, 1.6), (0.20, 0.42, 0.62, 1)),
             caixa(nome + "_vidro2", (0, -7.06, 3.4), (22, 0.2, 1.2), (0.20, 0.42, 0.62, 1)),
             caixa(nome + "_turb", (19, 0, 3.2), (12, 10, 6.4), (0.76, 0.80, 0.84, 1)),
             caixa(nome + "_turbteto", (19, 0, 6.55), (12.6, 10.6, 0.4), (0.42, 0.46, 0.52, 1)),
             caixa(nome + "_porta", (19, -5.04, 1.6), (4, 0.15, 3.2), (0.30, 0.34, 0.40, 1))]
    topos = []
    for k, x in enumerate((-7.0, 3.0)):
        pecas.append(cilindro(nome + f"_cham{k}", (x, 10.5, 14), 1.6, 28, conc, seg=14, r2=1.05))
        for z, r in ((26.3, 1.12), (22.5, 1.26), (18.7, 1.40)):
            pecas.append(cilindro(nome + f"_lista{k}", (x, 10.5, z), r + 0.05, 1.5, C["ameaca"], seg=14, r2=r))
        topos.append((x, 10.5, 28.5))
    pecas.append(cilindro(nome + "_resf1", (-24, 2, 6.5), 8.0, 13, conc, seg=20, r2=5.2))
    pecas.append(cilindro(nome + "_resf2", (-24, 2, 15.5), 5.2, 5, conc, seg=20, r2=6.2))
    topos.append((-24, 2, 18.5))
    for k in range(3):
        pecas.append(cilindro(nome + f"_duto{k}", (-10 + k * 7, -8.2, 1.0), 0.5, 2.0, (0.75, 0.55, 0.20, 1), seg=8))
    filho(pai, *pecas)
    return pai, topos

# ---------- modelos nucleares (vídeo inspetores nucleares, 25/11) ----------
def centrifuga(nome, loc, h=6.0, r=0.5, cor=(0.90, 0.91, 0.93, 1), unico=None):
    """Centrífuga a gás: tubo alto com base, tampa, faixa escura e listra vertical (a listra mostra o giro)."""
    base = cilindro(nome, (loc[0], loc[1], 0.25), r * 1.5, 0.5, (0.35, 0.37, 0.40, 1), seg=10)
    tubo = cilindro(_id("ctubo"), (0, 0, h / 2 + 0.25), r, h, cor, seg=14, unico=unico); filho(base, tubo)
    tampa = cilindro(_id("ctampa"), (0, 0, h + 0.55), r * 1.08, 0.35, (0.55, 0.58, 0.62, 1), seg=14); filho(base, tampa)
    faixa = cilindro(_id("cfaixa"), (0, 0, h * 0.72), r * 1.03, 0.3, (0.18, 0.40, 0.70, 1), seg=14); filho(tubo, faixa); faixa.location = (0, 0, h * 0.22)
    listra = caixa(_id("clistra"), (0, 0, 0), (0.12, 0.08, h * 0.8), (0.20, 0.22, 0.25, 1)); filho(tubo, listra); listra.location = (r * 0.98, 0, 0)
    return base, tubo

def girar(ob, t0, rps=1.5):
    """Giro contínuo em Z (2 chaves + extrapolação linear)."""
    ob.rotation_euler = (0, 0, 0); ob.keyframe_insert("rotation_euler", frame=f(t0), index=2)
    ob.rotation_euler = (0, 0, 2 * math.pi * rps); ob.keyframe_insert("rotation_euler", frame=f(t0 + 1.0), index=2)
    for fc in ob.animation_data.action.fcurves:
        if fc.data_path == "rotation_euler":
            for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
            fc.extrapolation = "LINEAR"

def cilindro_uf6(nome, loc, cor=(0.86, 0.80, 0.30, 1)):
    """Cilindro de transporte de UF6 (deitado, com aros e pés)."""
    corpo = cilindro(nome, loc, 0.75, 3.2, cor, seg=14); corpo.rotation_euler = (0, math.radians(90), 0)
    for dz in (-1.2, 1.2):
        a = cilindro(_id("aro"), (0, 0, dz), 0.8, 0.18, (0.45, 0.42, 0.25, 1), seg=14); filho(corpo, a); a.location = (0, 0, dz)
    return corpo

def reator(nome, cor=(0.90, 0.89, 0.86, 1)):
    """Usina nuclear: prédio do reator (cilindro + cúpula), prédio das turbinas e 2 torres de resfriamento.
    Devolve (pai, [topos das torres])."""
    pai = vazio(nome); conc = (0.84, 0.83, 0.80, 1)
    pecas = [cilindro(nome + "_cont", (0, 0, 7), 7, 14, cor, seg=24)]
    cup = esfera(nome + "_cup", (0, 0, 14), 7, cor, sub=3); cup.scale = (1, 1, 0.75); pecas.append(cup)
    for z in (4.0, 9.0): pecas.append(cilindro(nome + "_aro", (0, 0, z), 7.08, 0.35, (0.62, 0.64, 0.66, 1), seg=24))
    pecas += [caixa(nome + "_turb", (16, 0, 4.5), (16, 10, 9), (0.80, 0.84, 0.88, 1)),
              caixa(nome + "_tteto", (16, 0, 9.2), (16.6, 10.6, 0.4), (0.42, 0.46, 0.52, 1)),
              caixa(nome + "_tvidro", (16, -5.06, 6.5), (13, 0.15, 1.4), (0.20, 0.42, 0.62, 1))]
    topos = []
    for k, (x, y) in enumerate(((-6, 28), (16, 30))):
        pecas.append(cilindro(nome + f"_resfA{k}", (x, y, 8), 11, 16, conc, seg=24, r2=7.2))
        pecas.append(cilindro(nome + f"_resfB{k}", (x, y, 19), 7.2, 6, conc, seg=24, r2=8.2))
        topos.append((x, y, 22.5))
    filho(pai, *pecas)
    return pai, topos

def satelite(nome, escala=1.0):
    """Satélite de observação: corpo dourado, 2 painéis solares e lente apontada para baixo (-Z)."""
    s = escala
    corpo = caixa(nome, (0, 0, 0), (1.6 * s, 1.6 * s, 2.4 * s), (0.85, 0.68, 0.22, 1))
    for d in (-1, 1):
        braco = caixa(_id("sbraco"), (0, 0, 0), (1.2 * s, 0.15 * s, 0.15 * s), C["cinza"]); filho(corpo, braco); braco.location = (d * 1.4 * s, 0, 0)
        pain = caixa(_id("spain"), (0, 0, 0), (4.0 * s, 1.8 * s, 0.08 * s), (0.10, 0.16, 0.38, 1)); filho(corpo, pain); pain.location = (d * 4.0 * s, 0, 0)
    lente = cilindro(_id("slente"), (0, 0, 0), 0.55 * s, 0.6 * s, C["escuro"], seg=12); filho(corpo, lente); lente.location = (0, 0, -1.45 * s)
    return corpo

# ---------- modelos de arsenal (vídeo estoque de mísseis, 26/11) ----------
def tomahawk(nome, escala=1.0, cor=(0.86, 0.87, 0.88, 1), unico=None):
    """Míssil de cruzeiro: corpo longo e liso, nariz arredondado, asas finas no meio, 4 aletas em X,
    faixa escura e bocal do motor. Frente = +Y (deitado)."""
    e = escala; Mx = __import__("mathutils").Matrix
    corpo = cilindro(nome, (0, 0, 0), 0.26 * e, 5.6 * e, cor, seg=14, unico=unico)
    corpo.data.transform(Mx.Rotation(math.radians(-90), 4, "X"))
    for pl in corpo.data.polygons: pl.use_smooth = True
    nariz = esfera(_id("tnariz"), (0, 0, 0), 0.26 * e, cor, sub=2, unico=unico); nariz.scale = (1, 1.9, 1); filho(corpo, nariz); nariz.location = (0, 2.8 * e, 0)
    for pl in nariz.data.polygons: pl.use_smooth = True
    faixa = cilindro(_id("tfaixa"), (0, 0, 0), 0.27 * e, 0.22 * e, (0.18, 0.20, 0.24, 1), seg=14); faixa.data.transform(Mx.Rotation(math.radians(-90), 4, "X"))
    filho(corpo, faixa); faixa.location = (0, 1.7 * e, 0)
    asa = caixa(_id("tasa"), (0, 0, 0), (2.9 * e, 0.45 * e, 0.05 * e), (0.70, 0.72, 0.74, 1)); filho(corpo, asa); asa.location = (0, 0.2 * e, -0.12 * e)
    for a in (45, 135, 225, 315):
        al = caixa(_id("taleta"), (0, 0, 0), (0.05 * e, 0.45 * e, 0.62 * e), (0.70, 0.72, 0.74, 1)); filho(corpo, al)
        r = math.radians(a); al.location = (math.cos(r) * 0.38 * e, -2.55 * e, math.sin(r) * 0.38 * e); al.rotation_euler = (0, -r + math.pi / 2, 0)
    boc = cilindro(_id("tbocal"), (0, 0, 0), 0.16 * e, 0.3 * e, (0.15, 0.15, 0.16, 1), seg=10); boc.data.transform(Mx.Rotation(math.radians(-90), 4, "X"))
    filho(corpo, boc); boc.location = (0, -2.9 * e, 0)
    return corpo

def caixote_missil(nome, cor=(0.36, 0.42, 0.26, 1), escala=1.0, unico=None):
    """Contêiner de transporte de míssil: caixa longa verde-oliva com aros, tampa e plaqueta amarela."""
    e = escala
    cx = caixa(nome, (0, 0, 0), (1.0 * e, 6.2 * e, 1.0 * e), cor, unico=unico)
    for y in (-2.4, 0.0, 2.4):
        filho(cx, caixa(_id("caro"), (0, y * e, 0), (1.08 * e, 0.18 * e, 1.08 * e), tuple(c * 0.7 for c in cor[:3]) + (1,)))
    filho(cx, caixa(_id("cplaca"), (0.55 * e, 1.2 * e, 0.15 * e), (0.04 * e, 0.9 * e, 0.4 * e), (0.95, 0.80, 0.15, 1)))
    return cx

def lancador_patriot(nome, loc, cor=(0.42, 0.46, 0.30, 1)):
    """Lançador tipo Patriot: semirreboque com 4 tubos quadrados inclinados (2x2), estabilizadores e cabine.
    Devolve (chassi, pivô dos tubos, [bocas dos tubos em coordenadas locais do pivô])."""
    chassi = caixa(nome, loc, (2.6, 10.0, 0.7), C["escuro"])
    cab = caixa(_id("pcab"), (0, 6.0, 0.9), (2.5, 2.2, 2.0), cor); filho(chassi, cab)
    vid = caixa(_id("pvid"), (0, 7.12, 1.3), (2.1, 0.06, 0.7), (0.15, 0.25, 0.35, 1)); filho(chassi, vid)
    for x in (-1.3, 1.3):
        for y in (-3.6, -2.4, 5.6):
            r = cilindro(_id("proda"), (x, y, -0.4), 0.55, 0.45, C["escuro"], seg=10); r.rotation_euler = (0, math.radians(90), 0); filho(chassi, r)
        for y in (-4.6, 3.8):
            pe = caixa(_id("ppe"), (x * 1.25, y, -0.5), (0.3, 0.3, 1.0), (0.30, 0.30, 0.30, 1)); filho(chassi, pe)
    piv = vazio(nome + "_piv", (0, -4.2, 0.6)); filho(chassi, piv)
    bocas = []
    for i, x in enumerate((-0.62, 0.62)):
        for j, z in enumerate((0.62, 1.86)):
            tb = caixa(_id("ptubo"), (x, 3.4, z), (1.18, 6.8, 1.18), cor); filho(piv, tb)
            tp = caixa(_id("ptampa"), (x, 6.82, z), (1.0, 0.06, 1.0), (0.85, 0.85, 0.80, 1)); filho(piv, tp)
            bocas.append((x, 6.9, z))
    piv.rotation_euler = (math.radians(38), 0, 0)
    return chassi, piv, bocas

# ---------- modelos navais (vídeo drones na Líbia, 26/11) ----------
def drone_naval(nome, escala=1.0, cor=(0.20, 0.22, 0.24, 1)):
    """Drone naval (barco sem tripulação): casco baixo em cunha, proa afilada, convés plano com tampa de
    carga, mastro de antena e câmera na frente, jato d'água na popa. Frente = +Y."""
    e = escala
    bm = bmesh.new()
    pts = [(-0.45, -1.6, 0.0), (0.45, -1.6, 0.0), (0.5, 0.6, 0.0), (0.0, 1.9, 0.05),
           (-0.5, 0.6, 0.0)]
    base = [bm.verts.new((x * e, y * e, z * e - 0.12 * e)) for x, y, z in pts]
    topo = [bm.verts.new((x * e * 0.92, y * e * 0.97, 0.30 * e)) for x, y, z in pts]
    bm.faces.new(list(reversed(base))); bm.faces.new(topo)
    for i in range(len(pts)):
        j = (i + 1) % len(pts); bm.faces.new([base[i], base[j], topo[j], topo[i]])
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    casco = bpy.data.objects.new(nome, me); bpy.context.collection.objects.link(casco); casco.data.materials.append(mat(cor))
    faixa = caixa(_id("faixaDN"), (0, 0, 0), (0.95 * e, 0.12 * e, 0.06 * e), (0.95, 0.80, 0.15, 1)); filho(casco, faixa); faixa.location = (0, 0.9 * e, 0.31 * e)
    tampa = caixa(_id("tampaDN"), (0, 0, 0), (0.6 * e, 1.1 * e, 0.08 * e), (0.30, 0.32, 0.34, 1)); filho(casco, tampa); tampa.location = (0, -0.3 * e, 0.34 * e)
    mastro = cilindro(_id("mastroDN"), (0, 0, 0), 0.04 * e, 0.8 * e, C["escuro"], seg=5); filho(casco, mastro); mastro.location = (0, -1.0 * e, 0.7 * e)
    for k, dz in enumerate((0.95, 1.1)):
        ant = cilindro(_id("antDN"), (0, 0, 0), 0.09 * e, 0.05 * e, (0.85, 0.85, 0.85, 1), seg=8); filho(casco, ant); ant.location = (0, -1.0 * e, dz * e)
    cam = esfera(_id("camDN"), (0, 0, 0), 0.12 * e, (0.05, 0.05, 0.06, 1), sub=1); filho(casco, cam); cam.location = (0, 1.2 * e, 0.38 * e)
    jato = cilindro(_id("jatoDN"), (0, 0, 0), 0.14 * e, 0.25 * e, C["escuro"], seg=8); filho(casco, jato); jato.location = (0, -1.68 * e, 0.0); jato.rotation_euler = (math.radians(90), 0, 0)
    return casco

def corveta(nome, escala=1.0, cinza=(0.52, 0.55, 0.58, 1)):
    """Corveta mais detalhada que navio_guerra: casco com proa em cunha e borda escura, canhão na proa,
    células de mísseis, superestrutura em 3 níveis com janelas da ponte, mastro com radar, chaminé,
    hangar e convoo com helicóptero na popa. Frente = +Y."""
    e = escala
    bm = bmesh.new()
    pts = [(-0.75, -4.2), (0.75, -4.2), (0.8, 2.2), (0.0, 4.6), (-0.8, 2.2)]
    base = [bm.verts.new((x * e * 0.8, y * e, -0.45 * e)) for x, y in pts]
    topo = [bm.verts.new((x * e, y * e * 1.02, 0.45 * e)) for x, y in pts]
    bm.faces.new(list(reversed(base))); bm.faces.new(topo)
    for i in range(len(pts)):
        j = (i + 1) % len(pts); bm.faces.new([base[i], base[j], topo[j], topo[i]])
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    casco = bpy.data.objects.new(nome, me); bpy.context.collection.objects.link(casco); casco.data.materials.append(mat(cinza))
    borda = caixa(_id("bordaC"), (0, 0, 0), (1.62 * e, 8.2 * e, 0.10 * e), (0.12, 0.12, 0.14, 1)); filho(casco, borda); borda.location = (0, -0.1 * e, -0.38 * e)
    claro = (0.66, 0.69, 0.72, 1)
    for nivel, (w, l, h, y, z) in enumerate([(1.2, 3.0, 0.7, -0.6, 0.8), (1.0, 1.9, 0.55, -0.2, 1.42), (0.8, 0.9, 0.4, 0.2, 1.88)]):
        s = caixa(_id("supC"), (0, 0, 0), (w * e, l * e, h * e), claro); filho(casco, s); s.location = (0, y * e, z * e)
    jan = caixa(_id("janC"), (0, 0, 0), (0.82 * e, 0.06 * e, 0.14 * e), (0.05, 0.08, 0.12, 1)); filho(casco, jan); jan.location = (0, 0.66 * e, 1.92 * e)
    mastro = cilindro(_id("mastroC"), (0, 0, 0), 0.07 * e, 1.8 * e, (0.30, 0.31, 0.33, 1), seg=6); filho(casco, mastro); mastro.location = (0, 0.0, 2.9 * e)
    rad = caixa(_id("radC"), (0, 0, 0), (1.0 * e, 0.14 * e, 0.32 * e), C["branco"]); filho(casco, rad); rad.location = (0, 0.0, 3.5 * e)
    esf = esfera(_id("domoC"), (0, 0, 0), 0.22 * e, C["branco"], sub=1); filho(casco, esf); esf.location = (0, 0.0, 3.95 * e)
    cham = caixa(_id("chamC"), (0, 0, 0), (0.5 * e, 0.6 * e, 0.7 * e), (0.40, 0.42, 0.45, 1)); filho(casco, cham); cham.location = (0, -1.7 * e, 1.3 * e)
    torre = cilindro(_id("torreC"), (0, 0, 0), 0.38 * e, 0.4 * e, cinza, seg=10); filho(casco, torre); torre.location = (0, 2.9 * e, 0.65 * e)
    cano = cilindro(_id("canoC"), (0, 0, 0), 0.06 * e, 1.3 * e, C["escuro"], seg=6); filho(casco, cano); cano.location = (0, 3.5 * e, 0.8 * e); cano.rotation_euler = (math.radians(-82), 0, 0)
    for k in range(4):
        cel = caixa(_id("celC"), (0, 0, 0), (0.28 * e, 0.28 * e, 0.06 * e), (0.25, 0.26, 0.28, 1)); filho(casco, cel)
        cel.location = ((-0.2 + 0.4 * (k % 2)) * e, (1.7 + 0.35 * (k // 2)) * e, 0.48 * e)
    hang = caixa(_id("hangC"), (0, 0, 0), (1.1 * e, 1.0 * e, 0.7 * e), claro); filho(casco, hang); hang.location = (0, -2.5 * e, 0.8 * e)
    conv = caixa(_id("convC"), (0, 0, 0), (1.3 * e, 1.3 * e, 0.04 * e), (0.30, 0.32, 0.34, 1)); filho(casco, conv); conv.location = (0, -3.6 * e, 0.47 * e)
    marca = anel(_id("hC"), (0, 0, 0), 0.4 * e, 0.04 * e, C["branco"], seg=20); filho(casco, marca); marca.location = (0, -3.6 * e, 0.5 * e)
    return casco

def mar_ondulado(nome, loc, tam, cor, res=120, altura=0.35, escala_onda=6.0, t_fim=90.0, vel=(1.2, 0.6)):
    """Backlog 4/32: mar com ondas de verdade. Grade subdividida + modificador Displace com textura de nuvens
    cujas coordenadas seguem um vazio que desliza no tempo (ondas andando)."""
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=res, y_subdivisions=res, size=1, location=loc)
    m = bpy.context.active_object; m.name = nome; m.scale = (tam[0], tam[1], 1)
    m.data.materials.append(mat(cor))
    for p in m.data.polygons: p.use_smooth = True
    tx = bpy.data.textures.new(nome + "_tx", "CLOUDS"); tx.noise_scale = escala_onda; tx.noise_depth = 1
    ref = vazio(nome + "_ref", (0, 0, 0))
    ref.location = (0, 0, 0); ref.keyframe_insert("location", frame=1)
    ref.location = (vel[0] * t_fim, vel[1] * t_fim, 0); ref.keyframe_insert("location", frame=f(t_fim))
    for fc in ref.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
    d = m.modifiers.new("ondas", "DISPLACE"); d.texture = tx; d.strength = altura; d.mid_level = 0.5
    d.texture_coords = "OBJECT"; d.texture_coords_object = ref
    return m
