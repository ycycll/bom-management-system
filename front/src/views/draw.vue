<template>
  <aside_navigation>
    <div>
      <div style="text-align: center; font-size: 30px; margin-bottom: 20px">图纸查看</div>

      <!-- 搜索区域 -->
      <div style="width: 90%; margin: 0 auto 16px auto; display: flex; gap: 40px; align-items: center">
        <el-input
            v-model="searchForm.draw_name"
            placeholder="图号搜索"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
        />
        <el-input
            v-model="searchForm.remark"
            placeholder="备注搜索"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>

      <!-- 搜索结果列表 -->
      <div style="width: 90%; margin: 0 auto 12px auto">
        <el-table
            :data="tableData"
            border
            stripe
            highlight-current-row
            @row-click="handleRowClick"
            style="cursor: pointer"
        >
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="draw_name" label="图号" />
          <el-table-column prop="remark" label="备注" />
          <el-table-column label="操作" width="100">
            <template #default="scope">
              <el-button size="small" type="primary" @click.stop="handleView(scope.row)">
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-top: 10px">
          <el-pagination
              background
              layout="total, prev, pager, next"
              :total="total"
              v-model:current-page="pageNum"
              v-model:page-size="pageSize"
              @change="loadList"
          />
        </div>
      </div>

      <!-- 图纸预览区域 -->
      <div style="width: 90%; margin: 0 auto">
        <div v-if="!currentDrawId" style="
          height: 67vh; border: 2px dashed #d0d0d0; border-radius: 8px;
          display: flex; align-items: center; justify-content: center;
          color: #aaa; font-size: 18px; background: #fafafa;
        ">
          请点击表格行或【查看】按钮加载图纸
        </div>
        <iframe
            v-else
            :src="iframeSrc"
            style="width: 100%; height: 67vh; border: 1px solid #e0e0e0; border-radius: 8px;"
        />
      </div>
    </div>
  </aside_navigation>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import aside_navigation from '../component/navigation.vue'

// 搜索表单
const searchForm = ref({ draw_name: '', remark: '' })

// 列表数据
const tableData = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(2)

// 当前预览的图纸 ID
const currentDrawId = ref(null)

// iframe src：通过后端接口流式返回文件
const iframeSrc = computed(() => {
  if (!currentDrawId.value) return ''
  return `/api/draw/file/${currentDrawId.value}`
})

// 加载列表
const loadList = () => {
  axios.get('/api/draw/list', {
    params: {
      draw_name: searchForm.value.draw_name,
      remark: searchForm.value.remark,
      page_num: pageNum.value,
      page_size: pageSize.value,
    }
  }).then(resp => {
    if (resp.data.code === 200) {
      tableData.value = resp.data.data
      total.value = resp.data.total
    }
  })
}

// 查询
const handleSearch = () => {
  pageNum.value = 1
  loadList()
}


// 点击行 或 点击查看 → 加载 iframe
const handleView = (row) => {
  currentDrawId.value = row.id
  ElMessage.success(`加载图纸：${row.draw_name}`)
}

const handleRowClick = (row) => {
  handleView(row)
}

// 初始化加载
loadList()
</script>