/* Humanoid 3D Model — Advanced Procedural Cyber-Robot Gait Kinematics */

export function createHumanoidScene(scene, data, THREE) {
    scene.background = new THREE.Color(0x0a0c10);
    scene.fog = new THREE.FogExp2(0x0a0c10, 0.04);

    scene.add(new THREE.AmbientLight(0x446688, 0.8));
    const sun = new THREE.DirectionalLight(0xffffee, 1.5);
    sun.position.set(5, 10, 8);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    scene.add(sun);

    const pointLight = new THREE.PointLight(0x00ffff, 1.0, 5);
    pointLight.position.set(0, 1.5, 1);
    scene.add(pointLight);

    // Floor
    const floor = new THREE.Mesh(
        new THREE.PlaneGeometry(30, 30),
        new THREE.MeshStandardMaterial({ color: 0x11141a, roughness: 0.8, metalness: 0.2 })
    );
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    scene.add(floor);
    
    const grid = new THREE.GridHelper(30, 60, 0x00ffff, 0x223344);
    grid.material.opacity = 0.2;
    grid.material.transparent = true;
    grid.position.y = 0.01;
    scene.add(grid);

    const SCALE = 3.0;

    // --- Materials ---
    const matArmor = new THREE.MeshStandardMaterial({ color: 0xecf0f1, metalness: 0.7, roughness: 0.2 });
    const matDark = new THREE.MeshStandardMaterial({ color: 0x1e272e, metalness: 0.8, roughness: 0.5 });
    const matJoint = new THREE.MeshStandardMaterial({ color: 0x2d3436, metalness: 0.5, roughness: 0.8 });
    const matNeon = new THREE.MeshStandardMaterial({ color: 0x00ffff, emissive: 0x00ffff, emissiveIntensity: 2.5 });

    // --- Geometries ---
    const geoJoint = new THREE.SphereGeometry(0.04, 16, 16);
    const geoBone = new THREE.CapsuleGeometry(0.035, 0.32, 8, 16); // used for limbs
    const geoForearm = new THREE.CapsuleGeometry(0.03, 0.28, 8, 16);
    
    // --- Hierarchy ---
    const root = new THREE.Group();
    scene.add(root);

    // Pelvis
    const pelvisPivot = new THREE.Group();
    root.add(pelvisPivot);
    const pelvisMesh = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.12, 0.15), matArmor);
    pelvisMesh.castShadow = true;
    pelvisPivot.add(pelvisMesh);

    // Torso
    const torsoPivot = new THREE.Group();
    torsoPivot.position.y = 0.06;
    pelvisPivot.add(torsoPivot);
    
    const torsoMesh = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.35, 0.18), matArmor);
    torsoMesh.position.y = 0.175;
    torsoMesh.castShadow = true;
    torsoPivot.add(torsoMesh);

    // Neon Core
    const coreMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.19, 16), matNeon);
    coreMesh.rotation.z = Math.PI / 2;
    coreMesh.position.set(0, 0.175, 0.02);
    torsoPivot.add(coreMesh);

    // Head
    const headPivot = new THREE.Group();
    headPivot.position.y = 0.38;
    torsoPivot.add(headPivot);
    const headMesh = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.18, 0.18), matArmor);
    headMesh.position.y = 0.09;
    headMesh.castShadow = true;
    headPivot.add(headMesh);
    const visorMesh = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.04, 0.19), matNeon);
    visorMesh.position.y = 0.1;
    visorMesh.position.z = 0.01;
    headPivot.add(visorMesh);

    // --- Limbs Builder ---
    function buildArm(isLeft) {
        const sign = isLeft ? 1 : -1;
        const shoulderPivot = new THREE.Group();
        shoulderPivot.position.set(sign * 0.2, 0.3, 0);
        torsoPivot.add(shoulderPivot);
        
        const shoulderJoint = new THREE.Mesh(geoJoint, matJoint);
        shoulderPivot.add(shoulderJoint);

        const upperArm = new THREE.Mesh(geoBone, matArmor);
        upperArm.position.y = -0.16;
        upperArm.castShadow = true;
        shoulderPivot.add(upperArm);

        const elbowPivot = new THREE.Group();
        elbowPivot.position.y = -0.32;
        shoulderPivot.add(elbowPivot);
        
        const elbowJoint = new THREE.Mesh(geoJoint, matJoint);
        elbowPivot.add(elbowJoint);

        const forearm = new THREE.Mesh(geoForearm, matDark);
        forearm.position.y = -0.14;
        forearm.castShadow = true;
        elbowPivot.add(forearm);

        return { shoulderPivot, elbowPivot };
    }

    function buildLeg(isLeft) {
        const sign = isLeft ? 1 : -1;
        const hipPivot = new THREE.Group();
        hipPivot.position.set(sign * 0.08, -0.06, 0);
        pelvisPivot.add(hipPivot);
        
        const hipJoint = new THREE.Mesh(geoJoint, matJoint);
        hipPivot.add(hipJoint);

        const thigh = new THREE.Mesh(geoBone, matArmor);
        thigh.position.y = -0.16;
        thigh.castShadow = true;
        hipPivot.add(thigh);

        const kneePivot = new THREE.Group();
        kneePivot.position.y = -0.32;
        hipPivot.add(kneePivot);

        const kneePad = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.08, 0.08), matDark);
        kneePad.position.z = 0.02;
        kneePivot.add(kneePad);

        const shin = new THREE.Mesh(geoBone, matArmor);
        shin.position.y = -0.16;
        shin.castShadow = true;
        kneePivot.add(shin);

        const anklePivot = new THREE.Group();
        anklePivot.position.y = -0.32;
        kneePivot.add(anklePivot);

        const ankleJoint = new THREE.Mesh(geoJoint, matJoint);
        anklePivot.add(ankleJoint);

        const foot = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.04, 0.22), matDark);
        foot.position.set(0, -0.02, 0.05);
        foot.castShadow = true;
        anklePivot.add(foot);

        return { hipPivot, kneePivot, anklePivot };
    }

    const leftArm = buildArm(true);
    const rightArm = buildArm(false);
    const leftLeg = buildLeg(true);
    const rightLeg = buildLeg(false);

    // --- Markers & Trail ---
    const comMarker = new THREE.Mesh(new THREE.SphereGeometry(0.03, 8, 8), new THREE.MeshBasicMaterial({ color: 0xff00ff, wireframe: true }));
    scene.add(comMarker);

    const zmpMarker = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.01, 16), new THREE.MeshBasicMaterial({ color: 0xff4488 }));
    scene.add(zmpMarker);

    const stepGeo = new THREE.BoxGeometry(0.18, 0.005, 0.10);
    let lastIdx = -1;
    data.forEach(r => {
        if (r.support_index !== lastIdx) {
            const mat = new THREE.MeshStandardMaterial({
                color: r.support_index % 2 === 0 ? 0x00ffff : 0xff00ff,
                transparent: true, opacity: 0.3,
            });
            const marker = new THREE.Mesh(stepGeo, mat);
            marker.position.set(r.support_x * SCALE, 0.005, -r.support_y * SCALE);
            scene.add(marker);
            lastIdx = r.support_index;
        }
    });

    const trailPts = data.map(r => new THREE.Vector3(r.com_x * SCALE, 0.85, -r.com_y * SCALE));
    scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(trailPts), new THREE.LineBasicMaterial({ color: 0x00ffff, transparent: true, opacity: 0.4 })));

    // Precompute steps
    const stepTimes = [];
    lastIdx = -1;
    data.forEach(r => {
        if (r.support_index !== lastIdx) {
            stepTimes.push({ time: r.time, idx: r.support_index, x: r.support_x, y: r.support_y });
            lastIdx = r.support_index;
        }
    });

    return {
        root, pelvisPivot,
        leftHipPivot: leftLeg.hipPivot, rightHipPivot: rightLeg.hipPivot,
        leftKneePivot: leftLeg.kneePivot, rightKneePivot: rightLeg.kneePivot,
        leftAnklePivot: leftLeg.anklePivot, rightAnklePivot: rightLeg.anklePivot,
        leftShoulderPivot: leftArm.shoulderPivot, rightShoulderPivot: rightArm.shoulderPivot,
        leftElbowPivot: leftArm.elbowPivot, rightElbowPivot: rightArm.elbowPivot,
        comMarker, zmpMarker, stepTimes, SCALE
    };
}

