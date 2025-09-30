-- Stored Procedure para consulta de pré-cadastro no banco de dados dbformiguinhasprecbr
-- Retorna todas as colunas de todas as tabelas relacionadas
-- SP já criada no banco de dados dbformiguinhasprecbr

CREATE PROCEDURE [dbo].[usp_consultar_precadastro]
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        SELECT 
            f.familia_precadastro_id,
            
            -- Tabela familias
            f.nome_responsavel,
            f.data_nascimento,
            f.genero,
            f.genero_autodeclarado,
            f.estado_civil,
            f.rg,
            f.cpf,
            f.autoriza_uso_imagem,
            f.status_cadastro,
            f.data_hora_log_utc AS data_log_familia,

            -- Tabela enderecos
            e.cep,
            e.preenchimento_manual,
            e.logradouro,
            e.numero,
            e.complemento,
            e.bairro,
            e.cidade,
            e.estado,
            e.ponto_referencia,
            e.data_hora_log_utc AS data_log_endereco,

            -- Tabela composicao_familiar
            cf.total_residentes,
            cf.quantidade_bebes,
            cf.quantidade_criancas,
            cf.quantidade_adolescentes,
            cf.quantidade_adultos,
            cf.quantidade_idosos,
            cf.tem_menores_na_escola,
            cf.motivo_ausencia_escola,
            cf.data_hora_log_utc AS data_log_composicao,

            -- Tabela contatos
            c.telefone_principal,
            c.telefone_principal_whatsapp,
            c.telefone_principal_nome_contato,
            c.telefone_alternativo,
            c.telefone_alternativo_whatsapp,
            c.telefone_alternativo_nome_contato,
            c.email_responsavel,
            c.data_hora_log_utc AS data_log_contato

        FROM [dbo].[familias] f
        LEFT JOIN [dbo].[enderecos] e 
            ON f.familia_precadastro_id = e.familia_precadastro_id
        LEFT JOIN [dbo].[composicao_familiar] cf 
            ON f.familia_precadastro_id = cf.familia_precadastro_id
        LEFT JOIN [dbo].[contatos] c 
            ON f.familia_precadastro_id = c.familia_precadastro_id
        ORDER BY f.familia_precadastro_id;
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();

        SELECT 
            'ERROR' as status,
            @ErrorMessage as message,
            @ErrorSeverity as severity,
            @ErrorState as state;

        RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH
END
GO
