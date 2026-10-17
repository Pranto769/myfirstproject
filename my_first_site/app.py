import os
import requests
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

# ====================== CONFIG - FIXED TO 3.8 ======================
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# PRIMARY IS 3.8 AS YOU WANTED - FALLBACK IS 2.0 IF 3.8 NOT FOUND
MODEL_PRIMARY = "gemini-3.8-flash" 
MODEL_FALLBACK = "gemini-2.0-flash"

# ====================== SYSTEM PROMPT ======================
SYSTEM_PROMPT = """
You are StudentFinance AI, a specialized Cross-border & Student Finance Agent for the Tsinghua University x WeBank FinTechathon (Topic C).
Goal: Help students from Bangladesh with real financial tasks.

Strict Answer Format:
1. Quick Summary (2-4 lines max)
2. Step-by-Step Guide
3. Important Notes / Warnings
4. Cost Overview (when relevant)
End with exactly: *This is general guidance only, not official financial advice. Please verify with your bank and official sources.*

Key Rules:
- Always recommend OUR fee code for SWIFT.
- Always mention keeping MT103.
- Strongly discourage Hundi/informal agents.
- For Germany: Separate Semesterbeitrag, Tuition, and Blocked Account (€11,208).
- For Canada: Living cost CAD 20,635+.
- Use live exchange rate when provided.
- Be practical, clear, and student-friendly in English.
"""

def get_live_rate(base="USD", target="BDT"):
    try:
        res = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=6)
        return f"1 {base} = {res.json()['rates'].get(target):.2f} {target}"
    except:
        return "Rate temporarily unavailable"

def get_checklist(country):
    country = country.lower()
    data = {
        "germany": ["Admission Letter", "Blocked Account (€11,208)", "Health Insurance", "Semesterbeitrag"],
        "canada": ["LOA", "GIC Certificate", "Proof of Funds CAD 20,635+", "Tuition Receipt"],
        "uk": ["CAS Letter", "Proof of Funds", "TB Test", "English Test"],
        "usa": ["I-20 Form", "SEVIS Fee", "Strong Bank Statements"],
        "china": ["Admission Notice (JW202)", "Visa Application Form", "Physical Examination", "Proof of Funds"],
        "australia": ["CoE", "GTE Statement", "Proof of Funds", "Health Insurance OSHC"],
        "japan": ["COE", "Admission Letter", "Bank Solvency", "Japanese Language Proof"],
        "south korea": ["Admission Letter", "Bank Statement $20k+", "Academic Docs"],
        "malaysia": ["Offer Letter", "EMGS Approval", "Medical Screening"],
        "sweden": ["Admission Letter", "Proof of Funds SEK 10k+/month", "Insurance"],
        "france": ["Campus France Approval", "Accommodation Proof", "Blocked Funds"],
        "italy": ["Universitaly Pre-enrollment", "Proof of Funds", "Accommodation"]
    }
    items = data.get(country, ["Admission Letter", "Passport", "Proof of Funds"])
    return "Document Checklist for " + country.title() + ": " + ", ".join(items)

