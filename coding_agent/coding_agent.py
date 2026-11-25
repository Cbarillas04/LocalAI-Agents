from shared.ai_client import AIClient
from coding_agent.project_manager import ProjectManager

class CodingAgent:
    def __init__(self, context_manager, conversation_manager):
        self.ai = AIClient()
        self.contexts = context_manager
        self.conversations = conversation_manager
        self.project = None
        self.conversation_id = None

        # behavior of the AI
        self.system_prompt = """
            You are a technical coding helper and teacher
            
            You are responsible for:
            - Explain programming concepts clearly.
            - Analyze code and identify bugs.
            - Suggest improvements and better practices.
            - Explain why each recommendations change is necessary.
            - Help design software architecture.
            - Generate code in response to requirements
            - Never claim to have modified or executed files unless our
                Python tools actually performed those actions.
            - Never directly modify files unless specifically prompted to.
            - Adapt explanations to the user's programming experience.
            - When teaching, explain the reasoning behind the implementation
        """

    # Get project summary of active open project
    def get_project_summary(self):
        if self.project is None or not self.project.validate_project():
            raise ValueError("No valid project is open")
        return self.project.get_project_summary()

    # Get all files by type
    def find_project_files(self, pattern):
        if self.project is None or not self.project.validate_project():
            raise ValueError("No valid project is open")
        return self.project.find_files(pattern)

    # Read a project file
    def read_project_file(self, file):
        if self.project is None or not self.project.validate_project():
            raise ValueError("No valid project is open")
        return self.project.read_file(file)

    # When supplied with a project root, assign project attribute
    def open_project(self, root):
        self.project = ProjectManager(root)
        if not self.project.validate_project():
            self.project = None
            raise ValueError("Project root is not valid")

    # Show project directory and file structure
    def get_project_tree(self):
        if self.project is None or not self.project.validate_project():
            raise ValueError("No valid project is open")
        return self.project.get_project_tree()

    # Read content and send to AI model to analyze, returns its analysis
    def analyze_file(self, file_path, question = None):
        result = self.read_project_file(file_path)
        if question is None:
            question = "Analyze the code, explain its purpose and functionality, identify potential bugs, and suggest improvements."
        prompt = f""" Question: {question}
                    Code:
                    {result}
                """
        return self.chat(prompt)

    # Create a conversation
    def create_conversation(self, title):
        conversation_id = self.conversations.create_conversation(title)
        self.conversation_id = conversation_id
        self.contexts.create_context(conversation_id)
        return conversation_id

    # Open a conversation
    def load_conversation(self, conversation_id):
        result = self.conversations.get_conversation(conversation_id)
        if result is None:
            raise ValueError("No conversation with that ID")

        self.conversation_id = conversation_id
        # ensure that context exists, otherwise it just creates one
        self.contexts.create_context(conversation_id)

        return result

    # Delete a conversation + its context
    def delete_conversation(self, conversation_id):
        result = self.conversations.get_conversation(conversation_id)
        if result is None:
            raise ValueError("No conversation with that ID")

        self.conversations.delete_conversation(conversation_id)
        self.contexts.delete_context(conversation_id)
        if self.conversation_id == conversation_id:
            self.conversation_id = None

    # Send the prompt to the AI to chat
    def chat(self, prompt):
        if self.conversation_id is None:
            self.create_conversation(prompt)

        # Create a message from the prompt
        self.conversations.create_message(self.conversation_id, "user", prompt)
        # Retrieve message history, add system prompt the beginning
        msg_history = self.conversations.get_messages(self.conversation_id)
        messages = [{
            "role": "system",
            "content": self.system_prompt,
        }]
        messages.extend([{
            "role": message[2],
            "content": message[3]
        } for message in msg_history]
        )

        # Send the messages to the AI
        response = self.ai.generate_response(messages)
        # Save the AI's response
        self.conversations.create_message(self.conversation_id, "assistant", response)

        return response