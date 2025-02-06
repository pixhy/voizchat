import { defineStore } from "pinia";
import { fetchWrapper } from "@/helpers/fetch-wrapper";
import {  type User } from "@/helpers/users";

interface Channel{
  id: number,
  channel_id: string,
  channel_type: string,
  last_update: number
}


export interface OpenedChat {
  channel: Channel;
  users: User[];
}

interface ConversationsState {
  openedChatList: OpenedChat[];
  isLoading: boolean;
  error: string | null; 
}

export const useConversationsStore = defineStore("conversations", {
  state: (): ConversationsState => ({
    openedChatList: [],
    isLoading: true,
    error: null,
  }),
  actions: {
    async fetchConversations() {
      this.error = null;

      try {
        const response = await fetchWrapper.get(`/api/opened_chat/all`);
        if (!response.success) {
          throw new Error("Failed to fetch conversations");
        }
        this.openedChatList = response.value as OpenedChat[]

      } catch (err: any) {
        this.error = err.message; 
      } finally {
        this.isLoading = false;
      }
    },
    async openOpenedChat(channelId: string): Promise<OpenedChat>{
      for(let openedChat of this.openedChatList){
        if(openedChat.channel.channel_id == channelId){
          return openedChat
        }
      }  
      // /api/opened_chat/channel/{channel_id}
      const openedChatResponse = await fetchWrapper.post(`/api/opened_chat/channel/${channelId}`)
      if (openedChatResponse.success){
        this.openedChatList.push(openedChatResponse.value)
        return openedChatResponse.value
      }
      throw "failed to request channel";
    },
    async openOpenedChatWithUser(userId: string): Promise<OpenedChat>{
      for(let openedChat of this.openedChatList){
        if(openedChat.channel.channel_type == "user" && openedChat.users[0].userid == userId){
          return openedChat
        }
      }  
      // /api/opened_chat/user/{user_id}
      const openedChatResponse = await fetchWrapper.post(`/api/opened_chat/user/${userId}`)
      if (openedChatResponse.success){
        this.openedChatList.push(openedChatResponse.value)
        return openedChatResponse.value
      }
      throw "failed to request channel";
    },
    async closeOpenedChat(channelId: string): Promise<boolean> {
      const response = await fetchWrapper.delete(`/api/opened_chat/${channelId}`);
      if(response.success){
        this.openedChatList = this.openedChatList.filter(e => e.channel.channel_id !== channelId)
        return true;
      }
      console.log("closeOpenedChat: failed to close chat", response.error);
      return false;
    }
  },
});
