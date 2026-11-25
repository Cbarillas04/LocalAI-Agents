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

    # Send a prompt; return response
    def generate_response(self, messages, temperature = 0.2):
        response = self.client.chat.completions.create(
            model = self.model,
            messages = messages,
            temperature = temperature
        )
        return response.choices[0].message.content