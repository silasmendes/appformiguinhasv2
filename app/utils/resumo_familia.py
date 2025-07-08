import json
import logging
import hashlib
from decimal import Decimal
from openai import AzureOpenAI
from flask import current_app, session
from typing import Dict, Any, Optional
from app.utils.openai_usage_tracker import OpenAIUsageTracker
from app import db
from app.models.resumo_familia_ia import ResumoFamiliaIA
from datetime import datetime, timezone, timedelta

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
Analise os dados abaixo de uma família em vulnerabilidade social e gere um resumo CONCISO em formato Markdown.

Dados da família:
{json_data}

INSTRUÇÕES OBRIGATÓRIAS:
- Máximo 3 frases curtas e diretas
- Use **negrito** para destacar os problemas mais críticos
- Use *itálico* para condições secundárias
- Foque apenas nos 2-3 desafios mais graves
- Linguagem técnica e objetiva
- NÃO inclua dados pessoais

FORMATO OBRIGATÓRIO:
Família de X pessoas enfrentando **[problema crítico 1]** e **[problema crítico 2]**. *[Condição secundária]* agrava a situação. Demandas urgentes: **[demanda prioritária]**.

EXEMPLO:
Família de 4 pessoas com **baixa renda** e **ausência de saneamento básico**. *Problemas de saúde crônicos* comprometem a qualidade de vida. Demandas urgentes: **moradia adequada**.

Seja CONCISO - máximo 400 caracteres:
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
                    {"role": "system", "content": "Você é um especialista em análise social que gera resumos CONCISOS em Markdown. Seja direto, objetivo e use formatação Markdown para destacar problemas críticos. Máximo 400 caracteres por resposta."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,  # Reduzido significativamente para forçar concisão
                temperature=0.1,  # Menor para mais consistência
                top_p=0.8,
                frequency_penalty=0.2,  # Evita repetições
                presence_penalty=0.3   # Força novidade nas palavras
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
        """Gera resumo básico em Markdown quando Azure OpenAI não está disponível"""
        if not cadastro_data:
            return "Informações da família não disponíveis."
        
        summary_parts = []
        critical_issues = []
        secondary_issues = []
        
        # Composição familiar
        total_residentes = cadastro_data.get('total_residentes', 0)
        if total_residentes > 0:
            summary_parts.append(f"Família de {total_residentes} pessoas")
        
        # Situação financeira (crítico)
        renda = cadastro_data.get('renda_familiar_total')
        if renda and float(renda) < 1000:
            critical_issues.append("**baixa renda**")
        
        # Condições de moradia (crítico)
        agua_encanada = cadastro_data.get('agua_encanada')
        esgoto = cadastro_data.get('rede_esgoto')
        if agua_encanada == 'Não' or esgoto == 'Não':
            critical_issues.append("**ausência de saneamento básico**")
        
        # Demandas urgentes (crítico)
        demandas = cadastro_data.get('demandas', [])
        demandas_urgentes = [d for d in demandas if d.get('prioridade') == 'Alta']
        if demandas_urgentes:
            critical_issues.append("**demandas urgentes**")
        
        # Saúde (secundário)
        medicacao = cadastro_data.get('descricao_medicacao')
        if medicacao and medicacao.strip() and medicacao != 'Sem medicação':
            secondary_issues.append("*necessidades médicas*")
        
        # Educação (secundário)
        creche = cadastro_data.get('filho_creche')
        if creche == 'Não':
            secondary_issues.append("*falta de acesso à creche*")
        
        # Constrói o resumo em Markdown
        if summary_parts and critical_issues:
            base = f"{' '.join(summary_parts)} enfrentando {' e '.join(critical_issues[:2])}"
            
            if secondary_issues:
                base += f". {secondary_issues[0]} agrava a situação"
            
            return base + "."
        elif summary_parts:
            return f"{' '.join(summary_parts)} em acompanhamento social."
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

def buscar_resumo_recente(familia_id: int, horas: int = 12) -> Optional[str]:
    """Busca resumo existente para a família nas últimas X horas"""
    try:
        limite_tempo = datetime.now(timezone.utc) - timedelta(hours=horas)
        
        resumo_recente = ResumoFamiliaIA.query.filter(
            ResumoFamiliaIA.familia_id == familia_id,
            ResumoFamiliaIA.data_hora_geracao >= limite_tempo
        ).order_by(ResumoFamiliaIA.data_hora_geracao.desc()).first()
        
        if resumo_recente:
            tempo_decorrido = datetime.now(timezone.utc) - resumo_recente.data_hora_geracao
            horas_decorridas = tempo_decorrido.total_seconds() / 3600
            logger.info(f"Resumo encontrado para família {familia_id} gerado em {resumo_recente.data_hora_geracao}")
            logger.debug(f"🔄 RESUMO REAPROVEITADO - Família {familia_id}: Evitada nova chamada OpenAI. "
                        f"Resumo gerado há {horas_decorridas:.1f}h. Economia de tokens e tempo!")
            return resumo_recente.resumo_texto
        
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar resumo recente: {e}")
        return None

def salvar_resumo_no_banco(familia_id: int, resumo_texto: str) -> Optional[ResumoFamiliaIA]:
    """Salva o resumo gerado pela IA no banco de dados"""
    try:
        novo_resumo = ResumoFamiliaIA(
            familia_id=familia_id,
            resumo_texto=resumo_texto
        )
        db.session.add(novo_resumo)
        db.session.commit()
        logger.info(f"Resumo salvo no banco para família ID {familia_id}")
        return novo_resumo
    except Exception as e:
        logger.error(f"Erro ao salvar resumo no banco: {e}")
        db.session.rollback()
        return None

def gerar_resumo_familia(cadastro_data: Dict[str, Any]) -> str:
    """Função helper para gerar resumo da família"""
    if not cadastro_data:
        return "Informações da família não disponíveis."
    
    try:
        # Verificar se temos familia_id na sessão
        familia_id = session.get('familia_id')
        
        # Se temos familia_id, verificar se já existe resumo recente (últimas 12 horas)
        if familia_id:
            resumo_existente = buscar_resumo_recente(familia_id, horas=12)
            if resumo_existente:
                logger.info(f"Reutilizando resumo existente para família {familia_id}")
                logger.debug(f"✅ ECONOMIA DE RECURSOS - Resumo reaproveitado para família {familia_id}. "
                           f"Nova chamada OpenAI evitada! Cache de 12h funcionando.")
                return resumo_existente
        
        # Se não há resumo recente ou não temos familia_id, gerar novo resumo
        logger.debug(f"🔥 NOVO RESUMO SENDO GERADO - Família {familia_id or 'SEM_ID'}: "
                    f"Nenhum resumo encontrado nas últimas 12h. Chamada OpenAI necessária.")
        service = get_resumo_service()
        resumo = service.gerar_resumo(cadastro_data)
        
        # Salvar resumo no banco de dados se temos familia_id e resumo válido
        if familia_id and resumo and resumo not in [
            "Informações da família não disponíveis.", 
            "Erro ao gerar resumo da família.",
            "Dados da família não disponíveis para análise."
        ]:
            salvar_resumo_no_banco(familia_id, resumo)
        
        return resumo
    except Exception as e:
        logger.error(f"Erro ao gerar resumo da família: {e}")
        return "Erro ao gerar resumo da família."
