import bpy, mathutils, math, os

class ahs_maincurve_fleshout(bpy.types.Operator):
	bl_idname = 'object.ahs_maincurve_fleshout'
	bl_label = "肉付け"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('Basic', "基本", "", 'MOD_CURVE', 1),
		('Sphere', "円", "", 'SPHERECURVE', 2),
		]
	taper_type = bpy.props.EnumProperty(items=items, name="テーパー", default='Basic')
	
	items = [
		('Sphere', "円", "", 'SURFACE_NCIRCLE', 1),
		('Sharp', "シャープ", "", 'LINCURVE', 2),
		('V', "切り込み", "", 'FILE_TICK', 3),
		('Corrugated', "ギザギザ", "", 'RNDCURVE', 4),
		]
	bevel_type = bpy.props.EnumProperty(items=items, name="ベベル", default='Sphere')
	
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
		self.layout.prop(self, 'bevel_type')
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
				data_to.objects = ["Taper_" + self.taper_type]
			taper_curve_ob = data_to.objects[0]
			taper_curve = taper_curve_ob.data
			name = ob.name + ":Taper"
			taper_curve_ob.name, taper_curve.name = name, name
			context.scene.objects.link(taper_curve_ob)
			curve.taper_object = taper_curve_ob
			
			# ベベルオブジェクトをアペンドして割り当て
			with context.blend_data.libraries.load(blend_path) as (data_from, data_to):
				data_to.objects = ["Bevel_" + self.bevel_type]
			bevel_curve_ob = data_to.objects[0]
			bevel_curve = bevel_curve_ob.data
			name = ob.name + ":Bevel"
			bevel_curve_ob.name, bevel_curve.name = name, name
			context.scene.objects.link(bevel_curve_ob)
			curve.bevel_object = bevel_curve_ob
			
			# 位置変更
			if not len(curve.splines): continue
			end_co = ob.matrix_world * mathutils.Vector(curve.splines[0].points[-1].co[:3])
			taper_curve_ob.location, bevel_curve_ob.location = end_co.copy(), end_co.copy()
			
			# 拡縮変更
			taper_curve_ob.scale = (self.scale, self.scale, self.scale)
			bevel_curve_ob.scale = (self.scale, self.scale * self.scale_y, self.scale)
		
		return {'FINISHED'}
