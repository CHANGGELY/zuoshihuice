<template>
  <div class="login-view">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1>永续合约做市策略回测平台</h1>
          <p>专业的交易策略回测分析平台</p>
        </div>
        
        <el-tabs v-model="activeTab" class="login-tabs">
          <!-- 登录表单 -->
          <el-tab-pane label="登录" name="login">
            <el-form
              ref="loginFormRef"
              :model="loginForm"
              :rules="loginRules"
              label-width="0"
              size="large"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="loginForm.username"
                  placeholder="用户名"
                  clearable
                />
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="密码"
                  show-password
                  clearable
                  @keyup.enter="handleLogin"
                />
              </el-form-item>
              
              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  :loading="loading"
                  @click="handleLogin"
                  block
                >
                  {{ loading ? '登录中...' : '登录' }}
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <!-- 注册表单 -->
          <el-tab-pane label="注册" name="register">
            <el-form
              ref="registerFormRef"
              :model="registerForm"
              :rules="registerRules"
              label-width="0"
              size="large"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="用户名"
                  clearable
                />
              </el-form-item>

              <el-form-item prop="email">
                <el-input
                  v-model="registerForm.email"
                  placeholder="邮箱"
                  clearable
                />
              </el-form-item>
              
              <el-form-item prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="密码"
                  show-password
                  clearable
                />
              </el-form-item>

              <el-form-item prop="confirmPassword">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="确认密码"
                  show-password
                  clearable
                  @keyup.enter="handleRegister"
                />
              </el-form-item>
              
              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  :loading="loading"
                  @click="handleRegister"
                  block
                >
                  {{ loading ? '注册中...' : '注册' }}
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
        
        <div class="login-footer">
          <p>© 2024 永续合约做市策略回测平台. All rights reserved.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

// Router
const router = useRouter()

// 简化的状态管理
const loading = ref(false)
const isAuthenticated = ref(false)

// 响应式数据
const activeTab = ref('login')
const loginFormRef = ref()
const registerFormRef = ref()

// 登录表单
const loginForm = reactive({
  username: '',
  password: ''
})

// 注册表单
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 方法
const handleLogin = async () => {
  try {
    await loginFormRef.value.validate()

    // 简化的登录逻辑
    loading.value = true

    // 模拟登录请求
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('登录成功')
    router.push('/trading')

  } catch (error) {
    if (error !== false) { // 不是表单验证错误
      ElMessage.error(error.message || '登录失败')
    }
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  try {
    await registerFormRef.value.validate()

    // 简化的注册逻辑
    loading.value = true

    // 模拟注册请求
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('注册成功')
    router.push('/trading')

  } catch (error) {
    if (error !== false) { // 不是表单验证错误
      ElMessage.error(error.message || '注册失败')
    }
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  // 如果已经登录，直接跳转到主页
  if (isAuthenticated.value) {
    router.push('/')
  }
})
</script>

<style lang="scss" scoped>
.login-view {
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.login-header {
  padding: 32px 32px 24px;
  text-align: center;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
  
  h1 {
    margin: 0 0 8px 0;
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    
    .el-icon {
      color: var(--binance-yellow);
    }
  }
  
  p {
    margin: 0;
    font-size: 14px;
    color: var(--text-secondary);
  }
}

.login-tabs {
  padding: 24px 32px;
  
  :deep(.el-tabs__header) {
    margin: 0 0 24px 0;
    
    .el-tabs__nav-wrap {
      &::after {
        background: var(--border-color);
      }
    }
    
    .el-tabs__item {
      color: var(--text-secondary);
      font-weight: 500;
      
      &.is-active {
        color: var(--binance-yellow);
      }
    }
    
    .el-tabs__active-bar {
      background: var(--binance-yellow);
    }
  }
  
  :deep(.el-form-item) {
    margin-bottom: 20px;
    
    .el-input {
      .el-input__wrapper {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        
        &:hover {
          border-color: var(--binance-yellow);
        }
        
        &.is-focus {
          border-color: var(--binance-yellow);
          box-shadow: 0 0 0 2px rgba(252, 213, 53, 0.2);
        }
      }
      
      .el-input__inner {
        color: var(--text-primary);
        
        &::placeholder {
          color: var(--text-tertiary);
        }
      }
    }
  }
  
  .el-button--primary {
    background: var(--binance-yellow);
    border-color: var(--binance-yellow);
    color: var(--bg-primary);
    font-weight: 600;
    
    &:hover {
      background: lighten(var(--binance-yellow), 10%);
      border-color: lighten(var(--binance-yellow), 10%);
    }
  }
}

.login-footer {
  padding: 16px 32px;
  text-align: center;
  background: var(--bg-primary);
  border-top: 1px solid var(--border-color);
  
  p {
    margin: 0;
    font-size: 12px;
    color: var(--text-tertiary);
  }
}

// 响应式设计
@media (max-width: 480px) {
  .login-view {
    padding: 12px;
  }
  
  .login-header {
    padding: 24px 20px 16px;
    
    h1 {
      font-size: 18px;
    }
  }
  
  .login-tabs {
    padding: 20px;
  }
  
  .login-footer {
    padding: 12px 20px;
  }
}
</style>
