from app import ma
from app.models.educacao_entrevistado import EducacaoEntrevistado


class EducacaoEntrevistadoSchema(ma.SQLAlchemySchema):
    class Meta:
        model = EducacaoEntrevistado
        load_instance = True

    educacao_id = ma.auto_field(dump_only=True)
    familia_id = ma.auto_field()
    nivel_escolaridade = ma.auto_field()
    estuda_atualmente = ma.auto_field()
    curso_ou_serie_atual = ma.auto_field()
    data_hora_log_utc = ma.auto_field(dump_only=True)
