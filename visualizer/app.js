import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { createVehicleScene, updateVehicle, getVehicleOverlay, getVehicleCamera } from './models/vehicle.js';
import { createManipulatorScene, updateManipulator, getManipulatorOverlay, getManipulatorCamera } from './models/manipulator.js';
import { createHumanoidScene, updateHumanoid, getHumanoidOverlay, getHumanoidCamera } from './models/humanoid.js';
import { createDroneScene, updateDrone, getDroneOverlay, getDroneCamera } from './models/drone.js';
import { createSatelliteScene, updateSatellite, getSatelliteOverlay, getSatelliteCamera } from './models/satellite.js';

/* ── CSV Parser ── */
async function loadCSV(filename) {
    const resp = await fetch(`../outputs/${filename}.csv`);
    const text = await resp.text();
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',');
    return lines.slice(1).map(line => {
        const vals = line.split(',');
        const obj = {};
        headers.forEach((h, i) => obj[h.trim()] = parseFloat(vals[i]));
        return obj;
    });
}

/* ── Simulation Registry ── */
const SIM_CONFIG = {
    vehicle_lane_change: { type: 'vehicle', file: 'vehicle_lane_change', label: 'Lane Change' },
    vehicle_drift_transition: { type: 'vehicle', file: 'vehicle_drift_transition', label: 'Drift' },
    vehicle_kinematic_bicycle_parking: { type: 'vehicle', file: 'vehicle_kinematic_bicycle_parking', label: 'Parking' },
    vehicle_ackermann_steering_course: { type: 'vehicle', file: 'vehicle_ackermann_steering_course', label: 'Ackermann' },
    vehicle_double_track_obstacle_avoidance: { type: 'vehicle', file: 'vehicle_double_track_obstacle_avoidance', label: 'Double Track' },
    vehicle_skid_steer_maneuver: { type: 'vehicle', file: 'vehicle_skid_steer_maneuver', label: 'Skid Steer' },
    vehicle_articulated_s_curve: { type: 'vehicle', file: 'vehicle_articulated_s_curve', label: 'Articulated' },
    vehicle_offroad_traverse: { type: 'vehicle', file: 'vehicle_offroad_traverse', label: 'Off-road' },
    vehicle_full_vehicle_handling: { type: 'vehicle', file: 'vehicle_full_vehicle_handling', label: 'Full Vehicle' },
    manipulator_tracking: { type: 'manipulator', file: 'manipulator_tracking', label: 'Manipulator' },
    humanoid_walk: { type: 'humanoid', file: 'humanoid_walk', label: 'Humanoid Walk' },
    drone_mission: { type: 'drone', file: 'drone_mission', label: 'Drone Mission' },
    satellite_orbit_raise: { type: 'satellite', file: 'satellite_orbit_raise', label: 'Satellite Orbit' },
};

const SCENE_BUILDERS = { vehicle: createVehicleScene, manipulator: createManipulatorScene, humanoid: createHumanoidScene, drone: createDroneScene, satellite: createSatelliteScene };
const UPDATERS = { vehicle: updateVehicle, manipulator: updateManipulator, humanoid: updateHumanoid, drone: updateDrone, satellite: updateSatellite };
const OVERLAY_FNS = { vehicle: getVehicleOverlay, manipulator: getManipulatorOverlay, humanoid: getHumanoidOverlay, drone: getDroneOverlay, satellite: getSatelliteOverlay };
const CAMERA_FNS = { vehicle: getVehicleCamera, manipulator: getManipulatorCamera, humanoid: getHumanoidCamera, drone: getDroneCamera, satellite: getSatelliteCamera };

/* ── App State ── */
const state = {
    currentSim: 'vehicle_lane_change',
    data: null,
    frameIndex: 0,
    playing: false,
    speed: 1,
    follow: true,
    sceneObjects: null,
    lastTime: 0,
    accumulator: 0,
};

/* ── Three.js Setup ── */
const container = document.getElementById('canvas-container');
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 100000000);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 1;
controls.maxDistance = 50000000;

function resize() {
    const w = container.clientWidth, h = container.clientHeight;
    if (w === 0 || h === 0) return;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
}
window.addEventListener('resize', resize);

