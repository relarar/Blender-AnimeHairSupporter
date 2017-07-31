import bpy, bmesh, mathutils

class ahs_convert_curve_to_mesh(bpy.types.Operator):
	bl_idname = 'object.ahs_convert_curve_to_mesh'
	bl_label = "カーブ > メッシュ"
	bl_options = {'REGISTER', 'UNDO'}
	
	is_join = bpy.props.BoolProperty(name="オブジェクトを統合", default=True)
	is_remove_doubles = bpy.props.BoolProperty(name="重複頂点を削除", default=True)
	is_uv_pack_islands = bpy.props.BoolProperty(name="UVの島を梱包", default=True)
	
	@classmethod
	def poll(cls, context):
		return True
	
	def draw(self, context):
		self.layout.prop(self, 'is_join', icon='FORCE_LENNARDJONES', toggle=True)
		
		self.layout.prop(self, 'is_remove_doubles', icon='STICKY_UVS_LOC', toggle=True)
		
		row = self.layout.row(align=True)
		row.prop(self, 'is_uv_pack_islands', icon='UV_ISLANDSEL', toggle=True)
		row.enabled = self.is_join
	
	def execute(self, context):
		# メッシュ選択モードを一時的に頂点モードに
		pre_mesh_select_mode = context.tool_settings.mesh_select_mode
		context.tool_settings.mesh_select_mode = (True, False, False)
		
		# 変換するカーブを抽出
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
		
		# テーパー/ベベルオブジェクトを保管
		taper_and_bevel_objects = []
		for ob in target_objects:
			taper_and_bevel_objects.append(ob.data.taper_object)
			taper_and_bevel_objects.append(ob.data.bevel_object)
		
		# 公式のカーブ > メッシュ
		bpy.ops.object.convert(target='MESH', keep_original=False)
		
		# 選択メッシュの中心位置を計算
		x_list, y_list, z_list = [], [], []
		for ob in target_objects:
			for co_tuple in ob.bound_box:
				co = ob.matrix_world * mathutils.Vector(co_tuple)
				x_list.append(co.x), y_list.append(co.y), z_list.append(co.z)
		x_center, y_center, z_center = (min(x_list) + max(x_list)) / 2, (min(y_list) + max(y_list)) / 2, (min(z_list) + max(z_list)) / 2
		objects_center = mathutils.Vector((x_center, y_center, z_center))
		
		# 変換されたメッシュを順に処理
		for ob in target_objects:
			# 事前処理
			context.scene.objects.active = ob
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.select_all(action='DESELECT')
			
			bm = bmesh.from_edit_mesh(ob.data)
			
			# 真ん中あたりの面 > ループ > 辺と辿って選択
			bm.faces.ensure_lookup_table()
			center_face = bm.faces[int(len(bm.faces) * 0.5)]
			center_face.loops[1].edge.select_set(True)
			
			# 辺ループ選択
			bpy.ops.mesh.loop_multi_select(ring=False)
			
			# 対象の断面の頂点/辺を保管
			selected_verts = [v for v in bm.verts if v.select]
			selected_edges = [e for e in bm.edges if e.select]
			bpy.ops.mesh.select_all(action='DESELECT')
			
			# シームを入れるべき辺ループに繋がってる頂点を検索
			verts_distance = [((ob.matrix_world * v.co) - objects_center).length for v in selected_verts]
			verts_density = []
			for vert in selected_verts:
				lengths = [e.calc_length() for e in vert.link_edges]
				verts_density.append(sum(lengths) / len(lengths))
			best_vert, best_score = selected_verts[0], 0
			min_verts_distance, max_verts_distance = min(verts_distance), max(verts_distance)
			min_verts_density, max_verts_density = min(verts_density), max(verts_density)
			for vert, distance, density in zip(selected_verts, verts_distance, verts_density):
				distance_score = (distance - min_verts_distance) / (max_verts_distance - min_verts_distance)
				density_score = (density - min_verts_density) / (max_verts_density - min_verts_density)
				score = ((1 - distance_score) * 0.5) + ((1 - density_score) * 0.5)
				if best_score < score:
					best_vert, best_score = vert, score
			
			# 1頂点選択状態から辺ループ選択してシームを入れる
			for edge in best_vert.link_edges:
				if edge not in selected_edges:
					edge.select_set(True)
			bpy.ops.mesh.loop_multi_select(ring=False)
			bpy.ops.mesh.mark_seam(clear=False)
			
			# 重複頂点を削除
			if self.is_remove_doubles:
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.mesh.select_non_manifold(extend=True, use_wire=True, use_boundary=True, use_multi_face=True, use_non_contiguous=True, use_verts=True)
				bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=False)
			
			# UV展開
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.uv.unwrap(method='ANGLE_BASED', fill_holes=True, correct_aspect=True, use_subsurf_data=False, margin=0.001)
			
			# 事後処理
			bmesh.update_edit_mesh(ob.data)
			bpy.ops.object.mode_set(mode='OBJECT')
		
		# 名前順で一番前のオブジェクトをアクティブ化
		context.scene.objects.active = sorted(target_objects, key=lambda o: o.name)[0]
		
		# 公式のオブジェクト統合
		if self.is_join: bpy.ops.object.join()
		
		# UVの島を梱包
		if self.is_uv_pack_islands and self.is_join:
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.uv.average_islands_scale()
			bpy.ops.uv.pack_islands(rotate=False, margin=0.02)
			bpy.ops.object.mode_set(mode='OBJECT')
		
		# 必要なくなったテーパー/ベベルを完全削除
		for ob in taper_and_bevel_objects:
			context.blend_data.curves.remove(ob.data, do_unlink=True)
			context.blend_data.objects.remove(ob, do_unlink=True)
		
		context.tool_settings.mesh_select_mode = pre_mesh_select_mode
		return {'FINISHED'}
