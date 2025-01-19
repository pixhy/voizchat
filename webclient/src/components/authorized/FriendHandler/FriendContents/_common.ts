import { fetchWrapper } from '@/helpers/fetch-wrapper';
import { type Ref } from 'vue';

async function addFriend(user: any, listRef: Ref<any | null>) {
  const response = await fetchWrapper.post(`/api/user/add-friend/${user.userid}`);
  if (response.success) {
    console.log("friend added");
    listRef.value?.removeUser(user); 
  } else {
    console.log(response.error.status);
  }
}

async function removeFriend(user: any, listRef: Ref<any | null>) {
  const response = await fetchWrapper.post(`/api/user/remove-friend/${user.userid}`);
  if (response.success) {
    console.log("friend removed");
    listRef.value?.removeUser(user); 
  } else {
    console.log(response.error.status);
  }
}

export { addFriend, removeFriend };
