﻿from pydantic import BaseModel

class CallInvite(BaseModel):
    caller_id: str
    offer: dict

class CallAnswer(BaseModel):
    caller_id: str
    answer: dict