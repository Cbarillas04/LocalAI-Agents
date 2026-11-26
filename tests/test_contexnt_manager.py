import pytest
from shared.context_manager import ContextManager

# Test 1: initializes contexts dictionary to empty
def test_context_manager_init():
    manager = ContextManager()
    assert manager.contexts == {}

# Test 2: Creates a new conversation
def test_create_context():
    manager = ContextManager()
    manager.create_context("conversation_1")

    assert manager.contexts["conversation_1"] == {
        "project": None,
        "active_file": None,
        "task": None
    }

# Test 3: Making the same conversation twice will not overwrite
def test_create_context_already_exists():
    manager = ContextManager()

    manager.create_context("conversation_1")
    manager.update_context("conversation_1", "project", "MyProject")
    manager.create_context("conversation_1")

    assert manager.contexts["conversation_1"]["project"] == "MyProject"

# Test 4: Retrieve conversation values
def test_get_context():
    manager = ContextManager()

    manager.create_context("conversation_1")
    result = manager.get_context("conversation_1")

    assert result == {
        "project": None,
        "active_file": None,
        "task": None
    }

# Test 5: KeyError if context doesn't exist
def test_get_context_missing():
    manager = ContextManager()

    with pytest.raises(KeyError):
        manager.get_context("conversation_1")

# Test 6: Conversation values can be updated
def test_update_context():
    manager = ContextManager()

    manager.create_context("conversation_1")
    manager.update_context("conversation_1", "project", "MyProject")

    assert manager.contexts["conversation_1"]["project"] == "MyProject"

# Test 7: KeyError if attempting to update key thats non-existent
def test_update_context_missing_conversation():
    manager = ContextManager()

    with pytest.raises(KeyError):
        manager.update_context("conversation_1", "project", "MyProject")

# Test 8: Returns key value
def test_get_context_value():
    manager = ContextManager()

    manager.create_context("conversation_1")
    manager.update_context("conversation_1", "project", "MyProject")

    result = manager.get_context_value("conversation_1", "project")

    assert result == "MyProject"

# Test 9: KeyError if attempting to nonexistent conversation
def test_get_context_value_missing_conversation():
    manager = ContextManager()

    with pytest.raises(KeyError):
        manager.get_context_value("conversation_1", "project")

# Test 10: KeyError if attempting to get key value
def test_get_context_value_missing_key():
    manager = ContextManager()

    manager.create_context("conversation_1")

    with pytest.raises(KeyError):
        manager.get_context_value("conversation_1", "invalid_key")

# Test 11: Successfully deletes a conversation
def test_delete_context():
    manager = ContextManager()

    manager.create_context("conversation_1")
    manager.delete_context("conversation_1")

    assert "conversation_1" not in manager.contexts

# Test 12: No error raised if the conversation doesn't exist.
def test_delete_context_missing():
    manager = ContextManager()
    manager.delete_context("conversation_1")

    assert manager.contexts == {}

# Helper for tests 13 - 20
def mock_token_counter(content):
    return len(content)

# Test 13: All conversation messages are included when they fit
def test_select_messages_all_fit():
    manager = ContextManager()

    sys_prompt = "You are a coding assistant."
    messages = [
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language."},
        {"role": "user", "content": "What is a variable?"}
    ]
    results  = manager.select_messages(sys_prompt, messages, mock_token_counter)

    assert len(results) == 4
    assert results[0]["content"] == "You are a coding assistant."
    assert results[1]["content"] == "What is Python?"
    assert results[2]["content"] == "Python is a programming language."
    assert results[3]["content"] == "What is a variable?"
    assert results[0]["role"] == "system"
    assert results[1]["role"] == "user"
    assert results[2]["role"] == "assistant"
    assert results[3]["role"] == "user"

# Test 14: Older messages get trimmed when budget is exceeded
def test_select_messages_trims_oldest():
    manager = ContextManager(40, 5, 5, 4, 0)

    sys_prompt = "System"
    messages = [
        {"role": "user", "content": "Old question"},
        {"role": "assistant", "content": "Old answer"},
        {"role": "user", "content": "New question"}
    ]

    results = manager.select_messages(sys_prompt, messages, mock_token_counter)

    assert len(results) == 2
    assert results[0]["role"] == "system"
    assert results[1]["content"] == "New question"

# Test 15:ValueError when newest message can't fit
def test_select_messages_latest_large():
    manager = ContextManager(20, 5, 5)

    sys_prompt = "s"
    messages = [
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language."},
        {"role": "user", "content": "What is a variable?"}
    ]

    with pytest.raises(ValueError):
        manager.select_messages(sys_prompt, messages, mock_token_counter)

# Test 16: Successfully passes when message fills exact budget
def test_select_messages_exact_budget():
    manager = ContextManager(20, 5, 5, 4, 0)
    manager.message_overhead = 4

    sys_prompt = "s"
    messages = [
        {"role": "user", "content": "a"}
    ]

    results = manager.select_messages(sys_prompt, messages, mock_token_counter)

    assert results == [
        {"role": "system", "content": "s"},
        {"role": "user", "content": "a"}
    ]

# Test 17: Returned messages are still in order
def test_select_messages_preserves_order():
    manager = ContextManager()
    manager.message_overhead = 4

    sys_prompt = "s"
    messages = [
        {"role": "user", "content": "First"},
        {"role": "assistant", "content": "Second"},
        {"role": "user", "content": "Third"}
    ]

    results = manager.select_messages(sys_prompt, messages, mock_token_counter)

    assert results[1:] == messages

# Test 18: Messages returned don't start with an assistant response
def test_select_messages_removes_leading_assistant():
    manager = ContextManager(40, 5, 5)
    manager.message_overhead = 4

    sys_prompt = "s"
    messages = [
        {"role": "user", "content": "Old question"},
        {"role": "assistant", "content": "a"},
        {"role": "user", "content": "b"}
    ]

    results = manager.select_messages(sys_prompt, messages, mock_token_counter)

    assert results == [
        {"role": "system", "content": "s"},
        {"role": "user", "content": "b"}
    ]

# Test 19: ValueError when system has no usable budget
def test_select_messages_sys_prompt_large():
    manager = ContextManager(20, 5, 5)
    manager.message_overhead = 4

    sys_prompt = "This system prompt is too large"
    messages = []

    with pytest.raises(ValueError):
        manager.select_messages(
            sys_prompt, messages, mock_token_counter
        )

# Test 20: Only returns system prompt if no messages exist
def test_select_messages_empty_history():
    manager = ContextManager()
    manager.message_overhead = 4

    sys_prompt = "System"
    messages = []

    results = manager.select_messages(sys_prompt, messages, mock_token_counter)

    assert results == [
        {"role": "system", "content": "System"}
    ]