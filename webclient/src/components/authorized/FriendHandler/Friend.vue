<script setup lang="ts">
import { RouterLink } from 'vue-router';

const {user, actions, clickable} = defineProps<{
  user: any,
  actions: Record<string, (user: any) => void>,
  clickable: boolean
}>();

</script>

<template>

  <div class="user">
    <img class="avatar" src="@/assets/default.png" alt="User Avatar" width="40"/>
    <div class="username" :title="user.username">
      <RouterLink v-if="clickable" :to="`/chat-user/${user.userid}`">{{ user.username }}</RouterLink>
      <span v-else>{{ user.username }}</span>
    </div>
    <div>
      <button
        v-for="[buttonText, callback] in Object.entries(actions)"
        class="action-button"
        v-on:click="callback(user)">
          {{ buttonText }}
      </button>
    </div>
  </div>
</template>

<style>

.user {
  margin-top: 25px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  width: 320px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  background-color: rgb(74, 95, 116);
  grid-template-columns: auto 1fr auto;
  display: grid;
  align-items: center;
}

.username {
  justify-self: center;
  margin: 3px;
  max-width: 170px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-button {
  padding: 8px;
  font-size: 14px;
  color: white;
  background-color: #28a745;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.2s;
  height: 37px;
  min-width: 37px;
  margin-left: 5px;
}

.action-button:hover {
  background-color: #218838;
}
</style>
