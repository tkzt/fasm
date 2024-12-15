import random
import string
import time


def current_time_seconds():
    return int(time.time())


def generate_random_code(length=6):
    characters = string.digits
    verification_code = "".join(random.choice(characters) for _ in range(length))
    return verification_code
