import re, bpy, bmesh, mathutils, webbrowser

def ArrangeName(name, flag=True):
	if flag:
		return re.sub(r'\.\d{3}$', "", name)
	return name

class vertex_group_transfer(bpy.types.Operator):
	bl_idname = 'object.vertex_group_transfer'
	bl_label = "クイック・ウェイト転送"
	bl_description = "アクティブなメッシュに他の選択メッシュの頂点グループを転送します"
	bl_options = {'REGISTER', 'UNDO'}
	
	vertex_group_remove_all = bpy.props.BoolProperty(name="最初に頂点グループ全削除", default=True)
	vertex_group_clean = bpy.props.BoolProperty(name="ウェイト0.0の頂点はグループから除外", default=True)
	vertex_group_delete = bpy.props.BoolProperty(name="割り当ての無い頂点グループ削除", default=True)
	
	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) <= 1):
			return False
		source_objs = []
		for obj in context.selected_objects:
			if (obj.type == 'MESH' and context.object.name != obj.name):
				source_objs.append(obj)
		if (len(source_objs) <= 0):
			return False
		for obj in source_objs:
			if (1 <= len(obj.vertex_groups)):
				return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		self.layout.prop(self, 'vertex_group_remove_all')
		self.layout.prop(self, 'vertex_group_clean')
		self.layout.prop(self, 'vertex_group_delete')
	
	def execute(self, context):
		source_objs = []
		for obj in context.selected_objects:
			if (obj.type == 'MESH' and context.active_object.name != obj.name):
				source_objs.append(obj)
		if (0 < len(context.active_object.vertex_groups) and self.vertex_group_remove_all):
			bpy.ops.object.vertex_group_remove(all=True)
		me = context.active_object.data
		vert_mapping = 'NEAREST'
		for obj in source_objs:
			if (len(obj.data.polygons) <= 0):
				for obj2 in source_objs:
					if (len(obj.data.edges) <= 0):
						break
				else:
					vert_mapping = 'EDGEINTERP_NEAREST'
				break
		else:
			vert_mapping = 'POLYINTERP_NEAREST'
		try:
			bpy.ops.object.data_transfer(use_reverse_transfer=True, data_type='VGROUP_WEIGHTS', use_create=True, vert_mapping=vert_mapping, layers_select_src='ALL', layers_select_dst='NAME')
		except TypeError:
			bpy.ops.object.data_transfer(use_reverse_transfer=True, data_type='VGROUP_WEIGHTS', use_create=True, vert_mapping=vert_mapping, layers_select_src='NAME', layers_select_dst='ALL')
		if (self.vertex_group_clean):
			bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0, keep_single=False)
		if (self.vertex_group_delete):
			obj = context.active_object
			for vg in obj.vertex_groups:
				for vert in obj.data.vertices:
					try:
						if (vg.weight(vert.index) > 0.0):
							break
					except RuntimeError:
						pass
				else:
					obj.vertex_groups.remove(vg)
		return {'FINISHED'}

