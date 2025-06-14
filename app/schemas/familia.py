from app import ma
from app.models.familia import Familia
from marshmallow import validates, validates_schema, ValidationError
import re

ESTADOS_CIVIS_VALIDOS = [
    "Solteira(o)",
    "Casada(o)",
    "União Estável",
    "Divorciada(o)",
    "Viúva(o)",
]

class FamiliaSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Familia
        load_instance = True

    familia_id = ma.auto_field(dump_only=True)
    nome_responsavel = ma.auto_field()
    data_nascimento = ma.auto_field()
    genero = ma.auto_field()
    genero_autodeclarado = ma.auto_field()
    estado_civil = ma.auto_field()
    rg = ma.auto_field()
    cpf = ma.auto_field()
    autoriza_uso_imagem = ma.auto_field()
    status_cadastro = ma.auto_field()
    data_hora_log_utc = ma.auto_field(dump_only=True)

    @validates("estado_civil")
    def validar_estado_civil(self, value, **kwargs):
        if value not in ESTADOS_CIVIS_VALIDOS:
            raise ValidationError("Estado civil inválido.")

    @validates("cpf")
    # Recebe **kwargs para compatibilidade com marshmallow>=4,
    # que passa o argumento extra `data_key` aos validadores.
    def validar_cpf(self, value, **kwargs):
        if not value:
            return  # Aceita CPF em branco

        if not self._cpf_valido(value):
            raise ValidationError("CPF inválido.")

    def _cpf_valido(self, cpf):
        cpf = re.sub(r"\D", "", cpf)

        # Aceita CPFs com todos os dígitos iguais, como 00000000000 ou 11111111111
        if re.fullmatch(r"(\d)\1{10}", cpf):
            return True

        if len(cpf) != 11:
            return False

        # Validação dos dígitos verificadores
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = 11 - (soma % 11)
        if digito1 > 9:
            digito1 = 0
        if digito1 != int(cpf[9]):
            return False

        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = 11 - (soma % 11)
        if digito2 > 9:
            digito2 = 0
        if digito2 != int(cpf[10]):
            return False

        return True

    @validates("status_cadastro")
    def validar_status(self, value, **kwargs):
        if value not in ["rascunho", "finalizado"]:
            raise ValidationError("Status inválido.")

    @validates_schema
    def validate_genero_autodeclarado(self, data, **kwargs):
        genero = data.get("genero")
        autodeclarado = data.get("genero_autodeclarado")

        if genero != "Outro" and autodeclarado:
            raise ValidationError(
                "Campo 'genero_autodeclarado' só pode ser informado se genero = 'Outro'.",
                field_name="genero_autodeclarado",
            )

        if genero == "Outro" and not autodeclarado:
            raise ValidationError(
                "Quando genero = 'Outro', o campo 'genero_autodeclarado' é obrigatório.",
                field_name="genero_autodeclarado",
            )
