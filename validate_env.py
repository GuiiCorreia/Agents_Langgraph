#!/usr/bin/env python
"""
Script para validar variáveis de ambiente do .env
Execute: python validate_env.py
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Carregar .env
dotenv_path = Path(".env")

print("=" * 60)
print("🔍 VALIDANDO ARQUIVO .env")
print("=" * 60)
print()

# Verificar se .env existe
if not dotenv_path.exists():
    print("❌ ERRO: Arquivo .env não encontrado!")
    print()
    print("📝 Solução:")
    print("   1. Copie o arquivo .env.example para .env")
    print("   2. Edite o .env com suas credenciais")
    print()
    print("   cp .env.example .env")
    print("   nano .env")
    print()
    sys.exit(1)

print(f"✅ Arquivo .env encontrado: {dotenv_path.absolute()}")
print()

# Carregar variáveis
load_dotenv(dotenv_path=dotenv_path)

# Variáveis obrigatórias
REQUIRED_VARS = {
    "DATABASE_URL": "URL de conexão com PostgreSQL",
    "OPENAI_API_KEY": "API Key da OpenAI",
    "GEMINI_API_KEY": "API Key do Google Gemini",
    "UAZAPI_BASE_URL": "URL base da Uazapi",
    "UAZAPI_TOKEN": "Token da Uazapi",
    "SECRET_KEY": "Chave secreta da aplicação",
}

# Variáveis opcionais
OPTIONAL_VARS = {
    "APP_NAME": "Nome da aplicação",
    "APP_VERSION": "Versão da aplicação",
    "DEBUG": "Modo debug (True/False)",
    "HOST": "Host do servidor",
    "PORT": "Porta do servidor",
    "ALGORITHM": "Algoritmo de criptografia",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "Tempo de expiração do token",
    "N8N_WEBHOOK_BASE_URL": "URL do webhook N8n (opcional)",
}

# Validar variáveis obrigatórias
print("🔑 VARIÁVEIS OBRIGATÓRIAS:")
print()

all_required_ok = True
for var_name, description in REQUIRED_VARS.items():
    value = os.getenv(var_name)
    if value:
        # Mascarar valores sensíveis
        if "KEY" in var_name or "TOKEN" in var_name or "SECRET" in var_name or "PASSWORD" in var_name:
            masked_value = value[:10] + "..." if len(value) > 10 else "***"
            print(f"  ✅ {var_name}: {masked_value}")
        elif "URL" in var_name:
            # Mostrar URL mas mascarar senha
            if "@" in value:
                parts = value.split("@")
                if ":" in parts[0]:
                    user_pass = parts[0].split(":")
                    masked_value = f"{user_pass[0]}:***@{parts[1]}"
                else:
                    masked_value = value
            else:
                masked_value = value
            print(f"  ✅ {var_name}: {masked_value}")
        else:
            print(f"  ✅ {var_name}: {value}")
    else:
        print(f"  ❌ {var_name}: NÃO CONFIGURADO")
        print(f"     → {description}")
        all_required_ok = False

print()

# Validar variáveis opcionais
print("⚙️  VARIÁVEIS OPCIONAIS:")
print()

for var_name, description in OPTIONAL_VARS.items():
    value = os.getenv(var_name)
    if value:
        print(f"  ✅ {var_name}: {value}")
    else:
        print(f"  ℹ️  {var_name}: Usando valor padrão")

print()

# Validações específicas
print("🔬 VALIDAÇÕES ADICIONAIS:")
print()

# Validar DATABASE_URL
db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgresql://"):
        print("  ✅ DATABASE_URL tem formato correto (postgresql://)")
    else:
        print("  ⚠️  DATABASE_URL não começa com 'postgresql://'")
        print("     Formato esperado: postgresql://user:password@host:port/database")

# Validar OpenAI Key
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    if openai_key.startswith("sk-"):
        print("  ✅ OPENAI_API_KEY tem formato correto (sk-...)")
    else:
        print("  ⚠️  OPENAI_API_KEY não começa com 'sk-'")

# Validar SECRET_KEY
secret_key = os.getenv("SECRET_KEY")
if secret_key:
    if len(secret_key) >= 32:
        print("  ✅ SECRET_KEY tem tamanho adequado (>= 32 caracteres)")
    else:
        print("  ⚠️  SECRET_KEY muito curta (recomendado >= 32 caracteres)")
        print("     Gere uma nova com: openssl rand -hex 32")

# Validar DEBUG em produção
debug = os.getenv("DEBUG", "True")
if debug.lower() in ["false", "0", "no"]:
    print("  ✅ DEBUG=False (modo produção)")
else:
    print("  ⚠️  DEBUG=True (modo desenvolvimento)")
    print("     ATENÇÃO: Em produção, configure DEBUG=False")

print()

# Resumo final
print("=" * 60)
if all_required_ok:
    print("✅ VALIDAÇÃO COMPLETA - Todas variáveis obrigatórias OK!")
    print()
    print("🚀 Próximo passo:")
    print("   python init_database.py  # Inicializar banco de dados")
    print("   python run.py            # Rodar aplicação")
    print()
    sys.exit(0)
else:
    print("❌ VALIDAÇÃO FALHOU - Variáveis obrigatórias faltando!")
    print()
    print("📝 Corrija o arquivo .env e execute novamente:")
    print("   python validate_env.py")
    print()
    sys.exit(1)
