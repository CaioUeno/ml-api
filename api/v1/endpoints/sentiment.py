import json
import logging
from typing import Union

import db
import ml
from core import utils
from core.schemas import mlio
from fastapi import APIRouter, Response

USERS_INDEX = utils.get_config("elasticsearch.indices", "users")
TWEETS_INDEX = utils.get_config("elasticsearch.indices", "tweets")

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/classify",
    response_model=Union[mlio.PredictedSentiment, mlio.InInstance],
    status_code=200,
)
def classify_text(instance: mlio.InInstance, response: Response):

    logging.info(f'Classify text: "{instance.text}"')

    if instance.text == "":

        logging.warning(f"Text is an empty string.")
        response.status_code = 500

        return instance

    logging.debug("Predict text.")
    pred_sentiment = ml.bow.predict([instance.text])[0]

    logging.debug("Instantiate response model.")
    out = mlio.PredictedSentiment(
        text=instance.text, sentiment=utils.sentiment_to_str(pred_sentiment)
    )

    return out


@router.post(
    "/quantify/user/{user_id}",
    response_model=Union[mlio.SentimentPrevalence, mlio.Empty],
)
def quantify_user(
    user_id: str, response: Response, date_from: str = None, date_to: str = None
):

    logging.info(f"Quantify tweets of user: {user_id}.")

    if not db.es.exists(index=USERS_INDEX, id=user_id):

        logging.error(f"User's document not found: id={user_id}.")
        response.status_code = 404

        return {}

    query = {
        "query": {
            "bool": {
                "filter": [
                    {"term": {"author_id": user_id}},
                ]
            }
        },
        "aggs": {"sentiments": {"terms": {"field": "sentiment"}}},
    }

    logging.debug(f"Parse date filters to range clause.")
    range_clause = utils.date_filter(date_from, date_to)

    if range_clause is not None:
        query["query"]["bool"]["filter"].append(range_clause)

    logging.info(f"Send request to Elasticsearch - search API.")
    logging.debug(f"Search query: {json.dumps(query)}")
    buckets = db.es.search(index=TWEETS_INDEX, body=query)["aggregations"][
        "sentiments"
    ]["buckets"]

    prevalence = {"negative": 0, "neutral": 0, "positive": 0}

    for b in buckets:
        prevalence[utils.sentiment_to_str(b["key"])] = b["doc_count"]

    return prevalence


@router.post(
    "/quantify/hashtag/{hashtag}",
    response_model=Union[mlio.SentimentPrevalence, mlio.Empty],
)
def quantify_hashtag(
    hashtag: str, response: Response, date_from: str = None, date_to: str = None
):

    logging.info(f"Quantify tweets mentioning hashtag: #{hashtag}.")

    query = {
        "query": {"bool": {"filter": [{"term": {"hashtags": "#" + hashtag}}]}},
        "aggs": {"sentiments": {"terms": {"field": "sentiment"}}},
    }

    logging.debug(f"Parse date filters to range clause.")
    range_clause = utils.date_filter(date_from, date_to)

    if range_clause is not None:
        query["query"]["bool"]["filter"].append(range_clause)

    logging.info(f"Send request to Elasticsearch - search API.")
    logging.debug(f"Search query: {json.dumps(query)}")
    buckets = db.es.search(index=TWEETS_INDEX, body=query,)["aggregations"][
        "sentiments"
    ]["buckets"]

    prevalence = {"negative": 0, "neutral": 0, "positive": 0}

    for b in buckets:
        prevalence[utils.sentiment_to_str(b["key"])] = b["doc_count"]

    return prevalence
