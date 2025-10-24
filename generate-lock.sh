#!/bin/bash
# Script para gerar uv.lock

set -e

echo "🚀 Gerando uv.lock..."

# Verificar se UV está instalado
if ! command -v uv &> /dev/null; then
    echo "❌ UV não instalado. Instalando..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✓ UV instalado: $(uv --version)"

# Gerar lock
echo "📦 Instalando dependências e gerando lock..."
uv sync

echo "✅ uv.lock gerado!"
echo ""
echo "Próximo passo:"
echo "  git add pyproject.toml uv.lock"
echo "  git commit -m 'feat: adicionar uv.lock'"
echo "  git push"