<template>
  <aside_navigation>
    <div class="zero-container">
      <el-upload
          class="upload-box"
          drag
          action="#"
          v-bind:auto-upload="false"
          v-bind:before-upload="beforeUpload"
          v-model:file-list="fileList"
          v-bind:limit="1"
          v-bind:accept="acceptTypes"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击选择文件</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            仅支持上传 .xls 或 .xlsx 格式的Excel文件
            <el-button type="primary" plain round @click="handleUpload" :loading="uploading" style="margin-left: 40px" size="default">
              处理
            </el-button>
            <el-button type="warning" plain round @click="check" :loading="checking" style="margin-left: 40px" size="default">
              校核
            </el-button>
            <el-button type="success" plain round @click="maintain" :loading="maintaining" style="margin-left: 40px" size="default">
              维护
            </el-button>
            <el-tooltip content="导出表格" placement="top">
              <el-button type="info" circle v-bind:icon="Monitor" @click="exportFilter" style="margin-left: 40px" size="default"></el-button>
            </el-tooltip>
            <el-tooltip content="推荐数据入库" placement="top">
              <el-button color="#003472" circle v-bind:icon="OfficeBuilding" @click="uploadRecommend" :loading="savingToDB" style="margin-left: 40px" size="default"></el-button>
            </el-tooltip>
            <el-tooltip content="合并" placement="top">
              <el-button color="#626aef" circle v-bind:icon="SetUp" @click="concatColumns" style="margin-left: 40px" size="default"></el-button>
            </el-tooltip>
            <el-tooltip content="批量粘贴" placement="top">
              <el-button color="#8FD2E6" circle v-bind:icon="DocumentCopy" @click="openPasteDialog" style="margin-left: 40px" size="default"></el-button>
            </el-tooltip>
            <el-tooltip content="保存进度" placement="top">
              <el-button type="warning" circle v-bind:icon="Upload" @click="openSaveDialog" style="margin-left: 40px" size="default"></el-button>
            </el-tooltip>
            <el-tooltip content="读取存档" placement="top">
              <el-button type="primary" circle v-bind:icon="Download" @click="loadArchives" style="margin-left: 40px" size="default"></el-button>
            </el-tooltip>
          </div>
        </template>
      </el-upload>

      <div v-if="fileName" class="file-info">
        <el-text size="large">已选择文件: {{ fileName }}</el-text>
      </div>

      <div style="margin-bottom: 10px; display: flex;">
        <el-input v-model="filterTextComputed" placeholder="请输入机座号筛选" style="width: 200px; margin-right: 40px;"/>
        <el-input v-model="polesFilterTextComputed" placeholder="请输入极数筛选" style="width: 200px"/>
      </div>

      <!-- 处理结果表格 -->
      <div style="height: 600px ; overflow-y: auto;">
        <el-table :data="filterData" style="width: 100%" border>
          <el-table-column prop="workNo" label="工作令号" min-width="140" />
          <el-table-column prop="techPreparation" label="技术准备" min-width="600">
            <template #default="scope">
              <el-input v-model="scope.row.techPreparation" @blur="saveData" type="textarea"/>
            </template>
          </el-table-column>
          <el-table-column prop="lineItemNotes" label="行项目备注" min-width="600" v-if="showLineItemNotesColumn" >
            <template #default="scope">
              <el-input v-model="scope.row.lineItemNotes" @blur="saveData" type="textarea"/>
            </template>
          </el-table-column>
          <el-table-column prop="productType" label="产品型号" width="140" >
            <template #default="scope">
              <el-input v-model="scope.row.productType" @blur="saveData" type="text"/>
            </template>
          </el-table-column>
          <el-table-column prop="materialNo" label="物料号码" width="150">
            <template #default="scope">
              <el-input v-model="scope.row.materialNo" @blur="saveData" />
            </template>
          </el-table-column>
          <el-table-column prop="materialDesc" label="物料长文本描述" min-width="220">
            <template #default="scope">
              <el-input v-model="scope.row.materialDesc" @blur="saveData" type="textarea"/>
            </template>
          </el-table-column>
          <el-table-column prop="power" label="功率" min-width="60" />
          <el-table-column label="推荐" width="80" fixed="right">
            <template #default="scope">
              <el-button type="primary" size="small" @click="showBOMRecommend(scope.row)">
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-drawer title="推荐" resizable v-model="drawerVisible" direction="rtl" size="60%">
          <div style="margin-bottom: 20px">
            <h3 style="margin: 0 0 10px 0; color: #409EFF; font-size: 16px">整机推荐</h3>
            <el-table v-bind:data="bomRecommendData" border>
              <el-table-column prop="recommendNo" label="物料号码" />
              <el-table-column prop="recommendDesc" label="物料描述" />
              <el-table-column prop="recommendTP" label="推荐准备" />
              <el-table-column prop="recommendScore" label="近似度" />
              <el-table-column prop="color" label="面漆" />
              <el-table-column label="操作" width="80">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="fillRecommend(scope.row)">
                    填入
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <h3 style="margin: 0 0 10px 0; color: #67C23A; font-size: 16px">部件推荐</h3>
          <el-input
              v-bind:value="componentText"
              type="textarea"
              v-bind:rows="8"
              readonly
              style="font-family: monospace; font-size: 13px"
          />
        </el-drawer>
        <el-drawer title="维护" resizable v-model="maintainDrawerVisible" direction="ltr" size="70%">
          <div style="text-align: left; margin-bottom: 10px;">
            <el-button type="success" @click="exportMaintainTable" size="default">
              导出 Excel
            </el-button>
          </div>
          <el-table v-bind:data="maintainResult" border>
            <el-table-column prop="出厂编码" label="出厂编码" />
            <el-table-column prop="物料号" label="物料号" />
            <el-table-column prop="中文描述" label="中文描述" />
            <el-table-column prop="型号" label="型号">
              <template #default="scope">
                <el-input v-model="scope.row.型号" />
              </template>
            </el-table-column>
            <el-table-column prop="额定功率" label="额定功率">
              <template #default="scope">
                <el-input v-model="scope.row.额定功率" />
              </template>
            </el-table-column>
            <el-table-column prop="额定电压" label="额定电压">
              <template #default="scope">
                <el-input v-model="scope.row.额定电压" />
              </template>
            </el-table-column>
            <el-table-column prop="频率" label="频率">
              <template #default="scope">
                <el-input v-model="scope.row.频率" />
              </template>
            </el-table-column>
            <el-table-column prop="防护等级" label="防护等级">
              <template #default="scope">
                <el-input v-model="scope.row.防护等级" />
              </template>
            </el-table-column>
            <el-table-column prop="绝缘等级" label="绝缘等级">
              <template #default="scope">
                <el-input v-model="scope.row.绝缘等级" />
              </template>
            </el-table-column>
            <el-table-column prop="冷却方式" label="冷却方式">
              <template #default="scope">
                <el-input v-model="scope.row.冷却方式" />
              </template>
            </el-table-column>
            <el-table-column prop="防腐等级" label="防腐等级">
              <template #default="scope">
                <el-input v-model="scope.row.防腐等级" />
              </template>
            </el-table-column>
            <el-table-column prop="防爆等级" label="防爆等级">
              <template #default="scope">
                <el-input v-model="scope.row.防爆等级" />
              </template>
            </el-table-column>
            <el-table-column prop="接法" label="接法">
              <template #default="scope">
                <el-input v-model="scope.row.接法" />
              </template>
            </el-table-column>
            <el-table-column prop="电流" label="电流">
              <template #default="scope">
                <el-input v-model="scope.row.电流" />
              </template>
            </el-table-column>
            <el-table-column prop="转速" label="转速">
              <template #default="scope">
                <el-input v-model="scope.row.转速" />
              </template>
            </el-table-column>
            <el-table-column prop="效率" label="效率">
              <template #default="scope">
                <el-input v-model="scope.row.效率" />
              </template>
            </el-table-column>
            <el-table-column prop="功率因数" label="功率因数">
              <template #default="scope">
                <el-input v-model="scope.row.功率因数" />
              </template>
            </el-table-column>
            <el-table-column prop="重量" label="重量">
              <template #default="scope">
                <el-input v-model="scope.row.重量" />
              </template>
            </el-table-column>
            <el-table-column prop="标准编码" label="标准编码">
              <template #default="scope">
                <el-input v-model="scope.row.标准编码" />
              </template>
            </el-table-column>
            <el-table-column prop="噪声" label="噪声">
              <template #default="scope">
                <el-input v-model="scope.row.噪声" />
              </template>
            </el-table-column>
            <el-table-column prop="驱动端轴承" label="驱动端轴承">
              <template #default="scope">
                <el-input v-model="scope.row.驱动端轴承" />
              </template>
            </el-table-column>
            <el-table-column prop="非驱动轴承" label="非驱动轴承">
              <template #default="scope">
                <el-input v-model="scope.row.非驱动轴承" />
              </template>
            </el-table-column>
            <el-table-column prop="铭牌料号" label="铭牌料号">
              <template #default="scope">
                <el-input v-model="scope.row.铭牌料号" />
              </template>
            </el-table-column>
            <el-table-column prop="打印模板" label="打印模板">
              <template #default="scope">
                <el-input v-model="scope.row.打印模板" />
              </template>
            </el-table-column>
            <el-table-column prop="环境温度" label="环境温度">
              <template #default="scope">
                <el-input v-model="scope.row.环境温度" />
              </template>
            </el-table-column>
            <el-table-column prop="海拔高度" label="海拔高度">
              <template #default="scope">
                <el-input v-model="scope.row.海拔高度" />
              </template>
            </el-table-column>
            <el-table-column prop="工作制" label="工作制">
              <template #default="scope">
                <el-input v-model="scope.row.工作制" />
              </template>
            </el-table-column>
            <el-table-column prop="服务系数SF" label="服务系数SF">
              <template #default="scope">
                <el-input v-model="scope.row['服务系数SF']" />
              </template>
            </el-table-column>
            <el-table-column prop="编码规则" label="编码规则">
              <template #default="scope">
                <el-input v-model="scope.row.编码规则" />
              </template>
            </el-table-column>
            <el-table-column prop="备用列8" label="备用列8">
              <template #default="scope">
                <el-input v-model="scope.row['备用列8']" />
              </template>
            </el-table-column>
            <el-table-column prop="备用13" label="备用13">
              <template #default="scope">
                <el-input v-model="scope.row['备用13']" />
              </template>
            </el-table-column>
          </el-table>
        </el-drawer>
        <el-drawer title="校核" resizable v-model="checkDrawerVisible" direction="btt" size="30%">
          <el-table v-bind:data="checkResult" border>
            <el-table-column prop="workNo" label="工作令号" />
            <el-table-column prop="bomFalse" label="BOM错误" />
          </el-table>
        </el-drawer>
      </div>
      <el-dialog v-model="pasteDialogVisible" title="批量粘贴物料数据" width="70%">
        <div style="margin-bottom: 10px; color: #909399;">
          请粘贴Excel数据（支持两列：物料号码、物料长文本描述），将自动匹配到对应行
        </div>
        <el-input
            v-model="pasteText"
            type="textarea"
            :rows="15"
            placeholder="在此处粘贴 Excel 数据...&#10;格式示例：&#10;物料号码1	物料描述1&#10;物料号码2	物料描述2"
        />
        <template #footer>
          <el-button @click="pasteDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmPaste">确认粘贴</el-button>
        </template>
      </el-dialog>
      <el-dialog v-model="saveDialogVisible" title="保存进度" width="600px">
        <el-form label-width="60px">
          <el-form-item label="流程号">
            <el-input v-model="saveForm.flow_no" placeholder="请输入流程号" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="saveForm.remark" type="textarea" :rows="3" placeholder="可选备注" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="saveDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveArchive" :loading="saving">保存</el-button>
        </template>
      </el-dialog>
      <el-dialog v-model="archiveListVisible" title="读取存档" width="900px">
        <div style="display: flex; gap: 10px; margin-bottom: 15px">
          <el-input v-model="archiveSearch" placeholder="搜索流程号或备注" clearable @keyup.enter="loadArchives" style="flex: 1" />
          <el-button @click="loadArchives" type="primary">搜索</el-button>
        </div>
        <el-table :data="archiveList" border>
          <el-table-column prop="flow_no" label="流程号" width="160" />
          <el-table-column prop="remark" label="备注" />
          <el-table-column prop="record_count" label="记录数" width="80" />
          <el-table-column prop="updated_at" label="更新时间" width="160" />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button type="primary" size="small" @click="loadArchive(scope.row.id)">加载</el-button>
              <el-button type="danger" size="small" @click="deleteArchive(scope.row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
            v-model:current-page="archivePage"
            :page-size="10"
            :total="archiveTotal"
            layout="total, prev, pager, next"
            @current-change="loadArchives"
            style="margin-top: 15px; justify-content: center"
        />
      </el-dialog>
    </div>
  </aside_navigation>

