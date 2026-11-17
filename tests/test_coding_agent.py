from coding_agent.coding_agent import CodingAgent
from unittest.mock import patch, MagicMock

# Test 1: verify intialization
def test_coding_agent_init():
    with patch('coding_agent.coding_agent.AIClient') as mock_ai:
        agent = CodingAgent()

        assert agent.ai == mock_ai.return_value
        # conversation only has one msg
        assert len(agent.conversation) == 1
        # message contains prompt
        assert agent.conversation[0]["content"] == agent.system_prompt
        assert agent.conversation[0]["role"] == "system"

# Test 2: chat request returns an answer
def test_chat_success():
    with patch('coding_agent.coding_agent.AIClient') as mock_ai:
        agent = CodingAgent()

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Python is a programming language"
        mock_ai.return_value.client.chat.completions.create.return_value = mock_response
        mock_ai.return_value.model = "qwen2.5-coder-7b"

        result = agent.chat("What is Python?")
        call_args = mock_ai.return_value.client.chat.completions.create.call_args

        assert result["answer"] == "Python is a programming language"
        # verify model and temperature used
        assert call_args.kwargs["model"] == "qwen2.5-coder-7b"
        assert call_args.kwargs["temperature"] == 0.2
        # verify the user message was sent and recorded
        assert agent.conversation[1] == {
            "role": "user",
            "content": "What is Python?"
        }
        # verify the AI response made
        assert agent.conversation[2] == {
            "role": "assistant",
            "content": "Python is a programming language"
        }

# Test 3: Questions and answers are saved
def test_chat_conversation_history():
    with patch('coding_agent.coding_agent.AIClient') as mock_ai:
        agent = CodingAgent()

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Python is a programming language"
        mock_ai.return_value.client.chat.completions.create.return_value = mock_response
        # initial setup message (system)
        assert len(agent.conversation) == 1
        agent.chat("What is Python?")
        # number of messages after first search (sys, question, answer)
        assert len(agent.conversation) == 3
        agent.chat("What is Java?")
        # number of messages after second search
        # (sys, question, answer, question2, answer2)
        assert len(agent.conversation) == 5

        # Verify the conversation's order
        assert agent.conversation[1]["content"] == "What is Python?"
        assert agent.conversation[2]["content"] == "Python is a programming language"
        assert agent.conversation[3]["content"] == "What is Java?"
        assert agent.conversation[4]["content"] == "Python is a programming language"

