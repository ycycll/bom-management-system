<template>
  <aside_navigation>
    <div class="tool-detail">
      <!-- 面包屑：第一级=工具浮窗主页，第二级=当前工具 -->
      <el-breadcrumb separator="/" class="crumb">
        <el-breadcrumb-item :to="{ path: '/home' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/tool' }">工具浮窗</el-breadcrumb-item>
        <el-breadcrumb-item>{{ toolName }}</el-breadcrumb-item>
      </el-breadcrumb>

      <div class="detail-body">
        <!-- ========== 计算器 ========== -->
        <div v-if="toolId === 'calculator'" class="glass-panel">
          <div class="calc-display">{{ calcDisplay }}</div>
          <div class="calc-buttons">
            <button class="calc-btn fn" @click="calcClear">C</button>
            <button class="calc-btn fn" @click="calcBackspace">←</button>
            <button class="calc-btn fn" @click="calcPressOp('%')">%</button>
            <button class="calc-btn fn" @click="calcPressOp('/')">÷</button>

            <button class="calc-btn" @click="calcPressNum('7')">7</button>
            <button class="calc-btn" @click="calcPressNum('8')">8</button>
            <button class="calc-btn" @click="calcPressNum('9')">9</button>
            <button class="calc-btn fn" @click="calcPressOp('*')">×</button>

            <button class="calc-btn" @click="calcPressNum('4')">4</button>
            <button class="calc-btn" @click="calcPressNum('5')">5</button>
            <button class="calc-btn" @click="calcPressNum('6')">6</button>
            <button class="calc-btn fn" @click="calcPressOp('-')">−</button>

            <button class="calc-btn" @click="calcPressNum('1')">1</button>
            <button class="calc-btn" @click="calcPressNum('2')">2</button>
            <button class="calc-btn" @click="calcPressNum('3')">3</button>
            <button class="calc-btn fn" @click="calcPressOp('+')">+</button>

            <button class="calc-btn zero" @click="calcPressNum('0')">0</button>
            <button class="calc-btn" @click="calcPressNum('.')">.</button>
            <button class="calc-btn eq" @click="calcEquals">=</button>
          </div>
        </div>

        <!-- ========== 记事本 ========== -->
        <div v-else-if="toolId === 'notepad'" class="glass-panel note-panel">
          <h3>📝 记事本</h3>
          <textarea
            class="note-input"
            v-model="noteContent"
            placeholder="在此输入内容..."
            rows="12"
          ></textarea>
          <div class="note-actions">
            <el-button type="primary" @click="saveNote">保存</el-button>
            <el-button @click="clearNote">清空</el-button>
          </div>
        </div>

        <!-- 未知工具兜底 -->
        <el-empty v-else description="没有这个工具，返回工具浮窗" />
      </div>
    </div>
  </aside_navigation>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import aside_navigation from '../component/navigation.vue';

const route = useRoute();
const router = useRouter();

const toolId = route.params.toolId;

const toolNames = { calculator: '计算器', notepad: '记事本' };
const toolName = computed(() => toolNames[toolId] || '未知工具');

/* ---------- 计算器 ---------- */
const calcDisplay = ref('0');
const calcPrev = ref(null);      // 上一个参与运算的数
const calcOp = ref(null);        // 当前运算符 (注意：不要和上面的 calcOp 函数重名即可)
const calcResetNext = ref(false);

const calcPressNum = (num) => {
  if (calcResetNext.value) {
    calcDisplay.value = num;
    calcResetNext.value = false;
  } else {
    calcDisplay.value = calcDisplay.value === '0' ? num : calcDisplay.value + num;
  }
};

const calcPressOp = (op) => {
  if (calcPrev.value === null) {
    calcPrev.value = parseFloat(calcDisplay.value);
  } else if (!calcResetNext.value) {
    calcEquals();
  }
  calcOp.value = op;
  calcResetNext.value = true;
};

const calcEquals = () => {
  if (calcOp.value !== null && calcPrev.value !== null && !calcResetNext.value) {
    const cur = parseFloat(calcDisplay.value);
    let result;
    switch (calcOp.value) {
      case '+': result = calcPrev.value + cur; break;
      case '-': result = calcPrev.value - cur; break;
      case '*': result = calcPrev.value * cur; break;
      case '/': result = calcPrev.value / cur; break;
      case '%': result = calcPrev.value % cur; break;
      default: return;
    }
    calcDisplay.value = String(result);
    calcPrev.value = result;
    calcResetNext.value = true;
  }
};

const calcClear = () => {
  calcDisplay.value = '0';
  calcPrev.value = null;
  calcOp.value = null;
  calcResetNext.value = false;
};

const calcBackspace = () => {
  if (!calcResetNext.value && calcDisplay.value.length > 1) {
    calcDisplay.value = calcDisplay.value.slice(0, -1);
  } else {
    calcDisplay.value = '0';
  }
};

/* ---------- 记事本 ---------- */
const noteContent = ref('');

const saveNote = () => {
  if (noteContent.value.trim()) {
    localStorage.setItem('toolNote', noteContent.value);
    ElMessage.success('笔记已保存');
  } else {
    ElMessage.warning('内容为空，无需保存');
  }
};

const clearNote = () => {
  noteContent.value = '';
  ElMessage.info('已清空');
};

onMounted(() => {
  noteContent.value = localStorage.getItem('toolNote') || '';
});
</script>

<style scoped>
.tool-detail {
  height: 100%;
  padding: 20px 32px;
  box-sizing: border-box;
  overflow: auto;
}
.crumb { margin-bottom: 22px; }

.glass-panel {
  max-width: 420px;
  border-radius: 18px;
  padding: 20px;
  box-sizing: border-box;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.65), rgba(255, 255, 255, 0.25));
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.12);
}

/* 计算器 */
.calc-display {
  background: rgba(255, 255, 255, 0.75);
  border-radius: 10px;
  padding: 16px 14px;
  text-align: right;
  font-size: 28px;
  min-height: 48px;
  word-break: break-all;
  margin-bottom: 14px;
  border: 1px solid rgba(255, 255, 255, 0.5);
}
.calc-buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 9px;
}
.calc-btn {
  padding: 14px 0;
  font-size: 17px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.55);
  color: #303133;
  cursor: pointer;
  transition: all 0.15s;
}
.calc-btn:hover { background: rgba(255, 255, 255, 0.9); }
.calc-btn:active { transform: scale(0.94); }
.calc-btn.fn { color: #e6a23c; }
.calc-btn.eq { background: #409eff; color: #fff; border-color: #409eff; }
.calc-btn.eq:hover { background: #66b1ff; }
.calc-btn.zero { grid-column: span 2; }

/* 记事本 */
.note-panel h3 { margin: 0 0 12px 0; color: #303133; }
.note-input {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.75);
  padding: 12px;
  font-size: 14px;
  resize: vertical;
  box-sizing: border-box;
}
.note-input:focus { outline: none; border-color: #409eff; }
.note-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
