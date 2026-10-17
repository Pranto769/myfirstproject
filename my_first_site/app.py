import os
from collections import defaultdict, deque
from flask import Flask, request, jsonify, render_template_string
app = Flask(__name__)

# ========== MEMORY SYSTEM ==========
# IP অনুযায়ী last 5 টা কথা মনে রাখবে
conversation_memory = defaultdict(lambda: deque(maxlen=5))

try:
    from google import genai
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else None
    print(f"Client init: {bool(client)} Has key: {bool(api_key)}")
except Exception as e:
    print(f"GenAI init fail: {e}")
    client = None

# ========== SMART FALLBACK - সব Country এর জন্য বড় উত্তর ==========
def get_smart_answer(q, history_text=""):
    ql = q.lower()
    # যদি প্রশ্ন ছোট হয় যেমন "total fee?" তাহলে history থেকে country বের করো
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
    if "korea" in combined or "south korea" in combined:
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
        # যদি history তে country থাকে, ওই অনুযায়ী visa বলবে
        if any(x in combined for x in ["usa","america"]):
            return "### 🛂 USA Visa\nSEVIS $350 + MRV $185 = $535 via own Dual Card. Docs: I-20, SEVIS Receipt, MRV, Bank Solvency $40k, Interview at US Embassy." + footer
        if "germany" in combined:
            return "### 🛂 Germany Visa\nVisa €75 + Blocked €11,208 + Health €120/mo + Admission + Student File. VFS Dhaka." + footer
        return "### 🛂 Visa & SEVIS\nUSA: $350+185. Germany: €75. UK: £490+IHS £1035. Canada: $150+85. Always use own card." + footer

    # Total fee জাতীয় প্রশ্নের জন্য - history থেকে country ধরে total বলে দেবে
    if "total" in ql and ("fee" in ql or "cost" in ql or "koto" in ql):
        if any(x in combined for x in ["usa","america"]):
            return "### 🇺🇸 USA Total Cost\nTuition $15k + SEVIS $350 + MRV $185 + Flight $900 + Health $800 + Student File 10k BDT = ~$17k first year show. Living $12k/year extra." + footer
        if "germany" in combined:
            return "### 🇩🇪 Germany Total\nBlocked €11,208 (your money back) + Tuition FREE Public + Health €1440/year + Visa €75 + Flight €700 + File 10k BDT = ~€13,500 show, actual spend €3k." + footer
        return f"### 💰 Total Cost for {q}\nGermany: ~€13,500 show (Blocked is yours). Canada: GIC $20,635+Tuition $15k. UK: £21k+ . USA: $17k+. This includes Tuition + Living + Visa + Flight + File 10k BDT." + footer

    return f"### 🎓 Expert for: {q}\n**Any Country:**\n1. Uni: Public cheap - IELTS 6.0-6.5\n2. Proof: Germany Blocked €11,208, Canada GIC $20,635, UK Bank £15k 28 days, USA Solvency $40k\n3. File: EBL/BRAC AD 10k BDT\n4. Transfer: Always SWIFT OUR +$30\n5. Visa: Admission+Financial+Health+Academic" + footer

