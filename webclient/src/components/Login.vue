
<template>
  <div class="login-page">
    <div class="login-container">
      <h1 class="title">VoizChat</h1>
      <form @submit.prevent="handleLogin" class="login-form">
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
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <a href="#" class="forgot-password">Forgotten password?</a>

        <button type="submit" class="login-button">Log in</button>

        <div class="signup-container">
          <p>Don’t have an account? <a href="#">Sign up</a></p>
        </div>

        <button type="button" class="google-login">Log in with Google</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
      showPassword: false,
    };
  },
  methods: {
    handleLogin() {
      console.log('Logging in with', this.email, this.password);
    },
  },
};
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
  background: url('../assets/voizchatbg.png') no-repeat center;
}

.login-container {
  background-color: rgba(0, 0, 0, 0.8);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
  width: 100%;
  max-width: 400px;
  text-align: center;
  color: #fff;
}

.title {
  margin-bottom: 1.5rem;
  font-size: 2rem;
  color: #fff;
}

.login-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 1rem;
  text-align: left;
}

input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.password-container {
  display: flex;
  align-items: center;
}

.toggle-password {
  background: none;
  border: none;
  margin-left: 0.5rem;
  cursor: pointer;
  color: #fff;
  font-size: 1.2rem;
}

.forgot-password {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #1e90ff;
  text-decoration: none;
}

.login-button {
  margin-top: 1rem;
  padding: 0.5rem;
  border: none;
  background-color: #1e90ff;
  color: #fff;
  font-size: 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.signup-container {
  margin-top: 1rem;
  font-size: 0.9rem;
}

.google-login {
  margin-top: 1rem;
  padding: 0.5rem;
  border: 1px solid #ddd;
  background-color: #fff;
  color: #000;
  font-size: 1rem;
  border-radius: 4px;
  cursor: pointer;
}
</style>
