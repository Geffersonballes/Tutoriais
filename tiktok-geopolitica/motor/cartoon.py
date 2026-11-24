"""Estilo C (cartoon 3D) da série 2 'Fase por Fase' + mascote ORIGINAL 'Pixel'.
Inspiração de ESTRUTURA (cores vivas, personagem em primeiro plano, cenas fechadas), nunca cópia de
personagem/marca de outro canal: o Pixel é um gamer de moletom laranja, fone verde-limão e cabelo espetado."""
import bpy, math
from mathutils import Vector
from lowpoly import *
from lowpoly import _id, _lin, _mats

PELE = (0.96, 0.76, 0.60, 1); MOLETOM = (1.0, 0.48, 0.12, 1); CALCA = (0.20, 0.24, 0.32, 1)
FONE = (0.55, 0.95, 0.20, 1); CABELO = (0.16, 0.10, 0.08, 1); TENIS = (0.97, 0.97, 0.97, 1); PRETO = (0.03, 0.03, 0.04, 1)

def liso(ob):
    for o in todos(ob):
        if o.type == "MESH":
            for p in o.data.polygons: p.use_smooth = True
    return ob

def capsula(nome, loc, r, h, cor, unico=None):
    """Cilindro com pontas arredondadas (corpo de brinquedo)."""
    c = cilindro(nome, loc, r, h, cor, seg=20, unico=unico)
    for z in (h / 2, -h / 2):
        e = esfera(_id("cap"), (0, 0, z), r, cor, sub=3, unico=unico); filho(c, e); e.location = (0, 0, z)
    return liso(c)

def sorriso(nome, R=0.14, r=0.03, cor=(0.40, 0.08, 0.06, 1)):
    """Meio anel (só a metade de baixo) = sorriso."""
    import bmesh
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=32, minor_segments=8, location=(0, 0, 0))
    ob = bpy.context.active_object; ob.name = nome
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > 0.02], context="VERTS")
    bm.to_mesh(ob.data); bm.free()
    ob.rotation_euler = (math.radians(90), 0, 0)
    ob.data.materials.append(mat(cor)); return liso(ob)

