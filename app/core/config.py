"""
Configurações da aplicação usando Pydantic Settings e python-dotenv
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
# Busca .env na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = BASE_DIR / ".env"

# Carregar .env (se existir)
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path, override=True)
    print(f"✅ Arquivo .env carregado: {dotenv_path}")
else:
    print(f"⚠️ Arquivo .env não encontrado em: {dotenv_path}")
    print("   Usando variáveis de ambiente do sistema")


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas do arquivo .env
    Usa pydantic-settings para validação e python-dotenv para carregar
    """

    # Database
    DATABASE_URL: str

    # API Keys
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str

    # Uazapi WhatsApp
    UAZAPI_BASE_URL: str
    UAZAPI_TOKEN: str

    # Application
    APP_NAME: str = "FinMec"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # N8n Webhooks
    N8N_WEBHOOK_BASE_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignorar variáveis extras do .env

    def __repr__(self) -> str:
        """Representação sem expor credenciais"""
        return f"Settings(APP_NAME={self.APP_NAME}, DEBUG={self.DEBUG}, HOST={self.HOST})"


# Instância global das configurações
settings = Settings()

# Validação básica ao carregar
if settings.DEBUG:
    print(f"🔧 Configurações carregadas:")
    print(f"   - App: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"   - Debug: {settings.DEBUG}")
    print(f"   - Host: {settings.HOST}:{settings.PORT}")
    print(f"   - Database: {'✅ Configurado' if settings.DATABASE_URL else '❌ Não configurado'}")
    print(f"   - OpenAI: {'✅ Configurado' if settings.OPENAI_API_KEY else '❌ Não configurado'}")
    print(f"   - Gemini: {'✅ Configurado' if settings.GEMINI_API_KEY else '❌ Não configurado'}")
    print(f"   - Uazapi: {'✅ Configurado' if settings.UAZAPI_TOKEN else '❌ Não configurado'}")
