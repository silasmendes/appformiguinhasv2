from flask import current_app
import re
from app.utils.resumo_familia import gerar_resumo_familia

def register_template_helpers(app):
    """Registra funções helper para os templates"""
    
    @app.context_processor
    def inject_resumo_familia():
        """Injeta a função de resumo da família nos templates"""
        return dict(gerar_resumo_familia=gerar_resumo_familia)
    
    @app.template_filter('simple_markdown')
    def simple_markdown_filter(text):
        """Filtro simples para converter Markdown básico para HTML"""
        if not text:
            return ""
        
        # Converter **texto** para <strong>texto</strong>
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Converter *texto* para <em>texto</em>
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        return text
