"""Use the real SDK with a simulated HTTP endpoint; no credentials or credits needed."""
import json

import httpx
from openai import OpenAI
import pytest
from flask import session

from app import create_app, db
from app.models.familia import Familia
from app.models.resumo_familia_ia import ResumoFamiliaIA
from app.models.openai_usage import OpenAIUsage
from app.utils import resumo_familia as summaries
from app.utils.openai_usage_tracker import OpenAIUsageTracker


@pytest.fixture
def context(tmp_path):
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'SESSION_FILE_DIR': str(tmp_path / 'sessions'),
        'OPENAI_API_KEY': 'sk-test-only',
        'OPENAI_MODEL': 'gpt-5.6-luna',
        'OPENAI_BASE_URL': 'https://api.openai.com/v1',
    })
    with app.test_request_context():
        db.create_all()
        family = Familia(nome_responsavel='Família fictícia')
        db.session.add(family)
        db.session.commit()
        session['familia_id'] = family.familia_id
        yield app, family.familia_id
        service = app.extensions.get('resumo_service')
        if service and service.client:
            service.client.close()
        db.session.remove()
        db.engine.dispose()


def mock_openai(monkeypatch, responses=None):
    requests = []
    responses = list(responses or [(200, '**Resumo de teste**')])

    def handle(request):
        requests.append(request)
        status, content = responses.pop(0)
        if status != 200:
            return httpx.Response(status, json={'error': {'message': 'Invalid test key',
                                                        'type': 'invalid_request_error',
                                                        'code': 'invalid_api_key'}})
        return httpx.Response(200, json={
            'id': 'chatcmpl-test', 'object': 'chat.completion', 'created': 1,
            'model': 'gpt-5.6-luna',
            'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': content},
                         'finish_reason': 'stop'}],
            'usage': {'prompt_tokens': 100, 'completion_tokens': 50, 'total_tokens': 150},
        })

    def factory(**kwargs):
        assert kwargs['api_key'] == 'sk-test-only'
        assert kwargs['base_url'] == 'https://api.openai.com/v1'
        return OpenAI(**kwargs, http_client=httpx.Client(transport=httpx.MockTransport(handle)))

    monkeypatch.setattr(summaries, 'OpenAI', factory)
    return requests


def test_direct_openai_request_usage_persistence_and_cache(context, monkeypatch):
    app, family_id = context
    requests = mock_openai(monkeypatch)
    data = {'nome_responsavel': 'Pessoa fictícia', 'cpf': '525.067.333-37', 'total_residentes': 4}
    assert summaries.gerar_resumo_familia(data) == '**Resumo de teste**'
    assert summaries.gerar_resumo_familia(data) == '**Resumo de teste**'
    assert len(requests) == 1
    request = requests[0]
    assert request.method == 'POST'
    assert str(request.url) == 'https://api.openai.com/v1/chat/completions'
    assert request.headers['authorization'] == 'Bearer sk-test-only'
    assert 'api-key' not in request.headers
    payload = json.loads(request.content)
    assert payload['model'] == app.config['OPENAI_MODEL']
    assert payload['max_completion_tokens'] == 2000
    assert payload['reasoning_effort'] == 'low'
    assert payload['store'] is False
    assert 'temperature' not in payload
    assert '525.067.333-37' not in request.content.decode()
    usage = OpenAIUsage.query.one()
    assert usage.success and usage.total_tokens == 150 and usage.familia_id == family_id
    assert usage.model == 'gpt-5.6-luna'
    assert ResumoFamiliaIA.query.one().resumo_texto == '**Resumo de teste**'
    assert len(OpenAIUsageTracker.get_daily_usage()) == 1


def test_missing_key_does_not_cache_fallback_or_prevent_later_request(context, monkeypatch):
    app, _ = context
    requests = mock_openai(monkeypatch)
    app.config['OPENAI_API_KEY'] = ''
    assert summaries.gerar_resumo_familia({'total_residentes': 4})
    assert requests == []
    assert ResumoFamiliaIA.query.count() == 0
    assert summaries.get_resumo_service().cache == {}
    app.config['OPENAI_API_KEY'] = 'sk-test-only'
    assert summaries.gerar_resumo_familia({'total_residentes': 4}) == '**Resumo de teste**'
    assert len(requests) == 1


def test_api_failure_falls_back_then_retries(context, monkeypatch):
    requests = mock_openai(monkeypatch, [(401, ''), (200, 'Resumo recuperado')])
    assert summaries.gerar_resumo_familia({'total_residentes': 4})
    assert ResumoFamiliaIA.query.count() == 0
    assert OpenAIUsage.query.one().success is False
    assert summaries.gerar_resumo_familia({'total_residentes': 4}) == 'Resumo recuperado'
    assert len(requests) == 2
    assert ResumoFamiliaIA.query.count() == 1


def test_legacy_local_summary_does_not_block_openai(context, monkeypatch):
    _, family_id = context
    db.session.add(ResumoFamiliaIA(familia_id=family_id, resumo_texto='Resumo local antigo'))
    db.session.commit()
    requests = mock_openai(monkeypatch)
    assert summaries.gerar_resumo_familia({'total_residentes': 4}) == '**Resumo de teste**'
    assert len(requests) == 1


def test_empty_api_content_is_not_persisted(context, monkeypatch):
    mock_openai(monkeypatch, [(200, '')])
    assert summaries.gerar_resumo_familia({'total_residentes': 4})
    assert ResumoFamiliaIA.query.count() == 0
    assert OpenAIUsage.query.one().success is False


@pytest.mark.parametrize('total', ['', None, '4'])
def test_fallback_accepts_unfilled_or_formatted_household_size(context, monkeypatch, total):
    app, _ = context
    app.config['OPENAI_API_KEY'] = ''
    mock_openai(monkeypatch)
    summary = summaries.gerar_resumo_familia({'total_residentes': total})
    assert summary and summary != 'Erro ao gerar resumo da família.'
    assert ResumoFamiliaIA.query.count() == 0
