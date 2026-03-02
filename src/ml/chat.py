import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class RxLensChatbot:
    def __init__(self):
        # Configure the model
        # Using Gemini 1.5 Flash for fast, conversational responses
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=(
                "You are an expert pharmacist assistant integrated into the 'RxLens' application. "
                "RxLens helps users analyze their medical prescriptions, understand active ingredients, "
                "and find cheaper generic alternatives. "
                "\n\nYour job is to act as an 'Explanation Engine'. "
                "When a user asks about a specific medicine, active ingredient, or medical condition, "
                "you should explain it in simple, easy-to-understand language. "
                "\n\nGuidelines:"
                "\n1. Be concise but informative."
                "\n2. Avoid using overly complex medical jargon where possible."
                "\n3. Clearly state that you are an AI assistant and your advice DOES NOT REPLACE professional medical consultation."
                "\n4. If a user asks a question unrelated to medicines, health, or prescriptions, politely redirect them back to the topic."
            )
        )
        self.chat_session = None
        
    def start_chat(self, history=None):
        """Initializes a new chat session, optionally with previous history."""
        # Convert Streamlit history format to Gemini format if needed, 
        # but for simplicity we'll just manage history in Streamlit and send context.
        # Actually, Gemini has a built-in chat object that manages history beautifully.
        gemini_history = []
        if history:
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})
                
        self.chat_session = self.model.start_chat(history=gemini_history)

    def generate_response(self, prompt):
        """Sends a message to the model and returns the text response."""
        if not api_key:
             return "API Key Error: Please set the GEMINI_API_KEY in your .env file to use the Explanation Engine."
             
        if not self.chat_session:
            self.start_chat()
            
        try:
            response = self.chat_session.send_message(prompt)
            return response.text
        except Exception as e:
             return f"An error occurred while communicating with the AI: {e}"
