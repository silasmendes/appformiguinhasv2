from app import db

class Familia(db.Model):
    __tablename__ = 'familias'

    familia_id = db.Column(db.Integer, primary_key=True)
    nome_responsavel = db.Column(db.String(100))
    data_nascimento = db.Column(db.Date)
    genero = db.Column(db.String(20))
    genero_autodeclarado = db.Column(db.String(20))
    estado_civil = db.Column(db.String(50))
    rg = db.Column(db.String(20))
    cpf = db.Column(db.String(14))
    autoriza_uso_imagem = db.Column(db.Boolean)