class blur_vertex_group(bpy.types.Operator):
	bl_idname = 'object.blur_vertex_group'
	bl_label = "頂点グループぼかし"
	bl_description = "アクティブ、もしくは全ての頂点グループをぼかします"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('ACTIVE', "アクティブのみ", "", 1),
		('ALL', "全て", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="対象頂点グループ", default='ACTIVE')
	blur_count = bpy.props.IntProperty(name="処理回数", default=10, min=1, max=100, soft_min=1, soft_max=100, step=1)
	use_clean = bpy.props.BoolProperty(name="ウェイト0.0の頂点は頂点グループから除外", default=True)
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'MESH':
				if ob.vertex_groups.active:
					return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		self.layout.prop(self, 'mode')
		self.layout.prop(self, 'blur_count')
		self.layout.prop(self, 'use_clean')
	
	def execute(self, context):
		activeObj = context.active_object
		pre_mode = activeObj.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		me = activeObj.data
		target_weights = []
		if (self.mode == 'ACTIVE'):
			target_weights.append(activeObj.vertex_groups.active)
		elif (self.mode == 'ALL'):
			for vg in activeObj.vertex_groups:
				target_weights.append(vg)
		bm = bmesh.new()
		bm.from_mesh(me)
		for count in range(self.blur_count):
			for vg in target_weights:
				vg_index = vg.index
				new_weights = []
				for vert in bm.verts:
					for group in me.vertices[vert.index].groups:
						if (group.group == vg_index):
							my_weight = group.weight
							break
					else:
						my_weight = 0.0
					near_weights = []
					for edge in vert.link_edges:
						for v in edge.verts:
							if (v.index != vert.index):
								edges_vert = v
								break
						for group in me.vertices[edges_vert.index].groups:
							if (group.group == vg_index):
								near_weights.append(group.weight)
								break
						else:
							near_weights.append(0.0)
					near_weight_average = 0
					for weight in near_weights:
						near_weight_average += weight
					try:
						near_weight_average /= len(near_weights)
					except ZeroDivisionError:
						near_weight_average = 0.0
					new_weights.append( (my_weight*2 + near_weight_average) / 3 )
				for vert, weight in zip(me.vertices, new_weights):
					if (self.use_clean and weight <= 0.000001):
						vg.remove([vert.index])
					else:
						vg.add([vert.index], weight, 'REPLACE')
		bm.free()
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class radius_blur_vertex_group(bpy.types.Operator):
	bl_idname = 'object.radius_blur_vertex_group'
	bl_label = "頂点グループ範囲ぼかし"
	bl_description = "アクティブ、もしくは全ての頂点グループを一定の範囲でぼかします"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('ACTIVE', "アクティブのみ", "", 1),
		('ALL', "全て", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="対象頂点グループ", default='ACTIVE')
	radius_multi = bpy.props.FloatProperty(name="範囲：辺の長さの平均×", default=2, min=0.1, max=10, soft_min=0.1, soft_max=10, step=10, precision=1)
	blur_count = bpy.props.IntProperty(name="処理回数", default=10, min=1, max=100, soft_min=1, soft_max=100, step=1)
	use_clean = bpy.props.BoolProperty(name="ウェイト0.0は頂点グループから除外", default=True)
	fadeout = bpy.props.BoolProperty(name="距離で影響減退", default=False)
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'MESH':
				if ob.vertex_groups.active:
					return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		self.layout.prop(self, 'mode')
		self.layout.prop(self, 'radius_multi')
		self.layout.prop(self, 'blur_count')
		self.layout.prop(self, 'use_clean')
		self.layout.prop(self, 'fadeout')
	
	def execute(self, context):
		ob = context.active_object
		me = ob.data
		
		bm = bmesh.new()
		bm.from_mesh(me)
		total_len = 0.0
		for edge in bm.edges:
			total_len += edge.calc_length()
		radius = (total_len / len(bm.edges)) * self.radius_multi
		bm.free()
		
		pre_mode = ob.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		target_weights = []
		if (self.mode == 'ACTIVE'):
			target_weights.append(ob.vertex_groups.active)
		elif (self.mode == 'ALL'):
			for vg in ob.vertex_groups:
				target_weights.append(vg)
		kd = mathutils.kdtree.KDTree(len(me.vertices))
		for i, v in enumerate(me.vertices):
			kd.insert(v.co, i)
		kd.balance()
		for count in range(self.blur_count):
			for vg in target_weights:
				new_weights = []
				for vert in me.vertices:
					for group in vert.groups:
						if group.group == vg.index:
							active_weight = group.weight
							break
					else:
						active_weight = 0.0
					near_weights = []
					near_weights_len = []
					for co, index, dist in kd.find_range(vert.co, radius):
						if index != vert.index:
							if self.fadeout:
								vec = co - vert.co
								near_weights_len.append(radius - vec.length)
							for group in me.vertices[index].groups:
								if group.group == vg.index:
									near_weights.append(group.weight)
									break
							else:
								near_weights.append(0.0)
					near_weight_average = 0.0
					near_weights_total = 0
					for weight_index, weight in enumerate(near_weights):
						if not self.fadeout:
							near_weight_average += weight
							near_weights_total += 1
						else:
							multi = near_weights_len[weight_index] / radius
							near_weight_average += weight * multi
							near_weights_total += multi
					try:
						near_weight_average /= near_weights_total
					except ZeroDivisionError:
						near_weight_average = 0.0
					new_weights.append( (active_weight*2 + near_weight_average) / 3 )
				for vert, weight in zip(me.vertices, new_weights):
					if (self.use_clean and weight <= 0.000001):
						vg.remove([vert.index])
					else:
						vg.add([vert.index], weight, 'REPLACE')
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class convert_cm3d2_vertex_group_names(bpy.types.Operator):
	bl_idname = "object.convert_cm3d2_vertex_group_names"
	bl_label = "頂点グループ名をCM3D2用←→Blender用に変換"
	bl_description = "CM3D2で使われてるボーン名(頂点グループ名)をBlenderで左右対称編集できるように相互変換します"
	bl_options = {'REGISTER', 'UNDO'}
	
	restore = bpy.props.BoolProperty(name="復元", default=False)
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'MESH':
				if ob.vertex_groups.active:
					return True
		return False
	
	def execute(self, context):
		ob = context.active_object
		for vg in ob.vertex_groups:
			if not self.restore:
				direction = re.search(r'[_ ]([rRlL])[_ ]', vg.name)
				if direction:
					direction = direction.groups()[0]
					vg_name = re.sub(r'([_ ])[rRlL]([_ ])', r'\1*\2', vg.name) + "." + direction
					self.report(type={'INFO'}, message=vg.name +" → "+ vg_name)
					vg.name = vg_name
			else:
				if vg.name.count('*') == 1:
					direction = re.search(r'\.([rRlL])$', vg.name)
					if direction:
						direction = direction.groups()[0]
						vg_name = re.sub(r'\.[rRlL]$', '', vg.name).replace('*', direction)
						vg_name = re.sub(r'([_ ])\*([_ ])', r'\1'+direction+r'\2', vg_name)
						self.report(type={'INFO'}, message=vg.name +" → "+ vg_name)
						vg.name = vg_name
		return {'FINISHED'}

