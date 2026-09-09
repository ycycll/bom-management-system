<template>
  <aside_navigation>
    <div class="tool-hub">
      <div class="hub-header">
        <h2>🧰 工具浮窗</h2>
        <p>前两个工具为占位测试的demo</p>
      </div>

      <!-- 卡片阵列：加工具就往上加对象 -->
      <div class="card-grid">
        <div
          class="glass-card"
          v-for="t in tools"
          :key="t.id"
          @mousemove="onMove"
          @mouseleave="onLeave"
          @mousedown="onDown"
          @mouseup="onUp"
          @click="openTool(t.id)"
        >
          <div class="card-glare"></div>
          <div class="card-icon">{{ t.icon }}</div>
          <div class="card-name">{{ t.name }}</div>
          <div class="card-desc">{{ t.desc }}</div>
        </div>
      </div>
    </div>
  </aside_navigation>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import aside_navigation from '../component/navigation.vue';

const router = useRouter();

const tools = ref([
  { id: 'calculator', icon: '🧮', name: '计算器', desc: '加减乘除、百分比' },
  { id: 'notepad', icon: '📝', name: '记事本', desc: '随手记，自动保存本地' }
]);

const MAX = 14; // 最大倾斜角度

// 鼠标在哪个角，哪个角就“压进屏幕”，对角翘起
const calc = (el, clientX, clientY) => {
  const rect = el.getBoundingClientRect();
  const px = (clientX - rect.left) / rect.width;  // 0=左 1=右
  const py = (clientY - rect.top) / rect.height;  // 0=上 1=下
  const rx = (0.5 - py) * 2 * MAX;  // 越靠上 → 顶端后仰(沉)
  const ry = (px - 0.5) * 2 * MAX;  // 越靠左 → 左端后仰(沉)  ← 关键：符号修正
  return { rx, ry };
};

const onMove = (e) => {
  const el = e.currentTarget;
  const { rx, ry } = calc(el, e.clientX, e.clientY);
  el.style.setProperty('--rx', rx.toFixed(1) + 'deg');
  el.style.setProperty('--ry', ry.toFixed(1) + 'deg');
  el.style.setProperty('--tz', '0px');
  // 高光跟随鼠标，增强立体感
  const rect = el.getBoundingClientRect();
  const px = (clientX - rect.left) / rect.width;
  const py = (clientY - rect.top) / rect.height;
  const glare = el.querySelector('.card-glare');
  if (glare) {
    glare.style.background =
      `radial-gradient(circle at ${px * 100}% ${py * 100}%, rgba(255,255,255,.45), transparent 55%)`;
  }
};

const onLeave = (e) => {
  const el = e.currentTarget;
  el.style.transition = 'transform .4s cubic-bezier(.2,.8,.3,1.2), box-shadow .4s';
  el.style.setProperty('--rx', '0deg');
  el.style.setProperty('--ry', '0deg');
  el.style.setProperty('--tz', '0px');
  const glare = el.querySelector('.card-glare');
  if (glare) glare.style.opacity = '0';
};

const onDown = (e) => {
  const el = e.currentTarget;
  const { rx, ry } = calc(el, e.clientX, e.clientY);
  el.style.transition = 'transform .08s ease-out, box-shadow .08s ease-out';
  el.style.setProperty('--rx', rx.toFixed(1) + 'deg');
  el.style.setProperty('--ry', ry.toFixed(1) + 'deg');
  el.style.setProperty('--tz', '-16px');   // 整体往里压 16px = 真按下
  el.style.boxShadow = '0 4px 14px rgba(31,38,135,.28)';
};

const onUp = (e) => {
  const el = e.currentTarget;
  const { rx, ry } = calc(el, e.clientX, e.clientY);
  el.style.transition = 'transform .25s cubic-bezier(.2,.8,.3,1.2), box-shadow .25s';
  el.style.setProperty('--rx', rx.toFixed(1) + 'deg');
  el.style.setProperty('--ry', ry.toFixed(1) + 'deg');
  el.style.setProperty('--tz', '0px');     // 弹回
  el.style.boxShadow = '';
};

const openTool = (id) => router.push(`/tool/${id}`);
</script>

<style scoped>
.tool-hub {
  height: 100%;
  padding: 24px 32px;
  box-sizing: border-box;
  overflow: auto;
}
.hub-header h2 { margin: 0 0 4px 0; color: #303133; }
.hub-header p { margin: 0 0 28px 0; color: #909399; font-size: 13px; }

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 28px;
  padding: 8px 4px;
}

.glass-card {
  position: relative;
  height: 172px;
  padding: 28px 24px;
  border-radius: 18px;
  box-sizing: border-box;
  cursor: pointer;
  background: linear-gradient(135deg, rgba(255,255,255,0.62), rgba(255,255,255,0.18));
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255,255,255,0.55);
  box-shadow: 0 8px 32px rgba(31,38,135,0.12);
  transform-style: preserve-3d;
  transform:
    perspective(900px)
    rotateX(var(--rx, 0deg))
    rotateY(var(--ry, 0deg))
    translateZ(var(--tz, 0px));
  transition: transform 0.18s ease-out, box-shadow 0.18s ease-out;
  will-change: transform;
}
.glass-card:hover {
  box-shadow: 0 16px 44px rgba(31,38,135,0.22);
}

/* 内容压在玻璃层上面 */
.card-icon, .card-name, .card-desc { position: relative; z-index: 1; }
.card-glare {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.18s ease-out;
  mix-blend-mode: overlay;
  z-index: 0;
}

.card-icon { font-size: 44px; line-height: 1; margin-bottom: 16px; }
.card-name { font-size: 20px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.card-desc { font-size: 13px; color: #909399; }
</style>
