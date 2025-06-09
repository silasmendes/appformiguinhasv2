from app.routes.familia import bp as familia_bp
from app.routes.contato import bp as contato_bp

def register_routes(app):
    app.register_blueprint(familia_bp)
    app.register_blueprint(contato_bp)
