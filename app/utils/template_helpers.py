from flask import current_app, session
import re
from datetime import datetime
from app.utils.resumo_familia import gerar_resumo_familia

def get_last_atendimento_date():
    """Obtém a data do último atendimento da família atual"""
    try:
        familia_id = session.get('familia_id')
        if not familia_id:
            return None
        
        from app import db
        from app.models.atendimento import Atendimento
        
        # Buscar o último atendimento desta família
        atendimento = db.session.query(Atendimento).filter_by(
            familia_id=familia_id
        ).order_by(Atendimento.data_hora_atendimento.desc()).first()
        
        if atendimento and atendimento.data_hora_atendimento:
            return atendimento.data_hora_atendimento
        return None
    except Exception as e:
        print(f"Erro ao buscar data do último atendimento: {e}")
        return None

def register_template_helpers(app):
    """Registra funções helper para os templates"""
    
    @app.context_processor
    def inject_resumo_familia():
        """Injeta a função de resumo da família nos templates"""
        return dict(
            gerar_resumo_familia=gerar_resumo_familia,
            get_last_atendimento_date=get_last_atendimento_date
        )
    
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
    
    @app.template_filter('format_date')
    def format_date_filter(date_value):
        """Filtro para formatar data no formato dd/mm/yyyy"""
        if not date_value:
            return ""
        
        if isinstance(date_value, str):
            try:
                date_value = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except:
                return ""
        
        return date_value.strftime('%d/%m/%Y')
