class ContextManager:
    def __init__(self):
        # hold each conversation
        self.contexts = {}

    # Create a conversation referenced by id #
    def create_context(self, conversation_id):
        if conversation_id not in self.contexts:
            self.contexts[conversation_id] = {
                "project": None,
                "active_file": None,
                "task": None
            }

    # Retrieve context from id #
    def get_context(self, conversation_id):
        return self.contexts[conversation_id]

    # Update value by key, raise KeyError if key does not exist
    def update_context(self, conversation_id, key, value):
        context = self.get_context(conversation_id)

        if key not in context:
            raise KeyError(f"Key {key} not found")

        context[key] = value

    # Delete context by id
    def delete_context(self, conversation_id):
        self.contexts.pop(conversation_id, None)

    # Retrieve specific context value
    def get_context_value(self, conversation_id, key):
        context = self.get_context(conversation_id)
        if key not in context:
            raise KeyError(f"Key {key} not found")
        return context[key]