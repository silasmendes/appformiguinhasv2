from app import db
from datetime import datetime, timezone


class Contato(db.Model):
    __tablename__ = "contatos"

    contato_id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, db.ForeignKey("familias.familia_id"), nullable=False, unique=True)
    telefone_principal = db.Column(db.String(20))
    telefone_principal_whatsapp = db.Column(db.Boolean)
    telefone_principal_nome_contato = db.Column(db.String(100))
    telefone_alternativo = db.Column(db.String(20))
    telefone_alternativo_whatsapp = db.Column(db.Boolean)
    telefone_alternativo_nome_contato = db.Column(db.String(100))
    email_responsavel = db.Column(db.String(100))
    data_hora_log_utc = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
