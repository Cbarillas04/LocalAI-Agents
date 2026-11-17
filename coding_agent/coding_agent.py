from shared.ai_client import AIClient

class CodingAgent:
    def __init__(self):
        self.ai = AIClient()
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