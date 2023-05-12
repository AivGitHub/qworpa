import datetime
from typing import Optional

from django.conf import settings
import jwt

DEFAULT_JWT_EXPIRATION_TIME: int = 60 * 60
DEFAULT_JWT_ALGORITHM = 'HS256'


class FatalSignatureError(Exception):
    """Fatal JWT signature error."""


class SignatureExpiredError(Exception):
    """JWT expired."""


def generate_jwt_signature(
        payload: dict,
        expiration_time: Optional[int] = DEFAULT_JWT_EXPIRATION_TIME,
        algorithm: Optional[str] = DEFAULT_JWT_ALGORITHM
) -> str:
    """Generates encoded JWT.

    JWT does not imply encryption, but payload signed with secret key,
    so later signature can be verified, until ``expiration_time`` is not expired.

    Args:
        payload (dict): Payload to be encoded.
        expiration_time (int, optional): After expiration time JWT signature can't be verified.
        algorithm (str, optional): With this algorithm payload will be signed.

    Returns:
        str: JWT signature.
    """
    cleaned_payload: dict = dict()
    if expiration_time is None:
        expiration_time = DEFAULT_JWT_EXPIRATION_TIME

    for key, value in payload.items():
        cleaned_payload.update({key: value})

    cleaned_payload.update(
        {
            'exp': datetime.datetime.now() + datetime.timedelta(seconds=expiration_time),
        }
    )

    return jwt.encode(cleaned_payload, settings.JWT_AUTH_KEY, algorithm=algorithm)


def decode_jwt_signature(token, algorithms=None):
    if algorithms is None:
        algorithms = [DEFAULT_JWT_ALGORITHM]

    try:
        return jwt.decode(token, settings.JWT_AUTH_KEY, algorithms=algorithms)
    except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError):
        raise FatalSignatureError()
    except jwt.exceptions.ExpiredSignatureError:
        raise SignatureExpiredError()

