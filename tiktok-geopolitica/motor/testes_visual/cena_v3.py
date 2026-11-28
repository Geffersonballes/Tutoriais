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
def personagem(arquivo, cores, escala=0.55, mangas=False, calca_longa=False, tenis=None, fone=None, sorriso=True, cabeca_nova=False):
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
    rosto = None
    if cabeca_nova:
        H = max((corpo.matrix_world @ v.co).z for v in me.vertices)
        pesc = [corpo.matrix_world @ me.vertices[i].co for i, g in enumerate(dom) if g == "Neck"] or cab
        O = Vector((sum(v.x for v in pesc) / len(pesc), sum(v.y for v in pesc) / len(pesc), mn.z + 0.01))
        # tira a cabeça quadrada do modelo (faces da cabeça, rosto e cabelo); pescoço e corpo ficam
        tirar = {idx.get("Face"), idx.get("Hair")}
        bm = bmesh.new(); bm.from_mesh(me)
        fora = [f for f in bm.faces if f.material_index in tirar or
                max(set(dom[v.index] for v in f.verts), key=[dom[v.index] for v in f.verts].count) == "Head"]
        bmesh.ops.delete(bm, geom=fora, context="FACES"); bm.to_mesh(me); bm.free()
        extras, rosto = cabeca_pixel(O, 0.30 * H / 1.184, fone or (0.55, 0.95, 0.20), cores.get("Hair", (0.16, 0.10, 0.08)))
        fone = None; sorriso = False
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
    if rosto is not None: acao.rosto = rosto
    return arm, acao

