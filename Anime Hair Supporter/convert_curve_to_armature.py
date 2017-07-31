import bpy, mathutils

class ahs_convert_curve_to_armature(bpy.types.Operator):
	bl_idname = 'object.ahs_convert_curve_to_armature'
	bl_label = "カーブ > アーマチュア"
	bl_options = {'REGISTER', 'UNDO'}
	
	bone_subdivide_count = bpy.props.IntProperty(name="ボーン分割数", default=1, min=0, max=8, soft_min=0, soft_max=8)
	
	@classmethod
	def poll(cls, context):
		return True
	
	def execute(self, context):
		bone_points = []
		for ob in context.selected_objects:
			ob.select = False
			if ob.type != 'CURVE': continue
			if not len(ob.data.splines): continue
			if len(ob.data.splines[0].points) < 2: continue
			
			pre_curve = ob.data
			temp_curve = pre_curve.copy()
			ob.data = temp_curve
			
			temp_curve.extrude = 0
			temp_curve.bevel_depth = 0
			temp_curve.bevel_factor_start = 0
			temp_curve.bevel_factor_end = 1
			temp_curve.taper_object = None
			temp_curve.bevel_object = None
			for spline in temp_curve.splines: spline.resolution_u = 64
			
			curve_point_cos = [mathutils.Vector(p.co[:3]) for p in temp_curve.splines[0].points]
			curve_point_lengths = [0]
			for index, co in enumerate(curve_point_cos):
				if index == 0: continue
				prev_co = curve_point_cos[index - 1]
				curve_point_lengths.append((co - prev_co).length)
			total_curve_point_length = sum(curve_point_lengths)
			curve_point_ratios = [l / total_curve_point_length for l in curve_point_lengths]
			
			temp_me = ob.to_mesh(context.scene, False, 'PREVIEW')
			
			ob.data = pre_curve
			context.blend_data.curves.remove(temp_curve, do_unlink=True)
			
			vert_cos = [ob.matrix_world * v.co for v in temp_me.vertices]
			vert_lengths = [0]
			for index, co in enumerate(vert_cos):
				if index == 0: continue
				prev_co = vert_cos[index - 1]
				vert_lengths.append((co - prev_co).length)
			total_vert_length = sum(vert_lengths)
			
			local_bone_points = [vert_cos[0].copy()]
			current_length = 0
			for ratio_index, ratio in enumerate(curve_point_ratios):
				if ratio_index == 0: continue
				raw_bone_length = total_vert_length * ratio
				bone_length = raw_bone_length / (self.bone_subdivide_count + 1)
				
				for bone_index in range(self.bone_subdivide_count + 1):
					target_length = current_length + (bone_length * (bone_index + 1))
					
					current_vert_length = 0
					for co_index, co in enumerate(vert_cos):
						if co_index == 0: continue
						pre_co = vert_cos[co_index - 1]
						current_vert_length += (co - pre_co).length
						target_co = co.copy()
						if target_length <= current_vert_length: break
					
					local_bone_points.append(target_co)
				
				current_length += raw_bone_length
			
			context.blend_data.meshes.remove(temp_me, do_unlink=True)
			
			bone_points.append(local_bone_points)
		
		new_arm = context.blend_data.armatures.new("Armature")
		new_ob = context.blend_data.objects.new("Armature", new_arm)
		new_ob.data = new_arm
		context.scene.objects.link(new_ob)
		new_ob.select = True
		context.scene.objects.active = new_ob
		new_ob.show_x_ray = True
		new_arm.draw_type = 'STICK'
		
		bpy.ops.object.mode_set(mode='EDIT')
		
		for index, local_bone_points in enumerate(bone_points):
			prev_bone = None
			for point_index, point in enumerate(local_bone_points):
				if point_index == 0: continue
				new_bone = new_arm.edit_bones.new("Hair " + str(index+1) + "-" + str(point_index))
				new_bone.head = local_bone_points[point_index - 1].copy()
				new_bone.tail = point.copy()
				new_bone.parent = prev_bone
				new_bone.use_connect = bool(prev_bone)
				prev_bone = new_bone
		
		bpy.ops.object.mode_set(mode='OBJECT')
		return {'FINISHED'}