class shape_key_transfer_ex(bpy.types.Operator):
	bl_idname = 'object.shape_key_transfer_ex'
	bl_label = "シェイプキー強制転送"
	bl_description = "頂点数の違うメッシュ同士でも一番近い頂点からシェイプキーを強制転送します"
	bl_options = {'REGISTER', 'UNDO'}
	
	remove_empty_shape = bpy.props.BoolProperty(name="全頂点に変形のないシェイプを削除", default=True)
	
	@classmethod
	def poll(cls, context):
		if len(context.selected_objects) != 2:
			return False
		for ob in context.selected_objects:
			if ob.type != 'MESH':
				return False
			if ob.name != context.active_object.name:
				if not ob.data.shape_keys:
					return False
		if context.active_object.mode != 'OBJECT':
			return False
		return True
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		self.layout.prop(self, 'remove_empty_shape')
	
	def execute(self, context):
		target_ob = context.active_object
		for ob in context.selected_objects:
			if ob.name != target_ob.name:
				source_ob = ob
		bm = bmesh.new()
		bm.from_mesh(source_ob.data)
		bm.faces.ensure_lookup_table()
		kd = mathutils.kdtree.KDTree(len(bm.verts))
		for i, vert in enumerate(bm.verts):
			kd.insert(vert.co.copy(), i)
		kd.balance()
		is_first = True
		for key_block in source_ob.data.shape_keys.key_blocks:
			if is_first:
				is_first = False
				if not target_ob.data.shape_keys:
					target_shape = target_ob.shape_key_add(name=key_block.name, from_mix=False)
				continue
			if key_block.name not in target_ob.data.shape_keys.key_blocks.keys():
				target_shape = target_ob.shape_key_add(name=key_block.name, from_mix=False)
			else:
				target_shape = target_ob.data.shape_keys.key_blocks[key_block.name]
			is_shaped = False
			for target_vert in target_ob.data.vertices:
				co, index, dist = kd.find(target_vert.co)
				total_diff = key_block.data[index].co - source_ob.data.vertices[index].co
				target_shape.data[target_vert.index].co = target_ob.data.vertices[target_vert.index].co + total_diff
				if not is_shaped and 0.001 <= total_diff.length:
					is_shaped = True
			if not is_shaped and self.remove_empty_shape:
				target_ob.shape_key_remove(target_shape)
		return {'FINISHED'}

