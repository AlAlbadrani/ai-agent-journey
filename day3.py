from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# Define the tool 
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

# The actual tool function 
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

# Send message with tools
response = client.messages.create(
    model = "claude-sonnet-4-6",
    max_tokens = 1024,
    tools = tools,
    messages = [
        {"role" : "user" , "content" : "What is the capital of France"},
        {"role": "user", "content": "What is 1337 multiplied by 42 and what's the weather in Paris?"}
    ]
)

print(f"Stop reason: {response.stop_reason}")
print(f"Response: {response.content}")

#Extract the tool call and execute it
# Find the tool use block specifically
tool_results = []
for block in response.content:
    if block.type == "text":
        # Claude answered directly
        print(f"\nClaude's answer: {response.content[0].text}")
    elif block.type == "tool_use":
        if block.name == "calculate" :
            tool_results.append({
            "type" : "tool_result",
            "tool_use_id" : block.id,
            "content" : calculate(block.input["expression"])
            })
        elif block.name == "get_weather" :
            tool_results.append({
            "type" : "tool_result",
            "tool_use_id" : block.id,    
            "content" : get_weather(block.input["city"])
            })



# Send the result back to Claude
final_response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What is 1337 multiplied by 42 and what's the weather in Paris?"},
        {"role": "assistant", "content": response.content},
        {"role": "user", "content": tool_results}
    ]
)

print(f"\nClaude's final answer: {final_response.content[0].text}")

