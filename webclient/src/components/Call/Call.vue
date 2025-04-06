<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import { remoteStream, peerConnection, localStream, animationFrameId, micLevel } from "@/helpers/webrtc";

const remoteVideo = ref<HTMLVideoElement | null>(null);
const localVideo = ref<HTMLVideoElement | null>(null);

onMounted(async () => {

  watch(localStream, (stream) => {
  if (localVideo.value && stream) {
    localVideo.value.srcObject = stream;
  }
  });

  watch(remoteStream, (stream) => {
    if (remoteVideo.value && stream) {
      remoteVideo.value.srcObject = stream;
    }
  });

});

onUnmounted(() => {
  // Clean up the WebRTC connection when Call.vue is destroyed
  peerConnection.value?.close();
  peerConnection.value = null;

  if (localStream.value) {
    localStream.value.getTracks().forEach((track) => track.stop());
  }
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
});


</script>

<template>
  <div>
    <h2>Call in Progress</h2>
    <video ref="localVideo" autoplay playsinline muted></video>
    <video ref="remoteVideo" autoplay playsinline></video>

    <div class="mic-container">
      <div class="mic-bar" :style="{ width: micLevel * 100 + '%' }"></div>
    </div>
    <button @click="$emit('endCall')">End Call</button>
  </div>
</template>


<style scoped>
.local-video,
.remote-video {
  width: 300px;
  height: 200px;
  background-color: black;
  margin: 10px;
}

.controls {
  margin-top: 10px;
}

button {
  padding: 10px 15px;
  margin-right: 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

.mic-container {
  width: 150px;
  height: 10px;
  background: #ddd;
  border-radius: 5px;
  overflow: hidden;
  margin-top: 10px;
}

.mic-bar {
  height: 100%;
  background: limegreen;
  transition: width 0.1s ease-out;
}
</style>