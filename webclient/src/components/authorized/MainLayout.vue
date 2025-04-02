<script setup lang="ts">
import { RouterView, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";
import { useConversationsStore } from "@/stores/opened_chats";
import { prefetchMe } from "@/helpers/users";
import { onMounted, onUnmounted, ref, provide, computed, nextTick } from "vue";
import { eventBus } from "@/eventBus";
import {
  useFriendsStore,
  type FriendStateUpdate,
} from "@/stores/friends.store";
import type { Message } from "./MessageHandler/Messages.vue";
import type { DrawData } from "../WhiteBoard/Whiteboard.vue";
import Call from "../Call/Call.vue";
import {
  initPeerConnection,
  handleOffer,
  handleAnswer,
  handleIceCandidate,
} from "@/helpers/webrtc";
import router from "@/router/index.ts";

const authStore = useAuthStore();
const conversationsStore = useConversationsStore();
const friendStore = useFriendsStore();
const route = useRoute();

let ws: WebSocket | null = null;

const incomingCall = ref(false);
const activateWhiteboard = ref(false);
const isCalling = ref(false);
const incomingOffer = ref<RTCSessionDescriptionInit | null>(null);

const loading = ref(true);

const hasActiveChat = computed(() => {
  return conversationsStore.openedChatList.some(
    (chat) => chat.channel.channel_id === route.params.channelId
  );
});

function getChannelId() {
  return Array.isArray(route.params.channelId)
    ? route.params.channelId[0]
    : route.params.channelId;
}

async function handleCall() {
  const currentChannelId = getChannelId();

  const pc = initPeerConnection(sendWebsocketCommand, currentChannelId);

  const localStream = await navigator.mediaDevices.getUserMedia({
    audio: true,
    video: true,
  });

  localStream.getTracks().forEach((track) => {
    pc.addTrack(track, localStream);
  });

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  sendWebsocketCommand("call-invite", {
    channel_id: currentChannelId,
    offer,
  });

  isCalling.value = true;
}

function toggleWhiteboard() {
  activateWhiteboard.value = !activateWhiteboard.value;

  nextTick(() => {
    eventBus.showWhiteboard = activateWhiteboard.value;
    eventBus.whiteboardButtonText = activateWhiteboard.value
      ? "Close Whiteboard"
      : "Whiteboard";
  });
}

onMounted(async () => {
  await friendStore.fetchFriends();
  await conversationsStore.fetchConversations();
  await prefetchMe();
  openWebsocket();
  loading.value = false;
});

onUnmounted(() => {
  closeWebsocket();
});

function sendWebsocketCommand(command: string, data: any) {
  ws!.send(JSON.stringify({ cmd: command, data }));
}
provide("sendWebsocketCommand", sendWebsocketCommand);

function openWebsocket() {
  ws = new WebSocket("/api/ws");

  ws.onopen = () => {
    sendWebsocketCommand("login", { token: authStore.token });
  };

  ws.onmessage = (event) => {
    const messageObj = JSON.parse(event.data);

    if (messageObj.cmd === "message") {
      handleMessage(messageObj.data as Message);
    } else if (messageObj.cmd === "friend-state-update") {
      friendStore.updateFriendState(messageObj.data as FriendStateUpdate);
    } else if (messageObj.cmd === "whiteboard") {
      handleDrawing(messageObj.data as DrawData);
    } else if (messageObj.cmd === "call-invite") {
      incomingOffer.value = messageObj.data.offer;
      incomingCall.value = true;
    } else if (messageObj.cmd === "call-answer") {
      handleAnswer(messageObj.data.answer);
      isCalling.value = true;
    } else if (messageObj.cmd === "call-ice-candidate") {
      handleIceCandidate(messageObj.data.candidate);
    }
  };
}

function closeWebsocket() {
  if (ws) {
    ws.close();
    ws = null;
  }
}

async function handleMessage(message: Message) {
  let chat = conversationsStore.openedChatList.find(
    (c) => c.channel.channel_id == message.channel_id
  );

  if (chat && chat.channel.last_update < message.created_at) {
    chat.channel.last_update = message.created_at;
  }
}

async function handleDrawing(drawData: DrawData) {}

async function closeButton(channelId: string) {
  const success = await conversationsStore.closeOpenedChat(channelId);
  if (success && getChannelId() == channelId) {
    router.push("/friends");
  }
}

async function acceptCall() {
  incomingCall.value = false;
  const currentChannelId = getChannelId();

  const pc = initPeerConnection(sendWebsocketCommand, currentChannelId);

  const localStream = await navigator.mediaDevices.getUserMedia({
    audio: true,
    video: true,
  });

  // Add saját stream
  localStream.getTracks().forEach((track) => {
    pc.addTrack(track, localStream);
  });

  // Add meg a videónak (a saját kép megjelenítéséhez is hasznos lehet)
  const localVideo = document.getElementById("localVideo") as HTMLVideoElement;
  if (localVideo) {
    localVideo.srcObject = localStream;
  }

  await handleOffer(
    incomingOffer.value!,
    currentChannelId,
    sendWebsocketCommand
  );

  isCalling.value = true;
}

function declineCall() {
  incomingCall.value = false;
}
</script>

<template>
  <div v-if="!loading" class="app">
    <div class="sidebar-left">
      <div class="sidebar-section">
        <!--<div class="sidebar-header">Servers</div>
        <RouterLink class="add-btn" to="/servers">+</RouterLink>-->
      </div>
      <div class="sidebar-section">
        <div class="sidebar-header">
          <RouterLink class="sidebar-header" to="/friends">Friends</RouterLink>
          <RouterLink class="add-btn" to="/user-search">+</RouterLink>
        </div>
        <div class="opened-friend-chat">
          <div
            v-if="!conversationsStore.isLoading"
            v-for="(chat, id) in conversationsStore.openedChatList.sort(
              (a, b) => b.channel.last_update - a.channel.last_update
            )"
            :key="id"
            class="chat"
          >
            <RouterLink :to="`/chat/${chat.channel.channel_id}`">{{
              chat.users[0].username
            }}</RouterLink>

            <div v-if="chat.unread_count > 0" class="unread-message">
              {{ chat.unread_count > 9 ? "9+" : chat.unread_count }}
            </div>
            <button
              v-on:click="closeButton(chat.channel.channel_id)"
              class="close-button"
            >
              X
            </button>
          </div>
          <div v-else>Loading conversation list...</div>
        </div>
      </div>
    </div>

    <main class="content">
      <RouterView></RouterView>
    </main>

    <div class="sidebar-right">
      <header class="top-bar">
        <img class="avatar" src="@/assets/default.png" alt="User Avatar" />
        <div>
          {{ authStore.userinfo.username }}
        </div>
        <button class="icon-btn" aria-label="Microphone">
          <i class="icon mic-icon"></i>
        </button>
        <button class="icon-btn" aria-label="Profile">
          <i class="icon profile-icon"></i>
        </button>
        <button class="icon-btn" aria-label="Settings">
          <i class="icon settings-icon"></i>
        </button>
      </header>
      <button
        v-if="hasActiveChat"
        class="whiteboard-btn"
        @click="toggleWhiteboard"
      >
        {{ eventBus.whiteboardButtonText }}
      </button>
      <button v-if="!isCalling" @click="handleCall">Start Call</button>
      <div v-if="incomingCall" class="incoming-call">
        <p>Incoming call</p>
        <button @click="acceptCall">Accept</button>
        <button @click="declineCall">Decline</button>
      </div>
      <Call v-if="isCalling" />

      <button v-on:click="authStore.logout" class="logout-btn">Logout</button>
    </div>
  </div>
  <div v-else>Loading...</div>
