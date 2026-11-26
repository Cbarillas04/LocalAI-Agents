import pytest
import shutil

from openai.lib.beta.agents import agent_text_format

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
        # verify system prompt exists
        assert agent.system_prompt is not None
        assert len(agent.system_prompt) > 0

# Test 2: Chat request returns an answer
def test_chat_success(tmp_path):
    with patch('coding_agent.coding_agent.AIClient') as mock_ai:
        context_manager = ContextManager()
        conversation_manager = ConversationManager(tmp_path / "test.db")

        agent = CodingAgent(context_manager, conversation_manager)

        mock_ai.return_value.generate_response.return_value = (
            "Python is a programming language"
        )
        mock_ai.return_value.count_tokens.side_effect = len

        result = agent.chat("What is Python?")
        messages = mock_ai.return_value.generate_response.call_args.args[0]
        msg_history = conversation_manager.get_messages(agent.conversation_id)

        assert result == "Python is a programming language"
        # System prompt was sent
        assert messages[0] == {
            "role": "system",
            "content": agent.system_prompt
        }
        # User message was sent and recorded
        assert messages[1] == {
            "role": "user",
            "content": "What is Python?"
        }
        assert msg_history[0][2] == "user"
        assert msg_history[0][3] == "What is Python?"
        assert msg_history[1][2] == "assistant"
        assert msg_history[1][3] == "Python is a programming language"
        assert mock_ai.return_value.count_tokens.called

# Test 3: Questions and answers are saved
def test_chat_conversation_history(tmp_path):
    with patch('coding_agent.coding_agent.AIClient') as mock_ai:
        context_manager = ContextManager()
        conversation_manager = ConversationManager(tmp_path / "test.db")

        agent = CodingAgent(context_manager, conversation_manager)
        mock_ai.return_value.generate_response.side_effect = [
            "Python is a programming language",
            "Java is another programming language"
        ]
        mock_ai.return_value.count_tokens.side_effect = len

        # Initial setup (no messages)
        assert agent.conversation_id is None

        agent.chat("What is Python?")

        # Number of messages after first chat (question, answer)
        msg_history = conversation_manager.get_messages(agent.conversation_id)
        assert len(msg_history) == 2

        agent.chat("What is Java?")

        # Number of messages after second chat
        # (question1, answer1, question2, answer2)
        msg_history = conversation_manager.get_messages(agent.conversation_id)
        assert len(msg_history) == 4

        # Verify the conversation's order
        assert msg_history[0][2] == "user"
        assert msg_history[0][3] == "What is Python?"
        assert msg_history[1][2] == "assistant"
        assert msg_history[1][3] == "Python is a programming language"
        assert msg_history[2][2] == "user"
        assert msg_history[2][3] == "What is Java?"
        assert msg_history[3][2] == "assistant"
        assert msg_history[3][3] == "Java is another programming language"

        # Verify the system prompt and history were sent on the second request
        messages = mock_ai.return_value.generate_response.call_args_list[1].args[0]
        assert len(messages) == 4
        assert messages[0]["role"] == "system"
        assert messages[1]["content"] == "What is Python?"
        assert messages[2]["content"] == "Python is a programming language"
        assert messages[3]["content"] == "What is Java?"
        assert mock_ai.return_value.count_tokens.call_count > 0

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

# Test 23: Tests a conversation is opened and loaded
def test_load_conversation(tmp_path):
    db_path = tmp_path / "conversation.db"
    context_manager = ContextManager()
    conversation_manager = ConversationManager(db_path)

    agent = CodingAgent(context_manager, conversation_manager)

    last_id = agent.create_conversation("Test conversation")
    result = agent.load_conversation(last_id)
    context = context_manager.get_context(last_id)

    assert context == {
        "project": None,
        "active_file": None,
        "task": None
    }
    assert agent.conversation_id == last_id
    assert result[1] == "Test conversation"

# Test 24: Value error raised when non-existent conversation is inputted
def test_load_conversation_failure(tmp_path):
    db_path = tmp_path / "conversation.db"
    context_manager = ContextManager()
    conversation_manager = ConversationManager(db_path)

    agent = CodingAgent(context_manager, conversation_manager)

    with pytest.raises(ValueError, match = "No conversation with that ID"):
        agent.load_conversation(1)

    assert agent.conversation_id is None

# Test 25: Existing context is not overwritten when a loading conversation
def test_load_conversation_preserves_context(tmp_path):
    db_path = tmp_path / "conversation.db"
    context_manager = ContextManager()
    conversation_manager = ConversationManager(db_path)

    agent = CodingAgent(context_manager, conversation_manager)

    last_id = agent.create_conversation("Test conversation")
    context_manager.update_context(
        last_id, "project", "C:/Projects/TestProject"
    )

    agent.load_conversation(last_id)
    context = context_manager.get_context(last_id)

    assert context["project"] == "C:/Projects/TestProject"

# Test 26: Successfully deletes a conversation
def test_delete_conversation(tmp_path):
    db_path = tmp_path / "conversation.db"
    context_manager = ContextManager()
    conversation_manager = ConversationManager(db_path)

    agent = CodingAgent(context_manager, conversation_manager)
    last_id = agent.create_conversation("Test conversation")
    agent.delete_conversation(last_id)

    assert conversation_manager.get_conversation(last_id) is None
    assert agent.conversation_id is None
    with pytest.raises(KeyError):
        context_manager.get_context(last_id)

# Test 27: ValueError when deleting a nonexistent conversation
def test_delete_conversation_failure(tmp_path):
    db_path = tmp_path / "conversation.db"
    context_manager = ContextManager()
    conversation_manager = ConversationManager(db_path)

    agent = CodingAgent(context_manager, conversation_manager)

    with pytest.raises(ValueError, match="No conversation with that ID"):
        agent.delete_conversation(1)
    assert agent.conversation_id is None

# Test 28: Deleting inactive conversation doesn't affect the active
def test_delete_conversation_inactive(tmp_path):
    db_path = tmp_path / "conversation.db"
    context_manager = ContextManager()
    conversation_manager = ConversationManager(db_path)

    agent = CodingAgent(context_manager, conversation_manager)
    convo_one_id = agent.create_conversation("Conversation 1")
    convo_two_id = agent.create_conversation("Conversation 2")

    # Keepy 2nd conversation active
    agent.load_conversation(convo_two_id)
    agent.delete_conversation(convo_one_id)

    assert conversation_manager.get_conversation(convo_one_id) is None
    assert agent.conversation_id == convo_two_id
    assert conversation_manager.get_conversation(convo_two_id)[1] == "Conversation 2"