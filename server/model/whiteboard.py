from pydantic import BaseModel

class WhiteboardDrawData(BaseModel):
    channel_id: str
    x: int
    y: int
    prevX: int
    prevY: int
    line_width: int
    line_color: str