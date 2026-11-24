/* Vehicle 3D Model — Advanced Procedural Sports Car / Cyber-truck Style */

export function createVehicleScene(scene, data, THREE) {
    scene.background = new THREE.Color(0x0a0c10);
    scene.fog = new THREE.FogExp2(0x0a0c10, 0.02);

    scene.add(new THREE.AmbientLight(0x405060, 0.8));
    const sun = new THREE.DirectionalLight(0xffffee, 1.2);
    sun.position.set(5, 10, 5);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    scene.add(sun);

    const pointLight = new THREE.PointLight(0x00ffff, 1.0, 10);
    pointLight.position.set(0, 2, 0);
    scene.add(pointLight);

    // Grid and Floor
    const floor = new THREE.Mesh(
        new THREE.PlaneGeometry(200, 200),
        new THREE.MeshStandardMaterial({ color: 0x111318, roughness: 0.9 })
    );
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    scene.add(floor);
    
    const grid = new THREE.GridHelper(200, 100, 0x00ffff, 0x1a2530);
    grid.position.y = 0.02;
    grid.material.opacity = 0.15;
    grid.material.transparent = true;
    scene.add(grid);

    // Physical dimensions
    const LENGTH = 4.8;
    const WIDTH = 2.0;
    const WHEEL_BASE = 2.8;
    const TRACK_WIDTH = 1.6;
    const WHEEL_RADIUS = 0.35;
    const WHEEL_WIDTH = 0.25;

    // --- Materials ---
    const matBody = new THREE.MeshStandardMaterial({ color: 0x1e272e, metalness: 0.8, roughness: 0.2 });
    const matGlass = new THREE.MeshStandardMaterial({ color: 0x050505, metalness: 0.9, roughness: 0.1, transparent: true, opacity: 0.8 });
    const matTire = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.9 });
    const matRim = new THREE.MeshStandardMaterial({ color: 0xbdc3c7, metalness: 0.9, roughness: 0.3 });
    const matHeadlight = new THREE.MeshStandardMaterial({ color: 0x00ffff, emissive: 0x00ffff, emissiveIntensity: 2.0 });
    const matTaillight = new THREE.MeshStandardMaterial({ color: 0xff0044, emissive: 0xff0044, emissiveIntensity: 2.0 });

    const car = new THREE.Group();
    scene.add(car);

    // Body (Roll/Pitch container)
    const body = new THREE.Group();
    car.add(body);

    // Lower Chassis
    const chassis = new THREE.Mesh(new THREE.BoxGeometry(LENGTH, 0.4, WIDTH), matBody);
    chassis.position.y = WHEEL_RADIUS + 0.2;
    chassis.castShadow = true;
    body.add(chassis);

    // Cabin
    const cabin = new THREE.Mesh(new THREE.BoxGeometry(LENGTH * 0.5, 0.4, WIDTH * 0.8), matBody);
    cabin.position.set(-0.2, WHEEL_RADIUS + 0.6, 0);
    cabin.castShadow = true;
    body.add(cabin);

    // Windows (Glass)
    const glassGeo = new THREE.BoxGeometry(LENGTH * 0.51, 0.38, WIDTH * 0.82);
    const glass = new THREE.Mesh(glassGeo, matGlass);
    glass.position.copy(cabin.position);
    body.add(glass);

    // Headlights
    const hlGeo = new THREE.BoxGeometry(0.1, 0.1, 0.4);
    const hl1 = new THREE.Mesh(hlGeo, matHeadlight);
    hl1.position.set(LENGTH/2, WHEEL_RADIUS + 0.3, WIDTH/2 - 0.3);
    const hl2 = new THREE.Mesh(hlGeo, matHeadlight);
    hl2.position.set(LENGTH/2, WHEEL_RADIUS + 0.3, -(WIDTH/2 - 0.3));
    body.add(hl1);
    body.add(hl2);

    // Taillights
    const tlGeo = new THREE.BoxGeometry(0.1, 0.1, 0.6);
    const tl1 = new THREE.Mesh(tlGeo, matTaillight);
    tl1.position.set(-LENGTH/2, WHEEL_RADIUS + 0.3, WIDTH/2 - 0.4);
    const tl2 = new THREE.Mesh(tlGeo, matTaillight);
    tl2.position.set(-LENGTH/2, WHEEL_RADIUS + 0.3, -(WIDTH/2 - 0.4));
    body.add(tl1);
    body.add(tl2);

    // Wheels
    const tireGeo = new THREE.CylinderGeometry(WHEEL_RADIUS, WHEEL_RADIUS, WHEEL_WIDTH, 32);
    const rimGeo = new THREE.CylinderGeometry(WHEEL_RADIUS * 0.7, WHEEL_RADIUS * 0.7, WHEEL_WIDTH * 1.05, 16);
    const spokeGeo = new THREE.BoxGeometry(WHEEL_RADIUS * 1.3, WHEEL_WIDTH * 1.1, 0.05);

    function createWheelMesh() {
        const wGroup = new THREE.Group();
        const tire = new THREE.Mesh(tireGeo, matTire);
        tire.castShadow = true;
        wGroup.add(tire);
        const rim = new THREE.Mesh(rimGeo, matRim);
        wGroup.add(rim);
        // Spokes
        for(let i=0; i<3; i++) {
            const spoke = new THREE.Mesh(spokeGeo, matRim);
            spoke.rotation.y = i * Math.PI / 3;
            wGroup.add(spoke);
        }
        return wGroup;
    }

    const wheelRefs = [];
    const frontPivots = [];

    const wheelPositions = [
        { x: WHEEL_BASE/2, z: TRACK_WIDTH/2, isFront: true },
        { x: WHEEL_BASE/2, z: -TRACK_WIDTH/2, isFront: true },
        { x: -WHEEL_BASE/2, z: TRACK_WIDTH/2, isFront: false },
        { x: -WHEEL_BASE/2, z: -TRACK_WIDTH/2, isFront: false },
    ];

    wheelPositions.forEach(pos => {
        const steeringPivot = new THREE.Group();
        steeringPivot.position.set(pos.x, WHEEL_RADIUS, pos.z);
        body.add(steeringPivot);

        const axleOrient = new THREE.Group();
        axleOrient.rotation.x = Math.PI / 2;
        steeringPivot.add(axleOrient);

        const wheelMesh = createWheelMesh();
        axleOrient.add(wheelMesh);

        wheelRefs.push({ steeringPivot, axleOrient, wheelMesh, isFront: pos.isFront });
        if (pos.isFront) {
            frontPivots.push(steeringPivot);
        }
    });

    // Trail
    const trail = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(data.map(r => new THREE.Vector3(r.x, 0.05, -(r.y || 0)))),
        new THREE.LineBasicMaterial({ color: 0xff0044, transparent: true, opacity: 0.6 })
    );
    scene.add(trail);

    // Reference path
    if (data[0].road_y !== undefined || data[0].ref_y !== undefined) {
        const refKey = data[0].road_y !== undefined ? 'road_y' : 'ref_y';
        const refPoints = data.map(r => new THREE.Vector3(r.x, 0.06, -(r[refKey] || 0)));
        scene.add(new THREE.Line(
            new THREE.BufferGeometry().setFromPoints(refPoints),
            new THREE.LineBasicMaterial({ color: 0x00ffff, transparent: true, opacity: 0.4 })
        ));
    }

    // Precompute absolute wheel rotation angles based on speed and radius
    const wheelAngles = new Float64Array(data.length);
    wheelAngles[0] = 0;
    for (let i = 1; i < data.length; i++) {
        const dt = data[i].time - data[i - 1].time;
        const speed = Math.abs(data[i].speed || data[i - 1].speed || 0);
        wheelAngles[i] = wheelAngles[i - 1] + (speed * dt) / WHEEL_RADIUS;
    }

    // Trailer for articulated vehicle
    let trailer = null;
    if (data[0].trailer_yaw !== undefined) {
        trailer = new THREE.Group();
        
        // Trailer container
        const tMesh = new THREE.Mesh(
            new THREE.BoxGeometry(6.0, 2.0, 2.2),
            new THREE.MeshStandardMaterial({ color: 0x2980b9, metalness: 0.6, roughness: 0.3 })
        );
        tMesh.position.y = 1.3;
        tMesh.castShadow = true;
        trailer.add(tMesh);

        // Trailer wheels
        [[-2.5, 1.1], [-2.5, -1.1]].forEach(([xx, zz]) => {
            const axleOrient = new THREE.Group();
            axleOrient.position.set(xx, WHEEL_RADIUS, zz);
            axleOrient.rotation.x = Math.PI / 2;
            trailer.add(axleOrient);
            
            const w = createWheelMesh();
            axleOrient.add(w);
            wheelRefs.push({ axleOrient, wheelMesh: w, isFront: false });
        });
        scene.add(trailer);
    }

    return { car, wheelRefs, frontPivots, trailer, wheelAngles, body };
}

