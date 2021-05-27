import bpy, math
from mathutils import Matrix

# Bone creation
bpy.ops.object.mode_set(mode='EDIT') 
eb = bpy.context.object.data.edit_bones

# Head
head = eb['Head']
headT = eb.get('HeadTracker')
if not headT:
    headT = eb.new('HeadTracker')
    headT.head = head.head
    headT.tail = head.head
    headT.head[2] = headT.head[2] + 10
    headT.tail[2] = headT.tail[2] + 7
    headT.use_deform = False
    
# Arm and Legs
for side in ['R', 'L']:
    # These must exist if its an Ultimate skeleton
    clavicle = eb['Clavicle' + side]
    shoulder = eb['Shoulder' + side]
    arm = eb['Arm' + side]
    hand = eb['Hand' + side]
    
    legC = eb['LegC']
    leg = eb['Leg' + side]
    knee = eb['Knee' + side]
    foot = eb['Foot' + side]
    
    # Bones that could exist if script previously ran
    '''
    shoulderFK = eb.get('Shoulder%s_FK' % side)
    if not shoulderFK:
        shoulderFK = eb.new('Shoulder%s_FK' % side)
        shoulderFK.head = shoulder.head
        shoulderFK.tail = shoulder.head
        shoulderFK.tail[1] = shoulderFK.tail[1] + 1
        shoulderFK.use_deform = False
        shoulderFK.parent = clavicle
    '''
    
    exoShoulder = eb.get('ExoShoulder' + side)
    if not exoShoulder:
        exoShoulder = eb.new('ExoShoulder' + side)
        exoShoulder.head = shoulder.head
        exoShoulder.tail = arm.head
        exoShoulder.use_deform = False
        # exoShoulder.parent = clavicle # Handled by contraints as of the FK/IK switch update
        exoShoulder.layers[0] = False
        exoShoulder.layers[1] = True
        
    exoArm = eb.get('ExoArm' + side)
    if not exoArm:
        exoArm = eb.new('ExoArm' + side)
        exoArm.head = arm.head
        exoArm.tail = hand.head
        exoArm.parent = exoShoulder
        exoArm.use_deform = False
        exoArm.use_connect = True
        exoArm.layers[0] = False
        exoArm.layers[1] = True
    
    handIK = eb.get('Hand%s_IK' % side)
    if not handIK:
        handIK = eb.new('Hand%s_IK' % side)
        handIK.head = hand.head
        handIK.tail = hand.tail
        handIK.use_deform = False
        if side == 'L':
            handIK.roll = math.radians(180)
        #handIK.parent = shoulderFK
        
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
        #exoLeg.parent = legC
        exoLeg.layers[0] = False
        exoLeg.layers[1] = True
        
    exoKnee = eb.get('ExoKnee' + side)
    if not exoKnee:
        exoKnee = eb.new('ExoKnee' + side)
        exoKnee.head = exoLeg.tail
        exoKnee.tail = foot.head
        exoKnee.parent = exoLeg
        exoKnee.use_deform = False
        exoKnee.use_connect = True
        exoKnee.layers[0] = False
        exoKnee.layers[1] = True
    
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
        if math.isclose(mat.determinant(), 0, abs_tol=0.0001):
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


#create custom bone groups
bpy.ops.object.mode_set(mode='POSE')
right = 'Right'
left = 'Left'
neutral = 'Neutral'

for side in [right, left, neutral]:
    g = bpy.context.object.pose.bone_groups.new()
    g.name = side
    if side in [right, left]:
        g.color_set = 'THEME01' if side is right else 'THEME03'
    else:
        g.color_set = 'THEME10'


#constraint creation
bpy.ops.object.mode_set(mode='POSE')
r = 'R'
l = 'L'

pb = bpy.context.object.pose.bones
boneGroups = bpy.context.object.pose.bone_groups
head = pb['Head']
headT = pb['HeadTracker']
headT.custom_shape = ring
headT.custom_shape_scale = .25
headT.bone_group = boneGroups.get('Neutral')
headT['Disable/Enable'] = 0