def cabeca_pixel(O, k, cor_fone, cor_cabelo):
    """Cabeça do Pixel no mesmo desenho do cartoon.py (cabeça redonda, olhos pretos com brilho, sorriso em arco,
    nariz-bolinha, bochechas, franja escura, fone verde). Coordenadas do cartoon.py (cabeça r=0.58) vezes k,
    a partir do topo do pescoço O. Devolve as peças (para prender no osso Head) e as peças animáveis do rosto."""
    def P(x, y, z): return O + Vector((x, y, z)) * k
    pecas = []; R = {"olhos": [], "brilhos": []}
    def esf(loc, r, cor, esc=(1, 1, 1), seg=32, rough=0.55, emis=0.0, sub=0):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r * k, location=P(*loc))
        o = bpy.context.object; o.scale = esc; o.data.materials.append(mcor(cor, rough, emis))
        for pl in o.data.polygons: pl.use_smooth = True
        if sub: o.modifiers.new("sub", "SUBSURF").levels = sub
        pecas.append(o); return o
    def cone(loc, r, h, rot, cor):
        bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=r * k, radius2=0, depth=h * k, location=P(*loc), rotation=rot)
        o = bpy.context.object; o.data.materials.append(mcor(cor, 0.6))
        for pl in o.data.polygons: pl.use_smooth = True
        pecas.append(o); return o
    def meio_anel(loc, Rm, r, cor, baixo=True, rot=(math.radians(90), 0, 0), seg=32):
        bpy.ops.mesh.primitive_torus_add(major_radius=Rm * k, minor_radius=r * k, major_segments=seg, minor_segments=10, location=P(*loc), rotation=rot)
        o = bpy.context.object; o.data.materials.append(mcor(cor, 0.45))
        bm = bmesh.new(); bm.from_mesh(o.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if (v.co.y > 0.02 * k if baixo else v.co.y < -0.02 * k)], context="VERTS")
        bm.to_mesh(o.data); bm.free()
        for pl in o.data.polygons: pl.use_smooth = True
        pecas.append(o); return o
    PELE_ = (0.96, 0.76, 0.60); PRETO_ = (0.03, 0.03, 0.04)
    esf((0, 0, 0.55), 0.58, PELE_, (1.0, 0.95, 1.02), seg=48, sub=1)                                   # cabeça
    for x in (-0.2, 0.2):
        R["olhos"].append(esf((x, -0.49, 0.62), 0.105, PRETO_, (1, 0.55, 1.25), rough=0.15))          # olhos
        R["brilhos"].append(esf((x + 0.03, -0.555, 0.685), 0.032, (1, 1, 1), rough=0.3, emis=1.5))  # brilho
        R["brilhos"].append(esf((x - 0.035, -0.55, 0.575), 0.014, (1, 1, 1), rough=0.3, emis=1.5))
        bpy.ops.mesh.primitive_cylinder_add(radius=0.024 * k, depth=0.15 * k, vertices=12, location=P(x, -0.52, 0.83),
                                            rotation=(0, math.radians(90 + (6 if x < 0 else -6)), 0))  # sobrancelha suave
        sb = bpy.context.object; sb.data.materials.append(mcor(cor_cabelo, 0.6)); sb.modifiers.new("b", "BEVEL").width = 0.02 * k
        pecas.append(sb)
        esf((x * 1.68, -0.44, 0.43), 0.085, (1.0, 0.55, 0.52), (1, 0.45, 0.65), rough=0.7)            # bochecha
    R["sorriso"] = meio_anel((0, -0.545, 0.47), 0.14, 0.03, (0.40, 0.08, 0.06))
    R["boca"] = esf((0, -0.52, 0.415), 0.105, (0.42, 0.06, 0.08), (1.15, 0.45, 0.04), rough=0.5)      # boca (abre na fala)
    esf((0, -0.575, 0.535), 0.062, (0.93, 0.66, 0.52), sub=0)                                          # nariz-bolinha
    # cabelo: calota + nuca + franja + mechas espetadas
    esf((0, 0.06, 0.86), 0.6, cor_cabelo, (1.03, 1.0, 0.58), seg=32)
    esf((0, 0.17, 0.60), 0.565, cor_cabelo, (1.0, 0.86, 0.92), seg=32)
    for i, x in enumerate((-0.36, -0.18, 0.0, 0.18, 0.36)):
        cone((x, -0.40 + abs(x) * 0.25, 0.97 - abs(x) * 0.12), 0.13, 0.34, (math.radians(150), math.radians(x * 40), 0), cor_cabelo)
    for kk in range(7):
        a = -0.45 + kk * 0.15
        cone((a, 0.08 + abs(a) * 0.2, 1.10 - abs(a) * 0.3), 0.13, 0.40, (math.radians(-25), math.radians(a * 70), 0), cor_cabelo)
    # fone verde: arco por cima + conchas + almofada + microfone
    meio_anel((0, 0.02, 0.60), 0.63, 0.05, cor_fone, baixo=False)
    for x in (-0.62, 0.62):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2 * k, depth=0.15 * k, vertices=24, location=P(x, 0.02, 0.55), rotation=(0, math.radians(90), 0))
        cp = bpy.context.object; cp.data.materials.append(mcor(cor_fone, 0.4)); md = cp.modifiers.new("b", "BEVEL"); md.width = 0.04 * k; md.segments = 3
        for pl in cp.data.polygons: pl.use_smooth = True
        pecas.append(cp)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.13 * k, depth=0.03 * k, vertices=24, location=P(x * 1.13, 0.02, 0.55), rotation=(0, math.radians(90), 0))
        pecas.append(bpy.context.object); bpy.context.object.data.materials.append(mcor((0.12, 0.14, 0.12), 0.5))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022 * k, depth=0.40 * k, vertices=8, location=P(0.52, -0.24, 0.40),
                                        rotation=(math.radians(70), 0, math.radians(30)))
    pecas.append(bpy.context.object); bpy.context.object.data.materials.append(mcor(PRETO_, 0.5))
    alvo = bpy.data.objects.new("alvo_rosto", None); s.collection.objects.link(alvo); alvo.location = P(0, -0.2, 0.58)
    pecas.append(alvo); R["alvo"] = alvo
    return pecas, R

def piscar(R, fr):
    """Piscada: olhos fecham em 2 quadros e abrem em 2."""
    for o in R["olhos"] + R["brilhos"]:
        z0 = o.scale[2]
        for df, f in ((0, 1.0), (2, 0.08), (3, 0.08), (5, 1.0)):
            o.scale[2] = z0 * f; o.keyframe_insert("scale", index=2, frame=fr + df)
        o.scale[2] = z0

