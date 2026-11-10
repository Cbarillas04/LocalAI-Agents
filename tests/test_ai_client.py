from unittest.mock import patch, MagicMock
from shared.ai_client import AIClient

# Test 1:
def test_client_intialization():
    client = AIClient()
    model = client.model
    url = str(client.client.base_url)
    assert model == "qwen2.5-coder-7b" and url == "http://127.0.0.1:8080/v1/"

# Test 2:
def test_generate_response():
    client = AIClient()
    result = client.generate_response("What is Python?")
    assert isinstance(result, str) and len(result.strip()) > 0

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