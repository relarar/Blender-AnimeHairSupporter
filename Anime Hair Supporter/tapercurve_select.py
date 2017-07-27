import bpy

class ahs_tapercurve_select(bpy.types.Operator):
	bl_idname = 'object.ahs_tapercurve_select'
	bl_label = "選択"
	bl_options = {'REGISTER', 'UNDO'}
	
	is_bevel = bpy.props.BoolProperty(name="ベベル")
	
	@classmethod
	def poll(cls, context):
		try:
			taper_and_bevel_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object] + [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
			for ob in context.visible_objects:
				if ob in taper_and_bevel_objects: break
			else: return False
		except: return False
		return True
	
	def execute(self, context):
		if not self.is_bevel: taper_or_bevel_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object]
		else: taper_or_bevel_objects = [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
		
		target_objects = []
		for ob in context.visible_objects:
			if ob in taper_or_bevel_objects: target_objects.append(ob)
		if not len(target_objects): return {'FINISHED'}
		
		if context.active_object not in target_objects:
			target_objects.sort(key=lambda ob: ob.name)
			context.scene.objects.active = target_objects[0]
		for ob in target_objects: ob.select = True
		return {'FINISHED'}
