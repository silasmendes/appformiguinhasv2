from app import ma
from app.models.demanda_tipo import DemandaTipo

class DemandaTipoSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DemandaTipo
        load_instance = True

    demanda_tipo_id = ma.auto_field(dump_only=True)
    demanda_tipo_nome = ma.auto_field()
    data_hora_log_utc = ma.auto_field(dump_only=True)
