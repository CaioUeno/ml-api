import logging
from typing import Any, Union

from core import utils
from core.schemas import user
from db import client
from elasticsearch import exceptions
from fastapi import APIRouter, Response

USERS_INDEX = "users-index"

logger = logging.getLogger(__name__)

logger.setLevel("INFO")

router = APIRouter()


@router.get(
    "/{user_id}", response_model=Union[user.User, user.NotFoundUser], status_code=200
)
def get_user(user_id: str, response: Response) -> Any:

    if client.es.exists(index=USERS_INDEX, id=user_id):
        document = client.es.get(index=USERS_INDEX, id=user_id)["_source"]

    else:
        logger.warning(f"Document not found: {user_id}")
        document = {}
        response.status_code = 404

    return document


@router.post("/", response_model=Union[user.User, user.EmptyUser], status_code=201)
def create_user(new_user: user.NewUser, response: Response) -> Any:

    # validate payload
    username_validation = utils.validate_username(new_user.username)

    if not username_validation:
        logger.error(f"Invalid username: {new_user.username}")
        response.status_code = 400
        return {}

    # check if username already exists
    new_user_id = utils.generate_md5(new_user.username)

    if client.es.exists(index=USERS_INDEX, id=new_user_id):

        logger.error(f"Username already exists: {new_user.username}")
        document = client.es.get(index=USERS_INDEX, id=new_user_id)["_source"]
        response.status_code = 409

        return document

    # create new document otherwise
    new_document = {
        "id": utils.generate_md5(new_user.username),
        "username": new_user.username,
        "joined_at": utils.time_now(),
        "follows": [],
        "followers": [],
    }

    client.es.create(index=USERS_INDEX, id=new_user_id, body=new_document)

    return new_document


@router.delete(
    "/{user_id}", response_model=Union[user.User, user.NotFoundUser], status_code=200
)
def delete_user(user_id: str, response: Response) -> Any:

    if client.es.exists(index=USERS_INDEX, id=user_id):
        document = client.es.get(index=USERS_INDEX, id=user_id)["_source"]
        client.es.delete(index=USERS_INDEX, id=user_id)

        return document

    else:
        logger.warning(f"Document not found: {user_id}")
        response.status_code = 404
        return {}


@router.put(
    "/{follower_id}/follow/{followed_id}",
    response_model=Union[user.User, user.NotFoundUser],
    status_code=200,
)
def follow(follower_id: str, followed_id: str, response: Response) -> Any:

    if not client.es.exists(index=USERS_INDEX, id=follower_id):
        logger.error(f"")
        response.status_code = 404
        return {}

    if not client.es.exists(index=USERS_INDEX, id=followed_id):
        logger.error(f"")
        response.status_code = 404
        return {}

    # same for both
    followed_at = utils.time_now()

    # update follower user document
    client.es.update(
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
    client.es.update(
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

    document = client.es.get(index=USERS_INDEX, id=follower_id)["_source"]

    return document


@router.put("/{user_id}/unfollow/{other_id}", response_model=user.User, status_code=200)
def unfollow(user_id: str, other_id: str) -> Any:
    return NotImplementedError()