export function updateVehicle(obj, row, data, idx, THREE) {
    const yaw = row.yaw || row.tractor_yaw || 0;

    obj.car.position.set(row.x, 0, -(row.y || 0));
    obj.car.rotation.y = yaw;

    // Body roll & pitch
    if (row.roll_deg !== undefined) {
        obj.body.rotation.z = -(row.roll_deg * Math.PI / 180);
    }
    if (row.pitch_deg !== undefined) {
        obj.body.rotation.x = (row.pitch_deg * Math.PI / 180);
    }

    // Steering
    const steering = row.steering || 0;
    obj.frontPivots.forEach(p => { p.rotation.y = steering; });

    // Wheel roll
    const rollAngle = obj.wheelAngles[idx] || 0;
    obj.wheelRefs.forEach(wr => {
        // Rotate the inner mesh around its local Y axis (which is aligned to the axle)
        wr.wheelMesh.rotation.y = rollAngle;
    });

    // Trailer
    if (obj.trailer && row.trailer_yaw !== undefined) {
        const ty = row.trailer_yaw;
        const hitchX = row.x - 2.5 * Math.cos(yaw);
        const hitchY = (row.y || 0) - 2.5 * Math.sin(yaw);
        obj.trailer.position.set(hitchX - 3.1 * Math.cos(ty), 0, -(hitchY - 3.1 * Math.sin(ty)));
        obj.trailer.rotation.y = ty;
    }
}

