from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import write_text
from .product_brief import sanitize_public_text


def render_versioned_launcher(docs: Path, manifest: list[dict[str, Any]]) -> None:
    docs.mkdir(parents=True, exist_ok=True)
    latest = str(manifest[0].get("url", "#")) if manifest else "#"
    index_html = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
  <title>NexusRealtime KitBuilder03</title>
  <link rel=\"stylesheet\" href=\"./launcher.css\" />
</head>
<body>
  <main class=\"shell\">
    <section class=\"hero\">
      <p class=\"eyebrow\">one-commit sandbox build</p>
      <h1>KitBuilder03 Active Builds</h1>
      <p class=\"lede\">Builds are grouped by game family. Use the version selector to jump between timestamped builds without scrolling through repeats.</p>
      <a class=\"primary\" id=\"latestLink\" href=\"LATEST_URL\">Play latest build</a>
      <a class=\"secondary\" href=\"./cleanup.html\">Review cleanup ledger</a>
    </section>
    <section class=\"summary-grid\" id=\"summaryGrid\" aria-label=\"Launcher summary\"></section>
    <section class=\"ladder\" id=\"projectList\" aria-label=\"Versioned game list\">
      <article class=\"game-card\"><div class=\"rank\">…</div><div><h2>Loading builds</h2><p>Reading docs/games.json…</p></div></article>
    </section>
  </main>
  <script src=\"./launcher.js\"></script>
</body>
</html>
""".replace("LATEST_URL", latest)
    css = ":root{color-scheme:dark;font-family:system-ui,sans-serif}body{margin:0;background:#06110c;color:#eefbf1}.shell{width:min(1120px,calc(100% - 32px));margin:auto;padding:48px 0}.hero,.game-card,.cleanup-card,.stat{border:1px solid rgba(157,255,190,.22);background:linear-gradient(135deg,rgba(6,28,18,.9),rgba(10,18,32,.84));border-radius:28px;padding:24px;margin:16px 0}.eyebrow{color:#afffc6;text-transform:uppercase;letter-spacing:.16em;font-weight:900}.lede{max-width:820px;color:#cbd8d0;font-size:18px}.primary,.secondary,.play{display:inline-flex;margin:10px 10px 0 0;padding:11px 15px;border-radius:999px;text-decoration:none;font-weight:900}.primary,.play{background:#bfffd2;color:#06110b}.secondary{border:1px solid rgba(255,255,255,.2);color:#eefbf1}.summary-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}.stat{margin:0}.stat strong{display:block;font-size:24px;color:#bfffd2}.stat span{color:#cbd8d0}.game-card{display:grid;grid-template-columns:74px 1fr;gap:18px}.rank{font-size:28px;font-weight:1000;color:#bfffd2}.score{color:#9fffc0;font-weight:900}.card-head{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}.version-pill{display:inline-flex;white-space:nowrap;border:1px solid rgba(191,255,210,.35);border-radius:999px;padding:6px 10px;color:#bfffd2;background:rgba(191,255,210,.08);font-weight:900}.selector-label{display:grid;gap:6px;margin:16px 0 4px;color:#bfffd2;font-weight:900}select.version-select{width:min(100%,620px);padding:12px;border-radius:14px;border:1px solid rgba(255,255,255,.25);background:#071b13;color:#eefbf1;font:inherit}details{margin-top:12px;color:#cbd8d0}summary{cursor:pointer;color:#bfffd2;font-weight:900}table{border-collapse:collapse;width:100%;margin-top:16px}td,th{border:1px solid rgba(255,255,255,.18);padding:8px;text-align:left}th{background:rgba(191,255,210,.14)}td a{color:#bfffd2;font-weight:900}@media(max-width:680px){.game-card{grid-template-columns:1fr}.rank{font-size:22px}.card-head{display:block}}"
    launcher_js = r"""
