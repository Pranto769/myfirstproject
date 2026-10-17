import os
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None
MODELS = ["gemini-2.0-flash", "gemini-1.5-flash"]

# ===== BEGINNER GUIDE - 100% ENGLISH =====
BEGINNER_GUIDE = """### 🚀 Complete Guideline - For Absolute Beginners

**Welcome! Starting from Zero? Follow these 6 Steps:**

**STEP 1: Select Your Country & University**
> Decide your destination first.
> - Low Cost + Blocked Account: Germany (€11,208)
> - GIC System: Canada ($20,635)
> - Higher Tuition but Scholarships: USA / UK
> **Action:** Click any Country button above to see the full roadmap.

**STEP 2: Open Student File (Bangladesh Bank Rule)**
> This is mandatory for any outward remittance.
> - Where: Any AD Branch of EBL, BRAC, City Bank
> - Documents: Passport, Offer Letter, NID, Photo
> - Fee: 5,000 - 15,000 BDT
> - Time: 1-2 days

**STEP 3: Get a Dual Currency Card**
> You will pay Tuition, SEVIS, and Visa fees with this card.
> - Best: EBL Dual Currency (Limit $12,000/year, Instant Activation)
> - Alternative: BRAC Bank (Best App Experience)
> **Important:** Use your own card, not someone else's, to avoid embassy issues.

**STEP 4: Main Financial Requirement (Country Specific)**
> - **For Germany:** Blocked Account - Open Expatrio (€49 - BEST, includes Blocked + Health + Travel Insurance) or Coracle (€25/mo). Then send €11,250 via SWIFT OUR and collect MT103.
> - **For Canada:** GIC Account - Send $20,635 CAD to CIBC / Scotia Bank.
> - **For UK/USA:** Tuition Fee + Bank Solvency (6 months FDR/Savings Statement)

**STEP 5: Health Insurance + Tuition Transfer**
> - Insurance: Germany €120/mo, Canada GuardMe $200/yr, UK IHS £1035/yr
> - Tuition: Always use SWIFT OUR + MT103 method. Never select SHA, otherwise University will deduct $25-30. After transfer, email the MT103 receipt to university finance.

**STEP 6: Visa Application**
> - Prepare all documents and apply via VFS / Embassy
> - For USA: SEVIS Fee $350 + Visa Fee $185 via your Dual Currency Card.
> - Bring printed copies of Offer Letter, Blocked/GIC Proof, MT103, Insurance for interview.

---
**What to do now?**
1. Click your preferred **Country** above (e.g., Germany)
2. Or type: `I want to go to Germany from zero, guide me`
"""

EXPERT_SHORT = {
    "tuition": "### 💸 Tuition Transfer\nAD Branch EBL/BRAC/City Fee 10k. Use OUR not SHA. MT103 receipt is mandatory.",
    "blocked": "### 🔒 Blocked Account €11,208\nExpatrio €49 BEST (Blocked+Health+Insurance). Coracle €25/mo cheaper. Send €11,250 via OUR.",
    "proof": "### 📄 Canada GIC $20,635\nCIBC/Scotia GIC + 6 months bank statement.",
    "card": "### 💳 Dual Currency Card\nEBL Dual Best ($12k), BRAC Best App.",
    "insurance": "### 🏥 Health Insurance\nGermany €120/mo, Canada GuardMe $200/yr.",
    "file": "### 📁 Student File Opening\nAD Branch docs: Passport, Admission Letter, NID. Fee 5k-15k BDT.",
    "visa": "### 🛂 Visa & SEVIS Fee\nUSA SEVIS $350 + Visa $185.",
    "loan": "### 🏦 Education Loan\nGermany: Loan NOT valid for Blocked Account. Canada: GIC must be cash."
}

def get_answer(q):
    ql = q.lower()
    if any(x in ql for x in ["i am new", "i know nothing", "complete guideline", "from zero", "beginner", "from jio"]):
        if client:
            for m in MODELS:
                try:
                    prompt = f"You are StudentFinance Expert for Bangladesh students. User is absolute beginner: '{q}'. Give a very detailed, step-by-step complete guideline from zero in 100% English. Structure: 1.Country Selection 2.Student File 3.Dual Currency Card 4.Blocked/GIC 5.Insurance 6.Tuition OUR+MT103 7.Visa. Mention specific costs and banks (EBL, BRAC, Expatrio 49 EUR). Friendly expert tone."
                    r = client.models.generate_content(model=m, contents=prompt)
                    return r.text
                except: continue
        return BEGINNER_GUIDE

    if client:
        for m in MODELS:
            try:
                r = client.models.generate_content(model=m, contents=f"You are StudentFinance Expert for Bangladesh students. Answer in 100% English, detailed and helpful. Question: {q}")
                print(f"Success {m}")
                return r.text
            except Exception as e:
                print(f"{m} error: {e}")
                continue
    
    if any(x in ql for x in ["tuition","swift","our","mt103"]): return EXPERT_SHORT["tuition"]
    if "blocked" in ql or "germany" in ql: return EXPERT_SHORT["blocked"]
    if any(x in ql for x in ["gic","proof"]): return EXPERT_SHORT["proof"]
    if any(x in ql for x in ["card","ebl"]): return EXPERT_SHORT["card"]
    if "insurance" in ql: return EXPERT_SHORT["insurance"]
    if "file" in ql: return EXPERT_SHORT["file"]
    if "visa" in ql or "sevis" in ql: return EXPERT_SHORT["visa"]
    if "loan" in ql: return EXPERT_SHORT["loan"]
    return BEGINNER_GUIDE

HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>StudentFinance</title>
<script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>#chat{height:calc(100vh - 280px)}.msg{max-width:85%}.user{background:#2563eb;color:#fff;margin-left:auto}.ai{background:#fff;border:1px solid #e5e7eb}</style></head>
<body class="bg-gray-50"><header class="bg-white border-b sticky top-0"><div class="max-w-6xl mx-auto px-4 py-3"><h1 class="font-bold text-blue-700">🎓 StudentFinance AGENT</h1><p class="text-xs text-gray-500">Expert guide for study abroad and finance</p></div></header>
<main class="max-w-6xl mx-auto px-4 py-4"><div id="chat" class="overflow-y-auto space-y-4 pb-4">
<div class="ai msg p-5 rounded-2xl"><h2 class="font-bold">Welcome! 👋</h2><p class="text-sm text-gray-600 mt-1 mb-4">Expert guide for study abroad and finance. Select destination, service and below.</p>
<p class="text-xs font-bold text-green-600 mb-2">🟢 NEW TO THIS? START HERE</p><div class="mb-6"><button onclick="ask('I am new, I know nothing, give me complete guideline from zero')" class="w-full bg-green-50 border-2 border-green-500 text-green-700 px-4 py-3 rounded-xl text-sm font-bold">🚀 I'm New - Complete Guideline For Me (I Know Nothing)</button></div>
<p class="text-xs font-bold text-gray-500 mb-2">SELECT DESTINATION</p><div class="flex flex-wrap gap-2 mb-6">
<button onclick="ask('Germany full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇩🇪 Germany</button><button onclick="ask('Canada full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇨🇦 Canada</button><button onclick="ask('UK full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇬🇧 UK</button><button onclick="ask('USA full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇺🇸 USA</button><button onclick="ask('China full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇨🇳 China</button><button onclick="ask('Australia full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇦🇺 Australia</button><button onclick="ask('Japan full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇯🇵 Japan</button><button onclick="ask('South Korea full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇰🇷 South Korea</button><button onclick="ask('Malaysia full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇲🇾 Malaysia</button><button onclick="ask('Sweden full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇸🇪 Sweden</button><button onclick="ask('France full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇫🇷 France</button><button onclick="ask('Italy full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇮🇹 Italy</button>
</div><p class="text-xs font-bold text-gray-500 mb-2">OUR SERVICES</p><div class="grid grid-cols-2 md:grid-cols-4 gap-3">
<button onclick="ask('Tuition transfer SWIFT OUR MT103 guide')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">💸 Tuition Transfer</p></button><button onclick="ask('Blocked Account Germany guide')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">🔒 Blocked Account</p></button><button onclick="ask('Proof of Funds GIC Canada')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">📄 Proof of Funds</p></button><button onclick="ask('Dual currency card EBL BRAC')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">💳 Dual Currency Card</p></button><button onclick="ask('Health insurance')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">🏥 Health Insurance</p></button><button onclick="ask('Student file opening')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">📁 Student File</p></button><button onclick="ask('Visa and SEVIS fee')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">🛂 Visa & SEVIS Fee</p></button><button onclick="ask('Education loan')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">🏦 Education Loan</p></button>
</div></div></div><div class="sticky bottom-0 bg-gray-50 pt-3"><div class="bg-white border rounded-2xl p-2 flex gap-2 shadow"><input id="inp" type="text" placeholder="Ask anything about studying abroad..." class="flex-1 px-4 py-3 rounded-xl focus:outline-none text-sm" onkeypress="if(event.key==='Enter')send()"><button onclick="send()" class="bg-blue-600 text-white px-6 py-3 rounded-xl text-sm font-bold">Send</button></div></div></main><script>const chat=document.getElementById('chat');const inp=document.getElementById('inp');function addMsg(c,isUser){const d=document.createElement('div');d.className=`msg p-4 rounded-2xl ${isUser?'user':'ai'}`;if(isUser)d.innerText=c;else d.innerHTML=marked.parse(c);chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}function ask(t){inp.value=t;send();}async function send(){const q=inp.value.trim();if(!q)return;addMsg(q,true);inp.value='';const l=document.createElement('div');l.className='ai msg p-4 rounded-2xl text-gray-400';l.innerHTML='Thinking...';chat.appendChild(l);chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});const d=await r.json();chat.removeChild(l);addMsg(d.answer,false);}catch(e){chat.removeChild(l);addMsg('Error.',false);}}</script></body></html>"""

@app.route("/")
def home(): return render_template_string(HTML)
@app.route("/ask", methods=["POST"])
def ask_agent():
    q=request.get_json().get("question","")
    return jsonify({"answer": get_answer(q)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))