from __future__ import annotations

from pathlib import Path
import json
import os
import re

from .common import harness_root, repo_root, utc_id, write_json, write_text, read_json, ledger
from .model_router import route
from .orchestrator_loop import run as run_orchestrator
from .slot_loop import fill as fill_slot
from .run_tools import run_all
from .reviewer_loop import review


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "game"


def game_js() -> str:
    return r'''
const HUD = document.getElementById('hud');
const statusLine = document.getElementById('status');
const restartButton = document.getElementById('restart');

import('https://unpkg.com/three@0.160.0/build/three.module.js').then((THREE) => {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x9fc7ff);
  scene.fog = new THREE.Fog(0x9fc7ff, 120, 650);

  const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 1200);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.shadowMap.enabled = true;
  document.body.appendChild(renderer.domElement);

  const sun = new THREE.DirectionalLight(0xffffff, 2.2);
  sun.position.set(90, 180, 70);
  sun.castShadow = true;
  scene.add(sun);
  scene.add(new THREE.HemisphereLight(0xddeeff, 0x334422, 1.2));

  function heightAt(x, z) {
    return Math.sin(x * 0.018) * 5 + Math.cos(z * 0.021) * 4 + Math.sin((x + z) * 0.009) * 3;
  }

  const terrainSize = 900;
  const terrainSegments = 120;
  const terrain = new THREE.PlaneGeometry(terrainSize, terrainSize, terrainSegments, terrainSegments);
  terrain.rotateX(-Math.PI / 2);
  const pos = terrain.attributes.position;
  for (let i = 0; i < pos.count; i += 1) {
    const x = pos.getX(i);
    const z = pos.getZ(i);
    pos.setY(i, heightAt(x, z));
  }
  terrain.computeVertexNormals();
  const ground = new THREE.Mesh(terrain, new THREE.MeshStandardMaterial({ color: 0x3d7d45, roughness: 0.95, metalness: 0.02 }));
  ground.receiveShadow = true;
  scene.add(ground);

  function makeTree(x, z) {
    const y = heightAt(x, z);
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 1.0, 7, 7), new THREE.MeshStandardMaterial({ color: 0x654321 }));
    trunk.position.set(x, y + 3.5, z);
    const top = new THREE.Mesh(new THREE.ConeGeometry(4.5, 12, 8), new THREE.MeshStandardMaterial({ color: 0x1f5d35 }));
    top.position.set(x, y + 12, z);
    scene.add(trunk, top);
  }

  function makeRock(x, z) {
    const rock = new THREE.Mesh(new THREE.DodecahedronGeometry(2.4, 0), new THREE.MeshStandardMaterial({ color: 0x7f8790, roughness: 1 }));
    rock.position.set(x, heightAt(x, z) + 2.1, z);
    rock.scale.setScalar(0.7 + Math.random() * 1.2);
    scene.add(rock);
  }

  const collectibles = [];
  function makeCollectible(x, z) {
    const gem = new THREE.Mesh(new THREE.IcosahedronGeometry(2.3, 1), new THREE.MeshStandardMaterial({ color: 0xffd24a, emissive: 0x6c4a00, roughness: 0.3 }));
    gem.position.set(x, heightAt(x, z) + 5, z);
    scene.add(gem);
    collectibles.push(gem);
  }

  for (let i = 0; i < 120; i += 1) {
    const x = (Math.random() - 0.5) * terrainSize * 0.9;
    const z = (Math.random() - 0.5) * terrainSize * 0.9;
    if (i % 3 === 0) makeRock(x, z); else makeTree(x, z);
  }
  for (let i = 0; i < 18; i += 1) {
    makeCollectible((Math.random() - 0.5) * 650, (Math.random() - 0.5) * 650);
  }

  const player = new THREE.Mesh(new THREE.CapsuleGeometry(2.2, 5.5, 4, 8), new THREE.MeshStandardMaterial({ color: 0x334cff, roughness: 0.45 }));
  player.castShadow = true;
  scene.add(player);

  const keys = new Set();
  let score = 0;
  let startTime = performance.now();
  let lastTime = performance.now();

  function reset() {
    score = 0;
    startTime = performance.now();
    player.position.set(0, heightAt(0, 0) + 5, 0);
    collectibles.forEach((gem) => { gem.visible = true; });
    statusLine.textContent = 'Explore the generated world and collect the gold cores.';
  }

  window.addEventListener('keydown', (event) => keys.add(event.key.toLowerCase()));
  window.addEventListener('keyup', (event) => keys.delete(event.key.toLowerCase()));
  restartButton.addEventListener('click', reset);
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  function update(dt) {
    const speed = 38;
    let dx = 0;
    let dz = 0;
    if (keys.has('w') || keys.has('arrowup')) dz -= 1;
    if (keys.has('s') || keys.has('arrowdown')) dz += 1;
    if (keys.has('a') || keys.has('arrowleft')) dx -= 1;
    if (keys.has('d') || keys.has('arrowright')) dx += 1;
    const len = Math.hypot(dx, dz) || 1;
    player.position.x += (dx / len) * speed * dt;
    player.position.z += (dz / len) * speed * dt;
    player.position.x = Math.max(-430, Math.min(430, player.position.x));
    player.position.z = Math.max(-430, Math.min(430, player.position.z));
    player.position.y = heightAt(player.position.x, player.position.z) + 5;

    collectibles.forEach((gem) => {
      gem.rotation.y += dt * 2.5;
      gem.position.y = heightAt(gem.position.x, gem.position.z) + 5 + Math.sin(performance.now() * 0.003 + gem.position.x) * 0.8;
      if (gem.visible && gem.position.distanceTo(player.position) < 8) {
        gem.visible = false;
        score += 1;
        statusLine.textContent = score >= collectibles.length ? 'All cores collected. The world is stable.' : 'Core collected.';
      }
    });

    const target = new THREE.Vector3(player.position.x - 28, player.position.y + 22, player.position.z + 38);
    camera.position.lerp(target, 0.08);
    camera.lookAt(player.position.x, player.position.y + 3, player.position.z);

    const elapsed = Math.floor((performance.now() - startTime) / 1000);
    HUD.textContent = `Cores ${score}/${collectibles.length} · Time ${elapsed}s · WASD/Arrows to move`;
  }

  function animate(now) {
    const dt = Math.min(0.05, (now - lastTime) / 1000);
    lastTime = now;
    update(dt);
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }

  reset();
  requestAnimationFrame(animate);
}).catch((error) => {
  statusLine.textContent = 'Three.js failed to load: ' + error.message;
});
'''.strip() + "\n"