class scale_shape_key(bpy.types.Operator):
	bl_idname = 'object.scale_shape_key'
	bl_label = "シェイプキーの変形を拡大/縮小"
	bl_description = "シェイプキーの変形を強力にしたり、もしくは弱くできます"
	bl_options = {'REGISTER', 'UNDO'}
	
	multi = bpy.props.FloatProperty(name="倍率", description="シェイプキーの拡大率です", default=1.1, min=-10, max=10, soft_min=-10, soft_max=10, step=10, precision=2)
	items = [
		('ACTIVE', "アクティブのみ", "", 1),
		('ALL', "全て", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="対象シェイプキー", default='ACTIVE')
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			ob = context.active_object
			if ob.type == 'MESH':
				if ob.active_shape_key:
					return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		self.layout.prop(self, 'multi')
		self.layout.prop(self, 'mode')
	
	def execute(self, context):
		ob = context.active_object
		me = ob.data
		shape_keys = me.shape_keys
		pre_mode = ob.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		if self.mode == 'ACTIVE':
			target_shapes = [ob.active_shape_key]
		elif self.mode == 'ALL':
			target_shapes = []
			for key_block in shape_keys.key_blocks:
				target_shapes.append(key_block)
		for shape in target_shapes:
			data = shape.data
			for i, vert in enumerate(me.vertices):
				diff = data[i].co - vert.co
				diff *= self.multi
				data[i].co = vert.co + diff
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class blur_shape_key(bpy.types.Operator):
	bl_idname = 'object.blur_shape_key'
	bl_label = "シェイプキーぼかし"
	bl_description = "シェイプキーの変形をぼかしてなめらかにします"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('ACTIVE', "アクティブのみ", "", 1),
		('ALL', "全て", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="対象シェイプキー", default='ACTIVE')
	strength = bpy.props.IntProperty(name="処理回数", description="ぼかしの強度(回数)を設定します", default=10, min=1, max=100, soft_min=1, soft_max=100, step=1)
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			ob = context.active_object
			if ob.type == 'MESH':
				if ob.active_shape_key:
					return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		self.layout.prop(self, 'mode')
		self.layout.prop(self, 'strength')
	
	def execute(self, context):
		ob = context.active_object
		me = ob.data
		shape_keys = me.shape_keys
		bm = bmesh.new()
		bm.from_mesh(me)
		pre_mode = ob.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		if self.mode == 'ACTIVE':
			target_shapes = [ob.active_shape_key]
		elif self.mode == 'ALL':
			target_shapes = []
			for key_block in shape_keys.key_blocks:
				target_shapes.append(key_block)
		for i, vert in enumerate(bm.verts):
			near_verts = []
			for edge in vert.link_edges:
				for v in edge.verts:
					if vert.index != v.index:
						near_verts.append(v)
						break
			for shape in target_shapes:
				for s in range(self.strength):
					data = shape.data
					average = mathutils.Vector((0, 0, 0))
					for v in near_verts:
						average += data[v.index].co - me.vertices[v.index].co
					average /= len(near_verts)
					co = data[i].co - vert.co
					data[i].co = ((co * 2) + average) / 3 + vert.co
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class radius_blur_shape_key(bpy.types.Operator):
	bl_idname = 'object.radius_blur_shape_key'
	bl_label = "シェイプキー範囲ぼかし"
	bl_description = "シェイプキーの変形を範囲でぼかしてなめらかにします"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('ACTIVE', "アクティブのみ", "", 1),
		('ALL', "全て", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="対象シェイプキー", default='ACTIVE')
	radius_multi = bpy.props.FloatProperty(name="範囲：辺の長さの平均×", default=2, min=0.1, max=10, soft_min=0.1, soft_max=10, step=10, precision=1)
	blur_count = bpy.props.IntProperty(name="処理回数", default=10, min=1, max=100, soft_min=1, soft_max=100, step=1)
	fadeout = bpy.props.BoolProperty(name="距離で影響減退", default=False)
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			ob = context.active_object
			if ob.type == 'MESH':
				if ob.active_shape_key:
					return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		self.layout.prop(self, 'mode')
		self.layout.prop(self, 'radius_multi')
		self.layout.prop(self, 'blur_count')
		self.layout.prop(self, 'fadeout')
	
	def execute(self, context):
		ob = context.active_object
		me = ob.data
		
		bm = bmesh.new()
		bm.from_mesh(me)
		total_len = 0.0
		for edge in bm.edges:
			total_len += edge.calc_length()
		radius = (total_len / len(bm.edges)) * self.radius_multi
		bm.free()
		
		shape_keys = me.shape_keys
		pre_mode = ob.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		if self.mode == 'ACTIVE':
			target_shapes = [ob.active_shape_key]
		elif self.mode == 'ALL':
			target_shapes = []
			for key_block in shape_keys.key_blocks:
				target_shapes.append(key_block)
		kd = mathutils.kdtree.KDTree(len(me.vertices))
		for i, v in enumerate(me.vertices):
			kd.insert(v.co, i)
		kd.balance()
		for count in range(self.blur_count):
			for shape in target_shapes:
				data = shape.data
				new_co = []
				for vert in me.vertices:
					average_co = mathutils.Vector((0, 0, 0))
					nears = kd.find_range(vert.co, radius)
					nears_total = 0
					for co, index, dist in nears:
						if self.fadeout:
							diff = co - vert.co
							multi = (radius - diff.length) / radius
							average_co += (data[index].co - me.vertices[index].co) * multi
							nears_total += multi
						else:
							average_co += data[index].co - me.vertices[index].co
							nears_total += 1
					average_co /= nears_total
					co = data[vert.index].co - vert.co
					new_co.append(((co * 2) + average_co) / 3 + vert.co)
					#data[vert.index].co = ((co * 2) + average_co) / 3 + vert.co
				for i, co in enumerate(new_co):
					data[i].co = co.copy()
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class new_cm3d2(bpy.types.Operator):
	bl_idname = 'material.new_cm3d2'
	bl_label = "CM3D2用マテリアルを新規作成"
	bl_description = "Blender-CM3D2-Converterで使用できるマテリアルを新規で作成します"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('COMMON', "汎用", "", 1),
		('TRANS', "透過", "", 2),
		('HAIR', "髪", "", 3),
		('MOZA', "モザイク", "", 4),
		]
	type = bpy.props.EnumProperty(items=items, name="マテリアルのタイプ", default='COMMON')
	
	@classmethod
	def poll(cls, context):
		if 'material' in dir(context):
			if not context.material:
				return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def draw(self, context):
		self.layout.prop(self, 'type')
	
	def execute(self, context):
		ob = context.active_object
		ob_names = ob.name.split('.')
		if not context.material_slot:
			bpy.ops.object.material_slot_add()
		mate = context.blend_data.materials.new(ob_names[0])
		context.material_slot.material = mate
		tex_list, col_list, f_list = [], [], []
		if self.type == 'COMMON':
			mate['shader1'] = 'CM3D2/Toony_Lighted_Outline'
			mate['shader2'] = 'CM3D2__Toony_Lighted_Outline'
			tex_list.append(("_MainTex", ob_names[0], "Assets\\texture\\texture\\" + ob_names[0] + ".png"))
			tex_list.append(("_ToonRamp", "toonGrayA1", r"Assets\texture\texture\toon\toonGrayA1.png"))
			tex_list.append(("_ShadowTex", ob_names[0] + "_shadow", "Assets\\texture\\texture\\" + ob_names[0] + "_shadow.png"))
			tex_list.append(("_ShadowRateToon", "toonDress_shadow", r"Assets\texture\texture\toon\toonDress_shadow.png"))
			col_list.append(("_Color", (1, 1, 1, 1)))
			col_list.append(("_ShadowColor", (0, 0, 0, 1)))
			col_list.append(("_RimColor", (0.5, 0.5, 0.5, 1)))
			col_list.append(("_OutlineColor", (0, 0, 0, 1)))
			col_list.append(("_ShadowColor", (0, 0, 0, 1)))
			f_list.append(("_Shininess", 0))
			f_list.append(("_OutlineWidth", 0.002))
			f_list.append(("_RimPower", 25))
			f_list.append(("_RimShift", 0))
		elif self.type == 'TRANS':
			mate['shader1'] = 'CM3D2/Toony_Lighted_Trans'
			mate['shader2'] = 'CM3D2__Toony_Lighted_Trans'
			tex_list.append(("_MainTex", ob_names[0], "Assets\\texture\\texture\\" + ob_names[0] + ".png"))
			tex_list.append(("_ToonRamp", "toonGrayA1", r"Assets\texture\texture\toon\toonGrayA1.png"))
			tex_list.append(("_ShadowTex", ob_names[0] + "_shadow", "Assets\\texture\\texture\\" + ob_names[0] + "_shadow.png"))
			tex_list.append(("_ShadowRateToon", "toonDress_shadow", r"Assets\texture\texture\toon\toonDress_shadow.png"))
			col_list.append(("_Color", (1, 1, 1, 1)))
			col_list.append(("_ShadowColor", (0, 0, 0, 1)))
			col_list.append(("_RimColor", (0.5, 0.5, 0.5, 1)))
			col_list.append(("_ShadowColor", (0, 0, 0, 1)))
			f_list.append(("_Shininess", 0))
			f_list.append(("_RimPower", 25))
			f_list.append(("_RimShift", 0))
		elif self.type == 'HAIR':
			mate['shader1'] = 'CM3D2/Toony_Lighted_Hair_Outline'
			mate['shader2'] = 'CM3D2__Toony_Lighted_Hair_Outline'
			tex_list.append(("_MainTex", ob_names[0], "Assets\\texture\\texture\\" + ob_names[0] + ".png"))
			tex_list.append(("_ToonRamp", "toonGrayA1", r"Assets\texture\texture\toon\toonGrayA1.png"))
			tex_list.append(("_ShadowTex", ob_names[0] + "_shadow", "Assets\\texture\\texture\\" + ob_names[0] + "_shadow.png"))
			tex_list.append(("_ShadowRateToon", "toonDress_shadow", r"Assets\texture\texture\toon\toonDress_shadow.png"))
			tex_list.append(("_HiTex", ob_names[0] + "_s", r"Assets\texture\texture\***_s.png"))
			col_list.append(("_Color", (1, 1, 1, 1)))
			col_list.append(("_ShadowColor", (0, 0, 0, 1)))
			col_list.append(("_RimColor", (0.5, 0.5, 0.5, 1)))
			col_list.append(("_OutlineColor", (0, 0, 0, 1)))
			col_list.append(("_ShadowColor", (0, 0, 0, 1)))
			f_list.append(("_Shininess", 0))
			f_list.append(("_OutlineWidth", 0.002))
			f_list.append(("_RimPower", 25))
			f_list.append(("_RimShift", 0))
			f_list.append(("_HiRate", 0.5))
			f_list.append(("_HiPow", 0.001))
		elif self.type == 'MOZA':
			mate['shader1'] = 'CM3D2/Mosaic'
			mate['shader2'] = 'CM3D2__Mosaic'
			tex_list.append(("_RenderTex", ""))
			f_list.append(("_FloatValue1", 30))
		slot_count = 0
		for data in tex_list:
			slot = mate.texture_slots.create(slot_count)
			tex = context.blend_data.textures.new(data[0], 'IMAGE')
			slot.texture = tex
			if data[1] == "":
				slot_count += 1
				continue
			slot.color = [0, 0, 1]
			img = context.blend_data.images.new(data[1], 128, 128)
			img.filepath = data[2]
			img.source = 'FILE'
			tex.image = img
			slot_count += 1
		for data in col_list:
			slot = mate.texture_slots.create(slot_count)
			mate.use_textures[slot_count] = False
			slot.color = data[1][:3]
			slot.diffuse_color_factor = data[1][3]
			slot.use_rgb_to_intensity = True
			tex = context.blend_data.textures.new(data[0], 'IMAGE')
			slot.texture = tex
			slot_count += 1
		for data in f_list:
			slot = mate.texture_slots.create(slot_count)
			mate.use_textures[slot_count] = False
			slot.diffuse_color_factor = data[1]
			tex = context.blend_data.textures.new(data[0], 'IMAGE')
			slot.texture = tex
			slot_count += 1
		return {'FINISHED'}

