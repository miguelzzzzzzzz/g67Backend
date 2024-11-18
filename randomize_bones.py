import bpy
import random

# Get the armature
armature = bpy.data.objects['Adjustable Mannequin']

# Define the min and max values for each body part
body_part_ranges = {
    "shoulder angle": (0, 0.22),
    "shoulders control": (0, 0.26),
    "neck control": (-0.045, 0.185),
    "breasts control": (0, 0.26),
    "breasts angle": (-0.11, 0.11),
    "torso control": (-0.04, 0.19),
    "hips control": (-0.02, 0.21),
    "legs control": (-0.035, 0.22),
    "belly control": (0, 0.22),
    "arms control": (-0.04, 0.215),
}

# Apply random values to the control bones
for bone_name, (min_val, max_val) in body_part_ranges.items():
    bone = armature.pose.bones.get(bone_name)
    if bone:
        random_value = random.uniform(min_val, max_val)
        bone.location.x = random_value
        print(f"Set '{bone.name}' location.x to {random_value:.3f}")
    else:
        print(f"Bone '{bone_name}' not found.")
bone = armature.pose.bones.get("head style")
bone.location.x = 0.57

# Adjust the Y-axis of the root pose bone (or a similar control bone)
root_bone = armature.pose.bones.get('root')  # Replace 'root' with the main control bone
if root_bone:
    root_bone.location.y += -3.5  # Move the bone along the Y-axis
    root_bone.location.x += -0.8  # Move the bone along the X-axis
    print(f"Adjusted root bone Y-axis to {root_bone.location.y:.3f}")
else:
    print("Root bone not found.")

# Update the scene
bpy.context.view_layer.update()

# Camera setup
camera = bpy.data.objects['Camera']
model = bpy.data.objects['Adjustable Mannequin']

# Move the camera further back to zoom out
direction = model.location - camera.location  # Direction from camera to model
distance = 13.0  # Adjust this value to zoom out (higher = more zoomed out)
camera.location = model.location + direction.normalized() * -distance

# Adjust camera orientation to point at the model
camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Set camera as the active camera
bpy.context.scene.camera = camera

# Adjust render resolution
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100

# Render and save the image
image_output_path = "C:/Users/migzuu/Downloads/Adjusted_Mannequin_YAdjusted.png"
bpy.context.scene.render.filepath = image_output_path
bpy.ops.render.render(write_still=True)
print(f"Snapshot saved to {image_output_path}")

obj_output_path = "C:/Users/migzuu/PycharmProjects/pythonProject5/Adjusted_Mannequin.obj"

# Ensure only the mannequin and related objects are exported
bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
model.select_set(True)  # Select the mannequin model
armature.select_set(True)  # Select the armature (if needed)

# Set the selected objects as the active context
bpy.context.view_layer.objects.active = model

# Export the selected objects as OBJ
bpy.ops.wm.obj_export(
    filepath=obj_output_path
)

print(f"Model exported as OBJ to {obj_output_path}")