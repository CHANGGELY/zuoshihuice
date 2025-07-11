<template>
  <div class="test-view">
    <h1>测试页面</h1>
    <p>如果你能看到这个页面，说明Vue组件正常工作</p>
    <el-button type="primary">测试按钮</el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const message = ref('Hello World')
</script>

<style scoped>
.test-view {
  padding: 20px;
  text-align: center;
}
</style>
