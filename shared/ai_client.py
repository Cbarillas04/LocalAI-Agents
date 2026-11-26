import httpx
from openai import OpenAI

# Handles the communication with the local AI model
class AIClient:
    def __init__(
            self,
            base_url = "http://127.0.0.1:8080/v1",
            api_key = "local",
            model = "qwen2.5-coder-7b"
    ):
        # Create a connection to the local AI server
        self.client = OpenAI(
            base_url = base_url,
            api_key = api_key
        )
        self.model = model
        self.tokenize_url = f"{base_url.rstrip('/').removesuffix('/v1')}/tokenize"

    # Send a prompt; return response
    def generate_response(self, messages, temperature = 0.2, max_tokens = 2500):
        response = self.client.chat.completions.create(
            model = self.model,
            messages = messages,
            temperature = temperature,
            max_tokens = max_tokens,
        )
        choice = response.choices[0]
        return {
            "content": choice.message.content,
            "truncated": choice.finish_reason == "length",
        }

    # Convert text into tokens using llama.cpp
    def count_tokens(self, text):
        response = httpx.post(self.tokenize_url, json = {"content": text}, timeout = 30.0)
        response.raise_for_status()
        result = response.json()

        return len(result["tokens"])