import bpy, mathutils, math, os
from . import _common

class ahs_maincurve_fleshout(bpy.types.Operator):
	bl_idname = 'object.ahs_maincurve_fleshout'
	bl_label = "肉付け"
	bl_description = "選択中のカーブにテーパー/ベベルを設定して実体化する"
	bl_options = {'REGISTER', 'UNDO'}
	
	taper_type = bpy.props.EnumProperty(items=_common.get_taper_enum_items(), name="テーパー", default='Tapered')
	
	bevel_type = bpy.props.EnumProperty(items=_common.get_bevel_enum_items(), name="ベベル", default='Sharp')
	is_bevel_mirror = bpy.props.BoolProperty(name="ベベルを左右反転", default=False)
	
	scale = bpy.props.FloatProperty(name="半径", default=0.2, min=0, max=10, soft_min=0, soft_max=10, step=0.1, precision=3)
	scale_y_multi = bpy.props.IntProperty(name="平たさ", default=50, min=0, max=100, soft_min=0, soft_max=100, subtype='PERCENTAGE')
	
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
		row.prop(self, 'is_bevel_mirror', text="", icon='MOD_MIRROR')
		
		self.layout.prop(self, 'scale')
		self.layout.prop(self, 'scale_y_multi', slider=True)
	
	def execute(self, context):
		# すでにテーパーかベベルとして指定されているオブジェクトをリスト
		taper_and_bevel_objects = [c.taper_object for c in context.blend_data.curves] + [c.bevel_object for c in context.blend_data.curves]
		
		blend_path = _common.get_append_data_blend_path()
		
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
			taper_curve_ob.select = False
			context.scene.objects.link(taper_curve_ob)
			curve.taper_object = taper_curve_ob
			
			# ベベルオブジェクトをアペンドして割り当て
			with context.blend_data.libraries.load(blend_path) as (data_from, data_to):
				data_to.objects = ["Bevel." + self.bevel_type]
			bevel_curve_ob = data_to.objects[0]
			bevel_curve = bevel_curve_ob.data
			name = ob.name + ":Bevel"
			bevel_curve_ob.name, bevel_curve.name = name, name
			bevel_curve_ob.select = False
			context.scene.objects.link(bevel_curve_ob)
			curve.bevel_object = bevel_curve_ob
			# 左右反転処理
			if self.is_bevel_mirror:
				co_list = [list(p.co) for p in bevel_curve.splines[0].points]
				co_list.reverse()
				for point, new_co in zip(bevel_curve.splines[0].points, co_list):
					new_co[0] = -new_co[0]
					point.co = new_co
			
			_common.relocation_taper_and_bevel(ob, taper_curve_ob, True)
			_common.relocation_taper_and_bevel(ob, bevel_curve_ob, False)
			
			# 拡縮変更
			taper_curve_ob.scale = (self.scale, self.scale, self.scale)
			bevel_curve_ob.scale = (self.scale, self.scale * self.scale_y_multi * 0.01, self.scale)
		
		return {'FINISHED'}
