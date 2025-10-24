# 🚀 FinMec - Sistema de Gestão Financeira via WhatsApp

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-orange)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![uv](https://img.shields.io/badge/uv-enabled-green)
![License](https://img.shields.io/badge/License-Proprietary-red)

Sistema completo de gestão financeira pessoal integrado com WhatsApp usando IA avançada (OpenAI GPT-4, Google Gemini) e LangGraph.

> ⚡ **Otimizado com uv** - Builds Docker 7x mais rápidos | Instalações 15x mais rápidas

---

## ✨ Funcionalidades

- 💬 **Chatbot via WhatsApp** - Converse naturalmente para registrar transações
- 🎙️ **Suporte a Áudio** - Envie mensagens de voz (transcrição automática)
- 📸 **Análise de Imagens** - Tire foto de notas fiscais e extraia valores automaticamente
- 📄 **Processamento de PDFs** - Analise boletos e faturas
- 📊 **Relatórios Inteligentes** - Gere relatórios por período e categoria
- 🔔 **Lembretes Automáticos** - Agende lembretes de pagamento
- 📈 **Gráficos e Dashboards** - Visualize suas finanças
- 🤖 **IA Avançada** - LangGraph Agent com múltiplas ferramentas

---

## 🏗️ Arquitetura

```
WhatsApp (Uazapi) → Webhook → Message Processor → LangGraph Agent → Tools
                                      ↓                    ↓
                              OpenAI/Gemini        PostgreSQL Database
                                      ↓
                              Response → WhatsApp
```

### Componentes Principais:

- **FastAPI**: API REST moderna e rápida
- **LangGraph**: Orquestração de agentes de IA
- **OpenAI GPT-4**: Conversação e transcrição
- **Google Gemini**: Análise de imagens e documentos
- **PostgreSQL**: Banco de dados robusto
- **Uazapi**: Integração WhatsApp
- **Docker**: Containerização e deploy

---

## 📦 Instalação Local

### Pré-requisitos:
- Python 3.12+
- PostgreSQL
- **uv** (gerenciador de pacotes ultra-rápido)
- Credenciais das APIs (OpenAI, Gemini, Uazapi)

### Passos:

```bash
# 1. Instalar uv (se ainda não tem)
# Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/Mac:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clonar repositório
git clone <repo-url>
cd "Agente Financeiro"

# 3. Criar ambiente virtual com uv
uv venv

# 4. Ativar ambiente (Windows)
.venv\Scripts\activate

# 5. Instalar dependências com uv (MUITO mais rápido!)
uv pip install -r requirements.txt
# Ou: uv sync

# 6. Configurar .env
cp .env.example .env
# Editar .env com suas credenciais

# 7. Inicializar banco de dados
python init_database.py

# 8. Rodar servidor
python run.py
```

**Acesse:** http://localhost:8000/docs

---

## 🐳 Deploy com Docker

### Método Rápido:

```bash
# 1. Configurar .env
cp .env.example .env
nano .env  # Editar credenciais

# 2. Deploy automático
chmod +x deploy.sh
./deploy.sh
```

### Método Manual:

```bash
# Build
docker compose build

# Iniciar
docker compose up -d

# Ver logs
docker compose logs -f finmec

# Inicializar banco
docker compose exec finmec python init_database.py
```

### Usando Makefile:

```bash
make install      # Instalar dependências (usa uv)
make init-db      # Inicializar banco
make run          # Rodar localmente
make docker-build # Build Docker
make deploy       # Deploy completo
make docker-logs  # Ver logs
make sync         # Sincronizar com pyproject.toml
```

📖 **Guia Completo:** Veja [DEPLOY.md](DEPLOY.md)

---

## 🌐 Configuração de Produção

### 1. Configurar DNS:
```
Tipo: A
Nome: finmec-hom
Valor: <IP_DO_SERVIDOR>
```

### 2. Configurar Nginx + SSL:
```bash
# Instalar Nginx e Certbot
sudo apt install nginx certbot python3-certbot-nginx

# Configurar (veja DEPLOY.md)
sudo nano /etc/nginx/sites-available/finmec

# Instalar SSL
sudo certbot --nginx -d finmec-hom.gcdutra.cloud
```

### 3. Configurar Webhooks na Uazapi:
- **Mensagens**: `https://finmec-hom.gcdutra.cloud/webhook/finmec`
- **Ativação**: `https://finmec-hom.gcdutra.cloud/webhook/ativacao`

---

## 📡 Endpoints da API

### Autenticação:
Todos os endpoints (exceto webhooks) requerem header:
```
apikey: seu-api-key-aqui
```

### Principais Endpoints:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | GET | Health check |
| `/api/transactions` | GET/POST | Transações |
| `/api/transactions/{id}` | GET/PATCH/DELETE | Transação específica |
| `/api/categories` | GET | Categorias |
| `/api/payment-methods` | GET | Métodos de pagamento |
| `/api/reminders` | GET/POST | Lembretes |
| `/api/wallet/current` | GET | Carteira atual |
| `/api/dashboard/summary` | GET | Resumo financeiro |
| `/api/charts/bar` | GET | Gráfico de barras |
| `/api/charts/pizza` | GET | Gráfico de pizza |
| `/webhook/finmec` | POST | Webhook WhatsApp |
| `/webhook/ativacao` | POST | Ativar usuário |

📖 **Documentação Completa:** http://localhost:8000/docs

---

## 💬 Como Usar via WhatsApp

### Registrar Despesa:
```
"Gastei 50 reais no almoço"
"Paguei 120 de luz"
"Comprei roupas por 250"
```

### Registrar Receita:
```
"Recebi 3000 de salário"
"Vendi um produto por 500"
```

### Consultar Saldo:
```
"Qual meu saldo?"
"Quanto tenho na carteira?"
```

### Ver Transações:
```
"Mostre minhas últimas transações"
"Quais foram meus gastos recentes?"
```

### Gerar Relatório:
```
"Quero relatório de janeiro"
"Mostre despesas de saúde esse mês"
```

### Criar Lembrete:
```
"Me lembre de pagar conta dia 15"
"Lembrete para pagar aluguel amanhã"
```

### Enviar Nota Fiscal:
```
[Enviar foto da nota fiscal]
→ Sistema extrai automaticamente itens e valores
```

### Enviar Áudio:
```
[Enviar áudio]
→ Sistema transcreve e processa
```

---

## 🛠️ Tecnologias Utilizadas

### Backend:
- **FastAPI** 0.109 - Framework web moderno
- **Python** 3.12 - Linguagem
- **SQLAlchemy** 2.0 - ORM
- **Pydantic** 2.5 - Validação de dados
- **Alembic** 1.13 - Migrações de banco

### IA e ML:
- **LangGraph** 0.2 - Orquestração de agentes
- **LangChain** 0.3 - Framework de IA
- **OpenAI** GPT-4o-mini - LLM principal
- **Google Gemini** 2.0-flash - Visão computacional

### Integrações:
- **Uazapi** - WhatsApp Business API
- **PostgreSQL** 16 - Banco de dados
- **Loguru** - Logging avançado

### DevOps:
- **Docker** & **Docker Compose**
- **Nginx** - Reverse proxy
- **Let's Encrypt** - SSL/TLS
- **Uvicorn** - ASGI server

---

## 📊 Estrutura do Projeto

```
📁 Agente Financeiro/
├── 📁 app/
│   ├── 📁 api/endpoints/        # 8 módulos de API REST
│   ├── 📁 core/                 # Config e segurança
│   ├── 📁 db/                   # Database setup
│   ├── 📁 models/               # 6 modelos SQLAlchemy
│   ├── 📁 schemas/              # Schemas Pydantic
│   ├── 📁 services/             # Lógica de negócio + LangGraph
│   ├── 📁 integrations/         # Uazapi, OpenAI, Gemini
│   └── main.py                  # App FastAPI
├── 📄 Dockerfile                # Imagem Docker
├── 📄 docker-compose.yml        # Orquestração
├── 📄 requirements.txt          # Dependências
├── 📄 .env.example              # Template de env
├── 📄 deploy.sh                 # Script de deploy
├── 📄 Makefile                  # Comandos úteis
├── 📄 DEPLOY.md                 # Guia de deploy
├── 📄 INSTALACAO.md             # Guia de instalação
└── 📄 README.md                 # Este arquivo
```

---

## 🔐 Segurança

### Boas Práticas Implementadas:
- ✅ API Key authentication
- ✅ Variáveis de ambiente para credenciais
- ✅ .gitignore para arquivos sensíveis
- ✅ SSL/TLS em produção
- ✅ Validação de dados com Pydantic
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Container não-root no Docker
- ✅ Health checks

### Recomendações para Produção:
- [ ] `DEBUG=False` no .env
- [ ] SECRET_KEY único e forte
- [ ] Firewall configurado (UFW)
- [ ] Rate limiting no Nginx
- [ ] Backup automático do banco
- [ ] Monitoramento de logs
- [ ] Rotação de credenciais

---

## 🧪 Testes

```bash
# Rodar testes (quando implementados)
pytest tests/

# Com coverage
pytest --cov=app tests/
```

---

## 📈 Performance

### Otimizações:
- Async/Await em toda a aplicação
- Connection pooling no PostgreSQL
- Cache de configurações
- Background tasks para webhooks
- Workers configuráveis no Uvicorn

### Escalabilidade:
```yaml
# Aumentar workers
CMD ["uvicorn", "app.main:app", "--workers", "4"]

# Ou usar múltiplas réplicas
docker compose up -d --scale finmec=3
```

---

## 🐛 Troubleshooting

### Container não inicia:
```bash
docker compose logs finmec
```

### Erro de conexão com banco:
```bash
# Testar conexão
docker compose exec finmec python -c "from app.db.database import engine; print(engine.connect())"
```

### Webhook não recebe mensagens:
1. Verificar URL configurada na Uazapi
2. Verificar logs: `docker compose logs -f finmec`
3. Testar endpoint: `curl https://finmec-hom.gcdutra.cloud/webhook/test`

---

## 📞 Suporte

- 📖 Documentação: http://localhost:8000/docs
- 📋 Logs: `docker compose logs -f finmec`
- 🔍 Health Check: http://localhost:8000/health

---

## 🗺️ Roadmap

### Próximas Features:
- [ ] Múltiplas carteiras por usuário
- [ ] Categorias customizadas
- [ ] Exportação de relatórios em PDF
- [ ] Integração com bancos (Open Finance)
- [ ] Análise preditiva com ML
- [ ] Notificações push
- [ ] Dashboard web
- [ ] API mobile

---

## 📄 Licença

Proprietary - Uso interno apenas

---

## 🎉 Agradecimentos

Desenvolvido com ❤️ usando tecnologias de ponta:
- FastAPI
- LangGraph
- OpenAI
- Google Gemini
- Uazapi

---

## 📞 Contato

Para dúvidas ou suporte, entre em contato com a equipe de desenvolvimento.

---

**🚀 FinMec - Gestão Financeira Inteligente via WhatsApp**
