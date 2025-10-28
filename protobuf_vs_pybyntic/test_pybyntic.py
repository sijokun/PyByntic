from models import generate_random_user


def test(sample_size: int = 1000):
    size = 0

    for _ in range(sample_size):
        user = generate_random_user()
        serialized = user.serialize()
        size += len(serialized)

    print(f"Average serialized size over {sample_size} samples: {size / sample_size:.2f} bytes")

if __name__ == "__main__":
    test()