"""
Integração com Google Gemini API
Baseado no fluxo N8n: [FLUXO PRINCIPAL] - ImageMessage e DocumentMessage processing
"""
import httpx
from typing import Optional, Dict, Any
from loguru import logger
from app.core.config import settings


class GeminiClient:
    """
    Cliente para interação com Google Gemini API (Vision)
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = "gemini-2.0-flash-exp"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def analyze_image(
        self,
        image_base64: str,
        mime_type: str,
        prompt: Optional[str] = None
    ) -> str:
        """
        Analisa imagem usando Gemini Vision

        Args:
            image_base64: Imagem em base64
            mime_type: Tipo MIME (image/png, image/jpeg, etc.)
            prompt: Prompt customizado (opcional)

        Returns:
            Texto extraído/analisado da imagem
        """
        # Prompt padrão baseado no N8n
        if not prompt:
            prompt = """Descreva todos os itens presentes nessa imagem que tenham um preço associado.
Para cada item identificado, formate a saída da seguinte maneira:

Comprei [nome do item] por [valor do item].

Regras importantes:
1. Use APENAS números para os valores (sem símbolos de moeda)
2. Coloque cada item em uma nova linha
3. Se não houver itens com preço, responda: "Não encontrei itens com preço nesta imagem"
4. Seja preciso com os valores encontrados"""

        url = f"{self.base_url}/models/{self.model}:generateContent"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    params={"key": self.api_key},
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                # Extrair texto da resposta
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"✅ Imagem analisada: {text[:100]}...")
                return text

        except httpx.HTTPError as e:
            logger.error(f"❌ Erro ao analisar imagem: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"❌ Erro ao extrair texto da resposta Gemini: {e}")
            raise

    async def analyze_document(
        self,
        document_base64: str,
        mime_type: str,
        prompt: Optional[str] = None
    ) -> str:
        """
        Analisa documento (PDF) usando Gemini

        Args:
            document_base64: Documento em base64
            mime_type: Tipo MIME (application/pdf, etc.)
            prompt: Prompt customizado (opcional)

        Returns:
            Texto extraído/analisado do documento
        """
        # Prompt padrão para PDFs
        if not prompt:
            prompt = """Analise este documento e extraia todas as informações financeiras relevantes.
Identifique:
1. Descrição de produtos/serviços
2. Valores
3. Datas
4. Categorias (se identificável)

Formate como:
Comprei [item] por [valor] em [data se disponível]."""

        # Usa o mesmo método de análise (Gemini suporta PDFs)
        return await self.analyze_image(document_base64, mime_type, prompt)

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7
    ) -> str:
        """
        Gera texto usando Gemini (sem imagem)

        Args:
            prompt: Texto do prompt
            temperature: Criatividade (0-1)

        Returns:
            Texto gerado
        """
        url = f"{self.base_url}/models/{self.model}:generateContent"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    params={"key": self.api_key},
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                text = data["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"✅ Texto gerado ({len(text)} chars)")
                return text

        except httpx.HTTPError as e:
            logger.error(f"❌ Erro ao gerar texto: {e}")
            raise


# Instância global do cliente
gemini_client = GeminiClient()
