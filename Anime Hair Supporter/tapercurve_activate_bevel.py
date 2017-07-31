import bpy

class ahs_tapercurve_activate_bevel(bpy.types.Operator):
	bl_idname = 'object.ahs_tapercurve_activate_bevel'
	bl_label = "ベベルへ"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('TAPER', "テーパー", "", 'CURVE_NCURVE', 1),
		('BEVEL', "ベベル", "", 'SURFACE_NCIRCLE', 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="モード")
	
	@classmethod
	def poll(cls, context):
		try:
			taper_and_bevel_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object] + [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
			if context.active_object not in taper_and_bevel_objects: return False
		except: return False
		return True
	
	def execute(self, context):
		ob = context.active_object
		
		target_ob = None
		for o in context.blend_data.objects:
			if o.type != 'CURVE': continue
			if o.data.taper_object == ob and self.mode == 'BEVEL':
				target_ob = o.data.bevel_object
				break
			if o.data.bevel_object == ob and self.mode == 'TAPER':
				target_ob = o.data.taper_object
				break
		if not target_ob: return {'CANCELLED'}
		
		for o in context.blend_data.objects: o.select = False
		target_ob.select = True
		context.scene.objects.active = target_ob
		
		return {'FINISHED'}
