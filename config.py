import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    INSTANCE_DIR = Path(__file__).resolve().parent / "instance"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{(INSTANCE_DIR / 'formiguinhas.db').as_posix()}"
    )
    SQLALCHEMY_PRE_CADASTRO_URI = os.getenv(
        "PRE_CADASTRO_DATABASE_URL",
        f"sqlite:///{(INSTANCE_DIR / 'precadastro.db').as_posix()}",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = os.getenv("FLASK_ENV", "production")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flask_session")

    # Configurações de localização
    LANGUAGES = ['pt-BR', 'pt']
    BABEL_DEFAULT_LOCALE = 'pt_BR'
    BABEL_DEFAULT_TIMEZONE = 'America/Sao_Paulo'

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True
    }
    
    # API direta da OpenAI. O endpoint não depende de configuração do Azure.
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "").strip() or "gpt-5.6-luna"
    OPENAI_BASE_URL = "https://api.openai.com/v1"

