# 🔐 Gerenciamento de Variáveis de Ambiente

Guia completo para configurar e gerenciar variáveis de ambiente no FinMec usando `python-dotenv`.

---

## 📋 O que é python-dotenv?

`python-dotenv` é uma biblioteca Python que carrega variáveis de ambiente de um arquivo `.env` para `os.environ`, facilitando o gerenciamento de configurações sensíveis.

### Vantagens:
- ✅ **Segurança**: Credenciais não ficam no código
- ✅ **Facilidade**: Um único arquivo `.env` para todas as configs
- ✅ **Portabilidade**: Fácil de replicar em diferentes ambientes
- ✅ **Git-safe**: `.env` não é commitado (está no `.gitignore`)

---

## 🚀 Como Usar

### 1. Criar arquivo .env

```bash
# Copiar template
cp .env.example .env

# Editar com suas credenciais
nano .env  # Linux/Mac
notepad .env  # Windows
```

### 2. Validar Configurações

```bash
# Validar .env antes de usar
python validate_env.py
```

**Output esperado:**
```
====================================================================
🔍 VALIDANDO ARQUIVO .env
====================================================================

✅ Arquivo .env encontrado: /caminho/para/.env

🔑 VARIÁVEIS OBRIGATÓRIAS:

  ✅ DATABASE_URL: postgresql://postgres:***@vps.gcdutra.cloud:5432/hom
  ✅ OPENAI_API_KEY: sk-proj-BX...
  ✅ GEMINI_API_KEY: AIzaSyAxfT...
  ✅ UAZAPI_BASE_URL: https://finmec.uazapi.com
  ✅ UAZAPI_TOKEN: 3a27c82f-7...
  ✅ SECRET_KEY: your-super...

⚙️  VARIÁVEIS OPCIONAIS:

  ✅ APP_NAME: FinMec
  ✅ APP_VERSION: 1.0.0
  ✅ DEBUG: True
  ...

====================================================================
✅ VALIDAÇÃO COMPLETA - Todas variáveis obrigatórias OK!
====================================================================
```

### 3. Rodar Aplicação

```bash
# python-dotenv carrega automaticamente
python run.py
```

**Output esperado:**
```
✅ Variáveis de ambiente carregadas de: /caminho/para/.env

====================================================================
🚀 Iniciando FinMec v1.0.0
====================================================================
🌐 Host: 0.0.0.0:8000
🔧 Debug: True
📚 Docs: http://0.0.0.0:8000/docs
====================================================================
```

---

## 📝 Estrutura do .env

### Template Completo:

```env
# ===================================
# DATABASE CONFIGURATION
# ===================================
DATABASE_URL=postgresql://user:password@host:port/database

# ===================================
# AI API KEYS
# ===================================
OPENAI_API_KEY=sk-proj-your-key-here
GEMINI_API_KEY=your-gemini-key-here

# ===================================
# UAZAPI WHATSAPP INTEGRATION
# ===================================
UAZAPI_BASE_URL=https://finmec.uazapi.com
UAZAPI_TOKEN=your-token-here

# ===================================
# APPLICATION SETTINGS
# ===================================
APP_NAME=FinMec
APP_VERSION=1.0.0
DEBUG=False  # True para desenvolvimento, False para produção
HOST=0.0.0.0
PORT=8000

# ===================================
# SECURITY
# ===================================
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ===================================
# N8N WEBHOOKS (OPTIONAL)
# ===================================
N8N_WEBHOOK_BASE_URL=https://n8n-webhook.gcdutra.cloud
```

---

## 🔒 Variáveis Obrigatórias

### 1. DATABASE_URL
**Formato:** `postgresql://user:password@host:port/database`

**Exemplo:**
```env
DATABASE_URL=postgresql://postgres:senha123@vps.gcdutra.cloud:5432/hom
```

**Validação:**
- ✅ Deve começar com `postgresql://`
- ✅ Incluir credenciais válidas
- ✅ Porta padrão: 5432

