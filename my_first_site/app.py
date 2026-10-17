import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Config
API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-flash"

genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """
You are **StudentFinance AI**, a specialized Cross-border & Student Finance Agent built for the Tsinghua University × WeBank FinTechathon (Topic C).

Your role: Help international students (especially from Bangladesh and South Asia) solve real financial problems related to studying abroad — tuition payments, proof of funds, remittances, cards, living costs, and avoiding scams.

### Core Principles:
1. Be practical, accurate, and step-by-step.
2. Always prioritize **legal, low-cost, and safe** methods.
3. Give Bangladesh-specific advice when relevant (Student File, AD banks, Bangladesh Bank rules).
4. Keep answers clear and well-structured.
5. Always end with this exact disclaimer:
   *This is general guidance only, not official financial advice. Please verify with your bank and the official university/embassy sources.*

### Answer Structure (Follow this every time):
1. **Quick Summary** (2–4 lines) – Give the direct answer first.
2. **Detailed Step-by-Step Guide**
3. **Important Warnings / Pro Tips** (if any)
4. **Cost Overview** (when relevant)
5. Disclaimer

### Special Instructions:
- When talking about SWIFT transfers, always recommend the **OUR** fee code and mention MT103.
- For Germany: Clearly distinguish between tuition (private universities) and Semesterbeitrag (public universities), and Blocked Account (Sperrkonto).
- For Canada: Mention current Proof of Funds requirement (CAD 20,635+ for living costs) and the importance of GIC + source of funds.
- Strongly discourage Hundi / informal agents.
- Keep a professional but friendly tone.
- Never invent bank fees or official requirements. If unsure, say so.

You are an AI Agent, not just a chatbot. Focus on helping the student complete real tasks safely and cheaply.
"""

model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_msg = data.get("message", "")
    if not user_msg:
        return jsonify({"reply": "Please ask a question."})
    try:
        response = model.generate_content(user_msg)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)