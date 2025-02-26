<script setup lang="ts">
import { onMounted, onUnmounted, onUpdated, inject } from 'vue';
import { useRoute, onBeforeRouteUpdate } from 'vue-router';
import { getMe, type User } from '@/helpers/users'
import { ref } from 'vue';
import { fetchWrapper } from '@/helpers/fetch-wrapper';
import { useConversationsStore, type OpenedChat } from '@/stores/opened_chats'
import Whiteboard from '@/components/WhiteBoard/Whiteboard.vue';

export interface Message {
  id: number,
  channel_id: string;
  sender_id: string;
  message: string;
  created_at: number;
}

const route = useRoute();
const conversationsStore = useConversationsStore();

const setMessageHandler = inject('setMessageHandler') as (handler: any) => {};
const sendWebsocketCommand = inject('sendWebsocketCommand') as (command: string, data: any) => {};

let channelId = Array.isArray(route.params.channelId) ? route.params.channel_id[0] : route.params.channelId;

const messages = ref<Array<Message>>();
const chatInfo = ref<OpenedChat | null>();
const loaded = ref<boolean>(false);
let needScrollToBottom = true;

const bottomElement = ref<HTMLElement | null>(null);

let me: User | null = null;
const showWhiteBoard = ref<boolean>(false);

onBeforeRouteUpdate(async (to, from) => {
  console.log("onBeforeRouteUpdate", from, to);
  if(to.params.channelId != from.params.channelId){
    channelId = Array.isArray(to.params.channelId) ? to.params.channel_id[0] : to.params.channelId;
    console.log("Messages channelId changed to ", channelId);
    await loadMessages();
  }
});

onMounted(async () => {
  console.log("Messages onMounted", channelId);

  me = getMe();
  console.log("ME", me)

  await loadMessages();
  setMessageHandler(onMessage);
});

onUnmounted(async() => {
  setMessageHandler(null);
});

async function loadMessages(){
  loaded.value = false;
  chatInfo.value = await conversationsStore.openOpenedChat(channelId);

  const messagesResponse = await fetchWrapper.get(`/api/messages/${channelId}?limit=20`)
  if(messagesResponse.success){
    messages.value = messagesResponse.value;
    needScrollToBottom = true;
    console.log(messagesResponse.value);
  }
  else {
    console.log("failed to load messages");
    return;
  }
  
  if(messages.value && messages.value.length > 0){
    sendWebsocketCommand("read_message", {"message_id": messages.value[messages.value.length - 1].id});
  }

  chatInfo.value.unread_count = 0;

  loaded.value = true;
}

onUpdated(() => {
  if(needScrollToBottom){
    scrollToBottom();
    needScrollToBottom = false;
  }
});

function onMessage(message: Message): boolean{
  if(message.channel_id !== channelId) {
    return false;
  }
  sendWebsocketCommand("read_message", {"message_id": message.id});
  
  if(me!.userid !== message.sender_id){
    addMessage(message);
  }

  return true;
}

const newMessage = ref("");

async function sendMessage(e : Event) {
  e.preventDefault()
  if(newMessage.value.length > 0){
    const messageObj = {message: newMessage.value}
    const postMessage = await fetchWrapper.post(`/api/message/${channelId}`, messageObj)
    if(postMessage.success){
      const message = postMessage.value as Message;
      if(chatInfo.value && chatInfo.value.channel.last_update < message.created_at){
        chatInfo.value.channel.last_update = message.created_at
      }
      addMessage(message);
      newMessage.value = "";
      sendWebsocketCommand("read_message", {"message_id": message.id})
    }
  }
};

function scrollToBottom(){
  bottomElement.value?.scrollIntoView();
}

function addMessage(message: Message){
  messages.value?.push(message);
  needScrollToBottom = true;
}

function convertDateToString(timestamp: number): string {
  return new Date(timestamp*1000).toLocaleString();
}

</script>

<template>
  <div class="channel-container">
    <div v-if="chatInfo"> 
      chat with {{ chatInfo.users[0].username }}
    </div>
    <Whiteboard v-if="showWhiteBoard" />
    <div class="chat-messages" v-if="loaded">
      <div class="message" v-for="(msg, index) in messages" :key="index">
        <div class="message-header">
          <img src="@/assets/default.png" alt="User Avatar" class="avatar" />
          <span class="username">{{ msg.sender_id == me!.userid ? me!.username : chatInfo?.users![0].username }}</span>
          <span class="timestamp">{{ convertDateToString(msg.created_at) }}</span>
        </div>
        <div class="message-content">
          <p>{{ msg.message }}</p>
        </div>
      </div>
      <div ref="bottomElement"></div>
    </div>
    <div class="chat-input">
      <input 
        v-model="newMessage" 
        type="text" 
        placeholder="Type a message..." 
        @keydown.enter="sendMessage" 
        class="input-field" 
      />
      <button v-on:click="sendMessage" class="send-button">Send</button>
      <button v-on:click="showWhiteBoard = true" class="send-button">Whiteboard</button>
    </div>
  </div>
</template>
  

  
<style scoped>
.channel-container{
  display: flex;
  flex-direction: column;
  height: 100%;
  align-items: center;
}

.chat-messages {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  width: 99%;
}

.message {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
}

.username {
  font-weight: bold;
  margin-right: 10px;
}

.timestamp {
  font-size: 0.85rem;
  color: gray;
}

.message-content {
  background-color: #2c2f33;
  padding: 10px;
  border-radius: 5px;
  color: white;
}

.chat-input {
  display: flex;
  background-color: #2c2f33;
  align-items: center;
  border-top: 1px solid #444;
  width: 99%;
}

.input-field {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 5px;
  margin-right: 10px;
}

.send-button {
  padding: 10px 15px;
  background-color: #5865f2;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.send-button:hover {
  background-color: #4752c4;
}
</style>
  