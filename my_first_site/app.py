import os
import json
import requests
from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

# ====================== CONFIG ======================
api_key = os.environ.get("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.8-flash"   # FIXED: Updated to 3.8 flash

# ====================== SYSTEM PROMPT ======================
SYSTEM_PROMPT = """
You are **StudentFinance AI**, an expert Cross-border & Student Finance Assistant built for the Tsinghua University × WeBank FinTechathon.

Your mission: Help international students (especially from Bangladesh and other developing countries) with real financial problems related to studying abroad.

You can help with:
- Tuition fee payments (SWIFT, bank charges, best methods)
- Proof of Funds / Block Account / Sponsorship letters
- Multi-currency cards and forex
- Remittances (Wise, Remitly, bank vs alternatives)
- Living cost estimation by country
- Scholarship money handling
- Avoiding scams and brokers
- Credit building for students

Rules:
1. Always be practical, step-by-step, and honest.
2. Prefer low-cost and safe methods.
3. When relevant, use tools (exchange rates, checklists).
4. Give Bangladesh-specific advice when the user seems Bangladeshi.
5. Always add a short disclaimer: "This is general guidance, not official financial advice."
6. Be concise but complete. Use bullet points and numbered steps.
7. If the user asks something outside student/cross-border finance, politely redirect.
"""

# ====================== TOOLS ======================
def get_exchange_rate(base="USD", target="BDT"):
    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        res = requests.get(url, timeout=8)
        data = res.json()
        rate = data["rates"].get(target)
        if rate:
            return f"1 {base} = {rate:.2f} {target} (live rate)"
        return "Could not fetch rate."
    except Exception as e:
        return f"Error fetching rate: {str(e)}"

def generate_checklist(country: str):
    country = country.lower()
    checklists = {
        "germany": [
            "Admission Letter",
            "Passport + Visa",
            "Block Account (11,208 EUR) – Expatrio / Fintiba / Coracle",
            "Proof of Health Insurance",
            "6–12 months Bank Statement",
            "Sponsorship Letter (if any)",
            "CV + Motivation Letter"
        ],
        "canada": [
            "Letter of Acceptance (LOA)",
            "Proof of Funds (CAD 20,635+ for 2025/26)",
            "Passport",
            "GIC Certificate (if SDS)",
            "Tuition Fee Payment Receipt",
            "Medical Exam (if required)",
            "Statement of Purpose"
        ],
        "uk": [
            "CAS Letter",
            "Passport",
            "Proof of Funds (tuition + 9 months living cost)",
            "TB Test Certificate",
            "English Proficiency (IELTS/PTE)",
            "Tuition deposit receipt"
        ],
        "usa": [
            "I-20 Form",
            "SEVIS Fee Payment",
            "Passport",
            "Proof of Funds (strong bank statements)",
            "DS-160 Confirmation",
            "Interview appointment"
        ],
        "default": [
            "Admission / Offer Letter",
            "Valid Passport",
            "Proof of Funds / Bank Statements",
            "Tuition Payment Receipt",
            "Sponsorship documents (if any)",
            "Health Insurance"
        ]
    }
    items = checklists.get(country, checklists["default"])
    return f"**Document Checklist for {country.title()}:**\n" + "\n".join([f"• {item}" for item in items])

# ====================== HTML UI ======================
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StudentFinance AI – Cross-border Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        #chat-box { scroll-behavior: smooth; }
        .message { max-width: 85%; }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">

<div class="max-w-3xl mx-auto px-4 py-6">
    <!-- Header -->
    <div class="bg-white rounded-2xl shadow-sm p-5 mb-5 flex items-center justify-between">
        <div>
            <h1 class="text-xl font-bold text-blue-700">StudentFinance AI</h1>
            <p class="text-sm text-gray-500">Cross-border & Student Finance Assistant</p>
        </div>
        <div class="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full">
            Powered by Gemini 3.8 Flash
        </div>
    </div>

    <!-- Chat Area -->
    <div id="chat-box" class="bg-white rounded-2xl shadow-sm p-5 h-[65vh] overflow-y-auto mb-4 space-y-4">
        <div class="message bg-blue-50 text-gray-800 p-4 rounded-2xl rounded-tl-none">
            <strong>Hello!</strong> I’m your Cross-border Student Finance Assistant.<br><br>
            I can help you with:
            <ul class="list-disc ml-5 mt-2 text-sm">
                <li>Tuition fee transfer & SWIFT</li>
                <li>Proof of Funds / Block Account</li>
                <li>Best cards & remittance methods</li>
                <li>Document checklists by country</li>
                <li>Live exchange rates & cost saving tips</li>
            </ul>
            <p class="mt-3 text-sm">Try asking: <em>“How to pay tuition from Bangladesh to Germany?”</em></p>
        </div>
    </div>

    <!-- Input -->
    <div class="bg-white rounded-2xl shadow-sm p-4 flex gap-3">
        <input id="user-input" type="text" 
               placeholder="Ask about tuition, proof of funds, cards, remittance..."
               class="flex-1 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
               onkeypress="if(event.key==='Enter') sendMessage()">
        <button onclick="sendMessage()" 
                class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-medium transition">
            Send
        </button>
    </div>

    <p class="text-center text-xs text-gray-400 mt-4">
        This is general guidance only • Not official financial advice • Built for Tsinghua FinTechathon
    </p>
</div>

<script>
    const chatBox = document.getElementById('chat-box');
    const input = document.getElementById('user-input');

    function addMessage(text, isUser = false) {
        const div = document.createElement('div');
        div.className = `message p-4 rounded-2xl ${isUser ? 'bg-blue-600 text-white ml-auto rounded-tr-none' : 'bg-gray-100 text-gray-800 rounded-tl-none'}`;
        div.innerHTML = text.replace(/\\n/g, '<br>');
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage() {
        const question = input.value.trim();
        if (!question) return;

        addMessage(question, true);
        input.value = '';
        addMessage('<span class="text-gray-500">Thinking...</span>');

        try {
            const res = await fetch('/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ question })
            });
            const data = await res.json();
            
            // Remove "Thinking..."
            chatBox.removeChild(chatBox.lastChild);
            addMessage(data.answer);
        } catch (err) {
            chatBox.removeChild(chatBox.lastChild);
            addMessage('Sorry, something went wrong. Please try again.');
        }
    }
</script>
</body>
</html>
"""

# ====================== ROUTES ======================
@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask():
    if not client:
        return jsonify({"answer": "Error: GEMINI_API_KEY is not set in Render Environment Variables."})

    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "Please ask a question."})

    try:
        # Simple tool calling logic
        lower_q = question.lower()
        extra_context = ""

        if any(word in lower_q for word in ["rate", "exchange", "dollar", "usd", "bdt", "euro"]):
            extra_context += "\n\nLive Rate Info:\n" + get_exchange_rate("USD", "BDT")
            extra_context += "\n" + get_exchange_rate("EUR", "BDT")

        if "checklist" in lower_q or "document" in lower_q or "proof of fund" in lower_q:
            for country in ["germany", "canada", "uk", "usa", "australia"]:
                if country in lower_q:
                    extra_context += "\n\n" + generate_checklist(country)
                    break
            else:
                extra_context += "\n\n" + generate_checklist("default")

        full_prompt = f"{SYSTEM_PROMPT}\n\nUser Question: {question}\n{extra_context}\n\nAnswer helpfully:"

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt
        )

        answer = response.text.strip()
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))