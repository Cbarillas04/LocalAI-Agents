from shared.ai_client import AIClient
from shared.web_search import WebSearch

class ResearchAgent:
    def __init__(self):
        self.ai = AIClient()
        self.web_search = WebSearch()
        # Assign agent behavior
        self.system_prompt = """
        You are a technical assistant.
        
        You responsbilities are to:
        - Explain technical concepts clearly.
        - Research and compare technologies approaches.
        - Break complex problems into manageble steps.
        - Distinguish established facts from assumptions.
        - Use the provided web search results when answering.
        - Cite sources using their titeles and urls.
        - Cite claims using numbered references such as [1], [2].
        - Never invent sources, citations, or facts.
        - State when supplied sources wasn't enough to generate a confident answer
        - Only respond in English
        
        Be accurate, structured and pratical.
        """

        # Store the conversations for each new chat
        self.conversation = [{
                "role" : "system",
                "content" : self.system_prompt
            }]

    def research(self, question):
        # Search for context
        search_results = self.web_search.search(
            query = question,
            max_results = 5
        )

        # Store each source with numbered ids
        self.search_sources = []
        for i, source in enumerate(search_results, start=1):
            self.search_sources.append({
                "id": i,
                "title": source['title'],
                "url": source['url'],
                "content": source['content']
            })

        # Format each k sites
        search_context = ""
        for site in self.search_sources:
            search_context += (f"Source ID: [{site['id']}]\n Source: {site['title']}\nURL: {site['url']}\nContent: {site['content']}\n\n")

        # Prompt the AI
        self.conversation.append({
                "role":"user",
                "content" : f"""
                    Question: {question}\n
                    Web search results: {search_context}\n
                """
            })

        # Resend conversation history to model
        response = self.ai.client.chat.completions.create(
            model =  self.ai.model,
            messages = self.conversation,
            temperature = 0.3
        )

        # Get answer
        answer = response.choices[0].message.content

        # Store the answer
        self.conversation.append({
                "role" : "assistant",
                "content" : answer
            })

        return {"answer": answer, "sources": self.search_sources}