def pixel(nome, loc=(0, 0, 0), moletom=MOLETOM, calca=CALCA, escala=1.0):
    """Mascote da série. Retorna dict com o objeto raiz e os pivôs de animação."""
    raiz = vazio(nome, loc); raiz.scale = (escala,) * 3
    P = {"raiz": raiz}
    # pernas + tênis
    for lado, x in (("E", -0.26), ("D", 0.26)):
        q = vazio(f"{nome}_quadril{lado}", (x, 0, 1.05)); filho(raiz, q)
        perna = capsula(_id("perna"), (0, 0, -0.45), 0.2, 0.6, calca); filho(q, perna); perna.location = (0, 0, -0.45)
        ten = esfera(_id("tenis"), (0, -0.08, -0.95), 0.24, TENIS, sub=3); ten.scale = (1, 1.45, 0.6); filho(q, ten); ten.location = (0, -0.08, -0.95); liso(ten)
        P["perna" + lado] = q
    # tronco (moletom com capuz nas costas e bolso)
    tronco = capsula(_id("tronco"), (0, 0, 1.55), 0.46, 0.55, moletom); filho(raiz, tronco); tronco.location = (0, 0, 1.55)
    tronco.scale = (1.0, 0.78, 1.0)
    capuz = esfera(_id("capuz"), (0, 0.32, 0.45), 0.36, moletom, sub=3); capuz.scale = (1.2, 0.7, 0.6); filho(tronco, capuz); capuz.location = (0, 0.34, 0.42); liso(capuz)
    bolso = caixa(_id("bolso"), (0, -0.43, -0.12), (0.52, 0.06, 0.2), tuple(c * 0.85 for c in moletom[:3]) + (1,)); filho(tronco, bolso); bolso.location = (0, -0.44, -0.12)
    P["tronco"] = tronco
    # braços com ombro e cotovelo
    for lado, x in (("E", -0.58), ("D", 0.58)):
        ombro = vazio(f"{nome}_ombro{lado}", (x, 0, 1.92)); filho(raiz, ombro)
        sup = capsula(_id("braco"), (0, 0, -0.25), 0.14, 0.32, moletom); filho(ombro, sup); sup.location = (0, 0, -0.25)
        cot = vazio(f"{nome}_cotovelo{lado}", (0, 0, -0.52)); filho(ombro, cot)
        ant = capsula(_id("antebraco"), (0, 0, -0.22), 0.12, 0.26, PELE); filho(cot, ant); ant.location = (0, 0, -0.22)
        mao = esfera(_id("mao"), (0, 0, -0.5), 0.16, PELE, sub=3); filho(cot, mao); mao.location = (0, 0, -0.5); liso(mao)
        ombro.rotation_euler = (0, math.radians(-8 if lado == "D" else 8), 0)
        P["ombro" + lado] = ombro; P["cotovelo" + lado] = cot
    # cabeça grande (proporção de brinquedo)
    pesc = vazio(f"{nome}_pescoco", (0, 0, 2.05)); filho(raiz, pesc); P["cabeca"] = pesc
    cab = esfera(_id("cabeca"), (0, 0, 0.55), 0.58, PELE, sub=4); filho(pesc, cab); cab.location = (0, 0, 0.55); cab.scale = (1.0, 0.95, 1.02); liso(cab)
    for x in (-0.2, 0.2):   # olhos com brilho
        o = esfera(_id("olho"), (x, -0.5, 0.62), 0.085, PRETO, sub=3); o.scale = (1, 0.6, 1.25); filho(pesc, o); o.location = (x, -0.5, 0.62); liso(o)
        b = esfera(_id("brilho"), (x + 0.025, -0.56, 0.67), 0.025, (1, 1, 1, 1), sub=2); filho(pesc, b); b.location = (x + 0.025, -0.555, 0.67)
        s = caixa(_id("sobr"), (x, -0.5, 0.8), (0.16, 0.04, 0.035), CABELO); filho(pesc, s); s.location = (x, -0.51, 0.81)
        s.rotation_euler = (0, math.radians(-10 if x < 0 else 10), 0)
    boca = sorriso(_id("boca")); filho(pesc, boca); boca.location = (0, -0.53, 0.47)
    nariz = esfera(_id("nariz"), (0, -0.58, 0.53), 0.06, (0.93, 0.66, 0.52, 1), sub=2); filho(pesc, nariz); nariz.location = (0, -0.57, 0.53); liso(nariz)
    # cabelo espetado
    for k in range(7):
        a = -0.45 + k * 0.15
        sp = cilindro(_id("mecha"), (0, 0, 0), 0.14, 0.42, CABELO, seg=6, r2=0.0); filho(pesc, sp)
        sp.location = (a, 0.05 + abs(a) * 0.2, 1.08 - abs(a) * 0.3); sp.rotation_euler = (math.radians(-25), math.radians(a * 70), 0)
    topo = esfera(_id("cabelo"), (0, 0.06, 0.82), 0.56, CABELO, sub=3); topo.scale = (1.02, 0.98, 0.55); filho(pesc, topo); topo.location = (0, 0.06, 0.86); liso(topo)
    # fone de ouvido (marca registrada do Pixel)
    arco = anel(_id("arcoFone"), (0, 0, 0.62), 0.62, 0.05, FONE, seg=32); filho(pesc, arco); arco.location = (0, 0, 0.62); arco.rotation_euler = (math.radians(90), 0, 0); arco.scale = (1.0, 1.0, 1.0)
    for x in (-0.6, 0.6):
        cp = cilindro(_id("concha"), (0, 0, 0), 0.2, 0.14, FONE, seg=20); cp.rotation_euler = (0, math.radians(90), 0); filho(pesc, cp); cp.location = (x, 0, 0.55); liso(cp)
    mic = cilindro(_id("mic"), (0, 0, 0), 0.025, 0.42, PRETO, seg=6); filho(pesc, mic); mic.location = (-0.5, -0.25, 0.42); mic.rotation_euler = (math.radians(70), 0, math.radians(-30))
    return P

# ---------- gestos (chaves nos pivôs) ----------
def _rot(ob, t, rx=0, ry=0, rz=0):
    ob.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz)); ob.keyframe_insert("rotation_euler", frame=f(t))

def repouso(P, t):
    _rot(P["ombroE"], t, 0, 8); _rot(P["ombroD"], t, 0, -8); _rot(P["cotoveloE"], t, -10); _rot(P["cotoveloD"], t, -10)
    _rot(P["cabeca"], t)

