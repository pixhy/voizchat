import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useAuthStore } from '@/stores/auth.store';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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
        },
        {
          path: '/friends',
          name: 'friends',
          component: () => import('../components/authorized/FriendHandler/FriendContents/AllFriends.vue')
        },
        {
          path: '/friends/incoming',
          name: 'friends-incoming',
          component: () => import('../components/authorized/FriendHandler/FriendContents/IncomingFriends.vue')
        },
        {
          path: '/friends/outgoing',
          name: 'friends-outgoing',
          component: () => import('../components/authorized/FriendHandler/FriendContents/OutgoingFriends.vue')
        }
      ]
    },
  ],
})

export default router
