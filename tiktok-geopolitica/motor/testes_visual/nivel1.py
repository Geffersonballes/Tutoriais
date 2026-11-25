# Nível 1 — luz de contorno + brilho suave + cor mais viva (custo de render ~0)
import bpy, math
s = bpy.context.scene
for o in bpy.data.objects:
    if o.type == "LIGHT" and o.name == "sol": o.data.energy = 3.2; o.data.angle = math.radians(8)
rim = bpy.data.lights.new("contorno", "SUN"); rim.energy = 1.5; rim.color = (1.0, 0.93, 0.80); rim.angle = math.radians(6)
ro = bpy.data.objects.new("contorno", rim); s.collection.objects.link(ro)
ro.rotation_euler = (math.radians(-58), 0, math.radians(25))
s.use_nodes = True; nt = s.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
rl = nt.nodes.new("CompositorNodeRLayers"); comp = nt.nodes.new("CompositorNodeComposite")
gl = nt.nodes.new("CompositorNodeGlare"); gl.glare_type = "FOG_GLOW"; gl.threshold = 0.85; gl.size = 7; gl.mix = -0.75; gl.quality = "MEDIUM"
hs = nt.nodes.new("CompositorNodeHueSat"); hs.inputs["Saturation"].default_value = 1.15; hs.inputs["Value"].default_value = 0.98
nt.links.new(rl.outputs["Image"], gl.inputs["Image"]); nt.links.new(gl.outputs["Image"], hs.inputs["Image"]); nt.links.new(hs.outputs["Image"], comp.inputs["Image"])
