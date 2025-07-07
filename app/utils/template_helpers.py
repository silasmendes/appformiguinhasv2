from flask import current_app
from app.utils.resumo_familia import gerar_resumo_familia

def register_template_helpers(app):
    """Registra funções helper para os templates"""
    
    @app.context_processor
    def inject_resumo_familia():
        """Injeta a função de resumo da família nos templates"""
        return dict(gerar_resumo_familia=gerar_resumo_familia)
