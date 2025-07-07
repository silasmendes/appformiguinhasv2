from datetime import datetime
from marshmallow import validates_schema, ValidationError, validates, fields, pre_load
from marshmallow.validate import OneOf, Length
from app import ma, db
from app.models.usuario import Usuario

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Usuario
        load_instance = True
        # Use the default SQLAlchemy session so that calls to ``load`` or
        # ``validate`` have a session available. Without this, ``validate``
        # raises ``ValueError: Validation requires a session`` when the schema
        # is used in the user creation form.
        sqla_session = db.session

    id = ma.auto_field(dump_only=True)
    login = ma.auto_field(required=True)
    nome_completo = ma.auto_field(required=True)
    email = ma.auto_field()
    tipo = ma.auto_field(required=True, validate=OneOf(['admin', 'temporario']))
    senha = fields.String(load_only=True, required=True, validate=Length(min=6))
    expires_at = fields.DateTime(allow_none=True)
    last_login_at = ma.auto_field(dump_only=True)
    created_at = ma.auto_field(dump_only=True)

    @pre_load
    def convert_expires_at(self, data, **kwargs):
        """Converte data do formato brasileiro (dd/mm/yyyy hh:mm) para datetime"""
        if 'expires_at' in data and data['expires_at']:
            expires_str = data['expires_at'].strip()
            if expires_str:
                try:
                    # Tenta converter do formato brasileiro: dd/mm/yyyy hh:mm
                    data['expires_at'] = datetime.strptime(expires_str, '%d/%m/%Y %H:%M')
                except ValueError:
                    try:
                        # Tenta converter do formato ISO como fallback
                        data['expires_at'] = datetime.fromisoformat(expires_str.replace('T', ' '))
                    except ValueError:
                        # Se não conseguir converter, deixa como está para o Marshmallow gerar erro
                        pass
            else:
                data['expires_at'] = None
        return data

    @validates_schema
    def validate_expires(self, data, **kwargs):
        if data.get('tipo') == 'temporario':
            expires = data.get('expires_at')
            if not expires:
                raise ValidationError('expires_at e obrigatorio para usuarios temporarios', 'expires_at')
            if expires <= datetime.utcnow():
                raise ValidationError('expires_at deve ser data futura', 'expires_at')
