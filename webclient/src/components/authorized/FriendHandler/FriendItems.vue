<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { fetchWrapper } from '@/helpers/fetch-wrapper';
import { isSuccess } from '@/helpers/result';
import Friend from '@/components/authorized/FriendHandler/Friend.vue'

const {endpoint, actions, clickable} = defineProps<{
  endpoint: string,
  actions: Record<string, (user: any) => void>
  clickable: boolean
}>();

const users = ref<any[]>([]);

async function getUsers() {
  try {
    const response = await fetchWrapper.get(endpoint);
    if (isSuccess(response)) {
      users.value = response.value;
    } else {
      console.error("Failed to fetch list:", response);
    }
  } catch (error) {
    console.error("Error while fetching list:", error);
  }
}

function removeUser(user: any){
  users.value = users.value.filter(u => u.userid !== user.userid);
}

defineExpose({getUsers, removeUser});

onMounted(() => {
  getUsers();
});

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
