from typing import Any

from core.schemas import user
from core import utils
from fastapi import APIRouter

router = APIRouter()


@router.get("/{user_id}", response_model=user.User)
def get_user(user_id: str) -> Any:

    fake_user = {
        "id": "dde",
        "username": "caio",
        "joined_at": utils.time_now(),
        "follows": [
            {
                "id": "abc",
                "followed_at": utils.time_now(),
            }
        ],
        "followers": [],
    }

    return fake_user


@router.post("/", response_model=user.User)
def create_user(new_user: user.NewUser) -> Any:

    new_user = user.User(
        id="dde",
        username=new_user["username"],
        joined_at=utils.time_now(),
        follows=[],
        followers=[],
    )

    return new_user


@router.delete("/{user_id}", response_model=user.User)
def delete_user(user_id: str) -> Any:

    return {
        "id": "dde",
        "username": "caio",
        "joined_at": utils.time_now(),
        "follows": [{"id": "abc", "followed_at": utils.time_now()}],
        "followers": [],
    }


@router.post("/{user_id}/follow/{other_id}", response_model=user.User)
def follow(user_id: str, other_id: str) -> Any:
    return {
        "id": "dde",
        "username": "caio",
        "joined_at": utils.time_now(),
        "follows": [{"id": "abc", "followed_at": utils.time_now()}],
        "followers": [],
    }


@router.delete("/{user_id}/unfollow/{other_id}", response_model=user.User)
def unfollow(user_id: str, other_id: str) -> Any:
    return {
        "id": "dde",
        "username": "caio",
        "joined_at": utils.time_now(),
        "follows": [{"id": "abc", "followed_at": utils.time_now()}],
        "followers": [],
    }
