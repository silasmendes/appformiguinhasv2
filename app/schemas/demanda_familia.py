from app import ma
from app.models.demanda_familia import DemandaFamilia

class DemandaFamiliaSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DemandaFamilia
        load_instance = True

    demanda_id = ma.auto_field(dump_only=True)
    familia_id = ma.auto_field()
    demanda_tipo_id = ma.auto_field()
    descricao = ma.auto_field()
    data_identificacao = ma.auto_field()
    prioridade = ma.auto_field()
    data_hora_log_utc = ma.auto_field(dump_only=True)
