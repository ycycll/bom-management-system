<template>
  <div class="main-layout">
    <!-- 左侧导航 -->
    <div class="sidebar">
      <div class="logo">百炼</div>
      <el-menu
          default-active="1"
          class="el-menu-vertical"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          router
      >
        <el-menu-item index="/home">
          <el-icon><HomeFilled /></el-icon>
          <span>主页</span>
        </el-menu-item>
        <el-menu-item index="/sample">
          <el-icon><Grid /></el-icon>
          <span>样本型谱</span>
        </el-menu-item>
        <el-menu-item index="/copilot">
          <el-icon><ChatLineSquare /></el-icon>
          <span>Copilot</span>
        </el-menu-item>
        <el-menu-item index="/defog">
          <el-icon><Sunny /></el-icon>
          <span>DEFOG</span>
        </el-menu-item>

        <el-sub-menu index="admin">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>后台管理</span>
          </template>
          <el-menu-item index="/hub">
            <el-icon><Odometer /></el-icon>
            <span>推荐后台</span>
          </el-menu-item>
          <el-menu-item index="/agreement">
            <el-icon><Document /></el-icon>
            <span>协议后台</span>
          </el-menu-item>
          <el-menu-item index="/draw">
            <el-icon><FolderOpened /></el-icon>
            <span>图纸后台</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
      <div class="logout-btn">
        <el-button type="danger" @click="handleLogout" plain>退出登录</el-button>
      </div>
    </div>

    <!-- 右侧内容 - 插槽 -->
    <div class="content">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import {useRouter} from "vue-router";
import {ElMessage} from "element-plus";
import {User, HomeFilled, Grid, ChatLineSquare, Sunny, Setting, Odometer, Box, Document, FolderOpened} from "@element-plus/icons-vue";
import { onMounted } from "vue";

const router = useRouter();

onMounted(() => {
  const initLive2D = () => {
    if (window.L2Dwidget) {
      window.L2Dwidget.init({
        pluginRootPath: 'https://fastly.jsdelivr.net/npm/live2d-widget@3.1.4/',
        pluginJsPath: 'lib/',
        pluginModelPath: 'assets/',
        tagMode: false,
        debug: false,
        model: {
          jsonPath: 'https://fastly.jsdelivr.net/npm/live2d-widget-model-miku@1.0.5/assets/miku.model.json'
        },
        display: {
          position: 'left',
          width: 130,
          height: 260,
          hOffset: 20,
          vOffset: 160
        },
        mobile: {
          show: true,
          scale: 0.5
        },
        react: {
          opacityDefault: 0.9,
          opacityOnHover: 0.2
        }
      });
    }
  };

  // 如果已加载则直接初始化
  if (window.L2Dwidget) {
    initLive2D();
    return;
  }

  // 加载核心 JS
  const script = document.createElement('script');
  script.src = 'https://fastly.jsdelivr.net/npm/live2d-widget@3.1.4/lib/L2Dwidget.min.js';
  script.onload = initLive2D;
  document.head.appendChild(script);
});

const handleLogout = () => {
  localStorage.removeItem('isLoggedIn');
  localStorage.removeItem('userRole');
  ElMessage.success('退出成功');
  router.push('/');
};
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  position: fixed;
  top: 0;
  left: 0;
}

.sidebar {
  width: 200px;
  background-color: #304156;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: white;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #1f2d3d;
  flex-shrink: 0;
}

.el-menu-vertical {
  flex: 1;
  border-right: none;
}

.logout-btn {
  padding: 20px;
  text-align: center;
  border-top: 1px solid #1f2d3d;
  flex-shrink: 0;
}

.content {
  flex: 1;
  background-color: #f0f2f5;
  padding: 4px;
  overflow: auto;
}
</style>