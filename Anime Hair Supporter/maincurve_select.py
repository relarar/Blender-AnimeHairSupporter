import bpy

class ahs_maincurve_select(bpy.types.Operator):
	bl_idname = 'object.ahs_maincurve_select'
	bl_label = "選択"
	bl_description = "メインカーブをすべて選択する"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		try:
			for ob in context.visible_objects:
				if ob.type != 'CURVE': continue
				if ob.data.taper_object and ob.data.bevel_object: break
			else: return False
		except: return False
		return True
	
	def execute(self, context):
		target_objects = []
		for ob in context.visible_objects:
			if ob.type != 'CURVE': continue
			if ob.data.taper_object and ob.data.bevel_object:
				target_objects.append(ob)
		if not len(target_objects): return {'FINISHED'}
		
		if context.active_object not in target_objects:
			target_objects.sort(key=lambda ob: ob.name)
			context.scene.objects.active = target_objects[0]
		for ob in target_objects: ob.select = True
		return {'FINISHED'}