export function getVehicleOverlay(row) {
    let html = `<div class="data-row"><span class="data-label">time</span><span class="data-value">${row.time.toFixed(2)}s</span></div>`;
    html += `<div class="data-row"><span class="data-label">x</span><span class="data-value">${row.x.toFixed(1)} m</span></div>`;
    html += `<div class="data-row"><span class="data-label">y</span><span class="data-value">${(row.y || 0).toFixed(2)} m</span></div>`;
    const yaw = row.yaw || row.tractor_yaw || 0;
    html += `<div class="data-row"><span class="data-label">yaw</span><span class="data-value">${(yaw * 180 / Math.PI).toFixed(1)}°</span></div>`;
    html += `<div class="data-row"><span class="data-label">speed</span><span class="data-value">${(row.speed || 0).toFixed(1)} m/s</span></div>`;
    if (row.steering !== undefined) html += `<div class="data-row"><span class="data-label">steer</span><span class="data-value">${(row.steering * 180 / Math.PI).toFixed(1)}°</span></div>`;
    if (row.sideslip_deg !== undefined) html += `<div class="data-row"><span class="data-label">sideslip</span><span class="data-value">${row.sideslip_deg.toFixed(1)}°</span></div>`;
    if (row.roll_deg !== undefined) html += `<div class="data-row"><span class="data-label">roll</span><span class="data-value">${row.roll_deg.toFixed(1)}°</span></div>`;
    if (row.trailer_yaw !== undefined) html += `<div class="data-row"><span class="data-label">t_yaw</span><span class="data-value">${(row.trailer_yaw * 180 / Math.PI).toFixed(1)}°</span></div>`;
    return html;
}

export function getVehicleCamera(data, idx) {
    if (idx === undefined) {
        return {
            position: { x: -8, y: 5, z: 8, copy(o) { this.x=o.x;this.y=o.y;this.z=o.z; return this; } },
            target: { x: 0, y: 0, z: 0, copy(o) { this.x=o.x;this.y=o.y;this.z=o.z; return this; } },
        };
    }
    const row = data[idx];
    const isTrailer = row.trailer_yaw !== undefined;
    return {
        followTarget: { x: row.x, y: 1, z: -(row.y || 0) },
        followPosition: { x: row.x - (isTrailer ? 15 : 10), y: 6, z: -(row.y || 0) + 10 },
    };
}
