import bpy, bmesh

class ahs_convert_curve_to_mesh(bpy.types.Operator):
	bl_idname = 'object.ahs_convert_curve_to_mesh'
	bl_label = "カーブ > メッシュ"
	bl_options = {'REGISTER', 'UNDO'}
	
	is_remove_doubles = bpy.props.BoolProperty(name="重複頂点を削除", default=True)
	is_pack_islands = bpy.props.BoolProperty(name="島を梱包", default=True)
	
	@classmethod
	def poll(cls, context):
		return True
	
	def draw(self, context):
		self.layout.prop(self, 'is_remove_doubles', icon='STICKY_UVS_LOC', toggle=True)
		self.layout.prop(self, 'is_pack_islands', icon='UV_ISLANDSEL', toggle=True)
	
	def execute(self, context):
		pre_mesh_select_mode = context.tool_settings.mesh_select_mode
		context.tool_settings.mesh_select_mode = (True, False, False)
		
		target_objects = []
		for ob in context.selected_objects:
			if ob.type != 'CURVE':
				ob.select = False
				continue
			if not ob.data.taper_object or not ob.data.bevel_object:
				ob.select = False
				continue
			target_objects.append(ob)
		if not len(target_objects): return {'CANCELLED'}
		
		taper_and_bevel_objects = []
		for ob in target_objects:
			taper_and_bevel_objects.append(ob.data.taper_object)
			taper_and_bevel_objects.append(ob.data.bevel_object)
		
		bpy.ops.object.convert(target='MESH', keep_original=False)
		
		for ob in target_objects:
			context.scene.objects.active = ob
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.select_all(action='DESELECT')
			
			bm = bmesh.from_edit_mesh(ob.data)
			
			bm.faces.ensure_lookup_table()
			center_face = bm.faces[int(len(bm.faces) * 0.5)]
			center_face.loops[1].edge.select_set(True)
			
			bpy.ops.mesh.loop_multi_select(ring=False)
			
			selected_verts = [v for v in bm.verts if v.select]
			selected_edges = [e for e in bm.edges if e.select]
			bpy.ops.mesh.select_all(action='DESELECT')
			
			verts_co_z = [(ob.matrix_world * v.co).z for v in selected_verts]
			verts_density = []
			for vert in selected_verts:
				lengths = [e.calc_length() for e in vert.link_edges]
				verts_density.append(sum(lengths) / len(lengths))
			best_vert, best_score = selected_verts[0], 0
			for vert, co_z, density in zip(selected_verts, verts_co_z, verts_density):
				co_z_score = (co_z - min(verts_co_z)) / (max(verts_co_z) - min(verts_co_z))
				density_score = (density - min(verts_density)) / (max(verts_density) - min(verts_density))
				score = (1 - co_z_score) + (1 - density_score)
				if best_score < score:
					best_vert, best_score = vert, score
			
			for edge in best_vert.link_edges:
				if edge not in selected_edges:
					edge.select_set(True)
			bpy.ops.mesh.loop_multi_select(ring=False)
			bpy.ops.mesh.mark_seam(clear=False)
			
			if self.is_remove_doubles:
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.mesh.select_non_manifold(extend=True, use_wire=True, use_boundary=True, use_multi_face=True, use_non_contiguous=True, use_verts=True)
				bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=False)
			
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.uv.unwrap(method='ANGLE_BASED', fill_holes=True, correct_aspect=True, use_subsurf_data=False, margin=0.001)
			
			bmesh.update_edit_mesh(ob.data)
			bpy.ops.object.mode_set(mode='OBJECT')
		
		context.scene.objects.active = sorted(target_objects, key=lambda o: o.name)[0]
		bpy.ops.object.join()
		
		if self.is_pack_islands:
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.uv.pack_islands(rotate=False, margin=0.02)
			bpy.ops.object.mode_set(mode='OBJECT')
		
		for ob in taper_and_bevel_objects:
			context.blend_data.curves.remove(ob.data, do_unlink=True)
			context.blend_data.objects.remove(ob, do_unlink=True)
		
		context.tool_settings.mesh_select_mode = pre_mesh_select_mode
		return {'FINISHED'}
