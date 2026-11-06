from shared.ai_client import AIClient

# Establish AI connection
ai = AIClient()

# Ask Questions
answer = ai.generate_response(
    "Explain what an API is in simple terms.",
    temperature = 0.2
)

print(answer)