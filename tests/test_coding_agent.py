import pytest
import shutil
from coding_agent.coding_agent import CodingAgent
from shared.context_manager import ContextManager
from shared.conversation_manager import ConversationManager
from unittest.mock import patch, MagicMock

# Test 1: verify intialization
def test_coding_agent_init(tmp_path):
    with patch('coding_agent.coding_agent.AIClient') as mock_ai:
        context_manager = ContextManager()
        conversation_manager = ConversationManager(tmp_path / "test.db")

        agent = CodingAgent(context_manager, conversation_manager)

        assert agent.ai == mock_ai.return_value
        # conversation only has one msg
        assert len(agent.conversation) == 1
        # message contains prompt
        assert agent.conversation[0]["content"] == agent.system_prompt
        assert agent.conversation[0]["role"] == "system"

# Test 2: chat request returns an answer
def test_chat_success(tmp_path):
    with patch('coding_agent.coding_agent.AIClient') as mock_ai:
        context_manager = ContextManager()
        conversation_manager = ConversationManager(tmp_path / "test.db")

        agent = CodingAgent(context_manager, conversation_manager)

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
def test_chat_conversation_history(tmp_path):
    with patch('coding_agent.coding_agent.AIClient') as mock_ai:
        context_manager = ContextManager()
        conversation_manager = ConversationManager(tmp_path / "test.db")

        agent = CodingAgent(context_manager, conversation_manager)

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

# Test 4: Adds a valid project when root is valid
def test_open_project_success(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    test_dir = tmp_path / "Project"
    test_dir.mkdir()
    agent.open_project(test_dir)
    assert agent.project.root == test_dir.resolve()

# Test 5: ValueError on invalid root
def test_open_project_failure(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    test_file = tmp_path / "Project"

    with pytest.raises(ValueError):
        agent.open_project(test_file)
    assert agent.project is None

# Test 6: Gets and returns summary of an opened project
def test_get_project_summary_success(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)

    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    (test_dir / "main.py").write_text("print('Hello')")
    (test_dir / "helper.py").write_text("print('Helper')")
    (test_dir / "README.txt").write_text("Project description")

    agent.open_project(test_dir)
    result = agent.get_project_summary()

    assert result == {
        "total_files": 3,
        "total_directories": 0,
        "file_types": {
            ".py": 2,
            ".txt": 1
        }
    }

# Test 7: ValueError when no project is open
def test_get_project_summary_no_project(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    with pytest.raises(ValueError):
        agent.get_project_summary()

# Test 8: Raise ValueError when project directory is removed
def test_get_project_summary_invalid_project(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    agent.open_project(test_dir)
    # delete directory
    shutil.rmtree(test_dir)

    with pytest.raises(ValueError):
        agent.get_project_summary()

#Test 9: Returns only the file of requested file type
def test_find_project_files_by_pattern(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    (test_dir / "main.py").write_text("print('Hello')")
    (test_dir / "helper.py").write_text("print('Helper')")
    (test_dir / "README.txt").write_text("Project description")

    agent.open_project(test_dir)

    result = agent.find_project_files("*.py")

    assert len(result) == 2
    assert all(file.suffix == ".py" for file in result)

# Test 10: Verifies empty list on return when no matching files
def test_find_project_files_no_matches(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    (test_dir / "main.py").write_text("print('Hello')")

    agent.open_project(test_dir)

    result = agent.find_project_files("*.json")

    assert result == []

# Test 11: ValueError when no project opened
def test_find_project_files_no_project(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    with pytest.raises(ValueError):
        agent.find_project_files("*.py")

# Test 12: file was read without issues
def test_read_project_file_success(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    test_file = test_dir / "main.py"
    test_file.write_text("print('Hello World')")

    agent.open_project(test_dir)
    result = agent.read_project_file(test_file)

    assert result == "print('Hello World')"

# Test 13: ValuError when a file doesn't exist
def test_read_project_file_missing(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    agent.open_project(test_dir)

    with pytest.raises(ValueError):
        agent.read_project_file(test_dir / "missing.py")

# Test 14: ValuerError when trying to read a file outside of project
def test_read_project_file_foreign(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    foreign_file = tmp_path / "outside.py"
    foreign_file.write_text("print('Outside')")

    agent.open_project(test_dir)

    with pytest.raises(ValueError):
        agent.read_project_file(foreign_file)

# Test 15: ValueError when no project is open
def test_read_project_file_no_project(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)

    with pytest.raises(ValueError):
        agent.read_project_file("main.py")

# Test 16: Retrieve the project tree successfully
def test_get_project_tree_success(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    (test_dir / "main.py").write_text("print('Hello')")
    src = test_dir / "src"
    src.mkdir()
    (src / "helper.py").write_text("print('Helper')")

    agent.open_project(test_dir)

    result = agent.get_project_tree()
    expected = {
        "main.py",
        "src/",
        "src/helper.py"
    }
    assert set(result) == expected

# Test 17: ValueError when no opened project
def test_get_project_tree_no_project(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    with pytest.raises(ValueError):
        agent.get_project_tree()

# Test 18: valueError when invalid/removed directory
def test_get_project_tree_invalid_project(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    agent.open_project(test_dir)
    shutil.rmtree(test_dir)

    with pytest.raises(ValueError):
        agent.get_project_tree()

# Test 19: Test question is successfully prompted to AI
def test_analyze_file_success(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    test_file = test_dir / "main.py"
    test_file.write_text("print('Hello World')")

    agent.open_project(test_dir)

    # Mock prompt the AI
    with patch.object(agent, "chat", return_value = {"answer": "Bug analysis"}) as mock_chat:
        result = agent.analyze_file(test_file, "Find the bugs in this code")

    prompt = mock_chat.call_args[0][0]
    assert result == {"answer": "Bug analysis"}
    assert "Find the bugs in this code" in prompt
    assert "Analyze the code" not in prompt

# Test 20: Missing file raises a ValueError
def test_analyze_file_missing(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    agent.open_project(test_dir)
    with pytest.raises(ValueError):
        agent.analyze_file(test_dir / "missing.py")

# Test 21: Raises ValueError when trying to analyze outside file
def test_analyze_file_foreign(tmp_path):
    context_manager = ContextManager()
    conversation_manager = ConversationManager(tmp_path / "test.db")

    agent = CodingAgent(context_manager, conversation_manager)
    test_dir = tmp_path / "project"
    test_dir.mkdir()

    foreign_file = tmp_path / "outside.py"
    foreign_file.write_text("print('Outside')")

    agent.open_project(test_dir)
    with pytest.raises(ValueError):
        agent.analyze_file(foreign_file)

# Test 22: Creates a
def test_create_conversation(tmp_path):
    db_path = tmp_path / "conversation.db"
    context_manager = ContextManager()
    conversation_manager = ConversationManager(db_path)

    agent = CodingAgent(context_manager, conversation_manager)

    result = agent.create_conversation("Test conversation")

    assert isinstance(result, int)
    assert agent.conversation_id == result
    context = context_manager.get_context(result)
    assert context == {
        "project": None,
        "active_file": None,
        "task": None
    }
    # Conversation holds
    conversation = conversation_manager.get_conversation(result)
    assert conversation[0] == result
    assert conversation[1] == "Test conversation"