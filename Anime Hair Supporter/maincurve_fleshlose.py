import bpy

class ahs_maincurve_fleshlose(bpy.types.Operator):
	bl_idname = 'object.ahs_maincurve_fleshlose'
	bl_label = "肉付けを削除"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		try:
			for ob in context.selected_objects:
				if ob.type != 'CURVE': continue
				if ob.data.taper_object or ob.data.bevel_object: break
			else: return False
		except: return False
		return True
	
	def execute(self, context):
		for ob in context.selected_objects:
			if ob.type != 'CURVE': continue
			if ob.data.taper_object:
				o, c = ob.data.taper_object, ob.data.taper_object.data
				if o: context.blend_data.objects.remove(o, do_unlink=True)
				if c: context.blend_data.curves.remove(c, do_unlink=True)
			if ob.data.bevel_object:
				o, c = ob.data.bevel_object, ob.data.bevel_object.data
				if o: context.blend_data.objects.remove(o, do_unlink=True)
				if c: context.blend_data.curves.remove(c, do_unlink=True)
		
		for area in context.screen.areas: area.tag_redraw()
		return {'FINISHED'}
