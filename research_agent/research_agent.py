import re
from shared.ai_client import AIClient
from shared.web_search import WebSearch

class ResearchAgent:
    def __init__(self):
        self.search_sources = None
        self.ai = AIClient()
        self.web_search = WebSearch()
        # Assign agent behavior
        self.system_prompt = """
        You are a technical assistant.
        
        You responsibilities are to:
        - Explain technical concepts clearly.
        - Research and compare technologies approaches.
        - Break complex problems into manageable steps.
        - Distinguish established facts from assumptions.
        - Use the provided web search results when answering.
        - Cite sources using their titles and urls.
        - Cite claims using numbered references such as [1], [2].
        - Never invent sources, citations, or facts.
        - State when supplied sources wasn't enough to generate a confident answer
        - Only respond in English
        
        Be accurate and structured.
        """

        # Store the conversations for each new chat
        self.conversation = [{
                "role" : "system",
                "content" : self.system_prompt
            }]

    # Validate that all Ai-gen citations are connected to a valid citation
    # Returns dictionary {Valid?, invalid list}
    def validate(self, answer):
        # getting generated citation ids
        rexp = []
        for group in re.findall(r"\[(\d+(?:,\s*\d+)*)\]", answer):
            for citation in group.split(","):
                rexp.append(citation.strip())

        # Valid citations
        valid_ids = []
        for source in self.search_sources:
            valid_ids.append(str(source["id"]))

        # Validating the generated citations
        invalid_ids = []
        for cite in rexp:
            if cite not in valid_ids:
                invalid_ids.append(cite)
                
        isValid = True
        if invalid_ids:
            isValid = False
        return {"is_valid": isValid, "invalid_ids": invalid_ids}

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
            search_context += (f"""
                Source ID: [{site['id']}]\n
                Source: {site['title']}\n
                URL: {site['url']}\n
                Content: {site['content']}\n
            \n""")

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

        # Validate citations
        citations = self.validate(answer)

        # Store the answer
        self.conversation.append({
                "role" : "assistant",
                "content" : answer
            })

        return {
            "answer": answer,
            "sources": self.search_sources,
            "citation_validation": citations
        }
