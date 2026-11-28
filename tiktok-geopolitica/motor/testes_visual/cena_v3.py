"""Cena de TESTE do visual v3 (não é o motor de produção).
Personagens de verdade (Quaternius, CC0), rigados e animados por NLA, numa rua de cidade cartoon, 30 FPS reais.
O "Pixel" é o Casual2_Male do Ultimate Animated Character Pack recolorido (moletom laranja de manga longa,
calça azul-escura, tênis branco, cabelo escuro) + fone verde e sorriso feitos aqui.
Uso:
  blender -b --factory-startup -P cena_v3.py -- <pasta_saida> [range A,B | quadros 1,60,120]
Variáveis: RES=1080 (ou 540), AMOSTRAS=8, VISUAL=2 (contorno/luz de contorno/fundo desfocado; 0 desliga).
Os modelos (dados de terceiros) só são importados por FBX: nada de dentro deles é executado."""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix, Quaternion

AQUI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.dirname(AQUI)
sys.path.insert(0, MOTOR)
from cartoon import visual_nivel2          # visual nível 2 já aprovado (contorno, luz de contorno, desfoque)

MOD = os.path.join(os.path.dirname(MOTOR), "assets", "modelos")
UACP = os.path.join(MOD, "quaternius_ultimate_animated_character", "Ultimate Animated Character Pack - Nov 2019", "FBX")
RUAS = os.path.join(MOD, "quaternius_modular_streets", "FBX")
CARROS = os.path.join(MOD, "quaternius_cars", "Realistic Car Pack - Nov 2018", "FBX")

FPS = 30; DUR = 7.0; NQ = int(DUR * FPS)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SAIDA = argv[0] if argv else os.path.join(AQUI, "v3")
RES = int(os.environ.get("RES", "1080"))
random.seed(7)

def F(t): return int(round(t * FPS)) + 1
def lin(c): return tuple((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c[:3]) + (1.0,)

# ---------------------------------------------------------------- cena limpa
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
s = bpy.context.scene
s.render.fps = FPS; s.frame_start = 1; s.frame_end = NQ

_mc = {}
def mcor(rgb, rough=0.6, emis=0.0, nome=None):
    k = (tuple(round(x, 3) for x in rgb[:3]), rough, emis)
    if k in _mc: return _mc[k]
    m = bpy.data.materials.new(nome or "c%d" % len(_mc)); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(rgb); b.inputs["Roughness"].default_value = rough
    try: b.inputs["Specular IOR Level"].default_value = 0.25
    except Exception: pass
    if emis:
        b.inputs["Emission Color"].default_value = lin(rgb); b.inputs["Emission Strength"].default_value = emis
    m.diffuse_color = rgb[:3] + (1,); _mc[k] = m; return m

def caixa(loc, dim, cor, rough=0.6, emis=0.0, bev=True):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object
    o.scale = dim; bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mcor(cor, rough, emis))
    if bev and min(dim) > 0.08:
        md = o.modifiers.new("bev", "BEVEL"); md.width = min(0.12, min(dim) * 0.15); md.segments = 2
    return o

def importar_fbx(path):
    antes_o, antes_a = set(bpy.data.objects), set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=path)
    novos = [o for o in bpy.data.objects if o not in antes_o]
    for o in novos:
        if o.type == "MESH":
            for m in o.data.materials:
                if m and m.use_nodes and "Principled BSDF" in m.node_tree.nodes:
                    m.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 1.0
                    m.blend_method = "OPAQUE"
    acoes = [a for a in bpy.data.actions if a not in antes_a]
    for a in acoes:      # as ações do FBX também chaveiam escala/posição do objeto armadura: só os ossos interessam
        for fc in list(a.fcurves):
            if not fc.data_path.startswith("pose.bones"): a.fcurves.remove(fc)
    return novos, acoes

