from app import ma
from app.models.endereco import Endereco

class EnderecoSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Endereco
        load_instance = True

    endereco_id = ma.auto_field(dump_only=True)
    familia_id = ma.auto_field(required=True)
    cep = ma.auto_field()
    preenchimento_manual = ma.auto_field()
    logradouro = ma.auto_field()
    numero = ma.auto_field()
    complemento = ma.auto_field()
    bairro = ma.auto_field()
    cidade = ma.auto_field()
    estado = ma.auto_field()
    ponto_referencia = ma.auto_field()
    data_hora_log_utc = ma.auto_field(dump_only=True)
