/* 6-DOF Manipulator 3D Model */

export function createManipulatorScene(scene, data, THREE) {
    scene.background = new THREE.Color(0x1a1a2e);
    scene.fog = new THREE.Fog(0x1a1a2e, 10, 50);

    const ambient = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambient);
    const sun = new THREE.DirectionalLight(0xffffff, 1.2);
    sun.position.set(5, 10, 5);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    scene.add(sun);

    // Floor and Grid
    const floor = new THREE.Mesh(
        new THREE.PlaneGeometry(20, 20),
        new THREE.MeshStandardMaterial({ color: 0x222233, roughness: 0.8, metalness: 0.2 })
    );
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    scene.add(floor);
    scene.add(new THREE.GridHelper(20, 40, 0x444466, 0x2a2a3c));

    // Materials
    const matBase = new THREE.MeshStandardMaterial({ color: 0x2c3e50, roughness: 0.7, metalness: 0.4 });
    const matArm = new THREE.MeshStandardMaterial({ color: 0xe0e0e0, roughness: 0.4, metalness: 0.6 });
    const matJoint = new THREE.MeshStandardMaterial({ color: 0xe74c3c, roughness: 0.3, metalness: 0.5 });
    const matEE = new THREE.MeshStandardMaterial({ color: 0xf1c40f, roughness: 0.5, metalness: 0.8 });

    // Link lengths (match python)
    const L1 = 0.4, L2 = 0.6, L3 = 0.5, L4 = 0.15, L5 = 0.15, L6 = 0.1;

    // Base
    const base = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.25, 0.1, 32), matBase);
    base.position.y = 0.05;
    base.castShadow = true;
    scene.add(base);

    // Robot Hierarchy:
    // Root -> J1(Y) -> Link1 -> J2(X) -> Link2 -> J3(X) -> Link3 -> J4(X) -> Link4 -> J5(Y) -> Link5 -> J6(X) -> EE

    // Joint 1 (Base yaw)
    const j1Pivot = new THREE.Group();
    j1Pivot.position.y = 0.1;
    scene.add(j1Pivot);
    const link1 = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, L1, 16), matArm);
    link1.position.y = L1 / 2;
    link1.castShadow = true;
    j1Pivot.add(link1);

    // Joint 2 (Shoulder pitch)
    const j2Pivot = new THREE.Group();
    j2Pivot.position.y = L1;
    j1Pivot.add(j2Pivot);
    const j2Mesh = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.2, 16), matJoint);
    j2Mesh.rotation.z = Math.PI / 2;
    j2Mesh.castShadow = true;
    j2Pivot.add(j2Mesh);
    const link2 = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, L2, 16), matArm);
    link2.position.y = L2 / 2;
    link2.castShadow = true;
    j2Pivot.add(link2);

    // Joint 3 (Elbow pitch)
    const j3Pivot = new THREE.Group();
    j3Pivot.position.y = L2;
    j2Pivot.add(j3Pivot);
    const j3Mesh = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 0.18, 16), matJoint);
    j3Mesh.rotation.z = Math.PI / 2;
    j3Mesh.castShadow = true;
    j3Pivot.add(j3Mesh);
    const link3 = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, L3, 16), matArm);
    link3.position.y = L3 / 2;
    link3.castShadow = true;
    j3Pivot.add(link3);

    // Joint 4 (Wrist 1 pitch) - Note: has a lateral offset
    const j4Pivot = new THREE.Group();
    j4Pivot.position.y = L3;
    j3Pivot.add(j4Pivot);
    const j4Mesh = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.16, 16), matJoint);
    j4Mesh.rotation.z = Math.PI / 2;
    j4Mesh.castShadow = true;
    j4Pivot.add(j4Mesh);
    
    // Link 4 has offset in -Z direction (Python Y maps to -Z in Three)
    const link4 = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, L4, 16), matArm);
    link4.rotation.x = Math.PI / 2;
    link4.position.z = -L4 / 2;
    link4.castShadow = true;
    j4Pivot.add(link4);

    // Joint 5 (Wrist 2 roll)
    const j5Pivot = new THREE.Group();
    j5Pivot.position.z = -L4;
    j4Pivot.add(j5Pivot);
    const j5Mesh = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.14, 16), matJoint);
    j5Mesh.castShadow = true;
    j5Pivot.add(j5Mesh);
    
    const link5 = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, L5, 16), matArm);
    link5.position.y = L5 / 2;
    link5.castShadow = true;
    j5Pivot.add(link5);

    // Joint 6 (Wrist 3 pitch)
    const j6Pivot = new THREE.Group();
    j6Pivot.position.y = L5;
    j5Pivot.add(j6Pivot);
    const j6Mesh = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.12, 16), matJoint);
    j6Mesh.rotation.z = Math.PI / 2;
    j6Mesh.castShadow = true;
    j6Pivot.add(j6Mesh);
    
    // End Effector
    const endEffector = new THREE.Mesh(new THREE.BoxGeometry(0.08, L6, 0.15), matEE);
    endEffector.position.y = L6 / 2;
    endEffector.castShadow = true;
    j6Pivot.add(endEffector);

    // Trajectory lines
    const actualPath = new THREE.BufferGeometry().setFromPoints(data.map(r => new THREE.Vector3(r.ee_x, r.ee_z, -r.ee_y)));
    const actualLine = new THREE.Line(actualPath, new THREE.LineBasicMaterial({ color: 0xff3333, linewidth: 2 }));
    scene.add(actualLine);

    // EE Marker
    const eeMarker = new THREE.Mesh(new THREE.SphereGeometry(0.04, 16, 16), new THREE.MeshBasicMaterial({ color: 0x00ff00 }));
    scene.add(eeMarker);

    return { j1Pivot, j2Pivot, j3Pivot, j4Pivot, j5Pivot, j6Pivot, eeMarker };
}

