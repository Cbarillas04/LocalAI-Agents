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

# Test 2: verify it generates a response
def test_generate_response():
    with patch("shared.ai_client.OpenAI") as mock_openai:
        client = AIClient()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Python is a programming language"

        mock_openai.return_value.chat.completions.create.return_value = mock_response
        result = client.generate_response("What is Python?")

        assert result == "Python is a programming language"
        mock_openai.return_value.chat.completions.create.assert_called_once_with(
            model = "qwen2.5-coder-7b",
            messages = [{
                "role": "user",
                "content": "What is Python?"
            }],
            temperature = 0.2
        )

# Test 3: Temperature passed to model
def test_temperature():
    client = AIClient()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Python is a programming language"

    with patch.object(
        client.client.chat.completions,
        "create",
        return_value = mock_response,
    ) as mock_create:
        prompt = "What is Python?"
        client.generate_response(prompt, 0.6)
        mock_create.assert_called_once()
        temperature = mock_create.call_args.kwargs["temperature"]

        assert temperature == 0.6

# Test 4: Prompt reaches model correctly
def test_prompt():
    client = AIClient()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Python is a programming language"

    with patch.object(
        client.client.chat.completions,
        "create",
        return_value = mock_response
    ) as mock_create:
        prompt = "What is Python?"
        client.generate_response(prompt)
        mock_create.assert_called_once()
        messages = mock_create.call_args.kwargs["messages"]

        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == prompt