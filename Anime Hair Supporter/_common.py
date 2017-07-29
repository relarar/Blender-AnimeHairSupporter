import bpy, math, mathutils
from . import _common

def relocation_taper_and_bevel(main_ob, sub_ob, is_taper):
	# 位置変更
	if len(main_ob.data.splines):
		if len(main_ob.data.splines[0].points):
			end_co = main_ob.matrix_world * mathutils.Vector(main_ob.data.splines[0].points[-1].co[:3])
			sub_ob.location = end_co.copy()
	
	# 回転変更
	if len(main_ob.data.splines):
		spline = main_ob.data.splines[0]
		if 2 <= len(spline.points):
			# 最後の辺をトラック
			sub_ob.rotation_mode = 'QUATERNION'
			last_direction = main_ob.matrix_world * mathutils.Vector(spline.points[-2].co[:3]) - main_ob.matrix_world * mathutils.Vector(spline.points[-1].co[:3])
			up_direction = mathutils.Vector((0, 0, 1))
			sub_ob.rotation_quaternion = up_direction.rotation_difference(last_direction)
			# Z回転
			diff_co = main_ob.matrix_world * mathutils.Vector(spline.points[-1].co[:3]) - main_ob.matrix_world * mathutils.Vector(spline.points[0].co[:3])
			rotation_z = math.atan2(diff_co.y, diff_co.x) - spline.points[-1].tilt
			if is_taper: sub_ob.rotation_quaternion *= mathutils.Quaternion((0, 0, 1), rotation_z)
			else       : sub_ob.rotation_quaternion *= mathutils.Quaternion((0, 0, 1), rotation_z - math.radians(90))
