
<template>
  <div class="auth-page">
    <div class="auth-container">
      <img src="@/assets/logo.png"/>
      <slot name="form"></slot>
    </div>
  </div>
</template>
    
<style scoped>
  .auth-page {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    width: 100vw;
    background: url('@/assets/voizchatbg.png') no-repeat center;
  }
  
  .auth-container {
    background-color: rgba(0, 0, 0, 0.8);
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
    width: 100%;
    max-width: 400px;
    text-align: center;
    color: #fff;
  }
  
  :slotted(.auth-form) {
    display: flex;
    flex-direction: column;
  }
  
  :slotted(.form-group) {
    margin-bottom: 1rem;
    text-align: left;
  }
  
  :slotted(.auth-input) {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    background-color: #ddd;
  }
  
  :slotted(.password-container) {
    display: flex;
    align-items: center;
    position: relative;
  }
  :slotted(.password-container input){
    padding-right: 32px;
  }
  
  :slotted(.toggle-password) {
    background: none;
    border: none;
    margin-left: 0.5rem;
    cursor: pointer;
    color: #fff;
    font-size: 1.2rem;
    position: absolute;
    right: 0px;
  }
  
  :slotted(.forgot-password) {
    font-size: 0.9rem;
    color: #1e90ff;
    text-decoration: none;
    text-align: left;
  }
  
  :slotted(.auth-button) {
    margin-top: 1rem;
    padding: 0.5rem;
    border: none;
    background-color: #1e90ff;
    color: #fff;
    font-size: 1rem;
    border-radius: 4px;
    cursor: pointer;
  }
  
  :slotted(.signup-container) {
    margin-top: 1rem;
    font-size: 0.9rem;
  }
  
  :slotted(.google-button) {
    margin-top: 1rem;
    padding: 0.5rem;
    border: 1px solid #ddd;
    background-color: #fff;
    color: #000;
    font-size: 1rem;
    border-radius: 4px;
    cursor: pointer;
  }

  :slotted(.pw-requirement){
    text-align: left;
  }
  :slotted(.forgot-pw){
    margin-bottom: 15px;
    text-align: left;
  }
</style>
  