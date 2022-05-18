from typing import Union
from core.schemas import ml
from fastapi import APIRouter, Response
import db

router = APIRouter()
USERS_INDEX = "users-index"


@router.post(
    "/classify",
    response_model=Union[ml.PredictedSentiment, ml.InInstance],
    status_code=200,
)
def classify_text(instance: ml.InInstance, response: Response):

    if instance.text == "":
        response.status_code = 500
        return instance

    out = ml.PredictedSentiment(text=instance.text, sentiment="positive")

    return out


@router.post(
    "/quantify/user/{user_id}", response_model=Union[ml.SentimentPrevalence, ml.Empty]
)
def quantify_user(
    user_id: str, response: Response, date_from: str = None, date_to: str = None
):
    print(date_from)
    print(date_to)
    if not db.es.exists(index=USERS_INDEX, id=user_id):
        response.status_code = 404
        return {}

    buckets = db.es.search(
        index="tweets-index",
        body={
            "query": {"bool": {"filter": {"term": {"author_id": user_id}}}},
            "aggs": {"sentiments": {"terms": {"field": "sentiment"}}},
        },
    )["aggregations"]["sentiments"]["buckets"]

    mapping_sentiment = {-1: "negative", 0: "neutral", 1: "positive"}
    prevalence = {}
    for b in buckets:
        prevalence[mapping_sentiment[b["key"]]] = b["doc_count"]

    # prevalence = {"negative": 0.0, "neutral": 0.0, "positive": 1.0}

    return prevalence


@router.post(
    "/quantify/hashtag/{hashtag}",
    response_model=Union[ml.SentimentPrevalence, ml.Empty],
)
def quantify_hashtag(
    hashtag: str, response: Response, date_from: str = None, date_to: str = None
):

    buckets = db.es.search(
        index="tweets-index",
        body={
            "query": {"bool": {"filter": {"term": {"hashtags": "#" + hashtag}}}},
            "aggs": {"sentiments": {"terms": {"field": "sentiment"}}},
        },
    )["aggregations"]["sentiments"]["buckets"]

    mapping_sentiment = {-1: "negative", 0: "neutral", 1: "positive"}
    prevalence = {}
    for b in buckets:
        prevalence[mapping_sentiment[b["key"]]] = b["doc_count"]
    print(prevalence)
    return prevalence