class convert_cm3d2_bone_names(bpy.types.Operator):
	bl_idname = "armature.convert_cm3d2_bone_names"
	bl_label = "ボーン名をCM3D2用←→Blender用に変換"
	bl_description = "CM3D2で使われてるボーン名をBlenderで左右対称編集できるように相互変換します"
	bl_options = {'REGISTER', 'UNDO'}
	
	restore = bpy.props.BoolProperty(name="復元", default=False)
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if ob:
			if ob.type == 'ARMATURE':
				return True
		return False
	
	def execute(self, context):
		ob = context.active_object
		arm = ob.data
		for bone in arm.bones:
			if not self.restore:
				direction = re.search(r'[_ ]([rRlL])[_ ]', bone.name)
				if direction:
					direction = direction.groups()[0]
					bone_name = re.sub(r'([_ ])[rRlL]([_ ])', r'\1*\2', bone.name) + "." + direction
					self.report(type={'INFO'}, message=bone.name +" → "+ bone_name)
					bone.name = bone_name
			else:
				if bone.name.count('*') == 1:
					direction = re.search(r'\.([rRlL])$', bone.name)
					if direction:
						direction = direction.groups()[0]
						bone_name = re.sub(r'\.[rRlL]$', '', bone.name)
						bone_name = re.sub(r'([_ ])\*([_ ])', r'\1'+direction+r'\2', bone_name)
						self.report(type={'INFO'}, message=bone.name +" → "+ bone_name)
						bone.name = bone_name
		return {'FINISHED'}

