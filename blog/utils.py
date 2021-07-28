import random
import string

from uuid import UUID


def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str


def validate_uuid4(uuid_str):
    try:
        UUID(uuid_str, version=4)
        return True
    except ValueError:
        return False