# ---------------------------------------------------------------- personagens
PELE = (0.96, 0.76, 0.60)
def personagem(arquivo, cores, escala=0.55, mangas=False, calca_longa=False, tenis=None, fone=None, sorriso=True):
    novos, acoes = importar_fbx(os.path.join(UACP, arquivo + ".fbx"))
    arm = next(o for o in novos if o.type == "ARMATURE")
    corpo = next(o for o in novos if o.type == "MESH")
    if arm.animation_data: arm.animation_data.action = None
    for pb in arm.pose.bones: pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    me = corpo.data
    idx = {}
    for i, m in enumerate(me.materials):
        base = m.name.split(".")[0]; idx[base] = i
        cor = cores.get(base, PELE if base == "Skin" else None)
        if base == "Face": cor = cores.get("Face", (0.05, 0.04, 0.05))
        if cor is not None: me.materials[i] = mcor(cor, 0.55 if base != "Face" else 0.3)
    # manga longa / calça longa / tênis: repinta faces da pele conforme o osso dominante
    gn = {g.index: g.name for g in corpo.vertex_groups}
    dom = []
    for v in me.vertices:
        g = max(v.groups, key=lambda x: x.weight, default=None); dom.append(gn[g.group] if g else "")
    if tenis is not None:
        me.materials.append(mcor(tenis, 0.5)); idx["Tenis"] = len(me.materials) - 1
    pele_i = idx.get("Skin")
    # sobrancelhas do modelo são inclinadas (cara de bravo): viram pele, ficam só os olhos ovais
    fi = idx.get("Face"); fz = [p.center.z for p in me.polygons if p.material_index == fi]
    if fz:
        zc = sorted(fz)[len(fz) // 2]
        for p in me.polygons:
            if p.material_index == fi and p.center.z > zc + 0.06: p.material_index = pele_i
    for p in me.polygons:
        if p.material_index != pele_i: continue
        gs = [dom[v] for v in p.vertices]; g = max(set(gs), key=gs.count)
        if mangas and g.startswith(("UpperArm", "LowerArm", "Shoulder")): p.material_index = idx["Shirt"]
        elif calca_longa and g.startswith(("LowerLeg", "UpperLeg")): p.material_index = idx["Pants"]
        elif tenis is not None and g.startswith("Foot"): p.material_index = idx["Tenis"]
    arm.scale = (escala,) * 3
    bpy.context.view_layer.update()
    # cabeça (pose de repouso) para encaixar fone e sorriso
    cab = [corpo.matrix_world @ me.vertices[i].co for i, g in enumerate(dom) if g == "Head"]
    mn = Vector([min(v[k] for v in cab) for k in range(3)]); mx = Vector([max(v[k] for v in cab) for k in range(3)])
    c = (mn + mx) / 2; L = (mx - mn)
    extras = []
    if fone:
        bpy.ops.mesh.primitive_torus_add(major_radius=L.x * 0.56, minor_radius=L.x * 0.05, major_segments=40, minor_segments=8,
                                         location=(c.x, c.y + L.y * 0.05, c.z + L.z * 0.06), rotation=(math.radians(90), 0, 0))
        aro = bpy.context.object; aro.data.materials.append(mcor(fone, 0.4))
        bm = bmesh.new(); bm.from_mesh(aro.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -L.x * 0.05], context="VERTS")   # meia-volta por cima
        bm.to_mesh(aro.data); bm.free(); extras.append(aro)
        for sx in (-1, 1):
            bpy.ops.mesh.primitive_cylinder_add(radius=L.z * 0.13, depth=L.x * 0.12, vertices=20,
                                                location=(c.x + sx * L.x * 0.55, c.y + L.y * 0.12, c.z - L.z * 0.02), rotation=(0, math.radians(90), 0))
            cp = bpy.context.object; cp.data.materials.append(mcor(fone, 0.4))
            md = cp.modifiers.new("bev", "BEVEL"); md.width = L.z * 0.04; md.segments = 3
            for pl in cp.data.polygons: pl.use_smooth = True
            extras.append(cp)
            bpy.ops.mesh.primitive_cylinder_add(radius=L.z * 0.09, depth=L.x * 0.03, vertices=20,
                                                location=(c.x + sx * L.x * 0.62, c.y + L.y * 0.12, c.z - L.z * 0.02), rotation=(0, math.radians(90), 0))
            cp2 = bpy.context.object; cp2.data.materials.append(mcor((0.10, 0.12, 0.10), 0.5)); extras.append(cp2)
    if sorriso:
        bpy.ops.mesh.primitive_torus_add(major_radius=L.x * 0.13, minor_radius=L.x * 0.022, major_segments=24, minor_segments=6,
                                         location=(c.x, mn.y + L.y * 0.02, c.z - L.z * 0.10), rotation=(math.radians(90), 0, 0))
        so = bpy.context.object; so.data.materials.append(mcor((0.45, 0.10, 0.08), 0.5))
        bm = bmesh.new(); bm.from_mesh(so.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > L.x * 0.02], context="VERTS")   # só a metade de baixo
        bm.to_mesh(so.data); bm.free(); extras.append(so)
    for e in extras:
        mw = e.matrix_world.copy(); e.parent = arm; e.parent_type = "BONE"; e.parent_bone = "Head"; e.matrix_world = mw
    def acao(nome):
        return next(a for a in acoes if a.name.split("|")[-1].split(".")[0] == nome)
    arm.animation_data_create()
    return arm, acao

