from unittest.mock import patch, MagicMock
from shared.ai_client import AIClient

# Test 1: Initialize the client
def test_client_intialization():
    with patch("shared.ai_client.OpenAI") as mock_openai:
        client = AIClient()
        assert client.model == "qwen2.5-coder-7b"

        mock_openai.assert_called_once_with(
            base_url = "http://127.0.0.1:8080/v1",
            api_key = "local"
        )

# Test 2: Verify it generates a response using messages
def test_generate_response():
    with patch("shared.ai_client.OpenAI") as mock_openai:
        client = AIClient()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Python is a programming language"

        mock_openai.return_value.chat.completions.create.return_value = mock_response

        messages = [
            {"role": "system", "content": "You are a coding assistant."},
            {"role": "user", "content": "What is Python?"}
        ]

        result = client.generate_response(messages)

        assert result == "Python is a programming language"
        mock_openai.return_value.chat.completions.create.assert_called_once_with(
            model = "qwen2.5-coder-7b",
            messages = messages,
            temperature = 0.2
        )

# Test 3: Temperature passed to model
def test_temperature():
    with patch("shared.ai_client.OpenAI") as mock_openai:
        client = AIClient()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Python is a programming language"

        mock_openai.return_value.chat.completions.create.return_value = mock_response
        messages = [
            {"role": "user", "content": "What is Python?"}
        ]
        client.generate_response(messages, 0.6)

        mock_openai.return_value.chat.completions.create.assert_called_once()
        temperature = (
            mock_openai.return_value.chat.completions.create.call_args.kwargs["temperature"]
        )
        assert temperature == 0.6