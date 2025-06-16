SET IDENTITY_INSERT [dbo].[demanda_tipo] ON;

INSERT INTO [dbo].[demanda_tipo] ([demanda_tipo_id], [demanda_tipo_nome], [data_hora_log_utc])
VALUES 
(1, 'Cursos profissionalizantes', SYSDATETIMEOFFSET()),
(2, 'Equipamentos para casa', SYSDATETIMEOFFSET()),
(3, 'Serviços domésticos', SYSDATETIMEOFFSET()),
(4, 'Medicamentos', SYSDATETIMEOFFSET()),
(5, 'Vaga em escola', SYSDATETIMEOFFSET()),
(6, 'Necessidades jurídicas', SYSDATETIMEOFFSET()),
(7, 'Outros', SYSDATETIMEOFFSET());

SET IDENTITY_INSERT [dbo].[demanda_tipo] OFF;