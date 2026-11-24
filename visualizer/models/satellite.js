/* Satellite 3D Model — Advanced Procedural Orbiter */

export function createSatelliteScene(scene, data, THREE) {
    scene.background = new THREE.Color(0x020305);
    // No fog in space
    scene.fog = null;

    const ambient = new THREE.AmbientLight(0x222233, 0.4);
    scene.add(ambient);
    const sun = new THREE.DirectionalLight(0xffffee, 2.0);
    // Place sun far away to simulate space lighting
    sun.position.set(100, 50, 100);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    scene.add(sun);

    // Starfield background
    const starsGeo = new THREE.BufferGeometry();
    const starsVertices = [];
    for(let i=0; i<1000; i++) {
        const x = (Math.random() - 0.5) * 1000;
        const y = (Math.random() - 0.5) * 1000;
        const z = (Math.random() - 0.5) * 1000;
        starsVertices.push(x, y, z);
    }
    starsGeo.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
    const starsMat = new THREE.PointsMaterial({ color: 0xffffff, size: 1.5, sizeAttenuation: false });
    const starField = new THREE.Points(starsGeo, starsMat);
    scene.add(starField);

    // Earth (giant sphere below)
    const earthRadius = 6371000; 
    const earthGeo = new THREE.SphereGeometry(earthRadius, 64, 64);
    // Simple shader-like blue sphere since we don't have textures
    const earthMat = new THREE.MeshStandardMaterial({ 
        color: 0x1e3d59, 
        emissive: 0x0a1a2a,
        roughness: 0.7,
        metalness: 0.1
    });
    const earth = new THREE.Mesh(earthGeo, earthMat);
    // Earth is at origin (0,0,0) in our simulation data coords usually, but let's check
    // Wait, in simulation data, satellite x,y are in orbit (~6.8e6 m).
    // So earth is at 0,0,0.
    earth.position.set(0, 0, 0);
    scene.add(earth);

    // Adding some simple atmosphere glow to Earth
    const atmosGeo = new THREE.SphereGeometry(earthRadius * 1.02, 64, 64);
    const atmosMat = new THREE.MeshBasicMaterial({
        color: 0x4ca1af,
        transparent: true,
        opacity: 0.15,
        side: THREE.BackSide
    });
    const atmos = new THREE.Mesh(atmosGeo, atmosMat);
    scene.add(atmos);

    // --- Satellite Materials ---
    // Kapton Gold Foil
    const matFoil = new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.8, roughness: 0.4 });
    // Silver metal for antennas
    const matMetal = new THREE.MeshStandardMaterial({ color: 0xbdc3c7, metalness: 0.9, roughness: 0.3 });
    // Dark blue/black solar cells
    const matSolar = new THREE.MeshStandardMaterial({ color: 0x112244, metalness: 0.6, roughness: 0.2, side: THREE.DoubleSide });
    // White structural parts
    const matWhite = new THREE.MeshStandardMaterial({ color: 0xeeeeee, metalness: 0.2, roughness: 0.5 });

    // SCALE factor since distances are in millions of meters
    const S = 0.001; 
    // Satellite visual size is boosted heavily to be seen in space
    const satSize = 50000; 

    const root = new THREE.Group();
    scene.add(root);

    // Satellite Bus (Hexagonal Prism)
    const busGeo = new THREE.CylinderGeometry(satSize, satSize, satSize * 2, 6);
    const bus = new THREE.Mesh(busGeo, matFoil);
    bus.rotation.x = Math.PI / 2; // Point cylinder forward
    bus.castShadow = true;
    root.add(bus);

    // Parabolic Dish Antenna
    const dishGroup = new THREE.Group();
    dishGroup.position.set(0, satSize, 0); // Top of the bus
    root.add(dishGroup);

    // Using sphere slice for dish
    const dishGeo = new THREE.SphereGeometry(satSize * 0.8, 16, 16, 0, Math.PI * 2, 0, Math.PI / 3);
    const dish = new THREE.Mesh(dishGeo, matWhite);
    dish.rotation.x = -Math.PI / 2; // Face outwards
    dish.material.side = THREE.DoubleSide;
    dishGroup.add(dish);
    
    // Dish receiver
    const receiver = new THREE.Mesh(new THREE.CylinderGeometry(satSize*0.05, satSize*0.05, satSize*0.6), matMetal);
    receiver.position.set(0, satSize*0.3, 0);
    dishGroup.add(receiver);

    // Solar Panels (Segmented)
    const wingLength = satSize * 4;
    const wingWidth = satSize * 1.5;
    const panelGeo = new THREE.BoxGeometry(wingLength, wingWidth, satSize * 0.1);

    const leftWing = new THREE.Group();
    leftWing.position.set(satSize + wingLength/2, 0, 0);
    root.add(leftWing);
    
    // Segment 1
    const p1 = new THREE.Mesh(panelGeo, matSolar);
    leftWing.add(p1);
    // Segment 2
    const p2 = new THREE.Mesh(panelGeo, matSolar);
    p2.position.set(wingLength + satSize * 0.2, 0, 0);
    leftWing.add(p2);

    const rightWing = new THREE.Group();
    rightWing.position.set(-(satSize + wingLength/2), 0, 0);
    root.add(rightWing);
    
    const p3 = new THREE.Mesh(panelGeo, matSolar);
    rightWing.add(p3);
    const p4 = new THREE.Mesh(panelGeo, matSolar);
    p4.position.set(-(wingLength + satSize * 0.2), 0, 0);
    rightWing.add(p4);

    // Structural connecting beams
    const beamGeo = new THREE.CylinderGeometry(satSize*0.1, satSize*0.1, satSize*2, 8);
    const lBeam = new THREE.Mesh(beamGeo, matMetal);
    lBeam.rotation.z = Math.PI / 2;
    lBeam.position.set(satSize, 0, 0);
    root.add(lBeam);
    const rBeam = new THREE.Mesh(beamGeo, matMetal);
    rBeam.rotation.z = Math.PI / 2;
    rBeam.position.set(-satSize, 0, 0);
    root.add(rBeam);

    // Orbit Trail
    const trailPts = data.map(r => new THREE.Vector3(r.x, r.z || 0, -r.y));
    const trail = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(trailPts),
        new THREE.LineBasicMaterial({ color: 0xff44aa, transparent: true, opacity: 0.6, linewidth: 2 })
    );
    scene.add(trail);

    return { root, leftWing, rightWing, S };
}

