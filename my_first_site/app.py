import os, requests
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None
MODEL = "gemini-3.8-flash"

EXPERT = {
    "tuition": "### 💸 Tuition Transfer\n**Student File:** AD Branch EBL/BRAC/City Fee 10k BDT.\n**OUR Code:** Must use OUR not SHA. SHA deducts $25-30.\n**MT103:** Demand MT103 receipt after transfer. Email to university.\n**Warning:** No Hundi.",
    "blocked": "### 🔒 Blocked Account €11,208\n**Expatrio €49 BEST:** Blocked + Health + Insurance Fast 24h.\n**Coracle €25/mo:** Cheaper.\nSend €11,250 via OUR with Expatrio ID. ~14.1 Lakh BDT.",
    "proof": "### 📄 Canada GIC $20,635\nGIC from CIBC/Scotia/SBI. Get cert for visa.\nBank Statement 6 months stable, Tuition + $10k CAD.",
    "card": "### 💳 Dual Currency Card\nEBL Dual Best ($12k), BRAC Best App, City AMEX Lounge.",
    "insurance": "### 🏥 Health Insurance\nGermany €120/mo, Canada GuardMe $200/yr, UK IHS £1035/yr, USA $1500/yr.",
    "file": "### 📁 Student File Opening\nAD Branch docs: Passport Admission NID Certs Fee 5k-15k BDT.",
    "visa": "### 🛂 Visa & SEVIS Fee\nUSA SEVIS $350 + Visa $185. Pay with YOUR EBL card.",
    "loan": "### 🏦 Education Loan\nGermany: Loan NOT for Blocked. Canada: GIC must be cash. BD Banks 10-30 Lakh 9-12% interest."
}

def router(q):
    ql=q.lower()
    if any(x in ql for x in ["tuition","swift","our","mt103"]): return EXPERT["tuition"]
    if any(x in ql for x in ["blocked","germany"]): return EXPERT["blocked"]
    if any(x in ql for x in ["gic","proof","canada"]): return EXPERT["proof"]
    if any(x in ql for x in ["card","ebl","dual"]): return EXPERT["card"]
    if any(x in ql for x in ["insurance","health"]): return EXPERT["insurance"]
    if "file" in ql: return EXPERT["file"]
    if any(x in ql for x in ["visa","sevis"]): return EXPERT["visa"]
    if "loan" in ql: return EXPERT["loan"]
    return "Select a destination or service above for detailed guide."

def rate(): 
    try:
        r=requests.get("https://open.er-api.com/v6/latest/USD",timeout=3)
        return f"Live USD={r.json()['rates']['BDT']:.0f} BDT"
    except: return "Live USD=117 BDT"

HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>StudentFinance</title>
<script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>#chat{height:calc(100vh - 250px)}.msg{max-width:85%}.user{background:#2563eb;color:#fff;margin-left:auto}.ai{background:#fff;border:1px solid #e5e7eb}</style></head>
<body class="bg-gray-50"><header class="bg-white border-b sticky top-0 z-50"><div class="max-w-6xl mx-auto px-4 py-3"><h1 class="font-bold text-blue-700">🎓 StudentFinance AGENT</h1><p class="text-xs text-gray-500">Expert guide for study abroad and finance</p></div></header>
<main class="max-w-6xl mx-auto px-4 py-4"><div id="chat" class="overflow-y-auto space-y-4 pb-4">
<div class="ai msg p-5 rounded-2xl"><h2 class="font-bold">Welcome! 👋</h2><p class="text-sm text-gray-600 mt-1 mb-4">Expert guide for study abroad and finance. Select destination, service and below.</p>

<p class="text-xs font-bold text-gray-500 mb-2">SELECT DESTINATION</p>
<div class="flex flex-wrap gap-2 mb-6">
<button onclick="ask('Germany full roadmap')" class="border border-blue-500 bg-blue-50 text-blue-700 px-4 py-2 rounded-full text-xs font-bold">🇩🇪 Germany</button>
<button onclick="ask('Canada full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇨🇦 Canada</button>
<button onclick="ask('UK full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇬🇧 UK</button>
<button onclick="ask('USA full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇺🇸 USA</button>
<button onclick="ask('China full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇨🇳 China</button>
<button onclick="ask('Australia full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇦🇺 Australia</button>
<button onclick="ask('Japan full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇯🇵 Japan</button>
<button onclick="ask('South Korea full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇰🇷 South Korea</button>
<button onclick="ask('Malaysia full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇲🇾 Malaysia</button>
<button onclick="ask('Sweden full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇸🇪 Sweden</button>
<button onclick="ask('France full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇫🇷 France</button>
<button onclick="ask('Italy full roadmap')" class="border px-4 py-2 rounded-full text-xs">🇮🇹 Italy</button>
</div>

<p class="text-xs font-bold text-gray-500 mb-2">OUR SERVICES</p>
<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
<button onclick="ask('Tuition transfer SWIFT OUR MT103 guide')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">💸 Tuition Transfer</p></button>
<button onclick="ask('Blocked Account Germany guide')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">🔒 Blocked Account</p></button>
<button onclick="ask('Proof of Funds GIC Canada')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">📄 Proof of Funds</p></button>
<button onclick="ask('Dual currency card EBL BRAC')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">💳 Dual Currency Card</p></button>
<button onclick="ask('Health insurance Germany Canada UK')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">🏥 Health Insurance</p></button>
<button onclick="ask('Student file opening Bangladesh')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">📁 Student File</p></button>
<button onclick="ask('Visa and SEVIS fee payment')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">🛂 Visa & SEVIS Fee</p></button>
<button onclick="ask('Education loan vs proof of funds')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">🏦 Education Loan</p></button>
</div>
</div></div>
<div class="sticky bottom-0 bg-gray-50 pt-3"><div class="bg-white border rounded-2xl p-2 flex gap-2 shadow"><input id="inp" type="text" placeholder="Ask..." class="flex-1 px-4 py-3 rounded-xl focus:outline-none text-sm" onkeypress="if(event.key==='Enter')send()"><button onclick="send()" class="bg-blue-600 text-white px-6 py-3 rounded-xl text-sm font-bold">Send</button></div></div>
</main><script>const chat=document.getElementById('chat');const inp=document.getElementById('inp');
function addMsg(c,isUser){const d=document.createElement('div');d.className=`msg p-4 rounded-2xl ${isUser?'user':'ai'}`;if(isUser)d.innerText=c;else d.innerHTML=marked.parse(c);chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}
function ask(t){inp.value=t;send();}
async function send(){const q=inp.value.trim();if(!q)return;addMsg(q,true);inp.value='';const l=document.createElement('div');l.className='ai msg p-4 rounded-2xl text-gray-400';l.innerHTML='Thinking...';chat.appendChild(l);chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});const d=await r.json();chat.removeChild(l);addMsg(d.answer,false);}catch(e){chat.removeChild(l);addMsg('Error.',false);}}
</script></body></html>"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask_agent():
    q=request.get_json().get("question","")
    try:
        if client:
            resp=client.models.generate_content(model=MODEL, contents=f"Answer: {q}. No intro 'I am AGENT'. {rate()}")
            if "I am StudentFinance AGENT" in resp.text: return jsonify({"answer": router(q)})
            return jsonify({"answer": resp.text})
    except: pass
    return jsonify({"answer": router(q)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))