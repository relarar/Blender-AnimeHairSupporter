import bpy, math, mathutils

class ahs_maincurve_gradation_tilt(bpy.types.Operator):
	bl_idname = 'object.ahs_maincurve_gradation_tilt'
	bl_label = "グラデーションひねり"
	bl_options = {'REGISTER', 'UNDO'}
	
	begin_ratio = bpy.props.IntProperty(name="始点", default=33, min=0, max=100, soft_min=0, soft_max=100, subtype='PERCENTAGE')
	begin_tilt = bpy.props.FloatProperty(name="始点のひねり", default=0, min=math.radians(-360), max=math.radians(360), soft_min=math.radians(-360), soft_max=math.radians(360), step=3, precision=0, subtype='ANGLE', unit='ROTATION')
	
	end_ratio = bpy.props.IntProperty(name="終点", default=100, min=0, max=100, soft_min=0, soft_max=100, subtype='PERCENTAGE')
	end_tilt = bpy.props.FloatProperty(name="終点のひねり", default=0, min=math.radians(-360), max=math.radians(360), soft_min=math.radians(-360), soft_max=math.radians(360), step=3, precision=0, subtype='ANGLE', unit='ROTATION')
	
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
	
	def draw(self, context):
		column = self.layout.column(align=True)
		column.prop(self, 'begin_ratio', slider=True)
		column.prop(self, 'begin_tilt', slider=True)
		
		column = self.layout.column(align=True)
		column.prop(self, 'end_ratio', slider=True)
		column.prop(self, 'end_tilt', slider=True)
		
		self.layout.prop(self, 'mode')
	
	def execute(self, context):
		begin_ratio, end_ratio = self.begin_ratio * 0.01, self.end_ratio * 0.01
		
		for ob in context.selected_objects:
			if ob.type != 'CURVE': continue
			curve = ob.data
			if not len(curve.splines): continue
			
			for spline in curve.splines:
				if len(spline.points) < 2: continue
				
				total_length = 0.0
				for index, point in enumerate(spline.points):
					if index == 0: continue
					diff_co = mathutils.Vector(point.co[:3]) - mathutils.Vector(spline.points[index - 1].co[:3])
					total_length += diff_co.length
				
				if total_length == 0.0: continue
				
				current_length = 0.0
				for index, point in enumerate(spline.points):
					if 1 <= index:
						diff_co = mathutils.Vector(point.co[:3]) - mathutils.Vector(spline.points[index - 1].co[:3])
						current_length += diff_co.length
					
					current_length_ratio = current_length / total_length
					
					if current_length_ratio <= begin_ratio:
						current_tilt = self.begin_tilt
					elif end_ratio <= current_length_ratio:
						current_tilt = self.end_tilt
					else:
						tilt_ratio = (current_length_ratio - begin_ratio) / (end_ratio - begin_ratio)
						current_tilt = (self.begin_tilt * (1 - tilt_ratio)) + (self.end_tilt * (tilt_ratio))
					
					if   self.mode == 'ABSOLUTE': point.tilt = current_tilt
					elif self.mode == 'RELATIVE': point.tilt += current_tilt
		
		return {'FINISHED'}
