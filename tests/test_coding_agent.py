import pytest
import shutil
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

# Test 4: Adds a valid project when root is valid
def test_open_project_success(tmp_path):
    agent = CodingAgent()
    test_dir = tmp_path / "Project"
    test_dir.mkdir()
    agent.open_project(test_dir)
    assert agent.project.root == test_dir.resolve()

# Test 5: ValueError on invalid root
def test_open_project_failure(tmp_path):
    agent = CodingAgent()
    test_file = tmp_path / "Project"

    with pytest.raises(ValueError):
        agent.open_project(test_file)
    assert agent.project is None

# Test 6: Gets and returns summary of an opened project
def test_get_project_summary_success(tmp_path):
    agent = CodingAgent()

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
def test_get_project_summary_no_project():
    agent = CodingAgent()
    with pytest.raises(ValueError):
        agent.get_project_summary()

# Test 8: Raise ValueError when project directory is removed
def test_get_project_summary_invalid_project(tmp_path):
    agent = CodingAgent()
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    agent.open_project(test_dir)
    # delete directory
    shutil.rmtree(test_dir)

    with pytest.raises(ValueError):
        agent.get_project_summary()

#Test 9: Returns only the file of requested file type
def test_find_project_files_by_pattern(tmp_path):
    agent = CodingAgent()
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
    agent = CodingAgent()
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    (test_dir / "main.py").write_text("print('Hello')")

    agent.open_project(test_dir)

    result = agent.find_project_files("*.json")

    assert result == []

# Test 11: ValueError when no project opened
def test_find_project_files_no_project():
    agent = CodingAgent()
    with pytest.raises(ValueError):
        agent.find_project_files("*.py")

# Test 12: file was read without issues
def test_read_project_file_success(tmp_path):
    agent = CodingAgent()
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    test_file = test_dir / "main.py"
    test_file.write_text("print('Hello World')")

    agent.open_project(test_dir)
    result = agent.read_project_file(test_file)

    assert result == "print('Hello World')"

# Test 13: ValuError when a file doesn't exist
def test_read_project_file_missing(tmp_path):
    agent = CodingAgent()
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    agent.open_project(test_dir)

    with pytest.raises(ValueError):
        agent.read_project_file(test_dir / "missing.py")

# Test 14: ValuerError when trying to read a file outside of project
def test_read_project_file_foreign(tmp_path):
    agent = CodingAgent()
    test_dir = tmp_path / "Project"
    test_dir.mkdir()

    foreign_file = tmp_path / "outside.py"
    foreign_file.write_text("print('Outside')")

    agent.open_project(test_dir)

    with pytest.raises(ValueError):
        agent.read_project_file(foreign_file)

# Test 15: ValueError when no project is open
def test_read_project_file_no_project():
    agent = CodingAgent()

    with pytest.raises(ValueError):
        agent.read_project_file("main.py")