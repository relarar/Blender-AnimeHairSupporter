import bpy, math, mathutils

class ahs_maincurve_gradation_tilt(bpy.types.Operator):
	bl_idname = 'object.ahs_maincurve_gradation_tilt'
	bl_label = "グラデーションひねり"
	bl_description = "選択カーブをゆるやかにひねる/傾ける"
	bl_options = {'REGISTER', 'UNDO'}
	
	is_tilt = bpy.props.BoolProperty(name="傾き", default=True)
	is_radius = bpy.props.BoolProperty(name="半径", default=False)
	is_weight_softbody = bpy.props.BoolProperty(name="ウェイト", default=False)
	
	begin_ratio = bpy.props.IntProperty(name="始点", default=33, min=0, max=100, soft_min=0, soft_max=100, subtype='PERCENTAGE')
	begin_tilt = bpy.props.FloatProperty(name="傾き", default=0, min=math.radians(-360), max=math.radians(360), soft_min=math.radians(-360), soft_max=math.radians(360), step=3, precision=0, subtype='ANGLE', unit='ROTATION')
	begin_radius = bpy.props.FloatProperty(name="半径", default=1, min=0, max=10, soft_min=0, soft_max=10, step=3, precision=2)
	begin_weight_softbody = bpy.props.IntProperty(name="ウェイト", default=100, min=0, max=100, soft_min=0, soft_max=100, subtype='PERCENTAGE')
	
	end_ratio = bpy.props.IntProperty(name="終点", default=100, min=0, max=100, soft_min=0, soft_max=100, subtype='PERCENTAGE')
	end_tilt = bpy.props.FloatProperty(name="傾き", default=0, min=math.radians(-360), max=math.radians(360), soft_min=math.radians(-360), soft_max=math.radians(360), step=3, precision=0, subtype='ANGLE', unit='ROTATION')
	end_radius = bpy.props.FloatProperty(name="半径", default=0, min=0, max=10, soft_min=0, soft_max=10, step=3, precision=2)
	end_weight_softbody = bpy.props.IntProperty(name="ウェイト", default=0, min=0, max=100, soft_min=0, soft_max=100, subtype='PERCENTAGE')
	
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
		row = self.layout.row(align=True)
		row.prop(self, 'is_tilt', icon='FORCE_MAGNETIC', toggle=True)
		row.prop(self, 'is_radius', icon='FORCE_FORCE', toggle=True)
		row.prop(self, 'is_weight_softbody', icon='MOD_SOFT', toggle=True)
		
		column = self.layout.column(align=True)
		column.prop(self, 'begin_ratio', slider=True)
		row = column.row(align=True)
		row.prop(self, 'begin_tilt', slider=True)
		row.enabled = self.is_tilt
		row = column.row(align=True)
		row.prop(self, 'begin_radius')
		row.enabled = self.is_radius
		row = column.row(align=True)
		row.prop(self, 'begin_weight_softbody', slider=True)
		row.enabled = self.is_weight_softbody
		
		column = self.layout.column(align=True)
		column.prop(self, 'end_ratio', slider=True)
		row = column.row(align=True)
		row.prop(self, 'end_tilt', slider=True)
		row.enabled = self.is_tilt
		row = column.row(align=True)
		row.prop(self, 'end_radius')
		row.enabled = self.is_radius
		row = column.row(align=True)
		row.prop(self, 'end_weight_softbody', slider=True)
		row.enabled = self.is_weight_softbody
		
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
						current_radius = self.begin_radius
						current_weight_softbody = self.begin_weight_softbody
					elif end_ratio <= current_length_ratio:
						current_tilt = self.end_tilt
						current_radius = self.end_radius
						current_weight_softbody = self.end_weight_softbody
					else:
						ratio = (current_length_ratio - begin_ratio) / (end_ratio - begin_ratio)
						current_tilt = (self.begin_tilt * (1 - ratio)) + (self.end_tilt * (ratio))
						current_radius = (self.begin_radius * (1 - ratio)) + (self.end_radius * (ratio))
						current_weight_softbody = ((self.begin_weight_softbody * (1 - ratio)) + (self.end_weight_softbody * (ratio))) * 0.01
					
					if self.is_tilt:
						if   self.mode == 'ABSOLUTE': point.tilt = current_tilt
						elif self.mode == 'RELATIVE': point.tilt += current_tilt
					if self.is_radius:
						if   self.mode == 'ABSOLUTE': point.radius = current_radius
						elif self.mode == 'RELATIVE': point.radius += current_radius
					if self.is_weight_softbody:
						if   self.mode == 'ABSOLUTE': point.weight_softbody = current_weight_softbody
						elif self.mode == 'RELATIVE': point.weight_softbody += current_weight_softbody
		
		return {'FINISHED'}
