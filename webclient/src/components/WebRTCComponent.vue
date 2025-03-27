<template>
  <div>
    <h1>WebRTC Video Chat</h1>
    <video ref="remoteVideo" autoplay></video>
    <button @click="startCall">Start Call</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";

const socket = new WebSocket("ws://localhost:8000/ws/your_user_id");
const peerConnection = new RTCPeerConnection();

export default defineComponent({
  name: "WebRTCComponent",
  setup() {
    const remoteVideo = ref<HTMLVideoElement | null>(null);

    socket.onmessage = async (event) => {
      const message = event.data;
      if (message.startsWith("offer")) {
        const offer = new RTCSessionDescription({
          sdp: message.split(" ", 1)[1],
          type: "offer",
        });
        await peerConnection.setRemoteDescription(offer);
        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);
        socket.send(`answer ${answer.sdp}`);
      } else if (message.startsWith("candidate")) {
        const candidate = new RTCIceCandidate({
          candidate: message.split(" ", 1)[1],
        });
        await peerConnection.addIceCandidate(candidate);
      }
    };

    navigator.mediaDevices
      .getUserMedia({ video: true, audio: true })
      .then((stream) => {
        stream
          .getTracks()
          .forEach((track) => peerConnection.addTrack(track, stream));
      })
      .catch((err) => console.error("Media error:", err));

    peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        socket.send(`candidate ${event.candidate.candidate}`);
      }
    };

    peerConnection.ontrack = (event) => {
      if (remoteVideo.value && event.streams[0]) {
        remoteVideo.value.srcObject = event.streams[0];
      }
    };

    const startCall = async () => {
      const offer = await peerConnection.createOffer();
      await peerConnection.setLocalDescription(offer);
      socket.send(`offer ${offer.sdp}`);
    };

    return { remoteVideo, startCall };
  },
});
</script>

<style scoped>
video {
  width: 100%;
  height: auto;
  border: 1px solid black;
}
</style>
