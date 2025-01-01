<template>
  <div class="app">
    <div class="sidebar-left">
      <div class="sidebar-section">
        <div class="sidebar-header">Servers</div>
        <button class="add-btn">+</button>
      </div>
      <div class="sidebar-section">
        <div class="sidebar-header">Friends</div>
        <button class="add-btn">+</button>
      </div>
    </div>

    <main class="content">
      <!-- Main content goes here -->
    </main>

    <div class="sidebar-right">
      <header class="top-bar">
        <img class="avatar" src="@/assets/default.png" alt="User Avatar" />
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
  
<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Messages',
});
</script>

<style scoped>
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.sidebar-header {
  font-size: 18px;
  font-weight: bold;
}

.add-btn {
  background: none;
  border: none;
  color: #9A9AAF;
  font-size: 20px;
  cursor: pointer;
}

.add-btn:hover {
  color: white;
}

.content {
  flex: 1;
  padding: 20px;
}

.top-bar {
  position: absolute;
  top: 0;
  height: 50px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  background-color: #292B40;
  width: calc(100% - 200px);
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
