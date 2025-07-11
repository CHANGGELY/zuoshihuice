import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/SimpleLoginView.vue'),
      meta: {
        title: '登录',
        requiresAuth: false
      }
    },
    {
      path: '/',
      name: 'home',
      redirect: '/trading',
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/trading',
      name: 'trading',
      component: () => import('@/views/SimpleTradingView.vue'),
      meta: {
        title: '交易图表',
        icon: 'TrendCharts',
        requiresAuth: false
      }
    },
    {
      path: '/backtest',
      name: 'backtest',
      component: () => import('@/views/SimpleBacktestView.vue'),
      meta: {
        title: '策略回测',
        icon: 'DataAnalysis',
        requiresAuth: false
      }
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: () => import('@/views/SimpleAnalysisView.vue'),
      meta: {
        title: '结果分析',
        icon: 'PieChart',
        requiresAuth: false
      }
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/SimpleSettingsView.vue'),
      meta: {
        title: '系统设置',
        icon: 'Setting',
        requiresAuth: false
      }
    },
    {
      path: '/test',
      name: 'test',
      component: () => import('@/views/TestView.vue'),
      meta: {
        title: '测试页面',
        requiresAuth: false
      }
    }
  ]
})

// 简化的路由守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 永续合约做市策略回测平台`
  }

  // 暂时跳过认证检查，直接允许访问
  next()
})

export default router
