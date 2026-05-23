import os
import json
import time
import urllib.request
import urllib.error
import re

from dotenv import load_dotenv

load_dotenv()

# Fixed API Key loading with failover keys
API_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    "AIzaSyA17aHqVroPl-3AA5fFsD8wmpsnC08oCx8",
    "AIzaSyB-iKaNhT5gKnNVShVdvOCyE6oidpgUMiU"
]
# Clean and keep unique keys
seen = set()
API_KEYS = [x for x in API_KEYS if x and not (x in seen or seen.add(x))]

# Models to try in order (each has separate quota)
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]


def call_gemini(prompt, model, api_key):

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 4096
        }
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=90) as response:

        result = json.loads(response.read().decode("utf-8"))

        text = result["candidates"][0]["content"]["parts"][0]["text"]

        # Clean up markdown if present
        text = text.strip()

        # Regex to strip ```language ... ```
        match = re.match(r"^```[a-zA-Z0-9+#-]*\s*(.*?)\s*```$", text, re.DOTALL)
        if match:
            text = match.group(1).strip()
        elif text.startswith("```"):
            # Fallback split
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        return text


def solve_problem(problem_text, language="python"):

    if not API_KEYS:
        raise Exception("No Gemini API keys found in environment or config")

    # ========================================
    # BUILD LANGUAGE SPECIFIC INSTRUCTIONS
    # ========================================
    lang_instructions = {
        "python": "Return ONLY executable Python 3 code. Use input() for inputs and print() for outputs.",
        "javascript": "Return ONLY executable JavaScript code (Node.js environment). Use fs.readFileSync(0, 'utf-8') or readline for inputs, and console.log() for outputs.",
        "java": "Return ONLY executable Java code. The class name should be Main (or public class Main). Make sure to import all required utilities.",
        "c++": "Return ONLY executable C++ code. Include necessary standard libraries and namespace std.",
        "c": "Return ONLY executable C code. Include stdio.h and other required standard headers.",
        "sql": "Return ONLY the raw SQL query. Do NOT write markdown, explanations, or comments. Just the query text.",
        "html": "Return ONLY HTML markup. If inline CSS/JS is required, embed it inside <style> and <script> tags.",
        "css": "Return ONLY raw CSS code."
    }

    instruction = lang_instructions.get(language, f"Return ONLY executable {language} code.")

    # ========================================
    # BUILD PROMPT (concise to save tokens)
    # ========================================

    prompt = f"""Solve this coding problem.
Language: {language}
Instructions: {instruction}
Do NOT wrap the code in markdown code blocks. Return ONLY the raw code/text.
No explanations, no markdown, no comments.
Return code that can run and pass all test cases immediately.

Problem:
{problem_text[:6000]}
"""

    # ========================================
    # TRY EACH API KEY AND MODEL COMBINATION
    # ========================================

    last_error = None

    for api_key in API_KEYS:
        key_snippet = api_key[:10] + "..." if len(api_key) > 10 else api_key
        for model in MODELS:
            try:
                print(f"    [AI] Trying {model} with key {key_snippet}")
                result = call_gemini(prompt, model, api_key)
                print(f"    [AI] Success with {model}")
                return result
            except urllib.error.HTTPError as e:
                error_body = e.read().decode("utf-8")
                last_error = f"API error {e.code} on {model}: {error_body[:150]}"
                print(f"    [AI] HTTP error {e.code} on {model}, trying next option...")
            except Exception as e:
                last_error = f"Error on {model}: {str(e)[:150]}"
                print(f"    [AI] Exception on {model}: {str(e)[:100]}, trying next option...")

    # Final retry fallback with small delay if everything failed
    print("    [AI] All keys and models failed. Retrying first model after 2s delay...")
    time.sleep(2)
    for api_key in API_KEYS:
        try:
            result = call_gemini(prompt, MODELS[0], api_key)
            return result
        except Exception as e:
            last_error = str(e)

    raise Exception(f"All models and keys failed. Last error: {last_error}")