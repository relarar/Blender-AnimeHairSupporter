import bpy

class ahs_tapercurve_hide(bpy.types.Operator):
	bl_idname = 'object.ahs_tapercurve_hide'
	bl_label = "隠す"
	bl_description = "テーパー/ベベルをすべて隠す/表示"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('TAPER', "テーパー", "", 'CURVE_NCURVE', 1),
		('BEVEL', "ベベル", "", 'SURFACE_NCIRCLE', 2),
		('BOTH', "両方", "", 'ARROW_LEFTRIGHT', 3),
		]
	mode = bpy.props.EnumProperty(items=items, name="モード", default='BOTH')
	
	is_hide = bpy.props.BoolProperty(name="隠す")
	
	@classmethod
	def poll(cls, context):
		try:
			taper_and_bevel_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object] + [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
			if not len(taper_and_bevel_objects): return False
		except: return False
		return True
	
	def execute(self, context):
		if self.mode == 'TAPER': taper_or_bevel_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object]
		elif self.mode == 'BEVEL': taper_or_bevel_objects = [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
		else: taper_or_bevel_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object] + [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
		
		for ob in taper_or_bevel_objects:
			ob.hide = self.is_hide
		return {'FINISHED'}
