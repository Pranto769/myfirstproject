import os
from collections import defaultdict, deque
from flask import Flask, request, jsonify, render_template_string
app = Flask(__name__)

# ========== MEMORY SYSTEM (Same as before) ==========
conversation_memory = defaultdict(lambda: deque(maxlen=5))

try:
    from google import genai
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else None
    print(f"Client init: {bool(client)} Has key: {bool(api_key)}")
except Exception as e:
    print(f"GenAI init fail: {e}")
    client = None

# ========== SMART FALLBACK - All Country Big Answer (Same) ==========
def get_smart_answer(q, history_text=""):
    ql = q.lower()
    combined = (history_text + " " + ql).lower()
    footer = "\n\n**Golden Rules BD:**\n1. Student File 10k BDT at EBL/BRAC AD\n2. Always SWIFT OUR (+$30)\n3. Use YOUR OWN Dual Card\n4. Keep MT103"

    if "germany" in combined or "german" in combined:
        return "### 🇩🇪 Germany Full Roadmap\n**Uni:** Public FREE! Uni-Assist €75. IELTS 6.5, HSC 3.5+\n**Blocked:** €11,208 via Expatrio €49. Your money, back €934/mo\n**Docs:** Passport, Academic, IELTS, Motivation, CV, Blocked Proof\n**Student File:** EBL Dhanmondi 10k BDT\n**Health:** €120/mo Mawista\n**Visa:** VFS Dhaka €75 + Blocked + Health + Admission\n**Total Show:** ~€13,500" + footer
    if "canada" in combined:
        return "### 🇨🇦 Canada Full Roadmap\n**Uni:** IELTS 6.5, HSC 4.0+. Tuition $15k-25k CAD\n**GIC:** $20,635 CAD via CIBC/Scotia (SDS Must) Back $1,400/mo\n**Tuition:** Pay 1st year via SWIFT OUR from Student File\n**Docs:** Offer, GIC, Tuition Receipt, IELTS, Medical, PCC, SOP, Solvency 40L+\n**Visa:** $150+85 Bio\n**Total Show:** GIC + Tuition $15k + Flight" + footer
    if "uk" in combined or "england" in combined:
        return "### 🇬🇧 UK Full Roadmap\n**Uni:** IELTS 6.0-6.5, HSC 3.5+. Tuition £12k-18k. CAS 2 weeks\n**Funds:** 28 days statement - Tuition + £9,207 (outside London) / £12,006 (London)\n**Docs:** CAS, Bank 28 days, IELTS, TB Test\n**Visa:** £490 + IHS £1035/year\n**Total:** Tuition £12k + Living £9k + Visa" + footer
    if "usa" in combined or "america" in combined:
        return "### 🇺🇸 USA Full Roadmap\n**Uni:** IELTS 6.5/TOEFL 80. Tuition $15k-30k. Get I-20\n**SEVIS:** $350 at fmjfee.com via Dual Card\n**Funds:** Solvency $40k-50k, 6 months statement\n**Visa:** DS-160 + MRV $185 + Interview US Embassy Dhaka\n**Docs:** I-20, SEVIS, MRV, Bank, Academic, IELTS, Property\n**Total:** SEVIS $350+MRV $185+Tuition $15k+Flight $900" + footer
    if "australia" in combined:
        return "### 🇦🇺 Australia Roadmap\n**Uni:** IELTS 6.5. Tuition AUD 20k-35k\n**Funds:** Show AUD 29k Living+Tuition=~AUD 50k 3 months bank\n**Health:** OSHC AUD 600/year\n**Visa:** Subclass 500 AUD 710\n**Transfer:** SWIFT OUR" + footer
    if "japan" in combined:
        return "### 🇯🇵 Japan Roadmap\n**Uni:** IELTS 5.5-6.0, Japanese N4. Tuition $5k-8k\n**Funds:** Sponsor Affidavit + Bank $15k + Tuition\n**Docs:** COE, Academic, Passport, Financial\n**Visa:** $50\n**Transfer:** SWIFT OUR" + footer
    if "korea" in combined:
        return "### 🇰🇷 South Korea Roadmap\n**Uni:** IELTS 5.5-6.0, TOPIK. Tuition $4k-7k\n**Funds:** Bank $18k 6 months\n**Visa:** $50\n**Transfer:** SWIFT OUR" + footer
    if "sweden" in combined:
        return "### 🇸🇪 Sweden Roadmap\n**Uni:** IELTS 6.5. Tuition €8k-15k\n**Funds:** €10k/year living + tuition show\n**Visa:** €150\n**Transfer:** SWIFT OUR" + footer
    if "france" in combined:
        return "### 🇫🇷 France Roadmap\n**Uni:** IELTS 6.0. Tuition Public €3k-5k, Private €8k-15k\n**Funds:** €12k/year + tuition\n**Visa:** €100\n**Transfer:** SWIFT OUR" + footer
    if "italy" in combined:
        return "### 🇮🇹 Italy Roadmap\n**Uni:** IELTS 6.0. Tuition €1k-4k Public\n**Funds:** €9k/year + tuition\n**Visa:** €50\n**Transfer:** SWIFT OUR" + footer
    if "malaysia" in combined:
        return "### 🇲🇾 Malaysia Roadmap\n**Uni:** IELTS 5.5. Tuition $3k-6k\n**Funds:** Bank $8k-10k\n**Visa:** EMGS $300\n**Transfer:** SWIFT OUR" + footer
    if "china" in combined:
        return "### 🇨🇳 China Roadmap\n**Uni:** IELTS 5.5. Tuition $2k-5k, Many Scholarship\n**Funds:** $10k bank + Sponsor\n**Visa:** $50\n**Transfer:** SWIFT OUR" + footer
    if "tuition" in combined or "swift" in combined or "our" in combined or "mt103" in combined:
        return "### 💸 Tuition Transfer - ALWAYS OUR\n1. Student File at EBL/BRAC AD - 10k BDT - Docs: Passport, Offer, NID\n2. Tell Bank: MT103 with OUR (+$25-45 extra)\n3. OUR=Correct, SHA=University gets less & Short Payment\n4. Collect MT103, email to uni finance\n5. Time 2-3 days" + footer
    if "student file" in combined:
        return "### 📁 Student File Opening\nMandatory for Bangladesh Bank. Where: EBL Dhanmondi Best. Docs: Passport, Offer Letter, NID, Photo. Cost 8k-15k BDT. Time 1 day." + footer
    if "visa" in ql or "sevis" in ql:
        if any(x in combined for x in ["usa","america"]):
            return "### 🛂 USA Visa\nSEVIS $350 + MRV $185 = $535 via own Dual Card. Docs: I-20, SEVIS Receipt, MRV, Bank Solvency $40k, Interview at US Embassy." + footer
        return "### 🛂 Visa & SEVIS\nUSA: $350+185. Germany: €75. UK: £490+IHS £1035. Canada: $150+85. Always use own card." + footer
    if "total" in ql and ("fee" in ql or "cost" in ql or "koto" in ql):
        if any(x in combined for x in ["usa","america"]):
            return "### 🇺🇸 USA Total Cost\nTuition $15k + SEVIS $350 + MRV $185 + Flight $900 + Health $800 + Student File 10k BDT = ~$17k first year show. Living $12k/year extra." + footer
        if "germany" in combined:
            return "### 🇩🇪 Germany Total\nBlocked €11,208 (your money back) + Tuition FREE Public + Health €1440/year + Visa €75 + Flight €700 + File 10k BDT = ~€13,500 show, actual spend €3k." + footer
        return f"### 💰 Total Cost\nGermany: ~€13,500 show (Blocked is yours). Canada: GIC $20,635+Tuition $15k. UK: £21k+. USA: $17k+. Includes Tuition+Living+Visa+Flight+File 10k BDT." + footer
    return f"### 🎓 Expert for: {q}\n**Any Country:**\n1. Uni: Public cheap - IELTS 6.0-6.5\n2. Proof: Germany Blocked €11,208, Canada GIC $20,635, UK Bank £15k 28 days, USA Solvency $40k\n3. File: EBL/BRAC AD 10k BDT\n4. Transfer: Always SWIFT OUR +$30\n5. Visa: Admission+Financial+Health+Academic" + footer

