from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
from app.models.usuario import Usuario
from app import db
from app.schemas.user import UserSchema

bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo != 'admin':
            abort(403)
        return func(*args, **kwargs)
    return wrapper

@bp.route('', methods=['GET'])
@login_required
@admin_required
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@bp.route('', methods=['POST'])
@login_required
@admin_required
def criar_usuario():
    data = request.form.to_dict()
    errors = user_schema.validate(data)
    if errors:
        for field, msg in errors.items():
            flash(f'{field}: {msg}', 'danger')
        return redirect(url_for('usuarios.listar_usuarios'))
    senha = data.pop('senha')
    usuario = Usuario(**{k:v for k,v in data.items() if k in user_schema.fields})
    usuario.senha_hash = generate_password_hash(senha)
    db.session.add(usuario)
    db.session.commit()
    flash('Usuário criado com sucesso', 'success')
    return redirect(url_for('usuarios.listar_usuarios'))

@bp.route('/<int:id>', methods=['PUT', 'PATCH', 'POST'])
@login_required
@admin_required
def atualizar_usuario(id):
    usuario = db.session.get(Usuario, id)
    if not usuario:
        abort(404)

    nome_completo = request.form.get('nome_completo', '').strip()
    email = request.form.get('email', '').strip()
    tipo = request.form.get('tipo', '').strip()
    expires_at_str = request.form.get('expires_at', '').strip()

    if nome_completo:
        usuario.nome_completo = nome_completo

    usuario.email = email if email else None

    if tipo in ('admin', 'temporario'):
        usuario.tipo = tipo

    if expires_at_str:
        try:
            usuario.expires_at = datetime.strptime(expires_at_str, '%d/%m/%Y %H:%M')
        except ValueError:
            try:
                usuario.expires_at = datetime.fromisoformat(expires_at_str)
            except ValueError:
                flash('Formato de data de expiração inválido', 'danger')
                return redirect(url_for('usuarios.listar_usuarios'))
    else:
        if tipo == 'admin':
            usuario.expires_at = None

    if tipo == 'temporario' and not usuario.expires_at:
        flash('Data de expiração é obrigatória para usuários temporários', 'danger')
        return redirect(url_for('usuarios.listar_usuarios'))

    db.session.commit()
    flash('Usuário atualizado com sucesso', 'success')
    return redirect(url_for('usuarios.listar_usuarios'))

@bp.route('/<int:id>/reset-senha', methods=['POST'])
@login_required
@admin_required
def reset_senha(id):
    usuario = db.session.get(Usuario, id)
    if not usuario:
        abort(404)
    nova = request.form.get('nova_senha')
    if not nova:
        nova = 'mudarsenha'
    usuario.senha_hash = generate_password_hash(nova)
    db.session.commit()
    flash('Senha redefinida', 'success')
    return redirect(url_for('usuarios.listar_usuarios'))

@bp.route('/<int:id>/delete', methods=['DELETE', 'POST'])
@login_required
@admin_required
def deletar_usuario(id):
    # Rota mantida mas não exposta na interface por questões de rastreabilidade
    if request.method == 'POST' and request.form.get('_method') != 'DELETE':
        abort(405)
    
    usuario = db.session.get(Usuario, id)
    if not usuario:
        abort(404)
    
    nome_usuario = usuario.nome_completo  # Guardar nome para mensagem
    db.session.delete(usuario)
    db.session.commit()
    flash(f'Usuário "{nome_usuario}" removido com sucesso', 'success')
    return redirect(url_for('usuarios.listar_usuarios'))