class show_apply_modifier_addon_web(bpy.types.Operator):
	bl_idname = "object.show_apply_modifier_addon_web"
	bl_label = "モディファイアを適用できない場合"
	bl_description = "Apply ModifierのWEBサイトを開きます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		webbrowser.open("https://sites.google.com/site/matosus304blendernotes/home/download#apply_modifier")
		return {'FINISHED'}

# 頂点グループメニューに項目追加
def MESH_MT_vertex_group_specials(self, context):
	self.layout.separator()
	self.layout.operator(vertex_group_transfer.bl_idname, icon='SPACE2')
	self.layout.separator()
	self.layout.operator(convert_cm3d2_vertex_group_names.bl_idname, icon='SPACE2', text="頂点グループ名を CM3D2 → Blender").restore = False
	self.layout.operator(convert_cm3d2_vertex_group_names.bl_idname, icon='SPACE2', text="頂点グループ名を Blender → CM3D2").restore = True
	self.layout.separator()
	self.layout.operator(blur_vertex_group.bl_idname, icon='SPACE2')
	self.layout.operator(radius_blur_vertex_group.bl_idname, icon='SPACE2')

# シェイプメニューに項目追加
def MESH_MT_shape_key_specials(self, context):
	self.layout.separator()
	self.layout.operator(shape_key_transfer_ex.bl_idname, icon='SPACE2')
	self.layout.separator()
	self.layout.operator(scale_shape_key.bl_idname, icon='SPACE2')
	self.layout.separator()
	self.layout.operator(blur_shape_key.bl_idname, icon='SPACE2')
	self.layout.operator(radius_blur_shape_key.bl_idname, icon='SPACE2')

