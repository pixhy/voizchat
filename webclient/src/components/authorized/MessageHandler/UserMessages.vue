<script setup lang="ts">
import { onMounted, onUpdated } from 'vue';
import { useRoute } from 'vue-router';
import { getUser, getMe, prefetchMe, type User } from '@/helpers/users'
import { ref } from 'vue';
import { fetchWrapper } from '@/helpers/fetch-wrapper';
import { useAuthStore } from '@/stores/auth.store';
import { useConversationsStore } from '@/stores/opened_chats'

interface Message {
  sender_id: string;
  message: string;
  created_at: number;
}

const route = useRoute();
const userid = Array.isArray(route.params.userid) ? route.params.userid[0] : route.params.userid;

const messages = ref<Array<Message>>();
const userInfo = ref<User | null>();
const loaded = ref<boolean>(false);
let needScrollToBottom = true;

const bottomElement = ref<HTMLElement | null>(null);

let me: User | null = null;

onMounted(async () => {
  const conversationsStore = useConversationsStore();
  await conversationsStore.openOpenedChat(userid);

  const messagesResponse = await fetchWrapper.get(`/api/messages/user/${userid}?limit=20`)
  if(messagesResponse.success){
    messages.value = messagesResponse.value
    needScrollToBottom = true;
  }
  userInfo.value = await getUser(userid);
  await prefetchMe();
  me = getMe();
  console.log("ME", me)
  
  loaded.value = true;

  const ws = new WebSocket("/api/ws")
  ws.onopen = function(event){
    console.log("onopen");
    ws.send(JSON.stringify({"cmd": "login", "data": {"token": useAuthStore().token }}));
  }

  ws.onmessage = function(event){
    const messageObj = JSON.parse(event.data);
    console.log(messageObj);
    if(messageObj.cmd == "message"){
      const data = messageObj.data as Message
      if(data.sender_id == userid){
        addMessage(data)
      }
    }
  }

  ws.onclose = async function(e){
    console.log("onclose", e);
  }

  ws.onerror = async function(e){
    console.log("onerror", e);
  }

});

onUpdated(() => {
  if(needScrollToBottom){
    scrollToBottom();
    needScrollToBottom = false;
  }
});

const newMessage = ref("");

async function sendMessage(e : Event) {
  e.preventDefault()
  if(newMessage.value.length > 0){
    const messageObj = {message: newMessage.value}
    const postMessage = await fetchWrapper.post(`/api/message/user/${userid}`, messageObj)
    if(postMessage.success){
      addMessage(postMessage.value);
      newMessage.value = ""; 
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
    <div class="chat-messages" v-if="loaded">
      <div class="message" v-for="(msg, index) in messages" :key="index">
        <div class="message-header">
          <img src="@/assets/default.png" alt="User Avatar" class="avatar" />
          <span class="username">{{ msg.sender_id == me!.userid ? me!.username : userInfo!.username }}</span>
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
    </div>
  </template>
  

  
  <style scoped>
  .chat-messages {
    flex: 1;
    padding: 10px;
    overflow-y: auto;
    height: 94%;
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
  padding: 10px;
  background-color: #2c2f33;
  align-items: center;
  border-top: 1px solid #444;
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
  