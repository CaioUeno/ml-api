import logging
from typing import Union

import db
from core import utils
from core.schemas import user
from fastapi import APIRouter, Response

USERS_INDEX = utils.get_config("elasticsearch.indices", "users")
TWEETS_INDEX = utils.get_config("elasticsearch.indices", "tweets")

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{user_id}", response_model=Union[user.User, user.EmptyUser], status_code=200
)
def get_user(user_id: str, response: Response):

    if not db.es.exists(index=USERS_INDEX, id=user_id):

        logger.error(f"User's document not found: id={user_id}")
        response.status_code = 404

        return {}

    else:
        user_document = db.es.get(index=USERS_INDEX, id=user_id)["_source"]
        return user_document


@router.post("/", response_model=Union[user.User, user.EmptyUser], status_code=201)
def create_user(new_user: user.NewUser, response: Response):

    # validate payload
    username_validation = utils.validate_username(new_user.username)

    if not username_validation:

        logger.error(f"Invalid username: {new_user.username}")
        response.status_code = 400

        return {}

    # check if username already exists
    new_user_id = utils.generate_md5(new_user.username)

    if db.es.exists(index=USERS_INDEX, id=new_user_id):

        logger.error(f"Username already exists: {new_user.username}")
        user_document = db.es.get(index=USERS_INDEX, id=new_user_id)["_source"]
        response.status_code = 409

        return user_document

    # create new document otherwise
    new_user_document = {
        "id": utils.generate_md5(new_user.username),
        "username": new_user.username,
        "joined_at": utils.time_now(),
        "follows": [],
        "followers": [],
    }

    db.es.create(index=USERS_INDEX, id=new_user_id, body=new_user_document)

    return new_user_document


@router.delete(
    "/{user_id}", response_model=Union[user.User, user.EmptyUser], status_code=200
)
def delete_user(user_id: str, response: Response):

    if not db.es.exists(index=USERS_INDEX, id=user_id):

        logger.error(f"User's document not found: {user_id}")
        response.status_code = 404

        return {}

    user_document = db.es.get(index=USERS_INDEX, id=user_id)["_source"]

    # update users who user_id follows
    for follow_user in user_document["follows"]:

        db.es.update(
            index=USERS_INDEX,
            id=follow_user["id"],
            body={
                "script": {
                    "source": """
                            ctx._source.followers.removeIf(f -> f.id == params.user.id)
                        """,
                    "lang": "painless",
                    "params": {"user": {"id": user_id}},
                }
            },
        )

    # update users who follow user_id
    for follower_user in user_document["followers"]:

        db.es.update(
            index=USERS_INDEX,
            id=follower_user["id"],
            body={
                "script": {
                    "source": """
                            ctx._source.follows.removeIf(f -> f.id == params.user.id)
                        """,
                    "lang": "painless",
                    "params": {"user": {"id": user_id}},
                }
            },
        )

    # clean document fields to return
    user_document["follows"] = []
    user_document["followers"] = []

    # delete user's tweets and retweets
    db.es.delete_by_query(
        index=TWEETS_INDEX,
        body={
            "query": {
                "bool": {
                    "filter": {
                        "bool": {
                            "should": [
                                {"term": {"author_id": user_id}},
                                {"term": {"user_id": user_id}},
                            ]
                        }
                    }
                }
            }
        },
    )

    # update tweets that user_id retweeted and/or like
    db.es.update_by_query(
        index=TWEETS_INDEX,
        body={
            "query": {
                "bool": {
                    "filter": {
                        "nested": {
                            "path": "retweets",
                            "query": {"term": {"retweets.id": user_id}},
                        }
                    }
                }
            },
            "script": {
                "source": """
                            ctx._source.retweets.removeIf(f -> f.id == params.user.id)
                        """,
                "lang": "painless",
                "params": {"user": {"id": user_id}},
            },
        },
        refresh=True,
    )

    db.es.update_by_query(
        index=TWEETS_INDEX,
        body={
            "query": {
                "bool": {
                    "filter": {
                        "nested": {
                            "path": "likes",
                            "query": {"term": {"likes.id": user_id}},
                        }
                    }
                }
            },
            "script": {
                "source": """
                            ctx._source.likes.removeIf(f -> f.id == params.user.id)
                        """,
                "lang": "painless",
                "params": {"user": {"id": user_id}},
            },
        },
        refresh=True,
    )

    # permanently delete it
    db.es.delete(index=USERS_INDEX, id=user_id)

    return user_document


