# import os
# basedir = os.path.abspath(os.path.dirname(__file__))


# class BaseConfig(object):
#     """Base configuration."""
#     SECRET_KEY = '123'
#     SECURITY_PASSWORD_SALT = 'samwoo'
#     DEBUG = False
#     BCRYPT_LOG_ROUNDS = 13
#     WTF_CSRF_ENABLED = True
#     DEBUG_TB_ENABLED = False
#     DEBUG_TB_INTERCEPT_REDIRECTS = False


# class DevelopmentConfig(BaseConfig):
#     """Development configuration."""
#     DEBUG = True


# class TestingConfig(BaseConfig):
#     """Testing configuration."""
#     TESTING = True
#     DEBUG = True


# class ProductionConfig(BaseConfig):
#     """Production configuration."""
#     SECRET_KEY = '123'
#     DEBUG = False