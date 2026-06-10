<template>
  <aside_navigation>
    <div>
      <div style="text-align: center; font-size: 30px; margin-bottom: 30px">推荐后台</div>
      <div style="width: 80%; margin: 30px auto;">
        <div style="margin-bottom: 8px">
          <el-input placeholder="请输入技术准备筛选" v-model="data.recommendTP" clearable
                    style="width: 20% ; margin-right: 20px"></el-input>
          <el-input placeholder="请输入料号查询" v-model="data.recommendNo" clearable
                    style="width: 20% ; margin-right: 20px"></el-input>
        </div>
        <div style="margin-bottom: 20px">
          <el-input placeholder="请输入描述查询" v-model="data.recommendDesc" clearable
                    style="width: 20% ; margin-right: 20px"></el-input>
          <el-input placeholder="请输入机座号查询" v-model="data.const" clearable
                    style="width: 20% ; margin-right: 20px"></el-input>
          <el-button type="primary" v-on:click="load" style="margin-right: 10px">查询</el-button>
        </div>
        <div style="margin-top: 10px">
          <el-table v-bind:data="data.tableData" style="width: 100%" border stripe>
            <el-table-column prop="recommendTP" label="技术准备" width="400"/>
            <el-table-column prop="recommendNo" label="料号" width="130"/>
            <el-table-column prop="recommendDesc" label="描述" width="600"/>
            <el-table-column prop="const" label="机座" width="100"/>
            <el-table-column label="操作" width="80" fixed="right">
              <template #default="scope">
                <el-button :type="isAdmin ? 'danger' : 'default'" :disabled="!isAdmin"
                           size="small" v-on:click="huddle_delete(scope.row.recommendTP)">删除</el-button>
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
  </aside_navigation>
</template>
<script setup>
import {ref, computed} from "vue";
import axios from "axios";
import {ElMessage} from "element-plus";

import aside_navigation from '../component/navigation.vue'

let data = ref({
      total: 0,
      tableData: [],
      page_num: 1,
      page_size: 6,
      recommendTP: null,
      recommendNo: null,
      recommendDesc: null,
      const: null,
      form: {},
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



let huddle_delete = function (recommendTP) {
  axios.delete('/hub/delete/' + recommendTP).then(
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



let load = function () {
  axios.get('/hub/list', {
    params: {
      page_num: data.value.page_num,
      page_size: data.value.page_size,
      recommendTP: data.value.recommendTP,
      recommendNo: data.value.recommendNo,
      recommendDesc: data.value.recommendDesc,
      const: data.value.const,
    }
  }).then(function (resp) {
    data.value.tableData = resp.data.json_resp
    data.value.total = resp.data.total
  })
}
load()
</script>

<style scoped>


</style>