import bpy
from mathutils import Vector

# Replace with your object name
obj = bpy.data.objects['Box']
camera = bpy.context.scene.camera

# Offset in camera's local space (e.g., 2 units in front of camera)
offset = Vector((0, 1, -8))

# Convert offset to world space
world_position = camera.matrix_world @ offset

# Move object to new position
obj.location = world_position
