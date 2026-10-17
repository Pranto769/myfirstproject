import os
import requests
from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

# ====================== CONFIG - FIXED MODEL ======================
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

MODEL_PRIMARY = "gemini-2.0-flash"  # Real, stable model - no more 404
MODEL_FALLBACK = "gemini-1.5-flash"

SYSTEM_PROMPT = """
You are StudentFinance AGENT, a Tool-Enabled Finance AGENT for Tsinghua x WeBank FinTechathon Topic C.
You are NOT a simple chatbot. You use tools.

Tools you have:
- get_live_rate(base, target)
- get_country_checklist(country)
- calculate_total_cost(country, tuition)

Rules:
1. If user asks about Germany/Canada/UK/USA/China etc, call get_country_checklist
2. If user asks about rate, USD, BDT, EUR, cost, call get_live_rate
3. If user asks total cost, call calculate_total_cost
4. Always respond in this format:
   1. Quick Summary
   2. Step-by-Step Roadmap
   3. Cost Breakdown (use tool data)
   4. Important Warnings (Warn about Hundi, recommend OUR code, MT103 receipt)
5. End with: *General guidance only, not official financial advice.*

Keep English, concise, helpful.
"""

# ====================== TOOLS ======================
def get_live_rate(base="USD", target="BDT"):
    try:
        r = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=5)
        rate = r.json()['rates'].get(target)
        return f"1 {base} = {rate:.2f} {target} (Live)"
    except:
        return "Live rate unavailable, est: 1 USD=117 BDT, 1 EUR=126 BDT, 1 CAD=86 BDT"

def get_checklist(country):
    data = {
        "germany": "Admission Letter, Blocked Account €11,208 (Expatrio/Coracle), Health Insurance ~€120/mo, Semesterbeitrag €300, Anabin Check",
        "canada": "LOA, GIC $20,635 (CIBC/Scotia), 6-Month Bank Statement, Tuition Receipt, SOP/LOE",
        "uk": "CAS Letter, 28-Day Bank Statement, TB Test, IHS Fee £1035/yr, English Test",
        "usa": "I-20, SEVIS Fee $350, 6-Month Bank Statement + Affidavit, Sponsor Docs",
        "china": "Admission Notice + JW202, Physical Exam, Proof of Funds ~$5000, Police Clearance",
        "australia": "CoE, GTE Statement, OSHC Health Insurance, Proof of Funds AUD 29,710",
        "japan": "COE, Admission Letter, Bank Solvency $20k+, JLPT/N5 or IELTS",
        "south korea": "Admission Letter, Bank Statement $20k+, TOPIK/IELTS, Medical Check",
        "malaysia": "Offer Letter, EMGS Approval (need 70%+ marks), Medical Screening, Proof of Funds",
        "sweden": "Admission Letter, Proof of Funds SEK 10,314/month x10, Insurance",
        "france": "Campus France Interview, Blocked Account/Proof €7,380, Accommodation Proof",
        "italy": "Universitaly Pre-enrollment, Proof of Funds €6,079, Accommodation + Insurance, CIMEA"
    }
    return data.get(country.lower(), "Passport, Admission Letter, Proof of Funds, Medical, English Proficiency, Police Clearance")

def calculate_total_cost(country, tuition):
    living = {"germany":11208,"canada":20635,"uk":15000,"usa":18000,"china":5000,"australia":21000,"japan":12000,"south korea":10000,"malaysia":8000,"sweden":12000,"france":10000,"italy":8000}
    lv = living.get(country.lower(), 12000)
    try: total = float(tuition) + lv
    except: total = lv
    return f"{country.title()} - Tuition {tuition} + Living ~{lv} = Total ~{total} (plus SWIFT $30, Insurance, Visa fee)"

