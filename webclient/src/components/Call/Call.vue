<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import {
  remoteStream,
  peerConnection,
  localStream,
  animationFrameId,
  micLevel,
  localVideo,
  remoteVideo,
  endCall,
} from "@/helpers/webrtc";

defineProps<{
  outGoingCall: boolean;
}>();

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
  endCall();
});
</script>

<template>
  <div lass="call-container">
    <div class="call-header">
      <h2 v-if="!outGoingCall">Call in Progress</h2>
      <h2 v-else>
        Calling
        <span class="animated-heading">...</span>
      </h2>
    </div>
    <video
      ref="localVideo"
      class="local-video"
      autoplay
      playsinline
      muted
    ></video>
    <video ref="remoteVideo" class="remote-video" autoplay playsinline></video>

    <div class="mic-container">
      <div class="mic-bar" :style="{ width: micLevel * 100 + '%' }"></div>
    </div>

    <button @click="$emit('endCall')" class="end-call-btn">End Call</button>
  </div>
</template>

<style scoped>
.call-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100%;
}

.call-container h2 {
  font-size: bold;
  font-size: 24px;
}

.call-header {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.animated-heading {
  display: inline-block;
  background: linear-gradient(90deg, #ffffff, #ff3385);
  background-size: 200% auto;
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  animation: shine 3s linear infinite;
}

@keyframes shine {
  0% {
    background-position: 200% center;
  }
  100% {
    background-position: -200% center;
  }
}

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

.remote-mic-container {
  width: 150px;
  height: 10px;
  background: #ddd;
  border-radius: 5px;
  overflow: hidden;
  margin-top: 10px;
}

.remote-mic-bar {
  height: 100%;
  background: limegreen;
  transition: width 0.1s ease-out;
  margin-top: 10px;
}

.local-video {
  width: 80%;
  max-width: 200px;
  height: auto;
  z-index: 1;
  border: #444 2px solid;
  border-radius: 5px;
}

.remote-video {
  width: 80%;
  max-width: 200px;
  height: auto;

  z-index: 0;
  border: #45a049 2px solid;
  border-radius: 5px;
}

.end-call-btn {
  margin-top: 10px;
  min-width: 180px;
  border: none;
  background-color: hsla(0, 100%, 50%, 1);
  color: white;
  padding: 10px;
  cursor: pointer;
  border-radius: 5px;
}

.end-call-btn:hover {
  background-color: hsla(0, 100%, 40%, 1);
}
</style>