# マテリアルタブに項目追加
def MATERIAL_PT_context_material(self, context):
	mate = context.material
	if not mate:
		self.layout.operator(new_cm3d2.bl_idname, icon='SPACE2')
	else:
		if 'shader1' in mate.keys() and 'shader2' in mate.keys():
			box = self.layout.box()
			box.label(text="CM3D2用", icon='SPACE2')
			box.prop(mate, '["shader1"]', icon='TEXTURE_SHADED', text="shader1")
			box.prop(mate, '["shader2"]', icon='TEXTURE_SHADED', text="shader2")

# アーマチュアタブに項目追加
def DATA_PT_context_arm(self, context):
	ob = context.active_object
	if ob:
		if ob.type == 'ARMATURE':
			col = self.layout.column(align=True)
			col.label(text="CM3D2用 ボーン名変換", icon='SPACE2')
			row = col.row(align=True)
			row.operator(convert_cm3d2_bone_names.bl_idname, text="CM3D2 → Blender").restore = False
			row.operator(convert_cm3d2_bone_names.bl_idname, text="Blender → CM3D2").restore = True
		arm = ob.data
		if 'BoneData:0' in arm.keys() and 'LocalBoneData:0' in arm.keys():
			self.layout.label(text="CM3D2用ボーン情報が存在", icon='CHECKBOX_HLT')