### 2. OPENAI_API_KEY
**Formato:** `sk-proj-...` ou `sk-...`

**Onde obter:**
- https://platform.openai.com/api-keys

**Validação:**
- ✅ Deve começar com `sk-`
- ✅ Mínimo 40 caracteres

### 3. GEMINI_API_KEY
**Formato:** `AIzaSy...`

**Onde obter:**
- https://makersuite.google.com/app/apikey

**Validação:**
- ✅ Deve começar com `AIzaSy`
- ✅ 39 caracteres

### 4. UAZAPI_BASE_URL
**Formato:** `https://domain.uazapi.com`

**Exemplo:**
```env
UAZAPI_BASE_URL=https://finmec.uazapi.com
```

### 5. UAZAPI_TOKEN
**Formato:** UUID

**Exemplo:**
```env
UAZAPI_TOKEN=3a27c82f-7d14-4656-b616-89a4be7e1ce4
```

**Onde obter:**
- Painel da Uazapi → API Tokens

### 6. SECRET_KEY
**Formato:** String aleatória (mínimo 32 caracteres)

**Gerar:**
```bash
# Gerar chave segura
openssl rand -hex 32

# Ou em Python
python -c "import secrets; print(secrets.token_hex(32))"
```

**IMPORTANTE:**
- 🔴 **NUNCA** use a chave de exemplo em produção
- 🔴 **NUNCA** commite a SECRET_KEY no Git
- ✅ Gere uma única chave por ambiente
- ✅ Mínimo 32 caracteres (recomendado 64)

---

## ⚙️ Variáveis Opcionais

### APP_NAME
**Padrão:** `FinMec`
```env
APP_NAME=FinMec
```

### APP_VERSION
**Padrão:** `1.0.0`
```env
APP_VERSION=1.0.0
```

### DEBUG
**Padrão:** `True`
**Valores:** `True`, `False`, `1`, `0`, `yes`, `no`

```env
DEBUG=False  # Produção
DEBUG=True   # Desenvolvimento
```

**IMPORTANTE:**
- ⚠️ `DEBUG=True` expõe informações sensíveis
- ✅ Sempre use `DEBUG=False` em produção

### HOST
**Padrão:** `0.0.0.0`
```env
HOST=0.0.0.0  # Aceita conexões de qualquer IP
HOST=127.0.0.1  # Apenas localhost
```

### PORT
**Padrão:** `8000`
```env
PORT=8000
```

### ALGORITHM
**Padrão:** `HS256`
```env
ALGORITHM=HS256
```

### ACCESS_TOKEN_EXPIRE_MINUTES
**Padrão:** `30`
```env
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🔍 Como python-dotenv Funciona

### 1. Carregamento Automático

O arquivo `app/core/config.py` carrega automaticamente:

```python
from dotenv import load_dotenv
from pathlib import Path

# Localizar .env na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = BASE_DIR / ".env"

# Carregar variáveis
load_dotenv(dotenv_path=dotenv_path, override=True)
```

### 2. Validação com Pydantic

Após carregar, Pydantic valida os tipos:

```python
class Settings(BaseSettings):
    DATABASE_URL: str  # Obrigatório, tipo string
    DEBUG: bool = True  # Opcional, converte para bool
    PORT: int = 8000  # Opcional, converte para int
```

### 3. Acesso Global

Configurações disponíveis em toda aplicação:

```python
from app.core.config import settings

print(settings.DATABASE_URL)
print(settings.DEBUG)
```

---

## 🐳 Docker e Variáveis de Ambiente

### Opção 1: Usar .env com Docker Compose

`docker-compose.yml` já está configurado:

```yaml
services:
  finmec:
    env_file: .env  # ← Carrega automaticamente
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      ...
```

**Usar:**
```bash
docker compose up -d
```

### Opção 2: Passar Variáveis Manualmente

```bash
docker run -e DATABASE_URL=postgresql://... \
           -e OPENAI_API_KEY=sk-... \
           finmec:latest