</template>
<script setup>
import aside_navigation from '../component/navigation.vue'
import {UploadFilled, Monitor, SetUp, OfficeBuilding, DocumentCopy, Download, Upload} from "@element-plus/icons-vue";
import {ElMessage, ElMessageBox} from "element-plus";
import axios from 'axios';
import {computed, ref} from "vue";
import * as XLSX from "xlsx";

let drawerVisible = ref(false);
let showLineItemNotesColumn = ref(true);
let bomRecommendData = ref([]);
let componentText = ref('');
let currentSelectedRow = ref(null);
// 文件列表
let fileList = ref([])

let savingToDB = ref(false)
// 上传状态
let uploading = ref(false)
// 接受的文件类型
let acceptTypes = '.xls,.xlsx'
// 当前文件名
let fileName = ref('')
// 处理返回数据
let data = ref(JSON.parse(localStorage.getItem('copilotData') || '[]'))

let filterText = ref(localStorage.getItem('copilotFilterText') || '');
let polesFilterText = ref(localStorage.getItem('copilotPolesFilterText') || '')

let pasteDialogVisible = ref(false)
let pasteText = ref('')
let openPasteDialog = function () {
  pasteText.value = ''
  pasteDialogVisible.value = true
}

// 存档相关
let saveDialogVisible = ref(false)
let saveForm = ref({ flow_no: '', remark: '' })
let saving = ref(false)

