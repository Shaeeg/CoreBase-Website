from flask import Flask, render_template, request, jsonify
import json
import os
import xmlrpc.client
from dotenv import load_dotenv

load_dotenv(override=True)

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
    
    odoo_url = os.getenv('ODOO_URL')
    odoo_db = os.getenv('ODOO_DB')
    odoo_username = os.getenv('ODOO_USERNAME')
    odoo_password = os.getenv('ODOO_PASSWORD')
    
    if not all([odoo_url, odoo_db, odoo_username, odoo_password]):
        print("Missing Odoo credentials in .env file.")
        return jsonify({"status": "error", "message": "Server configuration error. Contact form temporarily disabled."}), 500

    try:
        # Authenticate with Odoo
        common = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/common')
        uid = common.authenticate(odoo_db, odoo_username, odoo_password, {})
        
        if not uid:
            print("Failed to authenticate with Odoo.")
            return jsonify({"status": "error", "message": "Server authentication error."}), 500

        # Create Lead
        models = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/object')
        lead_id = models.execute_kw(odoo_db, uid, odoo_password, 'crm.lead', 'create', [{
            'name': f"Website Lead: {company}",
            'contact_name': name,
            'partner_name': company,
            'phone': phone,
            'description': f"Lead generated from CoreBase website.\nName: {name}\nCompany: {company}\nPhone: {phone}"
        }])
        
        print(f"Successfully created Odoo Lead ID: {lead_id}")
        return jsonify({"status": "success", "message": "Thank you! We will get back to you shortly."})

    except Exception as e:
        print(f"Odoo XML-RPC Error: {str(e)}")
        return jsonify({"status": "error", "message": "There was an error processing your request. Please try again later."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)