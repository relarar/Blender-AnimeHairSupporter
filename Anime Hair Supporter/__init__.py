# アドオンを読み込む時に最初にこのファイルが読み込まれます

# アドオン情報
bl_info = {
	'name' : "Anime Hair Supporter",
	'author' : "saidenka",
	'version' : (1, 0),
	'blender' : (2, 7, 8),
	'location' : "3Dビュー > オブジェクトモード > ツールシェルフ > ツール > アニメ髪支援パネル",
	'description' : "",
	'warning' : "",
	'wiki_url' : "",
	'tracker_url' : "",
	'category' : "Tools"
}

# サブスクリプト群をインポート
if 'bpy' in locals():
	import imp
	imp.reload(_panel)
	
	imp.reload(convert_mesh_to_curve)
	imp.reload(convert_curve_to_mesh)
	
	imp.reload(maincurve_fleshout)
	imp.reload(maincurve_fleshlose)
	imp.reload(maincurve_extra_deform)
	imp.reload(maincurve_gradation_tilt)
	imp.reload(maincurve_select)
	imp.reload(maincurve_hide)
	imp.reload(maincurve_activate_taper)
	
	imp.reload(tapercurve_id_singlize)
	imp.reload(tapercurve_change_type)
	imp.reload(tapercurve_move)
	imp.reload(tapercurve_mirror)
	imp.reload(tapercurve_select)
	imp.reload(tapercurve_hide)
	imp.reload(tapercurve_activate_main)
else:
	from . import _panel
	
	from . import convert_mesh_to_curve
	from . import convert_curve_to_mesh
	
	from . import maincurve_fleshout
	from . import maincurve_fleshlose
	from . import maincurve_extra_deform
	from . import maincurve_gradation_tilt
	from . import maincurve_select
	from . import maincurve_hide
	from . import maincurve_activate_taper
	
	from . import tapercurve_id_singlize
	from . import tapercurve_change_type
	from . import tapercurve_move
	from . import tapercurve_mirror
	from . import tapercurve_select
	from . import tapercurve_hide
	from . import tapercurve_activate_main

# この位置に記述 (重要)
import bpy

# プラグインをインストールしたときの処理
def register():
	bpy.utils.register_module(__name__)

# プラグインをアンインストールしたときの処理
def unregister():
	bpy.utils.unregister_module(__name__)

# 最初に実行される
if __name__ == '__main__':
	register()
