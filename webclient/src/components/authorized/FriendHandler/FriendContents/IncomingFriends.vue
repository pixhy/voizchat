<script setup lang="ts">
import { ref } from 'vue';
import FriendNavigation from '../FriendNavigation.vue';
import FriendItems from '../FriendItems.vue'
import {addFriend, removeFriend} from './_common'

const incomingFriends = ref<any | null>(null);

const actions = {
  '✓': (user: any) => addFriend(user, incomingFriends),
  'X': (user: any) => removeFriend(user, incomingFriends),
};

</script>

<template>
  <FriendNavigation />
  <FriendItems
   endpoint="/api/user/incoming-friend-requests"
   :actions="actions"
   ref="incomingFriends">
    <template #empty>
      No pending requests.
    </template>
  </FriendItems>
</template>