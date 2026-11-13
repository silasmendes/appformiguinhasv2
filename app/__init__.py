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

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    if app.config['ENV'] == 'production':
        secret = app.config.get('SECRET_KEY') or ''
        if len(secret) < 32 or secret.startswith(('SUBSTITUA', 'chave-ficticia', 'local-development')):
            raise ValueError('Em produção, defina SECRET_KEY com um segredo aleatório de pelo menos 32 caracteres.')
        app.config.update(DEBUG=False, SESSION_COOKIE_SECURE=True, REMEMBER_COOKIE_SECURE=True)
    os.makedirs(app.instance_path, exist_ok=True)

    os.makedirs(app.config.get("SESSION_FILE_DIR", "./flask_session"), exist_ok=True)

    db.init_app(app)
    from sqlalchemy import create_engine
    from app.sqlite import configure_sqlite
    with app.app_context():
        for engine in db.engines.values():
            configure_sqlite(engine, app.config['SQLITE_BUSY_TIMEOUT_MS'])
    pre_engine = create_engine(app.config['SQLALCHEMY_PRE_CADASTRO_URI'])
    configure_sqlite(pre_engine, app.config['SQLITE_BUSY_TIMEOUT_MS'])
    app.extensions['pre_cadastro_engine'] = pre_engine
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
