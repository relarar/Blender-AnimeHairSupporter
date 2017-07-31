import bpy, mathutils

class ahs_maincurve_extra_deform(bpy.types.Operator):
	bl_idname = 'object.ahs_maincurve_extra_deform'
	bl_label = "余剰変形"
	bl_description = "選択中のカーブを過剰に変形、もしくは緩やかにする"
	bl_options = {'REGISTER', 'UNDO'}
	
	order_u = bpy.props.IntProperty(name="次数", default=3, min=3, max=6, soft_min=3, soft_max=6)
	extra_deform_multi = bpy.props.IntProperty(name="余剰変形率", default=50, min=-100, max=200, soft_min=-100, soft_max=200, subtype='PERCENTAGE')
	
	@classmethod
	def poll(cls, context):
		try:
			for ob in context.selected_objects:
				if ob.type != 'CURVE': continue
				break
			else: return False
		except: return False
		return True
	
	def draw(self, context):
		self.layout.prop(self, 'order_u', slider=True)
		self.layout.prop(self, 'extra_deform_multi', slider=True)
	
	def execute(self, context):
		for ob in context.selected_objects:
			if ob.type != 'CURVE': continue
			
			curve = ob.data
			if not curve.splines.active: continue
			
			for spline in curve.splines:
				spline.order_u = self.order_u
				if len(spline.points) < 3: continue
				for index, point in enumerate(spline.points):
					if index == 0 or len(spline.points) - 1 == index: continue
					
					co = mathutils.Vector(point.co[:3])
					prev_line = co - mathutils.Vector(spline.points[index - 1].co[:3])
					next_line = co - mathutils.Vector(spline.points[index + 1].co[:3])
					
					plus_co = prev_line.lerp(next_line, 0.5) * (self.extra_deform_multi * 0.01)
					point.co = list(co + plus_co) + [point.co.w]
		
		return {'FINISHED'}
