# 🚀 Guia de Deploy - FinMec

Guia completo para fazer deploy do FinMec no seu servidor usando Docker.

---

## 📋 Pré-requisitos no Servidor

Seu servidor precisa ter:

- **Sistema Operacional**: Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- **RAM**: Mínimo 2GB (Recomendado 4GB)
- **CPU**: Mínimo 2 cores
- **Disco**: Mínimo 10GB livres
- **Docker**: Versão 20.10+
- **Docker Compose**: Versão 2.0+
- **Portas**: 8000 (HTTP) e opcionalmente 443 (HTTPS)

---

## 🔧 Passo 1: Instalar Docker no Servidor

### Ubuntu/Debian:

```bash
# Atualizar pacotes
sudo apt-get update

# Instalar dependências
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# Adicionar chave GPG do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório do Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Adicionar seu usuário ao grupo docker
sudo usermod -aG docker $USER

# Reiniciar sessão ou executar
newgrp docker

# Verificar instalação
docker --version
docker compose version
```

### CentOS/RHEL:

```bash
# Instalar Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Iniciar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Adicionar usuário ao grupo
sudo usermod -aG docker $USER
```

---

## 📦 Passo 2: Enviar Código para o Servidor

### Opção 1: Via Git (Recomendado)

```bash
# No servidor
cd /opt
sudo mkdir finmec
sudo chown $USER:$USER finmec
cd finmec

# Clonar repositório (se estiver no Git)
git clone <seu-repositorio-git> .

# OU baixar código diretamente
# Fazer upload via scp, rsync, etc.
```

### Opção 2: Via SCP (do seu PC Windows)

```bash
# No seu PC (PowerShell ou CMD)
scp -r "C:\Users\Guilherme\Documents\Agente Financeiro" usuario@vps.gcdutra.cloud:/opt/finmec
```

### Opção 3: Via SFTP/FTP

Use um cliente como FileZilla ou WinSCP para transferir os arquivos.

---

## ⚙️ Passo 3: Configurar Variáveis de Ambiente

```bash
# No servidor, dentro da pasta do projeto
cd /opt/finmec

# Copiar arquivo de exemplo
cp .env.example .env

# Editar arquivo .env
nano .env
```

# Application
APP_NAME=FinMec
APP_VERSION=1.0.0
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Security (GERE UMA CHAVE SECRETA FORTE!)
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
```

**Salvar:** `Ctrl+O`, Enter, `Ctrl+X`

---

## 🚀 Passo 4: Deploy da Aplicação

### Deploy Automatizado (Recomendado):

```bash
# Dar permissão de execução ao script
chmod +x deploy.sh

# Executar deploy
./deploy.sh
```

### Deploy Manual:

```bash
# Build da imagem
docker compose build

# Iniciar containers
docker compose up -d

# Verificar status
docker compose ps

# Ver logs
docker compose logs -f finmec
```

---

## 🗄️ Passo 5: Inicializar Banco de Dados

```bash
# Executar dentro do container
docker compose exec finmec python init_database.py
```

Isso vai criar:
- ✅ Todas as tabelas
- ✅ Categorias padrão (Alimentação, Saúde, etc.)
- ✅ Métodos de pagamento padrão (PIX, Cartão, etc.)

---

## 🔒 Passo 6: Configurar Nginx + SSL (Opcional mas Recomendado)

### Instalar Nginx:

```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

### Configurar Nginx:

```bash
sudo nano /etc/nginx/sites-available/finmec
```

**Cole esta configuração:**

```nginx
server {
    listen 80;
    server_name finmec-hom.gcdutra.cloud;

    # Redirecionar HTTP para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name finmec-hom.gcdutra.cloud;

    # SSL será configurado pelo certbot
    # ssl_certificate /etc/letsencrypt/live/finmec-hom.gcdutra.cloud/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/finmec-hom.gcdutra.cloud/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy para FastAPI
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Timeout para webhooks
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
```

### Ativar configuração:

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/finmec /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### Instalar SSL (Let's Encrypt):

```bash
sudo certbot --nginx -d finmec-hom.gcdutra.cloud

# Renovação automática já está configurada!
```

---

## 🌐 Passo 7: Configurar DNS

No seu provedor de DNS (Cloudflare, GoDaddy, etc.):

