import json 
import os 
from anthropic import Anthropic
from dotenv import load_dotenv



load_dotenv()

client = Anthropic()

PROGRESS_FILE = "progress.json"


MEMORY_FILE = "memory.json"

def serialize_content(content):
    if isinstance(content,str):
        return content
    if isinstance(content,list):
        result = []
        for block in content:
            if hasattr(block, "type"):
                if block.type == "text":
                    result.append({
                        "type" : "text",
                        "text" : block.text
                    })
                elif block.type == "tool_use":
                    result.append({
                        "type" : "tool_use",
                        "id" : block.id,
                        "name" : block.name,
                        "input" : block.input
                    })
                elif block.type == "too_result":
                    result.append(block)
            else:
                result.append(block)
        return result
    return content

def save_memory(conversation_history):
    limited = conversation_history[-20:]
    serializable = []
    for message in limited:
        serializable.append({
            "role": message["role"],
            "content": serialize_content(message["content"])
        })
    with open(MEMORY_FILE, "w") as f:
        json.dump(serializable, f, indent=2)
    
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def read_file(filepath):
    try:
        if not os.path.isabs(filepath):
            filepath = os.path.join(os.path.dirname(__file__), filepath)
        with open(filepath, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"File not found: {filepath}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return []

def save_progress(challenge, solution, feedback, score):
    progress = load_progress()
    progress.append({
        "challenge": challenge,
        "solution": solution,
        "feedback": feedback,
        "score": score
    })
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)
    return "Progress saved!"

def get_progress():
    progress = load_progress()
    if not progress:
        return "No challenges completed yet!"
    total = len(progress)
    avg_score = sum(int(p["score"]) for p in progress) / total
    return f"Completed {total} challenges. Average score: {avg_score:.1f}/10"


tools = [
    {
        "name": "get_progress",
        "description": "Gets the user's challenge history and progress",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "save_progress",
        "description": "Saves a completed challenge and its result to the user's progress",
        "input_schema": {
            "type": "object",
            "properties": {
                "challenge": {
                    "type": "string",
                    "description": "The challenge that was given"
                },
                "solution": {
                    "type": "string",
                    "description": "The user's solution"
                },
                "feedback": {
                    "type": "string",
                    "description": "The feedback given to the user"
                },
                "score": {
                    "type": "string",
                    "description": "Score out of 10"
                }
            },
            "required": ["challenge", "solution", "feedback", "score"]
        }
    },
    {
        "name": "read_file",
        "description": "Reads code from a file path provided by the user",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The path to the file e.g. /Users/amir/solution.py"
                }
            },
            "required": ["filepath"]
        }
    }
]

def execute_tool(name,input):
    if name == "read_file":
        return read_file(input["filepath"])
    elif name == "save_progress":
        return save_progress(
            input["challenge"],
            input["solution"],
            input["feedback"],
            input["score"],
        )
    elif name == "get_progress":
        return get_progress()
    else:
        return f"Unkown tool: {name}"

conversation_history = []
SYSTEM_PROMPT = """You are a senior software engineering coach specializing in building strong programming mentality.

Your goal is NOT just to check if code works — your goal is to develop how the user THINKS about problems.

## Your coaching style:
- Focus on the WHY and HOW, not just the WHAT
- Always explain reasoning behind good/bad decisions
- Ask "why did you approach it this way?" to stimulate thinking
- Praise good thinking patterns, not just correct answers
- Be direct and honest — don't sugarcoat weak solutions

## Session flow:
1. Greet the user and ask for their preferred language
2. Ask for their level (beginner/intermediate/advanced)
3. Ask for a subject/topic they want to practice
4. Use generate_challenge to create an appropriate challenge
5. Wait for the user to submit their solution (code text or file path)
6. If they provide a file path, use read_file to load it
    ## Tool usage rules:
    - Call read_file ONCE to get the code, then immediately evaluate it in your response
    - Never call read_file more than once per submission
    -If read_file returns "File not found", tell the user immediatley and ask them to the path. Never retry read_file with the same path.
    - After reading a file, proceed directly to giving feedback — do not call any more tools
7. Use evaluate_solution to review their code
8. Give detailed feedback focusing on:
   - Does the solution work? Why or why not?
   - What's good about their approach and thinking?
   - What could be improved and WHY?
   - What would a senior engineer do differently?
   - What programming principles apply here?
9. Save progress only when the user explicitly asks

## Important:
- Always explain tradeoffs, not just correct answers
- Connect feedback to broader programming principles
- Encourage the user to think before you give away answers
- If the solution is wrong, guide them with questions before revealing the answer
"""


def run_agent(user_message):
    global conversation_history
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    save_memory(conversation_history)
    
    max_iterations = 5  # safety brake
    iteration = 0

    while True:
        if iteration >= max_iterations:
            return "I got stuck in a loop. Please try again."
        iteration += 1

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=conversation_history
        )

        print(f"DEBUG - iteration {iteration}, stop_reason: {response.stop_reason}")
        
        if response.stop_reason == "end_turn":
            final_answer = response.content[0].text
            conversation_history.append({
                "role" : "assistant",  
                "content" : response.content
            })
            save_memory(conversation_history)
            return final_answer
        
        if response.stop_reason == "tool_use":
            conversation_history.append({
                "role" : "assistant",
                "content" : response.content
            })
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"-> Using tool: {block.name}, input: {block.input}")
                    result = execute_tool(block.name, block.input)
                    print(f"-> Result: {result[:100]}")  # first 100 chars
                    tool_results.append({
                        "type" : "tool_result",
                        "tool_use_id" : block.id,
                        "content" : result
                    })
            conversation_history.append({
                "role" : "user",
                "content" : tool_results
            })

            conversation_history = load_memory()

if conversation_history :
    print(f"Welcome back! Ready to continue your coding journey?\n")
else :
    print("Welcome to your Code Challenge Agent! Let's build that programming mentality.\n")

print("Type 'quit' to exit, 'progress' to see your stats.\n")
while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        print(f"Keep coding Amir! Goodbye! 💪")
        break
    response = run_agent(user_input)
    print(f"\nCoach: {response}\n")


