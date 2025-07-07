from decimal import Decimal
import json

def convert_decimals(data):
    """Converte objetos Decimal para float recursivamente"""
    if isinstance(data, dict):
        return {k: convert_decimals(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimals(item) for item in data]
    elif isinstance(data, Decimal):
        return float(data)
    else:
        return data

# Teste
test_data = {
    'renda_familiar_total': Decimal('1500.50'),
    'total_gastos': Decimal('800.25'),
    'nome_responsavel': 'João Silva'
}

print("Dados originais:", test_data)
converted = convert_decimals(test_data)
print("Dados convertidos:", converted)
print("JSON serialization:", json.dumps(converted))
print("Conversão bem sucedida!")
