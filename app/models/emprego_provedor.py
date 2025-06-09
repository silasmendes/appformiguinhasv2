from app import db
from datetime import datetime

class EmpregoProvedor(db.Model):
    __tablename__ = "emprego_provedor"

    emprego_id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, nullable=False)
    relacao_provedor_familia = db.Column(db.String(100))
    descricao_provedor_externo = db.Column(db.Text)
    situacao_emprego = db.Column(db.String(50))
    descricao_situacao_emprego_outro = db.Column(db.Text)
    profissao_provedor = db.Column(db.String(100))
    experiencia_profissional = db.Column(db.Text)
    formacao_profissional = db.Column(db.Text)
    habilidades_relevantes = db.Column(db.Text)
    data_hora_log_utc = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
