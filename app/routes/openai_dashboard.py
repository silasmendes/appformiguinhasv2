from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.openai_usage import OpenAIUsage
from app.utils.openai_usage_tracker import OpenAIUsageTracker
from datetime import datetime, timedelta
import json

openai_dashboard_bp = Blueprint('openai_dashboard', __name__)

@openai_dashboard_bp.route('/admin/openai-usage')
@login_required
def openai_usage_dashboard():
    """Dashboard de uso do OpenAI - apenas para admins"""
    if not current_user.is_authenticated or current_user.tipo != 'admin':
        return "Acesso negado", 403
    
    # Resumo geral
    summary = OpenAIUsage.get_usage_summary()
    
    # Uso diário
    daily_usage = OpenAIUsageTracker.get_daily_usage()
    
    # Uso por tipo
    usage_by_type = OpenAIUsageTracker.get_usage_by_type()
    
    return render_template('admin/openai_usage_dashboard.html',
                         summary=summary,
                         daily_usage=daily_usage,
                         usage_by_type=usage_by_type,
                         config=current_app.config)

@openai_dashboard_bp.route('/admin/openai-usage/api/daily')
@login_required
def api_daily_usage():
    """API para dados de uso diário"""
    if not current_user.is_authenticated or current_user.tipo != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    daily_usage = OpenAIUsageTracker.get_daily_usage()
    
    data = {
        'dates': [str(usage.date) for usage in daily_usage],
        'tokens': [int(usage.total_tokens) for usage in daily_usage],
        'costs': [float(usage.total_cost) for usage in daily_usage],
        'requests': [int(usage.total_requests) for usage in daily_usage]
    }
    
    return jsonify(data)
