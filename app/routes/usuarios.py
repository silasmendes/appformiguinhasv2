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

@bp.route('/<int:id>', methods=['PUT', 'PATCH'])
@login_required
@admin_required
def atualizar_usuario(id):
    usuario = db.session.get(Usuario, id)
    if not usuario:
        abort(404)
    expires_at = request.form.get('expires_at')
    if expires_at:
        usuario.expires_at = datetime.fromisoformat(expires_at)
    db.session.commit()
    flash('Usuário atualizado', 'success')
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

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def deletar_usuario(id):
    usuario = db.session.get(Usuario, id)
    if not usuario:
        abort(404)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuário removido', 'success')
    return redirect(url_for('usuarios.listar_usuarios'))
