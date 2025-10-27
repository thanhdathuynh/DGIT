import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def ask_ai_google(question, interactions=None): 
    #Ask Google Gemini AI assistant.
    prompt = f"""
You are a helpful assistant for gene-drug interactions.
Question: {question}
Data: {interactions if interactions else "No data available."}
Answer concisely in plain language.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI error: {str(e)}"
