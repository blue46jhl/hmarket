from itsdangerous import URLSafeTimedSerializer
from flask import current_app as app

SECRET_KEY = 'secretkey'
SECURITY_PASSWORD_SALT = 'secretsalt'

def encrypt(email):
    serializer=URLSafeTimedSerializer('secretkey')
    key= serializer.dumps(email)
    return key

def confirm(token):
    serializer=URLSafeTimedSerializer('secretkey')
    try:
        email= serializer.loads(token)
    except:
        return False
    return email
