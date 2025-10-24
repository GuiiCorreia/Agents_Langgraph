from pydantic import BaseModel, Field
from typing import Optional, Any, Dict


class WhatsAppMessage(BaseModel):
    """
    Schema para mensagens recebidas do WhatsApp via Uazapi
    """
    id: Optional[str] = Field(None, description="ID da mensagem")
    fromMe: Optional[bool] = Field(None, description="Mensagem enviada por mim?")
    author: Optional[str] = None
    pushName: Optional[str] = None
    type: str = Field(..., description="Tipo: conversation, extendedTextMessage, audioMessage, etc")
    body: Optional[str] = Field(None, description="Corpo da mensagem de texto")
    conversation: Optional[str] = Field(None, description="Texto da conversa")

    # Para mensagens de áudio
    audioMessage: Optional[Dict[str, Any]] = None

    # Para mensagens de imagem
    imageMessage: Optional[Dict[str, Any]] = None

    # Para documentos/PDFs
    documentMessage: Optional[Dict[str, Any]] = None

    # Metadados
    timestamp: Optional[int] = None
    messageTimestamp: Optional[int] = None


class WebhookRequest(BaseModel):
    """
    Schema principal do webhook do WhatsApp
    """
    remoteJid: str = Field(..., description="JID do remetente")
    instanceId: Optional[str] = None
    message: WhatsAppMessage = Field(..., description="Dados da mensagem")

    class Config:
        json_schema_extra = {
            "example": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "instanceId": "finmec",
                "message": {
                    "type": "conversation",
                    "body": "Gastei 50 reais no almoço",
                    "conversation": "Gastei 50 reais no almoço",
                    "timestamp": 1234567890
                }
            }
        }


class WhatsAppMediaInfo(BaseModel):
    """
    Schema para informações de mídia (áudio, imagem, documento)
    """
    url: Optional[str] = None
    mimetype: Optional[str] = None
    fileSha256: Optional[str] = None
    fileLength: Optional[int] = None
    caption: Optional[str] = None
    fileName: Optional[str] = None
