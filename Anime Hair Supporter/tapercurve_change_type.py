import bpy, os
from . import _common

class ahs_tapercurve_change_type(bpy.types.Operator):
	bl_idname = 'object.ahs_tapercurve_change_type'
	bl_label = "種類を変更"
	bl_options = {'REGISTER', 'UNDO'}
	
	is_taper = bpy.props.BoolProperty(name="テーパーを変更")
	taper_type = bpy.props.EnumProperty(items=_common.get_taper_enum_items(), name="テーパー", default='Tapered')
	
	is_bevel = bpy.props.BoolProperty(name="ベベルを変更")
	bevel_type = bpy.props.EnumProperty(items=_common.get_bevel_enum_items(), name="ベベル", default='Sharp')
	is_bevel_mirror = bpy.props.BoolProperty(name="ベベルを左右反転", default=False)
	
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
		row = self.layout.row(align=True)
		if self.is_taper: icon = 'FILE_TICK'
		else: icon = 'BLANK1'
		row.prop(self, 'is_taper', text="", icon=icon, toggle=True)
		sub_row = row.row(align=True)
		sub_row.prop(self, 'taper_type')
		sub_row.enabled = self.is_taper
		
		row = self.layout.row(align=True)
		if self.is_bevel: icon = 'FILE_TICK'
		else: icon = 'BLANK1'
		row.prop(self, 'is_bevel', text="", icon=icon, toggle=True)
		sub_row = row.row(align=True)
		sub_row.prop(self, 'bevel_type')
		sub_row.prop(self, 'is_bevel_mirror', text="", icon='MOD_MIRROR')
		sub_row.enabled = self.is_bevel
	
	def execute(self, context):
		blend_path = _common.get_append_data_blend_path()
		
		if self.is_taper:
			target_objects = []
			taper_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object]
			for ob in context.selected_objects:
				if ob.type != 'CURVE': continue
				
				if ob.data.taper_object: target_objects.append(ob.data.taper_object)
				elif ob in taper_objects: target_objects.append(ob)
			
			for ob in target_objects:
				pre_curve = ob.data
				pre_name = pre_curve.name
				
				with context.blend_data.libraries.load(blend_path) as (data_from, data_to):
					data_to.curves = ["Taper." + self.taper_type]
				new_curve = data_to.curves[0]
				
				ob.data = new_curve
				context.blend_data.curves.remove(pre_curve, do_unlink=True)
				new_curve.name = pre_name
		
		if self.is_bevel:
			target_objects = []
			bevel_objects = [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
			for ob in context.selected_objects:
				if ob.type != 'CURVE': continue
				
				if ob.data.bevel_object: target_objects.append(ob.data.bevel_object)
				elif ob in bevel_objects: target_objects.append(ob)
			
			for ob in target_objects:
				pre_curve = ob.data
				pre_name = pre_curve.name
				
				with context.blend_data.libraries.load(blend_path) as (data_from, data_to):
					data_to.curves = ["Bevel." + self.bevel_type]
				new_curve = data_to.curves[0]
				
				ob.data = new_curve
				context.blend_data.curves.remove(pre_curve, do_unlink=True)
				new_curve.name = pre_name
				
				# 左右反転処理
				if self.is_bevel_mirror:
					co_list = [list(p.co) for p in new_curve.splines[0].points]
					co_list.reverse()
					for point, new_co in zip(new_curve.splines[0].points, co_list):
						new_co[0] = -new_co[0]
						point.co = new_co
		
		return {'FINISHED'}
