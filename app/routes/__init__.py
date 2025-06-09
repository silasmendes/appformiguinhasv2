from app.routes.familia import bp as familia_bp
from app.routes.contato import bp as contato_bp
from app.routes.condicoes_moradia import bp as condicoes_moradia_bp

def register_routes(app):
    app.register_blueprint(familia_bp)
    app.register_blueprint(contato_bp)
    app.register_blueprint(condicoes_moradia_bp)
