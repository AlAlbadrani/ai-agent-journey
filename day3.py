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
    }
]

# The actual tool function 
def calculate(expression):
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
    

# Send message with tools
response = client.messages.create(
    model = "claude-sonnet-4-6",
    max_tokens = 1024,
    tools = tools,
    messages = [
        {"role" : "user" , "content" : "What is 1337 multiplied by 42?"},
        {"role" : "user" , "content" : "What is the capital of France"}
    ]
)


#Extract the tool call and execute it
# Find the tool use block specifically
tool_use_block = None
for block in response.content:
    if block.type == "text":
        # Claude answered directly
        print(f"\nClaude's answer: {response.content[0].text}")

    if block.type == "tool_use":
        tool_use_block = block
        break

if tool_use_block:
    # handle tool call
    tool_name = tool_use_block.name
    tool_input = tool_use_block.input
    print(f"\nClaude wants to call: {tool_name}")
    print(f"With input: {tool_input}")
    result = calculate(tool_input["expression"])
    print(f"Tool result: {result}")
else:
    # Claude answered directly
    print(f"\nClaude's answer: {response.content[0].text}")


# Send the result back to Claude
final_response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What is 1337 multiplied by 42?"},
        {"role": "assistant", "content": response.content},
        {"role": "user", "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_block.id,
                "content": result
            }
        ]}
    ]
)

print(f"\nClaude's final answer: {final_response.content[0].text}")