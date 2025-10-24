# Makefile para FinMec
# Facilita comandos comuns do projeto

.PHONY: help install run dev test clean docker-build docker-up docker-down docker-logs deploy

help: ## Mostra esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências usando uv
	uv pip install -r requirements.txt

validate-env: ## Valida variáveis de ambiente do .env
	python validate_env.py

init-db: ## Inicializa o banco de dados
	python init_database.py

run: ## Roda o servidor localmente
	python run.py

dev: ## Roda o servidor em modo desenvolvimento
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Roda testes (quando implementados)
	pytest tests/

clean: ## Limpa arquivos temporários
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete

docker-build: ## Build da imagem Docker
	docker compose build

docker-up: ## Inicia containers
	docker compose up -d

docker-down: ## Para containers
	docker compose down

docker-restart: ## Reinicia containers
	docker compose restart

docker-logs: ## Mostra logs dos containers
	docker compose logs -f finmec

docker-shell: ## Acessa shell do container
	docker compose exec finmec bash

docker-clean: ## Remove containers e volumes
	docker compose down -v
	docker system prune -f

deploy: ## Deploy completo (build + up + init-db)
	@echo "🚀 Iniciando deploy..."
	docker compose down
	docker compose build --no-cache
	docker compose up -d
	@echo "⏳ Aguardando containers iniciarem..."
	sleep 10
	docker compose exec finmec python init_database.py || true
	@echo "✅ Deploy concluído!"
	@make docker-logs

status: ## Mostra status dos containers
	docker compose ps

health: ## Verifica health da aplicação
	@curl -s http://localhost:8000/health | python -m json.tool || echo "❌ Aplicação não está respondendo"

format: ## Formata código com black
	black app/ tests/

lint: ## Verifica código com flake8
	flake8 app/ tests/

backup-db: ## Faz backup do banco de dados
	@echo "📦 Fazendo backup do banco de dados..."
	docker compose exec postgres pg_dump -U postgres finmec > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup criado!"

update: ## Atualiza dependências usando uv
	uv pip install --upgrade -r requirements.txt

freeze: ## Congela dependências atuais usando uv
	uv pip freeze > requirements.txt

sync: ## Sincroniza dependências do pyproject.toml
	uv sync

docs: ## Abre documentação da API
	@echo "📚 Abrindo documentação..."
	@echo "http://localhost:8000/docs"
