import bpy, mathutils

class ahs_maincurve_surplus_transform(bpy.types.Operator):
	bl_idname = 'object.ahs_maincurve_surplus_transform'
	bl_label = "余剰変形"
	bl_options = {'REGISTER', 'UNDO'}
	
	surplus_transform_multi = bpy.props.FloatProperty(name="余剰変形", default=0.5, min=-1, max=2, soft_min=-1, soft_max=2, step=3, precision=2)
	
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
		self.layout.prop(self, 'surplus_transform_multi', slider=True)
	
	def execute(self, context):
		for ob in context.selected_objects:
			if ob.type != 'CURVE': continue
			
			curve = ob.data
			if not curve.splines.active: continue
			
			for spline in curve.splines:
				if len(spline.points) < 3: continue
				for index, point in enumerate(spline.points):
					if index == 0 or len(spline.points) - 1 == index: continue
					
					co = mathutils.Vector(point.co[:3])
					prev_line = co - mathutils.Vector(spline.points[index - 1].co[:3])
					next_line = co - mathutils.Vector(spline.points[index + 1].co[:3])
					
					plus_co = prev_line.lerp(next_line, 0.5) * self.surplus_transform_multi
					point.co = list(co + plus_co) + [point.co.w]
		
		return {'FINISHED'}
