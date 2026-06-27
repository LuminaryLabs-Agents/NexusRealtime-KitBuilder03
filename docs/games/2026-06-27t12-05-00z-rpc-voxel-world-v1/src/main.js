import * as THREE from "three";

const canvas = document.querySelector("#game");
const hud = document.querySelector("#hud");
const inventoryEl = document.querySelector("#inventory");
const rpcPanel = document.querySelector("#rpcPanel");
const errorPanel = document.querySelector("#errorPanel");

const BLOCKS = [
  { id: 1, key: "grass", name: "Grass", color: 0x55b96f },
  { id: 2, key: "soil", name: "Soil", color: 0x8b5c37 },
  { id: 3, key: "basalt", name: "Basalt", color: 0x59616f },
  { id: 4, key: "copper", name: "Copper", color: 0xc97845 },
  { id: 5, key: "crystal", name: "Crystal", color: 0x80e6ff, transparent: true },
  { id: 6, key: "sand", name: "Sand", color: 0xd9c06d },
  { id: 7, key: "leaf", name: "Leaf", color: 0x3f9d55, transparent: true },
  { id: 8, key: "signal", name: "Signal", color: 0xe7ff8a }
];
const BLOCK_BY_ID = Object.fromEntries(BLOCKS.map((b) => [b.id, b]));

function showFatal(error) {
  errorPanel.hidden = false;
  errorPanel.textContent = String(error?.stack ?? error?.message ?? error);
}

function hash2(x, z, seed = 91027) {
  let h = Math.imul(x, 374761393) ^ Math.imul(z, 668265263) ^ seed;
  h = (h ^ (h >>> 13)) >>> 0;
  h = Math.imul(h, 1274126177) >>> 0;
  return ((h ^ (h >>> 16)) >>> 0) / 4294967295;
}
function smoothNoise(x, z, seed = 91027) {
  const xi = Math.floor(x); const zi = Math.floor(z);
  const xf = x - xi; const zf = z - zi;
  const a = hash2(xi, zi, seed); const b = hash2(xi + 1, zi, seed);
  const c = hash2(xi, zi + 1, seed); const d = hash2(xi + 1, zi + 1, seed);
  const u = xf * xf * (3 - 2 * xf); const v = zf * zf * (3 - 2 * zf);
  return (a * (1 - u) + b * u) * (1 - v) + (c * (1 - u) + d * u) * v;
}
function heightAt(x, z, seed) {
  const a = smoothNoise(x * 0.018, z * 0.018, seed) * 38;
  const b = smoothNoise(x * 0.061 + 20, z * 0.061 - 11, seed + 5) * 10;
  const c = smoothNoise(x * 0.17 - 9, z * 0.17 + 7, seed + 99) * 3;
  return Math.max(2, Math.floor(4 + a + b + c));
}
function biomeAt(x, z, seed) {
  const n = smoothNoise(x * 0.015 - 100, z * 0.015 + 38, seed + 200);
  if (n < 0.22) return "dunes";
  if (n < 0.48) return "moss";
  if (n < 0.74) return "highlands";
  return "crystal ridge";
}