let openSaveDialog = function () {
  if (filterData.value.length === 0) {
    ElMessage.warning('无数据可保存')
    return
  }
  saveForm.value = { flow_no: '', remark: '' }
  saveDialogVisible.value = true
}

let saveArchive = async function () {
  if (!saveForm.value.flow_no.trim()) {
    ElMessage.warning('请输入流程号')
    return
  }
  saving.value = true
  try {
    await axios.post('/api/copilot/archive/save', {
      flow_no: saveForm.value.flow_no,
      remark: saveForm.value.remark,
      archive_data: filterData.value
    })
    ElMessage.success('保存成功')
    saveDialogVisible.value = false
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  } finally {
    saving.value = false
  }
}

let archiveListVisible = ref(false)
let archiveList = ref([])
let archiveTotal = ref(0)
let archivePage = ref(1)
let archiveSearch = ref('')

let loadArchives = async function () {
//  archivePage.value = 1 
  try {
    const response = await axios.get('/api/copilot/archive/list', {
      params: { page: archivePage.value, page_size: 10, keyword: archiveSearch.value }
    })
    if (response.data.code === 200) {
      archiveList.value = response.data.data
      archiveTotal.value = response.data.total
      archiveListVisible.value = true
    }
  } catch (error) {
    ElMessage.error('查询失败：' + error.message)
  }
}

