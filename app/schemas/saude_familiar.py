from app import ma
from app.models.saude_familiar import SaudeFamiliar

class SaudeFamiliarSchema(ma.SQLAlchemySchema):
    class Meta:
        model = SaudeFamiliar
        load_instance = True

    saude_id = ma.auto_field(dump_only=True)
    familia_id = ma.auto_field(required=True)
    tem_doenca_cronica = ma.auto_field()
    descricao_doenca_cronica = ma.auto_field()
    usa_medicacao_continua = ma.auto_field()
    descricao_medicacao = ma.auto_field()
    tem_deficiencia = ma.auto_field()
    descricao_deficiencia = ma.auto_field()
    recebe_bpc = ma.auto_field()
    data_hora_log_utc = ma.auto_field(dump_only=True)