def get_ai(q, client_ip, history_list):
    history_text = " ".join([h['q'] for h in history_list]) if history_list else ""
    if not client:
        return get_smart_answer(q, history_text)
    # SAME MODEL LIST - 3.8 INCLUDED, NO CHANGE
    models_to_try = ["gemini-2.5-flash-lite", "gemini-2.0-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]
    full_prompt = ""
    if history_list:
        full_prompt += "Conversation history (remember this):\n"
        for h in history_list[-3:]:
            full_prompt += f"User: {h['q']}\nAssistant: {h['a'][:400]}\n"
        full_prompt += "\n"
    full_prompt += f"Current user question: {q}\n\nInstruction: If current question is short like 'total fee?', 'visa cost?', use country from history. Give detailed markdown answer for Bangladeshi students. Keep answer big and helpful."
    for model_name in models_to_try:
        try:
            print(f"Trying model: {model_name} for IP {client_ip} Q: {q}")
            res = client.models.generate_content(model=model_name, contents=full_prompt)
            print(f"AI OK with {model_name}")
            return res.text
        except Exception as e:
            print(f"Failed {model_name}: {e}")
            continue
    print("All AI failed, using fallback with history")
    return get_smart_answer(q, history_text)

# ========== NEW BEAUTIFUL DESIGN - White Removed ==========
HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>StudentFinance - Study Abroad Expert</title>
<script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{font-family:'Plus Jakarta Sans',sans-serif}
#chat{height:calc(100vh - 300px)}
.msg{max-width:85%;animation:slideIn .3s ease}
@keyframes slideIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.user{background:linear-gradient(135deg,#2563eb,#7c3aed);color:#fff;margin-left:auto;box-shadow:0 8px 20px rgba(37,99,235,.3)}
.ai{background:#fff;border:1px solid #eef2ff;box-shadow:0 4px 20px rgba(0,0,0,.05)}
.glass{background:rgba(255,255,255,.8);backdrop-filter:blur(20px)}
.btn-country{background:#fff;border:1px solid #e0e7ff;transition:all .2s}
.btn-country:hover{background:linear-gradient(135deg,#eef2ff,#f5f3ff);border-color:#6366f1;transform:translateY(-2px);box-shadow:0 6px 15px rgba(99,102,241,.2)}
.service-card{background:linear-gradient(135deg,#fff,#f8fafc);border:1px solid #f1f5f9;transition:all .2s}
.service-card:hover{transform:translateY(-3px);box-shadow:0 10px 25px rgba(0,0,0,.08);border-color:#c7d2fe}
</style></head>
<body class="bg-[#f8f9ff] min-h-screen">
<!-- Header with Gradient -->
<header class="sticky top-0 z-20 glass border-b border-indigo-50">
<div class="max-w-6xl mx-auto px-4 md:px-6 py-4 flex justify-between items-center">
<div class="flex items-center gap-3">
<div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-600 to-violet-600 flex items-center justify-center text-white font-bold text-lg">🎓</div>
<div><h1 class="font-bold text-[16px] text-slate-800 tracking-tight">StudentFinance</h1><p class="text-[11px] text-slate-500 -mt-1">Expert Finance & Visa Guidance</p></div>
</div>
<div class="flex items-center gap-2"><span class="hidden md:block text-[11px] text-slate-500">For Bangladeshi Students</span><span class="text-[11px] bg-emerald-50 text-emerald-700 border border-emerald-100 px-3 py-1.5 rounded-full font-semibold">● Online</span></div>
</div>
</header>

<main class="max-w-6xl mx-auto px-4 md:px-6 py-6">
<div id="chat" class="overflow-y-auto space-y-4 pb-4 pr-1">
<!-- Welcome Card - NEW DESIGN, NO MEMORY FIXED TEXT -->
<div class="ai msg p-0 rounded-[24px] overflow-hidden">
<div class="bg-gradient-to-br from-indigo-600 via-blue-600 to-violet-600 p-6 md:p-7 text-white relative overflow-hidden">
<div class="absolute top-0 right-0 w-40 h-40 bg-white/10 rounded-full -mr-16 -mt-16"></div>
<div class="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-10 -mb-10"></div>
<div class="relative z-10">
<h2 class="font-bold text-[20px] leading-tight">Welcome to StudentFinance ✨</h2>
<p class="text-[13px] text-blue-100 mt-2 leading-relaxed">Your trusted partner for studying abroad. Get complete roadmap for tuition, blocked account, GIC, visa & student file — specially designed for Bangladeshi students.</p>
<div class="mt-4 flex gap-2">
<span class="text-[10px] bg-white/20 px-2.5 py-1 rounded-full">🇩🇪 Germany FREE</span>
<span class="text-[10px] bg-white/20 px-2.5 py-1 rounded-full">🇨🇦 Canada SDS</span>
<span class="text-[10px] bg-white/20 px-2.5 py-1 rounded-full">🇺🇸 USA F1</span>
</div>
</div>
</div>
<div class="p-5 md:p-6 bg-white">
<p class="text-[11px] font-bold text-indigo-600 tracking-widest mb-3">🚀 START YOUR JOURNEY</p>
<button onclick="ask('I am new, I know nothing, give me complete guideline from zero for studying abroad from Bangladesh')" class="w-full bg-gradient-to-r from-emerald-500 to-teal-600 text-white px-4 py-3.5 rounded-2xl text-[13px] font-bold shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/30 transition-all">🌟 I'm New - Show Me Complete Guideline</button>

<p class="text-[11px] font-bold text-slate-400 tracking-widest mt-7 mb-3">🌍 CHOOSE DESTINATION</p>
<div class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2.5">
<button onclick="ask('Germany full roadmap')" class="btn-country px-3 py-3 rounded-2xl text-[12px] font-semibold text-slate-700">🇩🇪 Germany</button>
<button onclick="ask('Canada full roadmap')" class="btn-country px-3 py-3 rounded-2xl text-[12px] font-semibold text-slate-700">🇨🇦 Canada</button>
<button onclick="ask('UK full roadmap')" class="btn-country px-3 py-3 rounded-2xl text-[12px] font-semibold text-slate-700">🇬🇧 UK</button>
<button onclick="ask('USA full roadmap')" class="btn-country px-3 py-3 rounded-2xl text-[12px] font-semibold text-slate-700">🇺🇸 USA</button>
<button onclick="ask('Australia full roadmap')" class="btn-country px-3 py-3 rounded-2xl text-[12px] font-semibold text-slate-700">🇦🇺 Australia</button>
<button onclick="ask('Japan full roadmap')" class="btn-country px-3 py-3 rounded-2xl text-[12px] font-semibold text-slate-700">🇯🇵 Japan</button>
<button onclick="ask('South Korea full roadmap')" class="btn-country px-3 py-3 rounded-2xl text-[12px] font-semibold text-slate-700">🇰🇷 Korea</button>
<button onclick="ask('Malaysia full roadmap')" class="btn-country px-3 py-3 rounded-2xl text-[12px] font-semibold text-slate-700">🇲🇾 Malaysia</button>
<button onclick="ask('Sweden full roadmap')" class="btn-country px-3 py-3 rounded-2xl text-[12px] font-semibold text-slate-700">🇸🇪 Sweden</button>
<button onclick="ask('France full roadmap')" class="btn-country px-3 py-3 rounded-2xl text-[12px] font-semibold text-slate-700">🇫🇷 France</button>
<button onclick="ask('Italy full roadmap')" class="btn-country px-3 py-3 rounded-2xl text-[12px] font-semibold text-slate-700">🇮🇹 Italy</button>
<button onclick="ask('China full roadmap')" class="btn-country px-3 py-3 rounded-2xl text-[12px] font-semibold text-slate-700">🇨🇳 China</button>
</div>

<p class="text-[11px] font-bold text-slate-400 tracking-widest mt-7 mb-3">💼 OUR SERVICES</p>
<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
<button onclick="ask('Tuition transfer SWIFT OUR MT103 guide')" class="service-card p-4 rounded-2xl text-left"><p class="text-[12px] font-bold text-slate-800">💸 Tuition</p><p class="text-[10px] text-slate-500 mt-1">SWIFT OUR Guide</p></button>
<button onclick="ask('Blocked Account Germany guide')" class="service-card p-4 rounded-2xl text-left"><p class="text-[12px] font-bold text-slate-800">🔒 Blocked</p><p class="text-[10px] text-slate-500 mt-1">€11,208 Guide</p></button>
<button onclick="ask('Proof of Funds GIC Canada')" class="service-card p-4 rounded-2xl text-left"><p class="text-[12px] font-bold text-slate-800">📄 GIC Funds</p><p class="text-[10px] text-slate-500 mt-1">$20,635 Guide</p></button>
<button onclick="ask('Dual currency card EBL BRAC')" class="service-card p-4 rounded-2xl text-left"><p class="text-[12px] font-bold text-slate-800">💳 Dual Card</p><p class="text-[10px] text-slate-500 mt-1">EBL / BRAC</p></button>
<button onclick="ask('Health insurance for students')" class="service-card p-4 rounded-2xl text-left"><p class="text-[12px] font-bold text-slate-800">🏥 Health</p><p class="text-[10px] text-slate-500 mt-1">Insurance</p></button>
<button onclick="ask('Student file opening full process')" class="service-card p-4 rounded-2xl text-left"><p class="text-[12px] font-bold text-slate-800">📁 Student File</p><p class="text-[10px] text-slate-500 mt-1">10k BDT</p></button>
<button onclick="ask('Visa and SEVIS fee guide')" class="service-card p-4 rounded-2xl text-left"><p class="text-[12px] font-bold text-slate-800">🛂 Visa & SEVIS</p><p class="text-[10px] text-slate-500 mt-1">$350+$185</p></button>
<button onclick="ask('Education loan Bangladesh')" class="service-card p-4 rounded-2xl text-left"><p class="text-[12px] font-bold text-slate-800">🏦 Edu Loan</p><p class="text-[10px] text-slate-500 mt-1">40L+ Guide</p></button>
</div>
</div>
</div>
</div>

<div class="sticky bottom-0 pt-4 bg-gradient-to-t from-[#f8f9ff] via-[#f8f9ff] to-transparent">
<div class="bg-white border border-indigo-100 rounded-[20px] p-2 flex gap-2 shadow-[0_20px_40px_rgba(79,70,229,.1)]">
<input id="inp" type="text" placeholder="Ask about any country, visa, fees..." class="flex-1 px-5 py-3.5 rounded-[14px] focus:outline-none text-[13px] bg-slate-50 focus:bg-white border border-transparent focus:border-indigo-200 transition-all" onkeypress="if(event.key==='Enter')send()">
<button onclick="send()" class="bg-gradient-to-r from-blue-600 to-violet-600 text-white px-7 py-3.5 rounded-[14px] text-[13px] font-bold shadow-lg shadow-blue-600/20 hover:shadow-blue-600/30 transition-all">Send ➤</button>
</div>
<p class="text-[10px] text-center text-slate-400 mt-3">Built for Bangladeshi Students • SWIFT OUR • Student File • Blocked Account Expert</p>
</div>
</main>
<script>
let chatHistory=[];const chat=document.getElementById('chat');const inp=document.getElementById('inp');
function addMsg(c,isUser){const d=document.createElement('div');d.className=`msg p-5 rounded-[20px] leading-relaxed text-[13px] ${isUser?'user':'ai'}`;if(isUser)d.innerText=c;else d.innerHTML=marked.parse(c);chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}
function ask(t){inp.value=t;send();}
async function send(){const q=inp.value.trim();if(!q)return;addMsg(q,true);inp.value='';const l=document.createElement('div');l.className='ai msg p-5 rounded-[20px] text-slate-400 text-[13px]';l.innerHTML='✨ Thinking...';chat.appendChild(l);chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q,history:chatHistory})});const d=await r.json();chat.removeChild(l);addMsg(d.answer,false);chatHistory.push({q:q,a:d.answer});if(chatHistory.length>6)chatHistory.shift();}catch(e){chat.removeChild(l);addMsg('Error connecting to AI. Please try again.',false);}}
</script></body></html>"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/wallet-demo")
def wallet_demo():
    return render_template_string("""
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>EduPay Demo</title>
<style>body{background:#0a0a0a;color:white;font-family:sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}.card{background:#1a1a1a;border:1px solid #00FF88;border-radius:16px;padding:30px;width:90%;max-width:380px;text-align:center}.btn{background:#00FF88;color:black;width:100%;padding:15px;border:none;border-radius:8px;font-weight:bold;cursor:pointer}</style>
</head><body><div class="card">
<h2 style="color:#00FF88">EduPay Global</h2><p style="font-size:11px;color:#aaa">Team: Tiger Panda</p>
<h3>500,000 BDT<br><span style="color:#00FF88;font-size:14px">~ $4,537 USD</span></h3>
<p style="background:#222;padding:8px;border-radius:8px;font-size:12px">✅ KYC Verified | Univ. of Birmingham</p>
<button class="btn" onclick="alert('Payment Successful! Mock Tx: 0x8a3f...f12a')">Pay $5,000 Tuition Now</button>
<p style="font-size:10px;color:#666;margin-top:15px">Mock Tx: 0x8a3f...f12a - Ready for FISCO BCOS<br>FinTechathon 2026 Demo</p>
</div></body></html>
    """)

@app.route("/ask", methods=["POST"])
def ask_agent():
    data = request.get_json()
    q = data.get("question","")
    frontend_history = data.get("history", [])
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if frontend_history:
        history_list = frontend_history[-3:]
    else:
        history_list = list(conversation_memory[client_ip])
    answer = get_ai(q, client_ip, history_list)
    conversation_memory[client_ip].append({"q": q, "a": answer})
    return jsonify({"answer": answer})

@app.route("/health")
def health(): 
    return {"has_key": bool(os.environ.get("GEMINI_API_KEY")), "client": bool(client), "status": "ok", "model": "gemini-3.8-flash included + lite for quota"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))