# オブジェクトタブに項目追加
def OBJECT_PT_context_object(self, context):
	ob = context.active_object
	if ob:
		if 'BoneData:0' in ob.keys() and 'LocalBoneData:0' in ob.keys():
			self.layout.label(text="CM3D2用ボーン情報が存在", icon='CHECKBOX_HLT')

# モディファイアタブに項目追加
def DATA_PT_modifiers(self, context):
	if 'apply_all_modifier' not in dir(bpy.ops.object):
		ob = context.active_object
		if ob:
			if ob.type == 'MESH':
				me = ob.data
				if me.shape_keys:
					if len(ob.modifiers):
						self.layout.operator(show_apply_modifier_addon_web.bl_idname, icon='SPACE2')

# テクスチャタブに項目追加
def TEXTURE_PT_context_texture(self, context):
	try:
		tex_slot = context.texture_slot
		tex = context.texture
	except:
		return
	if tex.name[0] != '_':
		return
	is_use = tex_slot.use
	is_rgb = tex_slot.use_rgb_to_intensity
	if is_use:
		type = "tex"
	else:
		if is_rgb:
			type = "col"
		else:
			type = "f"
	box = self.layout.box()
	box.label(text="CM3D2用", icon='SPACE2')
	box.label(text="設定値タイプ: " + type)
	box.prop(tex, 'name', icon='SORTALPHA', text="設定値名")
	if type == "tex":
		if tex.type == 'IMAGE':
			img = tex.image
			if img:
				if img.source == 'FILE':
					box.prop(img, 'name', icon='IMAGE_DATA', text="テクスチャ名")
					box.prop(img, 'filepath', text="テクスチャパス")
				box.prop(tex_slot, 'color', text="")
				box.prop(tex_slot, 'diffuse_color_factor', icon='IMAGE_RGB_ALPHA', text="色の透明度")
	elif type == "col":
		box.prop(tex_slot, 'color', text="")
		box.prop(tex_slot, 'diffuse_color_factor', icon='IMAGE_RGB_ALPHA', text="色の透明度")
	elif type == "f":
		box.prop(tex_slot, 'diffuse_color_factor', icon='ARROW_LEFTRIGHT', text="値")
	
	base_name = ArrangeName(tex.name)
	description = ""
	if base_name == '_MainTex':
		description = "面の色を決定するテクスチャを指定"
	elif base_name == '_ShadowTex':
		description = "陰部分の面の色を決定するテクスチャを指定"
	elif base_name == '_Color':
		description = "面の色を指定"
	elif base_name == '_ShadowColor':
		description = "影の色を指定"
	elif base_name == '_RimColor':
		description = "縁にできる光の反射の色を指定"
	elif base_name == '_OutlineColor':
		description = "輪郭線の色を指定"
	elif base_name == '_Shininess':
		description = "スペキュラーの強さを指定"
	elif base_name == '_OutlineWidth':
		description = "輪郭線の太さを指定"
	elif base_name == '_RimPower':
		description = "縁にできる光の反射の強さを指定"
	elif base_name == '_RimShift':
		description = "縁にできる光の反射の幅を指定"
	if description != "":
		sub_box = box.box()
		sub_box.label(text=description, icon='TEXT')
