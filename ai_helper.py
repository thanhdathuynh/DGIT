import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def ask_ai_google(question, interactions=None, ncbi_summary=None):
    """
    Ask Gemini AI to summarize or explain a gene/drug/protein based on DGIdb and NCBI context.
    """
    context_text = ""

    # Include DGIdb data (if any)
    if interactions:
        context_text += f"\nDGIdb interaction data:\n{interactions}\n"

    # Include NCBI summary (if available)
    if ncbi_summary:
        context_text += f"\nAccording to NCBI:\n{ncbi_summary}\n"

    # Build prompt for Gemini
    prompt = f"""
You are an expert biomedical assistant that helps explain gene-drug interactions.

User Question:
{question}

Context:
{context_text if context_text else "No data provided"}

Instructions:
1. If DGIdb data is provided, summarize what it means in plain, understandable terms.
2. If no DGIdb data but the question involves a gene or drug, describe what it is, what it does, and its biological or clinical role.
3. Always mention the sources (e.g., "Based on DGIdb" or "According to NCBI").
4. Keep the explanation under 150 words, factual, and easy to read.

Answer:
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"AI error: {str(e)}"
