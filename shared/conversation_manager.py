from shared.database import DatabaseManager
from datetime import datetime

class ConversationManager:
    def __init__(self, db_path = None):
        self.db_manager = DatabaseManager(db_path)
        with self.db_manager.connection() as connection:
            # Create a conversations table
            connection.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            # Create a messages table
            connection.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id NOT NULL,
                    role TEXT,
                    content TEXT,
                    created_at TEXT,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                )
            """)

    # create a new conversation
    def create_conversation(self, title):
        current_time = datetime.now().isoformat()
        with self.db_manager.connection() as connection:
            cursor = connection.execute(
                "INSERT INTO conversations (title, created_at, updated_at) VALUES (?, ?, ?)",
                (title, current_time, current_time))
            last_id = cursor.lastrowid
        return last_id

    # Create a new message
    def create_message(self, conversation_id, role, content):
        current_time = datetime.now().isoformat()
        with self.db_manager.connection() as connection:
            connection.execute(
                "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, current_time))

            # Update the "updated_at" in conversation
            connection.execute("""
                UPDATE conversations
                SET updated_at = ?
                WHERE id = ?        
            """, (current_time, conversation_id))

    # Get a conversation
    def get_conversation(self, conversation_id):
        with self.db_manager.connection() as connection:
            cursor = connection.execute("""
                SELECT * FROM conversations 
                WHERE id = ?
            """,(conversation_id,))
            conversation = cursor.fetchone()
        return conversation

    # Get messages from messages table
    def get_messages(self, conversation_id):
        with self.db_manager.connection() as connection:
            cursor = connection.execute("""
                SELECT * FROM messages 
                WHERE conversation_id = ?
                ORDER BY created_at ASC, id ASC
            """,(conversation_id,))

            messages = cursor.fetchall()
        return messages

    # Get all conversations
    def get_all_conversations(self):
        with self.db_manager.connection() as connection:
            cursor = connection.execute("""
                SELECT * FROM conversations
                ORDER BY updated_at DESC
            """)
            cursor = cursor.fetchall()
        return cursor

    # Update a conversation title
    def update_conversation_title(self, conversation_id, title):
        current_time = datetime.now().isoformat()
        with self.db_manager.connection() as connection:
            connection.execute("""
                UPDATE conversations
                SET title = ?, updated_at = ?
                WHERE id = ?
            """,(title, current_time, conversation_id))

    # Delete a conversation
    def delete_conversation(self, conversation_id):
        with self.db_manager.connection() as connection:
            # Delete messages first, because of foreign key
            connection.execute(
                "DELETE FROM messages WHERE conversation_id = ?", (conversation_id,)
            )
            # Delete conversation
            connection.execute(
                "DELETE FROM conversations WHERE id = ?",(conversation_id,)
            )