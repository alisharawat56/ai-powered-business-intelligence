from ollama import chat

response = chat(
    model="qwen3.5:0.8b",
    messages=[
        {
            "role": "user",
            "content": (
                "You are an e-commerce business analyst. "
                "The repeat purchase rate is 3.00%. "
                "Give one concise business observation. "
                "Do not invent metrics."
            )
        }
    ],
    think=False
)

print(response.message.content)