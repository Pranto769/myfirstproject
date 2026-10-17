import os
import requests
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

# ====================== CONFIG ======================
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None
MODEL_PRIMARY = "gemini-2.0-flash"
MODEL_FALLBACK = "gemini-2.0-flash"

# ====================== SYSTEM PROMPT ======================
SYSTEM_PROMPT = """
You are StudentFinance AI, a specialized Cross-border & Student Finance Agent for the Tsinghua University × WeBank FinTechathon (Topic C).
Goal: Help Bangladeshi students with real financial tasks.
Strict Format:
1. Quick Summary (2-4 lines)
2. Step-by-Step Guide
3. Important Notes / Warnings
4. Cost Overview (when relevant)
End with: *This is general guidance only, not official financial advice. Please verify with your bank and official sources.*
Rules: Always recommend OUR fee code for SWIFT, keep MT103, discourage Hundi, Germany=Blocked Account €11,208 separate from tuition, Canada=CAD 20635+. Use live rate. Be practical and student-friendly. Support Bangla and English mix.
"""

def get_live_rate(base="USD", target="BDT"):
    try:
        res = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=6)
        return f"1 {base} = {res.json()['rates'].get(target)} {target}"
    except:
        return "Rate unavailable"

def get_checklist(country):
    c = country.lower()
    data = {
        "germany": ["Admission Letter", "Blocked Account (€11,208)", "Health Insurance", "Semesterbeitrag"],
        "canada": ["LOA", "GIC + Proof of Funds (CAD 20,635+)", "Tuition Receipt"],
    }
    items = data.get(c, ["Admission Letter", "Passport", "Proof of Funds"])
    return "Checklist: " + ", ".join(items)

