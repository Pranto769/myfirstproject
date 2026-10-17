import os
import requests
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

# Gemini Client
api_key = os.environ.get("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)

MODEL_ID = "gemini-2.0-flash"  # Stable, 3.8-flash এর মতোই Fast

def get_exchange_rate():
    try:
        # Free API, Key লাগে না
        r = requests.get("https://open.er-api.com/v6/latest/EUR", timeout=3)
        data = r.json()
        eur_bdt = data['rates'].get('BDT', 125)
        return f"\nLIVE INFO: 1 EUR = {eur_bdt} BDT (Today's Rate)."
    except:
        return "\nLIVE INFO: 1 EUR = ~127 BDT."

def generate_checklist(country):
    country = country.lower()
    if "germany" in country:
        return "Checklist for Germany: 1. Blocked Account (11,208 EUR) 2. University Admission 3. Visa Appointment 4. Health Insurance"
    elif "italy" in country:
        return "Checklist for Italy: 1. Pre-enrollment on Universitaly 2. DOV/CIMEA 3. Bank Statement"
    else:
        return f"Checklist for {country}: 1. Admission Letter 2. Financial Proof 3. Visa Docs"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>StudentFinance AI - Powered by Gemini 3.8 Flash</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial;background:#f5f7ff;padding:20px} .box{max-width:700px;margin:auto;background:white;padding:25px;border-radius:15px;box-shadow:0 5px 20px rgba(0,0,0,0.1)}
h2{color:#4f46e5} input,button{width:100%;padding:12px;margin-top:10px;border-radius:8px;border:1px solid #ddd} button{background:#4f46e5;color:white;border:none;cursor:pointer;font-weight:bold} #ans{margin-top:20px;white-space:pre-wrap;background:#f9fafb;padding:15px;border-radius:8px}
</style>
</head>
<body>
<div class="box">
<h2>🎓 StudentFinance AI</h2>
<p>Powered by Gemini 3.8 Flash | For Tsinghua x WeBank FinTechathon</p>
<input id="q" placeholder="Ex: How to open blocked account for Germany? SWIFT fee?">
<button onclick="ask()">Ask AI</button>
<div id="ans">Answer will appear here...</div>
</div>
<script>
async function ask(){
 let q=document.getElementById('q').value;
 let ansDiv=document.getElementById('ans');
 ansDiv.innerText='Thinking...';
 try{
  let res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
  let data=await res.json();
  ansDiv.innerText=data.answer;
 }catch(e){ ansDiv.innerText='Error: '+e; }
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/ask", methods=["POST"])
def ask_ai():
    try:
        user_q = request.json.get("question","")
        if not client:
            return jsonify({"answer": "GEMINI_API_KEY not set in Render Environment."})
        
        # Merged Logic - Error Proof
        extra = get_exchange_rate() + "\n" + generate_checklist(user_q)

        prompt = f"""You are StudentFinance AI for Bangladeshi students going abroad.
        User Question: {user_q}
        Extra Context: {extra}
        Give a helpful, short, step-by-step answer in English/Bangla mix about finance, blocked account, SWIFT, student file.
        """

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        return jsonify({"answer": response.text})
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"answer": f"Sorry, AI error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)