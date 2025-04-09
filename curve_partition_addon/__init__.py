bl_info = {
    "name": "Planar Channel Partitioning",
    "blender": (4,4,0),
    "version": (0,1),
    "author": "ComicAddict",
    "category": "Object"
}

import bpy
from bpy_extras import view3d_utils
from bpy.utils import resource_path
from pathlib import Path
from math import radians
from bpy.app.handlers import persistent

def append_partition():
    USER = Path(resource_path('USER'))
    src = USER/"scripts/addons"/"curve_partition_addon"

    file_path = src/"GNs.blend"
    inner_path = "NodeTree"
    object_name = "PARTITION"
    bpy.ops.wm.append(
        filepath=str(file_path / inner_path / object_name),
        directory=str(file_path / inner_path),  
        filename = object_name
    )   

def append_one2many():
    USER = Path(resource_path('USER'))
    src = USER/"scripts/addons"/"curve_partition_addon"

    file_path = src/"GNs.blend"
    inner_path = "NodeTree"
    object_name = "ONE2MANY"
    bpy.ops.wm.append(
        filepath=str(file_path / inner_path / object_name),
        directory=str(file_path / inner_path),  
        filename = object_name
    )


def append_shape2shape():
    USER = Path(resource_path('USER'))
    src = USER/"scripts/addons"/"curve_partition_addon"

    file_path = src/"GNs.blend"
    inner_path = "NodeTree"
    object_name = "SHAPE2SHAPE"
    bpy.ops.wm.append(
        filepath=str(file_path / inner_path / object_name),
        directory=str(file_path / inner_path),  
        filename = object_name
    )

def append_layout_and_export():
    USER = Path(resource_path('USER'))
    src = USER/"scripts/addons"/"curve_partition_addon"

    file_path = src/"GNs.blend"
    inner_path = "NodeTree"
    object_name = "LAYOUT_AND_EXPORT"
    bpy.ops.wm.append(
        filepath=str(file_path / inner_path / object_name),
        directory=str(file_path / inner_path),  
        filename = object_name
    )

def append_transform():
    USER = Path(resource_path('USER'))
    src = USER/"scripts/addons"/"curve_partition_addon"

    file_path = src/"GNs.blend"
    inner_path = "NodeTree"
    object_name = "TRANSFORM"
    bpy.ops.wm.append(
        filepath=str(file_path / inner_path / object_name),
        directory=str(file_path / inner_path),  
        filename = object_name
    )

def main(context, event):
    """Run this function on left mouse, execute the ray cast"""
    # get the context arguments
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    ray_target = ray_origin + view_vector

    def visible_objects_and_duplis():
        """Loop over (object, matrix) pairs (mesh only)"""

        depsgraph = context.evaluated_depsgraph_get()
        for dup in depsgraph.object_instances:
            if dup.is_instance:  # Real dupli instance
                obj = dup.instance_object
                yield (obj, dup.matrix_world.copy())
            else:  # Usual object
                obj = dup.object
                yield (obj, obj.matrix_world.copy())

    def obj_ray_cast(obj, matrix):
        """Wrapper for ray casting that moves the ray into object space"""

        # get the ray relative to the object
        matrix_inv = matrix.inverted()
        ray_origin_obj = matrix_inv @ ray_origin
        ray_target_obj = matrix_inv @ ray_target
        ray_direction_obj = ray_target_obj - ray_origin_obj

        # cast the ray
        success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

        if success:
            return location, normal, face_index
        else:
            return None, None, None

    # cast rays and find the closest object
    best_length_squared = -1.0
    best_obj = None
    hit_world = (0,0,0)

    for obj, matrix in visible_objects_and_duplis():
        if obj.type == 'MESH':
            hit, normal, face_index = obj_ray_cast(obj, matrix)
            if hit is not None:
                hit_world = matrix @ hit
                # scene.cursor.location = hit_world
                length_squared = (hit_world - ray_origin).length_squared
                if best_obj is None or length_squared < best_length_squared:
                    best_length_squared = length_squared
                    best_obj = obj

    # now we have the object under the mouse cursor,
    # we could do lots of stuff but for the example just select.
    if best_obj is not None:
        # for selection etc. we need the original object,
        # evaluated objects are not in view-layer.
        best_original = best_obj.original
        best_original.select_set(True)
        context.view_layer.objects.active = best_original

    return hit_world

