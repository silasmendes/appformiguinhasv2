from datetime import datetime
from flask_login import UserMixin
from app import db

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    nome_completo = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128))
    tipo = db.Column(db.String(16), nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime)
    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

