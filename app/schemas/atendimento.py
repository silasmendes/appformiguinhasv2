from app import ma
from app.models.atendimento import Atendimento
from marshmallow import validates, ValidationError

PERCEPCAO_VALIDOS = ["Alta", "Media", "Baixa", "Inativo", "Excluído"]

class AtendimentoSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Atendimento
        load_instance = True

    atendimento_id = ma.auto_field(dump_only=True)
    familia_id = ma.auto_field(required=True)
    usuario_atendente_id = ma.auto_field()
    percepcao_necessidade = ma.auto_field()
    duracao_necessidade = ma.auto_field()
    motivo_duracao = ma.auto_field()
    cesta_entregue = ma.auto_field()
    data_entrega_cesta = ma.auto_field()
    data_hora_atendimento = ma.auto_field(dump_only=True)

    @validates("percepcao_necessidade")
    def validar_percepcao(self, value, **kwargs):
        if value not in PERCEPCAO_VALIDOS:
            raise ValidationError("percepcao_necessidade inválida.")

