# Nível 2 — nível 1 + contorno de desenho (casca invertida) + fundo desfocado
import bpy, os
exec(open(os.path.join(os.path.dirname(os.environ["DBG"]), "nivel1.py")).read())
lin = bpy.data.materials.new("linha_contorno"); lin.use_nodes = True; ln = lin.node_tree
for n in list(ln.nodes):
    if n.bl_idname != "ShaderNodeOutputMaterial": ln.nodes.remove(n)
out = ln.nodes[0]; em = ln.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.02, 0.02, 0.05, 1)
tr = ln.nodes.new("ShaderNodeBsdfTransparent"); lp = ln.nodes.new("ShaderNodeLightPath"); mx = ln.nodes.new("ShaderNodeMixShader")
ln.links.new(lp.outputs["Is Shadow Ray"], mx.inputs[0]); ln.links.new(em.outputs[0], mx.inputs[1]); ln.links.new(tr.outputs[0], mx.inputs[2]); ln.links.new(mx.outputs[0], out.inputs["Surface"])
lin.use_backface_culling = True
try: lin.use_backface_culling_shadow = True
except Exception: pass
try: lin.use_transparent_shadow = True
except Exception: pass
for o in list(bpy.data.objects):
    if o.type != "MESH" or max(o.dimensions) > 25 or max(o.dimensions) < 0.05: continue
    sc = max(abs(v) for v in o.matrix_world.to_scale()) or 1
    o.data.materials.append(lin); idx = len(o.data.materials) - 1
    md = o.modifiers.new("linha", "SOLIDIFY"); md.thickness = 0.028 / sc; md.offset = 1; md.use_flip_normals = True
    md.use_rim = False; md.material_offset = idx
cam = bpy.context.scene.camera
cam.data.dof.use_dof = True; cam.data.dof.focus_object = alvo; cam.data.dof.aperture_fstop = 1.2
