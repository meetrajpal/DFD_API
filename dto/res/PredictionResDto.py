from pydantic import BaseModel


class PredictionResDto(BaseModel):
    pred_id: int
    user_id: int
    pred_label: str
    filename: str
    source: str
    url: str
