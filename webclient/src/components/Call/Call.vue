<template>
  <div>
    <h2>Call in Progress</h2>
    <video id="localVideo" ref="localVideo" autoplay playsinline muted></video>
    <video ref="remoteVideo" autoplay playsinline></video>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, inject, watch } from "vue";
import { initPeerConnection, remoteStream } from "@/helpers/webrtc";
import { useRoute } from "vue-router";

const sendWebsocketCommand = inject("sendWebsocketCommand") as (
  cmd: string,
  data: any
) => void;

const localVideo = ref<HTMLVideoElement | null>(null);
const remoteVideo = ref<HTMLVideoElement | null>(null);
const peerConnection = ref<RTCPeerConnection | null>(null);
const route = useRoute();

async function startLocalStream() {
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: true,
    video: true,
  });
  localVideo.value!.srcObject = stream;
  stream.getTracks().forEach((track) => {
    peerConnection.value!.addTrack(track, stream);
  });
}

onMounted(async () => {
  const channelId = Array.isArray(route.params.channelId)
    ? route.params.channelId[0]
    : route.params.channelId;

  peerConnection.value = initPeerConnection(sendWebsocketCommand, channelId);

  // Ha már jött be remote stream (másik oldal elfogadta), megjelenítjük
  if (remoteStream.value) {
    remoteVideo.value!.srcObject = remoteStream.value;
  }

  watch(
    () => remoteStream.value,
    (stream) => {
      if (stream && remoteVideo.value) {
        remoteVideo.value.srcObject = stream;
      }
    }
  );

  await startLocalStream();
});

onUnmounted(() => {
  peerConnection.value?.close();
  peerConnection.value = null;
});
</script>

<style scoped>
video {
  width: 80%;
  max-width: 200px;
  margin: 10px;
  border: 2px solid white;
}
</style>
