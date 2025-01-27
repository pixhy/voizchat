import { defineStore } from "pinia";
import { fetchWrapper } from "@/helpers/fetch-wrapper";
import { getUser, type User } from "@/helpers/users";

interface OpenedChat {
    id: number;
    target_id: string;
    user_id: string;
    target_type: string;
}

interface ConversationsState {
  list: User[];
  isLoading: boolean;
  error: string | null; 
}

export const useConversationsStore = defineStore("conversations", {
  state: (): ConversationsState => ({
    list: [],
    isLoading: false,
    error: null, 
  }),
  actions: {
    async fetchConversations() {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await fetchWrapper.get(`/api/opened_chat/all`);
        if (!response.success) {
          throw new Error("Failed to fetch conversations");
        }
        const users: User[] = []
        for(let target of response.value as OpenedChat[]){
            users.push((await getUser(target.target_id))!);
        }
        this.list = users;
      } catch (err: any) {
        this.error = err.message; 
      } finally {
        this.isLoading = false;
      }
    },
    async openOpenedChat(userid: string){
      // check this.list, post() if not found
    },
    async closeOpenedChat(userid: string){
      // delete from this.list, delete() on backend
    }
  },
});
