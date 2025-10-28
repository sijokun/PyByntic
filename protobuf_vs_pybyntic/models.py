from pybyntic import AnnotatedBaseModel
from pybyntic.types import (
	DateTime32,
	Float64,
	Int32,
	Int64,
	String,
	StringJson,
	UInt16,
	UInt32,
)

from typing import Annotated, Any


import datetime
import random

class Item(AnnotatedBaseModel):
    item_id: Annotated[int, UInt16]
    type: Annotated[str, String]
    rate: Annotated[int, UInt32]
    capacity: Annotated[int, Int32]
    start: Annotated[datetime.datetime, DateTime32]
    end: Annotated[datetime.datetime, DateTime32]
    updated_at: Annotated[datetime.datetime, DateTime32]


class User(AnnotatedBaseModel):
    id: Annotated[int, Int64] = 0  # User ID
    first_name: Annotated[str, String]
    last_name: Annotated[str, String]
    referral_count: Annotated[int, UInt32]
    mentions_count: Annotated[int, UInt32]
    balance: Annotated[int, Int64]  # Sum of all transactions COULD BE NEGATIVE
    spent: Annotated[float, Float64]
    items: list[Item]
    tasks: Annotated[list[str], list[String]]

    user_referral_code: Annotated[str, String] = ""

    last_update: Annotated[datetime.datetime, DateTime32]
    reactions: Annotated[int, UInt32] = 0


def generate_random_item() -> Item:
	"""Generate a random item for testing purposes."""
	return Item(
		item_id=random.randint(0, 2**16 - 1),
		type=random.choice(["gold", "diamond", "silver", "bronze", "elite"]),
		rate=random.randint(1, 2**32 - 1),
		capacity=random.randint(-2**31, 2**31 - 1),
		start=datetime.datetime.utcnow(),
		end=datetime.datetime(2106, 2, 7, 6, 28, 15),
		updated_at=datetime.datetime.utcnow(),
	)

def random_str(length: int) -> str:
	"""Generate a random string of fixed length."""
	letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	return ''.join(random.choice(letters) for i in range(length))

def generate_random_user() -> User:
	"""Generate a random user for testing purposes."""
	num_items = random.randint(0, 125)
	return User(
		id=random.randint(-2*63, 2**63 - 1),
		first_name=random_str(random.randint(3, 10)),
		last_name=random_str(random.randint(3, 10)),
		referral_count=random.randint(0, 2**32 - 1),
		mentions_count=random.randint(0, 2**32 - 1),
		balance=random.randint(-2*63, 2**63 - 1),
		spent=random.uniform(0, 10000),
		items=[generate_random_item() for _ in range(num_items)],
		tasks=[random_str(6) for i in range(random.randint(0, 100))],
		user_referral_code=random_str(8),
		last_update=datetime.datetime.utcnow(),
		reactions=random.randint(0, 2**32 - 1),
	)