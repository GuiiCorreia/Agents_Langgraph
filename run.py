"""
Script para iniciar o servidor FastAPI
Carrega automaticamente variáveis de ambiente do .env
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Garantir que .env seja carregado antes de importar qualquer coisa
dotenv_path = Path(".env")
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path, override=True)
    print(f"✅ Variáveis de ambiente carregadas de: {dotenv_path.absolute()}")
else:
    print(f"⚠️  Arquivo .env não encontrado em: {dotenv_path.absolute()}")
    print("   Criando .env a partir do .env.example...")

    example_path = Path(".env.example")
    if example_path.exists():
        import shutil
        shutil.copy(example_path, dotenv_path)
        print(f"✅ Arquivo .env criado! Configure suas credenciais:")
        print(f"   nano .env  # Linux/Mac")
        print(f"   notepad .env  # Windows")
        sys.exit(1)
    else:
        print("❌ Arquivo .env.example não encontrado!")
        sys.exit(1)

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print()
    print("=" * 60)
    print(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    print("=" * 60)
    print(f"🌐 Host: {settings.HOST}:{settings.PORT}")
    print(f"🔧 Debug: {settings.DEBUG}")
    print(f"📚 Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 60)
    print()

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
