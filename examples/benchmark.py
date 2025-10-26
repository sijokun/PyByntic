"""
Benchmarking PyByntic serialization size against JSON serialization size.

This example shows a realistic data model with nested structures and lists
which could be cached in Redis or sent over the network.

This example shoes 7x size reduction when using PyByntic compared to JSON.

Most of the size reduction comes from PyByntic's efficient binary encoding of integers and dates
"""

import datetime
import random
from typing import Annotated

from pybyntic import AnnotatedBaseModel
from pybyntic.types import Bool, Date, String, UInt8, UInt32


class Category(AnnotatedBaseModel):
    category_id: Annotated[int, UInt32]
    category_name: Annotated[str, String]
    category_description: Annotated[str, String]
    age_rating: Annotated[int, UInt8] = 0
    nsfw: Annotated[bool, Bool] = False


class Ratings(AnnotatedBaseModel):
    rating_id: Annotated[int, UInt32]
    user_id: Annotated[int, UInt32]
    rating: Annotated[int, UInt8]
    created_at: Annotated[datetime.date, Date]


class Post(AnnotatedBaseModel):
    id: Annotated[int, UInt32]
    title: Annotated[str, String]
    created_at: Annotated[datetime.date, Date]
    tags: Annotated[list[str], list[String]]
    categories: Annotated[list[Category], list[Category]]
    author_ids: Annotated[list[int], list[UInt32]] = []
    ratings: list[Ratings] = []


def random_uint32() -> int:
    return random.randint(0, 2**32 - 1)


words = [
    "Dream",
    "Silent",
    "Golden",
    "Ocean",
    "Shadow",
    "Future",
    "Bright",
    "Memory",
    "Lost",
    "Sky",
]
tags = [
    "adventure",
    "mystery",
    "romance",
    "fantasy",
    "horror",
    "sci-fi",
    "thriller",
    "drama",
    "comedy",
    "action",
]


def generate_title():
    return " ".join(random.sample(words, random.randint(2, 5)))


def generate_category() -> Category:
    return Category(
        category_id=random_uint32(),
        category_name=random.choice(
            ["Technology", "Lifestyle", "Health", "Travel", "Food"]
        ),
        category_description="A category about "
        + random.choice(["technology", "lifestyle", "health", "travel", "food"])
        + ".",
        age_rating=random.randint(0, 18),
        nsfw=random.choice([True, False]),
    )


def generate_rating() -> Ratings:
    return Ratings(
        rating_id=random_uint32(),
        user_id=random_uint32(),
        rating=random.randint(1, 5),
        created_at=datetime.date.today(),
    )


def generate_sample_post() -> Post:
    return Post(
        id=random_uint32(),
        title=generate_title(),
        created_at=datetime.date.today(),
        tags=random.sample(tags, random.randint(0, 10)),
        categories=[generate_category() for _ in range(random.randint(1, 5))],
        author_ids=[random_uint32() for _ in range(random.randint(1, 3))],
        ratings=[generate_rating() for _ in range(random.randint(0, 1000))],
    )


def main():
    size_pybantic = 0
    size_json = 0

    num_samples = 1000

    for _ in range(num_samples):
        post = generate_sample_post()

        serialized = post.serialize()
        size_pybantic += len(serialized)

        serialized_json = post.model_dump_json().encode("utf-8")
        size_json += len(serialized_json)

    print(f"Average size using PyByntic: {size_pybantic / num_samples:.2f} bytes")
    print(f"Average size using JSON: {size_json / num_samples:.2f} bytes")
    print(f"PyByntic is {size_json / size_pybantic:.2f} times smaller than JSON")


if __name__ == "__main__":
    main()
