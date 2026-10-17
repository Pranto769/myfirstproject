import os, requests
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None
MODEL = "gemini-3.8-flash"

# === 100% CLEAN EXPERT DATABASE - NO "I AM AGENT" TEXT ===
EXPERT_DB = {
    "tuition": """
### 💸 Tuition Transfer via SWIFT (OUR Code + MT103) - Full Guide

**1. Student File Opening (Mandatory in BD)**
Go to AD Branch (EBL/BRAC/City/Bank Asia). Docs: Admission Letter, Passport, NID, Certificates. Fee ~10k BDT.

**2. Transfer Process**
Tell bank officer: **"Use OUR charge code, NOT SHA"**. If you use SHA, $25-30 will be deducted by middle bank and University will receive less money = Rejection.
Send: Exact Tuition + $40 buffer for fees.

**3. Required Documents**
Offer Letter, Tuition Invoice, Student File Number, Form A.

**4. MUST Collect MT103**
After sending, ask bank for **MT103 Receipt**. This is SWIFT proof. Email this MT103 to your university finance office. Without MT103, they can't trace your payment.

**Total Cost:** Tuition + SWIFT $35 + OUR $25 + VAT.
**Warning:** Never use Hundi. Use only banking channel.
*General guidance only.*
""",
    "blocked": """
### 🔒 Germany Blocked Account €11,208 - Expatrio vs Coracle vs DB

**What:** You block €11,208 to prove living cost. You get €934/month back.

**Best Option for Bangladeshi:**
**1. Expatrio Value Pack (€49) - RECOMMENDED**
- Includes Blocked Account + Health Insurance + Free Travel Insurance
- Fastest approval (24h), Embassy knows it well

**2. Coracle (€25/mo)**
- Cheaper monthly fee, but health insurance separate

**3. Deutsche Bank (€150)**
- Slowest, old system, not recommended now

**How to Transfer:** From BD bank via OUR code. In reference, write your Expatrio ID. Send €11,250 (extra €42 for safety).
**Live:** €11,208 = ~14.1 Lakh BDT.
*General guidance only.*
""",
    "proof": """
### 📄 Canada Proof of Funds - GIC $20,635 + Bank Statement

**1. GIC (Mandatory for SDS)**
Buy online from CIBC/Scotiabank/SBI Canada. You pay $20,635 CAD. They give you $1,700/month for 12 months. You need GIC Certificate for visa.

**2. Bank Statement (6 Months)**
Show 6 months stable balance. Final balance must be: Tuition (1 year) + $10k CAD. No sudden big deposit before statement.

**Cost:** GIC $20,635 = ~17.7 Lakh BDT (1 CAD=86 BDT)
*General guidance only.*
""",
    "card": "### 💳 Dual Currency Card\n**EBL Dual:** Best, Dollar endorsement up to $12k, works for SEVIS/Visa fee.\n**BRAC Multi-Currency:** Best app.\n**City AMEX:** Lounge access.\nFor students: Open EBL Dual with Passport + Student File.",
    "insurance": "### 🏥 Health Insurance\n**Germany:** €120/mo - TK Public or Mawista Private. Expatrio includes it.\n**Canada:** GuardMe $200/yr mandatory.\n**UK:** IHS £1035/yr with visa fee.\n**USA:** $1500/yr via university.",
    "file": "### 📁 Student File Opening\nGo to any Authorized Dealer Branch. Docs: Passport, Admission, NID, Academic Docs. Fee 5k-15k BDT. This file allows you to legally send tuition and living costs abroad. It's mandatory.",
    "visa": "### 🛂 Visa & SEVIS Fee\n**USA:** SEVIS $350 (pay on fmjfee.com) + Visa $185 (CGI portal). Pay with your own EBL card. Keep receipt. Never pay with agent's personal card - causes fraud flag.",
    "loan": """
### 🏦 Education Loan vs Proof of Funds

**Can I show loan for Canada/Germany?**
**Germany:** NO. Loan NOT accepted for Blocked Account. Must show €11,208 cash.
**Canada:** Loan can be shown as additional support, but GIC must still be paid with cash.

**BD Banks:** EBL, BRAC, City, Prime give 10-30 Lakh loan at 9-12% interest, needs property collateral and 2 guarantors.
*General guidance only.*
"""
}

def offline_router(q):
    q = q.lower()
    if any(x in q for x in ["tuition", "swift", "our", "mt103"]): return EXPERT_DB["tuition"]
    if any(x in q for x in ["blocked", "germany", "expatrio", "coracle"]): return EXPERT_DB["blocked"]
    if any(x in q for x in ["gic", "proof", "canada"]): return EXPERT_DB["proof"]
    if any(x in q for x in ["card", "ebl", "dual"]): return EXPERT_DB["card"]
    if any(x in q for x in ["insurance", "health", "guardme", "ihs"]): return EXPERT_DB["insurance"]
    if "file" in q: return EXPERT_DB["file"]
    if any(x in q for x in ["visa", "sevis"]): return EXPERT_DB["visa"]
    if "loan" in q: return EXPERT_DB["loan"]
    # Default - clean welcome, not "I am AGENT"
    return "### Welcome to StudentFinance Guide\nSelect a topic above to get detailed roadmap.\n\n**Example:** Click Tuition Transfer for SWIFT OUR guide, or Blocked Account for Germany guide."

