import bpy

class ahs_maincurve_hide(bpy.types.Operator):
	bl_idname = 'object.ahs_maincurve_hide'
	bl_label = "隠す"
	bl_description = "メインカーブをすべて隠す"
	bl_options = {'REGISTER', 'UNDO'}
	
	is_hide = bpy.props.BoolProperty(name="隠す")
	
	@classmethod
	def poll(cls, context):
		try:
			for ob in context.blend_data.objects:
				if ob.type != 'CURVE': continue
				if ob.data.taper_object and ob.data.bevel_object: break
			else: return False
		except: return False
		return True
	
	def execute(self, context):
		for ob in context.blend_data.objects:
			if ob.type != 'CURVE': continue
			if ob.data.taper_object and ob.data.bevel_object:
				ob.hide = self.is_hide
		return {'FINISHED'}
