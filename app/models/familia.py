from app import db
from datetime import datetime, timezone

class Familia(db.Model):
    __tablename__ = 'familias'

    familia_id = db.Column(db.Integer, primary_key=True)
    nome_responsavel = db.Column(db.String(100))
    data_nascimento = db.Column(db.Date)
    genero = db.Column(db.String(20))
    genero_autodeclarado = db.Column(db.String(20))
    estado_civil = db.Column(db.String(50))
    rg = db.Column(db.String(20))
    cpf = db.Column(db.String(14))
    autoriza_uso_imagem = db.Column(db.Boolean)
    status_cadastro = db.Column(
        db.String(20), nullable=False, default="rascunho"
    )
    data_hora_log_utc = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
