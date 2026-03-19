from flask import Flask, request, jsonify, render_template
from code_challenge_agent import run_agent, conversation_history, load_memory
import markdown

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error" : "No message provided"}) , 400
    
    response = run_agent(user_message)
    html_response = markdown.markdown(response)
    return jsonify({"response" : html_response})

if __name__ == "__main__":
    app.run(debug=True)