```

### Opção 3: Variáveis de Ambiente do Sistema

```bash
# Linux/Mac - Exportar para sessão
export DATABASE_URL="postgresql://..."
export OPENAI_API_KEY="sk-..."

# Windows PowerShell
$env:DATABASE_URL="postgresql://..."
$env:OPENAI_API_KEY="sk-..."

# Rodar aplicação
python run.py
```

---

## 🛡️ Segurança

### ✅ Boas Práticas:

1. **NUNCA commite .env no Git**
   ```bash
   # .gitignore já contém:
   .env
   .env.local
   .env.*.local
   ```

2. **Use .env.example como template**
   ```bash
   # Commite .env.example (sem credenciais reais)
   git add .env.example
   git commit -m "Add environment template"
   ```

3. **Gere SECRET_KEY únicas**
   ```bash
   # Uma chave por ambiente
   openssl rand -hex 32  # Desenvolvimento
   openssl rand -hex 32  # Staging
   openssl rand -hex 32  # Produção
   ```

4. **Rotacione credenciais periodicamente**
   - API Keys: A cada 3-6 meses
   - SECRET_KEY: A cada ano ou após vazamento
   - Database passwords: A cada ano

5. **Use variáveis específicas por ambiente**
   ```
   .env              # Desenvolvimento
   .env.staging      # Staging
   .env.production   # Produção
   ```

### ❌ Evitar:

- ❌ Credenciais hardcoded no código
- ❌ Credenciais em logs
- ❌ Compartilhar .env por email/chat
- ❌ Usar mesma SECRET_KEY em todos ambientes
- ❌ Commitar .env no Git

---

## 🔧 Troubleshooting

### Problema: "Arquivo .env não encontrado"

**Solução:**
```bash
# Criar .env a partir do template
cp .env.example .env
nano .env
```

### Problema: "ValidationError: field required"

**Solução:**
```bash
# Validar quais variáveis estão faltando
python validate_env.py

# Adicionar variáveis faltantes no .env
nano .env
```

### Problema: "Variáveis não são carregadas"

**Solução 1:** Verificar localização do .env
```bash
# .env deve estar na RAIZ do projeto
ls -la .env
```

**Solução 2:** Forçar reload
```python
from dotenv import load_dotenv
load_dotenv(override=True)  # ← Sobrescreve variáveis existentes
```

### Problema: "Docker não lê .env"

**Solução:**
```bash
# Verificar docker-compose.yml
grep -A5 "env_file" docker-compose.yml

# Deve ter:
# env_file: .env
```

---

## 📚 Comandos Úteis

```bash
# Validar .env
python validate_env.py
make validate-env

# Ver variáveis carregadas
python -c "from app.core.config import settings; print(settings)"

# Gerar SECRET_KEY
openssl rand -hex 32

# Listar variáveis no .env (Linux/Mac)
cat .env | grep -v "^#" | grep -v "^$"

# Backup do .env
cp .env .env.backup.$(date +%Y%m%d)
```

---

## 🎓 Exemplos de Uso

### Acessar configurações no código:

```python
from app.core.config import settings

# Database
print(settings.DATABASE_URL)

# API Keys
print(settings.OPENAI_API_KEY)

# App settings
print(settings.APP_NAME)
print(settings.DEBUG)
print(settings.PORT)

# Security
print(settings.SECRET_KEY)
```

### Usar em testes:

```python
import os
from dotenv import load_dotenv

def test_config():
    # Carregar .env.test
    load_dotenv(".env.test")

    # Testar configurações
    assert os.getenv("DATABASE_URL") is not None
```

### Múltiplos ambientes:

```bash
# Desenvolvimento
python run.py --env .env

# Staging
python run.py --env .env.staging

# Produção
python run.py --env .env.production
```

---

## 📖 Referências

- **python-dotenv**: https://github.com/theskumar/python-dotenv
- **Pydantic Settings**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **12 Factor App**: https://12factor.net/config

---

**✅ Variáveis de ambiente configuradas com segurança usando python-dotenv!**