def falar(R, f0, f1):
    """Boca abre e fecha de leve (sílabas a cada ~4-5 quadros) e o sorriso sobe junto."""
    b = R["boca"]; z0 = b.scale[2]; fr = f0; k = 0
    b.keyframe_insert("scale", index=2, frame=f0 - 2)
    while fr < f1:
        b.scale[2] = z0 * (14 if k % 2 == 0 else 3); b.keyframe_insert("scale", index=2, frame=fr); fr += 4 + (k % 3 == 0); k += 1
    b.scale[2] = z0; b.keyframe_insert("scale", index=2, frame=f1 + 2)

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
    """Aceno com a mão direita: o braço sobe, o antebraço balança de um lado para o outro com chaves só nos
    extremos (curvas Bezier = movimento suave) e o pulso atrasa e passa um pouco do antebraço (balanço)."""
    ac = bpy.data.actions.new("Aceno_" + arm.name); arm.animation_data.action = ac
    ossos = ["UpperArm.R", "LowerArm.R", "Fist.R"]
    def mirar(nome, alvo):
        pb = arm.pose.bones[nome]; d = (pb.tail - pb.head).normalized()
        q = d.rotation_difference(Vector(alvo).normalized())
        pb.matrix = Matrix.Translation(pb.head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-pb.head) @ pb.matrix
        bpy.context.view_layer.update()
    sobe = 9; meia = (f_fim - f_ini - sobe) / (2 * n)
    chaves = [(0, None)] + [(sobe + i * meia, (1 if i % 2 == 0 else -1) * (0.5 if i == 0 else 1.0)) for i in range(2 * n + 1)]
    for fr, osc in chaves:
        for nm in ossos: arm.pose.bones[nm].rotation_quaternion = (1, 0, 0, 0)
        bpy.context.view_layer.update()
        if osc is None:
            mirar("UpperArm.R", (-0.55, -0.15, -0.8)); mirar("LowerArm.R", (-0.5, -0.1, -0.8))
        else:
            mirar("UpperArm.R", (-0.60 + 0.06 * osc, -0.25, 0.75))
            mirar("LowerArm.R", (-0.10 - 0.55 * osc, -0.30, 0.85))
            mirar("Fist.R", (-0.10 - 0.95 * osc, -0.35, 0.80))           # pulso passa do antebraço
        for nm in ossos: arm.pose.bones[nm].keyframe_insert("rotation_quaternion", frame=f_ini + int(round(fr)))
    for fc in ac.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = "BEZIER"; kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
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
def texto(txt, loc, tam, cor, rot=(math.radians(90), 0, 0)):
    cu = bpy.data.curves.new("txt", "FONT"); cu.body = txt; cu.size = tam; cu.extrude = 0.03; cu.align_x = "CENTER"; cu.align_y = "CENTER"
    o = bpy.data.objects.new("txt", cu); s.collection.objects.link(o); o.location = loc; o.rotation_euler = rot
    o.data.materials.append(mcor(cor, 0.5)); return o

