import os


class Config():

    # SQLAclhemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Flask-Security and Flask-Social
    SECURITY_REGISTERABLE = True
    SECURITY_PASSWORD_SALT = 'bcrypt'
    SECRET_KEY = 'randomsecrety1234'
    SOCIAL_TWITTER = {
        'consumer_key': 'twitter consumer key',
        'consumer_secret': 'twitter consumer secret'
    }

    # S3
    S3_SECRET = os.environ.get('S3_SECRET')
    S3_KEY = os.environ.get('S3_KEY')
    S3_UPLOAD_DIRECTORY = '/'
    S3_BUCKET = 'healthhack-mddb'

    # Mail
    MAIL_DEFAULT_SENDER = "me@matthewbrown.io"
    MAIL_SERVER = 'smtp.postmarkapp.com'
    MAIL_PORT = 25
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
