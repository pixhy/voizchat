<script setup lang="ts">
import { ref } from 'vue';
import FriendNavigation from '../FriendNavigation.vue';
import FriendItems from '../FriendItems.vue'
import {addFriend, removeFriend} from './_common'
import { FriendAction } from './_common';
import { useFriendsStore } from '@/stores/friends.store';

const friendsStore = useFriendsStore();

const actions = [
  new FriendAction('✓', addFriend, false),
  new FriendAction('X', removeFriend, false),
];

</script>

<template>
  <FriendNavigation />
  <FriendItems
   :users="friendsStore.incomingFriendRequests"
   :actions="actions"
   :clickable="false">
    <template #empty>
      No pending requests.
    </template>
  </FriendItems>
</template>