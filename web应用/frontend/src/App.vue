<template>
  <div id="app" class="app-container">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(async () => {
  console.log('App mounted successfully')

  // 延迟初始化stores，避免阻塞页面渲染
  try {
    const { useSystemStore } = await import('@/stores/system')
    const { useAuthStore } = await import('@/stores/auth')

    const systemStore = useSystemStore()
    const authStore = useAuthStore()

    // 初始化认证状态
    await authStore.initAuth()

    // 初始化系统信息
    systemStore.fetchSystemInfo()

    // 初始化主题
    systemStore.initTheme()

    console.log('Stores initialized successfully')
  } catch (error) {
    console.error('Failed to initialize stores:', error)
  }
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
