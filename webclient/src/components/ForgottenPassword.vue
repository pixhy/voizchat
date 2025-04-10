<script setup lang="ts">
import AuthDialog from './AuthDialog.vue'
import { ref } from 'vue'
import { fetchWrapper } from '@/helpers/fetch-wrapper'

const email = ref('')
const message = ref('')
const isSuccess = ref(false)

const handleLogin = async () => {
  message.value = ''
  isSuccess.value = false
  const response = await fetchWrapper.post('/api/users/request-password-reset', {
    email: email.value,
  })

  if (!response.success) {
    message.value = response.error.message
  } else {
    message.value = 'Recovery email sent! Please check your inbox.'
    isSuccess.value = true
  }
}
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

        <div v-if="message" :style="{ color: isSuccess ? 'lightgreen' : 'red', marginBottom: '1rem' }">
          {{ message }}
        </div>

        <button type="submit" class="auth-button">Send recovery email</button>
      </form>
    </template>
  </AuthDialog>
</template>