def cidade():
    caixa((10, 0, -0.06), (160, 80, 0.1), (0.55, 0.78, 0.42), bev=False)                         # chão/grama
    caixa((10, 0, 0.0), (160, 7.9, 0.06), (0.33, 0.35, 0.40), 0.8, bev=False)                    # asfalto
    for k in range(-40, 50):                                                                        # faixa central tracejada
        caixa((k * 2.0, 0, 0.035), (1.1, 0.16, 0.01), (0.98, 0.92, 0.55), bev=False)
    for y0 in (-1, 1):
        caixa((10, y0 * 3.55, 0.035), (160, 0.12, 0.01), (0.95, 0.95, 0.95), bev=False)            # linha de borda
    for k in range(8):                                                                              # faixa de pedestres
        caixa((-6.0, -3.2 + k * 0.9, 0.036), (2.6, 0.5, 0.01), (0.97, 0.97, 0.97), bev=False)
    # calçadas + meio-fio
    for y0 in (-1, 1):
        caixa((10, y0 * 6.3, 0.09), (160, 4.6, 0.18), (0.86, 0.82, 0.76), bev=False)
        caixa((10, y0 * 4.05, 0.11), (160, 0.22, 0.22), (0.70, 0.68, 0.66), bev=False)
        for k in range(-20, 30):                                                                    # juntas da calçada
            caixa((k * 2.0, y0 * 6.3, 0.185), (0.05, 4.6, 0.01), (0.74, 0.70, 0.66), bev=False)
    # postes do pacote
    for x in range(-24, 40, 12):
        for y0 in (-1, 1):
            novos, _ = importar_fbx(os.path.join(RUAS, "Streetlight_Single.fbx"))
            for o in novos:
                o.scale = tuple(4.5 * k for k in o.scale); o.location = (x + (6 if y0 > 0 else 0), y0 * 4.6, 0.18)
    # mobiliário genérico: banco, lixeira, hidrante
    for x in (-3.5, 9.0):
        caixa((x, -8.0, 0.45), (1.8, 0.45, 0.08), (0.62, 0.40, 0.22)); caixa((x, -8.2, 0.75), (1.8, 0.06, 0.45), (0.62, 0.40, 0.22))
        for dx in (-0.75, 0.75): caixa((x + dx, -8.0, 0.25), (0.08, 0.4, 0.45), (0.25, 0.27, 0.30))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.9, vertices=16, location=(6.2, -4.5, 0.63))
    bpy.context.object.data.materials.append(mcor((0.20, 0.55, 0.35)))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.7, vertices=12, location=(-1.2, -4.45, 0.53))
    bpy.context.object.data.materials.append(mcor((0.92, 0.22, 0.18)))
    # prédios do outro lado da rua
    cores = [(1.0, 0.72, 0.45), (0.55, 0.78, 0.98), (0.98, 0.58, 0.62), (0.70, 0.88, 0.60), (0.99, 0.88, 0.50),
             (0.78, 0.66, 0.95), (0.55, 0.88, 0.85), (1.0, 0.80, 0.70), (0.95, 0.95, 0.88), (0.62, 0.72, 0.90)]
    lojas = ["CAFÉ", "PADARIA", "LIVROS", "SORVETE", "FLORES", "GAMES", "PIZZA", "MERCADO", "BRINQUEDOS", "SUCOS"]
    random.shuffle(cores); x = -34.0; i = 0
    while x < 46:
        w = random.choice([6.5, 7.5, 8.5, 9.5]); h = random.choice([9.5, 12.5, 15.5, 18.5]); cor = cores[i % len(cores)]
        predio_cartoon(x + w / 2, 9.0 + random.choice([0, 0.3, 0.6]), w, 6.0, h, cor, lojas[i % len(lojas)], i); x += w + 0.25; i += 1
    # segunda fileira bem atrás (silhueta no desfoque)
    x = -40.0
    while x < 52:
        w = random.choice([8, 10, 12]); h = random.choice([20, 24, 28, 32])
        caixa((x + w / 2, 20, h / 2), (w, 6, h), random.choice([(0.70, 0.80, 0.95), (0.80, 0.78, 0.92), (0.76, 0.88, 0.94)]))
        x += w + 1.5
    for x in (-16, 13, 30):
        arvore((x, -7.9))
    for x in (-8, 10, 26):
        arvore((x, 7.4), 0.9)

