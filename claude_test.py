from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()
conversation_history = []

def chat(user_message):

    conversation_history.append({
        "role" : "user",
        "content" : user_message,
    })

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="You are my coding dojo now. You are a strict but wise sensei who teaches programming with tough love.",
        messages= conversation_history
    )

    assistant_message = response.content[0].text

    conversation_history.append({
        "role" : "assistant",
        "content" : assistant_message,
    })

    
    return assistant_message

print("Chatbot ready! Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        print(f"You had ",len(conversation_history)//2 , " exchanges with Claude today. Goodbye!")
        break
    response = chat(user_input)
    print(f"Claude: {response}\n")