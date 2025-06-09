from app import ma
from app.models.emprego_provedor import EmpregoProvedor

class EmpregoProvedorSchema(ma.SQLAlchemySchema):
    class Meta:
        model = EmpregoProvedor
        load_instance = True

    emprego_id = ma.auto_field(dump_only=True)
    familia_id = ma.auto_field()
    relacao_provedor_familia = ma.auto_field()
    descricao_provedor_externo = ma.auto_field()
    situacao_emprego = ma.auto_field()
    descricao_situacao_emprego_outro = ma.auto_field()
    profissao_provedor = ma.auto_field()
    experiencia_profissional = ma.auto_field()
    formacao_profissional = ma.auto_field()
    habilidades_relevantes = ma.auto_field()
