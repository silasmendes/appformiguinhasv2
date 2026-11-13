import json
import logging
import hashlib
from decimal import Decimal
from openai import OpenAI
from flask import current_app, session
from typing import Dict, Any, Optional
from app.utils.openai_usage_tracker import OpenAIUsageTracker
from app import db
from app.models.resumo_familia_ia import ResumoFamiliaIA
from app.models.openai_usage import OpenAIUsage
from app.models.atendimento import Atendimento
from app.models.demanda_familia import DemandaFamilia
from app.models.demanda_etapa import DemandaEtapa
from app.models.demanda_tipo import DemandaTipo
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
        """Obtém o cliente da API direta da OpenAI."""
        if self.client is None:
            try:
                # Verifica se as configurações necessárias estão disponíveis
                api_key = current_app.config.get('OPENAI_API_KEY', '').strip()
                
                if not api_key:
                    logger.warning("OPENAI_API_KEY não configurada; usando resumo local")
                    return None
                
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=current_app.config['OPENAI_BASE_URL'],
                    timeout=30.0,
                    max_retries=1,
                )
                logger.info("Cliente OpenAI inicializado com sucesso")
                
            except Exception as e:
                logger.error(f"Erro ao inicializar cliente OpenAI: {e}")
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
    
    def _fetch_additional_context(self, familia_id: int) -> Dict[str, Any]:
        """Busca dados adicionais de atendimentos e demandas do banco de dados"""
        context = {
            'ultimos_atendimentos': [],
            'demandas_ativas': [],
            'ultima_visita_domiciliar': None
        }
        
        if not familia_id:
            return context
        
        try:
            # Buscar últimos 3 atendimentos
            atendimentos = db.session.query(Atendimento).filter_by(
                familia_id=familia_id
            ).order_by(Atendimento.data_hora_atendimento.desc()).limit(3).all()
            
            for a in atendimentos:
                atend_info = {
                    'tipo_atendimento': a.tipo_atendimento,
                    'percepcao_necessidade': a.percepcao_necessidade,
                    'duracao_necessidade': a.duracao_necessidade,
                    'motivo_duracao': a.motivo_duracao,
                    'cesta_entregue': a.cesta_entregue,
                    'data_atendimento': a.data_hora_atendimento.strftime('%d/%m/%Y') if a.data_hora_atendimento else None,
                    'notas_visita': a.notas_visita
                }
                context['ultimos_atendimentos'].append(atend_info)
                
                # Registrar última visita domiciliar
                if a.tipo_atendimento == 'Visita domiciliar' and not context['ultima_visita_domiciliar']:
                    context['ultima_visita_domiciliar'] = {
                        'data': a.data_visita.strftime('%d/%m/%Y') if a.data_visita else a.data_hora_atendimento.strftime('%d/%m/%Y'),
                        'notas': a.notas_visita
                    }
            
            # Buscar demandas ativas (não concluídas/canceladas) com tipo e última etapa
            demandas = db.session.query(
                DemandaFamilia, DemandaTipo
            ).join(
                DemandaTipo, DemandaFamilia.demanda_tipo_id == DemandaTipo.demanda_tipo_id
            ).filter(
                DemandaFamilia.familia_id == familia_id,
                ~DemandaFamilia.status.in_(['Concluída', 'Cancelada'])
            ).all()
            
            for demanda, tipo in demandas:
                # Buscar a etapa mais recente desta demanda
                ultima_etapa = db.session.query(DemandaEtapa).filter_by(
                    demanda_id=demanda.demanda_id
                ).order_by(DemandaEtapa.data_atualizacao.desc()).first()
                
                demanda_info = {
                    'tipo': tipo.demanda_tipo_nome,
                    'descricao': demanda.descricao,
                    'status': demanda.status,
                    'prioridade': demanda.prioridade,
                    'data_identificacao': demanda.data_identificacao.strftime('%d/%m/%Y') if demanda.data_identificacao else None
                }
                
                if ultima_etapa:
                    demanda_info['ultimo_status'] = ultima_etapa.status_atual
                    demanda_info['ultima_observacao'] = ultima_etapa.observacao
                    demanda_info['data_ultima_atualizacao'] = ultima_etapa.data_atualizacao.strftime('%d/%m/%Y') if ultima_etapa.data_atualizacao else None
                
                context['demandas_ativas'].append(demanda_info)
            
            logger.info(f"Contexto adicional obtido: {len(context['ultimos_atendimentos'])} atendimentos, "
                       f"{len(context['demandas_ativas'])} demandas ativas")
                       
        except Exception as e:
            logger.error(f"Erro ao buscar contexto adicional para família {familia_id}: {e}")
        
        return context

    def _create_prompt(self, clean_data: Dict[str, Any], additional_context: Optional[Dict[str, Any]] = None) -> str:
        """Cria o prompt para o OpenAI"""
        json_data = json.dumps(clean_data, indent=2, ensure_ascii=False)
        
        # Montar seção de contexto adicional
        contexto_extra = ""
        if additional_context:
            partes = []
            
            # Atendimentos recentes
            atendimentos = additional_context.get('ultimos_atendimentos', [])
            if atendimentos:
                partes.append("\nÚLTIMOS ATENDIMENTOS:")
                for a in atendimentos:
                    linha = f"- {a.get('data_atendimento', 'N/A')} ({a.get('tipo_atendimento', 'N/A')}): "
                    linha += f"Necessidade {a.get('percepcao_necessidade', 'N/A')}, {a.get('duracao_necessidade', 'N/A')}"
                    if a.get('motivo_duracao'):
                        linha += f" ({a['motivo_duracao']})"
                    if a.get('cesta_entregue'):
                        linha += " | Cesta entregue"
                    if a.get('notas_visita'):
                        linha += f" | Notas: {a['notas_visita']}"
                    partes.append(linha)
            
            # Última visita domiciliar
            visita = additional_context.get('ultima_visita_domiciliar')
            if visita:
                partes.append(f"\nÚLTIMA VISITA DOMICILIAR: {visita.get('data', 'N/A')}")
                if visita.get('notas'):
                    partes.append(f"Observações da visita: {visita['notas']}")
            
            # Demandas ativas
            demandas = additional_context.get('demandas_ativas', [])
            if demandas:
                partes.append("\nDEMANDAS ATIVAS:")
                for d in demandas:
                    linha = f"- {d.get('tipo', 'N/A')} (Prioridade: {d.get('prioridade', 'N/A')}, Status: {d.get('status', 'N/A')})"
                    if d.get('descricao'):
                        linha += f" - {d['descricao']}"
                    if d.get('ultima_observacao'):
                        linha += f" | Última atualização ({d.get('data_ultima_atualizacao', 'N/A')}): {d['ultima_observacao']}"
                    partes.append(linha)
            
            if partes:
                contexto_extra = "\n".join(partes)
        
        prompt = f"""Analise os dados abaixo de uma família em vulnerabilidade social e gere um resumo em formato Markdown.

Dados cadastrais da família:
{json_data}
{contexto_extra}

INSTRUÇÕES OBRIGATÓRIAS:
- Máximo 5-6 frases curtas e diretas
- Use **negrito** para destacar os problemas mais críticos
- Use *itálico* para condições secundárias
- Foque nos desafios mais graves e nas demandas em andamento
- RESUMA as notas e observações com suas próprias palavras — NÃO copie o texto original literalmente
- Extraia apenas a essência: qual o problema, qual a ação em curso, e se há próxima data prevista
- Se houve visita domiciliar recente, mencione a data
- Mencione as demandas ativas com seu status atual e uma síntese curta da observação
- Linguagem técnica e objetiva
- NÃO inclua dados pessoais (nomes de pessoas, CPF, endereço, telefone)

EXEMPLO DE RESUMO BOM:
Família de 5 pessoas enfrentando **desemprego** e **demandas urgentes**. *Necessidades médicas* agravam a situação. Última visita domiciliar em 21/02/2026: situação crítica. Demandas ativas: **Reparação do telhado** (Em andamento - resolver humidade; próximo update em 26/02).

Seja informativo mas conciso - máximo 600 caracteres:
"""
        return prompt
    
    def gerar_resumo(self, cadastro_data: Dict[str, Any], familia_id: Optional[int] = None) -> str:
        """Gera resumo inteligente da situação familiar"""
        if not cadastro_data:
            return "Dados da família não disponíveis para análise."
        
        # Remove PII dos dados
        clean_data = self._remove_pii(cadastro_data)
        
        if not clean_data:
            return "Dados da família não disponíveis para análise."
        
        # Busca contexto adicional (atendimentos e demandas)
        additional_context = self._fetch_additional_context(familia_id)
        
        # Verifica cache (incluindo contexto adicional na chave)
        cache_input = {'cadastro': clean_data, 'contexto': additional_context,
                       'model': current_app.config['OPENAI_MODEL']}
        cache_key = self._get_cache_key(cache_input)
        if cache_key in self.cache:
            logger.info("Resumo obtido do cache")
            return self.cache[cache_key]
        
        client = self._get_client()
        
        if not client:
            logger.warning("Cliente OpenAI não disponível, usando resumo padrão")
            resumo = self._get_fallback_summary(cadastro_data, additional_context)
            return resumo
        
        try:
            # Cria o prompt
            prompt = self._create_prompt(clean_data, additional_context)
            
            # Faz a chamada para o OpenAI
            response = client.chat.completions.create(
                model=current_app.config['OPENAI_MODEL'],
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise social que gera resumos informativos em Markdown. Seja direto, objetivo e use formatação Markdown para destacar problemas críticos. RESUMA as observações dos atendimentos com suas próprias palavras — nunca copie o texto original. Extraia a essência: problema, ação em curso, próxima data. Máximo 600 caracteres."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=2000,
                reasoning_effort="low",
                store=False,
            )
            
            resumo = (response.choices[0].message.content or '').strip()
            if not resumo:
                raise ValueError('A OpenAI retornou um resumo vazio')
            
            # Remover code fences (```markdown ... ```) que a IA pode incluir
            import re
            resumo = re.sub(r'^```\w*\s*', '', resumo)
            resumo = re.sub(r'\s*```$', '', resumo)
            resumo = resumo.strip()
            
            # Registrar o uso de tokens
            OpenAIUsageTracker.track_usage(
                endpoint="chat/completions",
                model=current_app.config['OPENAI_MODEL'],
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                request_type="resumo_familia",
                success=True
            )
            
            # Log da operação (sem dados sensíveis)
            logger.info(f"Resumo gerado com sucesso via OpenAI. Tamanho: {len(resumo)} caracteres")
            
            # Salva no cache
            self.cache[cache_key] = resumo
            if familia_id:
                salvar_resumo_no_banco(familia_id, resumo)
            
            return resumo
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo com OpenAI: {e}")
            
            # Registrar erro de uso
            OpenAIUsageTracker.track_usage(
                endpoint="chat/completions",
                model=current_app.config['OPENAI_MODEL'],
                prompt_tokens=0,
                completion_tokens=0,
                request_type="resumo_familia",
                success=False,
                error_message=str(e)
            )
            
            resumo = self._get_fallback_summary(cadastro_data, additional_context)
            return resumo
    
    def _get_fallback_summary(self, cadastro_data: Dict[str, Any], additional_context: Optional[Dict[str, Any]] = None) -> str:
        """Gera resumo básico em Markdown quando OpenAI não está disponível"""
        if not cadastro_data:
            return "Informações da família não disponíveis."
        
        summary_parts = []
        critical_issues = []
        secondary_issues = []
        extra_parts = []
        
        # Composição familiar
        try:
            total_residentes = int(cadastro_data.get('total_residentes') or 0)
        except (TypeError, ValueError):
            total_residentes = 0
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
        
        # Informações de atendimentos e demandas (contexto adicional)
        if additional_context:
            # Última visita domiciliar
            visita = additional_context.get('ultima_visita_domiciliar')
            if visita:
                extra_parts.append(f"Última visita domiciliar em **{visita.get('data', 'N/A')}**")
                if visita.get('notas'):
                    extra_parts.append(f"Obs: *{visita['notas'].strip()}*")
            
            # Notas do último atendimento
            atendimentos = additional_context.get('ultimos_atendimentos', [])
            if atendimentos:
                ultimo = atendimentos[0]
                if ultimo.get('percepcao_necessidade'):
                    extra_parts.append(f"Necessidade percebida: **{ultimo['percepcao_necessidade']}**")
                if ultimo.get('motivo_duracao'):
                    extra_parts.append(f"Motivo: *{ultimo['motivo_duracao']}*")
            
            # Demandas ativas
            demandas_ativas = additional_context.get('demandas_ativas', [])
            if demandas_ativas:
                demanda_strs = []
                for d in demandas_ativas[:3]:  # Máximo 3 demandas
                    s = f"**{d.get('tipo', 'N/A')}** ({d.get('ultimo_status', d.get('status', 'N/A'))})"
                    demanda_strs.append(s)
                extra_parts.append(f"Demandas ativas: {'; '.join(demanda_strs)}")
        
        # Constrói o resumo em Markdown
        if summary_parts and critical_issues:
            base = f"{' '.join(summary_parts)} enfrentando {' e '.join(critical_issues[:2])}"
            
            if secondary_issues:
                base += f". {secondary_issues[0]} agrava a situação"
            
            base += "."
        elif summary_parts:
            base = f"{' '.join(summary_parts)} em acompanhamento social."
        else:
            base = "Família em acompanhamento social."
        
        if extra_parts:
            base += " " + ". ".join(extra_parts) + "."
        
        return base

