<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import AuthDialog from './AuthDialog.vue'

const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const message = ref('')
const router = useRouter()
const route = useRoute()

const email = ref('')
const code = ref('')

onMounted(() => {
  email.value = (route.query.email as string) || ''
  code.value = (route.query.code as string) || ''
})

const handleReset = async () => {
  message.value = ''

  if (password.value !== confirmPassword.value) {
    message.value = "Passwords do not match."
    return
  }

  const response = await fetchWrapper.post('/api/users/reset-password', {
    email: email.value,
    code: code.value,
    new_password: password.value
  })

  if (!response.success) {
    message.value = response.error.message
  } else {
    message.value = 'Password reset successfully!'
    setTimeout(() => router.push('/login'), 1500)
  }
}
</script>

<template>
  <AuthDialog>
    <template #form>
      <form @submit.prevent="handleReset" class="auth-form">
        <p>Set a new password for <strong>{{ email }}</strong></p>

        <div class="form-group">
          <label for="password">New Password:</label>
          <div class="password-container">
            <input
              :type="showPassword ? 'text' : 'password'"
              id="password"
              v-model="password"
              class="auth-input"
              required
            />
            <button type="button" @click="showPassword = !showPassword" class="toggle-password">
              {{ !showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm New Password:</label>
          <input
            :type="showPassword ? 'text' : 'password'"
            id="confirmPassword"
            v-model="confirmPassword"
            class="auth-input"
            required
          />
        </div>

        <div v-if="message" :style="{ color: message === 'Password reset successfully!' ? 'lightgreen' : 'red', marginBottom: '10px' }">
          {{ message }}
        </div>

        <button type="submit" class="auth-button">Reset Password</button>
      </form>
    </template>
  </AuthDialog>
</template>
