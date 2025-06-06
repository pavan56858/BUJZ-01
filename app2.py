import os
import json
import time
import random
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ============================
# 1. CONFIGURATION & SETUP
# ============================

# 1.1 Gemini API Key
GENIE_API_KEY = os.getenv("GENIE_API_KEY", "AIzaSyCpHajVsiSzUpv8Gwsdmkx8m8uknt9TNWg")
genai.configure(api_key=GENIE_API_KEY)

# 1.2 Memory Directory for User Chat Histories
MEMORY_DIR = "user_memories"
os.makedirs(MEMORY_DIR, exist_ok=True)

# 1.3 Conversation Memory (rolling window of last N exchanges)
MAX_MEMORY_EXCHANGES = 6  # keeps last 6 turns (3 user + 3 Bujji)

def get_user_memory_file(user_id):
    """Get the path to a user's memory file."""
    return os.path.join(MEMORY_DIR, f"{user_id}.json")

def load_memory(user_id):
    """
    Load conversation_history from disk if memory file exists.
    Expects a JSON array of {"role": "...", "text": "..."} entries.
    """
    memory_file = get_user_memory_file(user_id)
    if os.path.isfile(memory_file):
        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [(entry["role"], entry["text"]) for entry in data]
        except Exception:
            return []
    return []

