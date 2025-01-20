import bpy
import csv
import os

class KEYS_OT_output(bpy.types.Operator):
    """Export Grease Pencil keyframes frame by frame"""
    bl_idname = "keys.output"
    bl_label = "Export Keyframes"
    bl_description = "Render Grease Pencil keyframes frame by frame\n(Make sure the Grease Pencil object is selected)"

    def execute(self, context):

        # Notification popup
        def draw(self, context):
            self.layout.label(text="Started")
        bpy.context.window_manager.popup_menu(draw)

        # Get current scene
        scene = bpy.context.scene

        # Render settings
        film_transparent = True
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '16'
        scene.render.image_settings.compression = 0
        if scene.render.film_transparent == False:
            scene.render.film_transparent = True
            film_transparent = False

        # Handle and set render path
        render_filepath = scene.render.filepath
        render_filepath = bpy.path.abspath(render_filepath)
        if not render_filepath.endswith(os.sep):
            render_filepath += os.sep
        scene.render.filepath = render_filepath

        # Get selected Grease Pencil object
        gp_object = bpy.context.object
        if not gp_object or gp_object.type != 'GPENCIL':
            self.report({'ERROR'}, "Please select a Grease Pencil object.")
            return {'CANCELLED'}

        # Get Grease Pencil layers
        gpencil_data = gp_object.data
        gplayer_list = gpencil_data.layers

        if len(gplayer_list) == 0:
            self.report({'ERROR'}, "No layers found in the Grease Pencil object.")
            return {'CANCELLED'}

        # Render path adjustments
        render_filepath = bpy.path.abspath(scene.render.filepath)
        if not os.path.exists(render_filepath):
            os.makedirs(render_filepath)

        frame_end = scene.frame_end

        # Create CSV data structures
        def create_list(rows, cols):
            return [["" for _ in range(cols)] for _ in range(rows)]

        header = create_list(2, len(gplayer_list) + 2)
        data = create_list(frame_end + 5, len(gplayer_list) + 2)
        for i in range(frame_end):
            data[i][0] = i + 1

        # Fill header
        layer_tag = context.scene.layer_tag if hasattr(context.scene, "layer_tag") else ""
        header[0][1:] = [layer.name for layer in gplayer_list]
        header[0][0] = "Frame"
        header[1][1:] = [layer_tag] * len(gplayer_list)

        # Process each layer
        for i, layer in enumerate(gplayer_list):
            gpencil_data.layers.active_index = i
            layer.active = True

            if layer.hide:
                header[0][i + 1] += "*Hide"
                continue

            # Hide all layers except the current one
            for other_layer in gplayer_list:
                other_layer.hide = other_layer != layer

            keysname = 1

            # Jump to the first frame
            bpy.ops.screen.frame_jump(end=False)

            # Render all keyframes
            while scene.frame_current <= frame_end:
                if scene.frame_current not in [f.co[0] for f in layer.frames]:
                    bpy.ops.screen.keyframe_jump(next=True)
                    continue

                scene.render.filepath = os.path.join(
                    render_filepath, f"{layer.name}_{keysname:04}.png"
                )
                bpy.ops.render.render(animation=False, write_still=True)
                data[scene.frame_current - 1][i + 1] = keysname
                keysname += 1

                bpy.ops.screen.keyframe_jump(next=True)

        # Restore visibility of all layers
        for layer in gplayer_list:
            layer.hide = False

        # Restore film transparency setting
        if not film_transparent:
            scene.render.film_transparent = False

        # Save CSV file
        csv_filepath = os.path.join(render_filepath, f"{gp_object.name}.csv")
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(header)
            writer.writerows(data)

        self.report({'INFO'}, f"Export complete. CSV saved at {csv_filepath}")
        return {'FINISHED'}
