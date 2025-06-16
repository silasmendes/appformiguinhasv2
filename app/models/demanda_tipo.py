from app import db
from datetime import datetime, timezone

class DemandaTipo(db.Model):
    __tablename__ = "demanda_tipo"

    demanda_tipo_id = db.Column(db.Integer, primary_key=True)
    demanda_tipo_nome = db.Column(db.String(100), nullable=False)
    data_hora_log_utc = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
