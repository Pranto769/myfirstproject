import os
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

# API Key Render Environment থেকে নেবে
api_key = os.environ.get("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)

HTML = """
<!DOCTYPE html>
<html>
<head><title>Finance Assistant</title>
<style>
body{font-family:Arial;max-width:700px;margin:40px auto;padding:20px}
input{width:80%;padding:10px} button{padding:10px 20px}
#ans{margin-top:20px;background:#f5f5f5;padding:15px;border-radius:8px}
</style>
</head>
<body>
<h2>💰 Finance Assistant for Students</h2>
<input id="q" placeholder="যেমন: টাকা কিভাবে সেভ করবো?">
<button onclick="ask()">Ask</button>
<div id="ans"></div>
<script>
async function ask(){
 let q=document.getElementById('q').value;
 document.getElementById('ans').innerText='Thinking...';
 let res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
 let data=await res.json();
 document.getElementById('ans').innerText=data.answer;
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/ask', methods=['POST'])
def ask():
    if not client:
        return jsonify({"answer": "GEMINI_API_KEY is not set in Render Environment"})
    data = request.get_json()
    q = data.get('question','')
    try:
        response = client.models.generate_content(model="gemini-3.8-flash", contents=q)
        return jsonify({"answer": response.text})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run()