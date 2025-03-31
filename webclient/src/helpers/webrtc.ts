import type { Ref } from "vue";
import { ref } from "vue";

const configuration = {
  iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
};
const peerConnection = ref<RTCPeerConnection | null>(new RTCPeerConnection(configuration));
const remoteStream = ref<MediaStream | null>(null);

export function initPeerConnection(sendWebsocketCommand: (cmd: string, data: any) => void) {
  console.log("test", peerConnection.value)
  if (!peerConnection.value) {
    peerConnection.value = new RTCPeerConnection(configuration);

    console.log("peerconnection value", peerConnection.value)
    peerConnection.value.onicecandidate = (event) => {
      if (event.candidate) {
        sendWebsocketCommand("call-ice-candidate", event.candidate);
      }
    };
    peerConnection.value.ontrack = (event) => {
      if (!remoteStream.value) {
        remoteStream.value = new MediaStream();
      }
      remoteStream.value.addTrack(event.track);
      console.log("Received remote track:", event.track);
    };

    console.log("Initialized peer connection:", peerConnection.value);
  }
  
}

export async function startCall(channelId: string, sendWebsocketCommand: (cmd: string, data: any) => void) {
  initPeerConnection(sendWebsocketCommand);

  if (!peerConnection.value) {
    throw new Error("Peer connection not initialized.");
  }

  const offer = await peerConnection.value.createOffer();
  await peerConnection.value.setLocalDescription(offer);

  sendWebsocketCommand("call-invite", {
    channel_id: channelId,
    offer
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
  console.log("create offer", offer, );
  
}

export async function handleOffer(offer: RTCSessionDescriptionInit, channelId: string, sendWebsocketCommand: (type: string, data: any) => void) {
  initPeerConnection(sendWebsocketCommand);

  if (!peerConnection.value) {
    throw new Error("Peer connection not initialized.");
  }
  console.log("OFFER", offer)
  await peerConnection.value.setRemoteDescription(offer);
  const answer = await peerConnection.value.createAnswer();
  await peerConnection.value.setLocalDescription(answer);

  sendWebsocketCommand("call-answer", {
    channel_id: channelId,
    answer
  });
}

export async function handleAnswer(answer: RTCSessionDescriptionInit){
  if (peerConnection.value) {
    await peerConnection.value.setRemoteDescription(answer);
  }
}

export async function handleIceCandidate(candidate: RTCIceCandidateInit){
  if (peerConnection.value) {
    await peerConnection.value.addIceCandidate(candidate);
  }
}
export { remoteStream, peerConnection };
