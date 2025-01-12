import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/home',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../components/Login.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../components/Register.vue'),
    },
    {
      path: '/account-recovery',
      name: 'account-recovery',
      component: () => import('../components/ForgottenPassword.vue'),
    },
    {
      path: '/',
      name: 'main',
      component: () => import('../components/authorized/MainLayout.vue'),
      children: [
        {
          path: '', 
          component: () => import('../components/EmptyComponent.vue')
        },
        {
          path: '/search',
          name: 'search',
          component: () => import('../components/authorized/UserSearch.vue')
        }
      ]
    },
    {
      path: '/verify/:code',
      name: 'verify',
      component: () => import('../components/VerifyCode.vue'),
    },
  ],
})

export default router
