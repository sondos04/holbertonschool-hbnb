import os
from datetime import timedelta

class Config:
    SECRET_KEY = "super-secret-key"
    JWT_SECRET_KEY = "jwt-super-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)



class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///development.db"


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
