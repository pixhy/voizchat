<script setup lang="ts">
import FriendNavigation from '../FriendNavigation.vue';
import { ref, onMounted } from 'vue';

const friends = ref<any[]>([]);
</script>

<template>
  <FriendNavigation />
</template>

<style></style>