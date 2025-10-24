from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from loguru import logger

# Importar routers
from app.api.endpoints import (
    transactions,
    categories,
    payment_methods,
    reminders,
    wallet,
    dashboard,
    charts,
    webhooks
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de Gestão Financeira via WhatsApp",
    debug=settings.DEBUG
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Eventos executados ao iniciar a aplicação
    """
    logger.info(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"🔧 Modo Debug: {settings.DEBUG}")
    logger.info(f"🌐 Host: {settings.HOST}:{settings.PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Eventos executados ao encerrar a aplicação
    """
    logger.info(f"🛑 Encerrando {settings.APP_NAME}")


@app.get("/")
async def root():
    """
    Endpoint raiz para verificar se a API está funcionando
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "message": "API de Gestão Financeira via WhatsApp está funcionando!"
    }


@app.get("/health")
async def health_check():
    """
    Endpoint de health check
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Incluir routers
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transações"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categorias"])
app.include_router(payment_methods.router, prefix="/api/payment-methods", tags=["Métodos de Pagamento"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["Lembretes"])
app.include_router(wallet.router, prefix="/api/wallet", tags=["Carteiras"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(charts.router, prefix="/api/charts", tags=["Gráficos"])
app.include_router(webhooks.router, prefix="/webhook", tags=["Webhooks"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
