<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth.store';
import { RouterLink } from 'vue-router';
import AuthDialog from './AuthDialog.vue';

const email = ref('');
const password = ref('');
const showPassword = ref(false);

const authStore = useAuthStore();

const handleLogin = async () => {
  const response = await authStore.login(email.value, password.value);
  if (response != null) {
    console.log(response);
  }
};
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
