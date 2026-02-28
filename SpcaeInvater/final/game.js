const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// 動態設置畫布寬高
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let gameRunning = false; // 控制遊戲是否開始

let player = {
  x: canvas.width / 2 - 25,
  y: canvas.height - 50,
  width: 50,
  height: 20,
  color: 'white',
  speed: 7,
  lives: 10,
  movingLeft: false,
  movingRight: false
};

let bullets = [];
let enemyBullets = [];
let enemies = [];
let barriers = [];
let isShooting = false;
let shootCooldown = 0;
let enemyMoveDirection = 1; // 1 表示向右，-1 表示向左

// 玩家子彈
class Bullet {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.width = 5;
    this.height = 10;
    this.speed = 7;
  }

  update() {
    this.y -= this.speed;
  }

  draw() {
    ctx.fillStyle = 'yellow';
    ctx.fillRect(this.x, this.y, this.width, this.height);
  }
}

// 怪獸
class Enemy {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.width = 40;
    this.height = 30;
    this.speed = 2;
    this.cooldown = Math.random() * 200;
  }

  update() {
    this.x += this.speed * enemyMoveDirection;
  }

  draw() {
    ctx.fillStyle = 'green';
    ctx.fillRect(this.x, this.y, this.width, this.height);
  }

  shoot() {
    if (this.cooldown <= 0) {
      enemyBullets.push(new Bullet(this.x + this.width / 2, this.y + this.height));
      this.cooldown = Math.random() * 200 + 100;
    } else {
      this.cooldown--;
    }
  }
}

// 障礙物
class Barrier {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.width = 100;
    this.height = 20;
    this.pixels = Array(this.width * this.height).fill(true); // 每個像素是否存在
  }

  draw() {
    for (let i = 0; i < this.pixels.length; i++) {
      if (this.pixels[i]) {
        let px = this.x + (i % this.width);
        let py = this.y + Math.floor(i / this.width);
        ctx.fillStyle = 'gray';
        ctx.fillRect(px, py, 1, 1);
      }
    }
  }

  takeDamage(bulletX, bulletY) {
    // 將子彈碰撞處的幾個像素移除
    let localX = Math.floor(bulletX - this.x);
    let localY = Math.floor(bulletY - this.y);

    for (let i = -2; i <= 2; i++) {
      for (let j = -2; j <= 2; j++) {
        let pixelIndex = (localY + j) * this.width + (localX + i);
        if (pixelIndex >= 0 && pixelIndex < this.pixels.length) {
          this.pixels[pixelIndex] = false; // 模擬像素破壞
        }
      }
    }
  }
}

// 初始化怪獸
function createEnemies(rows, cols) {
  const enemyPadding = 10;
  const enemyOffsetX = 100;
  const enemyOffsetY = 50;
  const totalWidth = cols * (40 + enemyPadding) - enemyPadding;

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const x = (canvas.width - totalWidth) / 2 + col * (40 + enemyPadding) + enemyOffsetX;
      const y = row * (30 + enemyPadding) + enemyOffsetY;
      enemies.push(new Enemy(x, y));
    }
  }
}

// 初始化障礙物
function createBarriers() {
  const barrierWidth = 100;
  const gap = (canvas.width - 3 * barrierWidth) / 4;
  barriers.push(new Barrier(gap, canvas.height - 150));
  barriers.push(new Barrier(2 * gap + barrierWidth, canvas.height - 150));
  barriers.push(new Barrier(3 * gap + 2 * barrierWidth, canvas.height - 150));
}

// 處理輸入
document.addEventListener('keydown', function (e) {
  if (e.key === 'ArrowLeft') player.movingLeft = true;
  if (e.key === 'ArrowRight') player.movingRight = true;
  if (e.key === 'z' && shootCooldown <= 0) {
    isShooting = true;
  }
});

document.addEventListener('keyup', function (e) {
  if (e.key === 'ArrowLeft') player.movingLeft = false;
  if (e.key === 'ArrowRight') player.movingRight = false;
  if (e.key === 'z') isShooting = false;
});

