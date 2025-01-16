<script setup lang="ts">

const {user, actions} = defineProps(['user', 'actions']);

</script>

<template>

  <div class="user">
    <img class="avatar" src="@/assets/default.png" alt="User Avatar" width="40"/>
    <div class="username">{{ user.username }}</div>
    <div>
      <!--<button v-for="?" class="action-button" v-on:click="actionFunction(user)">
        {{ action }}
      </button>-->
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
}

.friend-request-button:hover {
  background-color: #218838;
}
</style>