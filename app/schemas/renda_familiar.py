from app import ma
from app.models.renda_familiar import RendaFamiliar

class RendaFamiliarSchema(ma.SQLAlchemySchema):
    class Meta:
        model = RendaFamiliar
        load_instance = True

    renda_id = ma.auto_field(dump_only=True)
    familia_id = ma.auto_field(required=True)
    gastos_supermercado = ma.auto_field()
    gastos_energia_eletrica = ma.auto_field()
    gastos_agua = ma.auto_field()
    valor_botijao_gas = ma.auto_field()
    duracao_botijao_gas = ma.auto_field()
    gastos_gas = ma.auto_field()
    gastos_transporte = ma.auto_field()
    gastos_medicamentos = ma.auto_field()
    gastos_celular = ma.auto_field()
    gastos_outros = ma.auto_field()
    renda_provedor_principal = ma.auto_field()
    renda_outros_moradores = ma.auto_field()
    ajuda_terceiros = ma.auto_field()
    possui_cadastro_unico = ma.auto_field()
    recebe_beneficios_governo = ma.auto_field()
    descricao_beneficios = ma.auto_field()
    valor_beneficios = ma.auto_field()
    renda_total_familiar = ma.auto_field()
    gastos_totais = ma.auto_field()
    saldo_mensal = ma.auto_field()
    data_hora_log_utc = ma.auto_field(dump_only=True)
