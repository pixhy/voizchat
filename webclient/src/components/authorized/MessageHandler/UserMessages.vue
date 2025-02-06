<script setup lang="ts">

import { onMounted } from 'vue';
import { useRoute } from 'vue-router';
import router from '@/router/index.ts'
import { useConversationsStore } from '@/stores/opened_chats'

const route = useRoute();
const userId = Array.isArray(route.params.userId) ? route.params.userId[0] : route.params.userId;


onMounted(async () => {
    const conversationsStore = useConversationsStore();
    const openedChat = await conversationsStore.openOpenedChatWithUser(userId);
    router.push(`/chat/${openedChat.channel.channel_id}`);
});

</script>
<template>
    Requesting user channel
</template>