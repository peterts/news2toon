import hashlib


def convert_to_alphanumeric(input_string: str) -> str:
    hash_object = hashlib.sha256(input_string.encode())
    return hash_object.hexdigest()
