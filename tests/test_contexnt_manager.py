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