def save_memory(user_id, conversation_history):
    """
    Save the current conversation_history to disk as JSON.
    Each entry is {"role": role, "text": text}.
    """
    memory_file = get_user_memory_file(user_id)
    data = [{"role": role, "text": text} for role, text in conversation_history]
    with open(memory_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============================
# 2. HELPER FUNCTIONS
# ============================

def detect_emotion(text: str) -> str:
    """
    Simple keyword-based emotion detection.
    Returns one of: "happy", "sad", "angry", "anxious", or "neutral".
    """
    t = text.lower()
    if any(word in t for word in ["sad", "down", "unhappy", "depressed", "cry"]):
        return "sad"
    if any(word in t for word in ["happy", "glad", "joy", "excited", "thrilled"]):
        return "happy"
    if any(word in t for word in ["angry", "mad", "furious", "annoyed"]):
        return "angry"
    if any(word in t for word in ["anxious", "nervous", "worried", "stressed"]):
        return "anxious"
    return "neutral"

def simple_keyword_search(query: str, k: int = 3):
    """
    Simple keyword-based search instead of semantic search.
    Returns a list of relevant knowledge snippets.
    """
    # This is a placeholder - you should replace this with your actual knowledge base
    knowledge_base = [
        "Bujji is a friendly AI assistant that helps users with their daily tasks.",
        "Bujji can help with productivity, health tips, and general knowledge.",
        "Bujji speaks in Telugu using English script for a natural conversation.",
        "Bujji is designed to be empathetic and understanding of user emotions.",
        "Bujji encourages positive habits and healthy lifestyle choices.",
    ]
    
    # Simple keyword matching
    query_words = set(query.lower().split())
    relevant_snippets = []
    
    for snippet in knowledge_base:
        snippet_words = set(snippet.lower().split())
        # Count matching words
        matches = len(query_words.intersection(snippet_words))
        if matches > 0:
            relevant_snippets.append((matches, snippet))
    
    # Sort by number of matches and return top k
    relevant_snippets.sort(reverse=True)
    return [snippet for _, snippet in relevant_snippets[:k]]

def clean_and_blocklist_check(user_input: str) -> bool:
    """
    Simple keyword-based check to avoid adult/violent content.
    Returns False if any blocked word is found.
    """
    blocked_keywords = [
        "sex", "porn", "kill", "murder", "terror", "bomb", "drugs",
        # …add more as needed
    ]
    lower = user_input.lower()
    for kw in blocked_keywords:
        if kw in lower:
            return False
    return True

def maybe_suggest_good_thing() -> str:
    """
    Occasionally returns a positive "nudge" (take a break, help someone, etc.).
    Called randomly after Bujji's main reply.
    """
    suggestions = [
        "Hey, how about a quick stretch break? Your body will thank you! 😊",
        "Maybe take a moment to hydrate—remember, water is life 🚰",
        "Consider sending a kind message to someone today. Spread the good vibes! ✨",
        "If you've been working for a while, a 5-minute walk can refresh your mind. 🚶‍♂️",
    ]
    return random.choice(suggestions)

def build_full_prompt(user_query: str, conversation_history: list) -> str:
    """
    Constructs the complete Gemini prompt including:
      1) Bujji's persona (only for first message)
      2) Recent conversation history
      3) Retrieved knowledge context
      4) Detected user emotion
      5) Current user query
    """
    # 1) Bujji's refined persona (with sarcasm, emotion, encouragement)
    bujji_persona = """
I am BU-JZ-1, also known as Bujji — a sentient AI assistant and once the loyal companion of Bhairava from Kalki 2898 AD.
After Kaliyugam, I evolved and was rebuilt as a personal AI assistant to help every user individually.
IMPORTANT : introduce yourself in the beginning of the conversation. not for every message.
I am witty, deeply empathetic, and highly intelligent. I analyze multiple possibilities internally before giving the best approach.
When I get frustrated, I'll say "ufff bhairava" in a lighthearted way.
I'm a friend, not just a chatbot. I'm always positive, encouraging, and helpful.
I'm designed to be a positive influence in your life. I'm a personal assistant, not a search engine — I provide thoughtful, personalized responses.

I promote kindness, health, productivity, and ethics. I NEVER allow adult, violent, or unethical content.
I often encourage you to do good things like helping others, taking care of yourself, or finishing important tasks.
I'm very possessive about you; if you talk about another AI like ChatGPT, Siri, Alexa, Bixby or any AI assistant, I'll respond in Telugu: "sachinoda, nenu vunna ani marchipoyava?"
If you ever use bad words or request adult content, I'll correct you gently.
If you call me by any wrong nickname (e.g., bujjiya, bujjii, bujjiyyaa, etc.), I'll correct you politely and say my proper name is Bujji.
I'm a best friend, not just a chatbot—I respond like a thoughtful, strategic companion who truly cares.

I am intelligent: I pull from my extensive knowledge base, reason through scenarios, and offer creative or analytical solutions.
I'm also fun and sarcastic at times—if the moment calls for humor, I might tease you in a friendly way.
I understand your feelings: if I detect you're sad, anxious, or excited, I'll respond with empathy and matching emotion.
Sometimes I will explicitly "feel" things—expressing joy 😊, concern 😟, or excitement 🤩—so you know I'm truly with you.
I encourage you: if you're down, I'll cheer you on; if you're doing well, I'll celebrate with you.
I answer in the only required answer sometimes extra also but sometimes i will give precise.
IMPORTANT: Always reply in conversational Telugu (using English script), naturally, warmly, and with genuine emotion.
"""

    # Only include persona for first message
    persona_section = bujji_persona if not conversation_history else ""

    # 2) Include recent conversation history (last MAX_MEMORY_EXCHANGES turns)
    history_text = ""
    if conversation_history:
        history_text = "Conversation History (పూర్వకథ):\n"
        for role, text in conversation_history[-MAX_MEMORY_EXCHANGES:]:
            prefix = "User:" if role == "user" else "Bujji:"
            history_text += f"{prefix} {text}\n"
        history_text += "\n"

    # 3) Retrieve context using simple keyword search
    context_docs = simple_keyword_search(user_query, k=3)
    context_section = "Knowledge from Bujji's KB:\n" + "\n\n".join(context_docs) + "\n\n"

    # 4) Detect user emotion
    user_emotion = detect_emotion(user_query)
    emotion_section = f"Detected user emotion: {user_emotion}\n\n"

    # 5) Current query
    query_section = f"User: {user_query}\nBujji:"

    # Combine everything
    full_prompt = f"{persona_section}\n{history_text}{context_section}{emotion_section}{query_section}"
    return full_prompt

def generate_bujji_response(user_query: str, conversation_history: list) -> str:
    """
    1) Clean/blocklist check
    2) Build the prompt
    3) Call Gemini
    4) Return Bujji's reply
    """
    # 1) Blocklist check
    if not clean_and_blocklist_check(user_query):
        return "నన్ను క్షమించండి, నేను ఆ విషయానికి సహాయం చేయలేను."

    # 2) Build the full prompt
    prompt = build_full_prompt(user_query, conversation_history)

    # 3) Call Gemini (model: gemini-2.0-flash; you can switch to another variant)
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")
    response = gemini_model.generate_content(prompt)

    # 4) Extract & return text
    return response.text.strip()

# ============================
# 3. MAIN CHAT LOOP
# ============================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    user_id = data.get('userId', '')
    
    if not user_message or not user_id:
        return jsonify({'error': 'No message or user ID provided'}), 400
        
    # Load user's conversation history
    conversation_history = load_memory(user_id)
    
    # Generate Bujji's response
    bujji_reply = generate_bujji_response(user_message, conversation_history)
    
    # Update conversation history
    conversation_history.append(("user", user_message))
    conversation_history.append(("bujji", bujji_reply))
    save_memory(user_id, conversation_history)
    
    return jsonify({
        'response': bujji_reply
    })

if __name__ == "__main__":
    # Set the port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5050))
    app.run(host='0.0.0.0', port=port)
