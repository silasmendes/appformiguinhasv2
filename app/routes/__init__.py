from app.routes.familia import bp as familia_bp
from app.routes.contato import bp as contato_bp
from app.routes.composicao_familiar import bp as composicao_familiar_bp

def register_routes(app):
    app.register_blueprint(familia_bp)
    app.register_blueprint(contato_bp)
    app.register_blueprint(composicao_familiar_bp)
