from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from app.models.usuario import Usuario
from app.models.password_reset_token import PasswordResetToken
from app.utils.email_reset import enviar_email_reset
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
                return redirect(url_for('menu_atendimento'))
        else:
            flash('Credenciais inválidas', 'danger')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# --------------- Esqueci minha senha ---------------

@bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()

        # Mensagem genérica — nunca revela se o email existe
        msg = 'Se existir uma conta com este email, você receberá instruções para redefinir a senha. Verifique também a caixa de Spam.'

        if email:
            usuario = Usuario.query.filter(db.func.lower(Usuario.email) == email).first()

            if usuario:
                # Limita: invalida tokens pendentes anteriores do mesmo usuário
                PasswordResetToken.query.filter_by(user_id=usuario.id, used=False).update({'used': True})

                token_obj = PasswordResetToken(user_id=usuario.id)
                db.session.add(token_obj)
                db.session.commit()

                reset_url = url_for('auth.reset_senha', token=token_obj.token, _external=True)

                try:
                    enviar_email_reset(usuario.email, token_obj.token, reset_url)
                except Exception as e:
                    print(f'[ERROR] Falha ao enviar email de reset para {email}: {e}')

        flash(msg, 'info')
        return redirect(url_for('auth.login'))

    return render_template('esqueci_senha.html')


@bp.route('/reset-senha/<token>', methods=['GET', 'POST'])
def reset_senha(token):
    token_obj = PasswordResetToken.query.filter_by(token=token).first()

    if not token_obj or not token_obj.is_valid:
        flash('O link de redefinição é inválido ou já expirou. Solicite um novo link.', 'danger')
        return redirect(url_for('auth.esqueci_senha'))

    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')

        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return render_template('reset_senha.html', token=token)

        if len(nova_senha) < 6:
            flash('A senha deve ter no mínimo 6 caracteres.', 'danger')
            return render_template('reset_senha.html', token=token)

        usuario = Usuario.query.get(token_obj.user_id)
        if not usuario:
            flash('Usuário não encontrado.', 'danger')
            return redirect(url_for('auth.login'))

        usuario.senha_hash = generate_password_hash(nova_senha)
        token_obj.mark_used()
        db.session.commit()

        flash('Sua senha foi redefinida com sucesso. Faça login com a nova senha.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_senha.html', token=token)
