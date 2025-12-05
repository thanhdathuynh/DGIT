import os
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

ALLOWED_BIO_KEYWORDS = {
    "bioinformatics",
    "genomics",
    "transcriptomics",
    "proteomics",
    "sequence",
    "sequencing",
    "alignment",
    "blast",
    "ngs",
    "next-generation",
    "variant",
    "annotation",
    "pipeline",
    "assembly",
    "vcf",
    "fasta",
    "fastq",
    "sam",
    "bam",
    "snp",
    "mutation",
    "expression",
    "differential",
}

NON_BIO_DISALLOWED = {
    "music",
    "art"
    "weather",
    "forecast",
    "temperature",
    "physics",
    "astronomy",
    "space",
    "economics",
    "finance",
    "stocks",
    "politics",
}

# Project-awareness
PROJECT_KEYWORDS = {
    "website",
    "tool",
    "project",
    "dgit",
    "readme",
    "readme.md",
    "ai_helper.py",
    "app.py",
    "gene_mapping.py",
    "db_conn.py",
    "templates",
}

def get_project_context(max_chars=2000) -> str:
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if not os.path.exists(readme_path):
        return ""
    try:
        with open(readme_path, "r", encoding="utf-8") as fh:
            text = fh.read(max_chars)
            return text
    except Exception:
        return ""

def classify_scope_with_model(question: str) -> str:
    """Ask the AI model to classify whether `question` is IN_SCOPE or OUT_OF_SCOPE.
    """
    if not question or not isinstance(question, str):
        return "OUT_OF_SCOPE"

    prompt = f"""
You are a strict classifier for the DGIT AI Assistant. Decide whether the user's
question should be handled by the assistant. The assistant's scope is limited to:
- Genes, proteins, and drugs
- Bioinformatics topics (genomics, sequencing, BLAST, pipelines, file formats, etc.)
- Questions about this codebase or its files

For each input, reply with exactly one token, either IN_SCOPE or OUT_OF_SCOPE.

Examples:
Q: What is TP53?
A: IN_SCOPE

Q: Explain BRCA1
A: IN_SCOPE

Q: How does BLAST work?
A: IN_SCOPE

Q: what is bioinformatics
A: IN_SCOPE

Q: Tell me the weather in London
A: OUT_OF_SCOPE

Q: Who painted the Mona Lisa?
A: OUT_OF_SCOPE

Q: What is the purpose of this website?
A: IN_SCOPE

Q: {question}
A:
"""

    resp = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    text = resp.text.strip()

    if "IN_SCOPE" in text.upper():
        return "IN_SCOPE"
    if "OUT_OF_SCOPE" in text.upper():
        return "OUT_OF_SCOPE"
    raise RuntimeError(f"Unexpected classifier response: {text!r}")

def is_in_scope(question: str) -> bool:
    """Return True if the question is about genes, proteins, or drugs only.
    """
    try:
        decision = classify_scope_with_model(question)
        return decision == "IN_SCOPE"
    except Exception:
        pass

    if not question or not isinstance(question, str):
        return False

    text = question.lower()

    # If asking about the purpose of the project/tool, allow only if bio/project keywords present
    if re.search(r"\bpurpose\b", text):
        for kw in PROJECT_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", text):
                return True
        return False

    # Allow if mentions gene/protein/drug words
    if re.search(r"\bgene(s)?\b", text) or re.search(r"\bprotein(s)?\b", text) or re.search(r"\bdrug(s)?\b", text):
        return True

    # Allow common bioinformatics keywords
    for kw in ALLOWED_BIO_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            return True

    # Allow queries about this codebase or files
    for kw in PROJECT_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            return True

    # Allow if contains a likely gene symbol (e.g., TP53, BRCA1) - 2-6 alnum uppercase
    if re.search(r"\b[A-Z0-9]{2,6}\b", question):
        return True

    return False


def is_project_question(question: str) -> bool:
    """Return True if the question is asking about this project/tool/website or how to use it."""
    if not question or not isinstance(question, str):
        return False
    text = question.lower()
    # common phrasing for purpose/usage
    if re.search(r"\b(how|how do i|how to|how can i)\b", text) and re.search(r"\b(use|install|run|setup|start)\b", text):
        return True
    if re.search(r"\b(what is this tool|what is this project|what does this project do|what does this tool do|purpose of this (site|website|tool|project))\b", text):
        return True
    # mention of README or project files
    for kw in PROJECT_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            return True
    return False


