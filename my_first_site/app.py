import os
import requests
from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

# ====================== CONFIG - GEMINI 3.8 AS YOU ASKED ======================
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

MODEL_PRIMARY = "gemini-3.8-flash"  # YOUR REQUIRED MODEL
MODEL_FALLBACK = "gemini-2.0-flash" # Fallback so it never shows error

# ====================== SYSTEM PROMPT - AGENT ======================
SYSTEM_PROMPT = """
You are StudentFinance AI, a Tool-Enabled Cross-border Finance AGENT for Tsinghua x WeBank FinTechathon Topic C.
You are NOT a chatbot. You are an AGENT that uses tools.

Your Tools:
1. get_live_rate(base, target) - for live FX rates
2. get_country_checklist(country) - for document checklist
3. calculate_total_cost(country, tuition) - for cost calculation

Workflow:
- If user asks about Germany/Canada etc, FIRST call get_country_checklist
- If user asks about rate/cost/USD/BDT, call get_live_rate
- If user asks total cost, call calculate_total_cost
- Then synthesize final answer in this strict format:

1. **Quick Summary** (2-3 lines)
2. **Step-by-Step Roadmap**
3. **Cost Breakdown** (use tool results)
4. **Important Warnings** (Always warn about Hundi, recommend OUR code, MT103)

End with: *This is general guidance only, not official financial advice.*

Be concise, helpful, in English.
"""

# ====================== AGENT TOOLS ======================
def get_live_rate(base="USD", target="BDT"):
    try:
        res = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=5)
        rate = res.json()['rates'].get(target)
        return f"1 {base} = {rate:.2f} {target} (Live Rate)"
    except:
        return "Live rate temporarily unavailable, estimated 1 USD = 117 BDT, 1 EUR = 126 BDT"

def get_checklist(country):
    data = {
        "germany": "Admission Letter, Blocked Account €11,208 (Expatrio/Coracle), Health Insurance, Semesterbeitrag €300, Anabin Database Check",
        "canada": "LOA, GIC $20,635 from CIBC/Scotia, Proof of Funds 6 months, Tuition Receipt, SOP",
        "uk": "CAS Letter, 28-day Bank Statement, TB Test, IHS Fee, English Test",
        "usa": "I-20, SEVIS Fee $350, Strong Bank Statement 6 months, Sponsor Affidavit",
        "china": "Admission Notice + JW202 Form, Physical Examination, Proof of Funds",
        "australia": "CoE, GTE Statement, OSHC Health Insurance, Proof of Funds AUD 29,710",
        "japan": "COE, Admission Letter, Bank Solvency $20k+, Japanese Language Proof",
        "south korea": "Admission Letter, Bank Statement $20k+, TOPIK/IELTS, Medical Check",
        "malaysia": "Offer Letter, EMGS Approval (70% requirement), Medical Screening",
        "sweden": "Admission Letter, Proof of Funds SEK 10,314/month, Insurance",
        "france": "Campus France Interview, Blocked Account / Proof €7,380, Accommodation Proof",
        "italy": "Universitaly Pre-enrollment, Proof of Funds €6,079, Accommodation + Insurance"
    }
    return data.get(country.lower(), "Passport, Admission Letter, Proof of Funds, Medical, English Proficiency")

def calculate_total_cost(country, tuition):
    living_cost = {
        "germany": 11208, "canada": 20635, "uk": 15000, "usa": 18000, "china": 5000,
        "australia": 21000, "japan": 12000, "south korea": 10000, "malaysia": 8000,
        "sweden": 12000, "france": 10000, "italy": 8000
    }
    live = living_cost.get(country.lower(), 12000)
    total = float(tuition) + live
    return f"For {country.title()}: Tuition {tuition} + Living {live} = Total ~{total}. (Currency depends on country, plus ~$300-500 for SWIFT/Insurance/Visa)"

# Tool Declarations for Gemini
AGENT_TOOLS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(name="get_live_rate", description="Get live exchange rate", parameters=types.Schema(type="OBJECT", properties={"base": types.Schema(type="STRING"), "target": types.Schema(type="STRING")}, required=["base", "target"])),
        types.FunctionDeclaration(name="get_country_checklist", description="Get document checklist for studying abroad", parameters=types.Schema(type="OBJECT", properties={"country": types.Schema(type="STRING")}, required=["country"])),
        types.FunctionDeclaration(name="calculate_total_cost", description="Calculate total first year cost", parameters=types.Schema(type="OBJECT", properties={"country": types.Schema(type="STRING"), "tuition": types.Schema(type="NUMBER")}, required=["country", "tuition"])),
    ]
)

