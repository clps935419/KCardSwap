"""Friends use cases"""
from .send_friend_request_use_case import SendFriendRequestUseCase
from .accept_friend_request_use_case import AcceptFriendRequestUseCase
from .block_user_use_case import BlockUserUseCase

__all__ = [
    "SendFriendRequestUseCase",
    "AcceptFriendRequestUseCase",
    "BlockUserUseCase",
]
