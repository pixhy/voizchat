<script setup lang="ts">
import { ref, onMounted, onUnmounted, inject, watch } from "vue";
import { initPeerConnection, remoteStream, peerConnection } from "@/helpers/webrtc";

const sendWebsocketCommand = inject("sendWebsocketCommand") as (
  command: string,
  data: any
) => {};

// Microphone volume tracking
const micLevel = ref(0);
let audioContext: AudioContext | null = null;
let analyser: AnalyserNode | null = null;
let micStream: MediaStream | null = null;
let animationFrameId: number | null = null;
const remoteVideo = ref<HTMLVideoElement | null>(null);


const localStream = ref<MediaStream | null>(null);

async function startLocalStream() {
  try {
    localStream.value = await navigator.mediaDevices.getUserMedia({
      video: false,
      audio: true,
    });

    localStream.value.getTracks().forEach((track) => {
      peerConnection.value?.addTrack(track, localStream.value!);
    });

    startMicVisualization(localStream.value);
  } catch (error) {
    console.error("Error accessing media devices:", error);
  }

}

function startMicVisualization(stream: MediaStream) {
  if (audioContext) {
    audioContext.close();
  }

  audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
  const source = audioContext.createMediaStreamSource(stream);
  analyser = audioContext.createAnalyser();
  analyser.fftSize = 256;
  source.connect(analyser);

  const dataArray = new Uint8Array(analyser.frequencyBinCount);

  function updateMicLevel() {
    if (!analyser) return;
    analyser.getByteFrequencyData(dataArray);
    micLevel.value = Math.max(...dataArray) / 255;

    animationFrameId = requestAnimationFrame(updateMicLevel);
  }

  updateMicLevel();
}

onMounted(async () => {

  initPeerConnection(sendWebsocketCommand);

// Wait for the remote stream to be available
  watch(remoteStream, (stream) => {
    if (remoteVideo.value && stream) {
      remoteVideo.value.srcObject = stream;
    }
  });
  await startLocalStream();
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
    <video ref="localVideo" autoplay playsinline></video>
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