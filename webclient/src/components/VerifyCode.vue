<script setup lang="ts">
import AuthDialog from './AuthDialog.vue'
import { useRoute } from 'vue-router'
import { defineComponent, ref, onBeforeUnmount } from 'vue'
import { useAuthStore } from '../stores/auth.store';
</script>
<script lang="ts">

export default defineComponent({
  data() {
    return {
      verificationResult: ref<null | string | true>(null),
      timeout: 3,
    };
  },
  mounted() {
    this.verifyCode()
  },
  methods: {
    async verifyCode() {
      const route = useRoute();
      const verificationCode = Array.isArray(route.params.code) ? route.params.code[0] : route.params.code;
      let response = useAuthStore().verifyCode(verificationCode);
      let data = await response
      if(data != null){
        this.verificationResult = data
      }
      else {
        this.verificationResult = true;
        let timer: null | number = setInterval(() => {
          this.timeout--;
          if(this.timeout == 0){
            if(timer !== null){
              clearInterval(timer);
              timer = null;
            }
            this.$router.push("/messages");
          }
        }, 1000);

        onBeforeUnmount(() => {if(timer !== null)clearInterval(timer);});
      }
    },
  },
});

</script>

<template>
  <AuthDialog>
    <template #form>
        <div v-if="verificationResult === null">
          Loading!
        </div>
        <div v-else-if="verificationResult === true">
          <p>Account verification successful!</p>
          <p>Redirecting to application in {{ timeout }} second(s)</p>
        </div>
        <div v-else>
          Account could not be verified<br/>
          {{ verificationResult }}
        </div>
    </template>    
  </AuthDialog>
</template>
