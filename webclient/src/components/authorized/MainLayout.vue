<script setup lang="ts">
import { RouterView } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";
import { useConversationsStore } from "@/stores/opened_chats";
import { prefetchMe } from "@/helpers/users";
import {
  onMounted,
  onUnmounted,
  ref,
  provide,
  computed,
  nextTick,
  inject,
} from "vue";
import { type Message } from "./MessageHandler/Messages.vue";
import { useRoute } from "vue-router";
import router from "@/router/index.ts";
import { eventBus } from "@/eventBus";
import {
  useFriendsStore,
  type FriendStateUpdate,
} from "@/stores/friends.store";
import Whiteboard, { type DrawData } from "../WhiteBoard/Whiteboard.vue";

import Call from "../Call/Call.vue";
import {
  startCall,
  handleOffer,
  handleAnswer,
  handleIceCandidate,
  endCall,
} from "@/helpers/webrtc";
const authStore = useAuthStore();
let conversationsStore = useConversationsStore();
const friendStore = useFriendsStore();
const route = useRoute();
let ws: WebSocket | null = null;

const activateWhiteboard = ref<boolean>(false);
const isCalling = ref<boolean>(false);
const incomingCall = ref<boolean>(false);
const outGoingCall = ref<boolean>(false);
const incomingOffer = ref<RTCSessionDescriptionInit | null>(null);

function getChannelId() {
  let currentChannelId = Array.isArray(route.params.channelId)
    ? route.params.channel_id[0]
    : route.params.channelId;
  console.log(currentChannelId);
  return currentChannelId;
}

const loading = ref<boolean>(true);

const hasActiveChat = computed(() => {
  return conversationsStore.openedChatList.some(
    (chat) => chat.channel.channel_id === route.params.channelId
  );
});

function toggleWhiteboard() {
  console.log("Toggling whiteboard. Current state:", activateWhiteboard.value);
  activateWhiteboard.value = !activateWhiteboard.value;

  nextTick(() => {
    eventBus.showWhiteboard = activateWhiteboard.value;
    eventBus.whiteboardButtonText = activateWhiteboard.value
      ? "Close Whiteboard"
      : "Whiteboard";
    console.log("Updated whiteboard state:", eventBus.showWhiteboard);
  });
}

onMounted(async () => {
  console.log("MainLayout mounted");
  if (loading.value == false) {
    console.log("loading is already false THIS IS BAD!");
  }
  await friendStore.fetchFriends();
  await conversationsStore.fetchConversations();
  console.log("fetchConversations done");
  await prefetchMe();
  console.log("prefetchMe done");
  openWebsocket();
  loading.value = false;
});

onUnmounted(async () => {
  closeWebsocket();
});

function sendWebsocketCommand(command: string, data: any) {
  ws!.send(JSON.stringify({ cmd: command, data: data }));
}
provide("sendWebsocketCommand", sendWebsocketCommand);

function openWebsocket() {
  ws = new WebSocket("/api/ws");
  ws.onopen = function (event) {
    console.log("onopen");
    sendWebsocketCommand("login", { token: useAuthStore().token });
  };

  ws.onmessage = function (event) {
    const messageObj = JSON.parse(event.data);
    console.log(messageObj);
    if (messageObj.cmd === "message") {
      handleMessage(messageObj.data as Message);
    } else if (messageObj.cmd === "friend-state-update") {
      friendStore.updateFriendState(messageObj.data as FriendStateUpdate);
    } else if (messageObj.cmd === "whiteboard") {
      handleDrawing(messageObj.data as DrawData);
    } else if (messageObj.cmd === "call-invite") {
      console.log("Received call-invite", messageObj);
      console.log("handleOffer function:", handleOffer);
      incomingOffer.value = messageObj.data.offer;
      incomingCall.value = true;
    } else if (messageObj.cmd === "call-answer") {
      handleAnswer(messageObj.data.answer);
      outGoingCall.value = false;
    } else if (messageObj.cmd === "call-end") {
      console.log("Call ended by remote peer");
      endCall();
      isCalling.value = false;
      incomingCall.value = false;
      incomingOffer.value = null;
      isCalling.value = false;
    } else if (messageObj.type === "call-ice-candidate") {
      handleIceCandidate(messageObj.data.candidate);
    }
  };

  ws.onclose = async function (e) {
    console.log("onclose", e);
  };

  ws.onerror = async function (e) {
    console.log("onerror", e);
  };
}

function closeWebsocket() {
  if (ws) {
    ws.close();
    ws = null;
  }
}

type MessageHandler = (message: Message) => {};
const messageHandler = ref<MessageHandler | null>(null);
async function handleMessage(message: Message) {
  let chat = conversationsStore.openedChatList.find(
    (c) => c.channel.channel_id == message.channel_id
  );

  if (chat && chat.channel.last_update < message.created_at) {
    chat.channel.last_update = message.created_at;
  }

  if (messageHandler.value && messageHandler.value(message)) {
    return; // message was handled by active Messages component
  }

  console.log("background message: ", message);
  if (!chat) {
    chat = await conversationsStore.openOpenedChat(message.channel_id);
  }
  chat.unread_count++;
}

