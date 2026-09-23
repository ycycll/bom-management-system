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

        <!-- ========== 轴承库 ========== -->
        <div v-else-if="toolId === 'bearing'" class="glass-panel bearing-panel">
          <h3 style="margin:0 0 14px 0">⚙️ 轴承库查询</h3>

          <div class="bearing-filters">
            <el-input v-model="bearingKeyword" placeholder="搜索型号(如6205)或机座号" clearable style="width: 200px" @keyup.enter="bearingPage = 1" />
            <el-select v-model="bearingSeries" placeholder="全部系列" clearable style="width: 140px" @change="bearingPage = 1">
              <el-option v-for="s in bearingSeriesList" :key="s" :label="s" :value="s" />
            </el-select>
            <el-input-number v-model="bearingDMin" :min="0" :controls="false" placeholder="内径≥" style="width:100px" />
            <span style="color:#909399">~</span>
            <el-input-number v-model="bearingDMax" :min="0" :controls="false" placeholder="内径≤" style="width:100px" />
            <el-button type="primary" @click="bearingPage = 1">查询</el-button>
            <el-button @click="resetBearingFilter">重置</el-button>
            <el-tag type="info" effect="plain">共 {{ filteredBearings.length }} 条</el-tag>
          </div>

          <el-table :data="pagedBearings" border stripe size="small" style="margin-top:14px" height="calc(100vh - 340px)">
            <el-table-column prop="model" label="型号" width="90" fixed />
            <el-table-column prop="series" label="系列" width="80" />
            <el-table-column prop="bearing_type" label="类型" width="130" />
            <el-table-column prop="d" label="内径 d(mm)" width="100" align="right" />
            <el-table-column prop="D" label="外径 D(mm)" width="100" align="right" />
            <el-table-column prop="B" label="宽度 B(mm)" width="100" align="right" />
            <el-table-column prop="dynamic_load" label="动载(N)" width="110" align="right">
              <template #default="{row}">{{ row.dynamic_load ? row.dynamic_load.toLocaleString() : '' }}</template>
            </el-table-column>
            <el-table-column prop="static_load" label="静载(N)" width="110" align="right">
              <template #default="{row}">{{ row.static_load ? row.static_load.toLocaleString() : '' }}</template>
            </el-table-column>
            <el-table-column prop="limit_speed" label="极限转速(r/min)" width="130" align="right" />
            <el-table-column prop="weight" label="重量(kg)" width="90" align="right">
              <template #default="{row}">{{ row.weight ? row.weight.toFixed(3) : '' }}</template>
            </el-table-column>
            <el-table-column prop="frame_no" label="对应机座号" width="130" />
            <el-table-column prop="position" label="安装位置" width="100" />
            <el-table-column prop="note" label="备注" min-width="160" />
          </el-table>

          <el-pagination
            style="margin-top: 12px; justify-content: flex-end"
            background
            layout="total, prev, pager, next"
            :total="filteredBearings.length"
            v-model:current-page="bearingPage"
            v-model:page-size="bearingPageSize"
          />
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
import { bearingData, bearingSeriesList } from './data/bearing-data.js';

const route = useRoute();
const router = useRouter();

const toolId = route.params.toolId;

const toolNames = { calculator: '计算器', notepad: '记事本', bearing: '轴承库' };
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

/* ---------- 轴承库 ---------- */
const bearingKeyword = ref('');
const bearingSeries = ref('');
const bearingDMin = ref(null);
const bearingDMax = ref(null);
const bearingPage = ref(1);
const bearingPageSize = ref(20);

const filteredBearings = computed(() => {
  return bearingData.filter(b => {
    if (bearingKeyword.value) {
      const kw = bearingKeyword.value.toLowerCase();
      const hit = b.model.toLowerCase().includes(kw)
        || (b.frame_no && b.frame_no.toLowerCase().includes(kw))
        || (b.note && b.note.toLowerCase().includes(kw));
      if (!hit) return false;
    }
    if (bearingSeries.value && b.series !== bearingSeries.value) return false;
    if (bearingDMin.value !== null && b.d < bearingDMin.value) return false;
    if (bearingDMax.value !== null && b.d > bearingDMax.value) return false;
    return true;
  });
});

const pagedBearings = computed(() => {
  const start = (bearingPage.value - 1) * bearingPageSize.value;
  return filteredBearings.value.slice(start, start + bearingPageSize.value);
});

const resetBearingFilter = () => {
  bearingKeyword.value = '';
  bearingSeries.value = '';
  bearingDMin.value = null;
  bearingDMax.value = null;
  bearingPage.value = 1;
};
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

/* 轴承库 */
.bearing-panel { max-width: none; width: 100%; }
.bearing-filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}
</style>
