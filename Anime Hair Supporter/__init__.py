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
	'wiki_url' : "https://github.com/saidenka/Blender-AnimeHairSupporter",
	'tracker_url' : "https://github.com/saidenka/Blender-AnimeHairSupporter",
	'category' : "Tools"
}

# サブスクリプト群をインポート
if 'bpy' in locals():
	import imp
	imp.reload(_panel)
	
	imp.reload(convert_edgemesh_to_curve)
	imp.reload(convert_curve_to_edgemesh)
	
	imp.reload(maincurve_activate)
	imp.reload(maincurve_volume_up)
	imp.reload(maincurve_volume_down)
	imp.reload(maincurve_extra_deform)
	imp.reload(maincurve_gradation_tilt)
	imp.reload(maincurve_select)
	imp.reload(maincurve_hide)
	imp.reload(maincurve_set_resolution)
	imp.reload(maincurve_set_order)
	
	imp.reload(tapercurve_activate)
	imp.reload(tapercurve_id_singlize)
	imp.reload(tapercurve_change_type)
	imp.reload(tapercurve_mirror)
	imp.reload(tapercurve_relocation)
	imp.reload(tapercurve_remove_alones)
	imp.reload(tapercurve_select)
	imp.reload(tapercurve_hide)
	
	imp.reload(convert_curve_to_armature)
	imp.reload(convert_curve_to_mesh)
else:
	from . import _panel
	
	from . import convert_edgemesh_to_curve
	from . import convert_curve_to_edgemesh
	
	from . import maincurve_activate
	from . import maincurve_volume_up
	from . import maincurve_volume_down
	from . import maincurve_extra_deform
	from . import maincurve_gradation_tilt
	from . import maincurve_select
	from . import maincurve_hide
	from . import maincurve_set_resolution
	from . import maincurve_set_order
	
	from . import tapercurve_activate
	from . import tapercurve_id_singlize
	from . import tapercurve_change_type
	from . import tapercurve_mirror
	from . import tapercurve_relocation
	from . import tapercurve_remove_alones
	from . import tapercurve_select
	from . import tapercurve_hide
	
	from . import convert_curve_to_armature
	from . import convert_curve_to_mesh

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
