import os
import requests
from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

# REAL 3.8 MODEL - As per Google's new update
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None
MODEL = "gemini-3.8-flash"

def get_live_rate(base="USD", target="BDT"):
    try:
        r = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=5)
        return f"1 {base} = {r.json()['rates'].get(target):.2f} {target} (Live)"
    except:
        return "Est: 1 USD=117 BDT, 1 EUR=126 BDT"

def get_checklist(c):
    d = {"germany":"Blocked €11,208 (Expatrio), Health Insurance","canada":"GIC $20,635, 6-Month Statement","uk":"CAS, 28-Day Statement","usa":"I-20, SEVIS $350","china":"JW202, Physical Exam","australia":"CoE, GTE, OSHC","japan":"COE, $20k Solvency","south korea":"Admission, $20k","malaysia":"EMGS, Medical","sweden":"SEK 10,314/mo","france":"Campus France, €7,380","italy":"Universitaly, €6,079"}
    return d.get(c.lower(),"Passport, Admission, Proof of Funds, Medical")

SYSTEM = "You are StudentFinance AGENT v3.8, Tsinghua x WeBank FinTechathon. Tools: Live FX, Checklist. Answer in 1. Quick Summary 2. Roadmap 3. Cost Breakdown 4. Warnings (Hundi, OUR code, MT103). End with *General guidance only.* English, concise."

HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>AGENT v3.8</title><script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script><style>#chat{height:calc(100vh - 240px)}.msg{max-width:85%}.user{background:#2563eb;color:#fff;margin-left:auto}.ai{background:#fff;border:1px solid #e5e7eb}</style></head>
<body class="bg-gray-50"><header class="bg-white border-b sticky top-0 z-50"><div class="max-w-6xl mx-auto px-4 py-3 flex justify-between"><div><h1 class="font-bold text-blue-700">🎓 StudentFinance AGENT v3.8</h1><p class="text-xs text-gray-500">Real Gemini 3.8 Flash • Tsinghua x WeBank</p></div><div class="text-xs bg-green-600 text-white px-3 py-1.5 rounded-full font-bold">● AGENT Live • Gemini 3.8 Flash</div></div></header>
<main class="max-w-6xl mx-auto px-4 py-4"><div id="chat" class="overflow-y-auto space-y-4 pb-4"><div class="ai msg p-5 rounded-2xl"><p class="font-bold">Hello! I am AGENT v3.8 - Real Model!</p><p class="text-xs bg-green-50 text-green-700 p-2 rounded mb-3">✅ Powered by Real gemini-3.8-flash (Google's Latest)</p>
<div class="flex flex-wrap gap-2 mb-4">
<button onclick="ask('Germany full roadmap')" class="border border-blue-300 text-blue-700 px-3 py-1.5 rounded-full text-xs">🇩🇪 Germany</button>
<button onclick="ask('Canada GIC full roadmap')" class="border px-3 py-1.5 rounded-full text-xs">🇨🇦 Canada</button>
<button onclick="ask('UK full roadmap')" class="border px-3 py-1.5 rounded-full text-xs">🇬🇧 UK</button>
<button onclick="ask('USA full roadmap')" class="border px-3 py-1.5 rounded-full text-xs">🇺🇸 USA</button>
<button onclick="ask('China full roadmap')" class="border px-3 py-1.5 rounded-full text-xs">🇨🇳 China</button>
<button onclick="ask('Australia full roadmap')" class="border px-3 py-1.5 rounded-full text-xs">🇦🇺 Australia</button>
<button onclick="ask('Japan full roadmap')" class="border px-3 py-1.5 rounded-full text-xs">🇯🇵 Japan</button>
<button onclick="ask('South Korea full roadmap')" class="border px-3 py-1.5 rounded-full text-xs">🇰🇷 Korea</button>
<button onclick="ask('Malaysia EMGS roadmap')" class="border px-3 py-1.5 rounded-full text-xs">🇲🇾 Malaysia</button>
<button onclick="ask('Sweden full roadmap')" class="border px-3 py-1.5 rounded-full text-xs">🇸🇪 Sweden</button>
<button onclick="ask('France Campus France')" class="border px-3 py-1.5 rounded-full text-xs">🇫🇷 France</button>
<button onclick="ask('Italy Universitaly')" class="border px-3 py-1.5 rounded-full text-xs">🇮🇹 Italy</button>
</div><div class="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
<button onclick="ask('Tuition SWIFT OUR MT103')" class="bg-blue-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">💸 Tuition</p></button>
<button onclick="ask('Blocked Account Germany')" class="bg-green-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">🔒 Blocked Account</p></button>
<button onclick="ask('Proof of Funds GIC')" class="bg-purple-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">📄 Proof of Funds</p></button>
<button onclick="ask('Dual currency card EBL BRAC')" class="bg-orange-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">💳 Card</p></button>
<button onclick="ask('Health insurance')" class="bg-red-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">🏥 Insurance</p></button>
<button onclick="ask('Student file opening')" class="bg-yellow-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">📁 Student File</p></button>
<button onclick="ask('Visa SEVIS fee')" class="bg-indigo-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">🛂 Visa Fee</p></button>
<button onclick="ask('Education loan')" class="bg-teal-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">🏦 Loan</p></button>
</div><button onclick="ask('I am new from Bangladesh, complete roadmap from zero')" class="w-full bg-blue-600 text-white font-bold py-2.5 rounded-xl text-sm">✨ I AM NEW - START FROM ZERO</button></div></div>
<div class="sticky bottom-0 bg-gray-50 pt-3"><div class="bg-white border rounded-2xl p-2 flex gap-2 shadow"><input id="inp" type="text" placeholder="Ask..." class="flex-1 px-4 py-3 rounded-xl focus:outline-none text-sm" onkeypress="if(event.key==='Enter')send()"><button onclick="send()" class="bg-blue-600 text-white px-5 py-3 rounded-xl text-sm">Send</button></div></div></main>
<script>const chat=document.getElementById('chat');const inp=document.getElementById('inp');
function addMsg(c,isUser){const d=document.createElement('div');d.className=`msg p-4 rounded-2xl ${isUser?'user':'ai'}`;if(isUser)d.innerText=c;else d.innerHTML=marked.parse(c);chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}
function ask(t){inp.value=t;send();}async function send(){const q=inp.value.trim();if(!q)return;addMsg(q,true);inp.value='';const l=document.createElement('div');l.className='ai msg p-4 rounded-2xl text-gray-500';l.innerHTML='🤖 AGENT v3.8 thinking...';chat.appendChild(l);chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});const d=await r.json();chat.removeChild(l);addMsg(d.answer,false);}catch(e){chat.removeChild(l);addMsg('Error.',false);}}
</script></body></html>"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask_agent():
    if not client: return jsonify({"answer": "GEMINI_API_KEY missing"})
    q = request.get_json().get("question","")
    extra = f"{get_live_rate('USD','BDT')} {get_live_rate('EUR','BDT')}"
    for c in ["germany","canada","uk","usa","china","australia","japan","korea","malaysia","sweden","france","italy"]:
        if c in q.lower():
            extra += f" Checklist {c}: {get_checklist(c)}"
            break
    try:
        resp = client.models.generate_content(model=MODEL, contents=f"{SYSTEM}\nToolData:{extra}\nQuestion:{q}")
        return jsonify({"answer": resp.text})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)[:300]}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))