from app import db
from datetime import datetime, timezone


class CondicaoMoradia(db.Model):
    __tablename__ = "condicoes_moradia"

    moradia_id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, db.ForeignKey("familias.familia_id"), nullable=False, unique=True)
    tipo_moradia = db.Column(db.String(50))
    valor_aluguel = db.Column(db.Numeric(10, 2))
    tem_agua_encanada = db.Column(db.Boolean)
    tem_rede_esgoto = db.Column(db.Boolean)
    tem_energia_eletrica = db.Column(db.Boolean)
    tem_fogao = db.Column(db.Boolean)
    tem_geladeira = db.Column(db.Boolean)
    quantidade_camas = db.Column(db.Integer)
    quantidade_tvs = db.Column(db.Integer)
    quantidade_ventiladores = db.Column(db.Integer)
    data_hora_log_utc = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
