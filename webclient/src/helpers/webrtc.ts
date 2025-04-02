import { ref } from "vue";

const peerConnection = ref<RTCPeerConnection | null>(null);
const remoteStream = ref<MediaStream | null>(null);

const configuration = {
  iceServers: [
    { urls: "stun:stun.l.google.com:19302" },
    {
      urls: "turn:relay.metered.ca:80",
      username: "openai",
      credential: "openai",
    },
  ],
};

export function initPeerConnection(
  sendWebsocketCommand: any,
  channelId: string
) {
  peerConnection.value = new RTCPeerConnection(configuration);

  peerConnection.value.onicecandidate = (event) => {
    if (event.candidate) {
      sendWebsocketCommand("call-ice-candidate", {
        channel_id: channelId,
        candidate: event.candidate,
      });
    }
  };

  peerConnection.value.ontrack = (event) => {
    if (!remoteStream.value) remoteStream.value = new MediaStream();
    remoteStream.value.addTrack(event.track);
  };

  return peerConnection.value;
}

export async function handleOffer(
  offer: RTCSessionDescriptionInit,
  channelId: string,
  sendWebsocketCommand: any
) {
  await peerConnection.value!.setRemoteDescription(
    new RTCSessionDescription(offer)
  );
  const answer = await peerConnection.value!.createAnswer();
  await peerConnection.value!.setLocalDescription(answer);
  sendWebsocketCommand("call-answer", {
    channel_id: channelId,
    answer,
  });
}

export async function handleAnswer(answer: RTCSessionDescriptionInit) {
  await peerConnection.value!.setRemoteDescription(
    new RTCSessionDescription(answer)
  );
}

export async function handleIceCandidate(candidate: RTCIceCandidateInit) {
  await peerConnection.value!.addIceCandidate(new RTCIceCandidate(candidate));
}

export { remoteStream };
