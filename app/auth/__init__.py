from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from datetime import datetime
from app.models.usuario import Usuario
from app import db

bp = Blueprint('auth', __name__, url_prefix='')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        login_ = data.get('login') if data else None
        senha = data.get('senha') if data else None
        usuario = Usuario.query.filter_by(login=login_).first()
        if usuario and check_password_hash(usuario.senha_hash, senha):
            if usuario.tipo == 'temporario' and usuario.expires_at and usuario.expires_at < datetime.utcnow():
                return jsonify({'mensagem': 'Conta expirada'}), 401
            usuario.last_login_at = datetime.utcnow()
            db.session.commit()
            token = create_access_token(identity=usuario.id)
            return jsonify({'access_token': token})
        return jsonify({'mensagem': 'Credenciais inválidas'}), 401
    return render_template('login.html')

@bp.route('/logout')
def logout():
    return redirect(url_for('auth.login'))
