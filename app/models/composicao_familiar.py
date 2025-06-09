from app import db
from datetime import datetime

class ComposicaoFamiliar(db.Model):
    __tablename__ = "composicao_familiar"

    composicao_id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, nullable=False)
    total_residentes = db.Column(db.Integer)
    quantidade_bebes = db.Column(db.Integer)
    quantidade_criancas = db.Column(db.Integer)
    quantidade_adolescentes = db.Column(db.Integer)
    quantidade_adultos = db.Column(db.Integer)
    quantidade_idosos = db.Column(db.Integer)
    tem_menores_na_escola = db.Column(db.Boolean)
    motivo_ausencia_escola = db.Column(db.Text)
    data_hora_log_utc = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
