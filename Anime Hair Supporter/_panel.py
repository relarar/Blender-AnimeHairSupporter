import bpy

class VIEW3D_PT_tools_anime_hair_supporter(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = 'Tools'
	bl_context = 'objectmode'
	bl_label = "アニメ髪支援"
	bl_options = {'DEFAULT_CLOSED'}
	
	def draw(self, context):
		column = self.layout.column(align=True)
		row = column.row(align=True)
		row.operator('object.ahs_convert_mesh_to_curve', icon='CURVE_NCURVE')
		row.enabled = bool( len([o for o in context.selected_objects if o.type == 'MESH']) )
		row = column.row(align=True)
		row.operator('object.ahs_convert_curve_to_mesh', icon='FILE_PARENT')
		row.enabled = bool( len([o for o in context.selected_objects if o.type == 'CURVE']) )
		
		
		
		# メインカーブ
		box = self.layout.box()
		box.label("メインカーブ", icon='MAN_ROT')
		
		# 肉付け関係
		row = box.row(align=True)
		row.operator('object.ahs_maincurve_fleshout', icon='MESH_CAPSULE')
		row.operator('object.ahs_maincurve_fleshlose', text="", icon='X')
		
		column = box.column(align=True)
		# 余剰変形
		column.operator('object.ahs_maincurve_extra_deform', icon='PARTICLE_PATH')
		# グラデーションひねり
		column.operator('object.ahs_maincurve_gradation_tilt', icon='FORCE_MAGNETIC')
		
		# サブツール
		column = box.column(align=True)
		row = column.row(align=True)
		row.operator('object.ahs_maincurve_select', icon='RESTRICT_SELECT_OFF')
		row.operator('object.ahs_maincurve_hide', text="表示", icon='VISIBLE_IPO_ON').is_hide = False
		row.operator('object.ahs_maincurve_hide', text="隠す", icon='VISIBLE_IPO_OFF').is_hide = True
		
		# 解像度
		row = column.split(percentage=0.59, align=True)
		try: is_successed = context.active_object.data.taper_object and context.active_object.data.bevel_object and context.active_object.data.splines.active
		except: is_successed = False
		if is_successed: row.prop(context.active_object.data.splines.active, 'resolution_u', text="解像度")
		else: row.label(text="解像度:")
		# 次数
		try: is_successed = context.active_object.data.taper_object and context.active_object.data.bevel_object and context.active_object.data.splines.active
		except: is_successed = False
		if is_successed: row.prop(context.active_object.data.splines.active, 'order_u', text="次数", slider=True)
		else: row.label(text="次数:")
		
		# アクティブ化
		row = box.row(align=True)
		row.operator('object.ahs_maincurve_activate_taper', text="テーパーへ", icon='ZOOM_SELECTED').mode = 'TAPER'
		row.operator('object.ahs_maincurve_activate_taper', text="ベベルへ", icon='ZOOM_SELECTED').mode = 'BEVEL'
		
		
		
		# テーパーカーブ
		box = self.layout.box()
		row = box.row(align=False)
		row.label("テーパーカーブ", icon='CURVE_NCURVE')
		row.operator('object.ahs_tapercurve_id_singlize', text="", icon='COPY_ID')
		
		# 位置を再設定とか
		row = box.split(percentage=0.6, align=False)
		row_sub = row.row(align=True)
		row_sub.operator('object.ahs_tapercurve_move', icon='PARTICLE_TIP').mode = 'TAPER'
		row_sub.operator('object.ahs_tapercurve_move', text="", icon='OUTLINER_DATA_ARMATURE').mode = 'BOTH'
		op = row.operator('object.ahs_tapercurve_mirror', icon='MOD_MIRROR')
		op.mode, op.is_mirror_x, op.is_mirror_y = 'TAPER', False, True
		
		# サブツール
		column = box.column(align=True)
		row = column.row(align=True)
		row.operator('object.ahs_tapercurve_select', icon='RESTRICT_SELECT_OFF').mode = 'TAPER'
		op = row.operator('object.ahs_tapercurve_hide', text="表示", icon='VISIBLE_IPO_ON')
		op.mode, op.is_hide = 'TAPER', False
		op = row.operator('object.ahs_tapercurve_hide', text="隠す", icon='VISIBLE_IPO_OFF')
		op.mode, op.is_hide = 'TAPER', True
		
		# 解像度
		try:
			column.prop(context.active_object.data.taper_object.data.splines.active, 'resolution_u', text="解像度")
			is_successed = True
		except: is_successed = False
		if not is_successed:
			taper_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object]
			try:
				if context.active_object in taper_objects:
					column.prop(context.active_object.data.splines.active, 'resolution_u', text="解像度")
					is_successed = True
			except: is_successed = False
		if not is_successed: column.label(text="解像度:")
		
		# アクティブ化
		box.operator('object.ahs_tapercurve_activate_main', icon='ZOOM_SELECTED')
		
		
		
		# ベベルカーブ
		box = self.layout.box()
		row = box.row(align=False)
		row.label("ベベルカーブ", icon='SURFACE_NCIRCLE')
		row.operator('object.ahs_tapercurve_id_singlize', text="", icon='COPY_ID')
		
		# 位置を再設定とか
		row = box.split(percentage=0.6, align=False)
		row_sub = row.row(align=True)
		row_sub.operator('object.ahs_tapercurve_move', icon='PARTICLE_TIP').mode = 'BEVEL'
		row_sub.operator('object.ahs_tapercurve_move', text="", icon='OUTLINER_DATA_ARMATURE').mode = 'BOTH'
		op = row.operator('object.ahs_tapercurve_mirror', icon='MOD_MIRROR')
		op.mode, op.is_mirror_x, op.is_mirror_y = 'BEVEL', True, False
		
		# サブツール
		column = box.column(align=True)
		row = column.row(align=True)
		row.operator('object.ahs_tapercurve_select', icon='RESTRICT_SELECT_OFF').mode = 'BEVEL'
		op = row.operator('object.ahs_tapercurve_hide', text="表示", icon='VISIBLE_IPO_ON')
		op.mode, op.is_hide = 'BEVEL', False
		op = row.operator('object.ahs_tapercurve_hide', text="隠す", icon='VISIBLE_IPO_OFF')
		op.mode, op.is_hide = 'BEVEL', True
		
		# 解像度
		try:
			column.prop(context.active_object.data.bevel_object.data.splines.active, 'resolution_u', text="解像度")
			is_successed = True
		except: is_successed = False
		if not is_successed:
			bevel_objects = [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
			try:
				if context.active_object in bevel_objects:
					column.prop(context.active_object.data.splines.active, 'resolution_u', text="解像度")
					is_successed = True
			except: is_successed = False
		if not is_successed: column.label(text="解像度:")
		
		# アクティブ化
		box.operator('object.ahs_tapercurve_activate_main', icon='ZOOM_SELECTED')
		
		
		
		row = self.layout.row(align=True)
		row.operator('object.convert', text="メッシュ化", icon='MESH_ICOSPHERE').target = 'MESH'
		for ob in context.selected_objects:
			if ob.type != 'CURVE': continue
			if ob.data.taper_object and ob.data.bevel_object:
				row.enabled = True
				break
		else: row.enabled = False
