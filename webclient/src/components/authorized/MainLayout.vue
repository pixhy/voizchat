<script setup lang="ts">
import { RouterView } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import { useConversationsStore } from '@/stores/opened_chats'
import { onMounted } from 'vue';

const authStore = useAuthStore();
const conversationsStore = useConversationsStore();

onMounted( async () => {
  await conversationsStore.fetchConversations();
})

</script>


<template>
  <div class="app">
    <div class="sidebar-left">
      <div class="sidebar-section">
        <!--<div class="sidebar-header">Servers</div>
        <RouterLink class="add-btn" to="/servers">+</RouterLink>-->
      </div>
      <div class="sidebar-section">
        <div class="sidebar-header">
          <RouterLink class="sidebar-header" to="/friends">Friends</RouterLink>
          <RouterLink class="add-btn" to="/user-search">+</RouterLink>
        </div>
        <div class="opened-friend-chat">
          <div v-for="chat, id in conversationsStore.list" :key="id">
            <RouterLink :to="`/chat/user/${chat.userid}`">{{ chat.username }}</RouterLink>

          </div>
        </div>
      </div>

    </div>

    <main class="content">
      <RouterView></RouterView>
    </main>

    <div class="sidebar-right">
      <header class="top-bar">
        <img class="avatar" src="@/assets/default.png" alt="User Avatar" />
        <div>
          {{ authStore.userinfo.username }}
        </div>
        <button class="icon-btn" aria-label="Microphone">
          <i class="icon mic-icon"></i>
        </button>
        <button class="icon-btn" aria-label="Profile">
          <i class="icon profile-icon"></i>
        </button>
        <button class="icon-btn" aria-label="Settings">
          <i class="icon settings-icon"></i>
        </button>
      </header>
    </div>
  </div>
</template>
  

<style scoped>

.opened-friend-chat {
  display: block;
}

.app {
  display: flex;
  height: 100vh;
  background-color: #1E1E2F;
  color: white;
}

.sidebar-left {
  width: 200px;
  background-color: #292B40;
  display: flex;
  flex-direction: column;
  padding: 10px;
  flex: 0 0 auto;
}
.sidebar-right {
  width: 200px;
  background-color: #292B40;
  display: flex;
  flex-direction: column;
  padding: 10px;
  flex: 0 0 auto;
}

.sidebar-section {
  margin-bottom: 20px;
}

div.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

a.sidebar-header {
  font-size: 18px;
  font-weight: bold;
  background: none;
  color: #9A9AAF;
}
.sidebar-header:hover{
  color: rgb(87, 123, 223)
}
.add-btn {
  background: none;
  color: #9A9AAF;
  font-size: 30px;
  cursor: pointer;
}

.add-btn:hover {
  color: rgb(87, 123, 223)
}

.content {
  flex: 1;
  padding: 20px;
}

.top-bar {
  height: 50px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  background-color: #292B40;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
}

.icon-btn {
  background: none;
  border: none;
  color: #9A9AAF;
  font-size: 20px;
  cursor: pointer;
  margin-left: 10px;
}

.icon-btn:hover {
  color: white;
}
</style>
