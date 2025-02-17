<script setup lang="ts">
import { ref } from 'vue';
import FriendNavigation from '../FriendNavigation.vue';
import FriendItems from '../FriendItems.vue'
import { removeFriend, FriendAction } from './_common'
import { useFriendsStore } from '@/stores/friends.store';

const actions = [
  new FriendAction('Remove friend', removeFriend, false),
]

const friendsStore = useFriendsStore();


</script>


<template>
  <FriendNavigation />
  <FriendItems
    :users="friendsStore.friendList"
    :actions="actions"
    :clickable="true">
    <template #empty>
      No friends found.
    </template>
  </FriendItems>
</template>
