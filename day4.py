from anthropic import Anthropic
from dotenv import load_dotenv
import random

load_dotenv()

client = Anthropic()

#Tool definition
tools = [
    {
        "name": "calculate",
        "description": "Performs basic math calculations. Use this when the user asks you to calculate something.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The math expression to evaluate e.g. '2 + 2' or '10 * 5'"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "get_weather",
        "description": "Gets the current weather for a given city. Use this when the user asks about weather.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to get weather for e.g. 'London' or 'Paris'"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_joke",
        "description": "Get random generated jokes from different categories.",
        "input_schema": {
            "type": "object",
            "properties": {
                "joke_type": {
                    "type": "string",
                    "description": "Joke typ. programming joke/dad joke/math joke"
                }
            },
            "required": ["joke_type"]
        }
    }
]

# Tool functions
def calculate(expression):
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
    
def get_weather(city):
    fake_weather = {
        "london": "15°C, cloudy",
        "paris": "18°C, sunny",
        "new york": "22°C, partly cloudy",
        "malmö": "10°C, windy"
    }
    return fake_weather.get(city.lower(), "Weather data not available for this city")

def get_joke(joke_type):
    joke_categories = {
        "programming joke" : [
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "I give my programming jokes a C++",
            "I tried to tell a dad joke to a function. But it didn’t get the reference."
        ],
        "dad joke" : [
            "Why don't scientists trust atoms? Because they make up everything.",
            "I'm such a good navigator, a self-driving car once asked me for directions.",
            "My boss said “dress for the job you want, not for the job you have.” So I went in as Batman.",
            "I went to the aquarium this weekend, but I didn’t stay long. There’s something fishy about that place."
        ],
        "math joke" : [
           "Why was the math book sad? It had too many problems.",
           "Hey, have you ever noticed what’s odd? Every other number!",
           "Swimmers love one kind of math more than all others, what is it? Dive-ision!",
           "Why was six afraid of seven? Because seven, eight, nine!"
        ]
    }

    search_term = str(joke_type).lower().strip()
    selected_list = joke_categories.get(search_term)

    if selected_list:
        return random.choice(selected_list)
    else:
        return "Category not found! Try 'programming jokes', 'dad jokes' or 'math jokes'"


def execute_tool(name, input):
    if name == "calculate":
        return calculate(input["expression"])
    elif name == "get_weather":
        return get_weather(input["city"])
    elif name == "get_joke":
        requested_type = input.get("joke_type", "dad jokes") 
        return get_joke(requested_type)
    else:
        return f"Unkown tool: {name}"
    
conversation_history = []

def run_agent(user_message):
    conversation_history.append({
        "role" : "user",
        "content" : user_message
    })

    while True:
        response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system="You are a helpful assistant with access to tools.",
                tools=tools,
                messages=conversation_history
            )
        
        if response.stop_reason == "end_turn":
            final_answer = response.content[0].text
            conversation_history.append({
                "role" : "assistant",
                "content" : response.content
            })
            return final_answer
        
        if response.stop_reason == "tool_use":
            conversation_history.append({
                "role" : "assistant",
                "content" : response.content
            })

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"-> Using tool: {block.name}")
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type" : "tool_result",
                        "tool_use_id" : block.id,
                        "content" : result
                    })

            conversation_history.append({
                "role" : "user",
                "content" : tool_results
            })

# Main loop
print("Agent ready! Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        print(f"You had {len(conversation_history) // 2} exchanges. Goodbye!")
        break
    
    response = run_agent(user_input)
    print(f"\nAgent: {response}\n")