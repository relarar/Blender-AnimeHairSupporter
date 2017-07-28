import bpy, mathutils, math, os

class ahs_maincurve_fleshout(bpy.types.Operator):
	bl_idname = 'object.ahs_maincurve_fleshout'
	bl_label = "肉付け"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('Tapered', "先細り", "", 'MOD_CURVE', 1),
		('Sphere', "円", "", 'SPHERECURVE', 2),
		('Reversed', "先太り", "", 'PMARKER', 3),
		]
	taper_type = bpy.props.EnumProperty(items=items, name="テーパー", default='Tapered')
	
	items = [
		('Sphere', "円", "", 'MESH_CIRCLE'),
		('2', "2本", "", 'OUTLINER_OB_META'),
		('3', "3本", "", 'COLLAPSEMENU'),
		('Triangle', "三角", "", 'EDITMODE_VEC_HLT'),
		('TriangleLoose', "ゆるやか三角", "", 'PLAY_REVERSE'),
		('Square', "四角", "", 'MESH_PLANE'),
		('SquareLoose', "ゆるやか四角", "", 'SNAP_VOLUME'),
		('Diamond', "ひし形", "", 'SPACE3'),
		('DiamondLoose', "ゆるやかひし形", "", 'KEYTYPE_EXTREME_VEC'),
		('Sharp', "シャープ", "", 'LINCURVE'),
		('Leaf', "葉っぱ", "", 'MAN_ROT'),
		('V', "切り込み", "", 'FILE_TICK'),
		('Tilde', "波", "", 'IPO_EASE_IN_OUT'),
		('Step', "段差", "", 'IPO_CONSTANT'),
		('Corrugated', "ギザギザ", "", 'RNDCURVE'),
		]
	for i, item in enumerate(items): items[i] = tuple(list(item) + [i + 1])
	bevel_type = bpy.props.EnumProperty(items=items, name="ベベル", default='Sharp')
	is_bevel_mirror = bpy.props.BoolProperty(name="ベベルを左右反転", default=False)
	
	scale = bpy.props.FloatProperty(name="サイズ", default=0.2, min=0, max=10, soft_min=0, soft_max=10, step=3, precision=2)
	scale_y = bpy.props.FloatProperty(name="平たさ", default=0.5, min=0, max=1, soft_min=0, soft_max=1, step=3, precision=2)
	
	@classmethod
	def poll(cls, context):
		try:
			for ob in context.selected_objects:
				if ob.type == 'CURVE': break
			else: return False
		except: return False
		return True
	
	def draw(self, context):
		self.layout.prop(self, 'taper_type')
		
		row = self.layout.row(align=True)
		row.prop(self, 'bevel_type')
		row.prop(self, 'is_bevel_mirror', text="", icon='ARROW_LEFTRIGHT')
		
		self.layout.prop(self, 'scale')
		self.layout.prop(self, 'scale_y', slider=True)
	
	def execute(self, context):
		# すでにテーパーかベベルとして指定されているオブジェクトをリスト
		taper_and_bevel_objects = [c.taper_object for c in context.blend_data.curves] + [c.bevel_object for c in context.blend_data.curves]
		
		blend_path = os.path.join(os.path.dirname(__file__), "_append_data.blend")
		
		for ob in context.selected_objects:
			if ob in taper_and_bevel_objects: continue
			if ob.type != 'CURVE': continue
			
			curve = ob.data
			
			# すでにテーパーかベベルがあって参照が1つの場合は削除
			if curve.taper_object:
				if len([c.taper_object for c in context.blend_data.curves if c.taper_object == curve.taper_object]) == 1:
					o, c = curve.taper_object, curve.taper_object.data
					if o: context.blend_data.objects.remove(o, do_unlink=True)
					if c: context.blend_data.curves.remove(c, do_unlink=True)
			if curve.bevel_object:
				if len([c.bevel_object for c in context.blend_data.curves if c.bevel_object == curve.bevel_object]) == 1:
					o, c = curve.bevel_object, curve.bevel_object.data
					if o: context.blend_data.objects.remove(o, do_unlink=True)
					if c: context.blend_data.curves.remove(c, do_unlink=True)
			
			# テーパーオブジェクトをアペンドして割り当て
			with context.blend_data.libraries.load(blend_path) as (data_from, data_to):
				data_to.objects = ["Taper." + self.taper_type]
			taper_curve_ob = data_to.objects[0]
			taper_curve = taper_curve_ob.data
			name = ob.name + ":Taper"
			taper_curve_ob.name, taper_curve.name = name, name
			context.scene.objects.link(taper_curve_ob)
			curve.taper_object = taper_curve_ob
			
			# ベベルオブジェクトをアペンドして割り当て
			with context.blend_data.libraries.load(blend_path) as (data_from, data_to):
				data_to.objects = ["Bevel." + self.bevel_type]
			bevel_curve_ob = data_to.objects[0]
			bevel_curve = bevel_curve_ob.data
			name = ob.name + ":Bevel"
			bevel_curve_ob.name, bevel_curve.name = name, name
			context.scene.objects.link(bevel_curve_ob)
			curve.bevel_object = bevel_curve_ob
			# 左右反転処理
			if self.is_bevel_mirror:
				co_list = [list(p.co) for p in bevel_curve.splines[0].points]
				co_list.reverse()
				for point, new_co in zip(bevel_curve.splines[0].points, co_list):
					new_co[0] = -new_co[0]
					point.co = new_co
			
			# 位置変更
			if len(curve.splines):
				end_co = ob.matrix_world * mathutils.Vector(curve.splines[0].points[-1].co[:3])
				taper_curve_ob.location, bevel_curve_ob.location = end_co.copy(), end_co.copy()
			
			# 回転変更
			if len(curve.splines):
				# 最後の辺をトラック
				taper_curve_ob.rotation_mode, bevel_curve_ob.rotation_mode = 'QUATERNION', 'QUATERNION'
				last_direction = ob.matrix_world * mathutils.Vector(curve.splines[0].points[-2].co[:3]) - ob.matrix_world * mathutils.Vector(curve.splines[0].points[-1].co[:3])
				up_direction = mathutils.Vector((0, 0, 1))
				quat = up_direction.rotation_difference(last_direction)
				taper_curve_ob.rotation_quaternion, bevel_curve_ob.rotation_quaternion = quat, quat
				# Z回転
				diff_co = ob.matrix_world * mathutils.Vector(curve.splines[0].points[-1].co[:3]) - ob.matrix_world * mathutils.Vector(curve.splines[0].points[0].co[:3])
				rotation_z = math.atan2(diff_co.y, diff_co.x) - curve.splines[0].points[-1].tilt
				taper_curve_ob.rotation_quaternion *= mathutils.Quaternion((0, 0, 1), rotation_z)
				bevel_curve_ob.rotation_quaternion *= mathutils.Quaternion((0, 0, 1), rotation_z - math.radians(90))
			
			# 拡縮変更
			taper_curve_ob.scale = (self.scale, self.scale, self.scale)
			bevel_curve_ob.scale = (self.scale, self.scale * self.scale_y, self.scale)
		
		return {'FINISHED'}
