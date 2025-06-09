from app import db


class Contato(db.Model):
    __tablename__ = "contatos"

    contato_id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, nullable=False)
    telefone_principal = db.Column(db.String(20))
    telefone_principal_whatsapp = db.Column(db.Boolean)
    telefone_principal_nome_contato = db.Column(db.String(100))
    telefone_alternativo = db.Column(db.String(20))
    telefone_alternativo_whatsapp = db.Column(db.Boolean)
    telefone_alternativo_nome_contato = db.Column(db.String(100))
    email_responsavel = db.Column(db.String(100))
