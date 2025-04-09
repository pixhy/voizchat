import type { Ref } from "vue";
import { ref } from "vue";

const configuration = {
  iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
};
export const peerConnection = ref<RTCPeerConnection | null>(null);
export const remoteStream = ref<MediaStream | null>(null);
export const localStream = ref<MediaStream | null>(null);
export const remoteVideo = ref<HTMLVideoElement | null>(null);
export const localVideo = ref<HTMLVideoElement | null>(null);

const pendingCandidates: RTCIceCandidateInit[] = [];
let remoteDescriptionSet = false;
// Microphone volume tracking

let audioContext: AudioContext | null = null;
let analyser: AnalyserNode | null = null;
let micStream: MediaStream | null = null;
export const micLevel = ref(0);
export const remoteMicLevel = ref(0);
export let animationFrameId: number | null = null;

export async function initPeerConnection(
  channelId: string,
  sendWebsocketCommand: (cmd: string, data: any) => void
) {
  console.log("test", peerConnection.value);
  if (!peerConnection.value) {
    peerConnection.value = new RTCPeerConnection(configuration);
  }

  // ✅ Add local media
  localStream.value = await navigator.mediaDevices.getUserMedia({
    audio: true,
    video: true,
  });

  localStream.value.getTracks().forEach((track) => {
    peerConnection.value?.addTrack(track, localStream.value!);
  });

  if (localVideo.value) {
    localVideo.value.srcObject = localStream.value;
  }
  startMicVisualization(localStream.value!);

  console.log("peerconnection value", peerConnection.value);
  console.log("onice", peerConnection.value.onicecandidate);
  peerConnection.value.onicecandidate = (event) => {
    console.log("ICE Candidate Event:", event);
    if (event.candidate) {
      sendWebsocketCommand("call-ice-candidate", {
        channel_id: channelId,
        candidate: event.candidate,
      });
    }
  };

  console.log(
    "onice candidate handler set:",
    peerConnection.value.onicecandidate
  );
  peerConnection.value.ontrack = (event) => {
    if (!remoteStream.value) {
      remoteStream.value = new MediaStream();
    }
    remoteStream.value.addTrack(event.track);
    console.log("Received remote track:", event.track);
    if (event.track.kind === "audio") {
      startRemoteMicVisualization(remoteStream.value!);
    }
  };

  console.log("Initialized peer connection:", peerConnection.value);
}

export function startMicVisualization(stream: MediaStream) {
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

export async function startCall(
  channelId: string,
  sendWebsocketCommand: (cmd: string, data: any) => void
) {
  await initPeerConnection(channelId, sendWebsocketCommand);

  if (!peerConnection.value) {
    throw new Error("Peer connection not initialized.");
  }

  const offer = await peerConnection.value.createOffer();
  await peerConnection.value.setLocalDescription(offer);

  await new Promise<void>((resolve) => {
    if (!peerConnection.value) return resolve();

    if (peerConnection.value.iceGatheringState === "complete") {
      resolve();
    } else {
      const checkState = () => {
        if (peerConnection.value?.iceGatheringState === "complete") {
          peerConnection.value.removeEventListener(
            "icegatheringstatechange",
            checkState
          );
          resolve();
        }
      };
      peerConnection.value.addEventListener(
        "icegatheringstatechange",
        checkState
      );
    }
  });

  sendWebsocketCommand("call-invite", {
    channel_id: channelId,
    offer: peerConnection.value.localDescription,
  });
}

export async function createOffer(
  peerConnection: Ref<RTCPeerConnection | null>,
  sendWebsocketCommand: (type: string, data: any) => void
) {
  if (!peerConnection.value) {
    throw new Error("Peer connection is not initialized.");
  }

  const offer = await peerConnection.value.createOffer();
  await peerConnection.value.setLocalDescription(offer);
  sendWebsocketCommand("offer", offer);
  console.log("create offer", offer);
}

export async function handleOffer(
  offer: RTCSessionDescriptionInit,
  channelId: string,
  sendWebsocketCommand: (type: string, data: any) => void
) {
  await initPeerConnection(channelId, sendWebsocketCommand);

  if (!peerConnection.value) {
    throw new Error("Peer connection not initialized.");
  }
  console.log("OFFER", offer);

  await peerConnection.value.setRemoteDescription(offer);
  remoteDescriptionSet = true;

  // Add any buffered ICE candidates
  for (const candidate of pendingCandidates) {
    await peerConnection.value.addIceCandidate(candidate);
  }
  pendingCandidates.length = 0;

  const answer = await peerConnection.value.createAnswer();
  await peerConnection.value.setLocalDescription(answer);

  sendWebsocketCommand("call-answer", {
    channel_id: channelId,
    answer,
  });
}

export async function handleAnswer(answer: RTCSessionDescriptionInit) {
  if (peerConnection.value) {
    await peerConnection.value.setRemoteDescription(answer);
  }
}

export async function handleIceCandidate(candidate: RTCIceCandidateInit) {
  if (peerConnection.value) {
    if (remoteDescriptionSet) {
      await peerConnection.value.addIceCandidate(candidate);
    } else {
      pendingCandidates.push(candidate);
    }
  }
}

export function endCall() {
  if (peerConnection.value) {
    peerConnection.value.close();
    peerConnection.value = null;
  }

  if (localStream.value) {
    localStream.value.getTracks().forEach((track) => track.stop());
    localStream.value = null;
  }

  remoteStream.value = null;

  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
    animationFrameId = null;
  }

  console.log("Call ended and resources cleaned up.");
}

export function startRemoteMicVisualization(stream: MediaStream) {
  const remoteAudioContext = new (window.AudioContext ||
    (window as any).webkitAudioContext)();
  const source = remoteAudioContext.createMediaStreamSource(stream);
  const analyserNode = remoteAudioContext.createAnalyser();
  analyserNode.fftSize = 256;
  source.connect(analyserNode);

  const dataArray = new Uint8Array(analyserNode.frequencyBinCount);

  function updateRemoteMicLevel() {
    analyserNode.getByteFrequencyData(dataArray);
    remoteMicLevel.value = Math.max(...dataArray) / 255;

    requestAnimationFrame(updateRemoteMicLevel);
  }

  updateRemoteMicLevel();
}
