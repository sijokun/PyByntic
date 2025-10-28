from user_pb2 import User, Item
import datetime
import random


def random_str(length: int) -> str:
    """Generate a random string of fixed length."""
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choice(letters) for i in range(length))


def datetime_to_timestamp(dt: datetime.datetime) -> int:
    """Convert datetime to Unix timestamp (seconds since epoch)."""
    return int(dt.timestamp())


def generate_random_item() -> Item:
    """Generate a random item for testing purposes."""
    item = Item()
    item.item_id = random.randint(0, 2**16 - 1)
    item.type = random.choice(["gold", "diamond", "silver", "bronze", "elite"])
    item.rate = random.randint(1, 2**32 - 1)
    item.capacity = random.randint(-2**31, 2**31 - 1)
    item.start = datetime_to_timestamp(datetime.datetime.utcnow())
    item.end = datetime_to_timestamp(datetime.datetime(2106, 2, 7, 6, 28, 15))
    item.updated_at = datetime_to_timestamp(datetime.datetime.utcnow())
    return item


def generate_random_user() -> User:
    """Generate a random user for testing purposes."""
    num_items = random.randint(0, 150)
    user = User()
    user.id = random.randint(-2**63, 2**63 - 1)
    user.first_name = random_str(random.randint(3, 10))
    user.last_name = random_str(random.randint(3, 10))
    user.referral_count = random.randint(0, 2**32 - 1)
    user.mentions_count = random.randint(0, 2**32 - 1)
    user.balance = random.randint(-2**63, 2**63 - 1)
    user.spent = random.uniform(0, 10000)
    user.items.extend([generate_random_item() for _ in range(num_items)])
    user.tasks.extend([random_str(6) for i in range(random.randint(0, 100))])
    user.user_referral_code = random_str(8)
    user.last_update = datetime_to_timestamp(datetime.datetime.utcnow())
    user.reactions = random.randint(0, 2**32 - 1)
    return user
