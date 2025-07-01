from flask import Flask
from flask_session import Session
import os
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask import jsonify, redirect, url_for, request
from config import Config

db = SQLAlchemy()
ma = Marshmallow()
login_manager = LoginManager()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config.get("SESSION_FILE_DIR", "./flask_session"), exist_ok=True)

    db.init_app(app)
    ma.init_app(app)

    jwt.init_app(app)

    @jwt.unauthorized_loader
    def unauthorized(reason):
        if request.accept_mimetypes.accept_html:
            return redirect(url_for('auth.login'))
        return jsonify({"msg": reason}), 401

    @jwt.invalid_token_loader
    def invalid(reason):
        if request.accept_mimetypes.accept_html:
            return redirect(url_for('auth.login'))
        return jsonify({"msg": reason}), 401

    @jwt.expired_token_loader
    def expired(jwt_header, jwt_payload):
        if request.accept_mimetypes.accept_html:
            return redirect(url_for('auth.login'))
        return jsonify({"msg": "Token expirado"}), 401

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'danger'

    from app.models.usuario import Usuario

    @login_manager.user_loader
    def load_user(user_id: str):
        return Usuario.query.get(int(user_id))

    from app.routes import register_routes
    register_routes(app)

    Session(app)

    return app
