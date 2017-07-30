import bpy

class ahs_maincurve_set_order(bpy.types.Operator):
	bl_idname = 'object.ahs_maincurve_set_order'
	bl_label = "次数を変更"
	bl_options = {'REGISTER', 'UNDO'}
	
	value = bpy.props.IntProperty(name="値", default=3, min=-6, max=6, soft_min=-6, soft_max=6)
	
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
			self.value = context.active_object.data.splines.active.order_u
		except: pass
		return self.execute(context)
	
	def execute(self, context):
		for ob in context.selected_objects:
			if ob.type != 'CURVE': continue
			for spline in ob.data.splines:
				if self.mode == 'ABSOLUTE': spline.order_u = self.value
				if self.mode == 'RELATIVE': spline.order_u += self.value
		return {'FINISHED'}
