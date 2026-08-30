<template>
  <aside_navigation>
    <div style="padding: 20px">
      <h2 style="margin: 0 0 15px">归档查询</h2>

      <!-- 筛选栏 -->
      <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; align-items: center">
        <el-select v-model="filters.flowNo" filterable clearable placeholder="选择流程号"
                   style="width: 180px" @change="search">
          <el-option v-for="i in flowOptions" :key="i" :label="i" :value="i" />
        </el-select>
        <el-input v-model="filters.workNo" placeholder="按工作令号搜索" clearable
                  style="width: 200px" @keyup.enter="search" @clear="search" />
        <el-input v-model="filters.keyword" placeholder="流程号/备注关键字" clearable
                  style="width: 180px" @keyup.enter="search" @clear="search" />
        <el-date-picker v-model="filters.dateRange" type="daterange" value-format="YYYY-MM-DD"
                        range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期"
                        style="width: 260px" @change="search" />
        <el-button type="primary" @click="search">查询</el-button>
        <el-button @click="reset">重置</el-button>
        <el-button type="success" :loading="exporting" @click="exportAll">导出全部（按当前筛选）</el-button>
      </div>

      <!-- 展示模式 -->
      <el-radio-group v-model="mode" style="margin-bottom: 12px" @change="handleModeChange">
        <el-radio-button value="record">按归档记录</el-radio-button>
        <el-radio-button value="flat">按时间铺开明细</el-radio-button>
      </el-radio-group>

      <!-- 模式一：按归档记录，行展开看明细 -->
      <template v-if="mode === 'record'">
        <el-table :data="records" border v-loading="loading">
          <el-table-column type="expand">
            <template #default="{ row }">
              <div style="padding: 10px 20px">
                <el-button size="small" type="success" style="margin-bottom: 8px"
                           @click="exportOne(row)">导出该归档明细</el-button>
                <el-table :data="row.items" border size="small" max-height="400">
                  <el-table-column v-for="col in detailColumns" :key="col.prop"
                                   :prop="col.prop" :label="col.label" :min-width="col.width"
                                   show-overflow-tooltip />
                </el-table>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="flow_no" label="流程号" width="160" />
          <el-table-column prop="remark" label="备注" show-overflow-tooltip />
          <el-table-column prop="item_count" label="明细条数" width="90" />
          <el-table-column prop="created_at" label="创建时间" width="170" />
          <el-table-column prop="updated_at" label="更新时间" width="170" />
        </el-table>
        <el-pagination background layout="total, prev, pager, next" style="margin-top: 12px"
                       :total="total" v-model:current-page="page" :page-size="pageSize"
                       @current-change="load" />
      </template>

      <!-- 模式二：按时间铺开，一行一个工作令号 -->
      <template v-else>
        <el-table :data="pagedFlatRows" border v-loading="flatLoading" max-height="620">
          <el-table-column prop="archive_time" label="归档时间" width="170" fixed />
          <el-table-column prop="flow_no" label="流程号" width="150" fixed />
          <el-table-column prop="remark" label="备注" width="130" show-overflow-tooltip />
          <el-table-column v-for="col in detailColumns" :key="col.prop"
                           :prop="col.prop" :label="col.label" :min-width="col.width"
                           show-overflow-tooltip />
        </el-table>
        <el-pagination background layout="total, prev, pager, next" style="margin-top: 12px"
                       :total="flatTotal" v-model:current-page="flatPage" :page-size="flatPageSize" />
      </template>
    </div>
  </aside_navigation>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'
import aside_navigation from '../component/navigation.vue'