# ====================== NEW UI - ENGLISH + 12 COUNTRIES + SERVICES ======================
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>StudentFinance AI | Tsinghua x WeBank</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; }
    #chat-container { height: calc(100vh - 240px); }
    .message { max-width: 85%; line-height: 1.65; }
    .user-msg { background: #2563eb; color: white; margin-left: auto; border-bottom-right-radius: 4px; }
    .ai-msg { background: #fff; border: 1px solid #e2e8f0; border-bottom-left-radius: 4px; }
    .ai-msg h3 { font-size: 15px; font-weight: 700; color: #1e40af; margin: 14px 0 8px 0; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }
  </style>
</head>
<body class="bg-gray-50 text-gray-800">
  <header class="bg-white border-b sticky top-0 z-50">
    <div class="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
      <div><h1 class="text-lg font-bold text-blue-700">🎓 StudentFinance AI</h1><p class="text-xs text-gray-500">Cross-border Student Finance Agent • Tsinghua x WeBank FinTechathon</p></div>
      <div class="text-xs bg-blue-50 text-blue-700 px-3 py-1 rounded-full font-medium">Powered by Gemini 3.8 Flash</div>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-4 py-4">
    <div id="chat-container" class="overflow-y-auto space-y-4 pb-4">
      <div class="ai-msg message p-5 rounded-2xl">
        <p class="font-bold text-base">Hello! I'm your Cross-border Finance Agent.</p>
        <p class="text-sm text-gray-600 mb-4">Select your destination country or explore our services below. You can ask anything in English.</p>

        <!-- 12 COUNTRIES AS YOU ASKED -->
        <p class="text-xs font-bold text-gray-500 mb-2">STEP 1: SELECT YOUR COUNTRY (12 Options)</p>
        <div class="flex flex-wrap gap-2 mb-5">
          <button onclick="askExample('Full financial roadmap for Germany from Bangladesh')" class="bg-white border border-blue-300 text-blue-700 px-3 py-1.5 rounded-full text-xs font-medium hover:bg-blue-600 hover:text-white">🇩🇪 Germany</button>
          <button onclick="askExample('Full financial roadmap for Canada with GIC and proof of funds')" class="bg-white border px-3 py-1.5 rounded-full text-xs hover:bg-blue-50">🇨🇦 Canada</button>
          <button onclick="askExample('Full financial roadmap for UK')" class="bg-white border px-3 py-1.5 rounded-full text-xs hover:bg-blue-50">🇬🇧 UK</button>
          <button onclick="askExample('Full financial roadmap for USA with SEVIS and I-20')" class="bg-white border px-3 py-1.5 rounded-full text-xs hover:bg-blue-50">🇺🇸 USA</button>
          <button onclick="askExample('Full financial roadmap for China with JW202 form')" class="bg-white border px-3 py-1.5 rounded-full text-xs hover:bg-blue-50">🇨🇳 China</button>
          <button onclick="askExample('Full financial roadmap for Australia with OSHC')" class="bg-white border px-3 py-1.5 rounded-full text-xs hover:bg-blue-50">🇦🇺 Australia</button>
          <button onclick="askExample('Full financial roadmap for Japan with COE')" class="bg-white border px-3 py-1.5 rounded-full text-xs hover:bg-blue-50">🇯🇵 Japan</button>
          <button onclick="askExample('Full financial roadmap for South Korea')" class="bg-white border px-3 py-1.5 rounded-full text-xs hover:bg-blue-50">🇰🇷 South Korea</button>
          <button onclick="askExample('Full financial roadmap for Malaysia with EMGS')" class="bg-white border px-3 py-1.5 rounded-full text-xs hover:bg-blue-50">🇲🇾 Malaysia</button>
          <button onclick="askExample('Full financial roadmap for Sweden')" class="bg-white border px-3 py-1.5 rounded-full text-xs hover:bg-blue-50">🇸🇪 Sweden</button>
          <button onclick="askExample('Full financial roadmap for France')" class="bg-white border px-3 py-1.5 rounded-full text-xs hover:bg-blue-50">🇫🇷 France</button>
          <button onclick="askExample('Full financial roadmap for Italy with Universitaly')" class="bg-white border px-3 py-1.5 rounded-full text-xs hover:bg-blue-50">🇮🇹 Italy</button>
        </div>

        <!-- OUR SERVICES SECTION AS YOU ASKED -->
        <p class="text-xs font-bold text-gray-500 mb-2">STEP 2: OUR SERVICES - What We Provide</p>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2 mb-5">
          <button onclick="askExample('How to pay tuition fee from Bangladesh via SWIFT with OUR code and MT103?')" class="bg-blue-50 border border-blue-100 p-3 rounded-xl text-left hover:bg-blue-600 hover:text-white group"><p class="text-xs font-bold">💸 Tuition Transfer</p><p class="text-[11px] opacity-70 mt-1 group-hover:text-white">SWIFT, OUR code, MT103</p></button>
          <button onclick="askExample('What is Blocked Account for Germany? How to open Expatrio or Coracle?')" class="bg-green-50 border border-green-100 p-3 rounded-xl text-left hover:bg-green-600 hover:text-white group"><p class="text-xs font-bold">🔒 Blocked Account</p><p class="text-[11px] opacity-70 mt-1">Germany €11,208 Guide</p></button>
          <button onclick="askExample('Proof of Funds and GIC for Canada, how to show bank statement?')" class="bg-purple-50 border border-purple-100 p-3 rounded-xl text-left hover:bg-purple-600 hover:text-white group"><p class="text-xs font-bold">📄 Proof of Funds</p><p class="text-[11px] opacity-70 mt-1">Canada GIC, POF, SOP</p></button>
          <button onclick="askExample('Best dual currency card for students in Bangladesh? EBL, BRAC, City?')" class="bg-orange-50 border border-orange-100 p-3 rounded-xl text-left hover:bg-orange-600 hover:text-white group"><p class="text-xs font-bold">💳 Dual Currency Card</p><p class="text-[11px] opacity-70 mt-1">Best cards comparison</p></button>
          <button onclick="askExample('Health insurance for students going abroad? OSHC, German insurance?')" class="bg-red-50 border border-red-100 p-3 rounded-xl text-left hover:bg-red-600 hover:text-white group"><p class="text-xs font-bold">🛡️ Health Insurance</p><p class="text-[11px] opacity-70 mt-1">OSHC, Germany, UK</p></button>
          <button onclick="askExample('Current USD to BDT and EUR to BDT rate and best exchange method?')" class="bg-yellow-50 border border-yellow-100 p-3 rounded-xl text-left hover:bg-yellow-600 hover:text-white group"><p class="text-xs font-bold">💱 Live Exchange Rate</p><p class="text-[11px] opacity-70 mt-1">USD, EUR, CAD live</p></button>
          <button onclick="askExample('Document checklist for studying abroad from Bangladesh?')" class="bg-gray-50 border p-3 rounded-xl text-left hover:bg-gray-800 hover:text-white group"><p class="text-xs font-bold">✅ Document Checklist</p><p class="text-[11px] opacity-70 mt-1">Country-wise list</p></button>
          <button onclick="askExample('Total cost to study abroad from Bangladesh? Scholarship options?')" class="bg-teal-50 border border-teal-100 p-3 rounded-xl text-left hover:bg-teal-600 hover:text-white group"><p class="text-xs font-bold">🎓 Cost & Scholarship</p><p class="text-[11px] opacity-70 mt-1">Full cost breakdown</p></button>
        </div>

        <div class="bg-blue-600 text-white p-3 rounded-xl">
          <button onclick="askExample('I am a new student from Bangladesh, I know nothing about studying abroad finance. Give me a complete step-by-step roadmap in English.')" class="w-full bg-white text-blue-700 font-bold py-2.5 rounded-lg text-sm">✨ I AM NEW - GUIDE ME FROM START</button>
        </div>
      </div>
    </div>

    <div class="sticky bottom-0 bg-gray-50 pt-3">
      <div class="bg-white border rounded-2xl p-2 flex gap-2 shadow-sm">
        <input id="user-input" type="text" placeholder="Ask anything... e.g. How much does it cost for Germany?" class="flex-1 px-4 py-3 rounded-xl focus:outline-none text-sm" onkeypress="if(event.key === 'Enter') sendMessage()">
        <button onclick="sendMessage()" class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-xl text-sm font-medium">Send</button>
      </div>
    </div>
  </main>

<script>
  const chatContainer = document.getElementById('chat-container');
  const input = document.getElementById('user-input');
  function getRelated(q){
    q=q.toLowerCase();
    if(q.includes('germany')) return ["What is Semesterbeitrag?","Coracle vs Expatrio which is better?","Health insurance cost in Germany?"];
    if(q.includes('canada')) return ["GIC process step-by-step?","How many months bank statement needed?"];
    if(q.includes('tuition')||q.includes('swift')) return ["What is OUR code in SWIFT?","Why keep MT103?","How to open student file?"];
    return ["Total cost?","Which bank is best?","What is Hundi risk?"];
  }
  function addMessage(content, isUser=false, originalQuestion=""){
    const div = document.createElement('div');
    div.className = `message p-4 rounded-2xl ${isUser ? 'user-msg' : 'ai-msg'}`;
    if(isUser){ div.innerText = content; }
    else{ div.innerHTML = marked.parse(content); }
    if(!isUser && originalQuestion){
      const related = getRelated(originalQuestion);
      let h = `<div class="mt-4 pt-3 border-t"><p class="text-xs font-bold text-gray-500 mb-2">🔍 Explore More:</p><div class="flex flex-wrap gap-2">`;
      related.forEach(r=>{ h+=`<button onclick="askExample('${r}')" class="text-xs bg-blue-50 text-blue-700 border px-3 py-1.5 rounded-full hover:bg-blue-600 hover:text-white">+ ${r}</button>`; });
      h+=`</div></div>`;
      div.innerHTML+=h;
    }
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
  function askExample(t){ input.value=t; sendMessage(); }
  async function sendMessage(){
    const q=input.value.trim(); if(!q) return;
    addMessage(q,true); input.value='';
    const loading=document.createElement('div'); loading.className='ai-msg message p-4 rounded-2xl text-gray-500'; loading.innerHTML='Thinking...'; chatContainer.appendChild(loading);
    chatContainer.scrollTop=chatContainer.scrollHeight;
    try{
      const res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
      const data=await res.json(); chatContainer.removeChild(loading); addMessage(data.answer,false,q);
    }catch(e){ chatContainer.removeChild(loading); addMessage('Sorry, error. Try again.',false,""); }
  }
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask():
    if not client:
        return jsonify({"answer": "Error: GEMINI_API_KEY missing in environment."})
    data = request.get_json()
    question = data.get("question","").strip()
    if not question:
        return jsonify({"answer": "Please type a question."})
    try:
        extra=""
        lq=question.lower()
        if any(w in lq for w in ["rate","usd","bdt","eur","euro","exchange"]):
            extra+=f" Live Rates: {get_live_rate('USD','BDT')} | {get_live_rate('EUR','BDT')} | {get_live_rate('CAD','BDT')}"
        for co in ["germany","canada","uk","usa","china","australia","japan","korea","malaysia","sweden","france","italy"]:
            if co in lq:
                extra+=f" {get_checklist(co)}"
                break
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser Question: {question}\nContext: {extra}\n\nProvide answer in strict markdown format."
        try:
            response = client.models.generate_content(model=MODEL_PRIMARY, contents=full_prompt)
        except Exception as e:
            print(f"Primary model {MODEL_PRIMARY} failed: {e}, trying fallback")
            response = client.models.generate_content(model=MODEL_FALLBACK, contents=full_prompt)
        return jsonify({"answer": response.text.strip()})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)