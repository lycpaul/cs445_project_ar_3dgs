import bpy
import os
import cv2

def capture_scene():
    # tmp directory
    home_dir = os.path.expanduser('~')
    filepath = os.path.join(home_dir, 'tmp/blender_scene.png')
    
    # set render settings
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = filepath

    # render camera view
    bpy.ops.render.render(write_still=True)

    # load cv2 image
    img = cv2.imread(filepath)
    return img


if __name__ == "__main__":
    img = capture_scene()
    print(img.shape)
