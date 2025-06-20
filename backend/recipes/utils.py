from uuid import uuid4
from .constans import LENGTH_SHORT_LINK


def generate_short_link():
    return uuid4().hex[:LENGTH_SHORT_LINK]
