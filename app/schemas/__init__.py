"""
Schemas Pydantic para validação de dados
"""
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserActivationRequest
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse
)
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse
)
from app.schemas.payment_method import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodResponse,
    PaymentMethodListResponse
)
from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderListResponse
)
from app.schemas.webhook import (
    WhatsAppMessage,
    WebhookRequest,
    WhatsAppMediaInfo
)

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserActivationRequest",
    # Transaction
    "TransactionCreate",
    "TransactionUpdate",
    "TransactionResponse",
    "TransactionListResponse",
    # Category
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryListResponse",
    # Payment Method
    "PaymentMethodCreate",
    "PaymentMethodUpdate",
    "PaymentMethodResponse",
    "PaymentMethodListResponse",
    # Reminder
    "ReminderCreate",
    "ReminderUpdate",
    "ReminderResponse",
    "ReminderListResponse",
    # Webhook
    "WhatsAppMessage",
    "WebhookRequest",
    "WhatsAppMediaInfo",
]