</template>

<style scoped>
.whiteboard-btn {
  margin-top: 10px;
  border: none;
  background-color: hsla(160, 100%, 37%, 1);
  color: white;
  padding: 10px;
  cursor: pointer;
  border-radius: 5px;
}

.whiteboard-btn:hover {
  background-color: hsla(160, 100%, 27%, 1);
}

.opened-friend-chat {
  display: block;
}

.app {
  display: flex;
  height: 100vh;
  background-color: #1e1e2f;
  color: white;
}

.sidebar-left {
  width: 200px;
  background-color: #292b40;
  display: flex;
  flex-direction: column;
  padding: 10px;
  flex: 0 0 auto;
}
.sidebar-right {
  width: 200px;
  background-color: #292b40;
  display: flex;
  flex-direction: column;
  padding: 10px;
  flex: 0 0 auto;
  height: 100vh;
  cursor: default;
}

.sidebar-section {
  margin-bottom: 20px;
}

div.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

a.sidebar-header {
  font-size: 18px;
  font-weight: bold;
  background: none;
  color: #9a9aaf;
}
.sidebar-header:hover {
  color: rgb(87, 123, 223);
}
.add-btn {
  background: none;
  color: #9a9aaf;
  font-size: 30px;
  cursor: pointer;
}

.add-btn:hover {
  color: rgb(87, 123, 223);
}

.content {
  flex: 1;
  padding: 20px;
}

.top-bar {
  height: 50px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  background-color: #292b40;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
}

.icon-btn {
  background: none;
  border: none;
  color: #9a9aaf;
  font-size: 20px;
  cursor: pointer;
  margin-left: 10px;
}

.icon-btn:hover {
  color: white;
}

.close-button {
  margin-left: auto;
  background: none;
  border: none;
  color: hsla(160, 100%, 37%, 1);
}
.close-button:hover {
  color: white;
  cursor: pointer;
}

.logout-btn {
  margin-top: auto;
  border: none;
  background: none;
  color: white;
}
.logout-btn:hover {
  cursor: pointer;
  color: rgb(137, 115, 158);
}
.chat {
  display: flex;
}
.unread-message {
  background-color: red;
  color: white;
  font-size: 12px;
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 50%;
  min-width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  align-self: center;
}
</style>
