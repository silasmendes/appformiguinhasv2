from app import ma
from app.models.familia import Familia
from marshmallow import validates, ValidationError
import re

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

    @validates("cpf")
    # Recebe **kwargs para compatibilidade com marshmallow>=4,
    # que passa o argumento extra `data_key` aos validadores.
    def validar_cpf(self, value, **kwargs):
        if not self._cpf_valido(value):
            raise ValidationError("CPF inválido.")

    def _cpf_valido(self, cpf):
        cpf = re.sub(r"\D", "", cpf)
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        for i in range(9, 11):
            soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(0, i))
            digito = ((soma * 10) % 11) % 10
            if digito != int(cpf[i]):
                return False

        return True
