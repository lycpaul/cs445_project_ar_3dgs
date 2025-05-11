import bpy
import os

# home directory
home_dir = os.path.expanduser('~')

# Set render settings
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath = os.path.join(
    home_dir, 'workspace/cs445_project_ar_3dgs/images/detected_marker_3.png')

# Render camera view
bpy.ops.render.render(write_still=True)
