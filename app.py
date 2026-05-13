from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Load translations
def load_translations(lang):
    file_path = os.path.join(app.root_path, 'translations', f'{lang}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/translations/<lang>')
def get_translations(lang):
    if lang not in ['en', 'az']:
        return jsonify({"error": "Language not supported"}), 400
    translations = load_translations(lang)
    return jsonify(translations)

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    data = request.json
    name = data.get('name')
    company = data.get('company')
    phone = data.get('phone')
    
    # In a real app, we would save to DB or send an email here.
    # For now, we just print and return success.
    print(f"New Contact: Name={name}, Company={company}, Phone={phone}")
    
    return jsonify({"status": "success", "message": "Thank you for reaching out!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