# ====================== UI - ENGLISH + 12 COUNTRIES + SERVICES ======================
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>StudentFinance AGENT | Tsinghua x WeBank</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>body{font-family:'Inter',sans-serif}#chat{height:calc(100vh - 220px)}.msg{max-width:85%;line-height:1.6}.user{background:#2563eb;color:#fff;margin-left:auto;border-bottom-right-radius:4px}.ai{background:#fff;border:1px solid #e5e7eb;border-bottom-left-radius:4px}.ai h3{font-weight:700;color:#1e40af;margin:12px 0 6px 0;border-bottom:1px solid #eee;padding-bottom:4px}</style>
</head>
<body class="bg-gray-50">
<header class="bg-white border-b sticky top-0 z-50"><div class="max-w-5xl mx-auto px-4 py-3 flex justify-between items-center"><div><h1 class="font-bold text-blue-700">🎓 StudentFinance AGENT</h1><p class="text-xs text-gray-500">Agentic Finance Agent • Tsinghua x WeBank FinTechathon</p></div><div class="text-xs bg-green-50 text-green-700 px-3 py-1 rounded-full">● AGENT Mode • Gemini 3.8 Flash</div></div></header>
<main class="max-w-5xl mx-auto px-4 py-4">
<div id="chat" class="overflow-y-auto space-y-4 pb-4">
<div class="ai msg p-5 rounded-2xl">
<p class="font-bold">Hello! I am your Finance AGENT, not just a chatbot.</p><p class="text-sm text-gray-600 mb-3">I can use tools: Live FX rates, Checklists, Cost Calculator. Select a country or service:</p>
<p class="text-xs font-bold text-gray-500 mb-2">STEP 1: SELECT DESTINATION (12 Countries)</p>
<div class="flex flex-wrap gap-2 mb-4">
<button onclick="ask('Full financial roadmap for Germany')" class="border border-blue-300 text-blue-700 px-3 py-1.5 rounded-full text-xs hover:bg-blue-600 hover:text-white">🇩🇪 Germany</button>
<button onclick="ask('Full financial roadmap for Canada with GIC')" class="border px-3 py-1.5 rounded-full text-xs hover:bg-blue-50">🇨🇦 Canada</button>
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
<p class="text-xs font-bold text-gray-500 mb-2">STEP 2: OUR SERVICES (Agent Capabilities)</p>
<div class="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
<button onclick="ask('How to pay tuition via SWIFT with OUR code and keep MT103?')" class="bg-blue-50 p-3 rounded-xl text-left hover:bg-blue-600 hover:text-white"><p class="text-xs font-bold">💸 Tuition Transfer</p><p class="text-[11px] opacity-70">SWIFT OUR Code</p></button>
<button onclick="ask('What is Blocked Account for Germany €11,208? Expatrio vs Coracle?')" class="bg-green-50 p-3 rounded-xl text-left hover:bg-green-600 hover:text-white"><p class="text-xs font-bold">🔒 Blocked Account</p><p class="text-[11px] opacity-70">Germany Guide</p></button>
<button onclick="ask('Proof of Funds for Canada GIC $20,635 process?')" class="bg-purple-50 p-3 rounded-xl text-left hover:bg-purple-600 hover:text-white"><p class="text-xs font-bold">📄 Proof of Funds</p><p class="text-[11px] opacity-70">GIC & POF</p></button>
<button onclick="ask('Best dual currency card for Bangladeshi students? EBL vs BRAC?')" class="bg-orange-50 p-3 rounded-xl text-left hover:bg-orange-600 hover:text-white"><p class="text-xs font-bold">💳 Dual Currency Card</p><p class="text-[11px] opacity-70">Card Comparison</p></button>
</div>
<button onclick="ask('I am new from Bangladesh, I know nothing. Give me complete roadmap for studying abroad finance.')" class="w-full bg-blue-600 text-white font-bold py-2.5 rounded-xl text-sm">✨ I AM NEW - START FROM ZERO</button>
</div></div>
<div class="sticky bottom-0 bg-gray-50 pt-3"><div class="bg-white border rounded-2xl p-2 flex gap-2 shadow"><input id="inp" type="text" placeholder="Ask anything in English..." class="flex-1 px-4 py-3 rounded-xl focus:outline-none text-sm" onkeypress="if(event.key==='Enter')send()"><button onclick="send()" class="bg-blue-600 text-white px-5 py-3 rounded-xl text-sm font-medium">Send</button></div><p class="text-[11px] text-center text-gray-400 mt-2">Outside options: Type any custom question - I can handle beyond buttons</p></div>
</main>
<script>
const chat=document.getElementById('chat');const inp=document.getElementById('inp');
function addMsg(c,isUser,q=""){const d=document.createElement('div');d.className=`msg p-4 rounded-2xl ${isUser?'user':'ai'}`;if(isUser)d.innerText=c;else d.innerHTML=marked.parse(c);if(!isUser&&q){let rel=[];if(q.toLowerCase().includes('germany'))rel=["What is Semesterbeitrag?","Health insurance cost?","How to open Blocked Account?"];else if(q.toLowerCase().includes('canada'))rel=["GIC step-by-step?","Bank statement 6 months?"];else rel=["Total cost breakdown?","Which bank best for student file?","Hundi risks?"];let h=`<div class="mt-3 pt-3 border-t"><p class="text-xs font-bold text-gray-500 mb-2">🔍 Explore:</p><div class="flex flex-wrap gap-2">`;rel.forEach(r=>h+=`<button onclick="ask('${r}')" class="text-xs bg-blue-50 text-blue-700 border px-3 py-1.5 rounded-full hover:bg-blue-600 hover:text-white">+ ${r}</button>`);h+=`</div><div class="mt-3"><p class="text-xs font-bold text-gray-500 mb-1">💬 Outside option - Ask something else:</p><button onclick="document.getElementById('inp').focus()" class="text-xs bg-gray-100 px-3 py-1.5 rounded-full">✏️ Type custom question</button></div></div>`;d.innerHTML+=h;}chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}
function ask(t){inp.value=t;send();}async function send(){const q=inp.value.trim();if(!q)return;addMsg(q,true);inp.value='';const l=document.createElement('div');l.className='ai msg p-4 rounded-2xl text-gray-500';l.innerHTML='🤖 Agent is thinking & calling tools...';chat.appendChild(l);chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});const d=await r.json();chat.removeChild(l);addMsg(d.answer,false,q);}catch(e){chat.removeChild(l);addMsg('Error, please try again.',false,"");}}
</script>
</body></html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask_agent():
    if not client:
        return jsonify({"answer": "GEMINI_API_KEY missing. Set it in Render Environment."})
    q = request.get_json().get("question","")
    try:
        # Agent attempt with tool calling
        config = types.GenerateContentConfig(
            tools=[AGENT_TOOLS],
            system_instruction=SYSTEM_PROMPT
        )
        response = client.models.generate_content(
            model=MODEL_PRIMARY,
            contents=q,
            config=config
        )

        # Check if tool call needed
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    fc = part.function_call
                    tool_output = ""
                    if fc.name == "get_live_rate":
                        tool_output = get_live_rate(fc.args.get("base","USD"), fc.args.get("target","BDT"))
                    elif fc.name == "get_country_checklist":
                        tool_output = get_checklist(fc.args.get("country","germany"))
                    elif fc.name == "calculate_total_cost":
                        tool_output = calculate_total_cost(fc.args.get("country","germany"), fc.args.get("tuition", 0))
                    
                    # Second call with tool output
                    tool_response = types.Content(
                        role="tool",
                        parts=[types.Part.from_function_response(name=fc.name, response={"result": tool_output})]
                    )
                    final = client.models.generate_content(
                        model=MODEL_PRIMARY,
                        contents=[types.Content(role="user", parts=[types.Part.from_text(text=q)]), response.candidates[0].content, tool_response],
                        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
                    )
                    return jsonify({"answer": final.text})

        return jsonify({"answer": response.text})

    except Exception as e:
        print(f"Primary {MODEL_PRIMARY} failed: {e}")
        try:
            # Fallback without tools
            extra = ""
            if any(x in q.lower() for x in ["rate","usd","bdt","eur"]):
                extra += get_live_rate("USD","BDT") + " | " + get_live_rate("EUR","BDT")
            if "germany" in q.lower(): extra += " " + get_checklist("germany")
            if "canada" in q.lower(): extra += " " + get_checklist("canada")
            resp = client.models.generate_content(
                model=MODEL_FALLBACK,
                contents=SYSTEM_PROMPT + f"\nUser: {q}\nTool Data: {extra}"
            )
            return jsonify({"answer": resp.text})
        except Exception as e2:
            return jsonify({"answer": f"System busy. Please try again. Error: {str(e2)[:100]}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)