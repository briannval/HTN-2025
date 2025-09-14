import os
from typing import Any, Dict, List

import cohere


class CohereAnswer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        self.client = cohere.Client(self.api_key)
        self.model = "command-r-plus"

    def generate_answer(self, query: str, context: List[Dict[str, Any]]) -> str:
        try:
            context_text = self._format_context(context)

            prompt = f"""Based on the following context information, please answer the user's question accurately and helpfully.

Context:
{context_text}

User Question: {query}

Please provide a clear, concise answer based on the context provided. If the context doesn't contain enough information to answer the question, please say so."""

            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )

            return response.message.content[0].text

        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        if not context:
            return "No context available."

        formatted_context = []
        for i, item in enumerate(context, 1):
            source = item.get("_source", {})
            score = item.get("_score", "N/A")

            context_entry = f"Result {i} (Relevance Score: {score}):\n"
            context_entry += f"- Description: {source.get('description', 'N/A')}\n"
            context_entry += f"- Location: {source.get('location', 'N/A')}\n"
            context_entry += f"- Time: {source.get('time', 'N/A')}\n"

            formatted_context.append(context_entry)

        return "\n".join(formatted_context)

    def generate_contextual_answer(
        self, query: str, context: List[Dict[str, Any]], system_prompt: str = None
    ) -> str:
        try:
            context_text = context

            default_system = "You are a helpful assistant that helps a blind or visually impaired person answer questions based on provided context. These are description of images that the user requested to take, and which seems to be relevant to the question. Be accurate, concise, and helpful. Talk about what might spike a memory from a blind person's perspective, and include the time as well."
            system_message = system_prompt or default_system

            user_prompt = f"""Context Information:
            {context_text}
            Question: {query}"""

            response = self.client.chat(
                model=self.model,
                message=user_prompt,
                documents=[
                    {
                        "instructions": system_message,
                        "reference": context_text,
                    }
                ],
                temperature=0.3,
                max_tokens=500,
            )

            return response.text

        except Exception as e:
            return f"Error generating contextual answer: {str(e)}"
