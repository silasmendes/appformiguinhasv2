from app import ma
from app.models.resumo_familia_ia import ResumoFamiliaIA

class ResumoFamiliaIASchema(ma.SQLAlchemySchema):
    class Meta:
        model = ResumoFamiliaIA
        load_instance = True

    resumo_id = ma.auto_field(dump_only=True)
    familia_id = ma.auto_field(required=True)
    resumo_texto = ma.auto_field(required=True)
    data_hora_geracao = ma.auto_field(dump_only=True)

# Instâncias dos schemas
resumo_familia_ia_schema = ResumoFamiliaIASchema()
resumos_familia_ia_schema = ResumoFamiliaIASchema(many=True)
