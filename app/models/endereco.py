from app import db
from datetime import datetime

class Endereco(db.Model):
    __tablename__ = "enderecos"

    endereco_id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, nullable=False)
    cep = db.Column(db.String(10))
    preenchimento_manual = db.Column(db.Boolean)
    logradouro = db.Column(db.String(150))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(50))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(100))
    ponto_referencia = db.Column(db.String(200))
    data_hora_log_utc = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
