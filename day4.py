from anthropic import Anthropic
from dotenv import load_dotenv

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
    }
]

# Tool functions
def calculate(city):
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

def execute_tool(name, input):
    if name == "calculate":
        return calculate(input["expression"])
    elif name == "get_weather":
        return get_weather(input["city"])
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