<template>
  <aside_navigation>
    <div>
      <div style="text-align: center; font-size: 30px; margin-bottom: 30px">部件推荐后台</div>
      <div style="width: 90%; margin: 30px auto;">
        <!-- 搜索区域 -->
        <div style="margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 10px;">
          <el-input placeholder="机座号" v-model="data.const" clearable style="width: 150px" @keyup.enter="load" />
          <el-input placeholder="技术准备" v-model="data.technical_preparation" clearable style="width: 200px" @keyup.enter="load" />
          <el-input placeholder="部件料号" v-model="data.component_id" clearable style="width: 150px" @keyup.enter="load" />
          <el-input placeholder="部件描述" v-model="data.component_desc" clearable style="width: 200px" @keyup.enter="load" />
          <el-button type="primary" @click="load" style="margin-right: 10px">查询</el-button>
          <el-button type="success" @click="openAddDialog" :disabled="!isAdmin">新增</el-button>
        </div>

        <!-- 数据表格 -->
        <div style="margin-top: 10px">
          <el-table :data="data.tableData" style="width: 100%" border stripe>
            <el-table-column prop="const" label="机座号" width="120" />
            <el-table-column prop="technical_preparation" label="技术准备" width="250" />
            <el-table-column prop="component_id" label="部件料号" width="150" />
            <el-table-column prop="component_desc" label="部件描述" width="600" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button type="primary" size="small" @click="openEditDialog(scope.row)" :disabled="!isAdmin">编辑</el-button>
                <el-button type="danger" size="small" @click="handleDelete(scope.row)" :disabled="!isAdmin">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 分页 -->
        <div style="margin-top: 10px; text-align: right">
          <el-pagination 
            background 
            layout="total, prev, pager, next" 
            @change="load"
            :total="data.total"
            v-model:current-page="data.page_num" 
            v-model:page-size="data.page_size"
          />
        </div>
      </div>

      <!-- 新增/编辑弹窗 -->
      <el-dialog 
        :title="dialogType === 'add' ? '新增部件' : '编辑部件'" 
        v-model="dialogVisible" 
        width="500px"
      >
        <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
          <el-form-item label="机座号" prop="const">
            <el-input v-model="form.const" placeholder="如：WE-80" />
          </el-form-item>
          <el-form-item label="技术准备" prop="technical_preparation">
            <el-input v-model="form.technical_preparation" placeholder="如：IC411" />
          </el-form-item>
          <el-form-item label="部件料号" prop="component_id">
            <el-input v-model="form.component_id" placeholder="如：88610849-01A" />
          </el-form-item>
          <el-form-item label="部件描述" prop="component_desc">
            <el-input v-model="form.component_desc" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">{{ dialogType === 'add' ? '确定新增' : '确定更新' }}</el-button>
        </template>
      </el-dialog>
    </div>
  </aside_navigation>
</template>

<script setup>
import { ref, computed } from "vue";
import axios from "axios";
import { ElMessage, ElMessageBox } from "element-plus";

import aside_navigation from '../component/navigation.vue';

let data = ref({
  total: 0,
  tableData: [],
  page_num: 1,
  page_size: 10,
  const: null,
  technical_preparation: null,
  component_id: null,
  component_desc: null,
});

let dialogVisible = ref(false);
let dialogType = ref('add');
let formRef = ref();
let form = ref({
  const: '',
  technical_preparation: '',
  component_id: '',
  component_desc: '',
});

let originalData = ref(null);

const rules = {
  const: [{ required: true, message: '请输入机座号', trigger: 'blur' }],
  technical_preparation: [{ required: true, message: '请输入技术准备', trigger: 'blur' }],
  component_id: [{ required: true, message: '请输入部件料号', trigger: 'blur' }],
  component_desc: [{ required: true, message: '请输入部件描述', trigger: 'blur' }],
};

// 判断是否为管理员
let userRole = computed(() => localStorage.getItem('userRole'));
const isAdmin = computed(() => userRole.value === 'admin');

// 加载数据
let load = function () {
  axios.get('/api/component/list', {
    params: {
      page_num: data.value.page_num,
      page_size: data.value.page_size,
      const: data.value.const,
      technical_preparation: data.value.technical_preparation,
      component_id: data.value.component_id,
      component_desc: data.value.component_desc,
    }
  }).then(function (resp) {
    data.value.tableData = resp.data.json_resp;
    data.value.total = resp.data.total;
  }).catch(function (err) {
    ElMessage.error('加载失败：' + err.message);
  });
};

// 打开新增弹窗
let openAddDialog = function () {
  dialogType.value = 'add';
  form.value = {
    const: '',
    technical_preparation: '',
    component_id: '',
    component_desc: '',
  };
  dialogVisible.value = true;
};

// 打开编辑弹窗
let openEditDialog = function (row) {
  dialogType.value = 'edit';
  form.value = {
    const: row.const,
    technical_preparation: row.technical_preparation,
    component_id: row.component_id,
    component_desc: row.component_desc,
  };
  originalData.value = { ...row };
  dialogVisible.value = true;
};

// 提交表单
let handleSubmit = function () {
  formRef.value.validate(async function (valid) {
    if (!valid) return;

    try {
      if (dialogType.value === 'add') {
        await axios.post('/api/component/add', {
          const: form.value.const,
          technical_preparation: form.value.technical_preparation,
          component_id: form.value.component_id,
          component_desc: form.value.component_desc,
        });
        ElMessage.success('新增成功');
      } else {
        await axios.put('/api/component/update', {
          const: form.value.const,
          technical_preparation: form.value.technical_preparation,
          component_id: form.value.component_id,
          component_desc: form.value.component_desc,
          old_const: originalData.value.const,
          old_technical_preparation: originalData.value.technical_preparation,
          old_component_id: originalData.value.component_id,
        });
        ElMessage.success('更新成功');
      }
      dialogVisible.value = false;
      load();
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || '操作失败：' + err.message);
    }
  });
};

// 删除
let handleDelete = async function (row) {
  try {
    await ElMessageBox.confirm('确定删除此部件推荐？', '删除确认', { type: 'warning' });
    await axios.delete('/api/component/delete', {
      data: {
        const: row.const,
        technical_preparation: row.technical_preparation,
        component_id: row.component_id,
        component_desc: ''
      }
    });
    ElMessage.success('删除成功');
    load();
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.response?.data?.detail || '删除失败：' + err.message);
    }
  }
};

// 初始化加载
load();
</script>

<style scoped>
</style>