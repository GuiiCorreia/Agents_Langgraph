# 🚀 Guia de Instalação - FinMec

Sistema completo de gestão financeira via WhatsApp usando FastAPI, LangGraph, OpenAI e Google Gemini.

---

## 📋 Pré-requisitos

- **Python 3.12.0** (já instalado ✅)
- **PostgreSQL** (acesso ao servidor configurado ✅)
- **Git** (opcional)

---

## 🔧 Passo 1: Instalar uv (Gerenciador de Pacotes)

**uv** é um gerenciador de pacotes Python ultra-rápido (10-100x mais rápido que pip).

### Windows:

```powershell
# Instalar uv via PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Ou via pip (mais lento)
pip install uv
```

### Linux/Mac:

```bash
# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou via pip (mais lento)
pip install uv
```

---

## 🔧 Passo 2: Preparar Ambiente

### Windows:

```bash
# Navegar até a pasta do projeto
cd "C:\Users\Guilherme\Documents\Agente Financeiro"

# Criar ambiente virtual com uv
uv venv

# Ativar ambiente virtual
.venv\Scripts\activate
```

### Linux/Mac:

```bash
# Navegar até a pasta do projeto
cd "/caminho/para/Agente Financeiro"

# Criar ambiente virtual com uv
uv venv

# Ativar ambiente virtual
source .venv/bin/activate
```

---

## 📦 Passo 3: Instalar Dependências

```bash
# Instalar dependências usando uv (MUITO mais rápido!)
uv pip install -r requirements.txt

# Ou sincronizar com pyproject.toml
uv sync
```

**Isso instalará:**
- FastAPI (API REST)
- Uvicorn (servidor ASGI)
- SQLAlchemy (ORM)
- PostgreSQL driver
- OpenAI SDK
- Google Generative AI SDK
- LangChain & LangGraph (Agente de IA)
- E muito mais...

**⚡ Vantagens do uv:**
- 10-100x mais rápido que pip
- Resolve dependências de forma mais inteligente
- Cache global para economizar espaço
- Melhor para CI/CD

---

## 🗄️ Passo 4: Configurar Variáveis de Ambiente

O arquivo `.env` já está configurado com todas as credenciais:

```env
# Database
DATABASE_URL=postgresql://postgres:253ad778d41c09bb0da7@vps.gcdutra.cloud:5432/hom

# API Keys
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaSyAxfTKmTDGHQhM6MzQWHou6m09Or-fY3Lk

# Uazapi WhatsApp
UAZAPI_BASE_URL=https://finmec.uazapi.com
UAZAPI_TOKEN=3a27c82f-7d14-4656-b616-89a4be7e1ce4

# Application
APP_NAME=FinMec
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

✅ **Já está tudo configurado!**

---

## 🗃️ Passo 5: Inicializar Banco de Dados

```bash
python init_database.py
```

**Este script irá:**
1. ✅ Criar todas as tabelas no PostgreSQL
2. ✅ Inserir categorias padrão (Alimentação, Saúde, etc.)
3. ✅ Inserir métodos de pagamento padrão (PIX, Cartão, etc.)

---

## 🚀 Passo 6: Iniciar o Servidor

```bash
python run.py
```

**Ou com uvicorn diretamente:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Servidor estará rodando em:**
- Local: http://localhost:8000
- Documentação: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📡 Passo 7: Configurar Webhooks no Uazapi

Acesse o painel da Uazapi e configure os webhooks:

### Webhook Principal (Mensagens)
- **URL**: `https://finmec-hom.gcdutra.cloud/webhook/finmec`
- **Método**: POST
- **Eventos**: Recebimento de mensagens

### Webhook de Ativação
- **URL**: `https://finmec-hom.gcdutra.cloud/webhook/ativacao`
- **Método**: POST
- **Uso**: Ativar novos usuários após pagamento

---

## 🧪 Passo 8: Testar a API

### Teste 1: Health Check

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "app": "FinMec",
  "version": "1.0.0"
}
```

### Teste 2: Listar Categorias

```bash
curl -X GET http://localhost:8000/api/categories \
  -H "apikey: SEU_API_KEY_AQUI"
