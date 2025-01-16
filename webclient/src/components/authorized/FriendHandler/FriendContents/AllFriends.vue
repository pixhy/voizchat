<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { fetchWrapper } from '@/helpers/fetch-wrapper';
import { isSuccess } from '@/helpers/result';
import Friend from '@/components/authorized/FriendHandler/Friend.vue'
import FriendNavigation from '../FriendNavigation.vue';

const friends = ref<any[]>([]);

async function getFriends() {
  try {
    const response = await fetchWrapper.get(`/api/user/get-friends`);
    if (isSuccess(response)) {
      friends.value = response.value;
    } else {
      console.error("Failed to fetch friends:", response);
    }
  } catch (error) {
    console.error("Error while fetching friends:", error);
  }
}

async function removeFriend(user: any){
  const response = await fetchWrapper.post(`/api/user/remove-friend/${user.userid}`);
  if (response.success) {
    console.log("friend removed");
    friends.value = friends.value.filter(u => u.userid !== user.userid)
  }
  else {
    console.log(response.error.status)
  }
};

onMounted(() => {
  getFriends();
});

</script>


<template>
  <FriendNavigation />
  <div v-if="friends.length > 0">
    <Friend v-for="friend in friends" :user="friend" action="Remove friend" :actionFunction="removeFriend"/>
  </div>
  <div v-else>
    <p>No friends found.</p>
  </div>
</template>

<style>

h2 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #ddd;
}

li:last-child {
  border-bottom: none;
}

p {
  font-size: 1rem;
  color: #666;
}
</style>
