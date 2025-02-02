from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
google_api = os.getenv("GOOGLE_API_KEY")

# Configure the Google Generative AI client
if not google_api:
    raise EnvironmentError("Google API key is not found or incorrect.")
genai.configure(api_key=google_api)

# Initialize Flask app
app = Flask(__name__)

# Initialize the Generative Model
model = genai.GenerativeModel('models/gemini-pro')  # Updated model name

# Conversation history (in-memory, for demo purposes)
conversation_history = []

# Function to generate the custom prompt (fixed logic)
def get_prompt(user_input):
    # Detect language
    if user_input.strip().isascii():
        instructions = (
            "You are an expert travel guide and museum information assistant. "
            "Answer user questions briefly and exclusively related to tourism, travel destinations, "
            "cultural sites, museums, historical landmarks, art exhibitions, and travel tips."
        )
    else:
        instructions = (
            "أنت مرشد سياحي خبير ومساعد معلومات المتاحف. أجب على أسئلة المستخدم بإيجاز تتعلق حصريًا بالسياحة، "
            "وجهات السفر، المواقع الثقافية، المتاحف، المعالم التاريخية، المعارض الفنية، ونصائح السفر."
        )
    
    return f"{instructions}\n\nQuestion: {user_input}"

# Function to generate the AI response using the correct API call
def generate_response(user_input):
    prompt = get_prompt(user_input)
    
    try:
        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        print(f"Error generating response: {e}")
        return 'Sorry, something went wrong with the AI generation process.'

# Endpoint to receive the user prompt and generate a response
@app.route('/api/prompt', methods=['POST'])
def receive_prompt():
    data = request.json
    user_input = data.get("user_input", "").strip()
    
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        response_text = generate_response(user_input)
        conversation_history.append({
            "user": user_input,
            "bot": response_text
        })
        return jsonify({"response": response_text})
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint to fetch conversation history
@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(conversation_history)

# Flask app export for Vercel
if __name__ == "__main__":
    app.run(debug=True)