from pydantic import BaseModel


class InInstance(BaseModel):
    text: str


class PredictedSentiment(InInstance):
    sentiment: str


class SentimentPrevalence(BaseModel):
    negative: int
    neutral: int
    positive: int
