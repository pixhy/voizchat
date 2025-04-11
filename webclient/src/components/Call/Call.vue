<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from "vue";
import {
  remoteStream,
  peerConnection,
  localStream,
  animationFrameId,
  micLevel,
  localVideo,
  remoteVideo,
  endCall,
  remoteMicLevel,
} from "@/helpers/webrtc";
import { Mic, MicOff, Video, VideoOff, Headphones } from "lucide-vue-next";

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

const isMicMuted = ref(false);
const isVideoOff = ref(false);
const isRemoteMuted = ref(false);

function toggleMic() {
  const track = localStream.value?.getAudioTracks()[0];
  if (track) {
    track.enabled = !track.enabled;
    isMicMuted.value = !track.enabled;
  }
}

function toggleVideo() {
  const track = localStream.value?.getVideoTracks()[0];
  if (track) {
    track.enabled = !track.enabled;
    isVideoOff.value = !track.enabled;
  }
}

function toggleRemoteAudio() {
  if (remoteVideo.value) {
    remoteVideo.value.muted = !remoteVideo.value.muted;
    isRemoteMuted.value = remoteVideo.value.muted;
  }
}
</script>

<template>
  <div class="call-container">
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
      <span class="local-mic-test">Local Mic Level</span>
      <div class="mic-bar-background">
        <div class="mic-bar" :style="{ width: micLevel * 100 + '%' }"></div>
      </div>
      <span class="local-mic-test">Remote Mic Level</span>
      <div class="mic-bar-background">
        <div
          class="mic-bar"
          :style="{ width: remoteMicLevel * 100 + '%' }"
        ></div>
      </div>
    </div>

    <div class="call-controls">
      <button
        @click="toggleMic"
        :class="['icon-btn', isMicMuted ? 'muted' : 'active']"
      >
        <component :is="isMicMuted ? MicOff : Mic" />
      </button>

      <button
        @click="toggleRemoteAudio"
        :class="['icon-btn', isRemoteMuted ? 'muted' : 'active']"
      >
        <Headphones />
      </button>

      <button
        @click="toggleVideo"
        :class="['icon-btn', isVideoOff ? 'muted' : 'active']"
      >
        <component :is="isVideoOff ? VideoOff : Video" />
      </button>
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

.local-mic-test {
  color: #fff;
  font-size: 12px;
  margin-bottom: 5px;
}

.mic-container {
  display: flex;
  flex-direction: column;
  margin-top: 5px;
  width: 150px;
  margin-top: 10px;
}

.mic-bar-background {
  width: 100%;
  height: 10px;
  background: #ddd;
  border-radius: 5px;
  overflow: hidden;
}
.mic-bar {
  height: 10px;
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

.call-controls {
  display: flex;
  justify-content: center;
  gap: 5px;
  margin-top: 10px;
}

.icon-btn {
  width: 60px;
  height: 40px;
  display: flex;
  border: none;
  justify-content: center;
  align-items: center;
}

.icon-btn svg {
  width: 20px;
  height: 20px;
}

.icon-btn.active {
  color: #45a049;
  background-color: transparent;
  transition: all 0.3s ease;
}

.icon-btn.muted {
  color: red;
  background-color: transparent;
  position: relative;
  transition: all 0.3s ease;
}

.icon-btn.muted::after {
  content: "";
  position: absolute;
  width: 2px;
  height: 24px;
  background-color: red;
  transform: rotate(45deg);
}
</style>
