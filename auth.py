import jwt
from datetime import datetime, timedelta

KEY = 'f12c835905ca4b12b57168eccbc7117a'


def create_access_token(user):
    payload = {
        'username': user.username,
        'exp': datetime.now() + timedelta(hours=3),
        'iat': datetime.now()
    }

    encoded = jwt.encode(payload, key=KEY, algorithm='HS256')

    return encoded


def decode_access_token(token):
    try:
        decoded = jwt.decode(token, KEY, algorithms='HS256')
        expiry_at = datetime.fromtimestamp(decoded.get('exp'))
        print(f'Expires at : {expiry_at}')
        print(f'User {decoded.get("username")} sent request')
        return decoded
    except Exception as e:
        print(e)
        raise e



