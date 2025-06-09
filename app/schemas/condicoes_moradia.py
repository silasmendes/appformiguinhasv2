from app import ma
from app.models.condicoes_moradia import CondicaoMoradia


class CondicaoMoradiaSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CondicaoMoradia
        load_instance = True

    moradia_id = ma.auto_field(dump_only=True)
    familia_id = ma.auto_field()
    tipo_moradia = ma.auto_field()
    valor_aluguel = ma.auto_field()
    tem_agua_encanada = ma.auto_field()
    tem_rede_esgoto = ma.auto_field()
    tem_energia_eletrica = ma.auto_field()
    tem_fogao = ma.auto_field()
    tem_geladeira = ma.auto_field()
    quantidade_camas = ma.auto_field()
    quantidade_tvs = ma.auto_field()
    quantidade_ventiladores = ma.auto_field()
    data_hora_log_utc = ma.auto_field(dump_only=True)