export function updateSatellite(obj, row) {
    // Position
    obj.root.position.set(row.x, row.z || 0, -row.y);

    // Orientation (pitch)
    obj.root.rotation.order = 'YXZ';
    obj.root.rotation.x = row.pitch;

    // Track sun with solar panels (simple rotation based on time to simulate tracking)
    // The panels rotate around the local X axis to face the sun
    const trackingAngle = row.time * 0.1; 
    obj.leftWing.rotation.x = trackingAngle;
    obj.rightWing.rotation.x = trackingAngle;
}

export function getSatelliteOverlay(row) {
    const r = Math.sqrt(row.x*row.x + row.y*row.y);
    const alt = r - 6371000;
    return `
        <div class="data-row"><span class="data-label">time</span><span class="data-value">${row.time.toFixed(1)}s</span></div>
        <div class="data-row"><span class="data-label">altitude</span><span class="data-value">${(alt / 1000).toFixed(1)} km</span></div>
        <div class="data-row"><span class="data-label">x</span><span class="data-value">${(row.x / 1000).toFixed(1)} km</span></div>
        <div class="data-row"><span class="data-label">y</span><span class="data-value">${(row.y / 1000).toFixed(1)} km</span></div>
        <div class="data-row"><span class="data-label">speed</span><span class="data-value">${(row.speed / 1000).toFixed(2)} km/s</span></div>
        <div class="data-row"><span class="data-label">pitch</span><span class="data-value">${(row.pitch * 180 / Math.PI).toFixed(1)}°</span></div>
    `;
}

export function getSatelliteCamera(data, idx) {
    if (idx === undefined) {
        return {
            position: { x: 0, y: 15000000, z: 20000000, copy(o) { this.x=o.x;this.y=o.y;this.z=o.z; return this; } },
            target: { x: 0, y: 0, z: 0, copy(o) { this.x=o.x;this.y=o.y;this.z=o.z; return this; } },
        };
    }
    const row = data[idx];
    // Follow camera stays near satellite
    // Since satellite coordinates are massive, offsets must be massive
    const offset = 400000;
    return {
        followTarget: { x: row.x, y: row.z || 0, z: -row.y },
        followPosition: { x: row.x + offset, y: (row.z || 0) + offset, z: -row.y + offset },
    };
}
