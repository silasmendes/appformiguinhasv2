SELECT 
    f.*, 
    e.*, 
    c.*, 
    cf.*, 
    cm.*, 
    ed.*, 
    ep.*, 
    rf.*, 
    sf.*,
	demandas_json.demandas,
	atendimentos_json.atendimentos
FROM dbo.familias f
LEFT JOIN dbo.enderecos e ON f.familia_id = e.familia_id
LEFT JOIN dbo.contatos c ON f.familia_id = c.familia_id
LEFT JOIN dbo.composicao_familiar cf ON f.familia_id = cf.familia_id
LEFT JOIN dbo.condicoes_moradia cm ON f.familia_id = cm.familia_id
LEFT JOIN dbo.educacao_entrevistado ed ON f.familia_id = ed.familia_id
LEFT JOIN dbo.emprego_provedor ep ON f.familia_id = ep.familia_id
LEFT JOIN dbo.renda_familiar rf ON f.familia_id = rf.familia_id
LEFT JOIN dbo.saude_familiar sf ON f.familia_id = sf.familia_id
OUTER APPLY (
    SELECT 
        df.demanda_id,
        df.familia_id,
        df.demanda_tipo_id,
        dt.demanda_tipo_nome,
        df.status,
        df.descricao,
        df.data_identificacao,
        df.prioridade,
        de.data_atualizacao,
        de.status_atual,
        de.observacao,
        de.usuario_atendente_id
    FROM demanda_familia df
    INNER JOIN demanda_tipo dt ON df.demanda_tipo_id = dt.demanda_tipo_id
    INNER JOIN demanda_etapa de ON df.demanda_id = de.demanda_id
    WHERE df.familia_id = f.familia_id
    FOR JSON PATH
) AS demandas_json(demandas)
OUTER APPLY (
    SELECT 
        a.*
    FROM dbo.atendimentos a
    WHERE a.familia_id = f.familia_id
    FOR JSON PATH
) AS atendimentos_json(atendimentos)