import os
import requests
from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

MODELS_TO_TRY = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-002", "gemini-1.5-pro"]

def get_live_rate(base="USD", target="BDT"):
    try:
        r = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=5)
        rate = r.json()['rates'].get(target)
        return f"1 {base} = {rate:.2f} {target} (Live)"
    except:
        return "Est: 1 USD=117 BDT, 1 EUR=126 BDT"

def get_checklist(country):
    data = {
        "germany": "Blocked Account €11,208 (Expatrio/Coracle), Health Insurance, Semesterbeitrag €300",
        "canada": "GIC $20,635 (CIBC/Scotia), 6-Month Bank Statement, Tuition Receipt",
        "uk": "CAS, 28-Day Bank Statement, TB Test, IHS Fee",
        "usa": "I-20, SEVIS $350, Bank Statement + Affidavit",
        "china": "Admission Notice + JW202, Physical Exam, Proof of Funds",
        "australia": "CoE, GTE Statement, OSHC, Proof AUD 29,710",
        "japan": "COE, Bank Solvency $20k+, JLPT/IELTS",
        "south korea": "Admission Letter, Bank $20k+, TOPIK/IELTS",
        "malaysia": "Offer Letter, EMGS Approval, Medical",
        "sweden": "Admission Letter, Proof SEK 10,314/month",
        "france": "Campus France, Proof €7,380",
        "italy": "Universitaly, Proof €6,079"
    }
    return data.get(country.lower(), "Passport, Admission, Proof of Funds, Medical")

SYSTEM_PROMPT = """
You are StudentFinance AGENT v3.8 Concept Architecture (Powered by Gemini 2.0 Flash).
You are an Agentic Finance Agent for Tsinghua x WeBank FinTechathon Topic C.
You have 3 tools conceptually: Live FX, Checklist, Cost Calculator.
Always answer in:
1. Quick Summary
2. Step-by-Step Roadmap
3. Cost Breakdown
4. Important Warnings (Warn Hundi, Recommend OUR Code, MT103)
End with: *General guidance only, not official financial advice.*
English, concise.
"""

HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>StudentFinance AGENT v3.8</title><script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>#chat{height:calc(100vh - 240px)}.msg{max-width:85%;line-height:1.6}.user{background:#2563eb;color:#fff;margin-left:auto}.ai{background:#fff;border:1px solid #e5e7eb}</style></head>
<body class="bg-gray-50">
<header class="bg-white border-b sticky top-0 z-50"><div class="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
<div><h1 class="font-bold text-blue-700">🎓 StudentFinance AGENT</h1><p class="text-xs text-gray-500">v3.8 Concept Architecture • Tsinghua x WeBank FinTechathon</p></div>
<div class="text-xs bg-blue-600 text-white px-3 py-1.5 rounded-full font-bold">● AGENT Mode • Gemini 3.8 Concept (Powered by 2.0 Flash)</div>
</div></header>
<main class="max-w-6xl mx-auto px-4 py-4"><div id="chat" class="overflow-y-auto space-y-4 pb-4">
<div class="ai msg p-5 rounded-2xl">
<p class="font-bold">Hello! I am StudentFinance AGENT v3.8</p><p class="text-sm text-gray-600 mb-1">Concept Architecture: 3 Tools + 8 Services + 12 Countries + Multi-step Planning</p><p class="text-[11px] text-blue-600 bg-blue-50 p-2 rounded mb-3">Powered by Gemini 2.0 Flash (Latest Stable) • Conceptual Version 3.8 for FinTechathon</p>
<p class="text-xs font-bold text-gray-500 mb-2">STEP 1: DESTINATION (12 Countries)</p>
<div class="flex flex-wrap gap-2 mb-4">
<button onclick="ask('Full roadmap for Germany')" class="border border-blue-300 text-blue-700 px-3 py-1.5 rounded-full text-xs">🇩🇪 Germany</button>
<button onclick="ask('Full roadmap for Canada with GIC')" class="border px-3 py-1.5 rounded-full text-xs">🇨🇦 Canada</button>
<button onclick="ask('Full roadmap for UK')" class="border px-3 py-1.5 rounded-full text-xs">🇬🇧 UK</button>
<button onclick="ask('Full roadmap for USA')" class="border px-3 py-1.5 rounded-full text-xs">🇺🇸 USA</button>
<button onclick="ask('Full roadmap for China')" class="border px-3 py-1.5 rounded-full text-xs">🇨🇳 China</button>
<button onclick="ask('Full roadmap for Australia')" class="border px-3 py-1.5 rounded-full text-xs">🇦🇺 Australia</button>
<button onclick="ask('Full roadmap for Japan')" class="border px-3 py-1.5 rounded-full text-xs">🇯🇵 Japan</button>
<button onclick="ask('Full roadmap for South Korea')" class="border px-3 py-1.5 rounded-full text-xs">🇰🇷 Korea</button>
<button onclick="ask('Full roadmap for Malaysia')" class="border px-3 py-1.5 rounded-full text-xs">🇲🇾 Malaysia</button>
<button onclick="ask('Full roadmap for Sweden')" class="border px-3 py-1.5 rounded-full text-xs">🇸🇪 Sweden</button>
<button onclick="ask('Full roadmap for France')" class="border px-3 py-1.5 rounded-full text-xs">🇫🇷 France</button>
<button onclick="ask('Full roadmap for Italy')" class="border px-3 py-1.5 rounded-full text-xs">🇮🇹 Italy</button>
</div>
<p class="text-xs font-bold text-gray-500 mb-2">STEP 2: OUR SERVICES (8 Agent Capabilities)</p>
<div class="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
<button onclick="ask('Tuition transfer via SWIFT OUR code and MT103?')" class="bg-blue-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">💸 Tuition Transfer</p><p class="text-[10px] opacity-60">SWIFT OUR + MT103</p></button>
<button onclick="ask('Blocked Account for Germany €11,208?')" class="bg-green-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">🔒 Blocked Account</p></button>
<button onclick="ask('Proof of Funds for Canada GIC $20,635?')" class="bg-purple-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">📄 Proof of Funds</p></button>
<button onclick="ask('Best dual currency card? EBL vs BRAC?')" class="bg-orange-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">💳 Dual Currency Card</p></button>
<button onclick="ask('Health insurance for students?')" class="bg-red-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">🏥 Health Insurance</p></button>
<button onclick="ask('Student file opening in Bangladesh?')" class="bg-yellow-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">📁 Student File</p></button>
<button onclick="ask('Visa and SEVIS fee payment?')" class="bg-indigo-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">🛂 Visa & SEVIS</p></button>
<button onclick="ask('Education loan vs proof of funds?')" class="bg-teal-50 p-3 rounded-xl text-left"><p class="text-xs font-bold">🏦 Education Loan</p></button>
</div>
<button onclick="ask('I am new from Bangladesh, give me complete roadmap from zero')" class="w-full bg-blue-600 text-white font-bold py-2.5 rounded-xl text-sm">✨ I AM NEW - START FROM ZERO</button>
</div></div>
<div class="sticky bottom-0 bg-gray-50 pt-3"><div class="bg-white border rounded-2xl p-2 flex gap-2 shadow"><input id="inp" type="text" placeholder="Ask anything..." class="flex-1 px-4 py-3 rounded-xl focus:outline-none text-sm" onkeypress="if(event.key==='Enter')send()"><button onclick="send()" class="bg-blue-600 text-white px-5 py-3 rounded-xl text-sm font-medium">Send</button></div></div></main>
<script>const chat=document.getElementById('chat');const inp=document.getElementById('inp');
function addMsg(c,isUser){const d=document.createElement('div');d.className=`msg p-4 rounded-2xl ${isUser?'user':'ai'}`;if(isUser)d.innerText=c;else d.innerHTML=marked.parse(c);chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}
function ask(t){inp.value=t;send();}async function send(){const q=inp.value.trim();if(!q)return;addMsg(q,true);inp.value='';const l=document.createElement('div');l.className='ai msg p-4 rounded-2xl text-gray-500';l.innerHTML='🤖 AGENT v3.8 thinking...';chat.appendChild(l);chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});const d=await r.json();chat.removeChild(l);addMsg(d.answer,false);}catch(e){chat.removeChild(l);addMsg('Error, try again.',false);}}
</script></body></html>"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask_agent():
    if not api_key: return jsonify({"answer": "GEMINI_API_KEY missing in Render."})
    q = request.get_json().get("question","")
    extra = ""
    if any(x in q.lower() for x in ["rate","usd","bdt","eur","cad"]):
        extra += f"Live Rate: {get_live_rate('USD','BDT')} , {get_live_rate('EUR','BDT')}. "
    for c in ["germany","canada","uk","usa","china","australia","japan","korea","malaysia","sweden","france","italy"]:
        if c in q.lower():
            extra += f" Checklist for {c}: {get_checklist(c)}. "
            break
    full_prompt = f"{SYSTEM_PROMPT}\nTool Data: {extra}\nUser Question: {q}"
    last_error = ""
    for model_name in MODELS_TO_TRY:
        try:
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(full_prompt)
            return jsonify({"answer": resp.text})
        except Exception as e:
            last_error = str(e)
            print(f"Model {model_name} failed: {e}")
            continue
    return jsonify({"answer": f"System Busy. Last error: {last_error[:200]}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)