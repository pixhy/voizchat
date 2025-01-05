<script setup lang="ts">
import AuthDialog from './AuthDialog.vue'
import { RouterLink } from 'vue-router'
import { defineComponent } from 'vue'
import { useAuthStore } from '../stores/auth.store';
</script>
<script lang="ts">

export default defineComponent({
  data() {
    return {
      email: '',
      password: '',
      showPassword: false,
    };
  },
  methods: {
    async handleLogin() {
      let response = await useAuthStore().login(this.email, this.password)
      if(response != null){
        console.log(response)
      }
    },
  },
});

</script>

<template>
  <AuthDialog>
    <template #form>
      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="email">E-Mail address:</label>
          <input
            type="email"
            id="email"
            v-model="email"
            placeholder="Enter your email"
            required
          />
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

        <a href="#" class="forgot-password">Forgotten password?</a>

        <button type="submit" class="auth-button">Log in</button>

        <div class="signup-container">
          <p>Don’t have an account? <RouterLink to="/register">Sign up</RouterLink></p>
        </div>

        <button type="button" class="google-button">Log in with Google</button>
      </form>
    </template>
  </AuthDialog>
</template>
