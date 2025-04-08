from pydantic import BaseModel

class CallInvite(BaseModel):
    caller_id: str
    offer: dict

class CallAnswer(BaseModel):
    caller_id: str
    answer: dict

class CallIceCandidate(BaseModel):
    caller_id: str
    candidate: dict

class CallEnd(BaseModel):
    caller_id: str
    channel_id: str