const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

const scoreEl = document.getElementById('score');
const livesEl = document.getElementById('lives');
const bestEl = document.getElementById('best');

const leftBtn = document.getElementById('left');
const rightBtn = document.getElementById('right');
const restartBtn = document.getElementById('restart');

const W = canvas.width;
const H = canvas.height;
let score = 0;
let lives = 3;
let speed = 2.5;
let gameOver = false;
let tick = 0;

const bestKey = 'fruit-catcher-best';
let best = Number(localStorage.getItem(bestKey) || 0);
bestEl.textContent = best;

const player = { x: W / 2 - 45, y: H - 70, w: 90, h: 30, vx: 0 };
const drops = [];

function spawn() {
  const bomb = Math.random() < 0.2;
  drops.push({
    x: 25 + Math.random() * (W - 50),
    y: -30,
    r: 18,
    vy: speed + Math.random() * 2,
    bomb,
    emoji: bomb ? '💣' : (Math.random() < 0.5 ? '🍎' : '🍊')
  });
}

function reset() {
  score = 0;
  lives = 3;
  speed = 2.5;
  gameOver = false;
  tick = 0;
  drops.length = 0;
  player.x = W / 2 - player.w / 2;
  updateHud();
}

function updateHud() {
  scoreEl.textContent = score;
  livesEl.textContent = lives;
  bestEl.textContent = best;
}

function collide(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function update() {
  if (gameOver) return;
  tick += 1;
  if (tick % Math.max(16, 42 - Math.floor(score / 3)) === 0) spawn();
  speed = Math.min(8, 2.5 + score * 0.04);

  player.x += player.vx;
  player.x = Math.max(0, Math.min(W - player.w, player.x));

  for (let i = drops.length - 1; i >= 0; i--) {
    const d = drops[i];
    d.y += d.vy;

    const box = { x: d.x - d.r, y: d.y - d.r, w: d.r * 2, h: d.r * 2 };
    if (collide(player, box)) {
      if (d.bomb) lives -= 1;
      else score += 1;
      drops.splice(i, 1);
      if (lives <= 0) {
        gameOver = true;
        best = Math.max(best, score);
        localStorage.setItem(bestKey, String(best));
      }
      continue;
    }

    if (d.y > H + 30) {
      if (!d.bomb) lives -= 1;
      drops.splice(i, 1);
      if (lives <= 0) {
        gameOver = true;
        best = Math.max(best, score);
        localStorage.setItem(bestKey, String(best));
      }
    }
  }

  updateHud();
}

function draw() {
  ctx.clearRect(0, 0, W, H);

  for (let i = 0; i < 40; i++) {
    ctx.fillStyle = 'rgba(255,255,255,.05)';
    ctx.fillRect((i * 83 + tick * 0.7) % W, (i * 47) % H, 2, 2);
  }

  ctx.fillStyle = '#d49f4f';
  ctx.fillRect(player.x, player.y, player.w, player.h);
  ctx.fillStyle = '#b97f2d';
  ctx.fillRect(player.x + 5, player.y + 5, player.w - 10, player.h - 8);

  ctx.font = '28px Apple Color Emoji, Segoe UI Emoji, sans-serif';
  ctx.textAlign = 'center';
  for (const d of drops) {
    ctx.fillText(d.emoji, d.x, d.y + 10);
  }

  if (gameOver) {
    ctx.fillStyle = 'rgba(0,0,0,.45)';
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 46px -apple-system, sans-serif';
    ctx.fillText('Game Over', W / 2, H / 2 - 30);
    ctx.font = 'bold 24px -apple-system, sans-serif';
    ctx.fillText(`Score: ${score}`, W / 2, H / 2 + 10);
    ctx.fillText('Tap Restart', W / 2, H / 2 + 50);
  }
}

function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}

function setMove(dir, down) {
  const v = 8;
  if (down) player.vx = dir * v;
  else if (Math.sign(player.vx) === dir) player.vx = 0;
}

leftBtn.addEventListener('pointerdown', () => setMove(-1, true));
rightBtn.addEventListener('pointerdown', () => setMove(1, true));
leftBtn.addEventListener('pointerup', () => setMove(-1, false));
rightBtn.addEventListener('pointerup', () => setMove(1, false));
leftBtn.addEventListener('pointercancel', () => setMove(-1, false));
rightBtn.addEventListener('pointercancel', () => setMove(1, false));

restartBtn.addEventListener('click', reset);

let dragging = false;
canvas.addEventListener('pointerdown', (e) => {
  dragging = true;
  const rect = canvas.getBoundingClientRect();
  player.x = ((e.clientX - rect.left) / rect.width) * W - player.w / 2;
});
canvas.addEventListener('pointermove', (e) => {
  if (!dragging || gameOver) return;
  const rect = canvas.getBoundingClientRect();
  player.x = ((e.clientX - rect.left) / rect.width) * W - player.w / 2;
});
canvas.addEventListener('pointerup', () => (dragging = false));
canvas.addEventListener('pointercancel', () => (dragging = false));

window.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowLeft') setMove(-1, true);
  if (e.key === 'ArrowRight') setMove(1, true);
});
window.addEventListener('keyup', (e) => {
  if (e.key === 'ArrowLeft') setMove(-1, false);
  if (e.key === 'ArrowRight') setMove(1, false);
});

reset();
loop();
