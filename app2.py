from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# --- Predefined FAQ Answers ---
faq = {
    "program": "Iron Lady offers leadership programs for women focusing on confidence, communication, career growth, and personal development.",
    "duration": "The program duration is 8 weeks, with weekly live sessions and self-paced learning modules.",
    "mode": "The program is conducted fully online, making it accessible to participants across India and globally.",
    "certificate": "Yes, a certificate of completion is provided to all participants who finish the program.",
    "mentors": "Our mentors are experienced professionals, industry leaders, and certified coaches passionate about empowering women."
}

# --- AI-Powered Response using Ollama (Local LLM) ---
def get_ai_response(question):
    # Context prompt to guide the AI
    system_prompt = (
        "You are an assistant for Iron Lady, an organization that empowers women through leadership training. "
        "Answer clearly and concisely based on these facts:\n"
        "- Programs: Leadership training for confidence, communication, and career growth.\n"
        "- Duration: 8 weeks (live + self-paced).\n"
        "- Mode: Fully online.\n"
        "- Certification: Yes, provided upon completion.\n"
        "- Mentors: Industry leaders and certified coaches.\n"
        "If unsure, say you don't know. Keep answers short."
    )
    
    full_prompt = f"{system_prompt}\n\nQuestion: {question}\nAnswer:"

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:8b-instruct-q4_0",  # Lightweight quantized model
                "prompt": full_prompt,
                "stream": False,
                "temperature": 0.7,
                "max_tokens": 100
            },
            timeout=10  # Don't hang forever
        )

        if response.status_code == 200:
            result = json.loads(response.text)
            return result["response"].strip()
        else:
            return None  # Fallback to rule-based
    except Exception as e:
        print(f"Ollama error: {e}")
        return None  # Fallback to rule-based

# --- Fallback Rule-Based Matching ---
def get_fallback_response(question):
    q = question.lower()

    if "program" in q or "offer" in q:
        return faq["program"]
    elif "duration" in q or "how long" in q:
        return faq["duration"]
    elif "online" in q or "offline" in q or "mode" in q:
        return faq["mode"]
    elif "certificate" in q or "certification" in q:
        return faq["certificate"]
    elif "mentor" in q or "coach" in q:
        return faq["mentors"]
    elif "hello" in q or "hi" in q:
        return "Hello! How can I help you with Iron Lady programs today?"
    elif "thank" in q:
        return "You're welcome! Feel free to ask more."
    else:
        return "I'm not sure. Please ask about programs, duration, mode, certificates, or mentors."

# --- Final Response Handler ---
def get_response(question):
    # First, try AI (Ollama)
    ai_reply = get_ai_response(question)
    if ai_reply and len(ai_reply) > 10:  # Valid response
        return ai_reply
    
    # If AI fails, fall back to rules
    return get_fallback_response(question)

# --- Routes ---
@app.route("/")
def index():
    return render_template("index1.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "Please ask a question."})
    
    bot_response = get_response(user_message)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    print("Starting Iron Lady Chatbot...")
    print("Make sure Ollama is running: http://localhost:11434")
    print("Try: ollama run llama3:8b-instruct-q4_0")
    app.run(debug=True)