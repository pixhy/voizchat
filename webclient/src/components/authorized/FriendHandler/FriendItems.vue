<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { fetchWrapper } from '@/helpers/fetch-wrapper';
import { isSuccess } from '@/helpers/result';
import Friend from '@/components/authorized/FriendHandler/Friend.vue'
import { type FriendAction } from './FriendContents/_common';
import { type User } from '@/helpers/users'

const {users, actions, clickable} = defineProps<{
  users: User[],
  actions: FriendAction[],
  clickable: boolean
}>();

</script>


<template>
  <div v-if="users.length > 0">
    <Friend v-for="friend in users" :user="friend" :actions="actions" :clickable="clickable"/>
  </div>
  <div v-else>
    <p class="no-items">
      <slot name="empty"></slot>
    </p>
  </div>
</template>

<style>

.no-items {
  font-size: 1rem;
  color: #666;
}
</style>