# ====================== FINAL UI WITH PERFECT FORMATTING ======================
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>StudentFinance AI</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; }
    #chat-container { height: calc(100vh - 200px); }
    .message { max-width: 85%; line-height: 1.65; }
    .user-msg { background: #2563eb; color: white; margin-left: auto; border-bottom-right-radius: 4px; }
    .ai-msg { background: #fff; border: 1px solid #e2e8f0; border-bottom-left-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,.04); }
    .ai-msg h3 { font-size: 15px; font-weight: 700; color: #1e40af; margin: 16px 0 8px 0; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }
    .ai-msg ul, .ai-msg ol { margin: 8px 0 8px 20px; }
    .ai-msg li { margin-bottom: 6px; font-size: 14px; }
    .ai-msg p { margin-bottom: 10px; font-size: 14px; }
  </style>
</head>
<body class="bg-gray-50 text-gray-800">
  <header class="bg-white border-b sticky top-0 z-50">
    <div class="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
      <div><h1 class="text-lg font-bold text-blue-700">🎓 StudentFinance AI</h1><p class="text-xs text-gray-500">For students who don't know where to start • Tsinghua x WeBank</p></div>
      <div class="text-xs bg-blue-50 text-blue-700 px-3 py-1 rounded-full font-medium">Gemini</div>
    </div>
  </header>
  <main class="max-w-4xl mx-auto px-4 py-4">
    <div id="chat-container" class="overflow-y-auto space-y-4 pb-4">
      <div class="ai-msg message p-5 rounded-2xl">
        <p class="font-bold text-base mb-1">নমস্কার! তুমি কি বিদেশে পড়তে যেতে চাও?</p>
        <p class="text-sm text-gray-600 mb-4">চিন্তা নেই, কিছু না জানলেও হবে। নিচ থেকে সিলেক্ট করো।</p>
        <p class="text-xs font-semibold text-gray-500 mb-2">STEP 1: কোন দেশে?</p>
        <div class="flex flex-wrap gap-2 mb-4">
          <button onclick="askExample('I want to go to Germany for Bachelors, give me full financial roadmap from Bangladesh')" class="bg-white border border-blue-200 text-blue-700 px-4 py-2 rounded-full text-sm font-medium hover:bg-blue-600 hover:text-white">🇩🇪 Germany</button>
          <button onclick="askExample('I want to go to Canada, what is the full proof of funds and GIC process?')" class="bg-white border px-4 py-2 rounded-full text-sm hover:bg-blue-50">🇨🇦 Canada</button>
          <button onclick="askExample('I want to go to UK')" class="bg-white border px-4 py-2 rounded-full text-sm hover:bg-blue-50">🇬🇧 UK</button>
          <button onclick="askExample('I want to go to USA')" class="bg-white border px-4 py-2 rounded-full text-sm hover:bg-blue-50">🇺🇸 USA</button>
        </div>
        <div class="bg-blue-600 text-white p-3 rounded-xl mt-2">
          <button onclick="askExample('I am new from Bangladesh, I know nothing about studying abroad finance. Give me a complete step-by-step roadmap in simple Bangla.')" class="w-full bg-white text-blue-700 font-bold py-2 rounded-lg text-sm">✨ আমি একদম নতুন, শুরু থেকে বুঝিয়ে দাও</button>
        </div>
      </div>
    </div>
    <div class="sticky bottom-0 bg-gray-50 pt-3">
      <div class="bg-white border rounded-2xl p-2 flex gap-2 shadow-sm">
        <input id="user-input" type="text" placeholder="বাংলায় লিখতে পারো... জার্মানির জন্য কত টাকা লাগবে?" class="flex-1 px-4 py-3 rounded-xl focus:outline-none text-sm" onkeypress="if(event.key === 'Enter') sendMessage()">
        <button onclick="sendMessage()" class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-xl text-sm font-medium">Send</button>
      </div>
    </div>
  </main>
<script>
  const chatContainer = document.getElementById('chat-container');
  const input = document.getElementById('user-input');
  function getRelatedQuestions(q){
    q=q.toLowerCase();
    if(q.includes('germany')) return ["Blocked Account ছাড়া উপায় আছে?","Semesterbeitrag কত?","Health Insurance কত লাগে?"];
    if(q.includes('canada')) return ["GIC আর POF কি একই?","Bank Statement কত মাসের?"];
    if(q.includes('tuition')||q.includes('swift')) return ["OUR code না দিলে কি হবে?","MT103 কেন রাখব?","Student File কিভাবে খুলব?"];
    return ["মোট কত টাকা খরচ হবে?","কোন ব্যাংক ভালো?","Hundi তে Risk কি?"];
  }
  function addMessage(content, isUser=false, originalQuestion=""){
    const div = document.createElement('div');
    div.className = `message p-4 rounded-2xl ${isUser ? 'user-msg' : 'ai-msg'}`;
    if(isUser){ div.innerText = content; }
    else{ div.innerHTML = marked.parse(content); }
    if(!isUser && originalQuestion){
      const related = getRelatedQuestions(originalQuestion);
      let h = `<div class="mt-4 pt-3 border-t"><p class="text-xs font-bold text-gray-500 mb-2">🔍 আরও জানতে পারো:</p><div class="flex flex-wrap gap-2">`;
      related.forEach(r=>{ h+=`<button onclick="askExample('${r}')" class="text-xs bg-blue-50 text-blue-700 border px-3 py-1.5 rounded-full hover:bg-blue-600 hover:text-white">+ ${r}</button>`; });
      h+=`</div><button onclick="document.getElementById('user-input').focus()" class="mt-3 w-full text-xs bg-gray-900 text-white py-2 rounded-lg">✏️ এর বাইরে অন্য কিছু লিখতে চাও? এখানে লিখো</button></div>`;
      div.innerHTML+=h;
    }
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
  function askExample(t){ input.value=t; sendMessage(); }
  async function sendMessage(){
    const q=input.value.trim(); if(!q) return;
    addMessage(q,true); input.value='';
    const loading=document.createElement('div'); loading.className='ai-msg message p-4 rounded-2xl text-gray-500'; loading.innerHTML='Thinking...'; chatContainer.appendChild(loading);
    chatContainer.scrollTop=chatContainer.scrollHeight;
    try{
      const res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
      const data=await res.json(); chatContainer.removeChild(loading); addMessage(data.answer,false,q);
    }catch(e){ chatContainer.removeChild(loading); addMessage('Sorry, error. Try again.',false,""); }
  }
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask():
    if not client:
        return jsonify({"answer": "Error: GEMINI_API_KEY missing."})
    data = request.get_json()
    question = data.get("question","").strip()
    if not question:
        return jsonify({"answer": "Please type a question."})
    try:
        extra=""
        lq=question.lower()
        if any(w in lq for w in ["rate","usd","bdt","eur","euro","dollar","exchange"]):
            extra+=f"\nLive Rates: {get_live_rate('USD','BDT')} | {get_live_rate('EUR','BDT')}"
        for co in ["germany","canada","uk","usa"]:
            if co in lq:
                extra+=f"\n{get_checklist(co)}"
                break
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {question}\nContext: {extra}\n\nAnswer in strict format with markdown headings."
        try:
            response = client.models.generate_content(model=MODEL_PRIMARY, contents=full_prompt)
        except:
            response = client.models.generate_content(model=MODEL_FALLBACK, contents=full_prompt)
        return jsonify({"answer": response.text.strip()})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)