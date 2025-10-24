# 🚀 Deploy no EasyPanel - FinMec

Guia completo para fazer deploy do FinMec no EasyPanel.

---

## 📋 Pré-requisitos

- Conta no EasyPanel
- Código do projeto em um repositório Git (GitHub, GitLab, Bitbucket)
- Credenciais das APIs (OpenAI, Gemini, Uazapi)
- PostgreSQL disponível (pode ser externo ou criar no EasyPanel)

---

## 🎯 Passo 1: Preparar Repositório Git

### Opção 1: GitHub (Recomendado)

```bash
# Inicializar Git (se ainda não tem)
cd "C:\Users\Guilherme\Documents\Agente Financeiro"
git init

# Adicionar arquivos
git add .

# Commit inicial
git commit -m "Initial commit - FinMec"

# Criar repositório no GitHub e vincular
git remote add origin https://github.com/SEU_USUARIO/finmec.git
git branch -M main
git push -u origin main
```

### Opção 2: GitLab ou Bitbucket

Similar ao GitHub, crie um repositório e faça push.

---

## 🐳 Passo 2: Criar Aplicação no EasyPanel

### 1. Acessar EasyPanel

- URL: https://easypanel.io
- Login com sua conta

### 2. Criar Novo Projeto

1. Clique em **"New Project"**
2. Nome: `finmec`
3. Clique em **"Create"**

### 3. Adicionar Serviço

1. Dentro do projeto, clique **"Add Service"**
2. Selecione **"App"**
3. Escolha **"GitHub"** (ou seu provider Git)
4. Autorize acesso ao repositório
5. Selecione o repositório `finmec`
6. Branch: `main`

---

## ⚙️ Passo 3: Configurar Build

### Build Settings:

1. **Build Method**: `Dockerfile`
2. **Dockerfile Path**: `./Dockerfile`
3. **Build Context**: `.`

**✨ Nosso Dockerfile já usa `uv` para builds ultra-rápidos!**

O Dockerfile já está otimizado com:
- ✅ **uv** - 10-100x mais rápido que pip
- ✅ Multi-stage build cache otimizado
- ✅ Health checks integrados
- ✅ Usuário não-root para segurança

---

## 🔐 Passo 4: Configurar Variáveis de Ambiente

No EasyPanel, vá para a aba **"Environment"** e adicione:

### Variáveis Obrigatórias:

```env
# Database (se usar PostgreSQL externo)
DATABASE_URL=postgresql://postgres:SUA_SENHA@SEU_HOST:5432/finmec

# OpenAI
OPENAI_API_KEY=sk-proj-SUA_CHAVE_AQUI

# Google Gemini
GEMINI_API_KEY=SUA_CHAVE_GEMINI_AQUI

# Uazapi
UAZAPI_BASE_URL=https://finmec.uazapi.com
UAZAPI_TOKEN=SEU_TOKEN_UAZAPI

# Security (IMPORTANTE: Gere uma chave única!)
SECRET_KEY=sua_chave_secreta_super_forte_aqui
```

### Variáveis Opcionais:

```env
APP_NAME=FinMec
APP_VERSION=1.0.0
DEBUG=False
HOST=0.0.0.0
PORT=8000
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Como Gerar SECRET_KEY:

```bash
# No seu PC
openssl rand -hex 32
```

Copie o resultado e cole no EasyPanel.

---

## 🗄️ Passo 5: Configurar PostgreSQL

### Opção 1: PostgreSQL Externo (Já Tem)

Use suas credenciais existentes:

```env
DATABASE_URL=postgresql://postgres:253ad778d41c09bb0da7@vps.gcdutra.cloud:5432/hom
```

### Opção 2: Criar PostgreSQL no EasyPanel

1. No projeto, clique **"Add Service"**
2. Selecione **"Database"** → **"PostgreSQL"**
3. Nome: `finmec-db`
4. Versão: `16` (latest)
5. Clique **"Create"**

Após criar, copie a **Connection String** e use como `DATABASE_URL`.

---

## 🌐 Passo 6: Configurar Domínio

### 1. Configurar Domínio no EasyPanel

1. Vá para **"Domains"**
2. Clique **"Add Domain"**
3. Digite: `finmec-hom.gcdutra.cloud`
4. Ative **"Enable SSL"** (Let's Encrypt automático)
5. Clique **"Save"**

### 2. Configurar DNS

No seu provedor de DNS (Cloudflare, etc.):

```
Tipo: A
Nome: finmec-hom
Valor: <IP_DO_EASYPANEL>
TTL: 3600
```

**IP do EasyPanel:** Você encontra nas configurações do projeto.

---

## 🚀 Passo 7: Deploy

### 1. Deploy Automático

1. Clique em **"Deploy"**
2. EasyPanel irá:
   - ✅ Clonar repositório
   - ✅ Build da imagem Docker
   - ✅ Iniciar container
   - ✅ Configurar SSL
   - ✅ Expor aplicação

### 2. Acompanhar Build

Na aba **"Logs"**, você verá:

```
Building Docker image...
Step 1/10: FROM python:3.12-slim
...
Successfully built image
Starting container...
Container started successfully!
```

### 3. Inicializar Banco de Dados

Após o deploy, você precisa executar uma vez:

1. Vá para **"Console"** (Terminal do container)
2. Execute:

```bash
python init_database.py
```

Isso criará:
- ✅ Todas as tabelas
- ✅ Categorias padrão
- ✅ Métodos de pagamento padrão

---

## ✅ Passo 8: Verificar Deploy

### 1. Health Check

```bash
curl https://finmec-hom.gcdutra.cloud/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "app": "FinMec",
  "version": "1.0.0"
}
```

### 2. Acessar Documentação

Abra no navegador:
- **Swagger UI**: https://finmec-hom.gcdutra.cloud/docs
- **ReDoc**: https://finmec-hom.gcdutra.cloud/redoc

---

## 🔔 Passo 9: Configurar Webhooks na Uazapi

1. Acesse o painel da **Uazapi**
2. Configure os webhooks:

### Webhook de Mensagens:
```
URL: https://finmec-hom.gcdutra.cloud/webhook/finmec
Método: POST
Eventos: Mensagens recebidas
```

### Webhook de Ativação:
```
URL: https://finmec-hom.gcdutra.cloud/webhook/ativacao
Método: POST
```

---

## 🔄 Atualizações Automáticas

### Configurar Auto-Deploy no GitHub:

O EasyPanel já detecta commits automaticamente!

1. Faça alterações no código
2. Commit e push:
   ```bash
   git add .
   git commit -m "Update feature X"
   git push
   ```
3. EasyPanel detecta e faz deploy automático!

### Deploy Manual:

No EasyPanel, clique **"Redeploy"** sempre que quiser.

---

## 📊 Monitoramento no EasyPanel

### 1. Logs em Tempo Real

Vá para **"Logs"** para ver:
- ✅ Logs da aplicação
- ✅ Erros
- ✅ Requisições HTTP

### 2. Métricas

Vá para **"Metrics"** para ver:
- ✅ CPU usage
- ✅ Memory usage
- ✅ Network traffic
- ✅ Request rate

### 3. Console (Terminal)

Acesse **"Console"** para:
```bash
# Ver logs
docker logs -f finmec

