from openai import OpenAI

# Connect to local llama.cpp server
client = OpenAI(
    base_url = "http://127.0.0.1:8080/v1",
    api_key="local"
)

#Send a question to the model (Qwen Coder 2.5)
response = client.chat.completions.create(
    model = "qwen2.5-coder-7b",
    messages = [
        {
            "role":"user",
            "content": "Explain what Python is in three sentences."
        }
    ],
    temperature = 0.7
)

# Display answer
print(response.choices[0].message.content)