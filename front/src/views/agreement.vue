<template>
  <aside_navigation>
    <div>
      <div style="text-align: center; font-size: 30px; margin-bottom: 30px">协议后台</div>
      <div style="width: 80%; margin: 30px auto;">
        <div style="margin-bottom: 20px">
          <el-input placeholder="请输入协议号或协议名查询" v-model="data.keyword" clearable
                    style="width: 20% ; margin-right: 20px" @keyup.enter="load"></el-input>
          <el-button type="primary" v-on:click="load" style="margin-right: 10px">查询</el-button>
          <el-button v-if="isAdmin" type="primary" v-on:click="handle_add">增加</el-button>
        </div>
        <div style="margin-top: 10px">
          <el-table v-bind:data="data.tableData" style="width: 100%" border stripe>
            <el-table-column prop="agreement_id" label="协议号" width="130"/>
            <el-table-column prop="name" label="协议名" width="300"/>
            <el-table-column label="协议要点" >
              <template #default="scope">
                <div style="min-height: 240px; max-height: 300px; overflow-y: auto; white-space: pre-wrap; word-break: break-word;">
                  {{ scope.row.tp }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140" fixed="right">
              <template #default="scope">
                <el-button :type="isAdmin ? 'primary' : 'default'" :disabled="!isAdmin"
                           size="small" v-on:click="huddle_edit(scope.row)">编辑</el-button>
                <el-button :type="isAdmin ? 'danger' : 'default'" :disabled="!isAdmin"
                           size="small" v-on:click="huddle_delete(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div style="margin-top: 10px">
          <el-pagination background layout="total, prev ,pager, next" v-on:change="load"
                         v-bind:total="data.total"
                         v-model:current-page="data.page_num" v-model:page-size="data.page_size"/>
        </div>
      </div>
    </div>
    <el-dialog v-model="data.dialogVisible" title="增加/修改" width="40%" destroy-on-close>
      <el-form v-bind:model="data.form" ref="form_ref" v-bind:rules="data.rules" label-width="120px"
               style="padding: 20px">
        <el-form-item label="协议号" prop="agreement_id">
          <el-input v-model="data.form.agreement_id" placeholder="请输入协议号" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="协议名" prop="name">
          <el-input v-model="data.form.name" placeholder="请输入协议名" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="技术准备" prop="tp">
          <el-input
              v-model="data.form.tp"
              type="textarea"
              :rows="12"
              placeholder="请输入技术准备"
              autocomplete="off">
          </el-input>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog_footer">
          <el-button @click="data.dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="save">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </aside_navigation>
</template>
<script setup>
import {ref, computed} from "vue";
import axios from "axios";
import {ElMessage} from "element-plus";

import aside_navigation from '../component/navigation.vue'

let form_ref = ref()
let data = ref({
      total: 0,
      tableData: [],
      page_num: 1,
      page_size: 2,
      keyword: null,
      agreement_id: null,
      name: null,
      tp: null,
      form: {},
      rules: {
        agreement_id: [{required: true, message: '请输入协议号', trigger: 'blur'}],
        name: [{required: true, message: '请输入协议名', trigger: 'blur'}],
        tp: [{required: true, message: '请输入技术准备', trigger: 'blur'}],
      },
    }
)

// 计算用户角色
let userRole = computed(() => {
  return localStorage.getItem('userRole');
});

// 判断是否为管理员
const isAdmin = computed(() => {
  return userRole.value === 'admin';
});

let huddle_edit = function (row) {
  data.value.form = JSON.parse(JSON.stringify(row))
  data.value.dialogVisible = true
}


let huddle_delete = function (id) {
  axios.delete('/api/agreement/delete/' + id).then(
      function (resp) {
        if (resp.status === 200) {
          load()
          ElMessage.success('删除成功')
        } else {
          ElMessage.error('删除失败')
        }
      }
  )
}

let handle_add = function () {
  data.value.dialogVisible = true
  data.value.form = {}
}

let add = function () {
  axios.post('/api/agreement/add', data.value.form).then(function (resp) {
    if (resp.status === 200) {
      data.value.dialogVisible = false
      load()
      ElMessage.success('新增成功')
    } else {
      ElMessage.error('新增失败')
    }
  })
}

let update = function () {
  axios.put('/api/agreement/update', data.value.form).then(function (resp) {
    if (resp.status === 200) {
      data.value.dialogVisible = false
      load()
      ElMessage.success('更新成功')
    } else {
      ElMessage.error('更新失败')
    }
  })
}

let save = function () {
  form_ref.value.validate(function (valid) {
    if (valid) {
      if (data.value.form.id) {
        update()
      } else {
        add()
      }
    }
  })
}

let load = function () {
  axios.get('/api/agreement/list', {
    params: {
      page_num: data.value.page_num,
      page_size: data.value.page_size,
      keyword: data.value.keyword,
    }
  }).then(function (resp) {
    data.value.tableData = resp.data.data
    data.value.total = resp.data.total
  })
}
load()
</script>

<style scoped>


</style>