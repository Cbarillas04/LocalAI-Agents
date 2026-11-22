from datetime import datetime
from shared.conversation_manager import ConversationManager
from shared.database import DatabaseManager


# Test 1: correctly initialize class
def test_conversation_manager_init(tmp_path):
    db_path = tmp_path / 'conversation.db'
    convo_manager = ConversationManager(db_path)
    assert isinstance(convo_manager.db_manager, DatabaseManager)

# Test 2: initializing conversation class creates both tables
def test_conversation_tables_created(tmp_path):
    db_path = tmp_path / 'conversation.db'
    ConversationManager(db_path)
    db_manager = DatabaseManager(db_path)
    with db_manager.connection() as connection:
        cursor = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
        result = cursor.fetchall()

    table_names = [row[0] for row in result]

    assert "conversations" in table_names
    assert "messages" in table_names

# Test 3: Conversation is successfully created
def test_create_conversation(tmp_path):
    db_path = tmp_path / 'conversation.db'
    convo_manager = ConversationManager(db_path)
    db_manager = DatabaseManager(db_path)

    test_id = convo_manager.create_conversation("test")
    with db_manager.connection() as connection:
        cursor = connection.execute(
            "SELECT * FROM conversations WHERE id = ?", (test_id,)
        )
        result = cursor.fetchone()

    assert result[0] == test_id
    assert result[1] == "test"
    assert result[2] is not None
    assert result[3] is not None

# Test 4: Message is created successfully
def test_create_message(tmp_path):
    db_path = tmp_path / 'conversation.db'
    convo_manager = ConversationManager(db_path)
    db_manager = DatabaseManager(db_path)

    test_id = convo_manager.create_conversation("test")
    convo_manager.create_message(test_id, "user","Hello World")

    with db_manager.connection() as connection:
        cursor = connection.execute(
            "SELECT * FROM messages WHERE conversation_id = ?", (test_id,)
        )
        messages = cursor.fetchall()

    assert messages[0][0] > 0
    assert messages[0][1] == test_id
    assert messages[0][2] == "user"
    assert messages[0][3] == "Hello World"
    assert messages[0][4] is not None

# Test 5: Successfully get messages
def test_get_messages(tmp_path):
    db_path = tmp_path / "conversation.db"
    convo_manager = ConversationManager(db_path)

    test_id = convo_manager.create_conversation("test")
    convo_manager.create_message(test_id, "user", "Hello")
    convo_manager.create_message(test_id, "assistant", "Hello! How can I help?")

    messages = convo_manager.get_messages(test_id)

    assert len(messages) == 2
    assert messages[0][1] == test_id
    assert messages[0][2] == "user"
    assert messages[0][3] == "Hello"
    assert messages[1][1] == test_id
    assert messages[1][2] == "assistant"
    assert messages[1][3] == "Hello! How can I help?"

# Test 6: Get message from empty conversation
def test_get_messages_empty(tmp_path):
    db_path = tmp_path / "conversation.db"
    convo_manager = ConversationManager(db_path)

    test_id = convo_manager.create_conversation("test")
    messages = convo_manager.get_messages(test_id)

    assert messages == []

# Test 7:
def test_get_conversation(tmp_path):
    db_path = tmp_path / "conversation.db"
    convo_manager = ConversationManager(db_path)

    test_id = convo_manager.create_conversation("test")
    conversation = convo_manager.get_conversation(test_id)

    assert conversation is not None
    assert conversation[0] == test_id
    assert conversation[1] == "test"
    assert conversation[2]
    assert conversation[3]

# Test 8: attempt to retrieve nonexistent conversation
def test_get_conversation_missing(tmp_path):
    db_path = tmp_path / "conversation.db"
    convo_manager = ConversationManager(db_path)

    conversation = convo_manager.get_conversation(999)

    assert conversation is None

# Test 9: Get all conversations
def test_get_all_conversations(tmp_path):
    db_path = tmp_path / "conversation.db"
    convo_manager = ConversationManager(db_path)

    first_id = convo_manager.create_conversation("First")
    second_id = convo_manager.create_conversation("Second")
    third_id = convo_manager.create_conversation("Third")

    conversations = convo_manager.get_all_conversations()

    assert len(conversations) == 3
    assert conversations[0][0] == third_id
    assert conversations[1][0] == second_id
    assert conversations[2][0] == first_id

# Test 10: Update a conversation title
def test_update_conversation_title(tmp_path):
    db_path = tmp_path / "conversation.db"
    convo_manager = ConversationManager(db_path)

    test_id = convo_manager.create_conversation("Old title")
    original = convo_manager.get_conversation(test_id)

    convo_manager.update_conversation_title(test_id, "New title")
    updated = convo_manager.get_conversation(test_id)

    assert updated[1] == "New title"
    assert updated[3] >= original[3]

# Test 11: Attempt to update a title to a non-existent conversation
def test_update_conversation_title_missing(tmp_path):
    db_path = tmp_path / "conversation.db"
    convo_manager = ConversationManager(db_path)

    convo_manager.update_conversation_title(999, "New title")

    assert convo_manager.get_conversation(999) is None

# Test 12: Adding a message to a conversation updates the timestamp in conversation table
def test_create_message_updates_conversation_timestamp(tmp_path):
    db_path = tmp_path / "conversation.db"
    convo_manager = ConversationManager(db_path)

    test_id = convo_manager.create_conversation("test")
    original = convo_manager.get_conversation(test_id)

    convo_manager.create_message(test_id, "user", "Hello")
    updated = convo_manager.get_conversation(test_id)

    assert updated[3] >= original[3]

# Test 13: Conversation deletion is successful
def test_delete_conversation(tmp_path):
    db_path = tmp_path / "conversation.db"
    convo_manager = ConversationManager(db_path)

    test_id = convo_manager.create_conversation("test")
    convo_manager.create_message(test_id, "user", "Hello")
    convo_manager.delete_conversation(test_id)

    assert convo_manager.get_conversation(test_id) is None
    assert convo_manager.get_messages(test_id) == []

# Test 14: Attempt to delete a non-existent conversation
def test_delete_conversation_missing(tmp_path):
    db_path = tmp_path / "conversation.db"
    convo_manager = ConversationManager(db_path)
    convo_manager.delete_conversation(999)

    assert convo_manager.get_conversation(999) is None
    assert convo_manager.get_messages(999) == []