/* ── UI Elements ── */
const btnPlay = document.getElementById('btn-play');
const btnReset = document.getElementById('btn-reset');
const timeline = document.getElementById('timeline');
const timeDisplay = document.getElementById('time-display');
const dataContent = document.getElementById('data-content');
const loadingOverlay = document.getElementById('loading-overlay');
const cameraFollow = document.getElementById('camera-follow');

btnPlay.addEventListener('click', () => {
    state.playing = !state.playing;
    btnPlay.textContent = state.playing ? '⏸' : '▶';
    btnPlay.classList.toggle('active', state.playing);
    state.lastTime = performance.now();
});

btnReset.addEventListener('click', () => {
    state.frameIndex = 0;
    state.accumulator = 0;
    timeline.value = 0;
    updateFrame();
});

timeline.addEventListener('input', () => {
    if (!state.data) return;
    state.frameIndex = Math.round((timeline.value / 1000) * (state.data.length - 1));
    state.accumulator = 0;
    updateFrame();
});

document.querySelectorAll('.speed-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.speed = parseFloat(btn.dataset.speed);
    });
});

cameraFollow.addEventListener('change', () => { state.follow = cameraFollow.checked; });

document.querySelectorAll('.sim-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.sim-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        loadSimulation(btn.dataset.sim);
    });
});

/* ── Scene Management ── */
async function loadSimulation(simKey) {
    loadingOverlay.classList.remove('hidden');
    state.currentSim = simKey;
    state.frameIndex = 0;
    state.accumulator = 0;
    state.playing = false;
    btnPlay.textContent = '▶';
    btnPlay.classList.remove('active');

    const config = SIM_CONFIG[simKey];
    try {
        state.data = await loadCSV(config.file);
    } catch (e) {
        console.error('CSV load failed:', e);
        loadingOverlay.classList.add('hidden');
        return;
    }

    // Clear scene
    while (scene.children.length > 0) scene.remove(scene.children[0]);

    // Build scene
    const builder = SCENE_BUILDERS[config.type];
    state.sceneObjects = builder(scene, state.data, THREE);

    // Set camera
    const camInfo = CAMERA_FNS[config.type](state.data);
    camera.position.copy(camInfo.position);
    controls.target.copy(camInfo.target);
    controls.update();

    resize();
    updateFrame();

    setTimeout(() => loadingOverlay.classList.add('hidden'), 200);
}

function updateFrame() {
    if (!state.data || !state.sceneObjects) return;
    const config = SIM_CONFIG[state.currentSim];
    const row = state.data[state.frameIndex];

    UPDATERS[config.type](state.sceneObjects, row, state.data, state.frameIndex, THREE);

    // Camera follow
    if (state.follow) {
        const camInfo = CAMERA_FNS[config.type](state.data, state.frameIndex);
        if (camInfo.followTarget) {
            controls.target.lerp(camInfo.followTarget, 0.1);
            if (camInfo.followPosition) {
                camera.position.lerp(camInfo.followPosition, 0.05);
            }
        }
    }

    // Time display
    const t = row.time;
    const tMax = state.data[state.data.length - 1].time;
    timeDisplay.textContent = `${t.toFixed(2)}s / ${tMax.toFixed(2)}s`;
    timeline.value = Math.round((state.frameIndex / (state.data.length - 1)) * 1000);

    // Data overlay
    const overlayHTML = OVERLAY_FNS[config.type](row);
    dataContent.innerHTML = overlayHTML;
}

/* ── Animation Loop ── */
function animate(now) {
    requestAnimationFrame(animate);

    if (state.playing && state.data) {
        const dt = (now - state.lastTime) / 1000;
        state.lastTime = now;
        if (dt > 0 && dt < 0.5) {
            const simDt = state.data.length > 1 ? (state.data[1].time - state.data[0].time) : 0.01;
            state.accumulator += dt * state.speed;
            while (state.accumulator >= simDt && state.frameIndex < state.data.length - 1) {
                state.frameIndex++;
                state.accumulator -= simDt;
            }
            if (state.frameIndex >= state.data.length - 1) {
                state.playing = false;
                btnPlay.textContent = '▶';
                btnPlay.classList.remove('active');
            }
            updateFrame();
        }
    }

    controls.update();
    renderer.render(scene, camera);
}

/* ── Boot ── */
loadSimulation('vehicle_lane_change').then(() => {
    state.lastTime = performance.now();
    animate(state.lastTime);
});
