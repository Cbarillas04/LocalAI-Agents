class ContextManager:
    def __init__(
            self,
            context_window = 16384,
            max_response_tokens = 2500,
            context_safety_margin = 884,
            message_overhead = 5,
            request_overhead = 3
    ):
        # confirm all inputs valid integers
        self._check_positive_int("context_window", context_window)
        self._check_positive_int("max_response_tokens", max_response_tokens)
        self._check_positive_int("context_safety_margin", context_safety_margin)

        # defaults at 13k
        self.max_prompt_tokens = (context_window - max_response_tokens - context_safety_margin)
        if self.max_prompt_tokens <= 0:
            raise ValueError(
                "context_window must be larger than max_response_tokens + context_safety_margin"
            )

        # hold each conversation
        self.contexts = {}
        self.context_window = context_window
        self.max_response_tokens = max_response_tokens
        self.context_safety_margin = context_safety_margin
        self.message_overhead = message_overhead
        self.request_overhead = request_overhead

    # helper to check integer validation
    @staticmethod
    def _check_positive_int(name, value):
        # Since isinstance(value, int) can pass some bools
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{name} must be an int, got {type(value).__name__}")
        # not less than zero
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}")

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

    # Message selection for limiting tokens (messages: conversation history)
    def select_messages(self, sys_prompt, messages, token_counter):
        # Validate our system prompt isn't too large
        budget = self.max_prompt_tokens - token_counter(sys_prompt) - self.message_overhead - self.request_overhead
        if budget <= 0:
            raise ValueError("System prompt exceeds the prompt budget")

        selected_messages = []
        used = 0
        for i, message in enumerate(reversed(messages)):
            cost = token_counter(message["content"]) + self.message_overhead
            if used + cost > budget:
                if i == 0:
                    raise ValueError("Newest user message exceeds budget")
                break
            selected_messages.append(message)
            used += cost

        selected_messages.reverse()

        # pop for trimming
        while selected_messages and selected_messages[0]["role"] == "assistant":
            selected_messages.pop(0)

        return [
            {"role": "system", "content": sys_prompt},
        *selected_messages]