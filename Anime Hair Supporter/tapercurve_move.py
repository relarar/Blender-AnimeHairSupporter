import bpy, mathutils, math

class ahs_tapercurve_move(bpy.types.Operator):
	bl_idname = 'object.ahs_tapercurve_move'
	bl_label = "再配置"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('TAPER', "テーパー", "", 'CURVE_NCURVE', 1),
		('BEVEL', "ベベル", "", 'SURFACE_NCIRCLE', 2),
		('BOTH', "両方", "", 'ARROW_LEFTRIGHT', 3),
		]
	mode = bpy.props.EnumProperty(items=items, name="モード", default='BOTH')
	
	is_location = bpy.props.BoolProperty(name="位置", default=True)
	is_rotation = bpy.props.BoolProperty(name="回転", default=False)
	
	@classmethod
	def poll(cls, context):
		try:
			taper_and_bevel_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object] + [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
			for ob in context.visible_objects:
				if ob in taper_and_bevel_objects: break
			else: return False
		except: return False
		return True
	
	def draw(self, context):
		self.layout.prop(self, 'mode')
		
		row = self.layout.row(align=True)
		row.prop(self, 'is_location', icon='MAN_TRANS', toggle=True)
		row.prop(self, 'is_rotation', icon='MAN_ROT', toggle=True)
	
	def execute(self, context):
		if self.mode == 'TAPER': taper_or_bevel_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object]
		elif self.mode == 'BEVEL': taper_or_bevel_objects = [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
		else: taper_or_bevel_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object] + [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
		
		target_zips = []
		for ob in context.visible_objects:
			if ob.type != 'CURVE': continue
			if ob not in taper_or_bevel_objects: continue
			
			parent_ob = None
			for o in context.blend_data.objects:
				if o.type != 'CURVE': continue
				
				if self.mode == 'TAPER' and o.data.taper_object == ob: parent_ob = o
				elif self.mode == 'BEVEL' and o.data.bevel_object == ob: parent_ob = o
				elif self.mode == 'BOTH' and (o.data.taper_object == ob or o.data.bevel_object == ob): parent_ob = o
			if not parent_ob: continue
			
			target_zips.append((ob, parent_ob))
		
		for ob, parent_ob in target_zips:
			if not len(parent_ob.data.splines): continue
			
			# 位置変更
			if self.is_location:
				end_co = parent_ob.matrix_world * mathutils.Vector(parent_ob.data.splines[0].points[-1].co[:3])
				ob.location = end_co.copy()
			
			# 回転変更
			if self.is_rotation:
				# 最後の辺をトラック
				ob.rotation_mode = 'QUATERNION'
				last_direction = parent_ob.matrix_world * mathutils.Vector(parent_ob.data.splines[0].points[-2].co[:3]) - parent_ob.matrix_world * mathutils.Vector(parent_ob.data.splines[0].points[-1].co[:3])
				up_direction = mathutils.Vector((0, 0, 1))
				ob.rotation_quaternion = up_direction.rotation_difference(last_direction)
				# Z回転
				diff_co = parent_ob.matrix_world * mathutils.Vector(parent_ob.data.splines[0].points[-1].co[:3]) - parent_ob.matrix_world * mathutils.Vector(parent_ob.data.splines[0].points[0].co[:3])
				rotation_z = math.atan2(diff_co.y, diff_co.x) - parent_ob.data.splines[0].points[-1].tilt
				if parent_ob.data.taper_object == ob: ob.rotation_quaternion *= mathutils.Quaternion((0, 0, 1), rotation_z)
				elif parent_ob.data.bevel_object == ob: ob.rotation_quaternion *= mathutils.Quaternion((0, 0, 1), rotation_z - math.radians(90))
		
		return {'FINISHED'}