for bone in [head]:
    ttc = head.constraints.new('TRACK_TO')
    ttc.target = bpy.context.object
    ttc.subtarget = headT.name
    ttc.track_axis = 'TRACK_Y'
    ttc.up_axis = 'UP_X'
    ttc.use_target_z = True
    ttc.target_space = 'POSE'
    ttc.owner_space = 'POSE'
    d = ttc.driver_add('influence')
    var = d.driver.variables.new()
    var.name = 'var'
    target = var.targets[0]
    target.id_type = 'OBJECT'
    target.id = armature
    target.data_path = 'pose.bones["%s"]["Disable/Enable"]' % headT.name
    d.driver.expression = "%s" % var.name
    
for bone in [headT]:
    coc = bone.constraints.new('CHILD_OF')
    coc.target = bpy.context.object
    coc.subtarget = head.name
    d = coc.driver_add('influence')
    var = d.driver.variables.new()
    var.name = 'var'
    target = var.targets[0]
    target.id_type = 'OBJECT'
    target.id = armature
    target.data_path = 'pose.bones["%s"]["Disable/Enable"]' % headT.name
    d.driver.expression = '1 - %s' % var.name

for side in [r, l]:
        
    clavicle = pb['Clavicle' + side]
    shoulder = pb['Shoulder' + side]
    arm = pb['Arm' + side]
    hand = pb['Hand' + side]
    exoShoulder = pb['ExoShoulder' + side]
    exoArm = pb['ExoArm' + side]
    handIK = pb['Hand%s_IK' % side]
    elbowIK = pb['Elbow%s_IK' % side]
    
    leg = pb['Leg' + side]
    legC = pb['LegC']
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
    
    #apply bone groups (for colors)
    rg = boneGroups.get('Right')
    lg = boneGroups.get('Left')
    for bone in [handIK, elbowIK, footIK, kneeIK]:
        bone.bone_group = rg if side is r else lg
    
    # Create FK/IK Switch on main IK Bones
    for bone in [handIK, footIK]:
        bone["FK/IK Switch"] = 0
    
    #apply constraints
    armature = bpy.context.object
    for bone in [shoulder, arm]:
        dtc = bone.constraints.new('DAMPED_TRACK')
        dtc.target = bpy.context.object
        dtc.subtarget = exoShoulder.name if bone is shoulder else handIK.name
        dtc.head_tail = 1 if bone is shoulder else 0
        dtc.track_axis = 'TRACK_X'
        dtc.influence = 1
        # Add FK/IK switch driver
        for c in [dtc]:
            d = c.driver_add('influence')
            var = d.driver.variables.new()
            var.name = 'var'
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = armature
            target.data_path = 'pose.bones["%s"]["FK/IK Switch"]' % handIK.name
            d.driver.expression = "%s" % var.name
    
    for bone in [leg, knee]:
        dtc = bone.constraints.new('DAMPED_TRACK')
        dtc.target = bpy.context.object
        dtc.subtarget = exoLeg.name if bone is leg else footIK.name
        dtc.head_tail = 1 if bone is leg else 0
        dtc.track_axis = 'TRACK_X'
        dtc.influence = 1
        for c in [dtc]:
            d = c.driver_add('influence')
            var = d.driver.variables.new()
            var.name = 'var'
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = armature
            target.data_path = 'pose.bones["%s"]["FK/IK Switch"]' % footIK.name
            d.driver.expression = "%s" % var.name
        
    for bone in [hand, foot]:
        crc = bone.constraints.new('COPY_ROTATION')
        csc = bone.constraints.new('COPY_SCALE')
        for c in [crc, csc]:
            c.target = bpy.context.object
            c.subtarget = handIK.name if bone is hand else footIK.name
            c.target_space = 'POSE'
            c.owner_space = 'POSE'
            # Add FK/IK switch drivers
            d = c.driver_add('influence')
            var = d.driver.variables.new()
            var.name = 'var'
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = armature
            target.data_path = 'pose.bones["%s"]["FK/IK Switch"]' % handIK.name
            d.driver.expression = "%s" % var.name
    
    for bone in [exoArm, exoKnee]:
        ikc = bone.constraints.new('IK')
        ikc.target = bpy.context.object
        ikc.subtarget = handIK.name if bone is exoArm else footIK.name
        ikc.pole_target = bpy.context.object
        ikc.pole_subtarget = elbowIK.name if bone is exoArm else kneeIK.name
        ikc.pole_angle = math.radians(-90)
        ikc.chain_count = 2
        # ttc ensures exo bone behaves appropriately in FK mode
        ttc = bone.constraints.new('TRACK_TO')
        ttc.target = armature
        ttc.subtarget = hand.name if bone is exoArm else foot.name
        ttc.track_axis = 'TRACK_Y'
        ttc.up_axis = 'UP_Z'
        ttc.use_target_z = True
        # Add FK/IK switch drivers
        for c in [ikc, ttc]:
            d = c.driver_add('influence')
            var = d.driver.variables.new()
            var.name = 'var'
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = armature
            target.data_path = 'pose.bones["%s"]["FK/IK Switch"]' % handIK.name if bone is exoArm else\
                                'pose.bones["%s"]["FK/IK Switch"]' % footIK.name
            d.driver.expression = "%s" % var.name if c is ikc else\
                                  "1 - %s" % var.name
            
    # New Constraints for FK/IK switching
    for bone in [handIK, footIK]:
        ctc = bone.constraints.new('COPY_TRANSFORMS')
        ctc.target = armature
        ctc.subtarget = hand.name if bone is handIK else foot.name
        ctc.target_space = 'POSE'
        ctc.owner_space = 'POSE'
        d = ctc.driver_add('influence')
        var = d.driver.variables.new()
        var.name = 'var'
        target = var.targets[0]
        target.id_type = 'OBJECT'
        target.id = armature
        target.data_path = 'pose.bones["%s"]["FK/IK Switch"]' % handIK.name if bone is handIK else\
                            'pose.bones["%s"]["FK/IK Switch"]' % footIK.name 
        d.driver.expression = "1 - %s" % var.name
    
    for bone in [exoShoulder]:
        for targetBone in [clavicle, shoulder]:
            coc = bone.constraints.new('CHILD_OF')
            coc.target = armature
            coc.subtarget = targetBone.name
            d = coc.driver_add('influence')
            var = d.driver.variables.new()
            var.name = 'var'
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = armature
            target.data_path = 'pose.bones["%s"]["FK/IK Switch"]' % handIK.name
            d.driver.expression = '%s' % var.name if targetBone is clavicle else\
                                    '1 - %s' % var.name

    for bone in [exoLeg]:
        for targetBone in [legC, leg]:
            coc = bone.constraints.new('CHILD_OF')
            coc.target = armature
            coc.subtarget = targetBone.name
            d = coc.driver_add('influence')
            var = d.driver.variables.new()
            var.name = 'var'
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = armature
            target.data_path = 'pose.bones["%s"]["FK/IK Switch"]' % footIK.name
            d.driver.expression = '%s' % var.name if targetBone is legC else\
                                    '1 - %s' % var.name    
    
    for bone in [elbowIK, kneeIK]:
        coc = bone.constraints.new('CHILD_OF')
        coc.target = armature
        coc.subtarget = shoulder.name if bone is elbowIK else leg.name
        d = coc.driver_add('influence')
        var = d.driver.variables.new()
        var.name = 'var'
        target = var.targets[0]
        target.id_type = 'OBJECT'
        target.id = armature
        target.data_path = 'pose.bones["%s"]["FK/IK Switch"]' % handIK.name if bone is elbowIK else\
                            'pose.bones["%s"]["FK/IK Switch"]' % footIK.name
        d.driver.expression = '1 - %s' % var.name