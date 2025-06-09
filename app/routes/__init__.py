from app.routes.familia import bp as familia_bp
from app.routes.contato import bp as contato_bp
from app.routes.composicao_familiar import bp as composicao_familiar_bp
from app.routes.condicoes_moradia import bp as condicoes_moradia_bp
from app.routes.renda_familiar import bp as renda_familiar_bp
from app.routes.endereco import bp as endereco_bp
from app.routes.saude_familiar import bp as saude_familiar_bp
from app.routes.educacao_entrevistado import bp as educacao_entrevistado_bp

def register_routes(app):
    app.register_blueprint(familia_bp)
    app.register_blueprint(contato_bp)
    app.register_blueprint(composicao_familiar_bp)
    app.register_blueprint(condicoes_moradia_bp)
    app.register_blueprint(renda_familiar_bp)
    app.register_blueprint(endereco_bp)
    app.register_blueprint(saude_familiar_bp)
    app.register_blueprint(educacao_entrevistado_bp)
