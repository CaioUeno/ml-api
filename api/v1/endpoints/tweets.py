import json
import logging
from typing import List, Union

import db
import ml
from core import utils
from core.schemas import tweet
from fastapi import APIRouter, Response

USERS_INDEX = utils.get_config("elasticsearch.indices", "users")
TWEETS_INDEX = utils.get_config("elasticsearch.indices", "tweets")

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{tweet_id}",
    response_model=Union[tweet.Tweet, tweet.ReferenceTweet, tweet.EmptyTweet],
    status_code=200,
)
def get_tweet(tweet_id: str, response: Response):

    logging.info(f"Retrieve tweet: {tweet_id}.")

    if not db.es.exists(index=TWEETS_INDEX, id=tweet_id):

        logger.error(f"(Re)Tweet's document not found: id={tweet_id}.")
        response.status_code = 404

        return {}

    else:

        tweet_document = db.es.get(index=TWEETS_INDEX, id=tweet_id)["_source"]

        logging.debug(f"Retrieved document: {json.dumps(tweet_document)}")

        return tweet_document


@router.get(
    "/user/{user_id}",
    response_model=List[tweet.Tweet],
    status_code=200,
)
def get_user_tweets(user_id: str, response: Response):

    logging.info(f"Retrieve tweets of user: {user_id}.")

    if not db.es.exists(index=USERS_INDEX, id=user_id):

        logger.error(f"User's document not found: {user_id}")
        response.status_code = 404

        return []

    else:

        query = {"query": {"bool": {"filter": {"term": {"author_id": user_id}}}}}

        logging.info(f"Send request to Elasticsearch - search API.")
        logging.debug(f"Search query: {json.dumps(query)}")

        # search API -> scroll API (what if user have more than 10k tweets?)
        hit_documents = db.es.search(body=query, index=TWEETS_INDEX)["hits"]["hits"]

        user_tweets = [hit["_source"] for hit in hit_documents]

        return user_tweets


@router.get(
    "/{user_id}/timeline",
    response_model=List[tweet.Tweet],
    status_code=200,
)
def get_user_timeline(user_id: str):
    return NotImplementedError()


@router.post(
    "/{user_id}/tweet",
    response_model=Union[tweet.Tweet, tweet.EmptyTweet],
    status_code=201,
)
def publish_tweet(user_id: str, new_tweet: tweet.NewTweet, response: Response):

    logging.info(f'User ({user_id}) publishes new tweet: "{new_tweet.text}".')

    if not db.es.exists(index=USERS_INDEX, id=user_id):

        logger.error(f"User's document not found: {user_id}.")
        response.status_code = 404

        return {}

    user_document = db.es.get(index=USERS_INDEX, id=user_id)["_source"]

    # check if same user already published the same text
    possible_tweet_id = utils.generate_md5(new_tweet.text + user_document["username"])

    if db.es.exists(index=TWEETS_INDEX, id=possible_tweet_id):

        logger.warning(f"User already tweeted the same text.")
        response.status_code = 409

        tweet_document = db.es.get(
            index=TWEETS_INDEX,
            id=possible_tweet_id,
        )["_source"]

        return tweet_document

    logging.debug(f"Instantiate classifier and predict new text.")
    clf = ml.Dummy()

    logging.debug(f"Instantiate new tweet's document.")
    # new tweet!
    new_tweet = tweet.Tweet(
        id=utils.generate_md5(new_tweet.text + user_document["username"]),
        author_id=user_document["id"],
        tweeted_at=utils.time_now(),
        text=new_tweet.text,
        sentiment=clf.single_prediction(new_tweet.text),
        hashtags=utils.extract_hashtags(new_tweet.text),
        retweets=[],
        likes=[],
    )

    logging.info(f"Send request to Elasticsearch - create document.")
    logging.debug(f"Document body: {json.dumps(new_tweet.dict())}")
    db.es.create(
        index=USERS_INDEX,
        id=new_tweet.id,
        body=new_tweet.dict(),
    )

    logging.debug(f"New tweet's document created.")

    return new_tweet.dict()


