# Dockerfile para FinMec - Sistema de Gestão Financeira via WhatsApp
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependências usando uv
RUN uv pip install --system --no-cache -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
