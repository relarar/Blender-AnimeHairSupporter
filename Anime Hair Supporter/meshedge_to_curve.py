import bpy, bmesh, mathutils

class ahs_meshedge_to_curve(bpy.types.Operator):
	bl_idname = 'object.ahs_meshedge_to_curve'
	bl_label = "辺メッシュ > カーブ"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		try:
			for ob in context.selected_objects:
				if ob.type == 'MESH': break
			else: return False
		except: return False
		return True
	
	def execute(self, context):
		new_objects = []
		for ob in context.selected_objects:
			if ob.type != 'MESH': continue
			if len(ob.data.vertices) < 2 or len(ob.data.edges) < 1 or len(ob.data.polygons): continue
			
			bm = bmesh.new()
			bm.from_mesh(ob.data)
			
			separated_verts = []
			already_edges = []
			for i in range(len(bm.verts) * 2):
				
				# まだ拾ってない開始頂点/辺を検索
				current_vert, current_edge = None, None
				for vert in bm.verts:
					# 繋がってる辺が2つは開始地点として不適切
					if len(vert.link_edges) == 2: continue
					# まだ拾ってない辺を検索
					for edge in vert.link_edges:
						if edge in already_edges: continue
						# 変数に確保して離脱
						current_vert, current_edge = vert, edge
						break
					if current_edge: break
				# 離脱
				else: break
				if not current_edge: break
				
				# 辿っていく
				local_verts = [current_vert]
				for j in range(len(bm.verts) * 2):
					# すでに拾ったもとと登録
					already_edges.append(current_edge)
					# 次の頂点を現在頂点に
					current_vert = current_edge.other_vert(current_vert)
					# ローカル結果にアペンド
					local_verts.append(current_vert)
					# 離脱
					if len(current_vert.link_edges) != 2: break
					# 2つある辺の次にあたるのを現在辺に
					for edge in current_vert.link_edges:
						if edge != current_edge:
							current_edge = edge
							break
				# 離脱
				else: break
				# 結果をアペンド
				separated_verts.append(local_verts)
			
			for local_verts in separated_verts:
				
				# グローバルZ軸が上の頂点を開始地点とする
				begin_co = ob.matrix_world * local_verts[0].co
				end_co   = ob.matrix_world * local_verts[-1].co
				if begin_co.z < end_co.z: local_verts.reverse()
				
				# カーブとオブジェクトを新規作成してリンク
				name = ob.name + ":HairCurve"
				curve = context.blend_data.curves.new(name, 'CURVE')
				curve_ob = context.blend_data.objects.new(name, curve)
				curve_ob.matrix_world = mathutils.Matrix.Translation(ob.matrix_world * local_verts[0].co)
				context.scene.objects.link(curve_ob)
				new_objects.append(curve_ob)
				
				# カーブの設定
				curve.dimensions = '3D'
				
				# スプライン＆ポイントを作成
				spline = curve.splines.new('NURBS')
				spline.points.add(len(local_verts) - 1)
				for point, vert in zip(spline.points, local_verts):
					point.co = list(curve_ob.matrix_world.inverted() * (ob.matrix_world * vert.co))[:] + [1.0]
				
				# スプラインの設定
				spline.order_u = 3
				spline.use_endpoint_u = True
			
			bm.free()
			context.scene.objects.unlink(ob)
		
		# 新規オブジェクトをアクティブ＆選択
		if len(new_objects): context.scene.objects.active = new_objects[0]
		for new_object in new_objects: new_object.select = True
		
		return {'FINISHED'}