export function updateHumanoid(obj, row, data, idx, THREE) {
    const S = obj.SCALE;
    const cx = row.com_x * S;
    const cz = -row.com_y * S;

    // --- Body Positioning ---
    obj.root.position.set(cx, 0, cz);

    const vx = row.com_vx || 0, vy = row.com_vy || 0;
    const speed = Math.sqrt(vx * vx + vy * vy);
    if (speed > 0.01) {
        // Face moving direction (+Z is forward)
        obj.root.rotation.y = Math.atan2(vx, -vy);
    }

    obj.comMarker.position.set(cx, 0.85, cz);
    obj.zmpMarker.position.set(row.zmp_x * S, 0.005, -row.zmp_y * S);

    // --- Phase Calculation ---
    const stepIdx = row.support_index;
    const isLeftSupport = stepIdx % 2 === 0;
    let swingPhase = 0;
    for (let i = 0; i < obj.stepTimes.length; i++) {
        if (obj.stepTimes[i].idx === stepIdx) {
            const stepStart = obj.stepTimes[i].time;
            const stepEnd = i + 1 < obj.stepTimes.length ? obj.stepTimes[i + 1].time : data[data.length - 1].time;
            const dur = stepEnd - stepStart;
            swingPhase = dur > 0 ? Math.min((row.time - stepStart) / dur, 1.0) : 0;
            break;
        }
    }

    // --- Advanced Gait Kinematics ---
    const maxHipAngle = 0.55; // increased stride
    const swingHipAngle = maxHipAngle * Math.cos(swingPhase * Math.PI); // back(+max) to front(-max)
    const supportHipAngle = -maxHipAngle * Math.cos(swingPhase * Math.PI); // front(-max) to back(+max)
    
    // Knee logic
    const swingKneeAngle = Math.sin(swingPhase * Math.PI) * 1.1; // pronounced knee bend
    const supportKneeAngle = 0.1; // slightly bent support knee

    // Ankle logic: 
    // Swing ankle points toe down at takeoff, levels out before landing
    const swingAnkleAngle = Math.sin(swingPhase * Math.PI) * 0.4;
    // Support ankle flexes to keep foot flat relative to leg angle
    const supportAnkleAngle = -supportHipAngle;

    // Apply leg kinematics
    if (isLeftSupport) {
        obj.leftHipPivot.rotation.x = supportHipAngle;
        obj.leftKneePivot.rotation.x = supportKneeAngle;
        obj.leftAnklePivot.rotation.x = supportAnkleAngle;

        obj.rightHipPivot.rotation.x = swingHipAngle;
        obj.rightKneePivot.rotation.x = swingKneeAngle;
        obj.rightAnklePivot.rotation.x = swingAnkleAngle;
    } else {
        obj.rightHipPivot.rotation.x = supportHipAngle;
        obj.rightKneePivot.rotation.x = supportKneeAngle;
        obj.rightAnklePivot.rotation.x = supportAnkleAngle;

        obj.leftHipPivot.rotation.x = swingHipAngle;
        obj.leftKneePivot.rotation.x = swingKneeAngle;
        obj.leftAnklePivot.rotation.x = swingAnkleAngle;
    }

    // Arm Kinematics (Opposite to legs)
    const leftShoulderAngle = -(isLeftSupport ? supportHipAngle : swingHipAngle) * 0.9;
    const rightShoulderAngle = -(isLeftSupport ? swingHipAngle : supportHipAngle) * 0.9;
    obj.leftShoulderPivot.rotation.x = leftShoulderAngle;
    obj.rightShoulderPivot.rotation.x = rightShoulderAngle;

    // Elbow Kinematics: Bend more when arm is forward (negative shoulder angle)
    obj.leftElbowPivot.rotation.x = leftShoulderAngle < 0 ? leftShoulderAngle * 0.8 : -0.1;
    obj.rightElbowPivot.rotation.x = rightShoulderAngle < 0 ? rightShoulderAngle * 0.8 : -0.1;

    // Pelvic Kinematics
    // Pelvis drops and sways on the swing side (sine curve peaking mid-swing)
    const pelvicDrop = Math.sin(swingPhase * Math.PI) * 0.1;
    obj.pelvisPivot.rotation.z = isLeftSupport ? pelvicDrop : -pelvicDrop; // Sway
    obj.pelvisPivot.rotation.y = isLeftSupport ? swingHipAngle * 0.2 : -swingHipAngle * 0.2; // Twist
    
    // Vertical bouncing (CoM height varies)
    const bounce = Math.abs(Math.sin(swingPhase * Math.PI)) * 0.05;
    obj.pelvisPivot.position.y = 0.85 - bounce;
}

