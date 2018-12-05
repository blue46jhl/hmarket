from itsdangerous import URLSafeTimedSerializer
from flask import current_app as app

Secret_key='123'

def encrypt(email):
    serializer=URLSafeTimedSerializer(Secret_key)
    key= serializer.dumps(email, salt="email-key")
    return key


def confirm(token):
    serializer=URLSafeTimedSerializer(Secret_key)
    try:
        email= serializer.loads(token,salt="email-key")
    except:
        return False
    return email

































