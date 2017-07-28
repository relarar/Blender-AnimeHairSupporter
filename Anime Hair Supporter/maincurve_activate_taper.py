import bpy

class ahs_maincurve_activate_taper(bpy.types.Operator):
	bl_idname = 'object.ahs_maincurve_activate_taper'
	bl_label = "テーパー/ベベルをアクティブ化"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('TAPER', "テーパー", "", 'CURVE_NCURVE', 1),
		('BEVEL', "ベベル", "", 'SURFACE_NCIRCLE', 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="モード")
	
	@classmethod
	def poll(cls, context):
		try:
			curve = context.active_object.data
			if not curve.taper_object and not curve.bevel_object: return False
		except: return False
		return True
	
	def execute(self, context):
		ob, curve = context.active_object, context.active_object.data
		
		if   self.mode == 'TAPER': target_ob = curve.taper_object
		elif self.mode == 'BEVEL': target_ob = curve.bevel_object
		
		if not target_ob: return {'CANCELLED'}
		
		for o in context.blend_data.objects: o.select = False
		target_ob.select, target_ob.hide = True, False
		context.scene.objects.active = target_ob
		
		return {'FINISHED'}
