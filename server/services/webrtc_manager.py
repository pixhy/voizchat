import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from pydantic import BaseModel

class Message(BaseModel):
    cmd: str
    data: str

class WebRTCManager:
    def __init__(self):
        self.connections = {}

    async def handle_offer(self, websocket: WebSocket, offer_sdp: str):
        pc = RTCPeerConnection()
        offer = RTCSessionDescription(sdp=offer_sdp, type="offer")
        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        await websocket.send_text(f"answer {answer.sdp}")

    async def handle_candidate(self, websocket: WebSocket, candidate_sdp: str):
        # Handle ICE candidates here
        pass

    async def handle_call_initiated(self, user_id: str):
        # Forward the call notification to the recipient
        websockets = self.connections.get(user_id)
        if websockets:
            for websocket in websockets:
                if websocket.client_state == WebSocketState.CONNECTED:
                    # Send the incoming call notification to the recipient
                    await websocket.send_text(f"Incoming call from user {user_id}")

    async def on_message(self, websocket: WebSocket, message: str):
        # Process WebSocket message
        message_obj = json.loads(message)
        if message_obj["cmd"] == "call_initiated":
            await self.handle_call_initiated(message_obj["data"]["userId"])
        elif message_obj["cmd"] == "offer":
            await self.handle_offer(websocket, message_obj["data"]["offer_sdp"])
        elif message_obj["cmd"] == "candidate":
            await self.handle_candidate(websocket, message_obj["data"]["candidate_sdp"])