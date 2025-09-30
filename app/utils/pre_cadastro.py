"""
Utilitários para trabalhar com dados de pré-cadastro.
"""
import pyodbc
from datetime import datetime
from config import Config
from typing import List, Dict, Optional


def get_pre_cadastro_connection():
    """
    Cria uma conexão direta com o banco de pré-cadastro.
    """
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={Config.DB_SERVER};"
        f"DATABASE={Config.DB_NAME_PRE_CADASTRO};"
        f"UID={Config.DB_USER};"
        f"PWD={Config.DB_PASSWORD};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )
    return pyodbc.connect(connection_string)


def buscar_pre_cadastros(termo_busca: str) -> List[Dict]:
    """
    Busca pré-cadastros no banco usando uma query direta.
    Filtra os resultados por nome ou CPF no código Python.
    """
    try:
        with get_pre_cadastro_connection() as conn:
            cursor = conn.cursor()
            # Usar uma query que converte os campos problemáticos para string
            sql_query = """
            SELECT 
                f.familia_precadastro_id,
                f.nome_responsavel,
                f.data_nascimento,
                f.genero,
                f.genero_autodeclarado,
                f.estado_civil,
                f.rg,
                f.cpf,
                f.autoriza_uso_imagem,
                f.status_cadastro,
                CONVERT(varchar, f.data_hora_log_utc, 120) AS data_log_familia,
                e.cep,
                e.preenchimento_manual,
                e.logradouro,
                e.numero,
                e.complemento,
                e.bairro,
                e.cidade,
                e.estado,
                e.ponto_referencia,
                CONVERT(varchar, e.data_hora_log_utc, 120) AS data_log_endereco,
                cf.total_residentes,
                cf.quantidade_bebes,
                cf.quantidade_criancas,
                cf.quantidade_adolescentes,
                cf.quantidade_adultos,
                cf.quantidade_idosos,
                cf.tem_menores_na_escola,
                cf.motivo_ausencia_escola,
                CONVERT(varchar, cf.data_hora_log_utc, 120) AS data_log_composicao,
                c.telefone_principal,
                c.telefone_principal_whatsapp,
                c.telefone_principal_nome_contato,
                c.telefone_alternativo,
                c.telefone_alternativo_whatsapp,
                c.telefone_alternativo_nome_contato,
                c.email_responsavel,
                CONVERT(varchar, c.data_hora_log_utc, 120) AS data_log_contato
            FROM [dbo].[familias] f
            LEFT JOIN [dbo].[enderecos] e 
                ON f.familia_precadastro_id = e.familia_precadastro_id
            LEFT JOIN [dbo].[composicao_familiar] cf 
                ON f.familia_precadastro_id = cf.familia_precadastro_id
            LEFT JOIN [dbo].[contatos] c 
                ON f.familia_precadastro_id = c.familia_precadastro_id
            ORDER BY f.familia_precadastro_id
            """
            cursor.execute(sql_query)
            
            # Mapear colunas para facilitar acesso
            columns = [column[0] for column in cursor.description]
            resultados = []
            
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                
                # Filtrar por termo de busca (nome ou CPF)
                nome = row_dict.get('nome_responsavel', '').lower() if row_dict.get('nome_responsavel') else ''
                cpf = row_dict.get('cpf', '').replace('.', '').replace('-', '').replace('/', '') if row_dict.get('cpf') else ''
                termo_limpo = termo_busca.lower().replace('.', '').replace('-', '').replace('/', '')
                
                if termo_limpo in nome or termo_limpo in cpf:
                    # Formatar data para exibição
                    data_log = row_dict.get('data_log_familia')
                    if data_log:
                        try:
                            if isinstance(data_log, datetime):
                                data_formatada = data_log.strftime('%d/%m/%Y')
                            else:
                                # Se já é string, tentar converter para datetime e depois formatar
                                data_str = str(data_log)[:10]  # Pegar só a parte da data
                                if len(data_str) == 10 and '-' in data_str:
                                    parts = data_str.split('-')
                                    if len(parts) == 3:
                                        data_formatada = f"{parts[2]}/{parts[1]}/{parts[0]}"
                                    else:
                                        data_formatada = data_str
                                else:
                                    data_formatada = data_str
                        except:
                            data_formatada = str(data_log)[:10] if data_log else 'Não informado'
                    else:
                        data_formatada = 'Não informado'
                    
                    resultados.append({
                        'familia_precadastro_id': row_dict.get('familia_precadastro_id'),
                        'nome_responsavel': row_dict.get('nome_responsavel'),
                        'cpf': row_dict.get('cpf'),
                        'data_pre_cadastro': data_formatada,
                        'dados_completos': row_dict  # Manter todos os dados para uso posterior
                    })
            
            return resultados
            
    except Exception as e:
        print(f"Erro ao buscar pré-cadastros: {str(e)}")
        return []


def _bool_to_sim_nao(valor):
    """Converte boolean para 'Sim'/'Não', igual à função do fluxo_atendimento."""
    if valor is None:
        return None
    return "Sim" if valor else "Não"