export function getHumanoidOverlay(row) {
    const vx = row.com_vx || 0, vy = row.com_vy || 0;
    return `
        <div class="data-row"><span class="data-label">time</span><span class="data-value">${row.time.toFixed(2)}s</span></div>
        <div class="data-row"><span class="data-label">CoM x</span><span class="data-value">${row.com_x.toFixed(3)} m</span></div>
        <div class="data-row"><span class="data-label">CoM y</span><span class="data-value">${row.com_y.toFixed(3)} m</span></div>
        <div class="data-row"><span class="data-label">ZMP x</span><span class="data-value">${row.zmp_x.toFixed(3)} m</span></div>
        <div class="data-row"><span class="data-label">ZMP y</span><span class="data-value">${row.zmp_y.toFixed(3)} m</span></div>
        <div class="data-row"><span class="data-label">step</span><span class="data-value">#${row.support_index}</span></div>
        <div class="data-row"><span class="data-label">speed</span><span class="data-value">${Math.sqrt(vx*vx+vy*vy).toFixed(3)} m/s</span></div>
    `;
}

export function getHumanoidCamera(data, idx) {
    const S = 3.0;
    if (idx === undefined) {
        return {
            position: { x: 3, y: 2.5, z: 4, copy(o) { this.x=o.x;this.y=o.y;this.z=o.z; return this; } },
            target: { x: 2.5, y: 0.8, z: 0, copy(o) { this.x=o.x;this.y=o.y;this.z=o.z; return this; } },
        };
    }
    const row = data[idx];
    return {
        followTarget: { x: row.com_x * S, y: 0.8, z: -row.com_y * S },
        followPosition: { x: row.com_x * S - 2.0, y: 1.5, z: -row.com_y * S + 3.0 },
    };
}
