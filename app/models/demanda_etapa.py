from app import db
from datetime import datetime, timezone

class DemandaEtapa(db.Model):
    __tablename__ = "demanda_etapa"

    etapa_id = db.Column(db.Integer, primary_key=True)
    demanda_id = db.Column(db.Integer, nullable=False)
    data_atualizacao = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status_atual = db.Column(db.String(20), nullable=False)
    observacao = db.Column(db.Text)
    usuario_atualizacao = db.Column(db.String(100))
