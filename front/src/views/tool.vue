<template>
  <aside_navigation>
    <div class="tool-hub">
      <div class="hub-header">
        <h2>🧰 工具浮窗</h2>
        <p>鼠标悬停卡片有重力效果，点击进入工具</p>
      </div>

      <!-- 卡片阵列：加工具就往上加对象 -->
      <div class="card-grid">
        <div
          class="glass-card"
          v-for="t in tools"
          :key="t.id"
          @mousemove="onMove"
          @mouseleave="onLeave"
          @click="openTool(t.id)"
        >
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

// 鼠标所在的那个角被"按下去"，对角"翘起来"
const onMove = (e) => {
  const el = e.currentTarget;
  const rect = el.getBoundingClientRect();
  const px = (e.clientX - rect.left) / rect.width;  // 0=左边缘 1=右边缘
  const py = (e.clientY - rect.top) / rect.height;  // 0=上边缘 1=下边缘
  const max = 14;                                   // 最大倾斜角度
  // 靠近上边/左边 => 正角度 => 该方向向屏幕里塌
  el.style.setProperty('--rx', ((0.5 - py) * 2 * max).toFixed(1) + 'deg');
  el.style.setProperty('--ry', ((0.5 - px) * 2 * max).toFixed(1) + 'deg');
};

const onLeave = (e) => {
  e.currentTarget.style.setProperty('--rx', '0deg');
  e.currentTarget.style.setProperty('--ry', '0deg');
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
  height: 172px;
  padding: 28px 24px;
  border-radius: 18px;
  box-sizing: border-box;
  cursor: pointer;
  /* 玻璃透明拟态 */
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.62), rgba(255, 255, 255, 0.18));
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.55);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.12);
  /* 重力倾斜：rx/ry 由 JS 动态写入 */
  transform: perspective(900px) rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg));
  transition: transform 0.35s cubic-bezier(0.2, 0.6, 0.3, 1), box-shadow 0.35s;
  will-change: transform;
}
.glass-card:hover {
  box-shadow: 0 16px 44px rgba(31, 38, 135, 0.22);
}

.card-icon { font-size: 44px; line-height: 1; margin-bottom: 16px; }
.card-name { font-size: 20px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.card-desc { font-size: 13px; color: #909399; }
</style>