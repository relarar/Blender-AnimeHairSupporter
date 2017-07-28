import bpy

class ahs_tapercurve_activate_main(bpy.types.Operator):
	bl_idname = 'object.ahs_tapercurve_activate_main'
	bl_label = "メインカーブへ"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		try:
			taper_and_bevel_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object] + [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
			if context.active_object not in taper_and_bevel_objects: return False
		except: return False
		return True
	
	def execute(self, context):
		ob = context.active_object
		
		parent_objects = []
		for o in context.blend_data.objects:
			if o.type != 'CURVE': continue
			if o.data.taper_object == ob: parent_objects.append(o)
			if o.data.bevel_object == ob: parent_objects.append(o)
		
		for o in context.blend_data.objects: o.select = False
		for target_ob in parent_objects:
			target_ob.select, target_ob.hide = True, False
			context.scene.objects.active = target_ob
		
		return {'FINISHED'}
