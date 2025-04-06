<script setup lang="ts">
import { ref, onMounted, onUnmounted, inject, watch, watchEffect } from "vue";
import {
  initPeerConnection,
  remoteStream,
  peerConnection,
} from "@/helpers/webrtc";

const sendWebsocketCommand = inject("sendWebsocketCommand") as (
  command: string,
  data: any
) => {};

// Microphone volume tracking
const micLevel = ref(0);
const remoteMicLevel = ref(0);
let audioContext: AudioContext | null = null;
let analyser: AnalyserNode | null = null;
let micStream: MediaStream | null = null;
let animationFrameId: number | null = null;

const localVideo = ref<HTMLVideoElement | null>(null);
const remoteVideo = ref<HTMLVideoElement | null>(null);
const localStream = ref<MediaStream | null>(null);

async function startLocalStream() {
  try {
    localStream.value = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    });
    console.log("Got localStream:", localStream.value);
    console.log("Video tracks:", localStream.value.getVideoTracks());
    console.log("Audio tracks:", localStream.value.getAudioTracks());

    localStream.value.getTracks().forEach((track) => {
      peerConnection.value?.addTrack(track, localStream.value!);
    });
    if (localVideo.value) {
      localVideo.value.srcObject = localStream.value;
    }

    startMicVisualization(localStream.value);
  } catch (error) {
    console.error("Error accessing media devices:", error);
  }
}

function startMicVisualization(stream: MediaStream) {
  if (audioContext) {
    audioContext.close();
  }

  audioContext = new (window.AudioContext ||
    (window as any).webkitAudioContext)();
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

function startRemoteMicVisualization(remoteStream: MediaStream) {
  const audioCtx = new AudioContext();
  const source = audioCtx.createMediaStreamSource(remoteStream);
  const analyser = audioCtx.createAnalyser();
  analyser.fftSize = 256;

  source.connect(analyser);

  const dataArray = new Uint8Array(analyser.frequencyBinCount);

  function updateRemoteMicLevel() {
    analyser.getByteFrequencyData(dataArray);
    const volume = Math.max(...dataArray) / 255;
    remoteMicLevel.value = volume;

    requestAnimationFrame(updateRemoteMicLevel);
  }

  updateRemoteMicLevel();
}

onMounted(async () => {
  //initPeerConnection(sendWebsocketCommand);
  await startLocalStream();
  console.log("onMounted");

  // Wait for the remote stream to be available
  watchEffect(() => {
    console.log("watchEffect running");
    console.log("remoteVideo.value", remoteVideo.value);
    console.log("remoteStream.value", remoteStream.value);
    console.log("remoteStream is currently", remoteStream.value);

    if (remoteVideo.value && remoteStream.value) {
      remoteVideo.value.srcObject = remoteStream.value;
      remoteVideo.value.play().catch((e) => {
        console.warn("Autoplay failed:", e);
      });
    }
  });

  watchEffect(() => {
    if (remoteVideo.value && remoteStream.value) {
      remoteVideo.value.srcObject = remoteStream.value;
      remoteVideo.value.play().catch((e) => {
        console.warn("Autoplay failed:", e);
      });

      startRemoteMicVisualization(remoteStream.value);
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
    <video ref="localVideo" class="local-video" autoplay playsinline></video>
    <video ref="remoteVideo" class="remote-video" autoplay playsinline></video>

    <div class="mic-container">
      <div class="mic-bar" :style="{ width: micLevel * 100 + '%' }"></div>
    </div>

    <div class="remote-mic-container">
      <div
        class="remote-mic-bar"
        :style="{ width: remoteMicLevel * 100 + '%' }"
      ></div>
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
</style>