def get_rate(): 
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=3)
        return f"Live: USD={r.json()['rates']['BDT']:.0f} BDT"
    except: return "Live: USD=117 BDT, EUR=126 BDT"

HTML = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>AGENT v3.8 Clean</title>
<script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>#chat{height:calc(100vh - 230px)}.msg{max-width:85%}.user{background:#2563eb;color:#fff;margin-left:auto}.ai{background:#fff;border:1px solid #e5e7eb}</style>
</head><body class="bg-gray-50">
<header class="bg-white border-b sticky top-0 z-50"><div class="max-w-6xl mx-auto px-4 py-3 flex justify-between"><div><h1 class="font-bold text-blue-700">🎓 StudentFinance AGENT</h1><p class="text-xs text-gray-500">Clean Professional Mode • 12 Countries • 8 Services</p></div><div class="text-xs bg-green-600 text-white px-3 py-1.5 rounded-full">● Live • Clean Mode</div></div></header>
<main class="max-w-6xl mx-auto px-4 py-4"><div id="chat" class="overflow-y-auto space-y-4 pb-4">
<div class="ai msg p-6 rounded-2xl"><h2 class="font-bold">Welcome! 👋</h2><p class="text-sm text-gray-600 mt-1 mb-4">Your expert guide for study abroad finance. Select a destination or service below.</p>
<div class="flex flex-wrap gap-2 mb-4"><button onclick="ask('Full financial roadmap for Germany')" class="border bg-blue-50 border-blue-500 text-blue-700 px-4 py-2 rounded-full text-xs font-bold">🇩🇪 Germany</button><button onclick="ask('Full financial roadmap for Canada')" class="border px-3 py-2 rounded-full text-xs">🇨🇦 Canada</button><button onclick="ask('UK roadmap')" class="border px-3 py-2 rounded-full text-xs">🇬🇧 UK</button><button onclick="ask('USA roadmap')" class="border px-3 py-2 rounded-full text-xs">🇺🇸 USA</button></div>
<div class="grid grid-cols-2 md:grid-cols-4 gap-2"><button onclick="ask('Tuition transfer SWIFT OUR MT103 guide')" class="border p-3 rounded-xl text-left hover:border-blue-500"><p class="text-xs font-bold">💸 Tuition Transfer</p></button><button onclick="ask('Blocked Account Germany guide')" class="border p-3 rounded-xl text-left hover:border-blue-500"><p class="text-xs font-bold">🔒 Blocked Account</p></button><button onclick="ask('Proof of Funds GIC Canada')" class="border p-3 rounded-xl text-left hover:border-blue-500"><p class="text-xs font-bold">📄 Proof of Funds</p></button><button onclick="ask('Education loan vs proof of funds? Can I show loan for Canada and Germany?')" class="border p-3 rounded-xl text-left hover:border-blue-500"><p class="text-xs font-bold">🏦 Education Loan</p></button></div>
</div></div>
<div class="sticky bottom-0 bg-gray-50 pt-3"><div class="bg-white border rounded-2xl p-2 flex gap-2 shadow"><input id="inp" type="text" placeholder="Ask..." class="flex-1 px-4 py-3 rounded-xl focus:outline-none text-sm" onkeypress="if(event.key==='Enter')send()"><button onclick="send()" class="bg-blue-600 text-white px-6 py-3 rounded-xl text-sm font-bold">Send</button></div></div>
</main>
<script>const chat=document.getElementById('chat');const inp=document.getElementById('inp');
function addMsg(c,isUser){const d=document.createElement('div');d.className=`msg p-4 rounded-2xl ${isUser?'user':'ai'}`;if(isUser)d.innerText=c;else d.innerHTML=marked.parse(c);chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}
function ask(t){inp.value=t;send();}
async function send(){const q=inp.value.trim();if(!q)return;addMsg(q,true);inp.value='';const l=document.createElement('div');l.className='ai msg p-4 rounded-2xl text-gray-400';l.innerHTML='Thinking...';chat.appendChild(l);chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});const d=await r.json();chat.removeChild(l);addMsg(d.answer,false);}catch(e){chat.removeChild(l);addMsg('Error.',false);}}
</script></body></html>
"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask_agent():
    q = request.get_json().get("question","")
    clean_q = q.lower()
    
    # Try Real AI first
    if client:
        try:
            prompt = f"You are a financial advisor. Directly answer: {q}. No intro like 'I am AGENT'. Give steps, cost, warning. Live Rate: {get_rate()}"
            resp = client.models.generate_content(model=MODEL, contents=prompt)
            # If AI returns generic intro, replace with our expert DB
            if "I am StudentFinance AGENT" in resp.text or "I help with Tuition Transfer" in resp.text[:200]:
                return jsonify({"answer": offline_router(clean_q)})
            return jsonify({"answer": resp.text})
        except Exception as e:
            # Quota error -> use clean expert DB
            return jsonify({"answer": offline_router(clean_q)})
    
    return jsonify({"answer": offline_router(clean_q)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))