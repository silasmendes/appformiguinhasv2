from app import db
from datetime import datetime, timezone

class DemandaFamilia(db.Model):
    __tablename__ = "demanda_familia"

    demanda_id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, nullable=False)
    demanda_tipo_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Em análise")
    descricao = db.Column(db.Text)
    data_identificacao = db.Column(db.Date, nullable=False)
    prioridade = db.Column(db.String(20))
    data_hora_log_utc = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
