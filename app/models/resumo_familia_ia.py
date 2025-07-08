from app import db
from datetime import datetime, timezone

class ResumoFamiliaIA(db.Model):
    __tablename__ = 'resumos_familia_ia'

    resumo_id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, db.ForeignKey("familias.familia_id"), nullable=False)
    resumo_texto = db.Column(db.Text, nullable=False)
    data_hora_geracao = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relacionamento com a tabela de famílias
    familia = db.relationship("Familia", backref="resumos_ia")
