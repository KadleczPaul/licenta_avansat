import os


class Config:

    APP_NAME = "Logistics Pro 2026"
    SECRET_KEY = os.environ.get('SECRET_KEY') or "licenta_secret_key_2026"


    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "cinema",
        "database": "transport_management",
        "raise_on_warnings": True
    }

