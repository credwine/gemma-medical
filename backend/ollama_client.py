"""Ollama client for Gemma 4 inference."""

import json
import httpx
from typing import AsyncGenerator
from backend.config import OLLAMA_BASE_URL, GEMMA_MODEL, MAX_TOKENS, TEMPERATURE


async def generate(prompt: str, system: str = "", model: str = None) -> str:
    """Generate a complete response from Gemma 4 via Ollama."""
    model = model or GEMMA_MODEL
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {
                    "num_predict": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                },
            },
        )
        response.raise_for_status()
        return response.json()["response"]


async def generate_stream(prompt: str, system: str = "", model: str = None) -> AsyncGenerator[str, None]:
    """Stream response tokens from Gemma 4 via Ollama."""
    model = model or GEMMA_MODEL
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": system,
                "stream": True,
                "options": {
                    "num_predict": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                },
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done"):
                        break


async def generate_with_tools(prompt: str, system: str = "", tools: list = None, model: str = None) -> dict:
    """Generate a response with function calling support."""
    model = model or GEMMA_MODEL
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {
            "num_predict": MAX_TOKENS,
            "temperature": TEMPERATURE,
        },
    }
    if tools:
        payload["tools"] = tools

    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
        )
        response.raise_for_status()
        return response.json()


async def chat(messages: list, system: str = "", model: str = None, tools: list = None) -> dict:
    """Chat completion with message history and optional tool use."""
    model = model or GEMMA_MODEL
    formatted_messages = []
    if system:
        formatted_messages.append({"role": "system", "content": system})
    formatted_messages.extend(messages)

    payload = {
        "model": model,
        "messages": formatted_messages,
        "stream": False,
        "options": {
            "num_predict": MAX_TOKENS,
            "temperature": TEMPERATURE,
        },
    }
    if tools:
        payload["tools"] = tools

    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
        )
        response.raise_for_status()
        return response.json()


async def chat_stream(messages: list, system: str = "", model: str = None) -> AsyncGenerator[str, None]:
    """Stream chat completion tokens."""
    model = model or GEMMA_MODEL
    formatted_messages = []
    if system:
        formatted_messages.append({"role": "system", "content": system})
    formatted_messages.extend(messages)

    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": model,
                "messages": formatted_messages,
                "stream": True,
                "options": {
                    "num_predict": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                },
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    msg = data.get("message", {})
                    if "content" in msg:
                        yield msg["content"]
                    if data.get("done"):
                        break


async def check_model() -> dict:
    """Check if the required model is available in Ollama."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            return {
                "ollama_running": True,
                "models_available": model_names,
                "gemma4_ready": any(GEMMA_MODEL in name for name in model_names),
                "required_model": GEMMA_MODEL,
            }
        except (httpx.ConnectError, httpx.HTTPError):
            return {
                "ollama_running": False,
                "models_available": [],
                "gemma4_ready": False,
                "required_model": GEMMA_MODEL,
            }
