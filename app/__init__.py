from flask import Flask
from flask_session import Session
import os
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import Config

db = SQLAlchemy()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config.get("SESSION_FILE_DIR", "./flask_session"), exist_ok=True)

    db.init_app(app)
    ma.init_app(app)

    from app.routes import register_routes
    register_routes(app)

    Session(app)

    return app
