from app import ma
from app.models.composicao_familiar import ComposicaoFamiliar

class ComposicaoFamiliarSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ComposicaoFamiliar
        load_instance = True

    composicao_id = ma.auto_field(dump_only=True)
    familia_id = ma.auto_field()
    total_residentes = ma.auto_field()
    quantidade_bebes = ma.auto_field()
    quantidade_criancas = ma.auto_field()
    quantidade_adolescentes = ma.auto_field()
    quantidade_adultos = ma.auto_field()
    quantidade_idosos = ma.auto_field()
    tem_menores_na_escola = ma.auto_field()
    motivo_ausencia_escola = ma.auto_field()
