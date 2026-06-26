// game.js
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');

const W = canvas.width;
const H = canvas.height;

// Game state
let score = 0;
let running = true;
let player = { x: W/2, y: H/2, r: 12, speed: 4 };
let tokens = [];
let glitches = [];
const tokenCount = 8;
const glitchCount = 5;

// Input
const keys = {};
window.addEventListener('keydown', e => { keys[e.code] = true; if(e.code==='KeyR') restart(); });
window.addEventListener('keyup', e => { keys[e.code] = false; });

function spawnToken() {
  const margin = 30;
  return {
    x: Math.random()*(W-2*margin)+margin,
    y: Math.random()*(H-2*margin)+margin,
    r: 8,
    collected: false
  };
}
function spawnGlitch() {
  const margin = 30;
  return {
    x: Math.random()*(W-2*margin)+margin,
    y: Math.random()*(H-2*margin)+margin,
    r: 10,
    angle: Math.random()*Math.PI*2,
    speed: 1.5 + Math.random()*1.5
  };
}
function init() {
  tokens = Array.from({length: tokenCount}, spawnToken);
  glitches = Array.from({length: glitchCount}, spawnGlitch);
  player.x = W/2; player.y = H/2;
  score = 0;
  updateScore();
  running = true;
}
function updateScore() { scoreEl.textContent = 'Score: ' + score; }

function restart() { init(); }

function update() {
  if(!running) return;
  // Player movement
  if(keys['ArrowUp'] || keys['KeyW']) player.y -= player.speed;
  if(keys['ArrowDown'] || keys['KeyS']) player.y += player.speed;
  if(keys['ArrowLeft'] || keys['KeyA']) player.x -= player.speed;
  if(keys['ArrowRight'] || keys['KeyD']) player.x += player.speed;
  // Clamp
  player.x = Math.max(player.r, Math.min(W-player.r, player.x));
  player.y = Math.max(player.r, Math.min(H-player.r, player.y));

  // Token collection
  tokens.forEach(t => {
    if(!t.collected) {
      const dx = t.x - player.x;
      const dy = t.y - player.y;
      if(dx*dx + dy*dy < (t.r + player.r)*(t.r + player.r)) {
        t.collected = true;
        score += 10;
        updateScore();
        // respawn token after short delay
        setTimeout(() => {
          Object.assign(t, spawnToken());
          t.collected = false;
        }, 1500);
      }
    }
  });

  // Glitch movement and collision
  glitches.forEach(g => {
    g.x += Math.cos(g.angle) * g.speed;
    g.y += Math.sin(g.angle) * g.speed;
    // bounce off walls
    if(g.x < g.r || g.x > W - g.r) g.angle = Math.PI - g.angle;
    if(g.y < g.r || g.y > H - g.r) g.angle = -g.angle;
    // collision with player
    const dx = g.x - player.x;
    const dy = g.y - player.y;
    if(dx*dx + dy*dy < (g.r + player.r)*(g.r + player.r)) {
      running = false;
    }
  });
}

function draw() {
  ctx.clearRect(0,0,W,H);
  // Draw tokens
  tokens.forEach(t => {
    if(!t.collected) {
      ctx.beginPath();
      ctx.arc(t.x, t.y, t.r, 0, Math.PI*2);
      ctx.fillStyle = '#0f0';
      ctx.fill();
      ctx.strokeStyle = '#0a0';
      ctx.lineWidth = 2;
      ctx.stroke();
    }
  });
  // Draw glitches
  glitches.forEach(g => {
    ctx.save();
    ctx.translate(g.x, g.y);
    ctx.rotate(g.angle);
    ctx.beginPath();
    ctx.moveTo(-g.r, -g.r);
    ctx.lineTo(g.r, g.r);
    ctx.moveTo(g.r, -g.r);
    ctx.lineTo(-g.r, g.r);
    ctx.strokeStyle = '#f00';
    ctx.lineWidth = 3;
    ctx.stroke();
    ctx.restore();
  });
  // Draw player (LLM core)
  ctx.beginPath();
  ctx.arc(player.x, player.y, player.r, 0, Math.PI*2);
  const grad = ctx.createRadialGradient(player.x, player.y, 0, player.x, player.y, player.r);
  grad.addColorStop(0, '#0ff');
  grad.addColorStop(1, '#008');
  ctx.fillStyle = grad;
  ctx.fill();
  ctx.strokeStyle = '#0ff';
  ctx.lineWidth = 2;
  ctx.stroke();
  // Game over overlay
  if(!running) {
    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    ctx.fillRect(0,0,W,H);
    ctx.fillStyle = '#fff';
    ctx.font = '36px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', W/2, H/2 - 20);
    ctx.font = '20px monospace';
    ctx.fillText('Score: ' + score, W/2, H/2 + 20);
    ctx.fillText('Press R to restart', W/2, H/2 + 50);
  }
}

function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}

init();
loop();