provide("setMessageHandler", (h: MessageHandler) => {
  messageHandler.value = h;
});

type DrawHandler = (drawData: DrawData) => {};
const drawHandler = ref<DrawHandler | null>(null);
async function handleDrawing(drawData: DrawData) {
  if (drawHandler.value && drawHandler.value(drawData)) {
    return;
  }
}
provide("setWhiteBoardHandler", (h: DrawHandler) => {
  drawHandler.value = h;
});

async function handleCall() {
  startCall(getChannelId(), sendWebsocketCommand);
  isCalling.value = true;
  outGoingCall.value = true;
  console.log("handleCall ");
}

function acceptCall() {
  console.log("Call accepted");
  incomingCall.value = false;
  isCalling.value = true;
  outGoingCall.value = false;

  if (incomingOffer.value) {
    handleOffer(incomingOffer.value, getChannelId(), sendWebsocketCommand);
  } else {
    console.warn("No incoming offer to accept.");
  }
}

function rejectCall() {
  console.log("Call rejected");

  sendWebsocketCommand("call-end", {
    channel_id: getChannelId(),
  });

  incomingCall.value = false;
  incomingOffer.value = null;
  isCalling.value = false;
}

function handleEndCall() {
  sendWebsocketCommand("call-end", { channel_id: getChannelId() });
  endCall();
  isCalling.value = false;
}

async function closeButton(channelId: string) {
  let currentChannelId = Array.isArray(route.params.channelId)
    ? route.params.channel_id[0]
    : route.params.channelId;
  console.log("closeButton", channelId, route.name, currentChannelId);
  const success = await conversationsStore.closeOpenedChat(channelId);
  if (success && currentChannelId == channelId) {
    console.log("current chat closed, redirecting to /friends");
    router.push("/friends");
  }
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
      <button
        v-if="hasActiveChat && !isCalling && !incomingCall"
        @click="handleCall"
        class="whiteboard-btn"
      >
        Start Call
      </button>
      <div v-if="incomingCall" class="incoming-call-container">
        <div class="incoming-call-header">
          <p>Incoming Call</p>
          <span class="vibrate-icon">📞</span>
        </div>
        <div class="incoming-call-btn-container">
          <button @click="acceptCall" class="accept-call-btn">
            Accept call
          </button>
          <button @click="rejectCall" class="reject-call-btn">
            Reject call
          </button>
        </div>
      </div>
      <Call
        v-if="isCalling"
        :outGoingCall="outGoingCall"
        @endCall="handleEndCall"
      />
      <button v-on:click="authStore.logout" class="logout-btn">Logout</button>
    </div>
  </div>
  <div v-else>Loading...</div>
</template>

<style scoped>
.whiteboard-btn,
.start-call-btn {
  margin-top: 10px;
  border: none;
  min-width: 180px;
  background-color: hsla(160, 100%, 37%, 1);
  color: white;
  padding: 10px;
  cursor: pointer;
  border-radius: 5px;
}

.whiteboard-btn:hover,
.start-call-btn:hover {
  background-color: hsla(160, 100%, 27%, 1);
}

.incoming-call-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #292b40;
  padding: 20px;
  border-radius: 5px;
}

.incoming-call-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.incoming-call-header p {
  font-size: 18 px;
  font-weight: bold;
  margin: 0;
}

.incoming-call-btn-container {
  display: flex;
  gap: 5px;
}

.accept-call-btn {
  margin-top: 10px;
  border: none;
  background-color: hsla(160, 100%, 37%, 1);
  color: white;
  padding: 10px;
  cursor: pointer;
  border-radius: 5px;
}

.accept-call-btn:hover {
  background-color: hsla(160, 100%, 27%, 1);
}

.reject-call-btn {
  margin-top: 10px;
  border: none;
  background-color: hsla(0, 100%, 50%, 1);
  color: white;
  padding: 10px;
  cursor: pointer;
  border-radius: 5px;
}

.reject-call-btn:hover {
  background-color: hsla(0, 100%, 40%, 1);
}

.accept-call-btn,
.reject-call-btn {
  padding: 4px 12px;
  min-width: 80px;
  font-size: 14px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  color: white;
  white-space: nowrap;
  text-align: center;
}

.vibrate-icon {
  animation: vibrate 0.2s linear infinite;
}

@keyframes vibrate {
  0% {
    transform: translate(0, 0);
  }
  25% {
    transform: translate(-2px, -2px);
  }
  50% {
    transform: translate(2px, -2px);
  }
  75% {
    transform: translate(-2px, 2px);
  }
  100% {
    transform: translate(0, 0);
  }
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
