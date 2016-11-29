import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Development environment."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "bucketlist.sqlite")


class TestingConfig(object):
    """Testing environment."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "test.sqlite")
