# DEPRECATED
* smash_ultimate_blender now imports the smash models with proper bone orientations. 
* This means that this script is no longer needed for those versions, and it wouldnt work anyways on that version
* Since the bones are more 'normal' in that version you can setup IK as u would with a standard skeleton.
* https://github.com/ssbucarlos/smash-ultimate-blender

# bpy_ultimate_rig_setup
Blender Rig setup script for imported smash ultimate skeletons. Useful because smash skeletons have rotated bones along the Shoulder-Elbow-Hand or Hip-Knee-Foot chains, which would break a conventional IK setup. The goal of this script is to setup IK without modifying the existing smash skeleton, in order to allow import + export of smash ultimate animations.
 
# To use:
Don't install this script. Just run it from the 'Scripting' tab in blender. Make sure the smash skeleton is selected!

# Features:
1. Arm + Leg IK controllers
2. Head Tracker

# Planned Features:
For the list of currently planned features, check out the 'issues' page. Please feel free to leave feature requests, especially if its a feature that makes your life animating alot easier!

# Known Issues:
Once you setup a rig using this script, imported smash ultimate transformation tracks will no longer work.