def predio_cartoon(cx, y0, w, d, h, cor, loja, i):
    escura = tuple(c * 0.78 for c in cor); clara = tuple(min(1, c * 1.12 + 0.05) for c in cor)
    caixa((cx, y0 + d / 2, h / 2), (w, d, h), cor)
    caixa((cx, y0 + d / 2, h + 0.2), (w + 0.4, d + 0.4, 0.4), escura)                                # platibanda
    for sx in (-1, 1): caixa((cx + sx * (w / 2 - 0.15), y0 - 0.05, h / 2), (0.35, 0.2, h), escura, bev=False)   # quinas
    caixa((cx, y0 - 0.08, 3.45), (w, 0.26, 0.22), clara, bev=False)                                  # faixa sobre o térreo
    estilo = i % 3; moldura = random.choice([(0.98, 0.97, 0.94), escura, (0.35, 0.30, 0.28)])
    vidro = (0.40, 0.62, 0.86); acesa = (1.0, 0.85, 0.55); cortina = random.choice([(0.95, 0.45, 0.40), (0.55, 0.75, 0.45), (0.98, 0.90, 0.60)])
    bmf = bmesh.new(); bmv = bmesh.new(); bma = bmesh.new(); bmc = bmesh.new()
    def cubo(bm, dim, loc):
        r = bmesh.ops.create_cube(bm, size=1.0)["verts"]; bmesh.ops.scale(bm, vec=dim, verts=r); bmesh.ops.translate(bm, vec=loc, verts=r)
    ncol = max(2, int(w / 2.0)); passo = (w - 0.6) / ncol
    nand = int((h - 3.6) / 3.0)
    for a in range(nand):
        z = 3.6 + a * 3.0 + 1.6
        if a > 0: cubo(bmf, (w - 0.5, 0.18, 0.14), (cx, y0 - 0.06, z - 1.6))                      # friso entre andares
        for c in range(ncol):
            xx = cx - w / 2 + 0.3 + passo * (c + 0.5)
            larg = passo * (0.58 if estilo != 1 else 0.42); alt = 1.55 if estilo != 2 else 1.85
            cubo(bmf, (larg + 0.22, 0.10, alt + 0.22), (xx, y0 - 0.03, z))                         # moldura
            alvo = bma if random.random() < 0.18 else bmv
            cubo(alvo, (larg, 0.14, alt), (xx, y0 - 0.05, z))                                       # vidro (às vezes aceso)
            cubo(bmf, (larg + 0.36, 0.34, 0.12), (xx, y0 - 0.14, z - alt / 2 - 0.08))                # peitoril
            if random.random() < 0.3: cubo(bmc, (larg * 0.32, 0.16, alt * 0.9), (xx - larg * 0.32, y0 - 0.07, z))   # cortina
            if estilo == 1 and a % 2 == 1:                                                          # sacada
                cubo(bmf, (larg + 0.6, 0.8, 0.12), (xx, y0 - 0.4, z - alt / 2 - 0.1))
                cubo(bmf, (larg + 0.6, 0.05, 0.6), (xx, y0 - 0.8, z - alt / 2 + 0.2))
    for bm, nome, m in ((bmf, "moldura", mcor(moldura)), (bmv, "vidro", mcor(vidro, 0.12, 0.25)),
                        (bma, "acesa", mcor(acesa, 0.3, 0.6)), (bmc, "cortina", mcor(cortina))):
        me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
        if len(me.vertices):
            o = bpy.data.objects.new(nome, me); s.collection.objects.link(o); me.materials.append(m)
    # térreo: vitrine + porta + toldo listrado + placa genérica (sem marca)
    caixa((cx - w * 0.08, y0 - 0.05, 1.55), (w * 0.55, 0.14, 2.1), (0.36, 0.62, 0.86), 0.12, 0.35)
    caixa((cx - w * 0.08, y0 - 0.02, 1.55), (w * 0.55 + 0.25, 0.1, 2.35), moldura)
    caixa((cx + w * 0.34, y0 - 0.05, 1.3), (1.2, 0.16, 2.5), random.choice([(0.45, 0.28, 0.18), (0.25, 0.45, 0.65), (0.75, 0.25, 0.25)]))
    toldo = random.choice([(0.95, 0.30, 0.28), (0.20, 0.65, 0.45), (0.25, 0.45, 0.90), (0.98, 0.72, 0.15), (0.70, 0.35, 0.80)])
    n = 6
    for k in range(n):
        tw = w * 0.62 / n
        t = caixa((cx - w * 0.08 - w * 0.31 + tw * (k + 0.5), y0 - 0.7, 3.0), (tw, 1.4, 0.12), toldo if k % 2 == 0 else (0.98, 0.97, 0.94), bev=False)
        t.rotation_euler[0] = math.radians(-18)
    pw = min(w * 0.75, 0.48 * len(loja) + 0.9)
    caixa((cx - w * 0.08, y0 - 0.18, 4.15), (pw, 0.16, 0.85), toldo)
    texto(loja, (cx - w * 0.08, y0 - 0.30, 4.15), 0.55 * min(1.0, (pw - 0.6) / (0.48 * len(loja))), (0.99, 0.98, 0.95))
    # telhado: caixa de ar-condicionado / caixa d'água
    if random.random() < 0.6: caixa((cx - w * 0.2, y0 + d * 0.6, h + 0.8), (1.4, 1.0, 0.8), (0.82, 0.84, 0.86))
    else:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=1.6, vertices=16, location=(cx + w * 0.2, y0 + d * 0.6, h + 1.2))
        bpy.context.object.data.materials.append(mcor((0.55, 0.40, 0.30)))

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