// 更新遊戲
function update() {
  if (!gameRunning) return;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 更新玩家
  if (player.lives <= 0) {
    alert('Game Over! You Lose.');
    resetGame();
    return;
  }

  if (player.movingLeft && player.x > 0) player.x -= player.speed;
  if (player.movingRight && player.x < canvas.width - player.width) player.x += player.speed;

  // 繪製玩家
  ctx.fillStyle = player.color;
  ctx.fillRect(player.x, player.y, player.width, player.height);

  // 發射子彈
  if (isShooting && shootCooldown <= 0) {
    bullets.push(new Bullet(player.x + player.width / 2, player.y));
    shootCooldown = 15; // 子彈冷卻時間
  }

  // 更新玩家子彈
  bullets.forEach((bullet, index) => {
    bullet.update();
    bullet.draw();

    // 檢查子彈是否超出畫布
    if (bullet.y < 0) bullets.splice(index, 1);
  });

  // 更新怪獸
  let reachedEdge = false;
  enemies.forEach((enemy, index) => {
    enemy.update();
    enemy.draw();
    enemy.shoot();

    // 檢查是否到達螢幕邊緣
    if (enemy.x + enemy.width >= canvas.width || enemy.x <= 0) {
      reachedEdge = true;
    }

    // 檢查玩家子彈命中怪獸
    bullets.forEach((bullet, bulletIndex) => {
      if (
        bullet.x > enemy.x &&
        bullet.x < enemy.x + enemy.width &&
        bullet.y > enemy.y &&
        bullet.y < enemy.y + enemy.height
      ) {
        enemies.splice(index, 1);
        bullets.splice(bulletIndex, 1);
      }
    });
  });

  // 怪獸到達螢幕邊緣時改變方向並向下移動
  if (reachedEdge) {
    enemyMoveDirection *= -1;
    enemies.forEach((enemy) => {
      enemy.y += 10; // 向下移動
    });
  }

  // 檢查玩家是否勝利
  if (enemies.length === 0) {
    alert('Congratulations! You Win!');
    resetGame();
    return;
  }

  // 更新障礙物
  barriers.forEach((barrier) => {
    barrier.draw();

    // 檢查玩家子彈命中障礙物
    bullets.forEach((bullet, bulletIndex) => {
      if (bullet.x > barrier.x && bullet.x < barrier.x + barrier.width && bullet.y > barrier.y) {
        barrier.takeDamage(bullet.x, bullet.y);
        bullets.splice(bulletIndex, 1);
      }
    });

    // 檢查怪獸子彈命中障礙物
    enemyBullets.forEach((bullet, bulletIndex) => {
      if (bullet.x > barrier.x && bullet.x < barrier.x + barrier.width && bullet.y > barrier.y) {
        barrier.takeDamage(bullet.x, bullet.y);
        enemyBullets.splice(bulletIndex, 1);
      }
    });
  });

  // 更新怪獸子彈
  enemyBullets.forEach((bullet, index) => {
    bullet.y += bullet.speed;
    bullet.draw();

    // 檢查是否超出畫布
    if (bullet.y > canvas.height) enemyBullets.splice(index, 1);

    // 檢查怪獸子彈命中玩家
    if (
      bullet.x > player.x &&
      bullet.x < player.x + player.width &&
      bullet.y > player.y &&
      bullet.y < player.y + player.height
    ) {
      player.lives--;
      document.getElementById('lives').innerText = `Lives: ${player.lives}`;
      enemyBullets.splice(index, 1);
    }
  });

  // 子彈冷卻
  if (shootCooldown > 0) shootCooldown--;

  requestAnimationFrame(update);
}

// 重置遊戲
function resetGame() {
  player.lives = 10;
  enemies = [];
  bullets = [];
  enemyBullets = [];
  barriers = [];
  gameRunning = false;
  document.getElementById('menu').style.display = 'block';
}

// 主菜單
document.getElementById('startButton').addEventListener('click', function () {
  document.getElementById('menu').style.display = 'none';
  gameRunning = true;
  createEnemies(4, 8);
  createBarriers();
  update();
});

// 初始化主菜單
document.getElementById('menu').style.display = 'block';
