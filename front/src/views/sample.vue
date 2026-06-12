<template>
  <aside_navigation>
    <div>
      <div style="text-align: center; font-size: 30px; margin-bottom: 30px">WE样本</div>
      <div style="width: 80%; margin: 30px auto;">
        <div style="margin-bottom: 8px">
          <el-input placeholder="请输入型号查询" v-model="data.we_type" clearable
                    style="width: 20% ; margin-right: 20px"></el-input>
          <el-select placeholder="请选择电压查询" v-model="data.we_volt" clearable
                     style="width: 20% ; margin-right: 20px">
            <el-option label="380" value="380"></el-option>
            <el-option label="400" value="400"></el-option>
            <el-option label="415" value="415"></el-option>
          </el-select>
        </div>
        <div style="margin-bottom: 20px">
          <el-select placeholder="请选择频率查询" v-model="data.we_freq" clearable
                     style="width: 20% ; margin-right: 20px">
            <el-option label="50" value="50"></el-option>
            <el-option label="60" value="60"></el-option>
          </el-select>
          <el-select placeholder="请选择材质查询" v-model="data.we_material" clearable
                    style="width: 20% ; margin-right: 20px">
            <el-option label="铁壳" value="铁壳"></el-option>
            <el-option label="铝壳" value="铝壳"></el-option>
          </el-select>
          <el-button type="primary" v-on:click="load" style="margin-right: 10px">查询</el-button>
          <el-button v-if="isAdmin" type="primary" v-on:click="handle_add">增加</el-button>
        </div>
        <div style="margin-top: 10px">
          <el-table v-bind:data="data.tableData" style="width: 100%" border stripe>
            <el-table-column prop="we_type" label="型号" width="120"/>
            <el-table-column prop="we_power" label="功率" width="60"/>
            <el-table-column prop="we_speed" label="转速" width="80"/>
            <el-table-column prop="we_eff" label="效率" width="80"/>
            <el-table-column prop="we_factor" label="功率因数" width="100"/>
            <el-table-column prop="we_tor_mul" label="堵转转矩倍数" width="120"/>
            <el-table-column prop="we_cur_mul" label="堵转电流倍数" width="120"/>
            <el-table-column prop="we_max_tor_mul" label="最大转矩倍数" width="120"/>
            <el-table-column prop="we_weight" label="重量" width="60"/>
            <el-table-column prop="we_noise_p" label="声压噪声" width="100"/>
            <el-table-column prop="we_noise_w" label="声压功率" width="100"/>
            <el-table-column prop="we_inertia" label="转动惯量" width="100"/>
            <el-table-column prop="we_torque" label="转矩" width="80"/>
            <el-table-column prop="we_freq" label="频率" width="80"/>
            <el-table-column prop="we_volt" label="电压" width="80"/>
            <el-table-column prop="we_cur" label="电流" width="80"/>
            <el-table-column prop="we_material" label="材质" width="80"/>
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
      <el-dialog v-model="data.dialogVisible" title="增加样本" width="40%" destroy-on-close>
        <el-form v-bind:model="data.form" ref="form_ref" v-bind:rules="data.rules" label-width="120px"
                 style="padding: 20px">
            <el-form-item label="型号" prop="we_type">
              <el-input v-model="data.form.we_type" placeholder="请输入型号" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="功率" prop="we_power">
              <el-input v-model="data.form.we_power" placeholder="请输入功率" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="转速" prop="we_speed">
              <el-input v-model="data.form.we_speed" placeholder="请输入转速" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="效率" prop="we_eff">
              <el-input v-model="data.form.we_eff" placeholder="请输入效率" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="功率因数" prop="we_factor">
              <el-input v-model="data.form.we_factor" placeholder="请输入功率因数" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="堵转转矩倍数" prop="we_tor_mul">
              <el-input v-model="data.form.we_tor_mul" placeholder="请输入堵转转矩倍数" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="堵转电流倍数" prop="we_cur_mul">
              <el-input v-model="data.form.we_cur_mul" placeholder="请输入堵转电流倍数" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="最大转矩倍数" prop="we_max_tor_mul">
              <el-input v-model="data.form.we_max_tor_mul" placeholder="请输入最大转矩倍数" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="重量" prop="we_weight">
              <el-input v-model="data.form.we_weight" placeholder="请输入重量" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="声压噪声" prop="we_noise_p">
              <el-input v-model="data.form.we_noise_p" placeholder="请输入声压噪声" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="声压功率" prop="we_noise_w">
              <el-input v-model="data.form.we_noise_w" placeholder="请输入声压功率" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="转动惯量" prop="we_inertia">
              <el-input v-model="data.form.we_inertia" placeholder="请输入转动惯量" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="转矩" prop="we_torque">
              <el-input v-model="data.form.we_torque" placeholder="请输入转矩" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="频率" prop="we_freq">
              <el-select v-model="data.form.we_freq" placeholder="请选择频率">
                <el-option label="50" value="50"></el-option>
                <el-option label="60" value="60"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="电压" prop="we_volt">
              <el-select v-model="data.form.we_volt" placeholder="请选择电压">
                <el-option label="380" value="380"></el-option>
                <el-option label="400" value="400"></el-option>
                <el-option label="415" value="415"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="电流" prop="we_cur">
              <el-input v-model="data.form.we_cur" placeholder="请输入电流" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="材质" prop="we_material">
              <el-select v-model="data.form.we_material" placeholder="请选择材质">
                <el-option label="铁壳" value="铁壳"></el-option>
                <el-option label="铝壳" value="铝壳"></el-option>
              </el-select>
            </el-form-item>
        </el-form>

        <template #footer>
          <div class="dialog_footer">
            <el-button @click="data.dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="save">保存</el-button>
          </div>
        </template>

      </el-dialog>
    </div>
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
      page_size: 12,
      we_type: null,
      we_volt: null,
      we_freq: null,
      we_material: null,
      dialogVisible: false,
      form: {},
      rules: {
        we_type: [{required: true, message: '请输入型号', trigger: 'blur'}],
        we_power: [{required: true, message: '请输入功率', trigger: 'blur'}],
        we_speed: [{required: true, message: '请输入转速', trigger: 'blur'}],
        we_eff: [{required: true, message: '请输入效率', trigger: 'blur'}],
        we_factor: [{required: true, message: '请输入功率因数', trigger: 'blur'}],
        we_tor_mul: [{required: true, message: '请输入堵转转矩倍数', trigger: 'blur'}],
        we_cur_mul: [{required: true, message: '请输入堵转电流倍数', trigger: 'blur'}],
        we_max_tor_mul: [{required: true, message: '请输入最大转矩倍数', trigger: 'blur'}],
        we_weight: [{required: true, message: '请输入重量', trigger: 'blur'}],
        we_noise_p: [{required: true, message: '请输入声压噪声', trigger: 'blur'}],
        we_noise_w: [{required: true, message: '请输入声压功率', trigger: 'blur'}],
        we_inertia: [{required: true, message: '请输入转动惯量', trigger: 'blur'}],
        we_torque: [{required: true, message: '请输入转矩', trigger: 'blur'}],
        we_freq: [{required: true, message: '请输入频率', trigger: 'blur'}],
        we_volt: [{required: true, message: '请输入电压', trigger: 'blur'}],
        we_cur: [{required: true, message: '请输入电流', trigger: 'blur'}],
        we_material: [{required: true, message: '请输入材质', trigger: 'blur'}]
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

let handle_add = function () {
  data.value.dialogVisible = true
  data.value.form = {}
}

let add = function () {
  axios.post('/we/add', data.value.form).then(function (resp) {
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
  axios.put('/we/update', data.value.form).then(function (resp) {
    if (resp.status === 200) {
      data.value.dialogVisible = false
      load()
      ElMessage.success('更新成功')
    } else {
      ElMessage.error('更新失败')
    }
  })
}

let huddle_edit = function (row) {
  data.value.form = JSON.parse(JSON.stringify(row))
  data.value.dialogVisible = true
}

let huddle_delete = function (id) {
  axios.delete('/we/delete/' + id).then(
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
  axios.get('/we/search_filter', {
    params: {
      page_num: data.value.page_num,
      page_size: data.value.page_size,
      we_type: data.value.we_type,
      we_volt: data.value.we_volt,
      we_freq: data.value.we_freq,
      we_material: data.value.we_material,
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