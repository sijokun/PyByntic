from typing import Annotated, Optional

from pybyntic import AnnotatedBaseModel
from pybyntic.types import Nullable, String, UInt32


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[Optional[str], Nullable[String]]


def _test_user(user: User):
    # Serialize to bytes
    serialized = user.serialize()

    # Deserialize from bytes
    deserialized_user = User.deserialize(serialized)

    # Verify all fields match
    assert deserialized_user.user_id == user.user_id
    assert deserialized_user.username == user.username

    # Verify the objects are equal
    assert deserialized_user == user


def test_not_null():
    user = User(user_id=123, username="admin")
    _test_user(user)


def test_null():
    user = User(user_id=123, username=None)
    _test_user(user)


class Post(AnnotatedBaseModel):
    post_id: Annotated[int, UInt32]
    tags: Annotated[list[Optional[str]], list[Nullable[String]]]


def _test_post(post: Post):
    # Serialize to bytes
    serialized = post.serialize()

    # Deserialize from bytes
    deserialized_post = Post.deserialize(serialized)

    # Verify all fields match
    assert deserialized_post.post_id == post.post_id
    assert deserialized_post.tags == post.tags

    # Verify the objects are equal
    assert deserialized_post == post


def test_list_all_not_null():
    post = Post(post_id=1, tags=["red", "green", "blue"])
    _test_post(post)


def test_list_some_null():
    post = Post(post_id=2, tags=["red", None, "blue", None])
    _test_post(post)


def test_list_all_null():
    post = Post(post_id=3, tags=[None, None, None])
    _test_post(post)


def test_list_empty():
    post = Post(post_id=4, tags=[])
    _test_post(post)
