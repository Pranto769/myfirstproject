import os
import requests
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

# --- Gemini Setup ---
api_key = os.environ.get("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)
    print("Gemini Client Initialized")

# Model - তুমি 3.8 চেয়েছিলে, এটাই Final
MODEL_ID = "gemini-3.8-flash"

def get_exchange_rate():
    try:
        r = requests.get("https://open.er-api.com/v6/latest/EUR", timeout=4)
        data = r.json()
        eur_bdt = data['rates'].get('BDT', 127)
        return f"\n[LIVE RATE] 1 EUR = {eur_bdt} BDT"
    except:
        return "\n[LIVE RATE] 1 EUR = ~127 BDT"

def generate_checklist(text):
    t = text.lower()
    if "germany" in t:
        return "Checklist Germany: Blocked Account 11,208 EUR, Admission, Visa, Insurance"
    if "italy" in t:
        return "Checklist Italy: Universitaly, CIMEA, Bank Solvency"
    return "Checklist: Admission Letter, Financial Proof, Student File"

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>StudentFinance AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:system-ui;background:#f6f7fb;padding:15px}
.box{max-width:720px;margin:auto;background:#fff;padding:24px;border-radius:16px;box-shadow:0 8px 24px rgba(0,0,0,.08)}
h2{color:#4f46e5;margin:0} small{color:#666}
input,button{width:100%;padding:14px;margin-top:12px;border-radius:10px;border:1px solid #e5e7eb;box-sizing:border-box}
button{background:#4f46e5;color:#fff;font-weight:700;border:none;cursor:pointer}
#ans{margin-top:18px;white-space:pre-wrap;background:#f9fafb;padding:14px;border-radius:10px;border:1px solid #eef2ff;min-height:60px}
</style>
</head>
<body>
<div class="box">
<h2>🎓 StudentFinance AI</h2>
<small>Powered by Gemini 3.8 Flash | Tsinghua x WeBank FinTechathon</small>
<input id="q" placeholder="Ex: Germany blocked account process? SWIFT charge?">
<button onclick="ask()">Ask AI</button>
<div id="ans">Answer will appear here...</div>
</div>
<script>
async function ask(){
 const q=document.getElementById('q').value;
 const el=document.getElementById('ans');
 if(!q){el.innerText='Please type a question';return}
 el.innerText='Thinking with Gemini 3.8 Flash...';
 try{
  const res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
  const data=await res.json();
  el.innerText=data.answer;
 }catch(e){ el.innerText='Network Error: '+e.message }
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask_ai():
    try:
        user_q = request.json.get("question","").strip()
        if not user_q:
            return jsonify({"answer": "Please ask something!"})
        if not client:
            return jsonify({"answer": "ERROR: GEMINI_API_KEY not set in Render Environment Variables."})

        extra = get_exchange_rate() + "\n" + generate_checklist(user_q)
        
        prompt = f"You are StudentFinance AI. Help Bangladeshi students with abroad study finance. Be concise, step-by-step. User: {user_q} Context: {extra}"

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        return jsonify({"answer": response.text})
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        # Fallback: যদি 3.8 fail করে, 2.0 দিয়ে try করবে
        try:
            fallback = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            return jsonify({"answer": fallback.text + "\n\n[Note: Answered with fallback model]"})
        except Exception as e2:
            return jsonify({"answer": f"AI Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)