_trk = [0]
def tocar(arm, action, ini, repetir=1.0, blend_in=0, blend_out=0, velocidade=1.0, extrap="HOLD_FORWARD"):
    """Cada strip numa trilha própria por cima das anteriores; blend_in faz a transição suave."""
    tr = arm.animation_data.nla_tracks.new(); _trk[0] += 1; tr.name = "t%d" % _trk[0]
    st = tr.strips.new(action.name, int(ini), action)
    st.repeat = repetir; st.scale = 1.0 / velocidade
    st.blend_in = blend_in; st.blend_out = blend_out; st.extrapolation = extrap
    st.use_auto_blend = False
    return st

def velocidade_passo(arm, walk):
    """Velocidade (m/quadro) que casa o deslocamento com o pé de apoio da animação Walk (sem patinar)."""
    arm.animation_data.action = walk
    pb = arm.pose.bones["Foot.L"]; ys, zs = [], []
    f0, f1 = map(int, walk.frame_range)
    for fr in range(f0, f1 + 1):
        s.frame_set(fr); ys.append(pb.head.y); zs.append(pb.head.z)
    zmin = min(zs); h = max(zs) - zmin
    vs = sorted(ys[i + 1] - ys[i] for i in range(len(ys) - 1) if zs[i] < zmin + 0.15 * h and zs[i + 1] < zmin + 0.15 * h)
    arm.animation_data.action = None
    for p in arm.pose.bones: p.rotation_quaternion = (1, 0, 0, 0); p.location = (0, 0, 0)
    v = abs(vs[len(vs) // 2]) if vs else 0.03
    return v * arm.scale[0], f1 - f0

def acao_aceno(arm, f_ini, f_fim, n=4):
    """Aceno com a mão direita (só UpperArm.R/LowerArm.R/Fist.R), montado por direções no espaço da armadura."""
    ac = bpy.data.actions.new("Aceno_" + arm.name); arm.animation_data.action = ac
    ossos = ["UpperArm.R", "LowerArm.R", "Fist.R"]
    def mirar(nome, alvo):
        pb = arm.pose.bones[nome]; d = (pb.tail - pb.head).normalized()
        q = d.rotation_difference(Vector(alvo).normalized())
        pb.matrix = Matrix.Translation(pb.head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-pb.head) @ pb.matrix
        bpy.context.view_layer.update()
    tot = f_fim - f_ini
    for k in range(0, tot + 1, 3):
        for nm in ossos: arm.pose.bones[nm].rotation_quaternion = (1, 0, 0, 0)
        bpy.context.view_layer.update()
        u = k / tot; sub = min(1.0, u / 0.15)                          # sobe o braço nos primeiros 15%
        osc = math.sin((u - 0.15) / 0.85 * n * 2 * math.pi) if u > 0.15 else 0
        mirar("UpperArm.R", Vector((-0.55, -0.15, -0.8)).lerp(Vector((-0.62, -0.25, 0.75)), sub))
        mirar("LowerArm.R", Vector((-0.5, -0.1, -0.8)).lerp(Vector((-0.05 - 0.65 * osc, -0.30, 0.85)), sub))
        for nm in ossos: arm.pose.bones[nm].keyframe_insert("rotation_quaternion", frame=f_ini + k)
    arm.animation_data.action = None
    for nm in ossos: arm.pose.bones[nm].rotation_quaternion = (1, 0, 0, 0)
    return ac

def chave(o, path, fr, val, interp="BEZIER"):
    setattr(o, path, val); o.keyframe_insert(path, frame=fr)
    for fc in o.animation_data.action.fcurves:
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                if int(kp.co[0]) == fr: kp.interpolation = interp

def andar(arm, walk, x0, y, x1, f0, rumo):
    """Pedestre andando em linha reta de x0 a x1 a partir de f0, na velocidade que casa com o passo."""
    v, ciclo = velocidade_passo(arm, walk)
    dist = abs(x1 - x0); nq = dist / v
    arm.location = (x0, y, 0); arm.rotation_euler = (0, 0, rumo)
    chave(arm, "location", f0, (x0, y, 0), "LINEAR"); chave(arm, "location", int(f0 + nq), (x1, y, 0), "LINEAR")
    tocar(arm, walk, f0 - ciclo * 2, repetir=(nq / ciclo) + 3, extrap="HOLD")
    return v

# ---------------------------------------------------------------- cidade
def cidade():
    caixa((10, 0, -0.06), (160, 80, 0.1), (0.55, 0.78, 0.42), bev=False)                         # chão/grama
    # rua do pacote (escala 4: uma peça = 8 m)
    for i in range(-6, 9):
        novos, _ = importar_fbx(os.path.join(RUAS, "Street_Straight.fbx"))
        for o in novos:
            o.scale = (4 * o.scale[0], 4 * o.scale[1], 4 * o.scale[2]); o.location = (i * 8, 0, -0.5)
            o.rotation_euler = (o.rotation_euler[0], o.rotation_euler[1], o.rotation_euler[2] + math.radians(RUA_ROT))
    # calçadas + meio-fio
    for y0 in (-1, 1):
        caixa((10, y0 * 6.3, 0.09), (160, 4.6, 0.18), (0.86, 0.82, 0.76), bev=False)
        caixa((10, y0 * 4.05, 0.11), (160, 0.22, 0.22), (0.70, 0.68, 0.66), bev=False)
        for k in range(-20, 30):                                                                    # juntas da calçada
            caixa((k * 2.0, y0 * 6.3, 0.185), (0.05, 4.6, 0.01), (0.74, 0.70, 0.66), bev=False)
    # postes do pacote
    for x in range(-24, 40, 12):
        for y0, rz in ((-1, 0), (1, 180)):
            novos, _ = importar_fbx(os.path.join(RUAS, "Streetlight_Single.fbx"))
            for o in novos:
                o.scale = tuple(4.5 * k for k in o.scale); o.location = (x + (6 if y0 > 0 else 0), y0 * 4.6, 0.18)
                o.rotation_euler[2] += math.radians(rz + 90 * (1 if y0 < 0 else -1) * 0)
    # prédios do outro lado da rua
    cores = [(1.0, 0.72, 0.45), (0.55, 0.78, 0.98), (0.98, 0.58, 0.62), (0.70, 0.88, 0.60), (0.99, 0.88, 0.50),
             (0.78, 0.66, 0.95), (0.55, 0.88, 0.85), (1.0, 0.80, 0.70)]
    x = -34.0; i = 0
    while x < 46:
        w = random.choice([6.5, 7.5, 8.5, 9.5]); h = random.choice([9, 11, 13, 15, 18]); cor = cores[i % len(cores)]
        predio_cartoon(x + w / 2, 9.0, w, 6.0, h, cor); x += w + 0.3; i += 1
    # segunda fileira bem atrás (silhueta no desfoque)
    x = -40.0
    while x < 52:
        w = random.choice([8, 10, 12]); h = random.choice([20, 24, 28, 32])
        caixa((x + w / 2, 20, h / 2), (w, 6, h), random.choice([(0.70, 0.80, 0.95), (0.80, 0.78, 0.92), (0.76, 0.88, 0.94)]))
        x += w + 1.5
    # árvores na calçada de cá
    for x in (-16, 13, 30):
        arvore((x, -7.9))
    for x in (-8, 10, 26):
        arvore((x, 7.4), 0.9)

def predio_cartoon(cx, y0, w, d, h, cor):
    caixa((cx, y0 + d / 2, h / 2), (w, d, h), cor)
    escura = tuple(c * 0.78 for c in cor)
    caixa((cx, y0 + d / 2, h + 0.2), (w + 0.4, d + 0.4, 0.4), escura)                                # platibanda
    # janelas: uma malha por prédio (barato)
    bm = bmesh.new(); ncol = max(2, int(w / 2.2)); passo = w / ncol
    for andar_i in range(1, int((h - 3.5) / 3.0) + 1):
        z = 3.5 + andar_i * 3.0 - 1.4
        for c in range(ncol):
            xx = cx - w / 2 + passo * (c + 0.5)
            r = bmesh.ops.create_cube(bm, size=1.0)["verts"]
            bmesh.ops.scale(bm, vec=(passo * 0.55, 0.12, 1.5), verts=r); bmesh.ops.translate(bm, vec=(xx, y0 - 0.02, z), verts=r)
            r = bmesh.ops.create_cube(bm, size=1.0)["verts"]                                        # peitoril
            bmesh.ops.scale(bm, vec=(passo * 0.68, 0.3, 0.16), verts=r); bmesh.ops.translate(bm, vec=(xx, y0 - 0.1, z - 0.85), verts=r)
    me = bpy.data.meshes.new("jan"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("janelas", me); s.collection.objects.link(o)
    me.materials.append(mcor((0.30, 0.52, 0.78), 0.15, 0.25))
    # térreo: vitrine + toldo listrado + porta
    caixa((cx, y0 - 0.05, 1.6), (w * 0.62, 0.14, 2.2), (0.36, 0.62, 0.86), 0.12, 0.35)
    caixa((cx + w * 0.38, y0 - 0.05, 1.3), (1.2, 0.16, 2.5), (0.45, 0.28, 0.18))
    toldo = random.choice([(0.95, 0.30, 0.28), (0.20, 0.65, 0.45), (0.25, 0.45, 0.90), (0.98, 0.72, 0.15)])
    n = 6
    for k in range(n):
        tw = w * 0.7 / n
        t = caixa((cx - w * 0.35 + tw * (k + 0.5), y0 - 0.7, 3.25), (tw, 1.4, 0.12), toldo if k % 2 == 0 else (0.98, 0.97, 0.94), bev=False)
        t.rotation_euler[0] = math.radians(-18)

def arvore(loc, sc=1.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.16 * sc, depth=2.6 * sc, vertices=8, location=(loc[0], loc[1], 1.3 * sc))
    tr = bpy.context.object; tr.data.materials.append(mcor((0.50, 0.33, 0.20)))
    for dx, dz, r in ((0, 3.3, 1.35), (0.7, 2.8, 0.95), (-0.7, 2.9, 1.0)):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r * sc, location=(loc[0] + dx * sc, loc[1], dz * sc))
        cp = bpy.context.object; cp.data.materials.append(mcor(random.choice([(0.36, 0.72, 0.30), (0.42, 0.78, 0.34)])))
        for p in cp.data.polygons: p.use_smooth = True

def carro(arquivo, cor_lataria=None):
    novos, _ = importar_fbx(os.path.join(CARROS, arquivo + ".fbx"))
    raiz = bpy.data.objects.new("carro_" + arquivo, None); s.collection.objects.link(raiz)
    rodas = []
    for o in novos:
        if o.parent is None:
            mw = o.matrix_world.copy(); o.parent = raiz; o.matrix_world = mw
        if "Wheel" in o.name: rodas.append(o)
        if o.type == "MESH" and cor_lataria and "Wheel" not in o.name:
            o.data.materials[0] = mcor(cor_lataria, 0.35)
        if o.type == "MESH":
            for i, m in enumerate(o.data.materials):
                if m and m.name.startswith("Windows"): o.data.materials[i] = mcor((0.18, 0.28, 0.45), 0.1)
    return raiz, rodas

RUA_ROT = float(os.environ.get("RUA_ROT", "0"))

# ---------------------------------------------------------------- montagem
cidade()

# Pixel
PX_Y = -6.6
px, px_acao = personagem("Casual2_Male", {"Shirt": (1.0, 0.48, 0.12), "Pants": (0.17, 0.21, 0.36), "Hair": (0.16, 0.10, 0.08),
                                          "Belt": (0.85, 0.36, 0.06)},
                         mangas=True, calca_longa=True, tenis=(0.97, 0.97, 0.97), fone=(0.55, 0.95, 0.20))
walk = px_acao("Walk"); idle = px_acao("Idle"); vit = px_acao("Victory")
v, ciclo = velocidade_passo(px, walk)
T_PARA = 3.2                                    # para de andar e vira para a câmera
f_para = F(T_PARA); x_para = 2.0; x_ini = x_para - v * (f_para - 1)
aceno = acao_aceno(px, F(3.75), F(5.25))
px.location = (x_ini, PX_Y, 0)
chave(px, "location", 1, (x_ini, PX_Y, 0), "LINEAR")
chave(px, "location", f_para - 4, (x_para - v * 4, PX_Y, 0), "BEZIER")
chave(px, "location", f_para + 6, (x_para + v * 3, PX_Y, 0), "BEZIER")
chave(px, "rotation_euler", f_para - 6, (0, 0, math.radians(90)))
chave(px, "rotation_euler", f_para + 10, (0, 0, math.radians(8)))
tocar(px, walk, 1 - ciclo, repetir=(f_para + ciclo) / ciclo + 1, extrap="HOLD")
tocar(px, idle, f_para - 6, repetir=3, blend_in=12)
st = tocar(px, aceno, F(3.75), blend_in=6, blend_out=6, extrap="NOTHING")
tocar(px, vit, F(5.25), blend_in=8)

# pedestres
p1, a1 = personagem("Casual_Female", {"Shirt": (0.30, 0.75, 0.95), "Pants": (0.95, 0.85, 0.35), "Hair": (0.55, 0.30, 0.12)},
                    calca_longa=False, tenis=(0.95, 0.35, 0.40))
andar(p1, a1("Walk"), 16, 6.2, -16, 1, math.radians(-90))
p2, a2 = personagem("Casual3_Male", {"Shirt": (0.55, 0.85, 0.40), "Pants": (0.30, 0.32, 0.40), "Hair": (0.12, 0.08, 0.06)},
                    mangas=False, tenis=(0.25, 0.25, 0.30))
andar(p2, a2("Walk"), -12, 6.8, 18, 1, math.radians(90))
p3, a3 = personagem("Suit_Female", {"Shirt": (0.96, 0.96, 0.96), "Black": (0.25, 0.22, 0.45), "Hair": (0.20, 0.12, 0.08)},
                    tenis=(0.15, 0.12, 0.25))
andar(p3, a3("Walk"), 12, -4.9, -10, 1, math.radians(-90))

# carro passando (pista de cá) e um estacionado
car, rodas = carro("Taxi")
car.rotation_euler = (0, 0, math.radians(-90))     # frente do pacote aponta -Y; gira para andar em +X
chave(car, "location", F(0.6), (-30, -1.9, 0.02), "LINEAR"); chave(car, "location", F(4.6), (40, -1.9, 0.02), "LINEAR")
for r in rodas:
    r.rotation_mode = "XYZ"; r0 = r.rotation_euler[0]
    voltas = 70 / (math.pi * 0.52)
    chave(r, "rotation_euler", F(0.6), (r0, r.rotation_euler[1], r.rotation_euler[2]), "LINEAR")
    chave(r, "rotation_euler", F(4.6), (r0 - voltas * 2 * math.pi, r.rotation_euler[1], r.rotation_euler[2]), "LINEAR")
par, _ = carro("NormalCar1", (0.95, 0.35, 0.30)); par.location = (-9, 2.6, 0.02); par.rotation_euler = (0, 0, math.radians(90))

# câmera acompanhando o Pixel
alvo = bpy.data.objects.new("alvo_cam", None); s.collection.objects.link(alvo)
cd = bpy.data.cameras.new("cam"); cd.lens = 30; cd.sensor_fit = "VERTICAL"; cd.sensor_height = 24
cam = bpy.data.objects.new("cam", cd); s.collection.objects.link(cam); s.camera = cam
tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
for fr, ax, cx_, cy_, cz_, az in ((1, x_ini + 0.3, x_ini + 1.6, -13.0, 1.6, 1.7), (f_para, x_para, x_para + 1.2, -11.6, 1.3, 1.75),
                                  (F(5.3), x_para + 0.1, x_para + 0.6, -11.0, 1.3, 1.65), (NQ, x_para + 0.1, x_para + 0.4, -10.7, 1.3, 1.7)):
    chave(alvo, "location", fr, (ax, PX_Y, az), "BEZIER"); chave(cam, "location", fr, (cx_, cy_, cz_), "BEZIER")
for o in (alvo, cam):
    for fc in o.animation_data.action.fcurves:
        fc.keyframe_points[0].interpolation = "LINEAR"

# ---------------------------------------------------------------- render (EEVEE, estilo cartoon + nível 2)
s.render.engine = "BLENDER_EEVEE_NEXT"
s.render.resolution_x, s.render.resolution_y = (RES, RES * 16 // 9)
s.eevee.taa_render_samples = int(os.environ.get("AMOSTRAS", "8"))
for k, val in (("use_shadows", True), ("use_raytracing", True), ("shadow_ray_count", 1), ("shadow_step_count", 4),
               ("use_gtao", True), ("gtao_distance", 0.6)):
    try: setattr(s.eevee, k, val)
    except Exception: pass
s.view_settings.view_transform = "Standard"
try: s.view_settings.look = "Medium High Contrast"
except Exception: pass
w = bpy.data.worlds.new("ceu"); s.world = w; w.use_nodes = True; nt = w.node_tree; bg = nt.nodes["Background"]
tcn = nt.nodes.new("ShaderNodeTexCoord"); sx = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tcn.outputs["Generated"], sx.inputs[0])
cr = nt.nodes.new("ShaderNodeValToRGB"); nt.links.new(sx.outputs[2], cr.inputs[0])
cr.color_ramp.elements[0].position = 0.48; cr.color_ramp.elements[0].color = lin((0.86, 0.94, 1.0))
cr.color_ramp.elements[1].position = 0.75; cr.color_ramp.elements[1].color = lin((0.36, 0.64, 0.98))
nt.links.new(cr.outputs[0], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 0.9
sol = bpy.data.lights.new("sol", "SUN"); sol.energy = 3.2; sol.angle = math.radians(10); sol.color = (1.0, 0.96, 0.90)
so = bpy.data.objects.new("sol", sol); s.collection.objects.link(so); so.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
fill = bpy.data.lights.new("fill", "SUN"); fill.energy = 0.8; fill.angle = math.radians(30); fill.color = (0.85, 0.92, 1.0); fill.use_shadow = False
fo = bpy.data.objects.new("fill", fill); s.collection.objects.link(fo); fo.rotation_euler = (math.radians(70), 0, math.radians(150))
if os.environ.get("VISUAL", "2") != "0":
    visual_nivel2(s, sol)
    cam.data.dof.aperture_fstop = float(os.environ.get("FSTOP", "2.0"))

os.makedirs(SAIDA, exist_ok=True)
s.render.image_settings.file_format = "JPEG"; s.render.image_settings.quality = 92
modo = argv[1] if len(argv) > 1 else "range"
lista = argv[2] if len(argv) > 2 else "1,%d" % NQ
if modo == "quadros":
    for q in [int(x) for x in lista.split(",")]:
        s.frame_set(q); s.render.filepath = os.path.join(SAIDA, "q_%04d.jpg" % q); bpy.ops.render.render(write_still=True)
else:
    a, b = [int(x) for x in lista.split(",")]
    s.frame_start, s.frame_end = a, b; s.frame_step = 1
    s.render.filepath = os.path.join(SAIDA, "f_")
    bpy.ops.render.render(animation=True)