# Executar comandos
python init_database.py

# Acessar banco
python -c "from app.db.database import engine; print(engine.connect())"
```

---

## 🔧 Configurações Avançadas

### Escalar Aplicação (Mais Workers):

1. Vá para **"Settings"**
2. **"Resources"**
3. Configure:
   - **CPU**: 1 vCPU (ou mais)
   - **Memory**: 1GB (ou mais)
   - **Replicas**: 1 (ou mais para alta disponibilidade)

### Health Check Customizado:

```yaml
Health Check Path: /health
Health Check Interval: 30s
Health Check Timeout: 10s
```

### Restart Policy:

```yaml
Restart Policy: always
Max Restart Attempts: 3
```

---

## 🐛 Troubleshooting

### Container não inicia

**1. Verificar logs:**
```
EasyPanel → Logs → Ver erros
```

**2. Variáveis de ambiente:**
```
Verificar se todas as variáveis obrigatórias estão configuradas
```

**3. Build falhou:**
```
Verificar se Dockerfile está correto
Verificar requirements.txt
```

### Erro de conexão com banco

**1. Verificar DATABASE_URL:**
```env
# Deve estar no formato correto
DATABASE_URL=postgresql://user:pass@host:port/db
```

**2. Testar conexão:**
```bash
# No Console do EasyPanel
python -c "from app.db.database import engine; print(engine.connect())"
```

### Webhook não funciona

**1. Verificar URL no Uazapi:**
```
Deve ser: https://finmec-hom.gcdutra.cloud/webhook/finmec
```

**2. Verificar SSL:**
```bash
curl -I https://finmec-hom.gcdutra.cloud/health
```

**3. Ver logs de requisições:**
```
EasyPanel → Logs → Filtrar por "webhook"
```

---

## 📋 Checklist Final

Antes de considerar o deploy concluído:

- [ ] Código no GitHub/GitLab
- [ ] Aplicação criada no EasyPanel
- [ ] Dockerfile detectado e build funcionando
- [ ] Variáveis de ambiente configuradas
- [ ] PostgreSQL configurado e acessível
- [ ] Domínio configurado (finmec-hom.gcdutra.cloud)
- [ ] SSL ativo (Let's Encrypt)
- [ ] Banco de dados inicializado (`init_database.py`)
- [ ] Health check respondendo
- [ ] Documentação acessível (/docs)
- [ ] Webhooks configurados na Uazapi
- [ ] Teste via WhatsApp funcionando
- [ ] Logs monitorados
- [ ] Auto-deploy configurado

---

## 🎉 Deploy Completo!

Seu FinMec está rodando no EasyPanel! 🚀

**URLs Finais:**
- 🌐 **App**: https://finmec-hom.gcdutra.cloud
- 📚 **Docs**: https://finmec-hom.gcdutra.cloud/docs
- 🏥 **Health**: https://finmec-hom.gcdutra.cloud/health
- 📡 **Webhook**: https://finmec-hom.gcdutra.cloud/webhook/finmec

**Próximo Passo:**
Envie uma mensagem no WhatsApp e teste o sistema!

---

## 📞 Suporte

- **EasyPanel Docs**: https://easypanel.io/docs
- **Logs**: EasyPanel → Seu Projeto → Logs
- **Status**: EasyPanel → Seu Projeto → Metrics

---

**✅ Sistema em produção no EasyPanel!**