def acenar(P, t, dur=1.4):
    repouso(P, t - 0.01)
    _rot(P["ombroD"], t + 0.25, 0, -150); _rot(P["cotoveloD"], t + 0.25, 0, 0, 0)
    for k in range(3):
        _rot(P["cotoveloD"], t + 0.4 + k * 0.3, 0, 30); _rot(P["cotoveloD"], t + 0.55 + k * 0.3, 0, -25)
    _rot(P["cabeca"], t + 0.3, 0, -8, 0)
    repouso(P, t + dur)

def apontar(P, t, dur=1.6, lado="D", alto=60):
    s = 1 if lado == "D" else -1
    repouso(P, t - 0.01)
    _rot(P["ombro" + lado], t + 0.25, -alto, -s * 60); _rot(P["cotovelo" + lado], t + 0.25, -5)
    _rot(P["cabeca"], t + 0.3, 0, 0, s * -20)
    repouso(P, t + dur)

def comemorar(P, t, dur=1.4):
    repouso(P, t - 0.01)
    for lado, s in (("E", -1), ("D", 1)):
        _rot(P["ombro" + lado], t + 0.2, 0, -s * 165); _rot(P["cotovelo" + lado], t + 0.2, -15)
    raiz = P["raiz"]; z0 = raiz.location.z
    for k, dz in enumerate((0, 0.5, 0, 0.35, 0)):
        raiz.location.z = z0 + dz; raiz.keyframe_insert("location", index=2, frame=f(t + 0.15 + k * 0.18))
    repouso(P, t + dur)

def pensar(P, t, dur=1.8):
    repouso(P, t - 0.01)
    _rot(P["ombroD"], t + 0.25, -70, 30); _rot(P["cotoveloD"], t + 0.25, -120)
    _rot(P["cabeca"], t + 0.3, 8, 12, 0)
    repouso(P, t + dur)

def espanto(P, t, dur=1.2):
    repouso(P, t - 0.01)
    for lado, s in (("E", -1), ("D", 1)):
        _rot(P["ombro" + lado], t + 0.12, -20, -s * 60); _rot(P["cotovelo" + lado], t + 0.12, -90)
    _rot(P["cabeca"], t + 0.12, -12)
    repouso(P, t + dur)

def respirar(P, t0, t1):
    """Balanço sutil contínuo (o personagem nunca fica congelado)."""
    tr = P["tronco"]; k = 0; t = t0
    while t < t1:
        tr.scale = (1.0, 0.78, 1.0 + (0.025 if k % 2 else 0)); tr.keyframe_insert("scale", frame=f(t)); t += 0.9; k += 1

def hud(nome, loc, cor=(0.10, 0.12, 0.18, 1), w=2.6, h=1.2):
    """Placa de HUD (tipo 'ALTURA 3.860 m') para ficar no cenário; o número vai no grafismo 2D."""
    p = caixa(nome, loc, (w, 0.12, h), cor)
    filho(p, caixa(_id("hudB"), (0, -0.07, 0), (w * 0.94, 0.02, h * 0.86), (0.20, 0.95, 0.55, 1)))
    return p


# ---------- câmera fechada (backlog #1: nada de chão vazio) ----------
PLANOS = {"close": (4.6, 0.25, 0.0), "medio": (6.5, 0.6, 0.1), "geral": (8.5, 1.4, 0.3)}
def camera_cartoon(lens=24):
    """Cria câmera + alvo com TRACK_TO. Retorna (cam, alvo, cam_key, plano)."""
    scn = bpy.context.scene
    cd = bpy.data.cameras.new("cam"); cd.lens = lens; cd.clip_end = 2000
    cam = bpy.data.objects.new("cam", cd); scn.collection.objects.link(cam); scn.camera = cam
    alvo = vazio("alvo")
    tc = cam.constraints.new("TRACK_TO"); tc.target = alvo; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    def cam_key(t, loc, tgt):
        for ob, v in ((cam, loc), (alvo, tgt)):
            ob.location = v; ob.keyframe_insert("location", frame=f(t))
    def plano(t, centro, tipo="medio", lado=0.0, altura=1.8):
        """Enquadramento padrão olhando de -Y para 'centro' (x, y): close ≈ 4,6 m, médio ≈ 6,5 m, geral ≈ 8,5 m.
        A câmera fica quase na altura do alvo, levemente acima, para o chão não ocupar a metade de baixo."""
        d, dz, dzt = PLANOS[tipo]; x, y = centro[0], centro[1]
        cam_key(t, (x + lado, y - d, altura + dz), (x, y, altura + dzt))
    return cam, alvo, cam_key, plano