export function updateManipulator(obj, row) {
    // 6-DOF Joint Angles mapping
    // Python axis mapping:
    // T01: rot Z (yaw) -> Three.js rot Y
    // T12: rot Y (pitch) -> Three.js rot X (since we use X for pitch in our model builder)
    // T23: rot Y -> rot X
    // T34: rot Y -> rot X
    // T45: rot Z -> rot Y
    // T56: rot Y -> rot X
    
    obj.j1Pivot.rotation.y = row.q1;
    obj.j2Pivot.rotation.x = row.q2;
    obj.j3Pivot.rotation.x = row.q3;
    obj.j4Pivot.rotation.x = row.q4;
    obj.j5Pivot.rotation.y = row.q5;
    obj.j6Pivot.rotation.x = row.q6;

    // Python (x, y, z) maps to Three.js (x, z, -y) due to Z-up vs Y-up convention
    // In python: z is up. In Three: y is up. 
    // Python Y is depth, Three Z is depth.
    obj.eeMarker.position.set(row.ee_x, row.ee_z, -row.ee_y);
}

export function getManipulatorOverlay(row) {
    return `
        <div class="data-row"><span class="data-label">time</span><span class="data-value">${row.time.toFixed(2)}s</span></div>
        <div class="data-row"><span class="data-label">q1</span><span class="data-value">${(row.q1 * 180 / Math.PI).toFixed(1)}°</span></div>
        <div class="data-row"><span class="data-label">q2</span><span class="data-value">${(row.q2 * 180 / Math.PI).toFixed(1)}°</span></div>
        <div class="data-row"><span class="data-label">q3</span><span class="data-value">${(row.q3 * 180 / Math.PI).toFixed(1)}°</span></div>
        <div class="data-row"><span class="data-label">q4</span><span class="data-value">${(row.q4 * 180 / Math.PI).toFixed(1)}°</span></div>
        <div class="data-row"><span class="data-label">q5</span><span class="data-value">${(row.q5 * 180 / Math.PI).toFixed(1)}°</span></div>
        <div class="data-row"><span class="data-label">q6</span><span class="data-value">${(row.q6 * 180 / Math.PI).toFixed(1)}°</span></div>
        <div class="data-row"><span class="data-label">EE x</span><span class="data-value">${row.ee_x.toFixed(3)} m</span></div>
        <div class="data-row"><span class="data-label">EE y</span><span class="data-value">${row.ee_y.toFixed(3)} m</span></div>
        <div class="data-row"><span class="data-label">EE z</span><span class="data-value">${row.ee_z.toFixed(3)} m</span></div>
        <div class="data-row"><span class="data-label">tau1</span><span class="data-value">${row.tau1.toFixed(1)} Nm</span></div>
        <div class="data-row"><span class="data-label">tau2</span><span class="data-value">${row.tau2.toFixed(1)} Nm</span></div>
        <div class="data-row"><span class="data-label">tau3</span><span class="data-value">${row.tau3.toFixed(1)} Nm</span></div>
        <div class="data-row"><span class="data-label">tau4</span><span class="data-value">${row.tau4.toFixed(1)} Nm</span></div>
        <div class="data-row"><span class="data-label">tau5</span><span class="data-value">${row.tau5.toFixed(1)} Nm</span></div>
        <div class="data-row"><span class="data-label">tau6</span><span class="data-value">${row.tau6.toFixed(1)} Nm</span></div>
    `;
}

export function getManipulatorCamera(data, idx) {
    return {
        position: { x: 2, y: 1.5, z: 2.5, copy(o) { this.x=o.x;this.y=o.y;this.z=o.z; return this; } },
        target: { x: 0, y: 0.5, z: 0, copy(o) { this.x=o.x;this.y=o.y;this.z=o.z; return this; } },
    };
}