```
Tipo: A
Nome: finmec-hom
Valor: IP_DO_SEU_SERVIDOR
TTL: 3600
```

---

## 📡 Passo 8: Configurar Webhooks na Uazapi

Acesse o painel da Uazapi e configure:

### Webhook de Mensagens:
- **URL**: `https://finmec-hom.gcdutra.cloud/webhook/finmec`
- **Método**: POST
- **Eventos**: Recebimento de mensagens

### Webhook de Ativação:
- **URL**: `https://finmec-hom.gcdutra.cloud/webhook/ativacao`
- **Método**: POST

---

## 🧪 Passo 9: Testar Deploy

```bash
# Health check
curl https://finmec-hom.gcdutra.cloud/health

# Deve retornar:
# {"status":"healthy","app":"FinMec","version":"1.0.0"}

# Documentação
# Acesse: https://finmec-hom.gcdutra.cloud/docs
```

---

## 📊 Comandos Úteis

### Ver logs em tempo real:
```bash
docker compose logs -f finmec
```

### Reiniciar aplicação:
```bash
docker compose restart finmec
```

### Parar aplicação:
```bash
docker compose down
```

### Atualizar aplicação (após mudanças no código):
```bash
git pull  # Se usar Git
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Entrar no container:
```bash
docker compose exec finmec bash
```

### Ver uso de recursos:
```bash
docker stats finmec-app
```

### Backup do banco de dados:
```bash
docker compose exec postgres pg_dump -U postgres finmec > backup_$(date +%Y%m%d).sql
```

---

## 🔍 Monitoramento e Logs

### Logs da aplicação:
```bash
# Ver logs
docker compose logs finmec

# Logs em tempo real
docker compose logs -f finmec

# Últimas 100 linhas
docker compose logs --tail=100 finmec
```

### Logs do Nginx:
```bash
# Access log
sudo tail -f /var/log/nginx/access.log

# Error log
sudo tail -f /var/log/nginx/error.log
```

### Verificar uso de disco:
```bash
df -h
docker system df
```

### Limpar recursos Docker não utilizados:
```bash
docker system prune -a
```

---

## 🚨 Troubleshooting

### Problema: Container não inicia

```bash
# Ver logs detalhados
docker compose logs finmec

# Verificar configuração
docker compose config

# Verificar .env
cat .env
```

### Problema: Erro de conexão com banco de dados

```bash
# Testar conexão com PostgreSQL
docker compose exec finmec python -c "from app.db.database import engine; print(engine.connect())"
```

### Problema: Porta 8000 já em uso

```bash
# Ver o que está usando a porta
sudo lsof -i :8000

# Matar processo
sudo kill -9 <PID>

# OU mudar a porta no docker-compose.yml
```

### Problema: SSL não funciona

```bash
# Verificar Nginx
sudo nginx -t

# Verificar certbot
sudo certbot certificates

# Renovar manualmente
sudo certbot renew
```

---

## 🔐 Segurança em Produção

### ✅ Checklist de Segurança:

- [ ] `DEBUG=False` no .env
- [ ] SECRET_KEY forte e única
- [ ] Firewall configurado (UFW)
- [ ] SSL/HTTPS ativo
- [ ] Backup automático do banco
- [ ] Monitoramento de logs
- [ ] Rate limiting no Nginx
- [ ] Atualizar Docker regularmente
- [ ] Senha forte no PostgreSQL

### Configurar Firewall (UFW):

```bash
# Instalar
sudo apt-get install -y ufw

# Configurar regras
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Ativar
sudo ufw enable

# Ver status
sudo ufw status
```

---

## 📈 Escalabilidade

Para escalar a aplicação:

```yaml
# No docker-compose.yml, aumentar workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Ou usar múltiplas réplicas:

```bash
docker compose up -d --scale finmec=3
```

---

## 🎉 Conclusão

Seu sistema FinMec agora está:
- ✅ Rodando em Docker
- ✅ Com SSL/HTTPS
- ✅ Monitorado
- ✅ Escalável
- ✅ Seguro
- ✅ Pronto para produção!

**URLs Finais:**
- API: https://finmec-hom.gcdutra.cloud
- Docs: https://finmec-hom.gcdutra.cloud/docs
- Health: https://finmec-hom.gcdutra.cloud/health

🚀 **Sistema em produção e funcionando!**