let loadArchive = async function (archiveId) {
  try {
    const response = await axios.get(`/api/copilot/archive/load/${archiveId}`)
    if (response.data.code === 200) {
      data.value = response.data.data
      localStorage.setItem('copilotData', JSON.stringify(data.value))
      ElMessage.success('加载成功')
      archiveListVisible.value = false
    }
  } catch (error) {
    ElMessage.error('加载失败：' + error.message)
  }
}

let deleteArchive = async function (archiveId) {
  try {
    await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
    await axios.delete(`/api/copilot/archive/delete/${archiveId}`)
    ElMessage.success('删除成功')
    loadArchives()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

let confirmPaste = function () {
  if (!pasteText.value.trim()) {
    ElMessage.warning('请输入要粘贴的数据')
    return
  }

  let rows = pasteText.value.trim().split('\n')
  let successCount = 0

  rows.forEach((rowText, index) => {
    if (index >= filterData.value.length) return

    const cells = rowText.split('\t')
    if (cells.length >= 2) {
      filterData.value[index].materialNo = cells[0].trim()
      filterData.value[index].materialDesc = cells[1].trim()
      successCount++
    }
  })

  localStorage.setItem('copilotData', JSON.stringify(data.value))
  ElMessage.success(`成功粘贴 ${successCount} 行数据`)
  pasteDialogVisible.value = false
}


let filterTextComputed = computed({
  get: () => filterText.value,
  set: (newValue) => {
    filterText.value = newValue;
    localStorage.setItem('copilotFilterText', newValue);
    showLineItemNotesColumn.value = true;
  }
});

let polesFilterTextComputed = computed({
  get: () => polesFilterText.value,
  set: (newValue) => {
    polesFilterText.value = newValue;
    localStorage.setItem('copilotPolesFilterText', newValue);
    showLineItemNotesColumn.value = true;
  }
});

let checking = ref(false);
let checkDrawerVisible = ref(false);
let checkResult = ref([]);

let check = async function () {
  if (filterData.value.length === 0) {
    ElMessage.warning('无数据');
    return;
  }

  checking.value = true;

  try {
    let response = await axios.post('/api/copilot/check', filterData.value, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log('Check response:', response.data);
    checkResult.value = response.data;
    checkDrawerVisible.value = true;
    ElMessage.success('校核成功');
  } catch (error) {
    console.error('Check error:', error);
    ElMessage.error('校核失败：' + error.message);
  } finally {
    checking.value = false;
  }
};


let maintaining = ref(false);
let maintainDrawerVisible = ref(false);
let maintainResult = ref([]);
let maintain = async function () {
  if (filterData.value.length === 0) {
    ElMessage.warning('无数据');
    return;
  }

  maintaining.value = true;

  try {
    let response = await axios.post('/api/copilot/maintain', filterData.value, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log('Maintain response:', response.data);
    maintainResult.value = response.data;
    maintainDrawerVisible.value = true;
    ElMessage.success('维护成功');
  } catch (error) {
    console.error('Maintain error:', error);
    ElMessage.error('维护失败：' + error.message);
  } finally {
    maintaining.value = false;
  }
};


let exportMaintainTable = function () {
  if (!maintainResult.value || maintainResult.value.length === 0) {
    ElMessage.warning('没有可导出的数据');
    return;
  }

  try {
    let worksheet = XLSX.utils.json_to_sheet(maintainResult.value);
    let workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, '铭牌数据');

    XLSX.writeFile(workbook, `铭牌数据_${new Date().getTime()}.xlsx`);
    ElMessage.success('导出成功');
  } catch (error) {
    console.error('Export error:', error);
    ElMessage.error('导出失败：' + error.message);
  }
};


// 计算筛选后的数据
let filterData = computed(() => {
  let handledFilter = data.value;

  // 机座号筛选
  if (filterText.value) {
    let regex = /-(\d+)/;
    handledFilter = handledFilter.filter(row => {
      if (!row.productType) return false;
      let match = row.productType.match(regex);
      if (match) {
        let frameNo = match[1];
        return frameNo.includes(filterText.value);
      }
      return false;
    });
  }

  // 极数筛选
  if (polesFilterText.value) {
    let regex = /-(\d+)$/;
    handledFilter = handledFilter.filter(row => {
      if (!row.productType) return false;
      let match = row.productType.match(regex);
      if (match) {
        let poles = match[1];
        return poles.includes(polesFilterText.value);
      }
      return false;
    });
  }

  return handledFilter;
});


let concatColumns = function () {
  if (filterData.value.length === 0) {
    ElMessage.warning('无数据可合并');
    return;
  }

  data.value = data.value.map(row => {
    return {
      ...row,
      techPreparation: ` ${row.techPreparation} \n ${row.lineItemNotes} `,
      lineItemNotes: ''
    };
  });

  showLineItemNotesColumn.value = false;
  localStorage.setItem('copilotData', JSON.stringify(data.value));
  ElMessage.success('列合并成功');
  // 复制四列数据到剪贴板（格式化为Excel兼容的表格）
  const clipboardData = filterData.value.map(row => {
    // 处理换行符和特殊字符，确保Excel正确解析
    const techPrep = row.techPreparation.replace(/\n/g, '\r\n');
    const materialDesc = row.materialDesc.replace(/\n/g, '\r\n');
    return `"${row.workNo}"\t"${techPrep}"\t"${row.materialNo}"\t"${materialDesc}"`;
  }).join('\r\n');

  navigator.clipboard.writeText(clipboardData).then(() => {
    ElMessage.success('已复制工作令号、技术准备、物料号、长文本描述到剪贴板');
  }).catch(err => {
    console.error('复制失败:', err);
    ElMessage.error('复制失败，请手动复制');
  });
};

// 导出筛选后的数据
let exportFilter = function () {
  if (filterData.value.length === 0) {
    ElMessage.warning('没有可导出的数据');
    return;
  }

  try {
    let exportFilterSheet = filterData.value.map((item) => ({
      '工作令号': item.workNo,
      '技术准备': item.techPreparation,
      '物料号码': item.materialNo,
      '物料长文本描述': item.materialDesc,
      '产品型号': item.productType,
      '功率': item.power,
      '电压': item.volt,
      '频率': item.freq,
      '安装方式': item.mountingType,
      '绝缘等级': item.insulationClass,
      '防护等级': item.protectionClass,
      '出线方式': item.leadWireMethod,
      '环境条件': item.environmentalConditions,
      '冷却方式': item.coolingMethod,
      '行项目备注': item.lineItemNotes,
      '防爆等级': item.explosionProofClass,
      '环境温度': item.ambientTemperature,
      '主接线盒位置及方向': item.junctionBoxPosition,
      '旋转方向': item.rotationDirection,
      '轴承品牌': item.bearingBrand,
      '海拔高度': item.altitude,
      '加热器': item.heater,
      '定子测温': item.statorTempSensor,
      '轴承测温': item.bearingTempSensor
    }));
    let worksheet = XLSX.utils.json_to_sheet(exportFilterSheet);
    let workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, '报排产');

    XLSX.writeFile(workbook, `报排产_${new Date().getTime()}.xlsx`);
    ElMessage.success('导出成功');
  } catch (error) {
    console.error('Export error:', error);
    ElMessage.error('导出失败：' + error.message);
  }
};

let saveData = function () {
  localStorage.setItem('copilotData', JSON.stringify(data.value));
  ElMessage.success('数据已保存');
};

let beforeUpload = function (file) {
  // 检查文件类型
  let isExcel = file.name.endsWith('.xls') || file.name.endsWith('.xlsx');
  if (!isExcel) {
    ElMessage.error('只能上传 .xls 或 .xlsx 格式的文件！');
    return false;
  }

  // 检查文件大小（限制50MB）
  let sizeLimit = 50 * 1024 * 1024;
  if (file.size > sizeLimit) {
    ElMessage.error('文件大小不能超过 50MB！');
    return false;
  }

  // 更新文件名显示
  fileName.value = file.name;

  return true;
};


// 保存到数据库
let uploadRecommend = async function () {
  if (filterData.value.length === 0) {
    ElMessage.warning('没有可入库的数据');
    return;
  }

  savingToDB.value = true;
  try {
    let response = await axios.post('/api/copilot/recommend-to-db', filterData.value);
    if (response.data.code === 200) {
      ElMessage.success('数据入库成功');
    } else {
      ElMessage.error(response.data.message || '入库失败');
    }
  } catch (error) {
    ElMessage.error('入库失败：' + error.message);
  } finally {
    savingToDB.value = false;
  }
};

let handleUpload = async function () {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件！');
    return;
  }

  uploading.value = true;
  data.value = [];

  try {
    let formData = new FormData();
    let file = fileList.value[0];
    if (file) {
      formData.append('file', file.raw);
    }

    let response = await axios.post('/api/copilot/upload', formData);

    if (response.data.code === 200) {
      data.value = response.data.data;
      localStorage.setItem('copilotData', JSON.stringify(data.value));
      ElMessage.success('文件处理成功');
      showLineItemNotesColumn.value = true;
    } else {
      ElMessage.error(response.data.message || '处理失败');
    }
  } catch (error) {
    ElMessage.error('上传失败：' + error.message);
  } finally {
    uploading.value = false;
    fileList.value = [];
    fileName.value = '';
  }
};

// 查看BOM推荐
let showBOMRecommend = function (row) {
  currentSelectedRow.value = row;
  axios.get('/api/copilot/recommend', {
    params: {
      techPreparation: row.techPreparation,
      productType: row.productType,
      environmentalConditions: row.environmentalConditions
    }
  }).then(function (response) {
    bomRecommendData.value = response.data.data;
    let components = response.data.components || [];

    if (components.length > 0) {
      componentText.value = components.map(item =>
          `${item.component_id}：${item.component_desc}`
      ).join('\n');
    } else {
      componentText.value = '';
    }
    drawerVisible.value = true;
    console.log(response);
  });
};

let fillRecommend = function (recommendItem) {
  if (!currentSelectedRow.value) return;

  currentSelectedRow.value.materialNo = recommendItem.recommendNo;
  currentSelectedRow.value.materialDesc = recommendItem.recommendDesc;

  localStorage.setItem('copilotData', JSON.stringify(data.value));
  ElMessage.success('已填入');
  drawerVisible.value = false;
};

</script>

<style scoped>.zero-container {
  padding: 20px;
  max-width: 1420px;
  margin: 0 auto;
}

.upload-box {
  margin-bottom: 20px;
}

.file-info {
  margin-top: 10px;
  text-align: center;
}
</style>