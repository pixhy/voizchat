<script setup lang="ts">
import AuthDialog from './AuthDialog.vue'
import { RouterLink } from 'vue-router'
import { defineComponent } from 'vue'
</script>
<script lang="ts">

export default defineComponent({
  data() {
    return {
      email: '',
    };
  },
  methods: {
    handleLogin() {
      console.log('Logging in with', this.email);
    },
  },
});

</script>

<template>
  <AuthDialog>
    <template #form>
      <form @submit.prevent="handleLogin" class="auth-form">
        <p class="forgot-pw">
            Forgot your account’s password? Enter your email address and we’ll send you a recovery link.
        </p>
        <div class="form-group">
          <label for="email">E-Mail address:</label>
          <input
            type="email"
            id="email"
            v-model="email"
            placeholder="Enter your email"
            required
            class="auth-input"
          />
        </div>
        <button type="submit" class="auth-button">Send recovery email</button>
      </form>
    </template>
  </AuthDialog>
</template>
