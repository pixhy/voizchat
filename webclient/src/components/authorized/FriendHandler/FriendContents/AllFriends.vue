<script setup lang="ts">
import { ref } from 'vue';
import FriendNavigation from '../FriendNavigation.vue';
import FriendItems from '../FriendItems.vue'
import { removeFriend } from './_common'

const allFriends = ref<any | null>(null);

const actions = {
  'Remove friend': (user: any) => removeFriend(user, allFriends),
};

</script>


<template>
  <FriendNavigation />
  <FriendItems
    endpoint="/api/user/get-friends"
    :actions="actions"
    ref="allFriends">
    <template #empty>
      No friends found.
    </template>
  </FriendItems>
</template>
