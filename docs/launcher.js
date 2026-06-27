
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
