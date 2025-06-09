from app import ma
from app.models.contato import Contato


class ContatoSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Contato
        load_instance = True

    contato_id = ma.auto_field(dump_only=True)
    familia_id = ma.auto_field()
    telefone_principal = ma.auto_field()
    telefone_principal_whatsapp = ma.auto_field()
    telefone_principal_nome_contato = ma.auto_field()
    telefone_alternativo = ma.auto_field()
    telefone_alternativo_whatsapp = ma.auto_field()
    telefone_alternativo_nome_contato = ma.auto_field()
    email_responsavel = ma.auto_field()
    data_hora_log_utc = ma.auto_field(dump_only=True)
