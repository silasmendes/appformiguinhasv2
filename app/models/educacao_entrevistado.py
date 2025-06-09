from app import db
from datetime import datetime

class EducacaoEntrevistado(db.Model):
    __tablename__ = "educacao_entrevistado"

    educacao_id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, nullable=False)
    nivel_escolaridade = db.Column(db.String(100))
    estuda_atualmente = db.Column(db.String(3))
    curso_ou_serie_atual = db.Column(db.Text)
    data_hora_log_utc = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