# ========== AI WITH MEMORY ==========
def get_ai(q, client_ip, history_list):
    history_text = " ".join([h['q'] for h in history_list]) if history_list else ""
    
    if not client:
        return get_smart_answer(q, history_text)
    
    # Quota বাঁচাতে Lite আগে
    models_to_try = ["gemini-2.5-flash-lite", "gemini-2.0-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]
    
    # History সহ Prompt বানাও - মেমোরির জন্য
    full_prompt = ""
    if history_list:
        full_prompt += "Conversation history (remember this):\n"
        for h in history_list[-3:]:
            full_prompt += f"User: {h['q']}\nAssistant: {h['a'][:400]}\n"
        full_prompt += "\n"
    full_prompt += f"Current user question: {q}\n\nInstruction: If current question is short like 'total fee?', 'visa cost?', 'what about living cost?' - you MUST use the country/topic from conversation history above. For example if history was about USA and now user says 'total fee koto?' answer USA total fee. Give detailed, formatted markdown answer for Bangladeshi students. Keep answer big and helpful."

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

HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>StudentFinance</title>
<script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>#chat{height:calc(100vh - 280px)}.msg{max-width:85%}.user{background:#2563eb;color:#fff;margin-left:auto}.ai{background:#fff;border:1px solid #e5e7eb}</style></head>
<body class="bg-gray-50"><header class="bg-white border-b sticky top-0 z-10"><div class="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center"><div><h1 class="font-bold text-blue-700">🎓 StudentFinance AGENT</h1><p class="text-xs text-gray-500">With Memory - Remembers Last Questions</p></div><span class="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full">🟢 Memory ON</span></div></header>
<main class="max-w-6xl mx-auto px-4 py-4"><div id="chat" class="overflow-y-auto space-y-4 pb-4">
<div class="ai msg p-5 rounded-2xl shadow-sm"><h2 class="font-bold">Welcome! 👋 Memory Fixed!</h2><p class="text-sm text-gray-600 mt-1 mb-4">Now I remember! Ask USA fee, then ask 'total fee?' - I will add it.</p>
<p class="text-xs font-bold text-green-600 mb-2">🟢 NEW TO THIS? START HERE</p><div class="mb-6"><button onclick="ask('I am new, I know nothing, give me complete guideline from zero for studying abroad from Bangladesh')" class="w-full bg-green-50 border-2 border-green-500 text-green-700 px-4 py-3 rounded-xl text-sm font-bold">🚀 I'm New - Complete Guideline</button></div>
<p class="text-xs font-bold text-gray-500 mb-2">SELECT DESTINATION</p><div class="flex flex-wrap gap-2 mb-6">
<button onclick="ask('Germany full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white">🇩🇪 Germany</button><button onclick="ask('Canada full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white">🇨🇦 Canada</button><button onclick="ask('UK full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white">🇬🇧 UK</button><button onclick="ask('USA full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white">🇺🇸 USA</button><button onclick="ask('China full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white">🇨🇳 China</button><button onclick="ask('Australia full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white">🇦🇺 Australia</button><button onclick="ask('Japan full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white">🇯🇵 Japan</button><button onclick="ask('South Korea full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white">🇰🇷 South Korea</button><button onclick="ask('Malaysia full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white">🇲🇾 Malaysia</button><button onclick="ask('Sweden full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white">🇸🇪 Sweden</button><button onclick="ask('France full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white">🇫🇷 France</button><button onclick="ask('Italy full roadmap')" class="border px-4 py-2 rounded-full text-xs bg-white">🇮🇹 Italy</button>
</div><p class="text-xs font-bold text-gray-500 mb-2">OUR SERVICES</p><div class="grid grid-cols-2 md:grid-cols-4 gap-3">
<button onclick="ask('Tuition transfer SWIFT OUR MT103 guide')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">💸 Tuition Transfer</p></button><button onclick="ask('Blocked Account Germany guide')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">🔒 Blocked Account</p></button><button onclick="ask('Proof of Funds GIC Canada')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">📄 Proof of Funds</p></button><button onclick="ask('Dual currency card EBL BRAC')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">💳 Dual Currency Card</p></button><button onclick="ask('Health insurance for students')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">🏥 Health Insurance</p></button><button onclick="ask('Student file opening full process')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">📁 Student File</p></button><button onclick="ask('Visa and SEVIS fee guide')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">🛂 Visa & SEVIS Fee</p></button><button onclick="ask('Education loan Bangladesh')" class="bg-white border p-3 rounded-xl text-left"><p class="text-xs font-bold">🏦 Education Loan</p></button>
</div></div></div><div class="sticky bottom-0 bg-gray-50 pt-3"><div class="bg-white border rounded-2xl p-2 flex gap-2 shadow-lg"><input id="inp" type="text" placeholder="Ask anything..." class="flex-1 px-4 py-3 rounded-xl focus:outline-none text-sm" onkeypress="if(event.key==='Enter')send()"><button onclick="send()" class="bg-blue-600 text-white px-6 py-3 rounded-xl text-sm font-bold">Send</button></div></div></main><script>let chatHistory=[];const chat=document.getElementById('chat');const inp=document.getElementById('inp');function addMsg(c,isUser){const d=document.createElement('div');d.className=`msg p-4 rounded-2xl ${isUser?'user':'ai shadow-sm'}`;if(isUser)d.innerText=c;else d.innerHTML=marked.parse(c);chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}function ask(t){inp.value=t;send();}async function send(){const q=inp.value.trim();if(!q)return;addMsg(q,true);inp.value='';const l=document.createElement('div');l.className='ai msg p-4 rounded-2xl text-gray-400';l.innerHTML='Thinking (with memory)...';chat.appendChild(l);chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q,history:chatHistory})});const d=await r.json();chat.removeChild(l);addMsg(d.answer,false);chatHistory.push({q:q,a:d.answer});if(chatHistory.length>6)chatHistory.shift();}catch(e){chat.removeChild(l);addMsg('Error connecting to AI.',false);}}</script></body></html>"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask_agent():
    data = request.get_json()
    q = data.get("question","")
    frontend_history = data.get("history", [])  # JS থেকে আসা history
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Frontend history থাকলে ওটা use করো, না থাকলে server memory
    if frontend_history:
        history_list = frontend_history[-3:]
    else:
        history_list = list(conversation_memory[client_ip])
    
    answer = get_ai(q, client_ip, history_list)
    
    # Memory save করো
    conversation_memory[client_ip].append({"q": q, "a": answer})
    
    return jsonify({"answer": answer})

@app.route("/health")
def health(): 
    return {"has_key": bool(os.environ.get("GEMINI_API_KEY")), "client": bool(client), "status": "ok", "model": "gemini-2.5-flash-lite + memory"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))