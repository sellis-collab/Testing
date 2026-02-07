const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const carNameEl = document.getElementById("carName");
const skillEl = document.getElementById("skillValue");
const upgradeEl = document.getElementById("upgradeValue");
const nextUpgradeEl = document.getElementById("nextUpgrade");
const progressEl = document.getElementById("upgradeProgress");
const restartBtn = document.getElementById("restartBtn");

const carLevels = [
  { name: "Old Wagon", color: "#9b6b43" },
  { name: "Rusty Sedan", color: "#6f6e6c" },
  { name: "Reliable Hatch", color: "#2f7d93" },
  { name: "Sport Coupe", color: "#cb4c45" },
  { name: "Super Racer", color: "#7c4bd6" },
  { name: "Hyper Glide", color: "#1c9a6f" },
];

const state = {
  laneOffset: 0,
  targetOffset: 0,
  speedBoost: false,
  skill: 0,
  upgrades: 0,
  carLevel: 0,
  obstacles: [],
  frame: 0,
  running: true,
};

const input = {
  left: false,
  right: false,
  boost: false,
};

const road = {
  width: 260,
  stripeGap: 60,
  stripeHeight: 30,
};

const car = {
  x: canvas.width / 2,
  y: canvas.height - 90,
  width: 44,
  height: 70,
};

function resetGame() {
  state.laneOffset = 0;
  state.targetOffset = 0;
  state.speedBoost = false;
  state.skill = 0;
  state.upgrades = 0;
  state.carLevel = 0;
  state.obstacles = [];
  state.frame = 0;
  state.running = true;
  updateHud();
}

function updateHud() {
  const level = carLevels[state.carLevel];
  carNameEl.textContent = level.name;
  skillEl.textContent = Math.floor(state.skill);
  upgradeEl.textContent = state.upgrades;
  const nextLevel = carLevels[Math.min(state.carLevel + 1, carLevels.length - 1)];
  nextUpgradeEl.textContent = nextLevel.name;
  const progress = (state.skill % 100) / 100;
  progressEl.style.width = `${progress * 100}%`;
}

function spawnObstacle() {
  const laneX = canvas.width / 2 + (Math.random() * 0.6 - 0.3) * road.width;
  state.obstacles.push({ x: laneX, y: -30, size: 18 });
}

function handleInput() {
  if (input.left) {
    state.targetOffset = Math.max(state.targetOffset - 3, -road.width / 2 + 30);
  } else if (input.right) {
    state.targetOffset = Math.min(state.targetOffset + 3, road.width / 2 - 30);
  }
  state.speedBoost = input.boost;
  state.laneOffset += (state.targetOffset - state.laneOffset) * 0.1;
}

function updateSkill() {
  const smoothness = 1 - Math.min(Math.abs(state.targetOffset) / (road.width / 2), 1);
  const boostBonus = state.speedBoost ? 0.3 : 0;
  state.skill += 0.25 + smoothness * 0.45 + boostBonus;

  const newLevel = Math.min(Math.floor(state.skill / 100), carLevels.length - 1);
  if (newLevel !== state.carLevel) {
    state.carLevel = newLevel;
    state.upgrades = state.carLevel;
  }
}

function updateObstacles() {
  if (state.frame % 90 === 0) {
    spawnObstacle();
  }

  const speed = state.speedBoost ? 5.2 : 3.8;
  state.obstacles.forEach((obstacle) => {
    obstacle.y += speed;
  });

  state.obstacles = state.obstacles.filter((obstacle) => obstacle.y < canvas.height + 40);

  state.obstacles.forEach((obstacle) => {
    const dx = obstacle.x - (canvas.width / 2 + state.laneOffset);
    const dy = obstacle.y - car.y;
    if (Math.abs(dx) < car.width / 2 && Math.abs(dy) < car.height / 2) {
      state.skill = Math.max(state.skill - 20, 0);
      state.targetOffset += dx > 0 ? -30 : 30;
      obstacle.y = canvas.height + 50;
    }
  });
}

function drawRoad() {
  ctx.fillStyle = "#2c7a3d";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "#3a3f44";
  ctx.fillRect(
    canvas.width / 2 - road.width / 2,
    0,
    road.width,
    canvas.height
  );

  ctx.strokeStyle = "#f1f1f1";
  ctx.lineWidth = 4;
  ctx.setLineDash([road.stripeHeight, road.stripeGap]);
  ctx.lineDashOffset = -state.frame * 6;
  ctx.beginPath();
  ctx.moveTo(canvas.width / 2, 0);
  ctx.lineTo(canvas.width / 2, canvas.height);
  ctx.stroke();
  ctx.setLineDash([]);
}

function drawCar() {
  const level = carLevels[state.carLevel];
  ctx.save();
  ctx.translate(canvas.width / 2 + state.laneOffset, car.y);
  ctx.fillStyle = level.color;
  ctx.fillRect(-car.width / 2, -car.height / 2, car.width, car.height);

  ctx.fillStyle = "#1c1c1c";
  ctx.fillRect(-car.width / 2 + 6, -car.height / 2 + 12, car.width - 12, 18);

  ctx.fillStyle = "#ffd166";
  ctx.fillRect(-car.width / 2 + 8, car.height / 2 - 12, car.width - 16, 6);

  ctx.restore();
}

function drawObstacles() {
  ctx.fillStyle = "#ff914d";
  state.obstacles.forEach((obstacle) => {
    ctx.beginPath();
    ctx.moveTo(obstacle.x, obstacle.y - obstacle.size / 2);
    ctx.lineTo(obstacle.x - obstacle.size / 2, obstacle.y + obstacle.size / 2);
    ctx.lineTo(obstacle.x + obstacle.size / 2, obstacle.y + obstacle.size / 2);
    ctx.closePath();
    ctx.fill();
  });
}

function loop() {
  if (!state.running) return;
  state.frame += 1;
  handleInput();
  updateSkill();
  updateObstacles();
  updateHud();

  drawRoad();
  drawObstacles();
  drawCar();

  requestAnimationFrame(loop);
}

window.addEventListener("keydown", (event) => {
  if (["ArrowLeft", "a", "A"].includes(event.key)) {
    input.left = true;
  }
  if (["ArrowRight", "d", "D"].includes(event.key)) {
    input.right = true;
  }
  if (["ArrowUp", "w", "W"].includes(event.key)) {
    input.boost = true;
  }
});

window.addEventListener("keyup", (event) => {
  if (["ArrowLeft", "a", "A"].includes(event.key)) {
    input.left = false;
  }
  if (["ArrowRight", "d", "D"].includes(event.key)) {
    input.right = false;
  }
  if (["ArrowUp", "w", "W"].includes(event.key)) {
    input.boost = false;
  }
});

restartBtn.addEventListener("click", () => {
  resetGame();
  loop();
});

resetGame();
loop();
