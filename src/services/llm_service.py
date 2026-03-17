"""LLM service for interactions with OpenAI."""

from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from src.core import settings
from src.prompts.templates import CLASSIFY_EMAIL_PROMPT, RESPONSE_PROMPT


class LLMService:
    """Service for LLM operations using LangChain."""

    def __init__(self):
        """Initialize LLM service with LangChain chains."""
        self.client = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=settings.openai_temperature,
        )

        # LangChain chain composition
        self._classify_chain = CLASSIFY_EMAIL_PROMPT | self.client | JsonOutputParser()
        self._response_chain = RESPONSE_PROMPT | self.client | StrOutputParser()

    async def classify_email(self, subject: str, body: str) -> Dict[str, Any]:
        """
        Classify email by intent, category, and priority.

        Args:
            subject: Email subject
            body: Email body

        Returns:
            Dict with keys: intent, category, priority
        """
        try:
            result = await self._classify_chain.ainvoke({"subject": subject, "body": body})
            # Ensure priority is within valid range
            priority = int(result.get("priority", 3))
            priority = max(1, min(5, priority))
            return {
                "intent": result.get("intent", "general_inquiry"),
                "category": result.get("category", "other"),
                "priority": priority,
            }
        except Exception as e:
            print(f"[CLASSIFY ERROR] {str(e)}")
            return {"intent": "general_inquiry", "category": "other", "priority": 3}

    async def generate_response(
        self, subject: str, body: str, category: str, context: str
    ) -> str:
        """
        Generate response to email using LLM.

        Args:
            subject: Email subject
            body: Email body
            category: Email category
            context: Knowledge base context

        Returns:
            str: Generated response
        """
        try:
            result = await self._response_chain.ainvoke({
                "subject": subject,
                "body": body,
                "category": category,
                "context": context,
            })
            return result
        except Exception as e:
            print(f"[RESPONSE ERROR] {str(e)}")
            return f"Thank you for your email about '{subject}'. We'll get back to you shortly."


llm_service = LLMService()
