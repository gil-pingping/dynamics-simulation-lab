/* Drone 3D Model — Advanced Procedural Quadcopter */

export function createDroneScene(scene, data, THREE) {
    scene.background = new THREE.Color(0x0a0c10);
    scene.fog = new THREE.FogExp2(0x0a0c10, 0.015);

    scene.add(new THREE.AmbientLight(0x334455, 0.8));
    const sun = new THREE.DirectionalLight(0xffffee, 1.2);
    sun.position.set(5, 10, 5);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    scene.add(sun);

    // Floor and Grid
    const floor = new THREE.Mesh(
        new THREE.PlaneGeometry(300, 300),
        new THREE.MeshStandardMaterial({ color: 0x111318, roughness: 0.9 })
    );
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    scene.add(floor);
    
    const grid = new THREE.GridHelper(300, 150, 0x00ffff, 0x1a2530);
    grid.position.y = 0.02;
    grid.material.opacity = 0.2;
    grid.material.transparent = true;
    scene.add(grid);

    // --- Materials ---
    const matBody = new THREE.MeshStandardMaterial({ color: 0xecf0f1, metalness: 0.5, roughness: 0.3 });
    const matCarbon = new THREE.MeshStandardMaterial({ color: 0x111111, metalness: 0.8, roughness: 0.7 });
    const matMotor = new THREE.MeshStandardMaterial({ color: 0xc0c0c0, metalness: 0.9, roughness: 0.4 });
    const matProp = new THREE.MeshStandardMaterial({ color: 0x111111, transparent: true, opacity: 0.8, side: THREE.DoubleSide });
    const matLens = new THREE.MeshStandardMaterial({ color: 0x050505, metalness: 1.0, roughness: 0.0 });
    
    const matLEDFront = new THREE.MeshStandardMaterial({ color: 0x00ff00, emissive: 0x00ff00, emissiveIntensity: 2 });
    const matLEDRear = new THREE.MeshStandardMaterial({ color: 0xff0000, emissive: 0xff0000, emissiveIntensity: 2 });

    const root = new THREE.Group();
    scene.add(root);

    // Central Fuselage
    const fuselage = new THREE.Mesh(new THREE.CapsuleGeometry(0.2, 0.4, 16, 16), matBody);
    fuselage.rotation.x = Math.PI / 2;
    fuselage.castShadow = true;
    root.add(fuselage);

    // Gimbal Camera
    const gimbalGroup = new THREE.Group();
    gimbalGroup.position.set(0, -0.15, 0.2); // front-bottom
    root.add(gimbalGroup);
    
    const cameraBody = new THREE.Mesh(new THREE.SphereGeometry(0.08, 16, 16), matCarbon);
    gimbalGroup.add(cameraBody);
    const lens = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.06, 16), matLens);
    lens.rotation.x = Math.PI / 2;
    lens.position.z = 0.06;
    gimbalGroup.add(lens);

    // Arms and Rotors
    const armGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.5, 16);
    const motorGeo = new THREE.CylinderGeometry(0.06, 0.06, 0.08, 16);
    // Propeller: long, flat box
    const propGeo = new THREE.BoxGeometry(0.6, 0.01, 0.04);
    
    const L = 0.35;
    const rotors = [];
    const positions = [
        { x: L, z: L, isFront: true },
        { x: -L, z: L, isFront: true },
        { x: L, z: -L, isFront: false },
        { x: -L, z: -L, isFront: false }
    ];

    positions.forEach(pos => {
        // Arm
        const arm = new THREE.Mesh(armGeo, matCarbon);
        // Point from center to pos
        const angle = Math.atan2(pos.x, pos.z);
        arm.rotation.y = angle;
        arm.rotation.x = Math.PI / 2;
        // Shift along the angle by half length
        arm.position.set(pos.x / 2, 0, pos.z / 2);
        arm.castShadow = true;
        root.add(arm);

        // Motor Mount
        const motor = new THREE.Mesh(motorGeo, matMotor);
        motor.position.set(pos.x, 0.02, pos.z);
        motor.castShadow = true;
        root.add(motor);

        // LED Indicator under motor
        const led = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.02, 16), pos.isFront ? matLEDFront : matLEDRear);
        led.position.set(pos.x, -0.03, pos.z);
        root.add(led);

        // Propeller
        const prop = new THREE.Mesh(propGeo, matProp);
        prop.position.set(pos.x, 0.08, pos.z);
        root.add(prop);
        rotors.push(prop);
    });

    // Trail
    const trailPts = data.map(r => new THREE.Vector3(r.x, r.z, -r.y));
    const trail = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(trailPts),
        new THREE.LineBasicMaterial({ color: 0x00ffff, transparent: true, opacity: 0.5 })
    );
    scene.add(trail);

    return { root, rotors };
}

export function updateDrone(obj, row) {
    // Position: python (x, y, z) -> three.js (x, z, -y)
    obj.root.position.set(row.x, row.z, -row.y);

    // Orientation: euler angles (roll, pitch, yaw)
    // Three.js order must be 'YXZ' to match standard aerodynamics Z-Y-X rotation
    obj.root.rotation.order = 'YXZ';
    obj.root.rotation.y = row.yaw;
    obj.root.rotation.x = row.pitch;  // Pitch tilts nose down/up
    obj.root.rotation.z = -row.roll;  // Roll tilts left/right

    // Spin rotors (visual effect, fast spinning based on time)
    const spinSpeed = 40.0; // rad/s
    obj.rotors.forEach((rotor, i) => {
        // Alternate spin direction for quadcopter (CW and CCW)
        const dir = (i % 2 === 0) ? 1 : -1;
        rotor.rotation.y = row.time * spinSpeed * dir;
    });
}

export function getDroneOverlay(row) {
    return `
        <div class="data-row"><span class="data-label">time</span><span class="data-value">${row.time.toFixed(2)}s</span></div>
        <div class="data-row"><span class="data-label">alt (z)</span><span class="data-value">${row.z.toFixed(2)} m</span></div>
        <div class="data-row"><span class="data-label">x</span><span class="data-value">${row.x.toFixed(2)} m</span></div>
        <div class="data-row"><span class="data-label">y</span><span class="data-value">${row.y.toFixed(2)} m</span></div>
        <div class="data-row"><span class="data-label">roll</span><span class="data-value">${(row.roll * 180 / Math.PI).toFixed(1)}°</span></div>
        <div class="data-row"><span class="data-label">pitch</span><span class="data-value">${(row.pitch * 180 / Math.PI).toFixed(1)}°</span></div>
        <div class="data-row"><span class="data-label">yaw</span><span class="data-value">${(row.yaw * 180 / Math.PI).toFixed(1)}°</span></div>
    `;
}

export function getDroneCamera(data, idx) {
    if (idx === undefined) {
        return {
            position: { x: -4, y: 3, z: 4, copy(o) { this.x=o.x;this.y=o.y;this.z=o.z; return this; } },
            target: { x: 0, y: 1, z: 0, copy(o) { this.x=o.x;this.y=o.y;this.z=o.z; return this; } },
        };
    }
    const row = data[idx];
    return {
        followTarget: { x: row.x, y: row.z, z: -row.y },
        followPosition: { x: row.x - 3, y: row.z + 1.5, z: -row.y + 3 },
    };
}
