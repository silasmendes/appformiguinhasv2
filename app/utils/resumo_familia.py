import json
import logging
import hashlib
from decimal import Decimal
from openai import AzureOpenAI
from flask import current_app
from typing import Dict, Any, Optional
from app.utils.openai_usage_tracker import OpenAIUsageTracker

logger = logging.getLogger(__name__)

class ResumoFamiliaService:
    def __init__(self):
        self.client = None
        self.cache = {}  # Cache simples para evitar regenerar resumos idênticos
    
    def _get_cache_key(self, data: Dict[str, Any]) -> str:
        """Gera uma chave única para o cache baseada nos dados"""
        # Serializa os dados e gera um hash, convertendo Decimal para string
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False, default=self._json_serializer)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _json_serializer(self, obj):
        """Serializa objetos não-JSON nativos"""
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _get_client(self):
        """Obtém o cliente Azure OpenAI, inicializando se necessário"""
        if self.client is None:
            try:
                # Verifica se as configurações necessárias estão disponíveis
                api_key = current_app.config.get('AZURE_OPENAI_API_KEY')
                endpoint = current_app.config.get('AZURE_OPENAI_ENDPOINT')
                api_version = current_app.config.get('AZURE_OPENAI_API_VERSION')
                
                if not all([api_key, endpoint, api_version]):
                    logger.warning("Configurações do Azure OpenAI não encontradas no arquivo .env")
                    return None
                
                self.client = AzureOpenAI(
                    api_key=api_key,
                    api_version=api_version,
                    azure_endpoint=endpoint
                )
                logger.info("Cliente Azure OpenAI inicializado com sucesso")
                
            except Exception as e:
                logger.error(f"Erro ao inicializar cliente Azure OpenAI: {e}")
                self.client = None
        return self.client
    
    def _remove_pii(self, cadastro_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove informações pessoais identificáveis (PII) dos dados"""
        if not cadastro_data:
            return {}
        
        # Lista de chaves que contêm PII
        pii_keys = [
            'nome_responsavel', 'cpf', 'rg', 'nome_completo',
            'telefone', 'email', 'whatsapp', 'celular',
            'logradouro', 'numero', 'complemento', 'cep',
            'nome_mae', 'nome_pai', 'naturalidade', 'nome'
        ]
        
        # Cria uma cópia dos dados sem PII
        clean_data = self._convert_decimals(cadastro_data.copy())
        
        # Remove chaves PII do nível raiz
        for key in pii_keys:
            clean_data.pop(key, None)
        
        # Remove PII de listas aninhadas (ex: membros da família)
        if 'membros_familia' in clean_data:
            for membro in clean_data['membros_familia']:
                for key in pii_keys:
                    membro.pop(key, None)
        
        # Remove PII de outros objetos aninhados mantendo estrutura
        for nested_key in ['contatos', 'enderecos', 'educacao', 'saude']:
            if nested_key in clean_data and isinstance(clean_data[nested_key], dict):
                for key in pii_keys:
                    clean_data[nested_key].pop(key, None)
            elif nested_key in clean_data and isinstance(clean_data[nested_key], list):
                for item in clean_data[nested_key]:
                    if isinstance(item, dict):
                        for key in pii_keys:
                            item.pop(key, None)
        
        return clean_data
    
    def _convert_decimals(self, data):
        """Converte objetos Decimal para float recursivamente"""
        if isinstance(data, dict):
            return {k: self._convert_decimals(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_decimals(item) for item in data]
        elif isinstance(data, Decimal):
            return float(data)
        else:
            return data
    
    def _create_prompt(self, clean_data: Dict[str, Any]) -> str:
        """Cria o prompt para o Azure OpenAI"""
        json_data = json.dumps(clean_data, indent=2, ensure_ascii=False)
        
        prompt = f"""
Analise os dados abaixo em formato JSON de uma família em situação de vulnerabilidade social e gere um resumo detalhado da situação. Destaque os principais desafios sociais, estruturais e econômicos enfrentados pela família.

Dados da família:
{json_data}

Instruções detalhadas:
- Crie um resumo de 2-3 frases bem estruturadas
- Identifique e destaque os principais problemas: moradia precária, falta de saneamento básico, baixa renda, problemas de saúde, falta de acesso à educação infantil, desemprego/trabalho informal
- Use linguagem técnica apropriada para assistentes sociais
- Foque nas condições que mais impactam a qualidade de vida da família
- Mencione demandas urgentes quando existirem
- Não inclua dados pessoais identificáveis (nomes, documentos, endereços específicos)
- Seja específico sobre as condições encontradas (ex: "ausência de água encanada e rede de esgoto", "moradia sem geladeira", "doença crônica que afeta visão")

Gere um resumo profissional e detalhado:
"""
        return prompt
    
    def gerar_resumo(self, cadastro_data: Dict[str, Any]) -> str:
        """Gera resumo inteligente da situação familiar"""
        if not cadastro_data:
            return "Dados da família não disponíveis para análise."
        
        # Remove PII dos dados
        clean_data = self._remove_pii(cadastro_data)
        
        if not clean_data:
            return "Dados da família não disponíveis para análise."
        
        # Verifica cache
        cache_key = self._get_cache_key(clean_data)
        if cache_key in self.cache:
            logger.info("Resumo obtido do cache")
            return self.cache[cache_key]
        
        client = self._get_client()
        
        if not client:
            logger.warning("Cliente Azure OpenAI não disponível, usando resumo padrão")
            resumo = self._get_fallback_summary(cadastro_data)
            self.cache[cache_key] = resumo
            return resumo
        
        try:
            # Cria o prompt
            prompt = self._create_prompt(clean_data)
            
            # Faz a chamada para o Azure OpenAI
            response = client.chat.completions.create(
                model=current_app.config.get('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[
                    {"role": "system", "content": "Você é um assistente social experiente especializado em análise de situações familiares em vulnerabilidade. Seu objetivo é fornecer resumos detalhados e precisos sobre a situação socioeconômica das famílias, destacando os principais desafios e necessidades. Use linguagem técnica apropriada e seja específico sobre as condições encontradas."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            resumo = response.choices[0].message.content.strip()
            
            # Registrar o uso de tokens
            OpenAIUsageTracker.track_usage(
                endpoint="chat/completions",
                model=current_app.config.get('AZURE_OPENAI_DEPLOYMENT_NAME'),
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                request_type="resumo_familia",
                success=True
            )
            
            # Log da operação (sem dados sensíveis)
            logger.info(f"Resumo gerado com sucesso via Azure OpenAI. Tamanho: {len(resumo)} caracteres")
            
            # Salva no cache
            self.cache[cache_key] = resumo
            
            return resumo
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo com Azure OpenAI: {e}")
            
            # Registrar erro de uso
            OpenAIUsageTracker.track_usage(
                endpoint="chat/completions",
                model=current_app.config.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'unknown'),
                prompt_tokens=0,
                completion_tokens=0,
                request_type="resumo_familia",
                success=False,
                error_message=str(e)
            )
            
            resumo = self._get_fallback_summary(cadastro_data)
            self.cache[cache_key] = resumo
            return resumo
    
    def _get_fallback_summary(self, cadastro_data: Dict[str, Any]) -> str:
        """Gera resumo básico quando Azure OpenAI não está disponível"""
        if not cadastro_data:
            return "Informações da família não disponíveis."
        
        summary_parts = []
        challenges = []
        
        # Composição familiar
        total_residentes = cadastro_data.get('total_residentes', 0)
        if total_residentes > 0:
            summary_parts.append(f"composta por {total_residentes} pessoas")
        
        # Situação financeira
        renda = cadastro_data.get('renda_familiar_total')
        if renda and float(renda) < 1000:
            challenges.append("baixa renda")
        
        # Condições de moradia
        agua_encanada = cadastro_data.get('agua_encanada')
        if agua_encanada == 'Não':
            challenges.append("ausência de água encanada")
        
        esgoto = cadastro_data.get('rede_esgoto')
        if esgoto == 'Não':
            challenges.append("sem rede de esgoto")
        
        # Demandas
        demandas = cadastro_data.get('demandas', [])
        if demandas:
            demandas_urgentes = [d for d in demandas if d.get('prioridade') == 'Alta']
            if demandas_urgentes:
                challenges.append("demandas urgentes")
        
        # Saúde
        medicacao = cadastro_data.get('descricao_medicacao')
        if medicacao and medicacao.strip():
            challenges.append("necessidades médicas")
        
        # Educação
        creche = cadastro_data.get('filho_creche')
        if creche == 'Não':
            challenges.append("falta de acesso à creche")
        
        # Constrói o resumo
        if summary_parts and challenges:
            return f"Família {' '.join(summary_parts)} enfrentando {', '.join(challenges)}."
        elif summary_parts:
            return f"Família {' '.join(summary_parts)} em acompanhamento social."
        else:
            return "Família em acompanhamento social."

# Instância global do serviço - será inicializada sob demanda
_resumo_service = None

def get_resumo_service():
    """Obtém a instância do serviço de resumo, criando se necessário"""
    global _resumo_service
    if _resumo_service is None:
        _resumo_service = ResumoFamiliaService()
    return _resumo_service

def gerar_resumo_familia(cadastro_data: Dict[str, Any]) -> str:
    """Função helper para gerar resumo da família"""
    if not cadastro_data:
        return "Informações da família não disponíveis."
    
    try:
        service = get_resumo_service()
        return service.gerar_resumo(cadastro_data)
    except Exception as e:
        logger.error(f"Erro ao gerar resumo da família: {e}")
        return "Erro ao gerar resumo da família."
