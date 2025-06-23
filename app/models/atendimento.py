from app import db
from datetime import datetime, timezone

class Atendimento(db.Model):
    __tablename__ = "atendimentos"

    atendimento_id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, db.ForeignKey("familias.familia_id"), nullable=False)
    usuario_atendente_id = db.Column(db.Integer)
    percepcao_necessidade = db.Column(db.String(20))
    duracao_necessidade = db.Column(db.String(20))
    motivo_duracao = db.Column(db.String(255))
    cesta_entregue = db.Column(db.Boolean)
    data_hora_atendimento = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

