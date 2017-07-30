import bpy, re

class ahs_tapercurve_remove_alones(bpy.types.Operator):
	bl_idname = 'object.ahs_tapercurve_remove_alones'
	bl_label = "ぼっち駆除"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('TAPER', "テーパー", "", 'CURVE_NCURVE', 1),
		('BEVEL', "ベベル", "", 'SURFACE_NCIRCLE', 2),
		('BOTH', "両方", "", 'ARROW_LEFTRIGHT', 3),
		]
	mode = bpy.props.EnumProperty(items=items, name="モード", default='BOTH')
	
	@classmethod
	def poll(cls, context):
		try:
			taper_and_bevel_objects = []
			for ob in context.blend_data.objects:
				if ob.type != 'CURVE': continue
				if ob.data.taper_object: taper_and_bevel_objects.append(ob.data.taper_object)
				if ob.data.bevel_object: taper_and_bevel_objects.append(ob.data.bevel_object)
			for ob in context.blend_data.objects:
				name = re.sub(r'\.\d{3,}$', "", ob.name)
				if re.search(r':(Taper|Bevel)$', name) and ob not in taper_and_bevel_objects: break
			else: return False
		except: return False
		return True
	
	def execute(self, context):
		if self.mode != 'BEVEL':
			taper_objects = []
			for ob in context.blend_data.objects:
				if ob.type != 'CURVE': continue
				if ob.data.taper_object: taper_objects.append(ob.data.taper_object)
			for ob in context.blend_data.objects:
				name = re.sub(r'\.\d{3,}$', "", ob.name)
				if re.search(r':Taper$', name) and ob not in taper_objects:
					context.blend_data.curves.remove(ob.data, do_unlink=True)
					context.blend_data.objects.remove(ob, do_unlink=True)
		
		if self.mode != 'TAPER':
			bevel_objects = []
			for ob in context.blend_data.objects:
				if ob.type != 'CURVE': continue
				if ob.data.bevel_object: bevel_objects.append(ob.data.bevel_object)
			for ob in context.blend_data.objects:
				name = re.sub(r'\.\d{3,}$', "", ob.name)
				if re.search(r':Bevel$', name) and ob not in bevel_objects:
					context.blend_data.curves.remove(ob.data, do_unlink=True)
					context.blend_data.objects.remove(ob, do_unlink=True)
		
		for area in context.screen.areas: area.tag_redraw()
		return {'FINISHED'}
