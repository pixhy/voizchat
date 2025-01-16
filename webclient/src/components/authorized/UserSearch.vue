<script setup lang="ts">
import { fetchWrapper } from '@/helpers/fetch-wrapper';
import { ref } from 'vue';
import { isSuccess } from '@/helpers/result';
import Friend from '@/components/authorized/FriendHandler/Friend.vue'

const username = ref('');
const searchedUser = ref<any>(null);
const errorMessage = ref('');

async function handleSearch(){
  const response = await fetchWrapper.get(`/api/users/find-by-name?username=${encodeURIComponent(username.value)}`);
  if (isSuccess(response)) {
    errorMessage.value = '';
    searchedUser.value = response.value;
  } else {
    errorMessage.value = response.error.message;
    searchedUser.value = null;
  }
};

async function addFriend (user: any){
  const response = await fetchWrapper.post(`/api/user/add-friend/${user.userid}`);
  if (response != null) {
    console.log(response);
  }
};
</script>

<template>
    <form @submit.prevent="handleSearch" class="search-form">
        <input id="username" v-model="username" placeholder="Search user" class="search-input"/>
        <button class="search-button">Search</button>
    </form>
    <div class="search-result">
      <Friend v-if="searchedUser" :user="searchedUser" action="Add friend" :actionFunction="addFriend"/>
      <div v-else-if="errorMessage" class="user-not-found">
        <div>{{ errorMessage }}</div>
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

.user-not-found {
  margin-top: 25px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  width: 320px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  background-color: rgb(74, 95, 116);
  display: flex;
  justify-content: center;
  align-items: center;
  height: 62px;
}

</style>
