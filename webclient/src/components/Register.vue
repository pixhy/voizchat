<script setup lang="ts">
import AuthDialog from './AuthDialog.vue'
import { RouterLink,  } from 'vue-router'
import { defineComponent } from 'vue'
import { useAuthStore } from '../stores/auth.store';
</script>

<script lang="ts">

export default defineComponent({
  data() {
    return {
      email: '',
      username: '',
      password: '',
      showPassword: false,
      registerSuccessful: false,
    };
  },
  methods: {
    async onSubmit() {

      let response = await useAuthStore().register(this.email, this.username, this.password)
      if(response != null){
        console.log(response);
      }
      else {
        this.registerSuccessful = true;
      }
    }
  }
});

</script>


<template>
  <AuthDialog>
    <template #form v-if="registerSuccessful == false">
      <form @submit.prevent="onSubmit"  class="auth-form">
        <div class="form-group">
          <label for="email">E-Mail address:</label>
          <input type="email" id="email" v-model="email" required />
        </div>
        <div class="form-group">
          <label for="username">Username:</label>
          <input type="text" id="username" v-model="username" required />
        </div>


        <div class="form-group">
          <label for="password">Password:</label>
          <div class="password-container">
            <input
              :type="showPassword ? 'text' : 'password'"
              id="password"
              v-model="password"
              placeholder="Enter your password"
              required
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="toggle-password"
            >
              {{ !showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>
        <small class="pw-requirement">Must contain 8+ characters, including at least 1 letter and 1 number.</small>
        <button type="submit" class="auth-button">Sign up</button>


      <div class="signup-container">
        Already have an account? <RouterLink to="/login">Log in</RouterLink>
      </div>

      <button class="google-button">Sign up with Google</button>
      </form>
    </template>
    <template #form v-else>
      You have successfully registered. A verification email has been sent
      to the provided email address.
    </template>
  </AuthDialog>
</template>
  
