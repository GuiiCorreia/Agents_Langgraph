# Dockerfile para FinMec - Sistema de Gestão Financeira via WhatsApp
# Python 3.12 oficial slim (menor e mais seguro)
FROM python:3.12-slim

# Metadados
LABEL maintainer="FinMec Team"
LABEL description="Sistema de gestão financeira via WhatsApp com FastAPI, LangGraph e IA"
LABEL version="1.0.0"

# Variáveis de ambiente para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv (gerenciador de pacotes Python ultra-rápido)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copiar arquivos de dependências primeiro (melhor cache do Docker)
COPY requirements.txt .

# Instalar dependências Python usando uv (muito mais rápido que pip)
RUN uv pip install --system --no-cache -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Criar diretório para logs
RUN mkdir -p /app/logs

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 finmec && \
    chown -R finmec:finmec /app

# Expor porta da aplicação
EXPOSE 8000

# Health check (executado como root, antes de mudar usuário)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Mudar para usuário não-root
USER finmec

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
