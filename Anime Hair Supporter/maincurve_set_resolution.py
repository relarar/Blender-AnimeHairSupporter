import bpy

class ahs_maincurve_set_resolution(bpy.types.Operator):
	bl_idname = 'object.ahs_maincurve_set_resolution'
	bl_label = "解像度を変更"
	bl_options = {'REGISTER', 'UNDO'}
	
	value = bpy.props.IntProperty(name="値", default=12, min=-64, max=64, soft_min=-64, soft_max=64)
	
	items = [
		('ABSOLUTE', "絶対", "", 'PREFERENCES', 1),
		('RELATIVE', "相対", "", 'ZOOMIN', 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="モード", default='ABSOLUTE')
	
	@classmethod
	def poll(cls, context):
		try:
			for ob in context.selected_objects:
				if ob.type != 'CURVE': continue
				break
			else: return False
		except: return False
		return True
	
	def invoke(self, context, event):
		try:
			self.value = context.active_object.data.splines.active.resolution_u
		except: pass
		return self.execute(context)
	
	def execute(self, context):
		for ob in context.selected_objects:
			if ob.type != 'CURVE': continue
			for spline in ob.data.splines:
				if self.mode == 'ABSOLUTE': spline.resolution_u = self.value
				if self.mode == 'RELATIVE': spline.resolution_u += self.value
		return {'FINISHED'}