@router.post(
    "/{user_id}/retweet/{tweet_id}",
    response_model=Union[tweet.ReferenceTweet, tweet.EmptyReferenceTweet],
    status_code=201,
)
def retweet(user_id: str, tweet_id: str, response: Response):

    logging.info(f"User ({user_id}) retweets tweet ({tweet_id}).")

    if not db.es.exists(index=USERS_INDEX, id=user_id):

        logger.error(f"User's document not found: {user_id}.")
        response.status_code = 404

        return {}

    if not db.es.exists(index=TWEETS_INDEX, id=tweet_id):

        logger.error(f"Tweet's document not found: {tweet_id}.")
        response.status_code = 404

        return {}

    # check if user_id is the tweet's author
    tweet_document = db.es.get(index=TWEETS_INDEX, id=tweet_id)["_source"]

    if user_id == tweet_document["author_id"]:

        logger.error(f"Users can not retweet their own tweet.")
        response.status_code = 500

        return {}

    # same for both
    retweeted_at = utils.time_now()

    script = {
        "script": {
            "source": """
                                if (!ctx._source.retweets.contains(ctx._source.retweets.find(f -> f.id == params.user.id))) {
                                        ctx._source.retweets.add(params.user)
                                    }
                          """,
            "lang": "painless",
            "params": {"user": {"id": user_id, "retweeted_at": retweeted_at}},
        }
    }

    logging.info(f"Send request to Elasticsearch - update API.")
    logging.debug(f"Script body: {json.dumps(script)}")

    # update tweet's document
    db.es.update(index=TWEETS_INDEX, id=tweet_id, body=script)

    logging.info(f"Instantiate new retweet's document.")
    # new retweet!
    new_retweet = tweet.ReferenceTweet(
        id=utils.generate_md5(tweet_id + user_id),
        user_id=user_id,
        referenced_at=retweeted_at,
        tweet_id=tweet_id,
    )

    logging.info(f"Send request to Elasticsearch - create document.")
    logging.debug(f"Document body: {json.dumps(new_retweet.dict())}")
    db.es.create(
        index=USERS_INDEX,
        id=new_retweet.id,
        body=new_retweet.dict(),
    )

    logging.debug(f"New retweet's document created.")

    return new_retweet


@router.post(
    "/{user_id}/like/{tweet_id}",
    response_model=Union[tweet.Tweet, tweet.EmptyTweet],
    status_code=201,
)
def like(user_id: str, tweet_id: str, response: Response):

    logging.info(f"User ({user_id}) likes tweet ({tweet_id}).")

    if not db.es.exists(index=USERS_INDEX, id=user_id):

        logger.error(f"User's document not found: {user_id}.")
        response.status_code = 404

        return {}

    if not db.es.exists(index=TWEETS_INDEX, id=tweet_id):

        logger.error(f"Tweet's document not found: {tweet_id}.")
        response.status_code = 404

        return {}

    # check if it is a tweet or a retweet
    unknown_document = db.es.get(index=TWEETS_INDEX, id=tweet_id)["_source"]

    if "referenced_at" in unknown_document.keys():

        logger.error(f"It is not possible to like a retweet (only tweets).")
        response.status_code = 500

        return {}

    script = {
        "script": {
            "source": """
                                if (!ctx._source.likes.contains(ctx._source.likes.find(f -> f.id == params.user.id))) {
                                        ctx._source.likes.add(params.user)
                                    }
                          """,
            "lang": "painless",
            "params": {"user": {"id": user_id, "liked_at": utils.time_now()}},
        }
    }

    logging.info(f"Send request to Elasticsearch - update API.")
    logging.debug(f"Script body: {json.dumps(script)}")

    # update tweet's document
    db.es.update(index=TWEETS_INDEX, id=tweet_id, body=script, refresh=True)

    tweet_document = db.es.get(index=TWEETS_INDEX, id=tweet_id)["_source"]

    return tweet_document


@router.delete(
    "/{tweet_id}",
    response_model=Union[tweet.Tweet, tweet.ReferenceTweet, tweet.EmptyTweet],
    status_code=200,
)
def delete_tweet(tweet_id: str, response: Response):

    logging.info(f"Delete tweet: {tweet_id}.")

    if not db.es.exists(index=TWEETS_INDEX, id=tweet_id):

        logger.error(f"Tweet's document not found: {tweet_id}.")
        response.status_code = 404

        return {}

    # check if it is a tweet or a retweet
    unknown_document = db.es.get(index=TWEETS_INDEX, id=tweet_id)["_source"]

    # if has "referenced_at" field it is a retweet
    if "referenced_at" in unknown_document.keys():

        script = {
            "script": {
                "source": """
                                    ctx._source.retweets.removeIf(f -> f.id == params.user.id)
                            """,
                "lang": "painless",
                "params": {"user": {"id": unknown_document["user_id"]}},
            },
        }

        logging.info(f"Send request to Elasticsearch - update API.")
        logging.debug(f"Script body: {json.dumps(script)}")

        # remove retweet from original tweet
        db.es.update(
            index=TWEETS_INDEX,
            id=unknown_document["tweet_id"],
            body=script,
            refresh=True,
        )

    # tweet otherwise
    else:

        query = {"query": {"bool": {"filter": {"term": {"tweet_id": tweet_id}}}}}

        logging.info(f"Send request to Elasticsearch - delete_by_query API.")
        logging.debug(f"Query body: {json.dumps(query)}")

        # delete all its retweets
        db.es.delete_by_query(index=TWEETS_INDEX, body=query, refresh=True)

    # permanently delete it
    db.es.delete(index=TWEETS_INDEX, id=tweet_id)

    return unknown_document
