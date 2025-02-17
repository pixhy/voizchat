import { fetchWrapper } from '@/helpers/fetch-wrapper';
import { type Ref } from 'vue';

async function addFriend(user: any) {
  const response = await fetchWrapper.post(`/api/user/add-friend/${user.userid}`);
  if (response.success) {
    console.log("friend added");
  } else {
    console.log(response.error.status);
  }
}

async function removeFriend(user: any) {
  const response = await fetchWrapper.post(`/api/user/remove-friend/${user.userid}`);
  if (response.success) {
    console.log("friend removed");
  } else {
    console.log(response.error.status);
  }
}

class FriendAction {
  buttonText: string;
  onClick: (user: any) => void;
  disabled: boolean;
  constructor(buttonText: string, onClick: (user: any) => void, disabled: boolean = false){
    this.buttonText = buttonText;
    this.onClick = onClick;
    this.disabled = disabled;
  }
}

export { addFriend, removeFriend, FriendAction };
