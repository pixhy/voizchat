<script setup lang="ts">
import { ref } from 'vue';
import FriendNavigation from '../FriendNavigation.vue';
import FriendItems from '../FriendItems.vue'
import { removeFriend } from './_common'

const outgoingFriends = ref<any | null>(null);

const actions = {
  'X': (user: any) => removeFriend(user, outgoingFriends),
};

</script>

<template>
  <FriendNavigation />
  <FriendItems
   endpoint="/api/user/outgoing-friend-requests"
   :actions="actions"
   :clickable="false"
   ref="outgoingFriends">
    <template #empty>
      No pending requests.
    </template>
  </FriendItems>
</template>