#!/bin/bash

# ===================================
# Script de Deploy - FinMec
# ===================================

set -e  # Parar em caso de erro

echo "======================================"
echo "🚀 DEPLOY DO FINMEC"
echo "======================================"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se .env existe
if [ ! -f .env ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado!${NC}"
    echo "Copie .env.example para .env e configure suas credenciais"
    echo "cp .env.example .env"
    exit 1
fi

echo -e "${GREEN}✅ Arquivo .env encontrado${NC}"

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não está instalado!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker está instalado${NC}"

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose não está instalado!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker Compose está instalado${NC}"

# Parar containers antigos
echo ""
echo -e "${YELLOW}🛑 Parando containers antigos...${NC}"
docker-compose down || true

# Build da imagem
echo ""
echo -e "${YELLOW}🔨 Construindo imagem Docker...${NC}"
docker-compose build --no-cache

# Iniciar containers
echo ""
echo -e "${YELLOW}🚀 Iniciando containers...${NC}"
docker-compose up -d

# Aguardar containers iniciarem
echo ""
echo -e "${YELLOW}⏳ Aguardando containers iniciarem...${NC}"
sleep 10

# Verificar status
echo ""
echo -e "${YELLOW}📊 Status dos containers:${NC}"
docker-compose ps

# Verificar logs
echo ""
echo -e "${YELLOW}📋 Últimas linhas do log:${NC}"
docker-compose logs --tail=20 finmec

# Executar inicialização do banco de dados
echo ""
echo -e "${YELLOW}🗄️ Inicializando banco de dados...${NC}"
docker-compose exec finmec python init_database.py || true

# Health check
echo ""
echo -e "${YELLOW}🏥 Verificando health check...${NC}"
sleep 5

HEALTH_CHECK=$(curl -s http://localhost:8000/health || echo "failed")

if [[ $HEALTH_CHECK == *"healthy"* ]]; then
    echo -e "${GREEN}✅ Aplicação está saudável!${NC}"
else
    echo -e "${RED}❌ Aplicação não está respondendo corretamente${NC}"
    echo "Verifique os logs: docker-compose logs finmec"
    exit 1
fi

# Resumo final
echo ""
echo "======================================"
echo -e "${GREEN}✅ DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
echo "======================================"
echo ""
echo "📍 URLs Disponíveis:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo "   - Health: http://localhost:8000/health"
echo ""
echo "📋 Comandos úteis:"
echo "   - Ver logs: docker-compose logs -f finmec"
echo "   - Parar: docker-compose down"
echo "   - Reiniciar: docker-compose restart"
echo "   - Entrar no container: docker-compose exec finmec bash"
echo ""
echo "🎉 Sistema pronto para uso!"
