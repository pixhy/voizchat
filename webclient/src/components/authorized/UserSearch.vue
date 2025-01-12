<script setup lang="ts">
import { fetchWrapper } from '@/helpers/fetch-wrapper';
import { defineComponent, ref } from 'vue';
import { isSuccess } from '@/helpers/result';
</script>

<script lang="ts">
export default defineComponent({
  data() {
    return {
        username: '',
        searchedUser: ref<any>(null),
    };
  },
  methods: {
    async handleSearch() {
      let response = await fetchWrapper.get(`/api/users/find-by-name?username=${encodeURIComponent(this.username)}`);
      if (isSuccess(response)) {
        this.searchedUser = response.value;
      }
    },
    async addFriend(userid:string){
      let response = await fetchWrapper.post(`/api/user/add-friend/${userid}`);
      if(response != null){
        console.log(response);
      }
    }
  },
});
</script>

<template>
    <form @submit.prevent="handleSearch" class="search-form">
        <input id="username" v-model="username" placeholder="Search user" class="search-input"/>
        <button class="search-button">Search</button>
    </form>
    <div class="search-result">
      <div v-if="searchedUser" class="searched-user">
        <img class="avatar" src="@/assets/default.png" alt="User Avatar" width="40"/>
        <div class="search-result-username">{{ searchedUser.username }}</div>
        <button class="friend-request-button" v-on:click="addFriend(searchedUser.id)">Add friend</button>
      </div>
    </div>
</template>

<style>

.search-form {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.search-input {
  padding: 10px 15px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #007BFF;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}

.search-button {
  padding: 10px 20px;
  font-size: 16px;
  color: white;
  background-color: #007BFF;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.2s;
}

.search-button:hover {
  background-color: #0056b3;
}
.search-result{
  display: flex;
  justify-content: center;
}
.searched-user {
  margin-top: 25px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  width: 320px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  background-color: rgb(74, 95, 116);
  grid-template-columns: auto 1fr auto;
  display: grid;
  align-items: center;
}

.search-result-username {
  justify-self: center;
  margin: 3px;
}

.friend-request-button {
  padding: 8px;
  font-size: 14px;
  color: white;
  background-color: #28a745;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.2s;
}

.friend-request-button:hover {
  background-color: #218838;
}

</style>
