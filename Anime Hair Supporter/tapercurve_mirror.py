import bpy

class ahs_tapercurve_mirror(bpy.types.Operator):
	bl_idname = 'object.ahs_tapercurve_mirror'
	bl_label = "ミラー"
	bl_description = "テーパー/ベベルの形状を左右/上下反転"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('TAPER', "テーパー", "", 'CURVE_NCURVE', 1),
		('BEVEL', "ベベル", "", 'SURFACE_NCIRCLE', 2),
		('BOTH', "両方", "", 'ARROW_LEFTRIGHT', 3),
		]
	mode = bpy.props.EnumProperty(items=items, name="モード", default='BOTH')
	
	is_mirror_x = bpy.props.BoolProperty(name="左右反転")
	is_mirror_y = bpy.props.BoolProperty(name="上下反転")
	
	@classmethod
	def poll(cls, context):
		try:
			taper_and_bevel_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object] + [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
			for ob in context.selected_objects:
				if ob.type != 'CURVE': continue
				if ob.data.taper_object or ob.data.bevel_object: break
				if ob in taper_and_bevel_objects: break
			else: return False
		except: return False
		return True
	
	def draw(self, context):
		self.layout.prop(self, 'mode')
		
		row = self.layout.row(align=True)
		row.prop(self, 'is_mirror_x', icon='ARROW_LEFTRIGHT', toggle=True)
		row.prop(self, 'is_mirror_y', icon='FILE_PARENT', toggle=True)
	
	def execute(self, context):
		taper_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object]
		bevel_objects = [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
		for selected_object in context.selected_objects:
			if selected_object.type != 'CURVE': continue
			
			target_objects, is_tapers = [], []
			if self.mode != 'BEVEL':
				if selected_object.data.taper_object:
					target_objects.append(selected_object.data.taper_object)
					is_tapers.append(True)
				elif selected_object in taper_objects:
					target_objects.append(selected_object)
					is_tapers.append(True)
			if self.mode != 'TAPER':
				if selected_object.data.bevel_object:
					target_objects.append(selected_object.data.bevel_object)
					is_tapers.append(False)
				elif selected_object in bevel_objects:
					target_objects.append(selected_object)
					is_tapers.append(False)
			
			for ob, is_taper in zip(target_objects, is_tapers):
				curve = ob.data
				
				if is_taper: is_mirror_x, is_mirror_y = self.is_mirror_y, self.is_mirror_x
				else: is_mirror_x, is_mirror_y = self.is_mirror_x, self.is_mirror_y
				
				for spline in curve.splines:
					if is_mirror_x:
						co_list = [list(p.co) for p in spline.points]
						co_list.reverse()
						for point, new_co in zip(spline.points, co_list):
							new_co[0] = -new_co[0]
							point.co = new_co
					
					if is_mirror_y:
						co_list = [list(p.co) for p in spline.points]
						if not is_taper:co_list.reverse()
						for point, new_co in zip(spline.points, co_list):
							new_co[1] = -new_co[1]
							point.co = new_co
		return {'FINISHED'}
