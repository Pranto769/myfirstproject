from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai

app = Flask(__name__)

# Gemini Setup
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# তোমার নিজের ডাটা
my_data = {
    "passport": "Passport করতে e-passport.gov.bd তে যান। লাগবে NID, ছবি।",
    "dollar": "Live Dollar Rate is 123.14 BDT (API থেকে আসছে)",
    "scholarship": "Scholarship এর জন্য DAAD, Erasmus দেখুন।",
    "visa": "Student Visa এর জন্য Bank Statement, IELTS লাগবে।"
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()

    # 1. প্রথমে তোমার নিজের ডাটা থেকে খোঁজা
    for key in my_data:
        if key in query:
            return jsonify({"answer": my_data[key]})

    # 2. না পেলে Gemini থেকে আনা
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"You are StudentFinance PRO assistant. Answer this: {query}")
        return jsonify({"answer": response.text})
    except Exception as e:
        return jsonify({"answer": f"AI Error: {str(e)}। API Key চেক করুন।"})

if __name__ == '__main__':
    app.run(debug=True)