```

### Teste 3: Webhook de Teste

```bash
curl http://localhost:8000/webhook/test
```

---

## 📱 Como Usar via WhatsApp

### 1. Ativar Usuário

Envie POST para `/webhook/ativacao`:

```json
{
  "telefone": "5511999999999",
  "dominio": "https://finmec-hom.gcdutra.cloud",
  "mensagem_ativacao": "Bem-vindo ao FinMec!",
  "acesso_web": {
    "usuario": "5511999999999@s.whatsapp.net",
    "senha": "senha123"
  }
}
```

### 2. Enviar Mensagem de Teste

O webhook `/webhook/finmec` receberá automaticamente mensagens do WhatsApp via Uazapi.

### Exemplos de Comandos

**Registrar Despesa:**
```
Gastei 50 reais no almoço
```

**Registrar Receita:**
```
Recebi 2000 reais de salário
```

**Ver Saldo:**
```
Qual meu saldo atual?
```

**Ver Transações Recentes:**
```
Mostre minhas últimas transações
```

**Gerar Relatório:**
```
Quero um relatório de janeiro
```

**Criar Lembrete:**
```
Me lembre de pagar a conta de luz dia 15
```

---

## 🏗️ Arquitetura do Sistema

```
WhatsApp (Uazapi)
       ↓
  Webhook /finmec
       ↓
Message Processor ← (Áudio → OpenAI Whisper)
       ↓             (Imagem → Gemini Vision)
LangGraph Agent   ← (PDF → Gemini)
       ↓
   Tools/Functions:
   ├── Inserir Transação
   ├── Listar Categorias
   ├── Buscar Saldo
   ├── Gerar Relatório
   ├── Criar Lembrete
   └── Resumo Mensal
       ↓
  PostgreSQL Database
       ↓
Resposta via WhatsApp
```

---

## 📊 Endpoints Disponíveis

### API REST

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/transactions` | POST | Criar transação |
| `/api/transactions` | GET | Listar transações |
| `/api/transactions/{id}` | GET | Buscar transação |
| `/api/transactions/{id}` | PATCH | Atualizar transação |
| `/api/transactions/{id}` | DELETE | Deletar transação |
| `/api/categories` | GET | Listar categorias |
| `/api/payment-methods` | GET | Listar métodos |
| `/api/reminders` | GET/POST | Lembretes |
| `/api/wallet/current` | GET | Carteira atual |
| `/api/dashboard/summary` | GET | Resumo dashboard |
| `/api/charts/bar` | GET | Gráfico de barras |
| `/api/charts/pizza` | GET | Gráfico de pizza |

### Webhooks

| Endpoint | Descrição |
|----------|-----------|
| `/webhook/finmec` | Recebe mensagens do WhatsApp |
| `/webhook/ativacao` | Ativa novos usuários |

---

## 🐛 Troubleshooting

### Erro: "Connection to PostgreSQL failed"

**Solução:** Verifique as credenciais no `.env` e se o servidor PostgreSQL está acessível.

```bash
# Testar conexão
psql -h vps.gcdutra.cloud -p 5432 -U postgres -d hom
```

### Erro: "Module not found"

**Solução:** Certifique-se de que o ambiente virtual está ativado e as dependências instaladas.

```bash
# Verificar ambiente
which python  # Linux/Mac
where python  # Windows

# Reinstalar dependências
pip install -r requirements.txt
```

### Erro: "Port 8000 already in use"

**Solução:** Altere a porta no `.env`:

```env
PORT=8001
```

---

## 🔐 Segurança

### Boas Práticas:

1. **NUNCA** commite o arquivo `.env` no Git
2. Use HTTPS em produção
3. Rotacione as API keys regularmente
4. Monitore logs de acesso
5. Implemente rate limiting em produção

---

## 📚 Próximos Passos

1. ✅ **Deploy em Produção:**
   - Configure servidor (AWS, DigitalOcean, etc.)
   - Use HTTPS (Let's Encrypt)
   - Configure domínio: `finmec-hom.gcdutra.cloud`

2. ✅ **Monitoramento:**
   - Configure logs (Loguru já integrado)
   - Monitore performance
   - Alertas de erro

3. ✅ **Melhorias:**
   - Adicionar mais categorias customizadas
   - Implementar gráficos visuais
   - Sistema de notificações avançado

---

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique os logs: `logs/app.log`
- Consulte a documentação: http://localhost:8000/docs
- Entre em contato com o suporte

---

## ✅ Checklist de Instalação

- [ ] Python 3.12.0 instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` configurado
- [ ] Banco de dados inicializado (`python init_database.py`)
- [ ] Servidor iniciado (`python run.py`)
- [ ] Webhook configurado na Uazapi
- [ ] Teste realizado com sucesso

---

🎉 **Parabéns! Seu sistema FinMec está pronto para uso!**