def game_index(title: str) -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <link rel="stylesheet" href="./style.css" />
</head>
<body>
  <main id="overlay">
    <h1>{title}</h1>
    <p id="hud">Loading world...</p>
    <p id="status">Collect the gold cores scattered across the generated terrain.</p>
    <button id="restart" type="button">Restart</button>
    <a href="../../index.html">Back to launcher</a>
  </main>
  <script src="./game.js"></script>
</body>
</html>
'''


def game_css() -> str:
    return '''html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; background: #0b1020; color: #f7fbff; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
canvas { display: block; }
#overlay { position: fixed; left: 18px; top: 18px; z-index: 5; width: min(420px, calc(100vw - 36px)); padding: 18px; border: 1px solid rgba(255,255,255,.18); border-radius: 20px; background: rgba(7, 12, 25, .72); backdrop-filter: blur(12px); box-shadow: 0 20px 80px rgba(0,0,0,.32); }
h1 { margin: 0 0 8px; font-size: clamp(26px, 5vw, 48px); line-height: .95; letter-spacing: -.06em; }
p { margin: 8px 0; color: #dbe7ff; line-height: 1.4; }
button, a { display: inline-flex; margin: 8px 8px 0 0; padding: 9px 12px; border-radius: 999px; border: 1px solid rgba(255,255,255,.2); background: rgba(255,255,255,.1); color: #fff; text-decoration: none; font-weight: 800; cursor: pointer; }
'''


def update_launcher(repo: Path, run_id: str, title: str, prompt: str) -> None:
    docs = repo / "docs"
    docs.mkdir(exist_ok=True)
    manifest_path = docs / "games.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = []
    else:
        manifest = []
    manifest = [item for item in manifest if item.get("id") != run_id]
    manifest.insert(0, {"id": run_id, "title": title, "prompt": prompt, "url": f"games/{run_id}/"})
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    cards = []
    for index, item in enumerate(manifest, start=1):
        cards.append(f'<article class="game-card"><div class="rank">#{index:02d}</div><div><h2>{item.get("title", item.get("id"))}</h2><p>{item.get("prompt", "")}</p><a class="play" href="{item.get("url")}">Play this build</a></div></article>')
    launcher = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>NexusLiveLLM Launcher</title><link rel="stylesheet" href="./launcher.css"></head><body><main class="shell"><section class="hero"><p class="eyebrow">NexusLiveLLM</p><h1>Generated Game Ladder</h1><p class="lede">LiveHarnessV.01 generated games. Newest builds appear first.</p><a class="primary" href="games/' + run_id + '/">Play latest build</a></section><section class="ladder">' + ''.join(cards) + '</section></main></body></html>'
    (docs / "index.html").write_text(launcher + "\n", encoding="utf-8")
    if not (docs / "launcher.css").exists():
        (docs / "launcher.css").write_text(':root{color-scheme:dark;font-family:system-ui,sans-serif}body{margin:0;background:#080b14;color:#eef3ff}.shell{width:min(1100px,calc(100% - 32px));margin:auto;padding:48px 0}.hero,.game-card{border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.06);border-radius:24px;padding:24px;margin:14px 0}.eyebrow{color:#9fb7ff;text-transform:uppercase;font-weight:900;letter-spacing:.16em}.primary,.play{display:inline-flex;padding:10px 14px;border-radius:999px;background:#dce8ff;color:#07101f;text-decoration:none;font-weight:900}.game-card{display:grid;grid-template-columns:70px 1fr;gap:16px}.rank{font-size:24px;font-weight:900}\n', encoding="utf-8")


def main() -> None:
    harness = harness_root()
    repo = repo_root()
    prompt = os.environ.get("GAME_PROMPT", "Build a Three.js open-world exploration game.")
    run_stamp = utc_id()
    run_id = run_stamp + "-three-open-world"
    run_dir = harness / "runs" / run_stamp
    title = "Ledgerwood: Three.js Open World"

    write_json(run_dir / "run-summary.json", {"run_id": run_id, "prompt": prompt, "harness": "LiveHarnessV.01"})
    run_orchestrator(run_dir, "root-orchestrator", "whole Three.js open-world game", ["runtime", "world", "player", "gameplay", "visuals", "tests"])
    for name in ["runtime", "world", "player", "gameplay", "visuals", "tests"]:
        run_orchestrator(run_dir, name + "-orchestrator", name + " domain", [])
    fill_slot(run_dir, "terrain-height-function", "js_function", {"function": "heightAt(x,z)", "contract": "returns terrain height in world units"})
    fill_slot(run_dir, "player-controller", "js_system", {"controls": "WASD and arrow keys", "depends_on": "heightAt"})
    fill_slot(run_dir, "launcher-card", "copy", {"title": title, "url": f"games/{run_id}/"})

    game_dir = repo / "docs" / "games" / run_id
    write_text(game_dir / "index.html", game_index(title))
    write_text(game_dir / "style.css", game_css())
    write_text(game_dir / "game.js", game_js())
    write_text(game_dir / "README.md", "# " + title + "\n\nGenerated by LiveHarnessV.01 rapid-game bootstrap path.\n")
    update_launcher(repo, run_id, title, prompt)

    applied = {"files": [str(game_dir / name) for name in ["index.html", "style.css", "game.js", "README.md"]], "manifest": "docs/games.json"}
    write_json(run_dir / "reconcile" / "applied-files.json", applied)
    ledger("action-ledger.jsonl", {"time": utc_id(), "move": "WRITE_FINAL_FILES", "run_id": run_id})
    tools = run_all()
    write_json(run_dir / "tools" / "final-tool-results.json", tools)
    review(run_dir, tools)
    write_json(harness / "state" / "latest.json", {"run_id": run_id, "url": f"docs/games/{run_id}/", "tools_ok": tools.get("ok")})


if __name__ == "__main__":
    main()
