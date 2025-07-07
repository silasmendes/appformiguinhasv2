from app import db
from datetime import datetime

class OpenAIUsage(db.Model):
    __tablename__ = 'openai_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    endpoint = db.Column(db.String(100), nullable=False)  # ex: 'chat/completions'
    model = db.Column(db.String(50), nullable=False)  # ex: 'gpt-4o'
    prompt_tokens = db.Column(db.Integer, nullable=False)
    completion_tokens = db.Column(db.Integer, nullable=False)
    total_tokens = db.Column(db.Integer, nullable=False)
    cost_estimate = db.Column(db.Numeric(10, 6), nullable=True)  # estimativa de custo em USD
    user_id = db.Column(db.Integer, nullable=True)
    familia_id = db.Column(db.Integer, nullable=True)
    request_type = db.Column(db.String(50), nullable=False)  # ex: 'resumo_familia', 'chat', etc
    success = db.Column(db.Boolean, default=True, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<OpenAIUsage {self.id}: {self.total_tokens} tokens>'
    
    @classmethod
    def get_usage_summary(cls, start_date=None, end_date=None):
        """Retorna resumo de uso de tokens"""
        query = cls.query
        
        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        if end_date:
            query = query.filter(cls.timestamp <= end_date)
            
        return {
            'total_requests': query.count(),
            'total_tokens': query.with_entities(db.func.sum(cls.total_tokens)).scalar() or 0,
            'total_prompt_tokens': query.with_entities(db.func.sum(cls.prompt_tokens)).scalar() or 0,
            'total_completion_tokens': query.with_entities(db.func.sum(cls.completion_tokens)).scalar() or 0,
            'total_cost_estimate': query.with_entities(db.func.sum(cls.cost_estimate)).scalar() or 0,
            'successful_requests': query.filter(cls.success == True).count(),
            'failed_requests': query.filter(cls.success == False).count()
        }
