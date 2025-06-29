from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from app.models.usuario import Usuario
from app import db

bp = Blueprint('auth', __name__, url_prefix='')


@bp.before_app_request
def check_expired_user():
    if current_user.is_authenticated and current_user.tipo == 'temporario' and current_user.expires_at and current_user.expires_at < datetime.utcnow():
        logout_user()
        flash('Sessão expirada', 'danger')
        return redirect(url_for('auth.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_ = request.form.get('login')
        senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(login=login_).first()
        if usuario and check_password_hash(usuario.senha_hash, senha):
            if usuario.tipo == 'temporario' and usuario.expires_at and usuario.expires_at < datetime.utcnow():
                flash(f'Conta expirada desde {usuario.expires_at.date().strftime("%d/%m/%Y")}', 'danger')
            else:
                usuario.last_login_at = datetime.utcnow()
                db.session.commit()
                login_user(usuario)
                return redirect(url_for('home'))
        else:
            flash('Credenciais inválidas', 'danger')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
