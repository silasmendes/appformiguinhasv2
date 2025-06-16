from app import ma, db
from app.models.demanda_familia import DemandaFamilia
from app.models.demanda_tipo import DemandaTipo
from marshmallow import validates, ValidationError

STATUS_PERMITIDOS = [
    "Em análise",
    "Em andamento",
    "Encaminhada",
    "Aguardando resposta",
    "Suspensa",
    "Cancelada",
    "Concluída",
]

DEMANDA_TIPOS_VALIDOS = [1, 2, 3, 4, 5, 6, 7]

class DemandaFamiliaSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DemandaFamilia
        load_instance = True

    demanda_id = ma.auto_field(dump_only=True)
    familia_id = ma.auto_field()
    demanda_tipo_id = ma.auto_field()
    status = ma.auto_field()
    descricao = ma.auto_field()
    data_identificacao = ma.auto_field()
    prioridade = ma.auto_field()
    data_hora_log_utc = ma.auto_field(dump_only=True)

    @validates("status")
    def validar_status(self, value, **kwargs):
        if value not in STATUS_PERMITIDOS:
            raise ValidationError("Status inválido.")

    @validates("demanda_tipo_id")
    def validar_demanda_tipo(self, value, **kwargs):
        if value not in DEMANDA_TIPOS_VALIDOS:
            raise ValidationError("demanda_tipo_id inválido.")
        if not db.session.get(DemandaTipo, value):
            raise ValidationError("demanda_tipo_id não encontrado.")