function createWorld(seed = 91027) {
  const overrides = new Map();
  const chunkSize = 16;
  const key = (x, y, z) => `${x},${y},${z}`;
  const chunkKey = (cx, cz) => `${cx},${cz}`;
  const chunkOf = (v) => Math.floor(v / chunkSize);
  function baseBlock(x, y, z) {
    const h = heightAt(x, z, seed);
    if (y < 0 || y > h + 10) return 0;
    if (y === h) {
      const biome = biomeAt(x, z, seed);
      if (biome === "dunes") return 6;
      if (biome === "crystal ridge") return 5;
      if (biome === "highlands") return 3;
      return 1;
    }
    if (y > h - 3) return 2;
    return 3;
  }
  function treeBlock(x, y, z) {
    const h = heightAt(x, z, seed);
    const rooted = hash2(x, z, seed + 4) > 0.988 && biomeAt(x, z, seed) === "moss";
    if (!rooted) return 0;
    if (y > h && y <= h + 5) return 4;
    if (y > h + 4 && y <= h + 7 && Math.abs((x % 5 + 5) % 5 - 2) <= 1 && Math.abs((z % 5 + 5) % 5 - 2) <= 1) return 7;
    return 0;
  }
  function getBlock(x, y, z) {
    const over = overrides.get(key(x, y, z));
    if (over !== undefined) return over;
    return treeBlock(x, y, z) || baseBlock(x, y, z);
  }
  function setBlock(x, y, z, blockId) {
    overrides.set(key(x, y, z), blockId);
  }
  function getSurfaceY(x, z) {
    const top = heightAt(x, z, seed) + 10;
    for (let y = top; y >= 0; y -= 1) if (getBlock(x, y, z)) return y;
    return 0;
  }
  function chunkDescriptor(cx, cz) {
    return { key: chunkKey(cx, cz), cx, cz, biome: biomeAt(cx * chunkSize, cz * chunkSize, seed) };
  }
  function visibleBlocks(chunks) {
    const blocks = [];
    for (const chunk of chunks) {
      for (let lx = 0; lx < chunkSize; lx += 1) for (let lz = 0; lz < chunkSize; lz += 1) {
        const x = chunk.cx * chunkSize + lx;
        const z = chunk.cz * chunkSize + lz;
        const h = heightAt(x, z, seed);
        for (let y = Math.max(0, h - 2); y <= h + 10; y += 1) {
          const blockId = getBlock(x, y, z);
          if (!blockId) continue;
          const exposed = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]].some(([a,b,c]) => !getBlock(x+a, y+b, z+c));
          if (exposed) blocks.push({ x, y, z, blockId });
        }
      }
    }
    return blocks;
  }
  return { seed, chunkSize, overrides, getBlock, setBlock, getSurfaceY, chunkOf, chunkDescriptor, visibleBlocks, heightAt: (x,z) => heightAt(x,z,seed), biomeAt: (x,z) => biomeAt(x,z,seed) };
}

function createRpcServer(world) {
  const applied = new Set();
  const trace = [];
  let sequence = 0;
  function emit(method, payload, ok = true, reason = "") {
    const event = { seq: ++sequence, method, ok, reason, payload, at: performance.now() };
    trace.push(event);
    if (trace.length > 64) trace.shift();
    return event;
  }
  return {
    call(method, payload) {
      const commandId = payload.commandId || `${method}:${sequence}`;
      if (applied.has(commandId)) return emit(method, payload, false, "duplicate commandId");
      applied.add(commandId);
      if (method === "world.placeBlock") {
        if (payload.y < 0 || payload.y > 96) return emit(method, payload, false, "vertical limit");
        world.setBlock(payload.x, payload.y, payload.z, payload.blockId);
        return emit(method, payload, true);
      }
      if (method === "world.clearBlock") {
        world.setBlock(payload.x, payload.y, payload.z, 0);
        return emit(method, payload, true);
      }
      if (method === "world.reseed") return emit(method, payload, true, "client reload required");
      return emit(method, payload, false, "unknown method");
    },
    getState() { return { appliedCommandIds: Array.from(applied).slice(-32), trace: trace.slice(), sequence }; }
  };
}

function createLoader(world, radius = 4) {
  const loaded = new Map();
  const unloaded = [];
  let revision = 0;
  let center = { cx: 0, cz: 0 };
  function tick(player) {
    const cx0 = world.chunkOf(Math.round(player.x));
    const cz0 = world.chunkOf(Math.round(player.z));
    const wanted = new Map();
    center = { cx: cx0, cz: cz0 };
    for (let cx = cx0 - radius; cx <= cx0 + radius; cx += 1) for (let cz = cz0 - radius; cz <= cz0 + radius; cz += 1) {
      const desc = world.chunkDescriptor(cx, cz);
      wanted.set(desc.key, desc);
    }
    let changed = false;
    for (const [k, v] of wanted) if (!loaded.has(k)) { loaded.set(k, v); changed = true; }
    for (const [k, v] of Array.from(loaded.entries())) if (!wanted.has(k) && (Math.abs(v.cx - cx0) > radius + 2 || Math.abs(v.cz - cz0) > radius + 2)) {
      loaded.delete(k); unloaded.push(k); if (unloaded.length > 24) unloaded.shift(); changed = true;
    }
    if (changed) revision += 1;
    return changed;
  }
  return { tick, force: () => { revision += 1; }, blocks: () => world.visibleBlocks(Array.from(loaded.values())), getState: () => ({ center, loadedChunks: loaded.size, recentlyUnloaded: unloaded.slice(-10), revision }) };
}

