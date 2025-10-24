"""
Integração com Uazapi (WhatsApp API)
Baseado no fluxo N8n: [FLUXO PRINCIPAL]
"""
import asyncio
import httpx
from typing import Optional, Dict, Any, List
from loguru import logger
from app.core.config import settings


class UazapiClient:
    """
    Cliente para interação com a API Uazapi (WhatsApp)
    """

    def __init__(self):
        self.base_url = settings.UAZAPI_BASE_URL
        self.token = settings.UAZAPI_TOKEN
        self.headers = {
            "token": self.token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    async def send_text(
        self,
        number: str,
        text: str,
        read_chat: bool = True,
        link_preview: bool = True
    ) -> Dict[str, Any]:
        """
        Envia mensagem de texto via WhatsApp

        Args:
            number: Número do destinatário (ex: 5511999999999 ou 5511999999999@s.whatsapp.net)
            text: Texto da mensagem
            read_chat: Marcar chat como lido
            link_preview: Mostrar preview de links

        Returns:
            Resposta da API Uazapi
        """
        # Limpar número (remover @s.whatsapp.net se existir)
        clean_number = number.split("@")[0] if "@" in number else number

        url = f"{self.base_url}/send/text"
        payload = {
            "number": clean_number,
            "text": text,
            "readchat": str(read_chat).lower(),
            "linkPreview": str(link_preview).lower()
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                logger.info(f"✅ Mensagem enviada para {clean_number}")
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}")
            raise

    async def send_media(
        self,
        number: str,
        media_type: str,
        file_url: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia mídia via WhatsApp (imagem, áudio, documento, vídeo)

        Args:
            number: Número do destinatário
            media_type: Tipo de mídia (image, audio, document, video)
            file_url: URL do arquivo
            caption: Legenda/texto da mídia

        Returns:
            Resposta da API Uazapi
        """
        clean_number = number.split("@")[0] if "@" in number else number

        url = f"{self.base_url}/send/media"
        payload = {
            "number": clean_number,
            "type": media_type,
            "file": file_url
        }

        if caption:
            payload["text"] = caption

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                logger.info(f"✅ Mídia ({media_type}) enviada para {clean_number}")
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"❌ Erro ao enviar mídia: {e}")
            raise

    async def download_media(
        self,
        message_id: str,
        return_base64: bool = True,
        return_link: bool = False
    ) -> Dict[str, Any]:
        """
        Baixa mídia de uma mensagem recebida

        Args:
            message_id: ID da mensagem
            return_base64: Retornar arquivo em base64
            return_link: Retornar link do arquivo

        Returns:
            Dict com base64Data e mimetype
        """
        url = f"{self.base_url}/message/download"
        payload = {
            "id": message_id,
            "return_base64": return_base64,
            "return_link": return_link
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()
                logger.info(f"✅ Mídia baixada: {data.get('mimetype', 'unknown')}")
                return data
        except httpx.HTTPError as e:
            logger.error(f"❌ Erro ao baixar mídia: {e}")
            raise

    async def schedule_message(
        self,
        numbers: List[str],
        text: str,
        scheduled_timestamp_ms: int,
        delay_min: int = 10,
        delay_max: int = 30,
        info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Agenda mensagem para envio futuro
        Usado no fluxo [INCLUI LEMBRETES]

        Args:
            numbers: Lista de números destinatários
            text: Texto da mensagem
            scheduled_timestamp_ms: Timestamp Unix em milissegundos
            delay_min: Delay mínimo entre mensagens (segundos)
            delay_max: Delay máximo entre mensagens (segundos)
            info: Informação adicional

        Returns:
            Resposta da API Uazapi
        """
        url = f"{self.base_url}/sender/simple"
        payload = {
            "numbers": numbers,
            "type": "text",
            "delayMin": delay_min,
            "delayMax": delay_max,
            "scheduled_for": scheduled_timestamp_ms,
            "text": text
        }

        if info:
            payload["info"] = info

        try:
            # Retry logic: 3 tentativas com delay de 3 segundos
            async with httpx.AsyncClient(timeout=30.0) as client:
                for attempt in range(3):
                    try:
                        response = await client.post(url, headers=self.headers, json=payload)
                        response.raise_for_status()
                        logger.info(f"✅ Mensagem agendada para {len(numbers)} número(s)")
                        return response.json()
                    except httpx.HTTPError as e:
                        if attempt == 2:  # última tentativa
                            raise
                        logger.warning(f"⚠️ Tentativa {attempt + 1} falhou, aguardando 3s...")
                        await asyncio.sleep(3)
        except httpx.HTTPError as e:
            logger.error(f"❌ Erro ao agendar mensagem: {e}")
            raise


# Instância global do cliente
uazapi_client = UazapiClient()
