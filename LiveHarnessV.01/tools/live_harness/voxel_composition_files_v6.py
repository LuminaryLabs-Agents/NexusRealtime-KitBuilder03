from __future__ import annotations

from .voxel_world_files_v3 import build_voxel_world_files


def build_voxel_composition_files_v6(candidate_id: str, title: str, summary: str) -> list[dict[str, str]]:
    files = build_voxel_world_files(candidate_id, title, summary)
    base = f"docs/games/{candidate_id}/"
    out = {item["path"]: dict(item) for item in files}

    def put(path: str, content: str, kind: str = "source") -> None:
        out[base + path] = {"path": base + path, "kind": kind, "content": content.rstrip() + "\n"}

    put("index.html", f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title}</title>
  <link rel="stylesheet" href="./style.css" />
  <script type="importmap">
  {{
    "imports": {{
      "@nexus/core": "https://cdn.jsdelivr.net/gh/LuminaryLabs-Dev/NexusRealtime@main/src/index.js",
      "@protokits/action-input": "https://cdn.jsdelivr.net/gh/LuminaryLabs-Agents/NexusRealtime-ProtoKits@main/protokits/action-input-kit/index.js",
      "three": "https://unpkg.com/three@0.160.0/build/three.module.js"
    }}
  }}
  </script>
</head>
<body>
  <main id="app">
    <canvas id="game"></canvas>
    <section id="hud"></section>
    <section id="inventory"></section>
    <section id="inputSurface"></section>
    <section id="errorPanel" hidden></section>
  </main>
  <script type="module" src="./src/boot.js"></script>
</body>
</html>''', "html")

    put("src/boot.js", '''import { resolveAllKits } from "./integration/nexusRuntimeAdapter.js";
const errorPanel = document.querySelector("#errorPanel");
function showFatal(error) { if (errorPanel) { errorPanel.hidden = false; errorPanel.textContent = String(error?.stack ?? error?.message ?? error); } }
resolveAllKits().then((kits) => {
  window.__KitResolution = kits.getState ? kits.getState() : { mode: "local-fallback" };
  return import("./main.js");
}).catch(showFatal);
''')

    put("src/integration/kitResolver.js", '''export async function resolveByAlias(id, alias, fallback) {
  try {
    const module = await import(alias);
    return { id, provider: "remote-kit", module, ok: true, error: null };
  } catch (error) {
    return { id, provider: "local-fallback", module: fallback, ok: false, error: String(error?.message ?? error) };
  }
}
export function summarizeResolved(kits) {
  const resolved = {}; const failures = [];
  for (const [key, value] of Object.entries(kits)) { if (value?.provider) { resolved[key] = value.provider; if (value.error) failures.push({ id: key, error: value.error }); } }
  return { mode: "import-map-with-local-fallback", resolved, failures };
}
''')

    put("src/integration/nexusRuntimeAdapter.js", '''import { resolveByAlias, summarizeResolved } from "./kitResolver.js";
import { createLocalRuntime } from "../runtime/localRuntime.js";
export async function resolveAllKits() {
  const runtime = await resolveByAlias("runtime", "@nexus/core", createLocalRuntime());
  const input = await resolveByAlias("input", "@protokits/action-input", { surface: "local input adapter" });
  const domainService = await resolveByAlias("domainService", "@nexus/core", { surface: "local DSK-shaped domains" });
  const kits = {
    runtime,
    input,
    domainService,
    worldLoader: { id: "worldLoader", provider: "local-fallback", module: { surface: "local world loader" }, ok: true, error: null },
    terrain: { id: "terrain", provider: "local-fallback", module: { surface: "local terrain sampler" }, ok: true, error: null }
  };
  return { ...kits, getState() { return summarizeResolved(kits); } };
}
''')

    put("src/integration/protokitAdapter.js", '''export const protokitAdapter = { mode: "alias-import-with-local-fallback" };
''')
    put("src/runtime/localRuntime.js", '''export function createLocalRuntime() { return { surface: "local runtime fallback" }; }
''')
    put("src/integration/adapters/actionInputAdapter.js", '''export const actionInputAdapter = {
  kit: "protokit.action-input-kit",
  expectedHostInput: ["keydown", "keyup", "pointer"],
  semanticEvents: ["movement.input.request", "inventory.select.request"],
  fallback: "src/host/inputAdapter.js",
  proof(state) { return Boolean(state?.input && state?.movement); }
};
''')
    put("src/integration/adapters/worldPatchAdapter.js", '''export const worldPatchAdapter = {
  kit: "protokit.world-patch-kit",
  expectedState: ["loadedChunks", "recentlyUnloaded", "revision"],
  fallback: "src/world/worldLoader.js",
  proof(state) { return Number.isFinite(state?.worldLoader?.loadedChunks) && Number.isFinite(state?.worldLoader?.revision); }
};
''')
    put("src/integration/adapters/terrainSamplerAdapter.js", '''export const terrainSamplerAdapter = {
  kit: "protokit.terrain-sampler-kit",
  expectedState: ["surfaceY", "biome"],
  fallback: "src/world/chunkStore.js",
  proof(state) { return state?.movement?.biome && Number.isFinite(state?.movement?.surfaceY); }
};
''')
    put("src/integration/adapters/domainServiceAdapter.js", '''export const domainServiceAdapter = {
  kit: "nexusrealtime.domain-service-kit",
  expectedState: ["domainTrace", "appliedCommandIds"],
  fallback: "src/domains/buildBreakDomain.js",
  proof(state) { return Array.isArray(state?.buildBreak?.domainTrace) && Array.isArray(state?.buildBreak?.appliedCommandIds); }
};
''')

    put("src/host/gameHost.js", '''export function installGameHost(parts) {
  window.GameHost = {
    getState() {
      return { clock: parts.clock.getState(), movement: parts.movement.getState(), inventory: parts.inventory.getState(), buildBreak: parts.buildBreak.getState(), sequence: parts.sequence.getState(), world: parts.chunkStore.getState(), worldLoader: parts.worldLoader.getState(), renderer: parts.renderer.getState(), input: parts.input.getState(), events: parts.events.recent(24), integration: window.__KitResolution || { mode: "local-fallback" }, debug: { candidate: "composition-host-v6", spawn: parts.spawnPoint } };
    },
    tick: parts.tick,
    rebuild: () => { parts.worldLoader.forceRefresh(); parts.renderer.rebuild(true); },
    issueCommand(command) { if (command.type === "build.place.request") return parts.buildBreak.requestPlace(command.x, command.y, command.z, command.blockId, command.commandId); if (command.type === "block.break.request") return parts.buildBreak.requestBreak(command.x, command.y, command.z, command.commandId); return null; }
  };
}
''')

    put("README.md", f'''# {title}

{summary}

This app uses a bounded HTML shell, import map, boot module, kit resolver, adapter contracts, and local fallbacks. The active provider state is visible at `window.GameHost.getState().integration`.
''', "readme")
    return list(out.values())
