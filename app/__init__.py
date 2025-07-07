from flask import Flask
from flask_session import Session
import os
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
ma = Marshmallow()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config.get("SESSION_FILE_DIR", "./flask_session"), exist_ok=True)

    db.init_app(app)
    ma.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'danger'

    from app.models.usuario import Usuario

    @login_manager.user_loader
    def load_user(user_id: str):
        return Usuario.query.get(int(user_id))

    from app.routes import register_routes
    register_routes(app)

    # Registra template helpers
    from app.utils.template_helpers import register_template_helpers
    register_template_helpers(app)

    # Registrar handlers de erro personalizados
    @app.errorhandler(404)
    def page_not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        from flask import render_template
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def access_forbidden(error):
        from flask import render_template
        return render_template('errors/403.html'), 403

    Session(app)

    return app
