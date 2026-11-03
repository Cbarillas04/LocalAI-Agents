from shared.ai_client import AIClient

class ResearchAgent:
    def __init__(self):
        self.ai = AIClient()
        # Assign agent behavior
        self.system_prompt = """
        You are a technical assistant.
        
        You responsbilities are to:
        - Explain technical concepts clearly.
        - Research and compare technologies approaches.
        - Break complex problems into manageble steps.
        - Distinguish established facts from assumptions.
        - Never invent sources, citations, or facts.
        
        Be accurate, structured and pratical.
        """

        # Store the conversations for each new chat
        self.conversation = [
            {
                "role" : "system",
                "content" : self.system_prompt
            }
        ]

    def research(self, question):
        self.conversation.append(
            {
                "role":"user",
                "content" : question
            }
        )

        # Resend conversation history to model
        response = self.ai.client.chat.completions.create(
            model =  self.ai.model,
            messages = self.conversation,
            temperature = 0.3
        )

        # Get answer
        answer = response.choices[0].message.content

        # Store the answer
        self.conversation.append(
            {
                "role" : "assistant",
                "content" : answer
            }
        )

        return answer