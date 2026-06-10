<template>
  <div class="login-container">
    <video class="background-video" autoplay loop muted playsinline ref="videoRef">
      <source :src="currentVideo" type="video/mp4">
    </video>
    <div class="button-group">
      <div class="glass-button" v-on:click="handleAdminLogin">
        <span>管理员</span>
      </div>
      <div class="glass-button" v-on:click="handleUserLogin">
        <span>用户</span>
      </div>
    </div>
    <el-button class="settings-btn" circle @click="showVideoList = !showVideoList">
      <el-icon><Setting /></el-icon>
    </el-button>
    <div v-if="showVideoList" class="video-list-panel">
      <div v-for="(video, index) in videoList" :key="index"
           class="video-item"
           :class="{active: currentVideo === video.src}"
           @click="selectVideo(video.src)">
        <video :src="video.src" muted autoplay loop playsinline></video>
        <div class="video-name">{{ video.name }}</div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue";
import {useRouter} from "vue-router";
import {ElMessage} from "element-plus";
import { Setting } from '@element-plus/icons-vue';
import girlVideo from "../asset/image/girl.mp4";
import xxVideo from "../asset/image/xx.mp4"
import inkVideo from "../asset/image/ink.mp4"
import rabbitVideo from "../asset/image/rabbit.mp4"
import hinata from "../asset/image/hinata.mp4"
import mc from "../asset/image/mc.mp4"

const router = useRouter();
const videoRef = ref(null);
const showVideoList = ref(false);
const currentVideo = ref(girlVideo);

const videoList = ref([
  { name: '默认', src: girlVideo },
  { name: '陈少波', src: xxVideo},
  { name: '水墨', src: inkVideo},
  { name: '流水线', src: rabbitVideo},
  { name: '雏田', src: hinata},
  { name: '我的世界', src: mc}
]);

onMounted(() => {
  const saved = localStorage.getItem('login_bg');
  if (saved) {
    currentVideo.value = saved;
    if (videoRef.value) {
      videoRef.value.load();
      videoRef.value.play();
    }
  }
});

const selectVideo = (src) => {
  currentVideo.value = src;
  localStorage.setItem('login_bg', src);
  showVideoList.value = false;
  if (videoRef.value) {
    videoRef.value.load();
    videoRef.value.play();
  }
  ElMessage.success('背景已切换');
};

const handleAdminLogin = () => {
  localStorage.setItem('isLoggedIn', 'true');
  localStorage.setItem('userRole', 'admin');
  ElMessage.success('管理员登录成功');
  router.push('/home');
};

const handleUserLogin = () => {
  localStorage.setItem('isLoggedIn', 'true');
  localStorage.setItem('userRole', 'user');
  ElMessage.success('用户登录成功');
  router.push('/home');
};
</script>

<style scoped>
.login-container {
  position: fixed;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 视频背景 */
.background-video {
  position: fixed;
  width: 100vw;
  height: 100vh;
  object-fit: cover;
  z-index: -1;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 30px;
  width: 100%;
  max-width: 300px;
}

.glass-button {
  padding: 25px 40px;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(2px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  width: 100%;
}

.glass-button:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
}

.settings-btn {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 100;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color:white;
}

.settings-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.video-list-panel {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(15px);
  border-radius: 12px;
  padding: 20px;
  z-index: 100;
  width: 80vw;
  max-width: 900px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.video-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  border: 3px solid transparent;
  aspect-ratio: 16/9;
}

.video-item:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.video-item.active {
  border-color: #409EFF;
  box-shadow: 0 0 20px rgba(64, 158, 255, 0.6);
}

.video-item video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-name {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  color: white;
  font-size: 13px;
  font-weight: bold;
  text-align: center;
}

</style>