import { createRouter, createWebHistory } from 'vue-router'
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
      path: '/verify/:code',
      name: 'verify',
      component: () => import('../components/VerifyCode.vue'),
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: () => import('../components/ResetPassword.vue'),
      beforeEnter: (to, from, next) => {
        const email = to.query.email
        const code = to.query.code
    
        if (email && code) {
          next()
        } else {
          next({ name: 'account-recovery' })
        }
      }
    },
    {
      path: '/',
      name: 'main',
      beforeEnter: (to, from, next) => { 
        if(!useAuthStore().token){
          router.push('/login');
        }
        next();
      },
      component: () => import('../components/authorized/MainLayout.vue'),
      children: [
        {
          path: '', 
          name: 'empty',
          component: () => import('../components/EmptyComponent.vue')
        },
        {
          path: '/user-search',
          name: 'user-search',
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
        },
        {
          path: '/chat-user/:userId',
          name: 'chat-user',
          component: () => import('../components/authorized/MessageHandler/UserMessages.vue')
        },
        {
          path: '/chat/:channelId',
          name: 'chat-channel',
          component: () => import('../components/authorized/MessageHandler/Messages.vue')
        }
      ]
    },
  ],
})

export default router
