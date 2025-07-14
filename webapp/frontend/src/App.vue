<template>
  <div id="app" class="app-container">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  console.log('App mounted successfully')
  // 暂时禁用stores初始化，避免后端连接问题影响页面显示
})
</script>

<style lang="scss">
.app-container {
  width: 100%;
  height: 100vh;
  background: var(--el-bg-color);
  color: var(--el-text-color-primary);
}

// 全局滚动条样式
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--el-border-color-lighter);
}

::-webkit-scrollbar-thumb {
  background: var(--el-border-color);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--el-border-color-dark);
}
</style>