# ---------- render cartoon ----------
def modo_cartoon(samples=6, res=(540, 960), ceu=((0.36, 0.64, 0.98), (0.80, 0.92, 1.0))):
    """Estilo C: EEVEE, céu em degradê, sol branco suave + luz de preenchimento, cores saturadas e foscas,
    quinas bem arredondadas, sem desfoque de maquete."""
    s = bpy.context.scene
    s.render.engine = "BLENDER_EEVEE_NEXT"
    s.render.resolution_x, s.render.resolution_y = res
    s.eevee.taa_render_samples = samples
    for k, v in (("use_shadows", True), ("use_raytracing", True), ("shadow_ray_count", 1), ("shadow_step_count", 4),
                 ("use_gtao", True), ("gtao_distance", 0.6)):
        try: setattr(s.eevee, k, v)
        except Exception: pass
    s.view_settings.view_transform = "Standard"; s.view_settings.look = "None"; s.view_settings.exposure = 0.0
    try: s.view_settings.look = "Medium High Contrast"
    except Exception: pass
    for m in bpy.data.materials:
        m.use_nodes = True
        b = m.node_tree.nodes.get("Principled BSDF")
        if not b: continue
        c = m.diffuse_color
        b.inputs["Base Color"].default_value = _lin(c)
        b.inputs["Roughness"].default_value = 0.62
        try: b.inputs["Specular IOR Level"].default_value = 0.25
        except Exception: pass
        ad = m.animation_data
        if ad and ad.action:
            for fc in ad.action.fcurves:
                if fc.data_path == "diffuse_color" and fc.array_index < 3:
                    for kp in fc.keyframe_points:
                        v = list(b.inputs["Base Color"].default_value); v[fc.array_index] = _lin((kp.co[1],) * 3)[0]
                        b.inputs["Base Color"].default_value = v
                        b.inputs["Base Color"].keyframe_insert("default_value", frame=kp.co[0])
    for o in bpy.data.objects:
        if o.type == "MESH" and len(o.data.polygons) <= 12 and max(o.dimensions) < 60:
            md = o.modifiers.new("bevel", "BEVEL"); md.width = min(0.25, min(o.dimensions) * 0.18 + 0.001); md.segments = 3
            for p in o.data.polygons: p.use_smooth = True
            try: o.data.shade_auto_smooth = True
            except Exception: pass
    # céu degradê
    w = s.world; w.use_nodes = True; nt = w.node_tree; bg = nt.nodes.get("Background")
    tc = nt.nodes.new("ShaderNodeTexCoord"); sx = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sx.inputs[0])
    cr = nt.nodes.new("ShaderNodeValToRGB"); nt.links.new(sx.outputs[2], cr.inputs[0])
    cr.color_ramp.elements[0].position = 0.45; cr.color_ramp.elements[0].color = _lin(ceu[1] + (1,))
    cr.color_ramp.elements[1].position = 0.75; cr.color_ramp.elements[1].color = _lin(ceu[0] + (1,))
    nt.links.new(cr.outputs[0], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 0.9
    sol = bpy.data.lights.new("sol", "SUN"); sol.energy = 3.2; sol.angle = math.radians(12); sol.color = (1.0, 0.96, 0.90)
    so = bpy.data.objects.new("sol", sol); bpy.context.collection.objects.link(so)
    so.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
    fill = bpy.data.lights.new("fill", "SUN"); fill.energy = 0.8; fill.angle = math.radians(30); fill.color = (0.85, 0.92, 1.0); fill.use_shadow = False
    fo = bpy.data.objects.new("fill", fill); bpy.context.collection.objects.link(fo); fo.rotation_euler = (math.radians(70), 0, math.radians(150))
    cam = s.camera
    if cam is not None: cam.data.dof.use_dof = False
    return bg, sol
