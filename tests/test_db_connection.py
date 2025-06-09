from app import create_app, db
from sqlalchemy import text 

def test_database_connection():
    app = create_app()

    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))  # <-- correção aqui
            assert True
        except Exception as e:
            assert False, f"Erro de conexão com o banco de dados: {e}"
