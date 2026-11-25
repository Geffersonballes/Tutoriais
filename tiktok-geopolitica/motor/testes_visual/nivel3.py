# Nível 3 — nível 2 + resolução maior (720x1280) + vinheta suave
import bpy, os
exec(open(os.path.join(os.path.dirname(os.environ["DBG"]), "nivel2.py")).read())
s = bpy.context.scene; s.render.resolution_x, s.render.resolution_y = 720, 1280; s.eevee.taa_render_samples = 16
nt = s.node_tree; hs = [n for n in nt.nodes if n.bl_idname == "CompositorNodeHueSat"][0]; comp = [n for n in nt.nodes if n.bl_idname == "CompositorNodeComposite"][0]
em = nt.nodes.new("CompositorNodeEllipseMask"); em.width = 1.1; em.height = 1.05
bl = nt.nodes.new("CompositorNodeBlur"); bl.size_x = bl.size_y = 200; bl.use_relative = False
nt.links.new(em.outputs["Mask"], bl.inputs["Image"])
mx = nt.nodes.new("CompositorNodeMixRGB"); mx.blend_type = "MULTIPLY"
mr = nt.nodes.new("CompositorNodeMapRange"); mr.inputs["To Min"].default_value = 0.78
nt.links.new(bl.outputs["Image"], mr.inputs["Value"]); nt.links.new(mr.outputs["Value"], mx.inputs["Fac"])
mx.inputs[2].default_value = (0, 0, 0, 1)
# fac alto = imagem original; inverte: Mix(fac) entre preto e imagem
nt.links.new(hs.outputs["Image"], mx.inputs[2]); mx.blend_type = "MIX"; mx.inputs[1].default_value = (0, 0, 0, 1)
nt.links.new(mx.outputs["Image"], comp.inputs["Image"])
