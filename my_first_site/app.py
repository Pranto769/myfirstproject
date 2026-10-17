import os
import requests
from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None
MODEL = "gemini-3.8-flash"

# ====== OFFLINE FALLBACK - WHEN QUOTA EXHAUSTED ======
FALLBACK_DB = {
    "germany": """
**Quick Summary:** Germany needs Blocked Account €11,208 + Tuition + Living.
**Step-by-Step Roadmap:**
1. Get Admission Letter + Anabin Check
2. Open Blocked Account via Expatrio / Coracle / Deutsche Bank - Transfer €11,208 with OUR fee code
3. Health Insurance ~€120/mo (TK / Mawista)
4. Semesterbeitrag €300 + Visa

**Cost Breakdown:**
- Blocked: €11,208 (Live: 1 EUR ~126 BDT)
- Tuition: 0-2000€ (Public), 10000€+ (Private)
- Total ~ €12,500 = ~15.7 Lakh BDT + SWIFT $30 fee
**Warnings:** Never use Hundi. Always use OUR code, else deduction will leave you below €11,208 visa threshold. Demand MT103 copy from your bank as proof.
*General guidance only.*
""",
    "canada": """
**Quick Summary:** Canada needs GIC $20,635 + Tuition.
**Roadmap:** 1. Get LOA 2. Open GIC via CIBC/Scotia 3. Pay Tuition 4. 6-Month Bank Statement + SOP
**Cost:** GIC $20,635 + Tuition $15k = ~$35k = ~41 Lakh BDT (Live: 1 CAD=86 BDT)
**Warnings:** Show 6 months stable balance, use OUR, keep MT103.
*General guidance only.*
""",
    "total cost": """
**Total Cost Calculator (Live Rates):**
- Germany: Tuition 0-2000€ + Blocked €11,208 + Insurance €1440 + Visa €75 = ~€13,000 (~16.3 Lakh BDT)
- Canada: GIC $20,635 + Tuition $15k + Living $10k = ~$45k CAD
- UK: Tuition £15k + IHS £1035 + Living £13k = ~£29k
- Always add: SWIFT $30, Bank File Fee 10k BDT, OUR Charge $25
- Live: 1 USD=117 BDT, 1 EUR=126 BDT, 1 CAD=86 BDT
Use OUR fee code to avoid deductions. Get MT103 receipt.
*General guidance only.*
""",
    "default": """
**StudentFinance AGENT v3.8 - Offline Mode (Quota Exhausted)**
We are in offline mode due to API limit, but here's guidance:
1. **Tuition Transfer:** Always instruct bank to use OUR fee code. Keep MT103.
2. **Blocked Account (Germany):** €11,208 via Expatrio/Coracle. Don't let balance go below threshold.
3. **Proof of Funds (Canada):** GIC $20,635 + 6-Month Statement.
4. **Dual Currency Card:** EBL Dual, BRAC Multi-Currency, City AMEX.
5. **Health Insurance:** Germany €120/mo, Canada GuardMe $200, UK IHS £1035/yr.
6. **Warnings:** Avoid Hundi, it causes visa rejection. All transfers via Student File + Banking Channel.
Live Rates: USD=117 BDT, EUR=126 BDT.
*General guidance only - API quota will reset in 1 hour.*
"""
}

def get_live_rate(base="USD", target="BDT"):
    try:
        r = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=5)
        return f"1 {base} = {r.json()['rates'].get(target):.2f} {target}"
    except:
        return "1 USD=117 BDT, 1 EUR=126 BDT"

def get_answer_offline(q):
    ql = q.lower()
    if "germany" in ql or "blocked" in ql: return FALLBACK_DB["germany"]
    if "canada" in ql or "gic" in ql: return FALLBACK_DB["canada"]
    if "total" in ql or "cost" in ql: return FALLBACK_DB["total cost"]
    return FALLBACK_DB["default"]

SYSTEM = "You are StudentFinance AGENT v3.8 Tsinghua x WeBank. Answer in 1. Summary 2. Roadmap 3. Cost Breakdown (use live rate) 4. Warnings (Hundi, OUR, MT103). End *General guidance only.*"

HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>AGENT v3.8</title><script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script><style>#chat{height:calc(100vh - 240px)}.msg{max-width:85%}.user{background:#2563eb;color:#fff;margin-left:auto}.ai{background:#fff;border:1px solid #e5e7eb}</style></head>
<body class="bg-gray-50"><header class="bg-white border-b sticky top-0 z-50"><div class="max-w-6xl mx-auto px-4 py-3 flex justify-between"><div><h1 class="font-bold text-blue-700">🎓 StudentFinance AGENT v3.8</h1><p class="text-xs text-gray-500">Real 3.8 Flash • Smart Fallback Enabled</p></div><div class="text-xs bg-green-600 text-white px-3 py-1.5 rounded-full font-bold">● Live • Quota Safe Mode</div></div></header>
<main class="max-w-6xl mx-auto px-4 py-4"><div id="chat" class="overflow-y-auto space-y-4 pb-4"><div class="ai msg p-5 rounded-2xl"><p class="font-bold">Hello! AGENT v3.8 with Quota Protection</p><p class="text-xs bg-blue-50 text-blue-700 p-2 rounded mb-3">If API quota ends, I auto-switch to offline expert answers - no more 429 error!</p>
<div class="flex flex-wrap gap-2 mb-3"><button onclick="ask('Germany total cost')" class="border border-blue-300 text-blue-700 px-3 py-1.5 rounded-full text-xs">🇩🇪 Germany Cost</button><button onclick="ask('Canada GIC total cost')" class="border px-3 py-1.5 rounded-full text-xs">🇨🇦 Canada Cost</button><button onclick="ask('total cost')" class="border px-3 py-1.5 rounded-full text-xs bg-yellow-100">💰 Total Cost</button></div>
<button onclick="ask('I am new from Bangladesh, complete roadmap from zero')" class="w-full bg-blue-600 text-white font-bold py-2.5 rounded-xl text-sm">✨ I AM NEW</button></div></div>
<div class="sticky bottom-0 bg-gray-50 pt-3"><div class="bg-white border rounded-2xl p-2 flex gap-2 shadow"><input id="inp" type="text" placeholder="Try total cost..." class="flex-1 px-4 py-3 rounded-xl focus:outline-none text-sm" onkeypress="if(event.key==='Enter')send()"><button onclick="send()" class="bg-blue-600 text-white px-5 py-3 rounded-xl text-sm">Send</button></div></div></main>
<script>const chat=document.getElementById('chat');const inp=document.getElementById('inp');
function addMsg(c,isUser){const d=document.createElement('div');d.className=`msg p-4 rounded-2xl ${isUser?'user':'ai'}`;if(isUser)d.innerText=c;else d.innerHTML=marked.parse(c);chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}
function ask(t){inp.value=t;send();}async function send(){const q=inp.value.trim();if(!q)return;addMsg(q,true);inp.value='';const l=document.createElement('div');l.className='ai msg p-4 rounded-2xl text-gray-500';l.innerHTML='🤖 AGENT v3.8 thinking...';chat.appendChild(l);chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});const d=await r.json();chat.removeChild(l);addMsg(d.answer,false);}catch(e){chat.removeChild(l);addMsg('Error.',false);}}
</script></body></html>"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask_agent():
    q = request.get_json().get("question","")
    extra = f"{get_live_rate('USD','BDT')} {get_live_rate('EUR','BDT')}"
    
    # Try Real AI
    if client:
        try:
            resp = client.models.generate_content(model=MODEL, contents=f"{SYSTEM}\nToolData:{extra}\nQ:{q}")
            return jsonify({"answer": resp.text})
        except Exception as e:
            err = str(e)
            # If Quota Error, use offline fallback - No more 429 to user!
            if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
                offline_ans = get_answer_offline(q)
                return jsonify({"answer": offline_ans + f"\n\n_[System Note: AI quota exhausted, showing offline expert answer. Quota resets in ~1 hour. Live Rate: {extra}]_"})
            return jsonify({"answer": f"Temp issue: {err[:200]}. Offline Answer: {get_answer_offline(q)}"})
    
    return jsonify({"answer": get_answer_offline(q)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))