def _format_date_from_db(date_value):
    """
    Formata uma data do banco de dados para o formato brasileiro dd/mm/yyyy.
    TRATA: datetime.date, datetime, strings GMT, strings ISO.
    """
    if date_value is None:
        return None
    
    try:
        # Se já é um objeto date ou datetime, formatar diretamente
        if hasattr(date_value, 'strftime'):
            return date_value.strftime('%d/%m/%Y')
        
        # Se é string, tentar diferentes formatos
        date_str = str(date_value).strip()
        if not date_str or date_str.lower() in ['none', 'null', '']:
            return None
        
        # Formato GMT: 'Tue, 04 Jan 2011 00:00:00 GMT'
        if 'GMT' in date_str:
            from datetime import datetime
            # Parsear o formato GMT
            date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
            return date_obj.strftime('%d/%m/%Y')
        
        # Formato ISO: 2011-01-04 ou 2011-01-04 00:00:00
        if '-' in date_str:
            date_part = date_str.split(' ')[0]
            if len(date_part) == 10:  # YYYY-MM-DD
                year, month, day = date_part.split('-')
                if year.isdigit() and month.isdigit() and day.isdigit():
                    date_obj = datetime(int(year), int(month), int(day))
                    return date_obj.strftime('%d/%m/%Y')
        
        return None
        
    except Exception as e:
        print(f"ERRO ao formatar data {repr(date_value)}: {str(e)}")
        return None


def _safe_get_string(data: Dict, key: str) -> str:
    """Pega um valor do dict e converte None para string vazia."""
    value = data.get(key)
    return '' if value is None else str(value)


def converter_pre_cadastro_para_sessao(dados_pre_cadastro: Dict) -> Dict:
    """
    Converte dados do pré-cadastro para o formato usado na sessão de atendimento.
    CORRIGE: Todos os None viram string vazia para não aparecer "None" nos formulários.
    """
    cadastro = {}
    cadastro['novo_cadastro'] = 1
    cadastro['origem_pre_cadastro'] = True
    cadastro['familia_precadastro_id'] = dados_pre_cadastro.get('familia_precadastro_id')
    
    # Dados pessoais - CORRIGINDO None para string vazia
    cadastro.update({
        'nome_responsavel': _safe_get_string(dados_pre_cadastro, 'nome_responsavel'),
        'data_nascimento': _format_date_from_db(dados_pre_cadastro.get('data_nascimento')),
        'genero': _safe_get_string(dados_pre_cadastro, 'genero'),
        'genero_autodeclarado': _safe_get_string(dados_pre_cadastro, 'genero_autodeclarado'),
        'estado_civil': _safe_get_string(dados_pre_cadastro, 'estado_civil'),
        'rg': _safe_get_string(dados_pre_cadastro, 'rg'),
        'cpf': _safe_get_string(dados_pre_cadastro, 'cpf'),
    })
    
    # Autorização de uso de imagem
    if dados_pre_cadastro.get('autoriza_uso_imagem') is not None:
        cadastro['autoriza_uso_imagem'] = _bool_to_sim_nao(dados_pre_cadastro.get('autoriza_uso_imagem'))
    else:
        cadastro['autoriza_uso_imagem'] = ''
    
    # Endereço - CORRIGINDO None para string vazia
    cadastro.update({
        'preenchimento_manual': _safe_get_string(dados_pre_cadastro, 'preenchimento_manual'),
        'cep': _safe_get_string(dados_pre_cadastro, 'cep'),
        'logradouro': _safe_get_string(dados_pre_cadastro, 'logradouro'),
        'numero': _safe_get_string(dados_pre_cadastro, 'numero'),
        'complemento': _safe_get_string(dados_pre_cadastro, 'complemento'),
        'bairro': _safe_get_string(dados_pre_cadastro, 'bairro'),
        'cidade': _safe_get_string(dados_pre_cadastro, 'cidade'),
        'estado': _safe_get_string(dados_pre_cadastro, 'estado'),
        'ponto_referencia': _safe_get_string(dados_pre_cadastro, 'ponto_referencia'),
    })
    
    # Composição familiar - números podem ficar None, strings viram vazias
    cadastro.update({
        'total_residentes': dados_pre_cadastro.get('total_residentes'),
        'quantidade_bebes': dados_pre_cadastro.get('quantidade_bebes'),
        'quantidade_criancas': dados_pre_cadastro.get('quantidade_criancas'),
        'quantidade_adolescentes': dados_pre_cadastro.get('quantidade_adolescentes'),
        'quantidade_adultos': dados_pre_cadastro.get('quantidade_adultos'),
        'quantidade_idosos': dados_pre_cadastro.get('quantidade_idosos'),
        'motivo_ausencia_escola': _safe_get_string(dados_pre_cadastro, 'motivo_ausencia_escola'),
    })
    
    # Menores na escola
    if dados_pre_cadastro.get('tem_menores_na_escola') is not None:
        cadastro['menores_na_escola'] = _bool_to_sim_nao(dados_pre_cadastro.get('tem_menores_na_escola'))
    else:
        cadastro['menores_na_escola'] = ''
    
    # Contatos - CORRIGINDO None para string vazia
    cadastro.update({
        'telefone_principal': _safe_get_string(dados_pre_cadastro, 'telefone_principal'),
        'telefone_principal_whatsapp': dados_pre_cadastro.get('telefone_principal_whatsapp'),  # boolean pode ficar None
        'telefone_principal_nome_contato': _safe_get_string(dados_pre_cadastro, 'telefone_principal_nome_contato'),
        'telefone_alternativo': _safe_get_string(dados_pre_cadastro, 'telefone_alternativo'),
        'telefone_alternativo_whatsapp': dados_pre_cadastro.get('telefone_alternativo_whatsapp'),  # boolean pode ficar None
        'telefone_alternativo_nome_contato': _safe_get_string(dados_pre_cadastro, 'telefone_alternativo_nome_contato'),
        'email_responsavel': _safe_get_string(dados_pre_cadastro, 'email_responsavel'),
    })
    
    return cadastro