class TDP_OT_AddTransform(bpy.types.Operator):
    """Adds GN based Curve Transform block"""
    bl_idname = "curve_partition.add_transform"
    bl_label = "Add transform block"

    def execute(self, context):
        col_id = bpy.data.collections.find("CHANNELS")
        if col_id == -1:
            bpy.data.collections.new("CHANNELS")
            context.scene.collection.children.link(bpy.data.collections["CHANNELS"])
        col = bpy.data.collections['CHANNELS']

        if(bpy.data.node_groups.find('TRANSFORM') == -1):
            append_transform()
        gn = bpy.data.node_groups['TRANSFORM']

        resmesh = bpy.data.meshes.new("transform.001")
        resob = bpy.data.objects.new("transform.001", resmesh)

        col.objects.link(resob) 

        mod = resob.modifiers.new("LAYOUT",'NODES')
        mod.node_group = gn

        resob.data.update()

        return {'FINISHED'}

class TDP_OT_AddShape2Shape(bpy.types.Operator):
    """Adds GN based Shape2Shape block"""
    bl_idname = "curve_partition.add_shape2shape"
    bl_label = "Add shape2shape block"

    def execute(self, context):
        col_id = bpy.data.collections.find("CHANNELS")
        if col_id == -1:
            bpy.data.collections.new("CHANNELS")
            context.scene.collection.children.link(bpy.data.collections["CHANNELS"])
        col = bpy.data.collections['CHANNELS']

        if(bpy.data.node_groups.find('SHAPE2SHAPE') == -1):
            append_shape2shape()
        gn = bpy.data.node_groups['SHAPE2SHAPE']

        resmesh = bpy.data.meshes.new("shape2shape.001")
        resob = bpy.data.objects.new("shape2shape.001", resmesh)

        col.objects.link(resob) 

        mod = resob.modifiers.new("LAYOUT",'NODES')
        mod.node_group = gn
        resob.data.update()

        return {'FINISHED'}

class TDP_OT_AddOneToMany(bpy.types.Operator):
    """Adds GN based 1:Many block"""
    bl_idname = "curve_partition.add_one2many"
    bl_label = "Add one2many block"

    def execute(self, context):
        col_id = bpy.data.collections.find("CHANNELS")
        if col_id == -1:
            bpy.data.collections.new("CHANNELS")
            context.scene.collection.children.link(bpy.data.collections["CHANNELS"])
        col = bpy.data.collections['CHANNELS']

        if(bpy.data.node_groups.find('ONE2MANY') == -1):
            append_one2many()
        gn = bpy.data.node_groups['ONE2MANY']

        resmesh = bpy.data.meshes.new("one2many.001")
        resob = bpy.data.objects.new("one2many.001", resmesh)

        col.objects.link(resob) 

        mod = resob.modifiers.new("LAYOUT",'NODES')
        mod.node_group = gn
        resob.data.update()

        return {'FINISHED'}

class TDP_OT_ApplyLayoutModifier(bpy.types.Operator):
    """Applies GN based printing layout modifier to active object"""
    bl_idname = "curve_partition.apply_layout"
    bl_label = "Curve Based Printing Layout"

    def execute(self, context):
        if(context.selected_objects == []):
            self.report({'ERROR'}, 'No object selected, please select an object from viewport')
        ob = context.selected_objects[0]

        if(bpy.data.node_groups.find('LAYOUT_AND_EXPORT') == -1):
            append_layout_and_export()
        gn = bpy.data.node_groups['LAYOUT_AND_EXPORT']

        resob = context.active_object
        mod = resob.modifiers.new("LAYOUT",'NODES')
        mod.node_group = gn

        resob.data.update()

        return {'FINISHED'}

class TDP_OT_ApplyPartitioningModifier(bpy.types.Operator):
    """Applies GN based Modifier to active object"""
    bl_idname = "curve_partition.apply_partition"
    bl_label = "Curve Based Partitioning"

    def execute(self, context):
        if(context.selected_objects == []):
            self.report({'ERROR'}, 'No object selected, please select an object from viewport')
        ob = context.selected_objects[0]

        if(bpy.data.collections.find("CHANNELS") == -1):
            self.report({'ERROR'}, 'CHANNELS collection not found, first create channels')
        col = bpy.data.collections['CHANNELS']

        if(bpy.data.node_groups.find('PARTITION') == -1):
            append_partition()
        gn = bpy.data.node_groups['FREE_FORM']

        if(bpy.data.collections.find("PARTITION RESULTS") == -1):
            rescol = bpy.data.collections.new("PARTITION RESULTS")
            context.scene.collection.children.link(rescol)
        rescol = bpy.data.collections['PARTITION RESULTS']

        resmesh = bpy.data.meshes.new('RESMESH')
        resob = bpy.data.objects.new('RESULT', resmesh)
        rescol.objects.link(resob)

        mod = resob.modifiers.new("PARTITIONING",'NODES')
        mod.node_group = gn
        mod["Socket_15"] = col
        mod["Socket_13"] = ob

        resob.data.update()

        return {'FINISHED'}