const projectList = document.querySelector('#projectList');
const summaryGrid = document.querySelector('#summaryGrid');
const latestLink = document.querySelector('#latestLink');
function safeText(value){return String(value||'').replace(/[&<>"']/g,(ch)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
function stamp(value){const raw=String(value||''); const d=new Date(raw.replace(/Z$/,'Z')); return Number.isNaN(d.getTime()) ? (raw||'unknown time') : d.toISOString().replace('.000Z','Z').replace('T',' ');}
function groupKey(item){return String(item.title||item.prompt||item.summary||item.id||'Untitled Build').trim().toLowerCase();}
function titleOf(items){return items[0]?.title||items[0]?.prompt||items[0]?.summary||'Untitled Build';}
function versionLabel(version,item){return `v${version} · ${stamp(item.promoted_at)} · score ${item.score ?? 'n/a'}`;}
function render(games){
  const active=games.filter((item)=>item&&item.visibility!=='hidden');
  if(!active.length){projectList.innerHTML='<article class="game-card"><div class="rank">#00</div><div><h2>No active builds</h2><p>No public builds are currently listed.</p></div></article>';latestLink.href='#';return;}
  latestLink.href=active[0].url||'#';
  const groups=new Map();
  for(const item of active){const key=groupKey(item); if(!groups.has(key))groups.set(key,[]); groups.get(key).push(item);}
  const projects=Array.from(groups.values()).map((items)=>{items.sort((a,b)=>String(b.promoted_at||'').localeCompare(String(a.promoted_at||''))); const oldest=[...items].reverse(); const versionById=new Map(oldest.map((item,index)=>[item.id,index+1])); return {items,latest:items[0],versionById};}).sort((a,b)=>String(b.latest.promoted_at||'').localeCompare(String(a.latest.promoted_at||'')));
  summaryGrid.innerHTML=[`<article class="stat"><strong>${projects.length}</strong><span>game families</span></article>`,`<article class="stat"><strong>${active.length}</strong><span>active builds</span></article>`,`<article class="stat"><strong>${stamp(active[0].promoted_at)}</strong><span>latest timestamp</span></article>`].join('');
  projectList.innerHTML=projects.map((project,i)=>{const title=safeText(titleOf(project.items)); const summary=safeText(project.latest.summary||project.latest.prompt||'No summary available.'); const latestVersion=project.versionById.get(project.latest.id); const options=project.items.map((item)=>{const version=project.versionById.get(item.id); return `<option value="${safeText(item.url)}" ${item===project.latest?'selected':''}>${safeText(versionLabel(version,item))}</option>`;}).join(''); const rows=project.items.map((item)=>{const version=project.versionById.get(item.id); return `<tr><td>v${version}</td><td>${safeText(stamp(item.promoted_at))}</td><td>${safeText(item.score ?? 'n/a')}</td><td><a href="${safeText(item.url)}">Play</a></td></tr>`;}).join(''); return `<article class="game-card version-card"><div class="rank">#${String(i+1).padStart(2,'0')}</div><div class="card-body"><div class="card-head"><div><h2>${title}</h2><p>${summary}</p></div><span class="version-pill">Latest v${latestVersion}</span></div><label class="selector-label">Choose version<select class="version-select">${options}</select></label><a class="play selected-play" href="${safeText(project.latest.url)}">Play selected version</a><details><summary>Show timestamped versions</summary><table><thead><tr><th>Version</th><th>Promoted at</th><th>Score</th><th>Play</th></tr></thead><tbody>${rows}</tbody></table></details></div></article>`;}).join('');
  for(const card of projectList.querySelectorAll('.version-card')){const select=card.querySelector('.version-select'); const play=card.querySelector('.selected-play'); select.addEventListener('change',()=>{play.href=select.value;});}
}
fetch('./games.json',{cache:'no-store'}).then((res)=>res.json()).then(render).catch((error)=>{projectList.innerHTML=`<article class="game-card"><div class="rank">!</div><div><h2>Unable to load builds</h2><p>${safeText(error.message||error)}</p></div></article>`;});
"""
    cleanup = "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Cleanup</title><link rel='stylesheet' href='./launcher.css'></head><body><main class='shell'><section class='hero'><p class='eyebrow'>Cleanup and Learning</p><h1>Rolling Gallery</h1><p class='lede'>The public manifest keeps at most ten active builds. Older outputs are retained as run artifacts or capsules before they are removed from public navigation.</p><a class='secondary' href='./index.html'>Back to launcher</a></section></main></body></html>"
    write_text(docs / "index.html", index_html)
    write_text(docs / "launcher.css", css)
    write_text(docs / "launcher.js", launcher_js)
    write_text(docs / "cleanup.html", cleanup)
