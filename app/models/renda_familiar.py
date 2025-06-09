from app import db

class RendaFamiliar(db.Model):
    __tablename__ = "renda_familiar"

    renda_id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, nullable=False)
    gastos_supermercado = db.Column(db.Numeric(10, 2))
    gastos_energia_eletrica = db.Column(db.Numeric(10, 2))
    gastos_agua = db.Column(db.Numeric(10, 2))
    valor_botijao_gas = db.Column(db.Numeric(10, 2))
    duracao_botijao_gas = db.Column(db.Numeric(10, 2))
    gastos_gas = db.Column(db.Numeric(10, 2))
    gastos_transporte = db.Column(db.Numeric(10, 2))
    gastos_medicamentos = db.Column(db.Numeric(10, 2))
    gastos_celular = db.Column(db.Numeric(10, 2))
    gastos_outros = db.Column(db.Numeric(10, 2))
    renda_provedor_principal = db.Column(db.Numeric(10, 2))
    renda_outros_moradores = db.Column(db.Numeric(10, 2))
    ajuda_terceiros = db.Column(db.Numeric(10, 2))
    possui_cadastro_unico = db.Column(db.Boolean)
    recebe_beneficios_governo = db.Column(db.Boolean)
    descricao_beneficios = db.Column(db.Text)
    valor_beneficios = db.Column(db.Numeric(10, 2))
    renda_total_familiar = db.Column(db.Numeric(10, 2))
    gastos_totais = db.Column(db.Numeric(10, 2))
    saldo_mensal = db.Column(db.Numeric(10, 2))
