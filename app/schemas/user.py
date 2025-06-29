from datetime import datetime
from marshmallow import validates_schema, ValidationError, validates, fields
from marshmallow.validate import OneOf, Length
from app import ma
from app.models.usuario import Usuario

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Usuario
        load_instance = True
        sqla_session = None

    id = ma.auto_field(dump_only=True)
    login = ma.auto_field(required=True)
    nome_completo = ma.auto_field(required=True)
    email = ma.auto_field()
    tipo = ma.auto_field(required=True, validate=OneOf(['admin', 'temporario']))
    senha = fields.String(load_only=True, required=True, validate=Length(min=6))
    expires_at = ma.auto_field()
    last_login_at = ma.auto_field(dump_only=True)
    created_at = ma.auto_field(dump_only=True)

    @validates_schema
    def validate_expires(self, data, **kwargs):
        if data.get('tipo') == 'temporario':
            expires = data.get('expires_at')
            if not expires:
                raise ValidationError('expires_at e obrigatorio para usuarios temporarios', 'expires_at')
            if expires <= datetime.utcnow():
                raise ValidationError('expires_at deve ser data futura', 'expires_at')
