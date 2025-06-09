from app import db
from datetime import datetime, timezone

class SaudeFamiliar(db.Model):
    __tablename__ = "saude_familiar"

    saude_id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, nullable=False)
    tem_doenca_cronica = db.Column(db.Boolean)
    descricao_doenca_cronica = db.Column(db.Text)
    usa_medicacao_continua = db.Column(db.Boolean)
    descricao_medicacao = db.Column(db.Text)
    tem_deficiencia = db.Column(db.Boolean)
    descricao_deficiencia = db.Column(db.Text)
    recebe_bpc = db.Column(db.Boolean)
    data_hora_log_utc = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
