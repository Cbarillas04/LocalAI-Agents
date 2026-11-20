from shared.ai_client import AIClient
from coding_agent.project_manager import ProjectManager

class CodingAgent:
    def __init__(self):
        self.ai = AIClient()
        self.project = None
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

        # Store the conversations for each new chat
        self.conversation = [{
            "role": "system",
            "content": self.system_prompt
        }]

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

    # Send the prompt to the AI to have a chat
    def chat(self, prompt):
        # Prompt the AI
        self.conversation.append({
            "role": "user",
            "content": prompt
        })

        # Resend conversation history to model
        response = self.ai.client.chat.completions.create(
            model = self.ai.model,
            messages = self.conversation,
            temperature = 0.2
        )
        # Get the answer
        answer = response.choices[0].message.content

        self.conversation.append({
            "role": "assistant",
            "content": answer
        })

        return {
            "answer": answer
        }