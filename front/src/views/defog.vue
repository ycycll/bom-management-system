<template>
  <aside_navigation>
    <div class="defog-container">
      <div class="defog-header">
        <h1 class="defog-title">DEFOG - MODEL - ZERO</h1>
        <p class="defog-subtitle">输入自然语言合同要求，自动提炼技术准备关键词</p>
      </div>

      <div class="chat-container">
        <div class="chat-messages" ref="messagesContainer">
          <div v-for="(msg, index) in messages" :key="index" class="message-wrapper">
            <div :class="['message', msg.type === 'user' ? 'user-message' : 'bot-message']">
              <div class="message-avatar">
                <el-icon v-if="msg.type === 'user'"><User /></el-icon>
                <el-icon v-else><ChatDotRound /></el-icon>
              </div>
              <div class="message-content">
                <div class="message-text">{{ msg.content }}</div>
                <div v-if="msg.output" class="message-result">
                  <div class="result-label">技术准备：</div>
                  <div class="result-tags">
                    <span v-for="(tag, i) in msg.output.split(',')" :key="i" class="result-tag bot1-tag">
                      {{ tag }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-if="loading" class="message-wrapper">
            <div class="message bot-message">
              <div class="message-avatar">
                <el-icon><ChatDotRound /></el-icon>
              </div>
              <div class="message-content">
                <div class="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="chat-input">
          <el-input
              v-model="inputText"
              type="textarea"
              :rows="3"
              placeholder="请输入技术要求，例如：SKF 轴承，金属风扇，电机需配置多点固定防雨罩..."
              @keyup.ctrl.enter="sendQuery"
              class="input-area"
          ></el-input>
          <el-tooltip content="上传附件" placement="top">
            <el-button
                :icon="Paperclip"
                circle
                @click="triggerFileUpload"
                class="attach-btn"
            />
          </el-tooltip>
          <input
              ref="fileInput"
              type="file"
              accept=".pdf,.doc,.docx"
              style="display: none"
              @change="handleFileSelect"
          />
          <div v-if="selectedFile" class="file-tag">
            <el-icon><Document /></el-icon>
            <span>{{ selectedFile.name }}</span>
            <el-icon class="close-icon" @click="clearFile"><Close /></el-icon>
          </div>
          <el-button type="primary" @click="sendQuery" :loading="loading" class="send-btn">
            <el-icon><Promotion /></el-icon>
            发送
          </el-button>
        </div>
      </div>
    </div>
  </aside_navigation>
</template>

<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { User, ChatDotRound, Promotion, Paperclip, Document, Close } from '@element-plus/icons-vue';
import aside_navigation from '../component/navigation.vue';

let inputText = ref('');
let messages = ref([]);
let loading = ref(false);
let messagesContainer = ref(null);
let fileInput = ref(null);
let selectedFile = ref(null);

let triggerFileUpload = () => {
  fileInput.value?.click();
};

let handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
    ElMessage.success(`已选择: ${file.name}`);
  }
};

let clearFile = () => {
  selectedFile.value = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

// 页面加载时恢复对话
onMounted(() => {
  let savedMessages = localStorage.getItem('defog_messages');
  if (savedMessages) {
    messages.value = JSON.parse(savedMessages);
    nextTick(() => scrollToBottom());
  }
});

// 页面离开时保存对话
onBeforeUnmount(() => {
  if (messages.value.length > 0) {
    localStorage.setItem('defog_messages', JSON.stringify(messages.value));
  }
});

let sendQuery = async () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请输入技术要求');
    return;
  }

  messages.value = [];

  let userMessage = {
    type: 'user',
    content: inputText.value + (selectedFile.value ? ` [${selectedFile.value.name}]` : '')
  };
  messages.value.push(userMessage);

  loading.value = true;
  let query = inputText.value;
  inputText.value = '';

  await nextTick();
  scrollToBottom();

  try {
    let response;

    if (selectedFile.value) {
      const formData = new FormData();
      formData.append('query', query);
      formData.append('file', selectedFile.value);

      response = await axios.post('/api/defog/question', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    } else {
      response = await axios.post('/api/defog/question', { query });
    }

    if (response.data.code === 200) {
      messages.value.push({
        type: 'bot',
        content: '解析完成：',
        output: response.data.output
      });
    } else {
      messages.value.push({
        type: 'bot',
        content: '查询失败：' + (response.data.message || '未知错误')
      });
    }

    clearFile();
  } catch (error) {
    messages.value.push({
      type: 'bot',
      content: '查询失败：' + (error.response?.data?.detail || error.message)
    });
  } finally {
    loading.value = false;
    await nextTick();
    scrollToBottom();
  }
};

let scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};
</script>

<style scoped>
.defog-container {
  height: 98vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2px;
  box-sizing: border-box;
}

.defog-header {
  text-align: center;
  color: white;
  margin-bottom: 20px;
}

.defog-title {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.defog-subtitle {
  font-size: 14px;
  opacity: 0.9;
  margin-top: 8px;
}

.chat-container {
  width: 70%;
  height: 60vh;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
  background: #f8f9fa;
}

.message-wrapper {
  margin-bottom: 16px;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.user-message .message-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.bot-message .message-avatar {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: white;
}

.message-content {
  max-width: 70%;
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.user-message .message-content {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.message-text {
  line-height: 1.5;
  word-break: break-word;
}

.message-result {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.result-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.result-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.result-tag {
  background: linear-gradient(135deg, #e0c3fc, #8ec5fc);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.bot1-tag {
  background: linear-gradient(135deg, #fef3c7, #fcd34d);
  color: #92400e;
}

.bot2-tag {
  background: linear-gradient(135deg, #ede9fe, #c4b5fd);
  color: #5b21b6;
}

.copy-btn {
  margin-top: 8px;
}

.loading-dots {
  display: flex;
  gap: 6px;
  padding: 8px 0;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.chat-input {
  padding: 16px;
  background: white;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.attach-btn {
  flex-shrink: 0;
}

.file-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 20px;
  font-size: 13px;
  color: #0369a1;
  max-width: 200px;
}

.file-tag .close-icon {
  cursor: pointer;
  font-size: 14px;
  color: #999;
}

.file-tag .close-icon:hover {
  color: #ef4444;
}

.input-area {
  flex: 1;
}

.send-btn {
  height: 40px;
  padding: 0 24px;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>