AGENT_TOOLS = types.Tool(function_declarations=[
    types.FunctionDeclaration(name="get_live_rate", description="Get live FX rate", parameters=types.Schema(type="OBJECT", properties={"base": types.Schema(type="STRING"), "target": types.Schema(type="STRING")}, required=["base","target"])),
    types.FunctionDeclaration(name="get_country_checklist", description="Get checklist for study destination", parameters=types.Schema(type="OBJECT", properties={"country": types.Schema(type="STRING")}, required=["country"])),
    types.FunctionDeclaration(name="calculate_total_cost", description="Calculate total cost", parameters=types.Schema(type="OBJECT", properties={"country": types.Schema(type="STRING"), "tuition": types.Schema(type="NUMBER")}, required=["country","tuition"])),
])

# ====================== UI - 12 COUNTRIES + 8 SERVICES ======================
HTML = """
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>StudentFinance AGENT | Tsinghua x WeBank</title>
<script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>#chat{height:calc(100vh - 240px)}.msg{max-width:85%;line-height:1.6}.user{background:#2563eb;color:#fff;margin-left:auto;border-bottom-right-radius:4px}.ai{background:#fff;border:1px solid #e5e7eb;border-bottom-left-radius:4px}</style>
</head><body class="bg-gray-50">
<header class="bg-white border-b sticky top-0 z-50"><div class="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
<div><h1 class="font-bold text-blue-700">🎓 StudentFinance AGENT</h1><p class="text-xs text-gray-500">Agentic Finance Agent • Tsinghua x WeBank FinTechathon</p></div>
<div class="text-xs bg-green-50 text-green-700 px-3 py-1 rounded-full">● AGENT Mode • Gemini 2.0 Flash</div></div></header>
<main class="max-w-6xl mx-auto px-4 py-4">
<div id="chat" class="overflow-y-auto space-y-4 pb-4">
<div class="ai msg p-5 rounded-2xl">
<p class="font-bold">Hello! I am your Finance AGENT, not just a chatbot.</p><p class="text-sm text-gray-600 mb-3">I autonomously call tools: Live FX, Checklists, Cost Calculator.</p>
<p class="text-xs font-bold text-gray-500 mb-2">STEP 1: SELECT DESTINATION (12 Countries)</p>
<div class="flex flex-wrap gap-2 mb-4">
<button onclick="ask('Full financial roadmap for Germany with Blocked Account')" class="border border-blue-300 text-blue-700 px-3 py-1.5 rounded-full text-xs hover:bg-blue-600 hover:text-white">🇩🇪 Germany</button>
<button onclick="ask('Full financial roadmap for Canada with GIC $20,635')" class="border px-3 py-1.5 rounded-full text-xs hover:bg-blue-50">🇨🇦 Canada</button>
<button onclick="ask('Full roadmap for UK with CAS and 28-day bank statement')" class="border px-3 py-1.5 rounded-full text-xs">🇬🇧 UK</button>
<button onclick="ask('Full roadmap for USA with I-20 and SEVIS')" class="border px-3 py-1.5 rounded-full text-xs">🇺🇸 USA</button>
<button onclick="ask('Full roadmap for China with JW202')" class="border px-3 py-1.5 rounded-full text-xs">🇨🇳 China</button>
<button onclick="ask('Full roadmap for Australia with CoE and GTE')" class="border px-3 py-1.5 rounded-full text-xs">🇦🇺 Australia</button>
<button onclick="ask('Full roadmap for Japan with COE')" class="border px-3 py-1.5 rounded-full text-xs">🇯🇵 Japan</button>
<button onclick="ask('Full roadmap for South Korea')" class="border px-3 py-1.5 rounded-full text-xs">🇰🇷 Korea</button>
<button onclick="ask('Full roadmap for Malaysia with EMGS')" class="border px-3 py-1.5 rounded-full text-xs">🇲🇾 Malaysia</button>
<button onclick="ask('Full roadmap for Sweden')" class="border px-3 py-1.5 rounded-full text-xs">🇸🇪 Sweden</button>
<button onclick="ask('Full roadmap for France with Campus France')" class="border px-3 py-1.5 rounded-full text-xs">🇫🇷 France</button>
<button onclick="ask('Full roadmap for Italy with Universitaly')" class="border px-3 py-1.5 rounded-full text-xs">🇮🇹 Italy</button>
</div>
<p class="text-xs font-bold text-gray-500 mb-2">STEP 2: OUR SERVICES (8 Agent Capabilities)</p>
<div class="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
<button onclick="ask('How to pay tuition via SWIFT with OUR code and keep MT103 receipt?')" class="bg-blue-50 p-3 rounded-xl text-left hover:bg-blue-600 hover:text-white"><p class="text-xs font-bold">💸 Tuition Transfer</p><p class="text-[11px] opacity-70">SWIFT OUR + MT103</p></button>
<button onclick="ask('What is Blocked Account for Germany €11,208? Expatrio vs Coracle vs Deutsche Bank?')" class="bg-green-50 p-3 rounded-xl text-left hover:bg-green-600 hover:text-white"><p class="text-xs font-bold">🔒 Blocked Account</p><p class="text-[11px] opacity-70">Germany €11,208</p></button>
<button onclick="ask('Proof of Funds for Canada GIC $20,635 step-by-step process?')" class="bg-purple-50 p-3 rounded-xl text-left hover:bg-purple-600 hover:text-white"><p class="text-xs font-bold">📄 Proof of Funds</p><p class="text-[11px] opacity-70">GIC & Bank Statement</p></button>
<button onclick="ask('Best dual currency card for Bangladeshi students? EBL vs BRAC vs City?')" class="bg-orange-50 p-3 rounded-xl text-left hover:bg-orange-600 hover:text-white"><p class="text-xs font-bold">💳 Dual Currency Card</p><p class="text-[11px] opacity-70">EBL, BRAC, City</p></button>
<button onclick="ask('Health insurance for students abroad? Germany €120, Canada GuardMe, UK IHS?')" class="bg-red-50 p-3 rounded-xl text-left hover:bg-red-600 hover:text-white"><p class="text-xs font-bold">🏥 Health Insurance</p><p class="text-[11px] opacity-70">Germany, UK, Canada</p></button>
<button onclick="ask('Student file opening cost and process in Bangladesh? What documents?')" class="bg-yellow-50 p-3 rounded-xl text-left hover:bg-yellow-600 hover:text-white"><p class="text-xs font-bold">📁 Student File</p><p class="text-[11px] opacity-70">Bank File Opening</p></button>
<button onclick="ask('Visa fee and SEVIS fee payment process? How to avoid hundi?')" class="bg-indigo-50 p-3 rounded-xl text-left hover:bg-indigo-600 hover:text-white"><p class="text-xs font-bold">🛂 Visa & SEVIS Fee</p><p class="text-[11px] opacity-70">Fee Payment Guide</p></button>
<button onclick="ask('Education loan vs proof of funds? Can I show loan for Canada?')" class="bg-teal-50 p-3 rounded-xl text-left hover:bg-teal-600 hover:text-white"><p class="text-xs font-bold">🏦 Education Loan</p><p class="text-[11px] opacity-70">Loan & Funds</p></button>
</div>
<button onclick="ask('I am new from Bangladesh, I know nothing. Give me complete roadmap for studying abroad finance from zero.')" class="w-full bg-blue-600 text-white font-bold py-2.5 rounded-xl text-sm">✨ I AM NEW - START FROM ZERO</button>
</div></div>
<div class="sticky bottom-0 bg-gray-50 pt-3"><div class="bg-white border rounded-2xl p-2 flex gap-2 shadow"><input id="inp" type="text" placeholder="Ask anything in English..." class="flex-1 px-4 py-3 rounded-xl focus:outline-none text-sm" onkeypress="if(event.key==='Enter')send()"><button onclick="send()" class="bg-blue-600 text-white px-5 py-3 rounded-xl text-sm font-medium">Send</button></div><p class="text-[11px] text-center text-gray-400 mt-2">Outside options: Type any custom question beyond buttons</p></div>
</main>
<script>
const chat=document.getElementById('chat');const inp=document.getElementById('inp');
function addMsg(c,isUser,q=""){const d=document.createElement('div');d.className=`msg p-4 rounded-2xl ${isUser?'user':'ai'}`;if(isUser)d.innerText=c;else d.innerHTML=marked.parse(c);if(!isUser&&q){let rel=[];if(q.toLowerCase().includes('germany'))rel=["What is Semesterbeitrag?","Health insurance €120?","Expatrio vs Coracle?"];else if(q.toLowerCase().includes('canada'))rel=["GIC step-by-step?","6-month bank statement?","SOP for Canada?"];else rel=["Total cost breakdown?","Which bank best for student file?","Hundi risks?"];let h=`<div class="mt-3 pt-3 border-t"><p class="text-xs font-bold text-gray-500 mb-2">🔍 Explore:</p><div class="flex flex-wrap gap-2">`;rel.forEach(r=>h+=`<button onclick="ask('${r}')" class="text-xs bg-blue-50 text-blue-700 border px-3 py-1.5 rounded-full hover:bg-blue-600 hover:text-white">+ ${r}</button>`);h+=`</div></div>`;d.innerHTML+=h;}chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}
function ask(t){inp.value=t;send();}async function send(){const q=inp.value.trim();if(!q)return;addMsg(q,true);inp.value='';const l=document.createElement('div');l.className='ai msg p-4 rounded-2xl text-gray-500';l.innerHTML='🤖 Agent thinking & calling tools...';chat.appendChild(l);chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});const d=await r.json();chat.removeChild(l);addMsg(d.answer,false,q);}catch(e){chat.removeChild(l);addMsg('Error, please try again.',false,"");}}
</script></body></html>
"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask_agent():
    if not client: return jsonify({"answer": "GEMINI_API_KEY missing in Render Environment."})
    q = request.get_json().get("question","")
    try:
        config = types.GenerateContentConfig(tools=[AGENT_TOOLS], system_instruction=SYSTEM_PROMPT)
        response = client.models.generate_content(model=MODEL_PRIMARY, contents=q, config=config)
        # Tool calling check
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    fc = part.function_call
                    out = ""
                    if fc.name == "get_live_rate": out = get_live_rate(fc.args.get("base","USD"), fc.args.get("target","BDT"))
                    elif fc.name == "get_country_checklist": out = get_checklist(fc.args.get("country","germany"))
                    elif fc.name == "calculate_total_cost": out = calculate_total_cost(fc.args.get("country","germany"), fc.args.get("tuition",0))
                    tool_resp = types.Content(role="tool", parts=[types.Part.from_function_response(name=fc.name, response={"result": out})])
                    final = client.models.generate_content(model=MODEL_PRIMARY, contents=[types.Content(role="user", parts=[types.Part.from_text(text=q)]), response.candidates[0].content, tool_resp], config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT))
                    return jsonify({"answer": final.text})
        return jsonify({"answer": response.text})
    except Exception as e:
        print(f"Primary failed {e}")
        try:
            extra = get_live_rate("USD","BDT") + " | " + get_live_rate("EUR","BDT")
            if "germany" in q.lower(): extra += " " + get_checklist("germany")
            if "canada" in q.lower(): extra += " " + get_checklist("canada")
            resp = client.models.generate_content(model=MODEL_FALLBACK, contents=SYSTEM_PROMPT + f"\nUser:{q}\nToolData:{extra}")
            return jsonify({"answer": resp.text})
        except Exception as e2:
            return jsonify({"answer": f"System busy, try again. {str(e2)[:100]}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)