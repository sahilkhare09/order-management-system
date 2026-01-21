import secrets


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)
