from app import db
from app.models.openai_usage import OpenAIUsage
from flask import session
from flask_login import current_user
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class OpenAIUsageTracker:
    # Preços aproximados do Azure OpenAI (em USD por 1K tokens)
    TOKEN_PRICES = {
        'gpt-4o': {
            'input': 0.005,   # $0.005 por 1K tokens de input
            'output': 0.015   # $0.015 por 1K tokens de output
        },
        'gpt-4': {
            'input': 0.03,
            'output': 0.06
        },
        'gpt-3.5-turbo': {
            'input': 0.0015,
            'output': 0.002
        }
    }
    
    @staticmethod
    def calculate_cost(model, prompt_tokens, completion_tokens):
        """Calcula o custo estimado baseado no modelo e tokens"""
        if model not in OpenAIUsageTracker.TOKEN_PRICES:
            return 0.0
        
        prices = OpenAIUsageTracker.TOKEN_PRICES[model]
        input_cost = (prompt_tokens / 1000) * prices['input']
        output_cost = (completion_tokens / 1000) * prices['output']
        
        return round(input_cost + output_cost, 6)
    
    @staticmethod
    def track_usage(endpoint, model, prompt_tokens, completion_tokens, 
                   request_type, success=True, error_message=None):
        """Registra o uso do OpenAI na base de dados"""
        try:
            total_tokens = prompt_tokens + completion_tokens
            cost_estimate = OpenAIUsageTracker.calculate_cost(model, prompt_tokens, completion_tokens)
            
            # Obter informações do usuário atual (com verificação segura)
            user_id = None
            if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                user_id = current_user.id
            
            familia_id = None
            if session and hasattr(session, 'get'):
                familia_id = session.get('familia_id')
            
            usage = OpenAIUsage(
                endpoint=endpoint,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_estimate=cost_estimate,
                user_id=user_id,
                familia_id=familia_id,
                request_type=request_type,
                success=success,
                error_message=error_message
            )
            
            db.session.add(usage)
            db.session.commit()
            
            logger.info(f"OpenAI usage tracked: {total_tokens} tokens, ${cost_estimate:.6f} estimated cost")
            
        except Exception as e:
            logger.error(f"Erro ao registrar uso do OpenAI: {e}")
            try:
                db.session.rollback()
            except:
                pass
    
    @staticmethod
    def get_daily_usage():
        """Retorna uso diário dos últimos 30 dias"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        return db.session.query(
            db.func.date(OpenAIUsage.timestamp).label('date'),
            db.func.sum(OpenAIUsage.total_tokens).label('total_tokens'),
            db.func.sum(OpenAIUsage.cost_estimate).label('total_cost'),
            db.func.count(OpenAIUsage.id).label('total_requests')
        ).filter(
            OpenAIUsage.timestamp >= thirty_days_ago
        ).group_by(
            db.func.date(OpenAIUsage.timestamp)
        ).order_by(
            db.func.date(OpenAIUsage.timestamp).desc()
        ).all()
    
    @staticmethod
    def get_usage_by_type():
        """Retorna uso por tipo de request"""
        return db.session.query(
            OpenAIUsage.request_type,
            db.func.sum(OpenAIUsage.total_tokens).label('total_tokens'),
            db.func.sum(OpenAIUsage.cost_estimate).label('total_cost'),
            db.func.count(OpenAIUsage.id).label('total_requests')
        ).group_by(
            OpenAIUsage.request_type
        ).order_by(
            db.func.sum(OpenAIUsage.total_tokens).desc()
        ).all()
