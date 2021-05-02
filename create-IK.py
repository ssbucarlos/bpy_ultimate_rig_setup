import bpy, math
from mathutils import Matrix

#bone creation
bpy.ops.object.mode_set(mode='EDIT')
for side in ['R', 'L']:
    eb = bpy.context.object.data.edit_bones
    #These must exist if its an Ultimate skeleton
    clavicle = eb['Clavicle' + side]
    shoulder = eb['Shoulder' + side]
    arm = eb['Arm' + side]
    hand = eb['Hand' + side]
    
    leg = eb['Leg' + side]
    knee = eb['Knee' + side]
    foot = eb['Foot' + side]
    
    
    # Bones that could exist if script previously ran
    exoShoulder = eb.get('ExoShoulder' + side)
    if not exoShoulder:
        exoShoulder = eb.new('ExoShoulder' + side)
        exoShoulder.head = shoulder.head
        exoShoulder.tail = arm.head
        exoShoulder.use_deform = False
    
    exoArm = eb.get('ExoArm' + side)
    if not exoArm:
        exoArm = eb.new('ExoArm' + side)
        exoArm.head = arm.head
        exoArm.tail = hand.head
        exoArm.parent = exoShoulder
        exoArm.use_deform = False
        exoArm.use_connect = True
    
    handIK = eb.get('Hand%s_IK' % side)
    if not handIK:
        handIK = eb.new('Hand%s_IK' % side)
        handIK.head = hand.head
        handIK.tail = hand.tail
        handIK.use_deform = False
        if side == 'L':
            handIK.roll = math.radians(180)
        
    elbowIK = eb.get('Elbow%s_IK' % side)
    if not elbowIK:
        elbowIK = eb.new('Elbow%s_IK' % side)
        elbowIK.head = exoArm.head
        elbowIK.head[2] = elbowIK.head[2] - 10
        elbowIK.tail = exoArm.head
        elbowIK.tail[2] = elbowIK.tail[2] - 7
        elbowIK.use_deform = False
        
    exoLeg = eb.get('ExoLeg' + side)
    if not exoLeg:
        exoLeg = eb.new('ExoLeg' + side)
        exoLeg.head = leg.head
        exoLeg.tail = knee.head
        exoLeg.use_deform = False
        
    exoKnee = eb.get('ExoKnee' + side)
    if not exoKnee:
        exoKnee = eb.new('ExoKnee' + side)
        exoKnee.head = exoLeg.tail
        exoKnee.tail = foot.head
        exoKnee.parent = exoLeg
        exoKnee.use_deform = False
        exoKnee.use_connect = True
    
    footIK = eb.get('Foot%s_IK' % side)
    if not footIK:
        footIK = eb.new('Foot%s_IK' % side)
        footIK.head = foot.head
        footIK.tail = foot.tail
        footIK.use_deform = False
        footIK.roll = math.radians(90)
        
    kneeIK = eb.get('Knee%s_IK' % side)
    if not kneeIK:
        kneeIK = eb.new('Knee%s_IK' % side)
        kneeIK.head = knee.head
        kneeIK.head[2] = kneeIK.head[2] + 10
        kneeIK.tail = knee.head
        kneeIK.tail[2] = kneeIK.tail[2] + 7
        kneeIK.use_deform = False
    
    #detect and fix co-linear exo bones
    armChain = [exoShoulder, exoArm, handIK]
    footChain = [exoLeg, exoKnee, footIK]
    for c in [armChain, footChain]:
        mat = Matrix([c[0].head, c[1].head, c[2].head])
        if 0 == mat.determinant():
            fix = -.01 if c is armChain else .01
            c[1].head[2] = c[1].head[2] + fix
            
    
#custom bone shapes
armature = bpy.context.object #Needed cus the ops below will change active object

col = bpy.data.collections.new('Custom Bone Shapes')
bpy.context.scene.collection.children.link(col)

bpy.ops.mesh.primitive_torus_add() # This op doesnt return obj ref 
ring = bpy.context.active_object
ring.scale[2] = .3
ring.name = 'CustomBoneShape'

col.objects.link(ring)
for c in ring.users_collection:
    if c is not col:
        c.objects.unlink(ring)

col.hide_viewport = True
ring.select_set(False)

armature.select_set(True)
bpy.context.view_layer.objects.active = armature

#constraint creation
bpy.ops.object.mode_set(mode='POSE')
for side in ['R', 'L']:
    pb = bpy.context.object.pose.bones
    
    clavicle = pb['Clavicle' + side]
    shoulder = pb['Shoulder' + side]
    arm = pb['Arm' + side]
    hand = pb['Hand' + side]
    exoShoulder = pb['ExoShoulder' + side]
    exoArm = pb['ExoArm' + side]
    handIK = pb['Hand%s_IK' % side]
    elbowIK = pb['Elbow%s_IK' % side]
    
    leg = pb['Leg' + side]
    knee = pb['Knee' + side]
    foot = pb['Foot' + side]
    exoLeg = pb['ExoLeg' + side]
    exoKnee = pb['ExoKnee' + side]
    footIK = pb['Foot%s_IK' % side]
    kneeIK = pb['Knee%s_IK' % side]
    
    #apply custom bone shapes
    handIK.custom_shape = ring
    handIK.custom_shape_scale = 3
    elbowIK.custom_shape = ring
    elbowIK.custom_shape_scale = .25
    footIK.custom_shape = ring
    footIK.custom_shape_scale = 4
    kneeIK.custom_shape = ring
    kneeIK.custom_shape_scale = .25
    
    
    for bone in [shoulder, arm]:
        dtc = bone.constraints.new('DAMPED_TRACK')
        dtc.target = bpy.context.object
        dtc.subtarget = exoShoulder.name if bone is shoulder else handIK.name
        dtc.head_tail = 1 if bone is shoulder else 0
        dtc.track_axis = 'TRACK_X'
        dtc.influence = 1
    
    for bone in [leg, knee]:
        dtc = bone.constraints.new('DAMPED_TRACK')
        dtc.target = bpy.context.object
        dtc.subtarget = exoLeg.name if bone is leg else footIK.name
        dtc.head_tail = 1 if bone is leg else 0
        dtc.track_axis = 'TRACK_X'
        dtc.influence = 1
        
    for bone in [hand, foot]:
        crc = bone.constraints.new('COPY_ROTATION')
        csc = bone.constraints.new('COPY_SCALE')
        for c in [crc, csc]:
            c.target = bpy.context.object
            c.subtarget = handIK.name if bone is hand else footIK.name
            c.target_space = 'POSE'
            c.owner_space = 'POSE'
    
    for bone in [exoArm, exoKnee]:
        ikc = bone.constraints.new('IK')
        ikc.target = bpy.context.object
        ikc.subtarget = handIK.name if bone is exoArm else footIK.name
        ikc.pole_target = bpy.context.object
        ikc.pole_subtarget = elbowIK.name if bone is exoArm else kneeIK.name
        ikc.pole_angle = math.radians(-90)
        ikc.chain_count = 2
    
    

