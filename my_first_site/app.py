import os
from flask import Flask, request, jsonify, render_template_string
app = Flask(__name__)

try:
    from google import genai
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else None
    print(f"Client init: {bool(client)} Has key: {bool(api_key)}")
except Exception as e:
    print(f"GenAI init fail: {e}")
    client = None

# Fallback - যদি AI fail করে তাও বড় উত্তর দেবে
def get_smart_answer(q):
    ql = q.lower()
    if "tuition" in ql or "swift" in ql or "mt103" in ql or "our" in ql or "sha" in ql:
        return "### 💸 Tuition Transfer - Complete Guide (Bangladesh)\n**Problem:** University says payment short by $25? Because you used SHA.\n**Solution: ALWAYS USE OUR.**\n**Step by Step:**\n1. **Student File:** Go to AD Branch (EBL, BRAC, City). Docs: Passport, Offer Letter, NID, Photo. Fee: 10k-15k BDT. Open File.\n2. **Bank Transfer:** Tell bank 'I need SWIFT MT103 with OUR charge'. Bank will take $ + $25-45 SWIFT charge.\n3. **OUR vs SHA:** OUR = You pay all charges (Correct). SHA = Charge shared, university gets less (Wrong).\n4. **Receipt:** Collect MT103 receipt from bank, email to university finance office with Student ID.\n5. **Time:** 2-3 working days. Keep MT103 for visa."
    if "student file" in ql:
        return "### 📁 Student File Opening - Full Process\n**What is it?** Mandatory file in Bangladesh Bank for sending tuition fee abroad.\n**Where:** Any AD Branch - EBL Dhanmondi Best, BRAC, City Bank, MTB.\n**Documents:** 1. Passport 2. Offer Letter 3. NID 4. Photo 5. Academic Docs.\n**Cost:** File opening 5k-15k BDT (EBL 10k, BRAC 8k). Yearly renewal 5k.\n**Why needed?** Without file you cannot send tuition via SWIFT."
    if "germany" in ql:
        return "### 💰 Germany Study Cost Breakdown 2025-26\n**Total Year 1:** ~ €13,500 needed to show.\n**Breakdown:**\n1. **Blocked Account:** €11,208 (YOUR money, back €934/month)\n2. **Health Insurance:** €120/month = €1,440/year\n3. **Semester Contribution:** €250-350 per semester (NOT tuition, for bus ticket)\n4. **Tuition:** Public Uni = FREE! Private = €10k-20k.\n5. **Other:** Visa €75 + Flight €700 + Student File 10k BDT.\n**Monthly Living:** €934 from Blocked is enough. Work 20hr/week = €500-800 extra.\n**Cheapest Blocked:** Expatrio €49 (Best value), Coracle €25/mo cheapest monthly."
    if "visa" in ql or "sevis" in ql:
        return "### 🛂 Visa & SEVIS Fee Guide\n**USA F1:** SEVIS $350 (fmjfee.com) + MRV $185 (ustraveldocs.com) = $535. Pay with YOUR OWN Dual Currency Card (EBL/BRAC). Save PDF receipt.\n**Germany:** National Visa €75 + Blocked Account proof €11,208 + Health Insurance proof.\n**Canada:** Visa $150 CAD + Biometric $85 CAD.\n**UK:** Visa £490 + IHS Health Surcharge £1035/year."
    return f"### 🎓 Student Finance Expert\nDetailed guide for: **{q}**\n**Germany:** Blocked €11,208 via Expatrio €49. Public uni free. Student File at EBL/BRAC 10k BDT. Send €11,250 via SWIFT OUR. Health €120/mo. Visa €75.\n**Canada:** GIC $20,635 via CIBC, Tuition via SWIFT OUR, Student File mandatory.\n**USA:** SEVIS $350 + MRV $185 via own card. Student File + SWIFT OUR for tuition.\n**General Rule:** Always use YOUR OWN Dual Currency Card (EBL $12k limit) and ALWAYS select OUR in SWIFT, never SHA. Keep MT103 receipt."

def get_ai(q):
    if not client:
        print("No client, using fallback")
        return get_smart_answer(q)
    
    # NEW MODELS 2026 - Old 2.0 is dead, now 2.5 is live
    models_to_try = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-flash-latest", "gemini-2.0-flash-lite"]
    
    for model_name in models_to_try:
        try:
            print(f"Trying model: {model_name}")
            res = client.models.generate_content(
                model=model_name, 
                contents=f"You are expert for Bangladeshi students study abroad finance. Give detailed, helpful, step-by-step answer in English with formatting for: {q}"
            )
            print(f"AI OK with {model_name}")
            return res.text
        except Exception as e:
            print(f"{model_name} error: {e}")
            continue
    
    print("All AI models failed, using fallback")
    return get_smart_answer(q)

HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>StudentFinance</title>
<script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>#chat{height:calc(100vh - 280px)}.msg{max-width:85%}.user{background:#2563eb;color:#fff;margin-left:auto}.ai{background:#fff;border:1px solid #e5e7eb}</style></head>
<body class="bg-gray-50"><header class="bg-white border-b sticky top-0 z-10"><div class="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center"><div><h1 class="font-bold text-blue-700">🎓 StudentFinance AGENT</h1><p class="text-xs text-gray-500">Expert guide for study abroad and finance</p></div><span class="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full">🟢 AI Live</span></div></header>
<main class="max-w-6xl mx-auto px-4 py-4"><div id="chat" class="overflow-y-auto space-y-4 pb-4">
<div class="ai msg p-5 rounded-2xl"><h2 class="font-bold">Welcome! 👋</h2><p class="text-sm text-gray-600 mt-1 mb-4">Expert guide for study abroad and finance. Select destination, service and below.</p>
<p class="text-xs font-bold text-green-600 mb-2">🟢 NEW TO THIS? START HERE</p><div class="mb-6"><button onclick="ask('I am new, I know nothing, give me complete guideline from zero for studying abroad from Bangladesh')" class="w-full bg-green-50 border-2 border-green-500 text-green-700 px-4 py-3 rounded-xl text-sm font-bold hover:bg-green-100">🚀 I'm New - Complete Guideline For Me (I Know Nothing)</button></div>
<p class="text-xs font-bold text-gray-500 mb-2">SELECT DESTINATION</p><div class="flex flex-wrap gap-2 mb-6">
<button onclick="ask('Germany full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white hover:bg-blue-50">🇩🇪 Germany</button><button onclick="ask('Canada full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white hover:bg-blue-50">🇨🇦 Canada</button><button onclick="ask('UK full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white hover:bg-blue-50">🇬🇧 UK</button><button onclick="ask('USA full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white hover:bg-blue-50">🇺🇸 USA</button><button onclick="ask('China full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white hover:bg-blue-50">🇨🇳 China</button><button onclick="ask('Australia full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white hover:bg-blue-50">🇦🇺 Australia</button><button onclick="ask('Japan full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white hover:bg-blue-50">🇯🇵 Japan</button><button onclick="ask('South Korea full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white hover:bg-blue-50">🇰🇷 South Korea</button><button onclick="ask('Malaysia full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white hover:bg-blue-50">🇲🇾 Malaysia</button><button onclick="ask('Sweden full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white hover:bg-blue-50">🇸🇪 Sweden</button><button onclick="ask('France full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white hover:bg-blue-50">🇫🇷 France</button><button onclick="ask('Italy full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white hover:bg-blue-50">🇮🇹 Italy</button>
</div><p class="text-xs font-bold text-gray-500 mb-2">OUR SERVICES</p><div class="grid grid-cols-2 md:grid-cols-4 gap-3">
<button onclick="ask('Tuition transfer SWIFT OUR MT103 guide')" class="bg-white border p-3 rounded-xl text-left hover:shadow"><p class="text-xs font-bold">💸 Tuition Transfer</p><p class="text-[10px] text-gray-500">SWIFT OUR</p></button><button onclick="ask('Blocked Account Germany guide')" class="bg-white border p-3 rounded-xl text-left hover:shadow"><p class="text-xs font-bold">🔒 Blocked Account</p><p class="text-[10px] text-gray-500">€11,208</p></button><button onclick="ask('Proof of Funds GIC Canada')" class="bg-white border p-3 rounded-xl text-left hover:shadow"><p class="text-xs font-bold">📄 Proof of Funds</p><p class="text-[10px] text-gray-500">GIC</p></button><button onclick="ask('Dual currency card EBL BRAC')" class="bg-white border p-3 rounded-xl text-left hover:shadow"><p class="text-xs font-bold">💳 Dual Currency Card</p><p class="text-[10px] text-gray-500">EBL/BRAC</p></button><button onclick="ask('Health insurance for students')" class="bg-white border p-3 rounded-xl text-left hover:shadow"><p class="text-xs font-bold">🏥 Health Insurance</p><p class="text-[10px] text-gray-500">Mawista</p></button><button onclick="ask('Student file opening full process')" class="bg-white border p-3 rounded-xl text-left hover:shadow"><p class="text-xs font-bold">📁 Student File</p><p class="text-[10px] text-gray-500">AD Branch</p></button><button onclick="ask('Visa and SEVIS fee guide')" class="bg-white border p-3 rounded-xl text-left hover:shadow"><p class="text-xs font-bold">🛂 Visa & SEVIS Fee</p><p class="text-[10px] text-gray-500">$350+$185</p></button><button onclick="ask('Education loan Bangladesh')" class="bg-white border p-3 rounded-xl text-left hover:shadow"><p class="text-xs font-bold">🏦 Education Loan</p><p class="text-[10px] text-gray-500">Loan</p></button>
</div></div></div><div class="sticky bottom-0 bg-gray-50 pt-3"><div class="bg-white border rounded-2xl p-2 flex gap-2 shadow-lg"><input id="inp" type="text" placeholder="Ask anything about studying abroad..." class="flex-1 px-4 py-3 rounded-xl focus:outline-none text-sm" onkeypress="if(event.key==='Enter')send()"><button onclick="send()" class="bg-blue-600 text-white px-6 py-3 rounded-xl text-sm font-bold hover:bg-blue-700">Send</button></div></div></main><script>const chat=document.getElementById('chat');const inp=document.getElementById('inp');function addMsg(c,isUser){const d=document.createElement('div');d.className=`msg p-4 rounded-2xl ${isUser?'user':'ai shadow-sm'}`;if(isUser)d.innerText=c;else d.innerHTML=marked.parse(c);chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}function ask(t){inp.value=t;send();}async function send(){const q=inp.value.trim();if(!q)return;addMsg(q,true);inp.value='';const l=document.createElement('div');l.className='ai msg p-4 rounded-2xl text-gray-400';l.innerHTML='Thinking with Gemini 2.5...';chat.appendChild(l);chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});const d=await r.json();chat.removeChild(l);addMsg(d.answer,false);}catch(e){chat.removeChild(l);addMsg('Error connecting to AI.',false);}}</script></body></html>"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask_agent():
    q=request.get_json().get("question","")
    return jsonify({"answer": get_ai(q)})

@app.route("/health")
def health(): 
    return {"has_key": bool(os.environ.get("GEMINI_API_KEY")), "client": bool(client), "status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))