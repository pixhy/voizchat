import { defineStore } from "pinia";
import { fetchWrapper } from "@/helpers/fetch-wrapper";
import { type User } from "@/helpers/users";

interface FriendListStore {
    friendList: User[],
    incomingFriendRequests: User[],
    outgoingFriendRequests: User[],
    isLoading: boolean,
    error: string | null,
}

async function fetchUserList(endpoint: string): Promise<User[]> {
        const response = await fetchWrapper.get(endpoint);
        if (!response.success) {
          throw new Error("Failed to fetch " + endpoint);
        }
        return response.value as User[]
}

export enum FriendState {
    Unknown,
    Friend,
    IncomingRequest,
    OutgoingRequest,
}

export interface FriendStateUpdate {
  other_user: User;
  new_state: string;
}

export const useFriendsStore = defineStore("friends", {
  state: (): FriendListStore => ({
    friendList: [],
    incomingFriendRequests: [],
    outgoingFriendRequests: [],
    isLoading: true,
    error: null,
  }),
  actions: {
    async fetchFriends() {
      this.error = null;

      try {
        [this.friendList, this.incomingFriendRequests, this.outgoingFriendRequests] 
          = await Promise.all([
            fetchUserList("/api/user/get-friends"),
            fetchUserList("/api/user/incoming-friend-requests"),
            fetchUserList("/api/user/outgoing-friend-requests"),
        ]);
      } catch (err: any) {
        this.error = err.message; 
      } finally {
        this.isLoading = false;
      }
    },
    getFriendState(userid: string){
        if(this.isLoading){
            console.error("getFriendState isLoading is true");
        }
        if(this.friendList.some(user => user.userid == userid)) {
            return FriendState.Friend;
        }
        if(this.incomingFriendRequests.some(user => user.userid == userid)){
            return FriendState.IncomingRequest;
        }
        if(this.outgoingFriendRequests.some(user => user.userid == userid)) {
            return FriendState.OutgoingRequest;
        }
        return FriendState.Unknown;
    },
    updateFriendState(update: FriendStateUpdate){
      switch(update.new_state){
        case "accept-outgoing":
          this.outgoingFriendRequests = this.outgoingFriendRequests.filter(u => u.userid != update.other_user.userid);
          this.friendList.push(update.other_user);
          break;
        case "accept-incoming":
          this.incomingFriendRequests = this.incomingFriendRequests.filter(u => u.userid != update.other_user.userid);
          this.friendList.push(update.other_user);
          break;
        case "request-incoming":
          this.incomingFriendRequests.push(update.other_user);
          break;
        case "request-outgoing":
          this.outgoingFriendRequests.push(update.other_user);
          break;
        case "remove-incoming":
          this.incomingFriendRequests = this.incomingFriendRequests.filter(u => u.userid != update.other_user.userid);
          break;
        case "remove-outgoing":
          this.outgoingFriendRequests = this.outgoingFriendRequests.filter(u => u.userid != update.other_user.userid);
          break;
        case "remove-friend":
          this.friendList = this.friendList.filter(u => u.userid != update.other_user.userid);
          break;
      }

    }
  },
});
