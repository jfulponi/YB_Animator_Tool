import bpy
from ..Operators.Output import KEYS_OT_output

class RENDER_OT_open_keys_render_popup(bpy.types.Operator):
    """Render Grease Pencil keyframes"""
    bl_idname = "render.open_keys_render_popup"
    bl_label = "Crayon Keyframe Rendering"

    def execute(self, context):
        # Verificar si hay un objeto Grease Pencil activo
        gp_object = bpy.context.object
        if not gp_object or gp_object.type != 'GPENCIL':
            self.report({'ERROR'}, "Please select a Grease Pencil object before rendering.")
            return {'CANCELLED'}

        # Invocar el operador para exportar keyframes
        bpy.ops.keys.output('INVOKE_DEFAULT')
        return {'FINISHED'}
