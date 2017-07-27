import bpy

class ahs_tapercurve_hide(bpy.types.Operator):
	bl_idname = 'object.ahs_tapercurve_hide'
	bl_label = "隠す"
	bl_options = {'REGISTER', 'UNDO'}
	
	is_bevel = bpy.props.BoolProperty(name="ベベル")
	is_hide = bpy.props.BoolProperty(name="隠す")
	
	@classmethod
	def poll(cls, context):
		try:
			taper_and_bevel_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object] + [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
			if not len(taper_and_bevel_objects): return False
		except: return False
		return True
	
	def execute(self, context):
		if not self.is_bevel: taper_or_bevel_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object]
		else: taper_or_bevel_objects = [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
		
		for ob in taper_or_bevel_objects:
			if not self.is_hide and ob.name not in context.scene.objects.keys():
				context.scene.objects.link(ob)
			elif self.is_hide and ob.name in context.scene.objects.keys():
				context.scene.objects.unlink(ob)
		return {'FINISHED'}