# ---------------------------------------------------------------- montagem
cidade()

# Pixel
PX_Y = -6.6
px, px_acao = personagem("Casual2_Male", {"Shirt": (1.0, 0.48, 0.12), "Pants": (0.17, 0.21, 0.36), "Hair": (0.16, 0.10, 0.08),
                                          "Belt": (0.85, 0.36, 0.06)},
                         mangas=True, calca_longa=True, tenis=(0.97, 0.97, 0.97), fone=(0.55, 0.95, 0.20), cabeca_nova=True)
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
ROSTO = px_acao.rosto
for t in (1.3, 3.55, 5.9): piscar(ROSTO, F(t))          # piscadas
falar(ROSTO, F(0.5), F(1.1)); falar(ROSTO, F(4.0), F(4.7))   # "fala" curtinha andando e no "oi!" do aceno

# pedestres
p1, a1 = personagem("Casual_Female", {"Shirt": (0.30, 0.75, 0.95), "Pants": (0.95, 0.85, 0.35), "Hair": (0.55, 0.30, 0.12)},
                    calca_longa=False, tenis=(0.95, 0.35, 0.40))
andar(p1, a1("Walk"), 16, 6.2, -16, 1, math.radians(-90))
p2, a2 = personagem("Casual3_Male", {"Shirt": (0.55, 0.85, 0.40), "Pants": (0.30, 0.32, 0.40), "Hair": (0.12, 0.08, 0.06)},
                    mangas=False, tenis=(0.25, 0.25, 0.30))
andar(p2, a2("Walk"), -12, 6.8, 18, 1, math.radians(90))
p3, a3 = personagem("Suit_Female", {"Shirt": (0.96, 0.96, 0.96), "Black": (0.25, 0.22, 0.45), "Hair": (0.20, 0.12, 0.08)},
                    tenis=(0.15, 0.12, 0.25))
andar(p3, a3("Walk"), 5, -4.9, -14, 1, math.radians(-90))

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
for fr, ax, cx_, cy_, cz_, az in ((1, x_ini + 0.3, x_ini + 1.5, -11.6, 2.3, 1.2), (f_para, x_para, x_para + 1.1, -10.8, 2.15, 1.22),
                                  (F(5.3), x_para + 0.1, x_para + 0.6, -10.3, 2.0, 1.25), (NQ, x_para + 0.1, x_para + 0.4, -10.0, 1.95, 1.3)):
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
if modo == "rosto":                     # close-ups do rosto (imagens paradas)
    ar = ROSTO["alvo"]; tc.target = ar; cam.data.lens = 55
    if cam.data.dof.use_dof: cam.data.dof.focus_object = ar; cam.data.dof.aperture_fstop = 2.8
    cam.animation_data_clear()
    for q in [int(x) for x in lista.split(",")]:
        s.frame_set(q); hp = ar.matrix_world.translation.copy()
        rz = px.matrix_world.to_euler().z; frente = Vector((math.sin(rz), -math.cos(rz), 0))
        cam.location = hp + frente * 2.3 + Vector((0.25, 0, 0.12)); bpy.context.view_layer.update()
        s.render.filepath = os.path.join(SAIDA, "rosto_%04d.jpg" % q); bpy.ops.render.render(write_still=True)
elif modo == "quadros":
    for q in [int(x) for x in lista.split(",")]:
        s.frame_set(q); s.render.filepath = os.path.join(SAIDA, "q_%04d.jpg" % q); bpy.ops.render.render(write_still=True)
else:
    a, b = [int(x) for x in lista.split(",")]
    s.frame_start, s.frame_end = a, b; s.frame_step = 1
    s.render.filepath = os.path.join(SAIDA, "f_")
    bpy.ops.render.render(animation=True)
