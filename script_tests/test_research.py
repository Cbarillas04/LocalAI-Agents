from research_agent.research_agent import ResearchAgent

# Establish the agent
research = ResearchAgent()

# Question
result = research.research(
    "Can you explain the world impact the iran world has had?"
)

print(f"Answer: {result['answer']}")
print("\nSources:")
for source in result["sources"]:
    print(f"[{source['id']}]Title: {source['title']}\nURL: {source['url']}\n")