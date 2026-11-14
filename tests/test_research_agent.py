from research_agent.research_agent import ResearchAgent
from unittest.mock import patch, MagicMock

# Test 1: verify agent initialization
def test_research_agent_init():
    with patch('research_agent.research_agent.AIClient') as mock_ai, \
        patch('research_agent.research_agent.WebSearch') as mock_search:

        research = ResearchAgent()

        assert research.search_sources is None
        assert research.ai == mock_ai.return_value
        assert research.web_search == mock_search.return_value
        # convo has only one message
        assert len(research.conversation) == 1
        # message contains prompt
        assert research.conversation[0]["content"] == research.system_prompt

# Test 2: valid citations pass
def test_research_citation_valid():
    with patch('research_agent.research_agent.AIClient'), \
        patch('research_agent.research_agent.WebSearch'):

        research = ResearchAgent()
        research.search_sources = [{"id": 1}, {"id": 2}, {"id": 3}]
        result = research.validate("""
            This answer [1] is contained the numbers used.
            Here is another use [2, 3].
        """)
        # Assure all ids are valid
        assert result["is_valid"] == True
        assert result["invalid_ids"] == []

# Test 3: Catches invalid citations
def test_research_citation_invalid():
    with patch('research_agent.research_agent.AIClient'), \
        patch('research_agent.research_agent.WebSearch'):
        research = ResearchAgent()
        research.search_sources = [{"id": 1}, {"id": 2}, {"id": 3}]
        result = research.validate("""
            This answer [1] is contained the numbers used.
            Here is another use [2, 3, 5].
        """)
        # Assure at least one id is invalid and invalid id is identified
        assert result["is_valid"] == False
        assert result["invalid_ids"] == ["5"]

# Test 4: research request returns an answer with sources
def test_research_success():
    with patch('research_agent.research_agent.AIClient') as mock_ai, \
        patch('research_agent.research_agent.WebSearch') as mock_search:

        research = ResearchAgent()

        # Fake web results
        search_results = [
            {
                "title": "Python",
                "url": "https://python.org",
                "content": "Python is a programming language"
            },
            {
                "title": "Python (programming language)",
                "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
                "content": """
                    Python is a high-level, general-purpose programming language that 
                    emphasizes code readability, simplicity, and ease-of-writing
                """
            }
        ]

        mock_search.return_value.search.return_value = search_results
        mock_response = MagicMock()
        # Set the response with citations
        mock_response.choices[0].message.content = "Python is a programming language[1][2]"
        mock_ai.return_value.client.chat.completions.create.return_value = mock_response

        mock_ai.return_value.model = "qwen2.5-coder-7b"
        result = research.research("What is Python?")

        assert result["answer"] == "Python is a programming language[1][2]"
        # two sources found and are valid
        assert len(research.search_sources) == 2
        assert result["citation_validation"]["is_valid"] == True
        # verify search was called
        mock_search.return_value.search.assert_called_once_with(
            query = "What is Python?", max_results = 5
        )
        # verify the AI was called
        mock_ai.return_value.client.chat.completions.create.assert_called_once_with(
            model = "qwen2.5-coder-7b",
            messages = mock_ai.return_value.client.chat.completions.create.call_args.kwargs["messages"],
            temperature = 0.3
        )

# Test 5: behavior for when web search returns no results
def test_research_no_sources():
    with patch('research_agent.research_agent.AIClient') as mock_ai, \
        patch('research_agent.research_agent.WebSearch') as mock_search:

        research = ResearchAgent()
        mock_search.return_value.search.return_value = []
        mock_ai.return_value.model = "qwen2.5-coder-7b"

        # Mock AI answer generation
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Not enough information to answer confidently [1]"
        mock_ai.return_value.client.chat.completions.create.return_value = mock_response

        result = research.research("What is Python?")

        assert result["answer"] == "Not enough information to answer confidently [1]"
        assert len(research.search_sources) == 0
        assert result["sources"] == []
        assert result["citation_validation"]["is_valid"] == False
        assert result["citation_validation"]["invalid_ids"] == ["1"]
        # verify the search was still called
        mock_search.return_value.search.assert_called_once_with(
            query="What is Python?", max_results=5
        )
        # verify the AI was still called
        mock_ai.return_value.client.chat.completions.create.assert_called_once_with(
            model="qwen2.5-coder-7b",
            messages=mock_ai.return_value.client.chat.completions.create.call_args.kwargs["messages"],
            temperature=0.3
        )

# Test 6: Questions and answers are saved
def test_research_conversation_history():
    with patch('research_agent.research_agent.AIClient') as mock_ai, \
        patch('research_agent.research_agent.WebSearch') as mock_search:
        research = ResearchAgent()

        # Mock found source
        search_results = [
            {
                "title": "Python",
                "url": "https://python.org",
                "content": "Python is a programming language"
            }
        ]

        mock_search.return_value.search.return_value = search_results
        mock_response = MagicMock()
        # Set the response with citations
        mock_response.choices[0].message.content = "Python is a programming language [1]"
        mock_ai.return_value.client.chat.completions.create.return_value = mock_response
        # initial setup message (system)
        assert len(research.conversation) == 1
        research.research("What is Python?")
        # number of messages after first search (sys, question, answer)
        assert len(research.conversation) == 3
        research.research("What is Python?")
        # number of messages after second search
        # (sys, question, answer, question2, answer2)
        assert len(research.conversation) == 5