// TPItem 明细字段的表头配置（和 model.py 的 TPItem 对齐）
const detailColumns = [
  { prop: 'workNo', label: '工作令号', width: 140 },
  { prop: 'materialNo', label: '物料号码', width: 140 },
  { prop: 'materialDesc', label: '物料长文本描述', width: 260 },
  { prop: 'techPreparation', label: '技术准备', width: 260 },
  { prop: 'productType', label: '产品型号', width: 120 },
  { prop: 'power', label: '功率', width: 80 },
  { prop: 'volt', label: '电压', width: 80 },
  { prop: 'freq', label: '频率', width: 70 },
  { prop: 'mountingType', label: '安装方式', width: 100 },
  { prop: 'insulationClass', label: '绝缘等级', width: 90 },
  { prop: 'protectionClass', label: '防护等级', width: 100 },
  { prop: 'leadWireMethod', label: '出线方式', width: 100 },
  { prop: 'environmentalConditions', label: '环境条件', width: 140 },
  { prop: 'coolingMethod', label: '冷却方式', width: 90 },
  { prop: 'lineItemNotes', label: '行项目备注', width: 140 },
  { prop: 'explosionProofClass', label: '防爆等级', width: 130 },
  { prop: 'ambientTemperature', label: '环境温度', width: 100 },
  { prop: 'junctionBoxPosition', label: '主接线盒位置及方向', width: 160 },
  { prop: 'rotationDirection', label: '旋转方向', width: 90 },
  { prop: 'bearingBrand', label: '轴承品牌', width: 100 },
  { prop: 'altitude', label: '海拔高度', width: 90 },
  { prop: 'heater', label: '加热器', width: 80 },
  { prop: 'statorTempSensor', label: '定子测温', width: 100 },
  { prop: 'bearingTempSensor', label: '轴承测温', width: 100 },
]

const flowOptions = ref([])
const filters = ref({ flowNo: '', workNo: '', keyword: '', dateRange: null })

const mode = ref('record')
const loading = ref(false)
const records = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const flatRows = ref([])
const flatLoading = ref(false)
const flatPage = ref(1)
const flatPageSize = ref(50)
const flatTotal = computed(() => flatRows.value.length)
const pagedFlatRows = computed(() =>
  flatRows.value.slice((flatPage.value - 1) * flatPageSize.value, flatPage.value * flatPageSize.value))

const exporting = ref(false)

function buildParams() {
  const [start, end] = filters.value.dateRange || []
  return {
    flow_no: filters.value.flowNo || '',
    work_no: filters.value.workNo || '',
    keyword: filters.value.keyword || '',
    start_date: start || '',
    end_date: end || '',
  }
}

function loadFlows() {
  axios.get('/api/archive_query/flows').then(resp => {
    if (resp.data.code === 200) flowOptions.value = resp.data.data
  })
}

function load() {
  loading.value = true
  axios.get('/api/archive_query/list', {
    params: { ...buildParams(), page: page.value, page_size: pageSize.value },
  }).then(resp => {
    if (resp.data.code === 200) {
      records.value = resp.data.data
      total.value = resp.data.total
    }
  }).finally(() => { loading.value = false })
}

function loadFlat() {
  flatLoading.value = true
  axios.get('/api/archive_query/flatten', { params: buildParams() }).then(resp => {
    if (resp.data.code === 200) flatRows.value = resp.data.data
  }).finally(() => { flatLoading.value = false })
}

function search() {
  if (mode.value === 'record') { page.value = 1; load() }
  else { flatPage.value = 1; loadFlat() }
}

function handleModeChange() {
  if (mode.value === 'flat' && flatRows.value.length === 0) loadFlat()
}

function reset() {
  filters.value = { flowNo: '', workNo: '', keyword: '', dateRange: null }
  flatRows.value = []
  search()
}

// rows: 铺平后的行；exportOne 时传 [{...item, archive_time, flow_no, remark}]
function exportRows(rows, filename) {
  if (!rows || rows.length === 0) { ElMessage.warning('没有可导出的数据'); return }
  const mapped = rows.map(r => {
    const o = { '归档时间': r.archive_time || '', '流程号': r.flow_no || '', '备注': r.remark || '' }
    detailColumns.forEach(c => { o[c.label] = r[c.prop] ?? '' })
    return o
  })
  const ws = XLSX.utils.json_to_sheet(mapped)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '归档明细')
  XLSX.writeFile(wb, filename)
  ElMessage.success('导出成功')
}

function exportOne(row) {
  const rows = row.items.map(it => ({ ...it, archive_time: row.created_at, flow_no: row.flow_no, remark: row.remark }))
  exportRows(rows, `归档明细_${row.flow_no}_${new Date().getTime()}.xlsx`)
}

function exportAll() {
  exporting.value = true
  axios.get('/api/archive_query/flatten', { params: buildParams() }).then(resp => {
    if (resp.data.code === 200) exportRows(resp.data.data, `归档明细_全量_${new Date().getTime()}.xlsx`)
  }).finally(() => { exporting.value = false })
}

onMounted(() => {
  loadFlows()
  load()
})
</script>