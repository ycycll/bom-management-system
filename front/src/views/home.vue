<template>
  <aside_navigation>
    <div style="width: 80%; margin-top: 200px; padding: 20px; margin-left: 120px">
      <el-carousel height="300px" motion-blur>
        <el-carousel-item v-for="item in cards" :key="item.title">
          <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 20px; box-sizing: border-box;">
            <h2 style="color: #475669; opacity: 0.75; margin: 0 0 15px 0; font-size: 24px; text-align: center; line-height: 1.5;">{{ item.title }}</h2>
            <p v-for="(desc, i) in item.descs" :key="i" style="color: #606266; margin: 5px 0; font-size: 16px;">{{ desc }}</p>
          </div>
        </el-carousel-item>
      </el-carousel>
    </div>
  </aside_navigation>
</template>

<script setup>
import { ref } from 'vue';
import aside_navigation from '../component/navigation.vue';

let cards = ref([
  {
    title: 'V1.2 更新内容',
    descs: ['模型优化', '推荐条目增加']
  },
  {
    title: 'V2.0敬请期待',
    descs: ['更智能', '更便捷', '更现代化', '引入Gemini']
  },
  {
    title: 'Defog 新功能',
    descs: ['RAG技术集成', '自然语言解析', '合同摘要']
  },
  {
    title: 'Hub 管理',
    descs: ['数据视窗']
  }
]);
</script>