def is_mdd_question(question: str) -> bool:
    """Return True if the question appears to ask about Major Depressive Disorder
    in any wording (e.g., 'MDD', 'major depressive disorder', 'major depression').
    """
    if not question or not isinstance(question, str):
        return False
    text = question.lower()
    # match common variants: 'mdd', 'major depressive disorder', 'major depression'
    if re.search(r"\bmdd\b", text):
        return True
    if re.search(r"major\s+depress", text):
        return True
    return False


def is_naming_request(question: str) -> bool:
    """Return True if the user asks to name/list examples of genes, proteins, or drugs.
    This uses a simple heuristic on verbs like 'name', 'list', 'give me', 'examples of',
    combined with entity keywords ('gene', 'protein', 'drug').
    """
    if not question or not isinstance(question, str):
        return False
    text = question.lower()
    if not re.search(r"\b(name|list|give me|give|show|what are|examples|example|cite)\b", text):
        return False
    if re.search(r"\b(gene|genes|protein|proteins|drug|drugs)\b", text):
        return True
    return False

def ask_ai_google(question, interactions=None, ncbi_summary=None, mdd_context=None):
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

    # tailored prompt that explains the tool and how to use it
    if is_project_question(question):
        proj_ctx = get_project_context()
        project_prompt = f"""
You are a helpful assistant describing a small software project. The user asked:
{question}

Project README (if available):
{proj_ctx if proj_ctx else 'No README available.'}

Instructions:
- Summarize the purpose of the project in 3-5 short sentences.
- If the README mentions a specific focus (e.g., Major Depressive Disorder), include that.
- Provide concise usage instructions for running or interacting with the tool (commands, files to edit) if present in the README.
- Keep the answer factual and under 200 words.

Answer:
"""
        try:
            resp = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=project_prompt
            )
            return resp.text.strip()
        except Exception as e:
            if proj_ctx:
                first_lines = proj_ctx.splitlines()[:6]
                return "\n".join(first_lines)
            return "This is outside of my scope."

    # bold formatting for named entities
    extra_instruction = ""
    if is_naming_request(question):
        extra_instruction = (
            "\nImportant: if you list or name genes, proteins, or drugs, wrap each "
            "name in double asterisks (Markdown bold), e.g., **TP53**, so it is easy to spot.\n"
        )
        # Require that listed entities are related to Major Depressive Disorder (MDD).
        extra_instruction += (
            "Only list genes, proteins, or drugs that are related to Major Depressive Disorder (MDD). "
            "If you use examples, prefer items from the project's MDD lists when available.\n"
        )

    # If MDD context (lists) were provided by the caller, include them for grounding
    if mdd_context and isinstance(mdd_context, dict):
        lists_text = []
        if mdd_context.get('genes'):
            lists_text.append("Genes: " + ", ".join(mdd_context.get('genes')))
        if mdd_context.get('proteins'):
            lists_text.append("Proteins: " + ", ".join(mdd_context.get('proteins')))
        if mdd_context.get('drugs'):
            lists_text.append("Drugs: " + ", ".join(mdd_context.get('drugs')))
        if lists_text:
            context_text += "\nProject MDD lists:\n" + "\n".join(lists_text) + "\n"

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
    {extra_instruction}

Answer:
"""

    # Enforce scope: refuse queries outside genes/proteins/drugs
    text = question.lower()
    for kw in PROJECT_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            proj_ctx = get_project_context()
            if proj_ctx:
                context_text += f"\nProject README:\n{proj_ctx}\n"

    # If the user asks about MDD in any form, always provide a concise summary
    if is_mdd_question(question):
        mdd_prompt = f"""
You are an expert biomedical assistant. The user asked: {question}

Task: Provide a concise (<=150 words) factual summary of Major Depressive Disorder (MDD). Prioritize information from authoritative sources, especially NCBI/NIH. Include typical core symptoms, common contributing factors (biological, genetic, environmental, psychological), and usual treatment approaches (psychotherapy, pharmacotherapy). End with a short source note like "(Source: NCBI)".

Keep language non-judgmental and avoid giving specific medical advice.

Answer:
"""
        try:
            resp = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=mdd_prompt
            )
            text = resp.text.strip()
            if text:
                return text
        except Exception:
            pass

        # Fallback brief summary if model call fails
        return (
            "Major Depressive Disorder (MDD) is a common and serious mood disorder "
            "characterized by persistent low mood, loss of interest or pleasure in most activities, "
            "and other cognitive and physical symptoms (changes in sleep, appetite, energy, "
            "concentration, or feelings of worthlessness). Causes are multifactorial and can include "
            "genetic, biological, environmental, and psychological factors. Treatment often involves "
            "psychotherapy, pharmacotherapy (antidepressant medications), or a combination of both. "
            "(Source: NCBI summary.)"
        )

    if not is_in_scope(question):
        return "This is outside of my scope."

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"AI error: {str(e)}"
