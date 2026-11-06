from research_agent.research_agent import ResearchAgent

# Establish the agent
research = ResearchAgent()

# Question
answer1 = research.research(
    "Compare REST APIs and GraphQL. Explain their main differences. Adv/dis-tanges & tradeoffs. "
)

print("\n First answer:\n", answer1)

answer2 = research.research(
    "Which of those is generally easier to cache, why? "
)

print("\n Second answer:\n", answer2)