import httpx
import pytest
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

# Test 4: Tokens are successfully counted
def test_count_tokens_success():
    with patch("shared.ai_client.httpx.post") as mock_post:
        client = AIClient()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tokens": [101, 202, 303, 404, 505, 606]
        }
        mock_post.return_value = mock_response

        result = client.count_tokens("Python is a programming language.")

        assert result == 6

        mock_post.assert_called_once_with(
            client.tokenize_url,
            json = {"content": "Python is a programming language."},
            timeout = 30.0
        )

# Test 5: Empty text returns zero tokens
def test_count_tokens_empty():
    with patch("shared.ai_client.httpx.post") as mock_post:
        client = AIClient()

        mock_response = MagicMock()
        mock_response.json.return_value = {"tokens": []}
        mock_post.return_value = mock_response

        result = client.count_tokens("")

        assert result == 0

# Test 6: HTTP errors
def test_count_tokens_http_error():
    with patch("shared.ai_client.httpx.post") as mock_post:
        client = AIClient()

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server error",
            request = MagicMock(),
            response = MagicMock()
        )
        mock_post.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            client.count_tokens("Python")