# Dockerfile para FinMec - Sistema de Gestão Financeira via WhatsApp
# Usando UV como único gerenciador de dependências
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Metadados
LABEL maintainer="FinMec Team"
LABEL description="Sistema de gestão financeira via WhatsApp com FastAPI, LangGraph e IA"
LABEL version="1.0.0"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de configuração do projeto
COPY pyproject.toml ./
COPY uv.lock ./

# Instalar dependências usando uv sync
# --frozen: usa exatamente as versões do uv.lock
# --no-cache: não usa cache para garantir build limpo
RUN uv sync --frozen --no-cache --no-dev

# Copiar o código da aplicação
COPY . .

# Criar diretório para logs
RUN mkdir -p /app/logs

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 finmec && \
    chown -R finmec:finmec /app

# Expor porta da aplicação
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Mudar para usuário não-root
USER finmec

# Comando para iniciar a aplicação
# Usando uv run para executar com o ambiente virtual do uv
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
