import os
from datetime import datetime
from werkzeug.security import generate_password_hash
from app import db
from app.models.usuario import Usuario


def seed_admin_user():
    senha_admin = os.getenv('SENHA_ADMIN')
    if not senha_admin:
        return
    if not Usuario.query.filter_by(login='admin').first():
        senha_hash = generate_password_hash(senha_admin)
        admin = Usuario(login='admin', nome_completo='Administrador', tipo='admin', senha_hash=senha_hash, created_at=datetime.utcnow())
        db.session.add(admin)
        db.session.commit()
