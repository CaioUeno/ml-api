from pydantic import BaseModel

class Empty(BaseModel):
    pass

class InInstance(BaseModel):
    text: str


class PredictedSentiment(InInstance):
    sentiment: str
    confidence: float


class SentimentPrevalence(BaseModel):
    negative: int
    neutral: int
    positive: int
