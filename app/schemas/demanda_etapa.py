from app import ma
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
from app.models.demanda_etapa import DemandaEtapa

class DemandaEtapaSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DemandaEtapa
        load_instance = True

    etapa_id = ma.auto_field(dump_only=True)
    demanda_id = ma.auto_field()
    data_atualizacao = ma.auto_field()
    status_atual = ma.auto_field()
    observacao = ma.auto_field()
    usuario_atualizacao = ma.auto_field()

    @validates("status_atual")
    def validar_status(self, value, **kwargs):
        if value not in STATUS_PERMITIDOS:
            raise ValidationError("Status inválido.")