class TDP_OT_PlanarCurveDrawing(bpy.types.Operator):
    """Modal planar curve drawing operator"""
    bl_idname = "curve_partition.modal_planar_curve_drawing"
    bl_label = "Planar 3D Curve Drawing"

    def modal(self, context, event):
        
        if self.curve_ob != None:
            if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'LEFTMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE','MOUSESMARTZOOM'}:
                return {'PASS_THROUGH'}
            elif event.ctrl and event.type == 'Z' and event.value =='PRESS':
                return {'PASS_THROUGH'}
            elif event.alt and event.type == 'Z' and event.value =='PRESS':
                return {'PASS_THROUGH'}
            elif event.type in {'ESC'}:
                temp = self.canvas.data
                bpy.data.objects.remove(self.canvas)
                bpy.data.meshes.remove(temp)
                context.view_layer.objects.active = self.curve_ob
                bpy.ops.object.editmode_toggle()
                return {'FINISHED'}
            else:
                return {'RUNNING_MODAL'}
        elif self.canvas != None:
            if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE','MOUSESMARTZOOM'}:
                return {'PASS_THROUGH'}
            elif event.type == 'MOUSEMOVE':
                self.canvas.rotation_euler.rotate_axis('X',radians((self.x - event.mouse_region_x)/5.0))
                self.x = event.mouse_region_x
                return {'RUNNING_MODAL'}
            elif event.type in {'RIGHTMOUSE'}:
                col_id = bpy.data.collections.find("CHANNELS")
                if col_id == -1:
                    bpy.data.collections.new("CHANNELS")
                    context.scene.collection.children.link(bpy.data.collections["CHANNELS"])
                col = bpy.data.collections["CHANNELS"]
                self.curve = bpy.data.curves.new("channel.001", 'CURVE')
                self.curve.dimensions = '3D'
                self.curve_ob = bpy.data.objects.new("channel.001", self.curve)
                col.objects.link(self.curve_ob) 
                context.view_layer.objects.active = self.curve_ob
                bpy.ops.object.editmode_toggle()
                bpy.ops.wm.tool_set_by_id(name="builtin.draw")
                bpy.context.scene.tool_settings.curve_paint_settings.depth_mode = 'SURFACE'
                bpy.context.scene.tool_settings.curve_paint_settings.use_project_only_selected = True
                for obj in bpy.context.selected_objects:
                    obj.select_set(False)
                self.canvas.select_set(True)
                return {'RUNNING_MODAL'}
        elif len(self.picked_points) > 1:
            v1 = self.picked_points[0]
            v2 = self.picked_points[1]
            c = (v1+v2)/2.0
            d = (v1-v2)
            self.axis = d
            s = d.length * 2.0
            rot = d.to_track_quat('X','Z').to_euler()

            bpy.ops.mesh.primitive_plane_add(size=s, location=c, rotation=rot)
            self.canvas = context.active_object
            return {'RUNNING_MODAL'}
        elif len(self.picked_points) == 1:    
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                hit_world = main(context, event)
                self.picked_points.append(hit_world)
            elif event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE','TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE','MOUSESMARTZOOM'}:
                # allow navigation
                return {'PASS_THROUGH'}
        elif event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE','MOUSESMARTZOOM'}:
            # allow navigation
            return {'PASS_THROUGH'}
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            hit_world = main(context, event)
            self.picked_points.append(hit_world)
            # args = (self, context, hit_world)
            # bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, args, 'WINDOW', 'POST_VIEW')
            return {'RUNNING_MODAL'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}
        

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            self.picked_points = []
            self.canvas = None
            self.curve = None
            self.curve_ob = None
            self.axis = None
            self.x = 0
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}

class TDP_PT_PlanarCurveDrawingSidebar(bpy.types.Panel):
    """Sidebar for channel partition addon"""
    bl_label = "Curve Partitioning Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Curve Partitioning Tool"
    def draw(self, contex):
        col = self.layout.column(align=True)
        prop = col.operator(TDP_OT_PlanarCurveDrawing.bl_idname, text="Add Canvas and Draw Channels")
        row = self.layout.row(align=True)
        prop = row.operator(TDP_OT_ApplyPartitioningModifier.bl_idname, text="Apply Partitioning")
        row = self.layout.row(align=True)
        prop = row.operator(TDP_OT_AddOneToMany.bl_idname, text="Add One:Many Block")
        row = self.layout.row(align=True)
        prop = row.operator(TDP_OT_AddShape2Shape.bl_idname, text="Add Shape:Shape Block")
        row = self.layout.row(align=True)
        prop = row.operator(TDP_OT_AddTransform.bl_idname, text="Add Transform Block")

classes = [
    TDP_OT_PlanarCurveDrawing,
    TDP_PT_PlanarCurveDrawingSidebar,
    TDP_OT_ApplyPartitioningModifier,
    TDP_OT_ApplyLayoutModifier,
    TDP_OT_AddOneToMany,
    TDP_OT_AddShape2Shape,
    TDP_OT_AddTransform
]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()