try {
  const state = {
    world: createWorld(91027),
    player: null,
    keys: new Set(),
    pointerLocked: false,
    selected: 1,
    frame: 0,
    fly: false,
    lastCommand: "none"
  };
  state.player = { x: 0, z: 0, y: state.world.getSurfaceY(0, 0) + 2.2, yaw: 0, pitch: -0.14 };
  state.loader = createLoader(state.world, 4);
  state.rpc = createRpcServer(state.world);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x9bcdfa);
  scene.fog = new THREE.Fog(0x9bcdfa, 42, 180);
  const camera = new THREE.PerspectiveCamera(72, innerWidth / innerHeight, 0.1, 500);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(2, devicePixelRatio || 1));
  renderer.setSize(innerWidth, innerHeight);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x3f6740, 1.25));
  const sun = new THREE.DirectionalLight(0xffffff, 1.7); sun.position.set(28, 64, 24); scene.add(sun);
  const geo = new THREE.BoxGeometry(1,1,1);
  const mats = Object.fromEntries(BLOCKS.map((b) => [b.id, new THREE.MeshStandardMaterial({ color: b.color, roughness: .82, transparent: !!b.transparent, opacity: b.transparent ? .62 : 1 })]));
  const blockGroup = new THREE.Group(); scene.add(blockGroup);
  const helper = new THREE.Object3D();
  let lastRevision = -1;
  let visibleBlocks = 0;

  function rebuild(force = false) {
    if (!force && state.loader.getState().revision === lastRevision) return;
    lastRevision = state.loader.getState().revision;
    blockGroup.clear();
    const buckets = new Map();
    for (const block of state.loader.blocks()) {
      if (!buckets.has(block.blockId)) buckets.set(block.blockId, []);
      buckets.get(block.blockId).push(block);
    }
    visibleBlocks = 0;
    for (const [blockId, blocks] of buckets) {
      visibleBlocks += blocks.length;
      const mesh = new THREE.InstancedMesh(geo, mats[blockId], blocks.length);
      blocks.forEach((block, i) => { helper.position.set(block.x, block.y, block.z); helper.updateMatrix(); mesh.setMatrixAt(i, helper.matrix); });
      blockGroup.add(mesh);
    }
  }
  function targetBlock(distance = 5) {
    const p = state.player;
    const horiz = Math.cos(p.pitch);
    return { x: Math.round(p.x + Math.sin(p.yaw) * horiz * distance), y: Math.max(0, Math.round(p.y + Math.sin(-p.pitch) * distance - 2)), z: Math.round(p.z - Math.cos(p.yaw) * horiz * distance) };
  }
  function rpc(method, payload) {
    const event = state.rpc.call(method, { ...payload, commandId: payload.commandId || `${method}:${state.frame}:${payload.x ?? 0}:${payload.y ?? 0}:${payload.z ?? 0}` });
    state.lastCommand = `${method} ${event.ok ? "ok" : event.reason}`;
    state.loader.force();
    return event;
  }
  canvas.tabIndex = 1;
  canvas.addEventListener("click", () => { canvas.focus(); canvas.requestPointerLock?.(); });
  document.addEventListener("pointerlockchange", () => state.pointerLocked = document.pointerLockElement === canvas);
  document.addEventListener("mousemove", (e) => { if (state.pointerLocked) { state.player.yaw -= e.movementX * .0026; state.player.pitch = Math.max(-1.2, Math.min(1.05, state.player.pitch - e.movementY * .002)); } });
  addEventListener("keydown", (e) => { state.keys.add(e.key.toLowerCase()); const n = Number(e.key); if (n >= 1 && n <= BLOCKS.length) state.selected = n; if (e.key.toLowerCase() === "f") state.fly = !state.fly; if (e.key.toLowerCase() === "r") location.reload(); });
  addEventListener("keyup", (e) => state.keys.delete(e.key.toLowerCase()));
  canvas.addEventListener("contextmenu", (e) => e.preventDefault());
  canvas.addEventListener("pointerdown", (e) => { const t = targetBlock(5); if (e.button === 2) rpc("world.placeBlock", { ...t, blockId: state.selected }); else rpc("world.clearBlock", t); });
  addEventListener("resize", () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });

  function update(dt) {
    state.frame += 1;
    const f = (state.keys.has("w") ? 1 : 0) - (state.keys.has("s") ? 1 : 0);
    const s = (state.keys.has("d") ? 1 : 0) - (state.keys.has("a") ? 1 : 0);
    const speed = state.fly ? 18 : 8;
    state.player.x += Math.sin(state.player.yaw) * f * speed * dt + Math.cos(state.player.yaw) * s * speed * dt;
    state.player.z += -Math.cos(state.player.yaw) * f * speed * dt + Math.sin(state.player.yaw) * s * speed * dt;
    if (state.fly) state.player.y += ((state.keys.has(" ") ? 1 : 0) - (state.keys.has("shift") ? 1 : 0)) * speed * dt;
    else state.player.y += (state.world.getSurfaceY(Math.round(state.player.x), Math.round(state.player.z)) + 2.2 - state.player.y) * Math.min(1, dt * 8);
    state.loader.tick(state.player);
    rebuild();
    camera.position.set(state.player.x, state.player.y, state.player.z);
    camera.rotation.order = "YXZ"; camera.rotation.y = state.player.yaw; camera.rotation.x = state.player.pitch;
  }
  function drawUi() {
    const biome = state.world.biomeAt(Math.round(state.player.x), Math.round(state.player.z));
    const ls = state.loader.getState();
    hud.innerHTML = `<div class="panel"><div class="title">RPC Voxel World V1</div><div class="row"><span class="pill">Biome ${biome}</span><span class="pill">Chunks ${ls.loadedChunks}</span><span class="pill">Blocks ${visibleBlocks}</span><span class="pill">Fly ${state.fly ? "on" : "off"}</span></div><div class="row"><span class="pill">XYZ ${state.player.x.toFixed(1)}, ${state.player.y.toFixed(1)}, ${state.player.z.toFixed(1)}</span><span class="pill">Last ${state.lastCommand}</span></div></div>`;
    inventoryEl.innerHTML = BLOCKS.map((b, i) => `<div class="slot ${state.selected === b.id ? "active" : ""}">${i + 1}<br>${b.name}</div>`).join("");
    rpcPanel.innerHTML = `<div class="title">RPC trace</div>` + state.rpc.getState().trace.slice(-16).reverse().map((e) => `<div class="rpc-line ${e.ok ? "ok" : "warn"}">#${e.seq} ${e.method} ${e.ok ? "ok" : e.reason}</div>`).join("");
  }
  let last = performance.now();
  function frame(now) { const dt = Math.min(1 / 30, (now - last) / 1000 || 1 / 60); last = now; update(dt); renderer.render(scene, camera); drawUi(); requestAnimationFrame(frame); }
  state.loader.tick(state.player); rebuild(true); requestAnimationFrame(frame);
  window.GameHost = { getState: () => ({ player: state.player, inventory: { selected: state.selected, blocks: BLOCKS }, worldLoader: state.loader.getState(), rpc: state.rpc.getState(), visibleBlocks, biome: state.world.biomeAt(Math.round(state.player.x), Math.round(state.player.z)), input: { keys: Array.from(state.keys), pointerLocked: state.pointerLocked }, domainTrace: state.rpc.getState().trace }) };
} catch (error) { showFatal(error); }
