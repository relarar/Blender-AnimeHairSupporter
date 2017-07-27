import bpy

class VIEW3D_PT_tools_anime_hair_supporter(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = 'Tools'
	bl_context = 'objectmode'
	bl_label = "アニメ髪支援"
	
	def draw(self, context):
		self.layout.operator('object.ahs_meshedge_to_curve', icon='CURVE_NCURVE')
		
		
		# メインカーブ
		box = self.layout.box()
		box.label("メインカーブ", icon='MAN_ROT')
		
		row = box.row(align=True)
		row.operator('object.ahs_maincurve_fleshout', icon='MESH_CAPSULE')
		row.operator('object.ahs_maincurve_fleshlose', text="", icon='X')
		
		row = box.row(align=True)
		row.operator('object.ahs_maincurve_select', icon='RESTRICT_SELECT_OFF')
		row.operator('object.ahs_maincurve_hide', text="表示", icon='VISIBLE_IPO_ON').is_hide = False
		row.operator('object.ahs_maincurve_hide', text="隠す", icon='VISIBLE_IPO_OFF').is_hide = True
		
		try: is_successed = context.active_object.data.taper_object and context.active_object.data.bevel_object and context.active_object.data.splines.active
		except: is_successed = False
		if is_successed: box.prop(context.active_object.data.splines.active, 'resolution_u', text="解像度")
		else: box.label(text="解像度:")
		
		
		# テーパーカーブ
		box = self.layout.box()
		box.label("テーパーカーブ", icon='CURVE_NCURVE')
		
		row = box.row(align=True)
		row.operator('object.ahs_tapercurve_select', icon='RESTRICT_SELECT_OFF').is_bevel = False
		op = row.operator('object.ahs_tapercurve_hide', text="表示", icon='VISIBLE_IPO_ON')
		op.is_bevel, op.is_hide = False, False
		op = row.operator('object.ahs_tapercurve_hide', text="隠す", icon='VISIBLE_IPO_OFF')
		op.is_bevel, op.is_hide = False, True
		box.operator('object.ahs_tapercurve_move', icon='PARTICLE_TIP').is_bevel = False
		
		try:
			box.prop(context.active_object.data.taper_object.data.splines.active, 'resolution_u', text="解像度")
			is_successed = True
		except: is_successed = False
		if not is_successed:
			taper_objects = [c.taper_object for c in context.blend_data.curves if c.taper_object]
			try:
				if context.active_object in taper_objects:
					box.prop(context.active_object.data.splines.active, 'resolution_u', text="解像度")
					is_successed = True
			except: is_successed = False
		if not is_successed: box.label(text="解像度:")
		
		
		# ベベルカーブ
		box = self.layout.box()
		box.label("ベベルカーブ", icon='SURFACE_NCIRCLE')
		
		row = box.row(align=True)
		row.operator('object.ahs_tapercurve_select', icon='RESTRICT_SELECT_OFF').is_bevel = True
		op = row.operator('object.ahs_tapercurve_hide', text="表示", icon='VISIBLE_IPO_ON')
		op.is_bevel, op.is_hide = True, False
		op = row.operator('object.ahs_tapercurve_hide', text="隠す", icon='VISIBLE_IPO_OFF')
		op.is_bevel, op.is_hide = True, True
		box.operator('object.ahs_tapercurve_move', icon='PARTICLE_TIP').is_bevel = True
		
		try:
			box.prop(context.active_object.data.bevel_object.data.splines.active, 'resolution_u', text="解像度")
			is_successed = True
		except: is_successed = False
		if not is_successed:
			bevel_objects = [c.bevel_object for c in context.blend_data.curves if c.bevel_object]
			try:
				if context.active_object in bevel_objects:
					box.prop(context.active_object.data.splines.active, 'resolution_u', text="解像度")
					is_successed = True
			except: is_successed = False
		if not is_successed: box.label(text="解像度:")
