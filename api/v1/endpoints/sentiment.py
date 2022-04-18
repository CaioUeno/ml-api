from core.schemas import ml
from fastapi import APIRouter

router = APIRouter()


@router.post("/classify", response_model=ml.PredictedSentiment)
def classify_text(instance: ml.InInstance):

    out = ml.PredictedSentiment(text=instance.text, sentiment=1)

    return out


@router.post("/quantify/{user_id}", response_model=ml.SentimentPrevalence)
def quantify_user(user_id: str, date_from: str = None, date_to: str = None):

    prevalence = {"negative": 0.0, "neutral": 0.0, "positive": 1.0}

    return prevalence


@router.post("/quantify/{hashtag}", response_model=ml.SentimentPrevalence)
def quantify_hashtag(hashtag: str, date_from: str = None, date_to: str = None):

    prevalence = {"negative": 0.0, "neutral": 0.0, "positive": 1.0}

    return prevalence
