from app.routes.familia import bp as familia_bp
from app.routes.contato import bp as contato_bp
from app.routes.composicao_familiar import bp as composicao_familiar_bp
from app.routes.condicoes_moradia import bp as condicoes_moradia_bp
from app.routes.renda_familiar import bp as renda_familiar_bp
from app.routes.endereco import bp as endereco_bp
from app.routes.saude_familiar import bp as saude_familiar_bp
from app.routes.educacao_entrevistado import bp as educacao_entrevistado_bp
from app.routes.emprego_provedor import bp as emprego_provedor_bp
from app.routes.demanda_tipo import bp as demanda_tipo_bp
from app.routes.demanda_familia import bp as demanda_familia_bp
from app.routes.demanda_etapa import bp as demanda_etapa_bp
from app.routes.atendimento import bp as atendimento_bp
from app.routes.fluxo_atendimento import bp as fluxo_atendimento_bp
from app.auth import bp as auth_bp
from app.routes.usuarios import bp as usuarios_bp
from app.routes.openai_dashboard import openai_dashboard_bp

def register_routes(app):
    app.register_blueprint(familia_bp)
    app.register_blueprint(contato_bp)
    app.register_blueprint(composicao_familiar_bp)
    app.register_blueprint(condicoes_moradia_bp)
    app.register_blueprint(renda_familiar_bp)
    app.register_blueprint(endereco_bp)
    app.register_blueprint(saude_familiar_bp)
    app.register_blueprint(educacao_entrevistado_bp)
    app.register_blueprint(emprego_provedor_bp)
    app.register_blueprint(demanda_tipo_bp)
    app.register_blueprint(demanda_familia_bp)
    app.register_blueprint(demanda_etapa_bp)
    app.register_blueprint(atendimento_bp)
    app.register_blueprint(fluxo_atendimento_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(openai_dashboard_bp)