@router.put(
    "/{follower_id}/follow/{followed_id}",
    response_model=Union[user.User, user.EmptyUser],
    status_code=200,
)
def follow(follower_id: str, followed_id: str, response: Response):

    if not db.es.exists(index=USERS_INDEX, id=follower_id):

        logger.error(f"User's document not found: {follower_id} (follower)")
        response.status_code = 404

        return {}

    if not db.es.exists(index=USERS_INDEX, id=followed_id):

        logger.error(f"User's document not found: {follower_id} (followed)")
        response.status_code = 404

        # return follower user document
        follower_document = db.es.get(index=USERS_INDEX, id=follower_id)["_source"]

        return follower_document

    # user can not follow themselves
    if follower_id == followed_id:

        logger.error(
            f"User can not follow themselves: follower_id ({follower_id}) == followed_id ({followed_id})"
        )
        response.status_code = 500

        # return follower user document
        follower_document = db.es.get(index=USERS_INDEX, id=follower_id)["_source"]

        return follower_document

    # same for both
    followed_at = utils.time_now()

    # update follower user document
    db.es.update(
        index=USERS_INDEX,
        id=follower_id,
        body={
            "script": {
                "source": """
                                if (!ctx._source.follows.contains(ctx._source.follows.find(f -> f.id == params.user.id))) {
                                        ctx._source.follows.add(params.user)
                                    }
                          """,
                "lang": "painless",
                "params": {"user": {"id": followed_id, "followed_at": followed_at}},
            }
        },
    )

    # update followed user document
    db.es.update(
        index=USERS_INDEX,
        id=followed_id,
        body={
            "script": {
                "source": """
                                if (!ctx._source.followers.contains(ctx._source.followers.find(f -> f.id == params.user.id))) {
                                        ctx._source.followers.add(params.user)
                                    }
                          """,
                "lang": "painless",
                "params": {"user": {"id": follower_id, "followed_at": followed_at}},
            }
        },
    )

    # return follower user document
    follower_document = db.es.get(index=USERS_INDEX, id=follower_id)["_source"]

    return follower_document


@router.put(
    "/{follower_id}/unfollow/{followed_id}",
    response_model=Union[user.User, user.EmptyUser],
    status_code=200,
)
def unfollow(follower_id: str, followed_id: str, response: Response):

    if not db.es.exists(index=USERS_INDEX, id=follower_id):

        logger.error(f"User's document not found: {follower_id} (follower)")
        response.status_code = 404

        return {}

    if not db.es.exists(index=USERS_INDEX, id=followed_id):

        logger.error(f"User's document not found: {followed_id} (followed)")
        response.status_code = 404

        # return follower document
        follower_document = db.es.get(index=USERS_INDEX, id=follower_id)["_source"]

        return follower_document

    if follower_id == followed_id:

        logger.error(
            f"User can not unfollow themselves: follower_id ({follower_id}) == followed_id ({followed_id})"
        )
        response.status_code = 500

        # return follower document
        follower_document = db.es.get(index=USERS_INDEX, id=follower_id)["_source"]

        return follower_document

    # update follower user document
    db.es.update(
        index=USERS_INDEX,
        id=follower_id,
        body={
            "script": {
                "source": """
                                ctx._source.follows.removeIf(f -> f.id == params.user.id)
                          """,
                "lang": "painless",
                "params": {"user": {"id": followed_id}},
            }
        },
    )

    # update followed user document
    db.es.update(
        index=USERS_INDEX,
        id=followed_id,
        body={
            "script": {
                "source": """
                                ctx._source.followers.removeIf(f -> f.id == params.user.id)
                          """,
                "lang": "painless",
                "params": {"user": {"id": follower_id}},
            }
        },
    )

    # return follower user document
    follower_document = db.es.get(index=USERS_INDEX, id=follower_id)["_source"]

    return follower_document
