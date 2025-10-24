# Dockerfile para FinMec - Sistema de Gestão Financeira via WhatsApp
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas pyproject.toml primeiro (melhor cache)
COPY pyproject.toml .

# Instalar dependências usando UV sync
RUN uv sync --no-dev

# Copiar o código da aplicação
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar usando uv run
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