# Instância global do serviço - será inicializada sob demanda
def get_resumo_service():
    """Obtém a instância do serviço de resumo, criando se necessário"""
    if 'resumo_service' not in current_app.extensions:
        current_app.extensions['resumo_service'] = ResumoFamiliaService()
    return current_app.extensions['resumo_service']

def buscar_resumo_recente(familia_id: int, horas: int = 12) -> Optional[str]:
    """Busca resumo existente para a família nas últimas X horas"""
    try:
        limite_tempo = datetime.now(timezone.utc) - timedelta(hours=horas)

        # Resumos locais/legados não devem impedir a primeira chamada à OpenAI.
        uso_openai = db.session.query(OpenAIUsage.id).filter(
            OpenAIUsage.familia_id == familia_id,
            OpenAIUsage.model == current_app.config['OPENAI_MODEL'],
            OpenAIUsage.endpoint == 'chat/completions',
            OpenAIUsage.success.is_(True),
            OpenAIUsage.timestamp >= limite_tempo,
            OpenAIUsage.timestamp <= ResumoFamiliaIA.data_hora_geracao,
        ).exists()
        
        resumo_recente = ResumoFamiliaIA.query.filter(
            ResumoFamiliaIA.familia_id == familia_id,
            ResumoFamiliaIA.data_hora_geracao >= limite_tempo
        ).filter(
            uso_openai
        ).order_by(ResumoFamiliaIA.data_hora_geracao.desc()).first()
        
        if resumo_recente:
            geracao = resumo_recente.data_hora_geracao
            if geracao.tzinfo is None:
                geracao = geracao.replace(tzinfo=timezone.utc)
            tempo_decorrido = datetime.now(timezone.utc) - geracao
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
        resumo = service.gerar_resumo(cadastro_data, familia_id=familia_id)
        
        return resumo
    except Exception as e:
        logger.error(f"Erro ao gerar resumo da família: {e}")
        return "Erro ao gerar resumo da família."
