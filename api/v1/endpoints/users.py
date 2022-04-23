import logging
from typing import Any

from core import utils
from core.schemas import user
from db import client
from elasticsearch import exceptions
from fastapi import APIRouter

USERS_INDEX = "users-index"

logger = logging.getLogger(__name__)

logger.setLevel("INFO")

router = APIRouter()


@router.get("/{user_id}", response_model=user.User, status_code=200)
def get_user(user_id: str) -> Any:
    return NotImplementedError()


@router.post("/", response_model=user.User, status_code=201)
def create_user(new_user: user.NewUser) -> Any:
    return NotImplementedError()


@router.delete("/{user_id}", response_model=user.User, status_code=200)
def delete_user(user_id: str) -> Any:
    return NotImplementedError()


@router.put("/{user_id}/follow/{other_id}", response_model=user.User, status_code=200)
def follow(user_id: str, other_id: str) -> Any:
    return NotImplementedError()


@router.put("/{user_id}/unfollow/{other_id}", response_model=user.User, status_code=200)
def unfollow(user_id: str, other_id: str) -> Any:
    return NotImplementedError()
