-- Optional SQLite seed. manage.py also creates these lookup values.
INSERT OR IGNORE INTO demanda_tipo (demanda_tipo_id, demanda_tipo_nome, data_hora_log_utc)
VALUES 
(1, 'Cursos profissionalizantes', CURRENT_TIMESTAMP),
(2, 'Equipamentos para casa', CURRENT_TIMESTAMP),
(3, 'Serviços domésticos', CURRENT_TIMESTAMP),
(4, 'Medicamentos', CURRENT_TIMESTAMP),
(5, 'Vaga em escola', CURRENT_TIMESTAMP),
(6, 'Necessidades jurídicas', CURRENT_TIMESTAMP),
(7, 'Outros', CURRENT_TIMESTAMP);
